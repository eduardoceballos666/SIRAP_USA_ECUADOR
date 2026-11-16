"""Fault injection against actual handlers with private-storage/device fakes only."""
from concurrent.futures import ThreadPoolExecutor
from email.message import Message
from pathlib import Path
from types import SimpleNamespace
import json
import io
import os
import subprocess
import sys
import threading
import uuid
import urllib.request
import urllib.response
import pandas as pd

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from _recovery_support import FakeGitHub
from api.deps import current_user
from api.main import storage_unavailable
from api.recognition_evidence import EvidenceStore
from api.routers import recognition,reports
from src.access_control import AccessDecision,HttpBarrier
from src.storage import CsvStore,StorageError


@pytest.fixture
def recovery_app(tmp_path,monkeypatch):
    remote=FakeGitHub(tmp_path/'remote.sqlite');remote.install(monkeypatch)
    db=CsvStore(tmp_path/'ephemeral-cache')
    user=dict(usuario='operator-a',nombre='Same display name',rol='OPERADOR',country='usa')
    state=SimpleNamespace(calls=0,succeeds=True)
    class Barrier:
        simulated=True
        def open(self,*args):
            state.calls+=1
            return state.succeeds
    monkeypatch.setattr(recognition,'get_store',lambda:db)
    monkeypatch.setattr(reports,'get_store',lambda:db)
    monkeypatch.setattr(recognition,'get_barrier',lambda:Barrier())
    monkeypatch.setattr(recognition,'evidence_store',EvidenceStore())
    monkeypatch.setattr(recognition,'_decide',lambda *args:AccessDecision('AUTORIZADO','Synthetic authorization','test','BLANCA'))
    app=FastAPI(telemetry={'auto_configure':False})
    app.add_exception_handler(StorageError,storage_unavailable)
    app.include_router(recognition.router);app.include_router(reports.router)
    app.dependency_overrides[current_user]=lambda:user
    return SimpleNamespace(client=TestClient(app),db=db,remote=remote,user=user,state=state,root=tmp_path)


def request_body(**changes):
    body=dict(country='usa',jurisdiction='CA',garita='Synthetic Gate',tipo_movimiento='ENTRADA',
        accion='APERTURA_MANUAL',placa_final='DEMO123',origen='MANUAL',
        motivo='Synthetic recovery verification',operacion_id=str(uuid.uuid4()))
    body.update(changes);return body


def get_status(app,body):
    return app.client.get('/api/operations/'+body['operacion_id']+'/status',params={'country':body['country']})


def cancel(app,body):
    return app.client.post('/api/operations/'+body['operacion_id']+'/cancel',json={
        'country':body['country'],'garita':body['garita'],'tipo_movimiento':body['tipo_movimiento'],
        'accion_solicitada':body['accion']})


@pytest.mark.parametrize('phase,exit_code,expected_state,expected_commands',[
    ('accepted',73,'SOLICITADA',0),('actuated',74,'SOLICITADA',1),('committed',75,'CONFIRMADA',1),
])
def test_forced_process_restart_restores_history_and_never_replays(phase,exit_code,expected_state,expected_commands,tmp_path):
    root=Path(__file__).resolve().parents[1]
    worker=Path(__file__).with_name('recovery_worker.py')
    identifier=str(uuid.uuid4())
    env=dict(os.environ,OTEL_SDK_DISABLED='true',FASTAPI_OTEL_AUTO_CONFIGURE='false',DO_NOT_TRACK='1')
    crashed=subprocess.run([sys.executable,str(worker),phase,str(tmp_path),identifier],cwd=root,
        env=env,capture_output=True,text=True,timeout=60)
    assert crashed.returncode==exit_code,crashed.stderr
    resumed=subprocess.run([sys.executable,str(worker),'resume',str(tmp_path),identifier],cwd=root,
        env=env,capture_output=True,text=True,timeout=60)
    assert resumed.returncode==0,resumed.stderr
    proof=json.loads(resumed.stdout.splitlines()[-1])
    assert proof['history_rows']==1 and proof['device_commands']==expected_commands
    assert proof['status']['estado_barrera']==expected_state
    assert proof['status']['barrera_abierta'] is (True if expected_state=='CONFIRMADA' else None)
    assert proof['status']['requiere_revision']==(expected_state=='SOLICITADA')


def test_lost_http_response_is_recovered_by_read_only_status(recovery_app):
    app=recovery_app;body=request_body()
    assert app.client.post('/api/operations',json=body).status_code==201
    # Pretend the browser never received that response and obtains a fresh instance.
    restored=CsvStore(app.root/'fresh-cache')
    assert restored.operation(body['operacion_id'])['estado_barrera']=='CONFIRMADA'
    for _ in range(3):
        response=get_status(app,body)
        assert response.status_code==200 and response.headers['cache-control']=='no-store'
        assert response.json()['barrera_abierta'] is True
    assert app.state.calls==1 and len(restored.operations())==1
    assert app.client.post('/api/operations',json=body).status_code==409
    assert app.state.calls==1


@pytest.mark.parametrize('failure,accepted',[('before_put',False),('after_put',True)])
def test_connection_failure_around_initial_commit_never_dispatches(recovery_app,failure,accepted):
    app=recovery_app;body=request_body();app.remote.fail_next=failure
    assert app.client.post('/api/operations',json=body).status_code==503
    assert app.state.calls==0
    status=get_status(app,body)
    assert status.status_code==(200 if accepted else 404)
    if accepted:
        assert status.json()['estado_barrera']=='SOLICITADA'
        assert status.json()['barrera_abierta'] is None
        assert cancel(app,body).json()['estado_barrera']=='SOLICITADA'
    else:
        assert cancel(app,body).json()['estado_barrera']=='CANCELADA'
    assert app.client.post('/api/operations',json=body).status_code==409
    assert app.state.calls==0 and len(app.db.operations())==1


def test_final_storage_failure_keeps_the_unknown_outcome_and_blocks_replay(recovery_app,monkeypatch):
    app=recovery_app;body=request_body();original=app.db.update_operation_state
    def lose_connection_after_actuation(*args):
        app.remote.fail_next='before_put'
        return original(*args)
    monkeypatch.setattr(app.db,'update_operation_state',lose_connection_after_actuation)
    assert app.client.post('/api/operations',json=body).status_code==503
    status=get_status(app,body).json()
    assert status['estado_barrera']=='SOLICITADA' and status['requiere_revision']
    assert status['barrera_abierta'] is None
    assert app.client.post('/api/operations',json=body).status_code==409
    assert app.state.calls==1 and len(app.db.operations())==1


def test_completed_commit_with_lost_final_ack_can_still_be_recovered(recovery_app,monkeypatch):
    app=recovery_app;body=request_body();original=app.db.update_operation_state
    def lose_ack(*args):
        app.remote.fail_next='after_put'
        return original(*args)
    monkeypatch.setattr(app.db,'update_operation_state',lose_ack)
    assert app.client.post('/api/operations',json=body).status_code==503
    assert get_status(app,body).json()['estado_barrera']=='CONFIRMADA'
    assert app.client.post('/api/operations',json=body).status_code==409
    assert app.state.calls==1


def test_cancellation_tombstone_prevents_a_late_original_request(recovery_app):
    app=recovery_app;body=request_body()
    assert get_status(app,body).status_code==404
    assert cancel(app,body).json()['estado_barrera']=='CANCELADA'
    assert cancel(app,body).json()['estado_barrera']=='CANCELADA'
    assert app.client.post('/api/operations',json=body).status_code==409
    assert app.state.calls==0 and len(app.db.operations())==1
    assert app.db.operation(body['operacion_id'])['operador_usuario']=='operator-a'


def test_cancellation_wins_while_a_late_request_is_still_being_validated(recovery_app,monkeypatch):
    app=recovery_app;body=request_body();entered=threading.Event();release=threading.Event()
    def delayed_decision(*args):
        entered.set();assert release.wait(15)
        return AccessDecision('AUTORIZADO','Synthetic authorization','test','BLANCA')
    monkeypatch.setattr(recognition,'_decide',delayed_decision)
    with ThreadPoolExecutor(max_workers=1) as pool:
        future=pool.submit(app.client.post,'/api/operations',json=body)
        assert entered.wait(15)
        try:assert cancel(app,body).json()['estado_barrera']=='CANCELADA'
        finally:release.set()
        assert future.result(timeout=15).status_code==409
    assert app.state.calls==0 and len(app.db.operations())==1


def test_an_accepted_command_cannot_be_cancelled_or_dispatched_again(recovery_app):
    app=recovery_app;body=request_body()
    assert app.client.post('/api/operations',json=body).status_code==201
    assert cancel(app,body).json()['estado_barrera']=='CONFIRMADA'
    assert app.state.calls==1 and len(app.db.operations())==1


def test_concurrent_identical_requests_dispatch_once(recovery_app):
    app=recovery_app;body=request_body()
    with ThreadPoolExecutor(max_workers=2) as pool:
        responses=list(pool.map(lambda _:app.client.post('/api/operations',json=body),range(2)))
    assert sorted(r.status_code for r in responses)==[201,409]
    assert app.state.calls==1 and len(app.db.operations())==1


def test_status_is_scoped_to_username_and_country_not_display_name(recovery_app):
    app=recovery_app;body=request_body()
    assert app.client.post('/api/operations',json=body).status_code==201
    app.user['usuario']='different-operator'  # same display name must not grant access
    assert get_status(app,body).status_code==404
    assert cancel(app,body).status_code==404
    app.user['rol']='SUPERVISOR'
    assert get_status(app,body).status_code==200
    app.user['country']='ecuador'
    assert get_status(app,body).status_code==403
    assert app.client.get('/api/operations/'+body['operacion_id']+'/status').status_code==404
    assert app.state.calls==1


def test_offline_status_returns_service_unavailable_without_stale_history(recovery_app,monkeypatch):
    app=recovery_app;body=request_body()
    assert app.client.post('/api/operations',json=body).status_code==201
    def offline(*args,**kwargs):raise StorageError('Synthetic network outage')
    monkeypatch.setattr(app.db,'operation',offline)
    response=get_status(app,body)
    assert response.status_code==503 and response.headers['cache-control']=='no-store'
    assert app.state.calls==1


def test_opening_requires_a_stable_id_before_any_write_or_command(recovery_app):
    app=recovery_app;body=request_body();body.pop('operacion_id')
    assert app.client.post('/api/operations',json=body).status_code==422
    assert app.state.calls==0 and app.db.operations().empty


def test_an_old_uuid_outside_the_history_page_still_blocks_an_opening(recovery_app):
    app=recovery_app;body=request_body()
    assert app.client.post('/api/operations',json=body).status_code==201
    history=app.db._read('operaciones')
    history.loc[0,'fecha_hora']='2000-01-01 00:00:00'
    template=history.iloc[0].to_dict()
    recent=[dict(template,id=str(i+2),operacion_id=str(uuid.uuid4()),fecha_hora='2026-11-16 20:00:00') for i in range(5000)]
    app.db._write('operaciones',pd.concat([history,pd.DataFrame(recent)],ignore_index=True))
    assert body['operacion_id'] not in app.db.operations().operacion_id.values
    assert get_status(app,body).json()['estado_barrera']=='CONFIRMADA'
    assert app.client.post('/api/operations',json=body).status_code==409
    assert app.state.calls==1 and len(app.db._read('operaciones'))==5001


def test_local_cache_failure_after_remote_acceptance_does_not_lose_history_or_open(recovery_app,monkeypatch):
    app=recovery_app;body=request_body()
    def fail_replace(*args):raise OSError('Synthetic cache disk failure')
    monkeypatch.setattr('src.storage.os.replace',fail_replace)
    assert app.client.post('/api/operations',json=body).status_code==503
    status=get_status(app,body).json()
    assert status['estado_barrera']=='SOLICITADA' and status['barrera_abierta'] is None
    assert app.client.post('/api/operations',json=body).status_code==409
    assert app.state.calls==0 and len(app.db.operations())==1


def test_http_controller_receives_the_same_id_and_timeout_never_retries(monkeypatch):
    calls=[];identifier=str(uuid.uuid4())
    def timeout(request,timeout):
        calls.append(request)
        assert request.get_header('Idempotency-key')==identifier
        assert json.loads(request.data)['operacion_id']==identifier
        raise TimeoutError('Synthetic controller ACK lost')
    monkeypatch.setattr('urllib.request.build_opener',lambda *handlers:SimpleNamespace(open=timeout))
    controller=HttpBarrier('https://synthetic.invalid/open','synthetic-token-not-a-credential')
    assert not controller.open_operation(identifier,'Synthetic Gate','APERTURA_MANUAL')
    assert len(calls)==1


def test_controller_redirect_cannot_send_a_second_command_or_forward_credentials(monkeypatch):
    calls=[];real_builder=urllib.request.build_opener
    class FakeHTTPS(urllib.request.HTTPSHandler):
        def https_open(self,request):
            calls.append(request)
            headers=Message();headers['Location']='https://other-synthetic.invalid/open'
            response=urllib.response.addinfourl(io.BytesIO(b'redirect'),headers,request.full_url,302)
            response.msg='Found'
            return response
    monkeypatch.setattr(urllib.request,'build_opener',lambda *handlers:real_builder(*handlers,FakeHTTPS()))
    controller=HttpBarrier('https://synthetic.invalid/open','synthetic-token-not-a-credential')
    assert not controller.open_operation(str(uuid.uuid4()),'Synthetic Gate','APERTURA_MANUAL')
    assert len(calls)==1 and calls[0].full_url=='https://synthetic.invalid/open'
