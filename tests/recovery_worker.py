"""Crash a real operation handler at a durable boundary, then restart independently."""
from pathlib import Path
import json
import os
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from _recovery_support import FakeGitHub
from src import github_storage
from src.storage import CsvStore
from src.access_control import AccessDecision
from api import schemas
from api.routers import recognition
from fastapi import BackgroundTasks,HTTPException,Response

phase,directory,operation_id=sys.argv[1:]
directory=Path(directory)
os.environ.update(SIRAP_DATA_GITHUB_TOKEN='synthetic-test-token-not-a-credential',SIRAP_GITHUB_REQUIRED='1')
remote=FakeGitHub(directory/'remote.sqlite')
github_storage._verify_private_repository=lambda:None
github_storage._request=remote.request
db=CsvStore(tempfile.mkdtemp(prefix='fresh-cache-',dir=directory))
recognition.get_store=lambda:db
recognition._decide=lambda *args:AccessDecision('AUTORIZADO','Synthetic authorization','test','BLANCA')
ledger=directory/'device_commands.jsonl'

class Barrier:
    simulated=True

    def open(self, gate, action):
        with ledger.open('a') as handle:
            handle.write(json.dumps({'id':operation_id,'gate':gate,'action':action})+'\n')
            handle.flush();os.fsync(handle.fileno())
        if phase=='actuated':os._exit(74)
        return True

recognition.get_barrier=lambda:Barrier()
body=schemas.OperationIn(country='usa',jurisdiction='CA',garita='Synthetic Gate',
    tipo_movimiento='ENTRADA',accion='APERTURA_MANUAL',placa_final='DEMO123',origen='MANUAL',
    motivo='Synthetic recovery verification',operacion_id=operation_id)
user=dict(usuario='synthetic-operator',nombre='Synthetic operator',rol='OPERADOR',country='usa')
if phase=='accepted':
    original=db.log_operation
    def stop_after_acceptance(**options):
        original(**options);os._exit(73)
    db.log_operation=stop_after_acceptance
elif phase=='committed':
    original=db.update_operation_state
    def stop_after_confirmation(*args):
        original(*args);os._exit(75)
    db.update_operation_state=stop_after_confirmation

if phase=='resume':
    recovered=recognition.operation_status(operation_id,Response(),country='usa',user=user)
    try:
        recognition.register_operation(body,BackgroundTasks(),user)
        raise AssertionError('A durable UUID was dispatched a second time')
    except HTTPException as error:
        assert error.status_code==409
    print(json.dumps(dict(status=recovered.model_dump(),history_rows=len(db.operations()),
                         device_commands=len(ledger.read_text().splitlines()) if ledger.exists() else 0)))
else:
    recognition.register_operation(body,BackgroundTasks(),user)
    raise AssertionError('The selected forced-crash boundary was not reached')
