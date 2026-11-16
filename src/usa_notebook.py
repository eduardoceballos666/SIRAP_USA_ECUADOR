"""Notebook diagnostics that reuse the deployed USA model and API rules.

Real-image pilots are development checks. Synthetic access-flow tests never use
the operational registry or a physical barrier. No function publishes user data.
"""
from __future__ import annotations

from functools import lru_cache
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from statistics import NormalDist
import csv
import hashlib
import json
import math
import os
import subprocess
import sys
import tempfile
import time
import uuid

import numpy as np
from PIL import Image

from src.data_processing import clean_text, load_image, plate_distance
from src.model import Recognition
from src.plate_identity import US_STATES
from src.usa_pipeline import USAPipeline, selected_checkpoint, validate_detector
from src.utils import ROOT_DIR, load_config

DETECTOR_THRESHOLD = 0.70
OCR_THRESHOLD = 0.94
MAX_PILOT_IMAGES = 8


def validate_selection(selection=None):
    selection = selection or selected_checkpoint()
    if (selection.get('seed') != 2 or selection.get('detector_threshold') != DETECTOR_THRESHOLD
            or selection.get('ocr_threshold') != OCR_THRESHOLD):
        raise ValueError('This notebook requires seed 2, detection 0.70 and OCR 0.94.')
    return selection


@lru_cache(maxsize=1)
def load_runtime_pipeline():
    """Load precisely the provider used by the application, including its hash checks."""
    validate_selection()
    config = load_config('config/countries/usa.yaml')
    if config['detector']['confidence'] != DETECTOR_THRESHOLD or config['ocr']['confidence'] != OCR_THRESHOLD:
        raise ValueError('The USA configuration differs from the frozen notebook profile.')
    return USAPipeline.from_config(config)


def runtime_profile(pipeline=None):
    selection = validate_selection()
    pipeline = pipeline or load_runtime_pipeline()
    if pipeline.country != 'usa':
        raise ValueError('The USA notebook requires the USA interpretation profile.')
    directory = validate_detector(Path(pipeline.detector.model_path).parent)
    packages = {}
    for name in ('openvino', 'fast-plate-ocr', 'onnxruntime', 'opencv-python-headless'):
        try:
            packages[name] = version(name)
        except PackageNotFoundError:
            pass
    record = {key: selection[key] for key in ('seed', 'artifact_repository', 'artifact_revision',
              'detector_sha256', 'metadata_sha256', 'ocr_sha256')}
    return dict(record, country='usa', checkpoint=str(directory), threshold=DETECTOR_THRESHOLD,
                ocr_threshold=OCR_THRESHOLD, enabled_for_diagnostic_inference=True,
                independent_performance_qualified=False, packages=packages,
                model_selection_record=json.dumps(record, sort_keys=True))


class RuntimeSession:
    """The application evidence rules, isolated for local camera diagnostics.

    These receipts exist only in this process and cannot authorize the live API.
    The session never consults a whitelist, opens a barrier, or uploads an event.
    """
    def __init__(self, pipeline=None, clock=None):
        from api.recognition_evidence import EvidenceStore
        self.pipeline = pipeline or load_runtime_pipeline()
        self.clock = clock or time.monotonic
        self.evidence = EvidenceStore(window=7.5, ttl=30, clock=self.clock)
        self.session = str(uuid.uuid4())

    def observe(self, image_rgb, frame_id):
        received = self.clock()
        readings = self.pipeline.recognize_many(image_rgb)
        receipts = self.evidence.record(readings, owner='notebook-diagnostic',
            gate='local-diagnostic', session=self.session, frame_id=str(frame_id),
            image_sha256=hashlib.sha256(np.ascontiguousarray(image_rgb).tobytes()).hexdigest(),
            received_at=received)
        observations = []
        for receipt in receipts:
            reading = receipt.reading
            if reading.box is None:
                continue
            observations.append(dict(plate_text=reading.plate or '', plate_key=reading.identity_key or '',
                country='usa', jurisdiction=reading.jurisdiction, identity_key=reading.identity_key,
                ocr_confidence_min=reading.ocr_confidence, ocr_confidence_mean=reading.ocr_mean_confidence,
                det_confidence=reading.det_confidence, box=reading.box,
                confirmation_count=len(receipt.frames), temporal_confirmed=receipt.confirmed,
                confirmation_scope='local_diagnostic_only', model_seed=2))
        return observations


def box_iou(a, b):
    intersection = max(0., min(a[2], b[2])-max(a[0], b[0])) * max(0., min(a[3], b[3])-max(a[1], b[1]))
    area = lambda box: max(0., box[2]-box[0])*max(0., box[3]-box[1])
    union = area(a)+area(b)-intersection
    return intersection/union if union else 0.


def match_boxes(predictions, annotations, iou_threshold=0.50):
    """Greedy confidence-ordered, one-to-one matches; unmatched boxes remain false positives."""
    unmatched = set(range(len(annotations)))
    matches = {}
    order = sorted(range(len(predictions)), key=lambda i: predictions[i].get('det_confidence') or 0, reverse=True)
    for index in order:
        box = predictions[index].get('box')
        if box is None:
            continue
        score, target = max(((box_iou(box, annotations[j]['box_xyxy_original_pixels']), j)
                            for j in unmatched), default=(0., -1))
        if score >= iou_threshold:
            matches[index] = target
            unmatched.remove(target)
    return matches, unmatched


def load_pilot_reference(root, reference_path=None):
    """Accept at most eight reviewed source files and verify every original image hash."""
    root = Path(root).resolve()
    reference_path = Path(reference_path) if reference_path else root/'referencia_humana_8_fotos.json'
    if not reference_path.is_file():
        raise FileNotFoundError('Set PILOT8_ROOT to the extracted eight-photo bundle containing its human reference.')
    reference = json.loads(reference_path.read_text(encoding='utf-8'))
    frames = reference.get('frames', [])
    if not 1 <= len(frames) <= MAX_PILOT_IMAGES:
        raise ValueError('A development pilot must contain between one and eight source images.')
    if len({row['photo'] for row in frames}) != len(frames):
        raise ValueError('The reference repeats a source image.')
    if len({row['original_sha256'] for row in frames}) != len(frames):
        raise ValueError('The reference repeats an original image hash.')
    for frame in frames:
        path = (root/'originales'/frame['photo']).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError('A referenced source image is missing or outside PILOT8_ROOT.')
        if hashlib.sha256(path.read_bytes()).hexdigest() != frame['original_sha256']:
            raise ValueError(f"The original image does not match its reviewed hash: {frame['photo']}")
        with Image.open(path) as image:
            width, height = image.size
        if type(frame.get('scene_complete_for_detector_scoring')) is not bool:
            raise ValueError('Every image needs an explicit complete/incomplete reference flag.')
        for annotation in frame.get('annotations', []):
            box = annotation['box_xyxy_original_pixels']
            if (len(box) != 4 or not all(math.isfinite(x) for x in box)
                    or not 0 <= box[0] < box[2] <= width or not 0 <= box[1] < box[3] <= height):
                raise ValueError('A human-reference box is outside its original image.')
            state = annotation.get('jurisdiction_gt')
            if state and state not in US_STATES:
                raise ValueError('A reference jurisdiction is not a supported state/DC code.')
    return reference, reference_path


def wilson_interval(successes, trials):
    if not trials:
        return {'lower': None, 'upper': None, 'method': 'Wilson score 95%'}
    z = NormalDist().inv_cdf(.975)
    p, denominator = successes/trials, 1+z*z/trials
    center = (p+z*z/(2*trials))/denominator
    margin = z*math.sqrt(p*(1-p)/trials+z*z/(4*trials*trials))/denominator
    return {'lower': max(0., center-margin), 'upper': min(1., center+margin), 'method': 'Wilson score 95%'}


def image_bootstrap_interval(successes, trials, resamples=5000):
    successes, trials = np.asarray(successes, float), np.asarray(trials, float)
    rng = np.random.default_rng(20261116)
    sampled = rng.integers(0, len(trials), size=(resamples, len(trials)))
    numerators, denominators = successes[sampled].sum(axis=1), trials[sampled].sum(axis=1)
    estimates = numerators[denominators > 0]/denominators[denominators > 0]
    bounds = np.quantile(estimates, [.025, .975]).tolist() if len(estimates) else [None, None]
    return dict(lower=bounds[0], upper=bounds[1], method='paired image-cluster percentile bootstrap 95%', resamples=resamples)


def evaluate_api_pilot(root, output_dir, reference_path=None, pipeline=None):
    """Run the real /api/recognize handler on the reviewed photos in an isolated registry.

    No operational accounts, allowlists, SRI lookups, uploads, or barrier actions are used.
    A different capture session per still image prevents treating photos as temporal proof.
    """
    from contextlib import ExitStack
    from unittest.mock import patch
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from api.deps import current_user
    from api.recognition_evidence import EvidenceStore
    from api.routers import recognition
    from src.storage import CsvStore

    reference, reference_path = load_pilot_reference(root, reference_path)
    pipeline = pipeline or load_runtime_pipeline()
    profile = runtime_profile(pipeline)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_rows, image_counts = [], []
    start = time.perf_counter()
    counts = dict(source_images=len(reference['frames']), confirmed_plates=0, complete_scenes=0,
        complete_scene_tp=0, complete_scene_fn=0, complete_scene_fp=0, matched_plates=0,
        serial_exact=0, known_serials=0, serial_character_errors=0, reference_characters=0,
        state_exact=0, known_states=0, state_predictions_on_known=0, wrong_state_assignments=0,
        known_state_serial_pairs=0, pair_exact_confident=0)

    def forbidden(*args, **kwargs):
        raise AssertionError('External lookup or actuation is outside the eight-photo diagnostic.')

    with tempfile.TemporaryDirectory(prefix='sirap_pilot8_') as temporary, ExitStack() as stack:
        stack.enter_context(patch.dict(os.environ, {'SIRAP_GITHUB_REQUIRED':'0', 'SIRAP_DATA_GITHUB_TOKEN':''}))
        database = CsvStore(temporary)
        stack.enter_context(patch.object(recognition, 'get_store', lambda: database))
        stack.enter_context(patch.object(recognition, 'get_pipeline', lambda country='usa': pipeline))
        stack.enter_context(patch.object(recognition, 'get_barrier', forbidden))
        stack.enter_context(patch.object(recognition, 'append_detection', lambda row: None))
        stack.enter_context(patch.object(recognition, 'enrich_detection', forbidden))
        stack.enter_context(patch.object(recognition, '_query_sri', forbidden))
        stack.enter_context(patch.object(recognition, 'evidence_store', EvidenceStore()))
        app = FastAPI(telemetry={'auto_configure':False})
        app.include_router(recognition.router)
        app.dependency_overrides[current_user] = lambda: dict(usuario='pilot8-diagnostic',
            nombre='Isolated diagnostic', rol='OPERADOR', country='usa')
        with TestClient(app) as client:
            for frame in reference['frames']:
                path = Path(root)/'originales'/frame['photo']
                response = client.post('/api/recognize', data={'country':'usa', 'garita':'Diagnostic',
                    'capture_session':str(uuid.uuid4()), 'frame_id':frame['photo']},
                    files={'file':(frame['photo'], path.read_bytes(), 'image/jpeg')})
                if response.status_code != 200:
                    raise RuntimeError(f"The recognition handler failed for {frame['photo']}: HTTP {response.status_code}")
                result = response.json()
                candidates = result['candidates']
                if any(row['decision']['permite_apertura'] for row in candidates):
                    raise AssertionError('A still-photo pilot cannot authorize an opening.')
                predictions = [row['recognition'] for row in candidates if row['recognition'].get('box')]
                annotations = frame['annotations']
                matches, unmatched = match_boxes(predictions, annotations)
                counts['confirmed_plates'] += len(annotations)
                counts['matched_plates'] += len(matches)
                per_image = dict(serial_exact=0, known_serials=0, state_exact=0, known_states=0)
                if frame['scene_complete_for_detector_scoring']:
                    counts['complete_scenes'] += 1
                    counts['complete_scene_tp'] += len(matches)
                    counts['complete_scene_fn'] += len(unmatched)
                    counts['complete_scene_fp'] += len(predictions)-len(matches)
                for index, prediction in enumerate(predictions):
                    target = annotations[matches[index]] if index in matches else {}
                    serial_gt, state_gt = target.get('serial_gt'), target.get('jurisdiction_gt')
                    serial_ok = bool(serial_gt and clean_text(prediction['plate']) == clean_text(serial_gt))
                    state_ok = bool(state_gt and prediction.get('jurisdiction') == state_gt)
                    if serial_gt:
                        counts['known_serials'] += 1; per_image['known_serials'] += 1
                        counts['serial_exact'] += serial_ok; per_image['serial_exact'] += serial_ok
                        counts['serial_character_errors'] += plate_distance(prediction['plate'], serial_gt)
                        counts['reference_characters'] += len(clean_text(serial_gt))
                    if state_gt:
                        counts['known_states'] += 1; per_image['known_states'] += 1
                        counts['state_exact'] += state_ok; per_image['state_exact'] += state_ok
                        counts['state_predictions_on_known'] += bool(prediction.get('jurisdiction'))
                        counts['wrong_state_assignments'] += bool(prediction.get('jurisdiction') and not state_ok)
                    if serial_gt and state_gt:
                        counts['known_state_serial_pairs'] += 1
                        counts['pair_exact_confident'] += bool(serial_ok and state_ok and prediction['ocr_confidence'] >= OCR_THRESHOLD)
                    output_rows.append(dict(photo=frame['photo'], matched_reference=index in matches,
                        complete_scene=frame['scene_complete_for_detector_scoring'], serial_gt=serial_gt or '',
                        state_gt=state_gt or '', serial_pred=prediction.get('plate') or '',
                        state_pred=prediction.get('jurisdiction') or '', identity_key=prediction.get('identity_key') or '',
                        serial_exact=serial_ok, state_exact=state_ok, detector_confidence=prediction['det_confidence'],
                        ocr_min_character_probability=prediction['ocr_confidence'], box=json.dumps(prediction['box']),
                        temporal_confirmed=prediction.get('temporal_confirmed',False), opening_allowed=False))
                for index in sorted(unmatched):
                    target = annotations[index]
                    output_rows.append(dict(photo=frame['photo'], matched_reference=False,
                        complete_scene=frame['scene_complete_for_detector_scoring'], missed_reference=True,
                        serial_gt=target.get('serial_gt') or '', state_gt=target.get('jurisdiction_gt') or '',
                        serial_pred='', state_pred='', opening_allowed=False))
                image_counts.append(per_image)
        if not database.operations().empty:
            raise AssertionError('The real-image diagnostic must not create access operations.')

    intervals = {}
    for label, successes, trials in (('serial_exact','serial_exact','known_serials'), ('state_exact','state_exact','known_states')):
        intervals[label] = dict(wilson=wilson_interval(counts[successes],counts[trials]),
            image_cluster_bootstrap=image_bootstrap_interval([r[successes] for r in image_counts], [r[trials] for r in image_counts]))
    report = dict(scope='reused eight-photo development pilot through the real USA API',
        independent_final_test=False, original_images_reused=True, source_images_limit=MAX_PILOT_IMAGES,
        model={key:profile[key] for key in ('seed','artifact_repository','artifact_revision','detector_sha256','metadata_sha256','ocr_sha256')},
        detector_threshold=DETECTOR_THRESHOLD, ocr_threshold=OCR_THRESHOLD, counts=counts,
        confidence_intervals_95=intervals, packages=profile['packages'],
        reference_sha256=hashlib.sha256(reference_path.read_bytes()).hexdigest(),
        elapsed_seconds=time.perf_counter()-start, access_operations=0,
        notes=['Unresolved scenes are excluded from complete-scene detection counts.',
               'OCR denominators include only matched detections with a known reference for that field.',
               'The convenience set has prior review exposure; intervals do not remove this bias.',
               'No empty-scene false-alarm estimate, independent final test or physical barrier test.'])
    columns = list(dict.fromkeys(key for row in output_rows for key in row))
    with (output_dir/'usa_seed2_pilot_private_rows.csv').open('w',encoding='utf-8-sig',newline='') as handle:
        writer = csv.DictWriter(handle,fieldnames=columns);writer.writeheader();writer.writerows(output_rows)
    (output_dir/'usa_seed2_pilot_summary.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    return report


def run_access_flow_checks(output_dir):
    """Run the real API rule tests in a child process with synthetic data and barrier."""
    output_dir = Path(output_dir);output_dir.mkdir(parents=True,exist_ok=True)
    environment = dict(os.environ, SIRAP_GITHUB_REQUIRED='0', SIRAP_DATA_GITHUB_TOKEN='',
        OTEL_SDK_DISABLED='true', FASTAPI_OTEL_AUTO_CONFIGURE='false',
        HF_HUB_DISABLE_TELEMETRY='1', DO_NOT_TRACK='1',
        SIRAP_JWT_SECRET='isolated-notebook-software-test-'+uuid.uuid4().hex)
    result = subprocess.run([sys.executable,'-m','pytest','-q',str(ROOT_DIR/'tests/test_usa_runtime.py'),
                             str(ROOT_DIR/'tests/test_usa_notebook.py')],cwd=ROOT_DIR,env=environment,
                            text=True,capture_output=True,timeout=180)
    (output_dir/'usa_seed2_access_flow_tests.log').write_text(result.stdout+result.stderr,encoding='utf-8')
    if result.returncode:
        raise RuntimeError('The isolated USA software flow checks failed; inspect the saved test log.')
    return dict(scope='synthetic software checks of the actual USA HTTP handlers',passed=True,
        model_accuracy_measured=False, operational_registry_used=False, physical_barrier_used=False,
        rules=['state+serial identity','0.70 detector / 0.94 OCR','distinct frame IDs and RGB hashes',
               '7.5-second confirmation','unknown state / low confidence stay manual',
               'current allowlist and revocation','single-use owner/gate-bound evidence',
               'persist operation before barrier','storage/actuator failure and replay prevention'])
