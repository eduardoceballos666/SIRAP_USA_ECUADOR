"""USA integration tests: synthetic identities and image buffers; no private lists or hardware."""
from dataclasses import replace
from io import BytesIO
import json
from types import SimpleNamespace
import uuid

import numpy as np
from PIL import Image
import pytest
from fastapi.testclient import TestClient

from api import main, deps
from api.recognition_evidence import EvidenceStore
from api.routers import recognition, reports
from src.model import Recognition, PlateDetector
from src.plate_identity import normalize_identity, identity_from_key
from src import usa_jurisdiction
from src.usa_jurisdiction import STATE_ABBR_TO_NAME, match_printed_dc, match_state_name, read_usa_jurisdiction, select_evidence
from src.access_control import decide_usa_access
from src.storage import CsvStore, StorageError

def test_country_caches_do_not_duplicate_default_profile(monkeypatch):
    marker=object()
    monkeypatch.setattr(deps,'_shared_pipeline',lambda:SimpleNamespace(for_country=lambda *args:marker))
    deps.get_pipeline.cache_clear()
    try:
        assert deps.get_pipeline() is deps.get_pipeline('ecuador') is marker
        assert deps.get_config() is deps.get_config('ecuador')
        assert deps.get_config('usa')['detector']['confidence']==.70
        assert deps.get_config('ecuador')['detector']['conf_minima']==.70
    finally:
        deps.get_pipeline.cache_clear()

def test_explicit_model_directory_is_never_replaced_by_a_download(tmp_path,monkeypatch):
    from src.usa_pipeline import ensure_detector
    monkeypatch.setenv('SIRAP_USA_DETECTOR_DIR',str(tmp_path))
    def forbidden(*args,**kwargs): raise AssertionError('Explicit model must not be overwritten')
    monkeypatch.setattr('src.usa_pipeline.requests.get',forbidden)
    (tmp_path/'openvino_model.xml').write_text('Wrong model')
    with pytest.raises(ValueError,match='semilla 2'):
        ensure_detector(tmp_path)
    assert (tmp_path/'openvino_model.xml').read_text()=='Wrong model'

def test_native_state_ocr_parses_tsv_without_losing_quotes(monkeypatch):
    from src.usa_jurisdiction import _tesseract_data
    def result(*args,**kwargs):
        return SimpleNamespace(stdout=b'level\ttext\tconf\n5\tVirginia\t90\n5\t"\t10\n')
    monkeypatch.setattr('src.usa_jurisdiction.subprocess.run',result)
    data=_tesseract_data(np.zeros((15,40),np.uint8),7,'')
    assert data['text']==['Virginia','"']

def test_pipeline_reads_all_candidates_without_ecuador_substitutions():
    from src.usa_pipeline import USAPipeline
    from src.model import Detection
    class Detector:
        name='RT-DETRv2-S (test stub)'
        def detect(self,image,max_detections):
            return [Detection((5,5,45,25),.9),Detection((50,10,120,45),.8)]
    class Reader:
        def read(self,crop): return '01IOB8',.99,.99
    pipeline=USAPipeline(Detector(),Reader(),lambda crop:{'jurisdiction_abbreviation':'CA'})
    result=pipeline.recognize_many(np.zeros((100,160,3),np.uint8))
    assert len(result)==2
    assert result[0].box==(50,10,120,45)
    assert all(r.identity_key=='US:CA:01IOB8' for r in result)
    adapted=pipeline.for_country('ecuador')
    assert adapted.detector is pipeline.detector
    assert adapted.reader is pipeline.reader
    assert adapted._lock is pipeline._lock

def test_same_weights_apply_only_country_specific_ocr_rules():
    from src.usa_pipeline import USAPipeline
    from src.model import Detection
    class Detector:
        name='Shared detector (test stub)'
        def detect(self,image,max_detections): return [Detection((5,5,100,40),.9)]
    class Reader:
        def read(self,crop): return 'ABC1234',.99,.99
    usa=USAPipeline(Detector(),Reader(),lambda crop:{'jurisdiction_abbreviation':'CA'})
    ecuador=usa.for_country('ecuador')
    image=np.zeros((100,160,3),np.uint8)
    ec=ecuador.recognize(image);us=usa.recognize(image)
    assert ec.plate=='ABC-1234' and ec.country=='ecuador' and ec.jurisdiction is None
    assert us.plate=='ABC1234' and us.identity_key=='US:CA:ABC1234'
    assert ecuador.detector is usa.detector

def reading(state='CA',plate='DEMO123',**changes):
    identity=normalize_identity(plate,'usa',state) if state else None
    values=dict(plate=plate,plate_raw=plate,ocr_confidence=.94,ocr_mean_confidence=.99,det_confidence=.70,
        box=(10.,10.,100.,50.),detector='RT-DETRv2-S/OpenVINO (test stub)',country='usa',jurisdiction=state,
        identity_key=identity.key if identity else None,lookup_key=identity.lookup_key if identity else None)
    values.update(changes)
    return Recognition(**values)

@pytest.mark.parametrize('raw,state,serial', [('01I-OB8','CA','01IOB8'),('im emo','VA','IMEMO'),('DEMO123','NY','DEMO123')])
def test_us_identity_preserves_characters(raw,state,serial):
    identity=normalize_identity(raw,'usa',state)
    assert identity.serial==serial
    assert identity_from_key(identity.key)==identity

@pytest.mark.parametrize('country,state', [('usa',None),('usa','ZZ'),('ecuador','CA'),('invalid',None)])
def test_missing_or_conflicting_profile_rejected(country,state):
    with pytest.raises(ValueError):
        normalize_identity('ABC1234',country,state)

def test_all_states_and_dc_have_consistent_names():
    from src.plate_identity import US_STATES
    assert set(STATE_ABBR_TO_NAME)==US_STATES
    assert len(US_STATES)==51
    assert match_state_name(['WEST','VIRGINIA'],[95.,95.])['code']=='WV'
    assert match_state_name(['NEW','YORK','VIRGINIA'],[95.]*3) is None
    assert select_evidence([dict(view='one',words=['TEXAS'],confidences=[95.]),
                            dict(view='two',words=['CALIFORNIA'],confidences=[95.])])[0] is None

def obs(view,*words):
    return dict(view=view,text=' '.join(words),words=list(words),confidences=[95.]*len(words))

def test_district_of_columbia_is_not_read_as_washington_state():
    # Word lists copied from the real OCR of U.S. plate crops: D.C. plates print "WASHINGTON, D.C.".
    dc=[obs('header_0_gray_psm7','FI','WASHINGTON','DC','A'),
        obs('full_plate','WASHINGTONDC','DPLBO','TAXATIONWITHOUTREPRESENTATION'),
        obs('header_1_otsu_psm7','RIE','WASHINGTON')]
    selected,status=select_evidence(dc)
    assert (selected['code'],status)==('DC','name_read')
    assert select_evidence([obs('full_plate','SWASHINGTONDC','DD')])[0]['code']=='DC'
    assert select_evidence([obs('header_0_gray_psm7','WASHINGTON','D','C')])[0]['code']=='DC'
    assert match_printed_dc(['WASHINGTON'],[95.]) is None

def test_washington_state_is_still_read_and_a_dc_slogan_vetoes_it():
    wa=[obs('header_0_gray_psm7','WASHINGTON'),obs('full_plate','WASHINGTON','AK','EVERGREENSTATEE')]
    selected,status=select_evidence(wa)
    assert (selected['code'],status)==('WA','name_read')
    # "DC" not read at all but the District's slogan is: abstain instead of assigning the wrong state.
    veto=[obs('header_0_gray_psm7','WASHINGTON'),obs('full_plate','WASHINGTON','TAXATIONWITHOUTREPRESENTATION')]
    assert select_evidence(veto)==(None,'state_not_read')
    # The slogan never assigns a state by itself.
    assert select_evidence([obs('full_plate','TAXATIONWITHOUTREPRESENTATION')])[0] is None

def test_glued_multiword_names_are_exact_readings():
    # Real OCR glues the words of a printed name together, or attaches a stray letter to it.
    for token,code in (('NORTHCAROLINA','NC'),('ANORTHCAROLINA','NC'),('SOUTHCAROLINA','SC'),
                       ('NEWMEXICO','NM'),('WESTVIRGINIA','WV'),('NEWYORKST','NY')):
        match=match_state_name([token],[90.])
        assert (match['code'],match['score'])==(code,1.0),token
    # Words split over several tokens still work, and single-word names are not matched inside longer words.
    assert match_state_name(['NORTH','CAROLINA'],[90.,90.])['code']=='NC'
    assert match_state_name(['ARKANSAS'],[90.])['code']=='AR'
    assert match_state_name(['TEXASRANGERS'],[90.]) is None
    # The window is the smallest one holding the name: a neighbouring word is not absorbed into it.
    assert match_state_name(['NEW','YORK','VIRGINIA'],[95.]*3) is None
    assert match_state_name(['NEWYORK','VIRGINIA'],[95.]*2) is None
    # A glued name that Tesseract is not confident about is ignored.
    assert match_state_name(['NORTHCAROLINA'],[10.]) is None
    # One glued reading in one view is now enough (it is an exact match, like a spaced one).
    assert select_evidence([obs('footer_0_gray_psm7','ANORTHCAROLINA')])[0]['code']=='NC'

def test_footer_views_run_only_when_the_first_pass_reads_nothing(monkeypatch):
    monkeypatch.setattr(usa_jurisdiction.shutil,'which',lambda name:'/usr/bin/tesseract')
    plate=np.full((120,200,3),255,np.uint8)
    calls=[]
    def fake(first_pass_words,footer_words):
        def observe(views):
            names=[view[0] for view in views]; calls.append(names)
            words=footer_words if names[0].startswith('footer_') else first_pass_words
            return [obs(name,*words) for name in names]
        return observe
    # Nothing readable in the first pass: the bottom bands are read and name the state.
    monkeypatch.setattr(usa_jurisdiction,'_observe',fake(['XQZ'],['ANORTHCAROLINA']))
    result=read_usa_jurisdiction(plate)
    assert result['jurisdiction_abbreviation']=='NC' and result['jurisdiction_status']=='name_read'
    assert result['jurisdiction_ocr_source'].startswith('footer_')
    assert len(calls)==2 and len(calls[1])==8 and not any(n.startswith('footer_') for n in calls[0])
    # Already read in the first pass: no second pass, same latency as before.
    calls.clear()
    monkeypatch.setattr(usa_jurisdiction,'_observe',fake(['TEXAS'],['ANORTHCAROLINA']))
    result=read_usa_jurisdiction(plate)
    assert result['jurisdiction_abbreviation']=='TX' and len(calls)==1
    # Nothing anywhere: abstain.
    calls.clear()
    monkeypatch.setattr(usa_jurisdiction,'_observe',fake(['XQZ'],['XQZ']))
    result=read_usa_jurisdiction(plate)
    assert (result['jurisdiction_abbreviation'],result['jurisdiction_status'])==('','state_not_read') and len(calls)==2

@pytest.mark.parametrize('shape',[(360,640),(640,480)])
def test_padded_model_restores_native_box(shape):
    class Compiled:
        def output(self,i): return i
        def __call__(self,inputs):
            return {0:np.array([[[10.]]]),1:np.array([[[.5,.25,.2,.1]]])}
    detector=PlateDetector.__new__(PlateDetector)
    detector.imgsz=640;detector.manifest={'bbox_coordinate_space':'padded_input'}
    detector.compiled_model=Compiled();detector.class_id=0;detector.conf=.7
    result=detector.detect(np.zeros((*shape,3),np.uint8))
    assert result[0].box==pytest.approx((256.,128.,384.,192.),abs=.0001)

@pytest.fixture
def evidence():
    clock=[100.]
    store=EvidenceStore(clock=lambda:clock[0])
    def record(rec=None,frame='a',image='image-a',**changes):
        args=dict(owner='operator',gate='Gate',session='session',frame_id=frame,
                  image_sha256=image,received_at=clock[0])
        args.update(changes)
        return store.record([rec or reading()],**args)[0]
    return store,clock,record

def test_distinct_frame_and_image_required(evidence):
    store,clock,record=evidence
    assert not record().confirmed
    clock[0]+=1
    assert not record(frame='b').confirmed
    assert not record(frame='a',image='image-b').confirmed
    assert record(frame='b',image='image-b').confirmed

def test_state_change_and_low_confidence_interrupt_confirmation(evidence):
    _,clock,record=evidence
    record()
    clock[0]+=1
    assert not record(reading(state='NY'),frame='b',image='image-b').confirmed
    clock[0]+=1
    assert not record(frame='c',image='image-c').confirmed
    record(reading(ocr_confidence=.9399),frame='d',image='image-d')
    assert not record(frame='e',image='image-e').confirmed

def test_window_owner_gate_session_and_expiration(evidence):
    store,clock,record=evidence
    first=record()
    assert not record(frame='b',image='b',owner='another').confirmed
    assert not record(frame='c',image='c',gate='Another Gate').confirmed
    assert not record(frame='d',image='d',session='another-session').confirmed
    clock[0]+=7.5001
    assert not record(frame='e',image='e').confirmed
    clock[0]+=30.001
    with pytest.raises(ValueError): store.get(first.id,owner='operator',gate='Gate')

def test_only_one_parallel_claim_and_retry_after_failed_persistence(evidence):
    store,clock,record=evidence
    record();clock[0]+=1
    second=record(frame='b',image='b')
    third=record(frame='c',image='c')
    store.get(second.id,owner='operator',gate='Gate',claim=True)
    with pytest.raises(ValueError): store.get(third.id,owner='operator',gate='Gate',claim=True)
    store.release(second.id)
    store.get(third.id,owner='operator',gate='Gate',claim=True)
    store.consume(third)
    with pytest.raises(ValueError): store.get(second.id,owner='operator',gate='Gate',claim=True)

def jdpower_record(serial,state,**changes):
    values=dict(lookup_status='found',vehicle_title='2013 Honda Civic',vehicle_body_type='Sedan 4D LX I4',specs_exterior='Taffeta White')
    values.update(changes)
    return recognition.usa_jdpower._record(serial,state,**values)

@pytest.fixture
def usa_app(tmp_path,monkeypatch):
    monkeypatch.delenv('SIRAP_DATA_GITHUB_TOKEN',raising=False)
    monkeypatch.setenv('SIRAP_GITHUB_REQUIRED','0')
    db=CsvStore(tmp_path)
    db.add_garita('Gate','Synthetic gate')
    db.upsert_vehicle('US:CA:DEMO123','Example','Model','Blue','CAMION','Synthetic owner','Synthetic carrier')
    db.set_authorization('US:CA:DEMO123','BLANCA','Synthetic permission')
    db.upsert_vehicle('US:NY:DEMO123','Example','Model','Red','CAMION','Another synthetic owner','Carrier')
    db.set_authorization('US:NY:DEMO123','RESTRINGIDA','Synthetic restriction')
    current={'usuario':'operator','nombre':'Test operator','rol':'ADMINISTRADOR','country':'usa'}
    state={'reading':reading()}
    class Pipeline:
        detector=SimpleNamespace(name='RT-DETRv2-S/OpenVINO (test stub)',is_model=True)
        reader=SimpleNamespace(model_name='OCR (test stub)')
        def recognize_many(self,image): return [replace(state['reading'],crop=image[:40,:80])]
    pipeline=Pipeline()
    class Barrier:
        simulated=True
        calls=0
        succeeds=True
        def open(self,*args):
            self.calls+=1
            return self.succeeds
    barrier=Barrier();exported=[]
    monkeypatch.setattr(main,'get_store',lambda:db)
    monkeypatch.setattr(main,'get_pipeline',lambda *args:pipeline)
    monkeypatch.setattr(recognition,'get_store',lambda:db)
    monkeypatch.setattr(reports,'get_store',lambda:db)
    monkeypatch.setattr(recognition,'get_pipeline',lambda *args:pipeline)
    monkeypatch.setattr(reports,'get_pipeline',lambda *args:pipeline)
    monkeypatch.setattr(recognition,'get_barrier',lambda:barrier)
    monkeypatch.setattr(recognition,'evidence_store',EvidenceStore())
    monkeypatch.setattr(recognition,'append_detection',lambda row:exported.append(row))
    def forbidden(*args): raise AssertionError('USA must not query SRI')
    monkeypatch.setattr(recognition,'_query_sri',forbidden)
    monkeypatch.setattr(recognition,'enrich_detection',forbidden)
    jdpower=SimpleNamespace(calls=[],record=None,error=None)
    def fake_lookup(serial,state):
        jdpower.calls.append((serial,state))
        if jdpower.error: raise jdpower.error
        return jdpower.record or jdpower_record(serial,state)
    monkeypatch.setattr(recognition.usa_jdpower,'lookup',fake_lookup)
    from api.routers import admin
    monkeypatch.setattr(admin,'get_store',lambda:db)
    previous=dict(main.app.dependency_overrides)
    main.app.dependency_overrides[deps.current_user]=lambda:dict(current)
    with TestClient(main.app) as client:
        yield SimpleNamespace(client=client,db=db,barrier=barrier,current=current,state=state,exported=exported,jdpower=jdpower)
    main.app.dependency_overrides.clear();main.app.dependency_overrides.update(previous)

def frame(app,color,index):
    image=BytesIO();Image.new('RGB',(300,200),color).save(image,format='PNG')
    response=app.client.post('/api/recognize',data={'country':'usa','garita':'Gate',
        'capture_session':'test-capture','frame_id':str(index)},files={'file':('frame.png',image.getvalue(),'image/png')})
    assert response.status_code==200,response.text
    return response.json()

def confirmed(app):
    first=frame(app,'red',1)
    assert not first['decision']['permite_apertura']
    second=frame(app,'blue',2)
    assert second['recognition']['temporal_confirmed']
    return second['recognition']['evidence_id']

def operation(evidence=None,**changes):
    body=dict(country='usa',jurisdiction='CA',garita='Gate',tipo_movimiento='ENTRADA',
        accion='APERTURA_AUTOMATICA',placa_final='DEMO123',origen='DETECCION',evidence_id=evidence,
        confianza_ocr=1.,det_confidence=1.,operacion_id=str(uuid.uuid4()))
    body.update(changes);return body

def test_two_real_api_requests_open_once_and_persist_trusted_fields(usa_app):
    app=usa_app;evidence_id=confirmed(app)
    response=app.client.post('/api/operations',json=operation(evidence_id,confianza_ocr=.01,det_confidence=.01))
    assert response.status_code==201,response.text
    assert response.json()['barrera_abierta']
    assert app.barrier.calls==1
    row=app.db.operations().iloc[0]
    assert (row.country,row.jurisdiction,row.identity_key)==('usa','CA','US:CA:DEMO123')
    assert row.confianza_ocr==pytest.approx(.94)
    assert float(row.det_confidence)==pytest.approx(.70)
    assert len(json.loads(row.evidence_json)['frames'])==2
    assert app.exported[0]['country']=='usa'
    assert app.client.post('/api/operations',json=operation(evidence_id)).status_code==409
    assert app.barrier.calls==1

@pytest.mark.parametrize('changes',[{'jurisdiction':'NY'},{'garita':'Other Gate'},
    {'placa_final':'OTHER123'},{'origen':'MANUAL'},{'evidence_id':None}])
def test_client_cannot_replace_state_plate_gate_or_evidence(usa_app,changes):
    evidence_id=confirmed(usa_app)
    assert usa_app.client.post('/api/operations',json=operation(evidence_id,**changes)).status_code==409
    assert usa_app.barrier.calls==0

def test_another_operator_cannot_use_receipt(usa_app):
    evidence_id=confirmed(usa_app)
    usa_app.current['usuario']='different-operator'
    assert usa_app.client.post('/api/operations',json=operation(evidence_id)).status_code==409
    assert usa_app.barrier.calls==0

def test_low_model_confidence_cannot_be_overridden_by_client(usa_app):
    usa_app.state['reading']=reading(ocr_confidence=.93)
    frame(usa_app,'red',1)
    out=frame(usa_app,'blue',2)
    assert not out['recognition']['temporal_confirmed']
    assert usa_app.client.post('/api/operations',json=operation(out['recognition']['evidence_id'])).status_code==409
    assert usa_app.barrier.calls==0

def test_revoked_permission_is_rechecked_before_opening(usa_app):
    evidence_id=confirmed(usa_app)
    usa_app.db.revoke_authorization('US:CA:DEMO123')
    assert usa_app.client.post('/api/operations',json=operation(evidence_id)).status_code==409
    assert usa_app.barrier.calls==0

def test_storage_failure_never_opens_and_releases_unused_confirmation(usa_app,monkeypatch):
    app=usa_app;evidence_id=confirmed(app);original=app.db.log_operation
    def fail(**kwargs): raise StorageError('Synthetic persistence failure')
    monkeypatch.setattr(app.db,'log_operation',fail)
    body=operation(evidence_id)
    assert app.client.post('/api/operations',json=body).status_code==503
    assert app.barrier.calls==0
    monkeypatch.setattr(app.db,'log_operation',original)
    assert app.client.post('/api/operations',json=body).status_code==201
    assert app.barrier.calls==1

def test_failed_barrier_is_not_retried_using_the_same_evidence(usa_app):
    evidence_id=confirmed(usa_app);usa_app.barrier.succeeds=False
    assert usa_app.client.post('/api/operations',json=operation(evidence_id)).status_code==502
    assert usa_app.client.post('/api/operations',json=operation(evidence_id)).status_code==409
    assert usa_app.barrier.calls==1

def test_us_lookup_is_local_and_unknown_state_stays_manual(usa_app):
    app=usa_app
    result=app.client.post('/api/plates/vehicle-data',json={'placa':'DEMO123','country':'usa','jurisdiction':'CA'})
    assert result.status_code==202
    lookup=app.client.get('/api/plates/vehicle-data/'+result.json()['request_id']).json()
    assert lookup['fuentes']['sri']=='no_aplica'
    assert lookup['vehiculo']['identity_key']=='US:CA:DEMO123'
    app.state['reading']=reading(state=None)
    data=frame(app,'green',1)
    assert not data['decision']['permite_apertura']
    assert not data['recognition']['identity_key']
    response=app.client.post('/api/operations',json=operation(data['recognition']['evidence_id'],
        accion='SOLO_REGISTRO',jurisdiction=None))
    assert response.status_code==201,response.text
    assert app.db.operations().iloc[0].country=='usa'

def vehicle_data(app,plate,state='CA'):
    started=app.client.post('/api/plates/vehicle-data',json={'placa':plate,'country':'usa','jurisdiction':state})
    assert started.status_code==202
    return started.json(),app.client.get('/api/plates/vehicle-data/'+started.json()['request_id']).json()

def test_us_lookup_adds_jdpower_fields_for_an_unregistered_plate(usa_app):
    started,lookup=vehicle_data(usa_app,'6ZGY984')
    assert started['estado']=='consultando' and lookup['estado']=='completado'
    assert usa_app.jdpower.calls==[('6ZGY984','CA')]
    assert lookup['fuentes']=={'local':'consultado','sri':'no_aplica','jdpower':'encontrado'}
    assert {k:lookup['vehiculo'][k] for k in ('state','vehicle_title','vehicle_body_type','specs_exterior')}=={
        'state':'CA','vehicle_title':'2013 Honda Civic','vehicle_body_type':'Sedan 4D LX I4','specs_exterior':'Taffeta White'}
    assert 'lookup_url' not in lookup['vehiculo'] and 'specs' not in lookup['vehiculo']

def test_us_lookup_keeps_the_local_record_beside_jdpower_data(usa_app):
    _,lookup=vehicle_data(usa_app,'DEMO123')
    assert lookup['vehiculo']['identity_key']=='US:CA:DEMO123' and lookup['vehiculo']['marca']=='Example'
    assert lookup['vehiculo']['vehicle_title']=='2013 Honda Civic'

@pytest.mark.parametrize('status',['access_limited_403','access_limited_429','http_404','error','browser_unavailable'])
def test_us_lookup_falls_back_to_local_data_when_jdpower_gives_none(usa_app,status):
    usa_app.jdpower.record=jdpower_record('DEMO123','CA',lookup_status=status,vehicle_title='',vehicle_body_type='',specs_exterior='')
    _,lookup=vehicle_data(usa_app,'DEMO123')
    assert lookup['estado']=='completado' and lookup['fuentes']['jdpower']==status
    assert lookup['vehiculo']['marca']=='Example' and 'vehicle_title' not in lookup['vehiculo']

def test_us_lookup_survives_an_unexpected_provider_error(usa_app):
    usa_app.jdpower.error=RuntimeError('boom')
    _,lookup=vehicle_data(usa_app,'DEMO123')
    assert lookup['estado']=='completado' and lookup['fuentes']['jdpower']=='error'
    assert lookup['vehiculo']['identity_key']=='US:CA:DEMO123'

def test_us_lookup_does_not_contact_jdpower_when_switched_off(usa_app,monkeypatch):
    monkeypatch.setattr(recognition.usa_jdpower,'lookup_enabled',lambda config:False)
    started,lookup=vehicle_data(usa_app,'DEMO123')
    assert started['estado']=='completado' and usa_app.jdpower.calls==[]
    assert lookup['fuentes']['jdpower']=='desactivado' and 'vehicle_title' not in lookup['vehiculo']

def test_admin_lists_and_history_distinguish_same_serial_in_different_states(usa_app):
    app=usa_app
    for state in ('CA','NY'):
        response=app.client.post('/api/plates/verify',json={'country':'usa','jurisdiction':state,'placa':'DEMO123'})
        assert response.status_code==200,response.text
        assert response.json()['decision']['vehiculo']['jurisdiction']==state
    rows=app.client.get('/api/admin/vehiculos').json()
    assert {r['identity_key'] for r in rows}=={'US:CA:DEMO123','US:NY:DEMO123'}
    assert app.client.post('/api/plates/verify',json={'placa':'DEMO123','country':'usa'}).status_code==422

def test_ecuador_and_us_authorizations_never_collide(db):
    db.upsert_vehicle('ABC-1234');db.set_authorization('ABC-1234','BLANCA')
    result=decide_usa_access('ABC1234','CA',.99,db,det_confidence=.99,temporal_confirmed=True)
    assert result.resultado=='NO_REGISTRADO'
    assert not result.permite_apertura

def test_profile_scopes_registry_owners_history_and_demo(usa_app):
    app=usa_app
    app.db.upsert_vehicle('ABC-1234',propietario='Ecuador synthetic owner')
    app.db.load_demo_history(2,country='ecuador')
    assert app.client.post('/api/admin/demo',params={'n':3}).json()['creadas']==3
    rows=app.client.get('/api/operations').json()
    assert len(rows)==3 and all(row['country']=='usa' for row in rows)
    vehicles=app.client.get('/api/admin/vehiculos').json()
    assert all(row['country']=='usa' for row in vehicles)
    owners=app.client.get('/api/admin/propietarios').json()
    assert 'Ecuador synthetic owner' not in {row['nombre'] for row in owners}
    assert app.client.get('/api/operations',params={'country':'ecuador'}).status_code==403
    assert app.client.delete('/api/admin/demo').json()['borradas']==3
    assert len(app.db.operations(country='ecuador'))==2
