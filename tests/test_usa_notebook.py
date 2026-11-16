"""USA notebook contract and diagnostics; synthetic images, no Hub token or device."""
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
import ast
import hashlib
import json

import numpy as np
from PIL import Image
import pytest

from src.model import Recognition
from src import usa_notebook as notebook
from src.plate_identity import normalize_identity


def synthetic_reading(state='CA', serial='DEMO123', confidence=.99):
    identity=normalize_identity(serial,'usa',state) if state else None
    return Recognition(plate=serial,plate_raw=serial,ocr_confidence=confidence,
        ocr_mean_confidence=confidence,det_confidence=.9,box=(10,10,150,70),
        country='usa',jurisdiction=state,identity_key=identity.key if identity else None,
        lookup_key=identity.lookup_key if identity else None,detector='Synthetic diagnostic model')


def synthetic_pipeline(reading=None):
    state={'reading':reading or synthetic_reading()}
    class Pipeline:
        detector=SimpleNamespace(is_model=True,name='Synthetic diagnostic model')
        def recognize_many(self,image):return [state['reading']]
    return Pipeline(),state


def reference_bundle(tmp_path,complete=True):
    images=tmp_path/'originales';images.mkdir()
    path=images/'synthetic.png';Image.new('RGB',(300,200),'green').save(path)
    frame=dict(photo=path.name,original_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        scene_complete_for_detector_scoring=complete,annotations=[dict(
        box_xyxy_original_pixels=[10,10,150,70],serial_gt='DEMO123',jurisdiction_gt='CA')])
    ref={'frames':[frame]};target=tmp_path/'referencia_humana_8_fotos.json'
    target.write_text(json.dumps(ref));return ref,target


def test_runtime_selection_rejects_seed_or_threshold_drift():
    selected=notebook.selected_checkpoint()
    assert notebook.validate_selection(selected)['seed']==2
    for key,value in [('seed',1),('detector_threshold',.60),('ocr_threshold',.90)]:
        changed={**selected,key:value}
        with pytest.raises(ValueError,match='seed 2'):notebook.validate_selection(changed)


def test_reference_limit_hashes_and_boxes_are_checked_before_inference(tmp_path):
    ref,path=reference_bundle(tmp_path)
    assert notebook.load_pilot_reference(tmp_path)[0]['frames'][0]['photo']=='synthetic.png'
    copy=deepcopy(ref);copy['frames']*=9;path.write_text(json.dumps(copy))
    with pytest.raises(ValueError,match='eight'):notebook.load_pilot_reference(tmp_path)
    copy=deepcopy(ref);copy['frames'][0]['original_sha256']='0'*64;path.write_text(json.dumps(copy))
    with pytest.raises(ValueError,match='hash'):notebook.load_pilot_reference(tmp_path)
    copy=deepcopy(ref);copy['frames'][0]['annotations'][0]['box_xyxy_original_pixels']=[0,0,500,70]
    path.write_text(json.dumps(copy))
    with pytest.raises(ValueError,match='outside'):notebook.load_pilot_reference(tmp_path)


def test_one_to_one_matching_preserves_false_positives_and_misses():
    annotations=[dict(box_xyxy_original_pixels=[0,0,20,20]),dict(box_xyxy_original_pixels=[40,0,60,20])]
    predictions=[dict(box=[0,0,20,20],det_confidence=.8),dict(box=[0,0,20,20],det_confidence=.9)]
    matched,unmatched=notebook.match_boxes(predictions,annotations)
    assert matched=={1:0} and unmatched=={1}


def test_runtime_session_reuses_actual_evidence_rules_and_full_state_identity():
    pipeline,state=synthetic_pipeline();clock=SimpleNamespace(now=0.)
    session=notebook.RuntimeSession(pipeline,clock=lambda:clock.now)
    red=np.zeros((100,160,3),np.uint8);blue=red.copy();blue[:,:,2]=255
    assert not session.observe(red,'one')[0]['temporal_confirmed']
    clock.now=1
    assert not session.observe(red,'two')[0]['temporal_confirmed']  # same RGB hash
    clock.now=2
    assert session.observe(blue,'three')[0]['temporal_confirmed']
    state['reading']=synthetic_reading(state='NY');clock.now=3
    assert not session.observe(red,'four')[0]['temporal_confirmed']
    clock.now=11
    assert not session.observe(blue,'five')[0]['temporal_confirmed']  # window expired
    state['reading']=synthetic_reading(confidence=.93);clock.now=12
    assert not session.observe(red,'six')[0]['temporal_confirmed']
    state['reading']=synthetic_reading(state=None);clock.now=13
    out=session.observe(blue,'seven')[0]
    assert not out['temporal_confirmed'] and not out['identity_key']
    assert out['confirmation_scope']=='local_diagnostic_only'


def test_real_http_pilot_keeps_rows_private_and_never_creates_access_operations(tmp_path,monkeypatch):
    reference_bundle(tmp_path)
    profile=dict(seed=2,artifact_repository='synthetic/model',artifact_revision='0'*40,
        detector_sha256={},metadata_sha256={},ocr_sha256={},packages={})
    monkeypatch.setattr(notebook,'runtime_profile',lambda pipeline:profile)
    pipeline,_=synthetic_pipeline()
    out=tmp_path/'private'
    report=notebook.evaluate_api_pilot(tmp_path,out,pipeline=pipeline)
    assert report['counts']['complete_scene_tp']==1
    assert report['counts']['serial_exact']==report['counts']['state_exact']==1
    assert report['counts']['pair_exact_confident']==1
    assert report['access_operations']==0 and not report['independent_final_test']
    summary=(out/'usa_seed2_pilot_summary.json').read_text()
    assert 'DEMO123' not in summary and 'synthetic.png' not in summary
    assert 'DEMO123' in (out/'usa_seed2_pilot_private_rows.csv').read_text()


def test_incomplete_scenes_are_not_scored_as_complete_detector_references(tmp_path,monkeypatch):
    reference_bundle(tmp_path,complete=False)
    monkeypatch.setattr(notebook,'runtime_profile',lambda pipeline:dict(seed=2,
        artifact_repository='synthetic/model',artifact_revision='0'*40,
        detector_sha256={},metadata_sha256={},ocr_sha256={},packages={}))
    pipeline,_=synthetic_pipeline()
    report=notebook.evaluate_api_pilot(tmp_path,tmp_path/'private',pipeline=pipeline)
    assert report['counts']['complete_scenes']==0
    assert report['counts']['complete_scene_tp']==report['counts']['complete_scene_fp']==0
    assert report['counts']['serial_exact']==1


def test_notebook_code_and_generated_scripts_compile_without_execution():
    path=Path(__file__).resolve().parents[1]/'notebooks/usa/sirap_backend_usa.ipynb'
    nb=json.loads(path.read_text())
    sources=[]
    for index,cell in enumerate(nb['cells']):
        if cell['cell_type']!='code':continue
        source=''.join(cell['source']);sources.append(source)
        tree=ast.parse(source,filename=f'usa-notebook-cell-{index}')
        compile(source,f'usa-notebook-cell-{index}','exec',flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)
        for node in ast.walk(tree):
            if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ('EDGE_RUNNER_SCRIPT','BRIDGE_SCRIPT') for t in node.targets):
                if isinstance(node.value,ast.Constant) and isinstance(node.value.value,str):
                    compile(node.value.value,'generated-camera-script','exec')
    joined='\n'.join(sources)
    assert 'Seed 1 selected by grouped Roboflow' not in joined
    assert 'ALPRPipeline(' not in joined
    assert 'RUN_RESEARCH_WORKFLOW = False' in joined
    assert 'RUN_FINAL_TEST_EVALUATION = False' in joined
    documentation='\n'.join(''.join(c['source']) for c in nb['cells'] if c['cell_type']=='markdown')
    assert 'The selected candidate is seed 1' not in documentation
    assert 'RUN_OPTUNA is enabled' not in documentation
