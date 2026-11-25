"""Shared seed-2 detector and global OCR, with USA/Ecuador interpretation rules."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import threading
import time
import requests
import re

from src.data_processing import clean_text, crop_with_margin, normalize_plate, DEFAULT_PATTERNS
from src.model import PlateDetector, PlateReader, Recognition
from src.plate_identity import normalize_identity
from src.usa_jurisdiction import read_usa_jurisdiction
from src.utils import ROOT_DIR, resolve_path

_INSTALL_LOCK=threading.RLock()

def ensure_detector(directory):
    """Install the selected immutable private artifact; never replace an explicit model path."""
    if os.environ.get('SIRAP_USA_DETECTOR_DIR'):
        return validate_detector(directory)
    with _INSTALL_LOCK:
        try:
            return validate_detector(directory)
        except ValueError:
            pass
        selection=selected_checkpoint()
        repo=selection.get('artifact_repository')
        revision=selection.get('artifact_revision')
        token=os.environ.get('SIRAP_USA_MODEL_TOKEN')
        if not repo or not revision or not token:
            raise ValueError('Configure el acceso al checkpoint privado de USA, semilla 2.')
        if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',repo) or not re.fullmatch(r'[0-9a-f]{40}',revision):
            raise ValueError('La referencia del checkpoint privado debe ser un repositorio y commit inmutables.')
        expected=dict(selection['detector_sha256'],**selection['metadata_sha256'])
        directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
        for name,digest in expected.items():
            destination=directory/name
            if destination.is_file() and _sha(destination)==digest:
                continue
            staged=destination.with_suffix(destination.suffix+'.partial')
            try:
                url=f'https://huggingface.co/{repo}/resolve/{revision}/{name}'
                with requests.get(url,headers={'Authorization':f'Bearer {token}'},
                                  stream=True,timeout=(10,60)) as response:
                    response.raise_for_status()
                    with staged.open('wb') as output:
                        for chunk in response.iter_content(1024*1024):
                            if chunk: output.write(chunk)
                if _sha(staged)!=digest:
                    raise ValueError('El artefacto descargado no coincide con la semilla 2 seleccionada.')
                staged.replace(destination)
            except requests.RequestException:
                # Avoid placing a signed redirect or authorization details into server logs.
                raise ValueError('No se pudo recuperar el checkpoint privado de USA.') from None
            finally:
                staged.unlink(missing_ok=True)
        return validate_detector(directory)

def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def selected_checkpoint():
    return json.loads((ROOT_DIR/'models/usa/selected_checkpoint.json').read_text(encoding='utf-8'))

def validate_detector(directory):
    directory=Path(directory)
    selection=selected_checkpoint()
    expected=dict(selection['detector_sha256'],**{
        'sirap_openvino.json':'9c7c3c3355157b8ba652f7524dbb5a371aeede6996f4374f6cb5d5a645167c0d',
        'sirap_training.json':'ef928b6f9f8a9696bff3a500a2d5ff6dce17c15ce1d833348be1122b83989767',
    })
    for name,digest in expected.items():
        path=directory/name
        if not path.is_file() or _sha(path)!=digest:
            raise ValueError('El detector de USA requiere los archivos verificados de la semilla 2. '
                             'Instale el checkpoint seleccionado; no se usará un modelo alternativo.')
    return directory

class USAPipeline:
    """One set of USA-trained weights, with country-specific OCR interpretation."""
    def __init__(self,detector,reader,state_reader=read_usa_jurisdiction,margin=.06,country='usa',patterns=None):
        self.detector=detector
        self.reader=reader
        self.state_reader=state_reader
        self.margin=margin
        self.country=country
        self.patterns=patterns or DEFAULT_PATTERNS
        self._lock=threading.RLock()

    def for_country(self,country,patterns=None):
        if country not in ('ecuador','usa'):
            raise ValueError('País inválido.')
        adapted=type(self)(self.detector,self.reader,self.state_reader,self.margin,country,patterns)
        adapted._lock=self._lock
        return adapted

    @classmethod
    def from_config(cls,config):
        cfg=config['detector']
        directory=ensure_detector(resolve_path(os.environ.get('SIRAP_USA_DETECTOR_DIR') or cfg['checkpoint']))
        detector=PlateDetector(directory,conf=.70,imgsz=640,device='CPU',fallback_checkpoint=None)
        from fast_plate_ocr.inference import hub
        ocr_directory=os.environ.get('SIRAP_USA_OCR_DIR')
        if ocr_directory:
            model=Path(ocr_directory)/'cct_s_v2_global.onnx'
            plate_config=Path(ocr_directory)/'cct_s_v2_global_plate_config.yaml'
        else:
            model,plate_config=hub.download_model('cct-s-v2-global-model')
        expected=selected_checkpoint()['ocr_sha256']
        if not model.is_file() or _sha(model)!=expected['cct_s_v2_global.onnx']:
            raise ValueError('El modelo OCR de USA no coincide con el artefacto verificado.')
        if not plate_config.is_file() or _sha(plate_config)!=expected['cct_s_v2_global_plate_config.yaml']:
            raise ValueError('La configuración OCR de USA no coincide con la verificada.')
        reader=PlateReader('cct-s-v2-global-model','cpu',model,plate_config)
        reader.model_name='cct-s-v2-global-model (verified global weights)'
        return cls(detector,reader,margin=cfg.get('crop_margin',.06))

    def recognize_many(self,image):
        # OpenVINO's cached infer request and OCR session are shared by API requests.
        with self._lock:
            start=time.perf_counter()
            detections=self.detector.detect(image,max_detections=20)
            detected_at=time.perf_counter()
            readings=[]
            for detection in sorted(detections,key=lambda d:d.area,reverse=True):
                if detection.confidence<.70:
                    continue
                crop=crop_with_margin(image,detection.box,self.margin)
                if not crop.size:
                    continue
                raw,minimum,mean=self.reader.read(crop)
                if self.country=='ecuador':
                    plate=normalize_plate(raw,self.patterns) or None
                    readings.append(Recognition(
                        plate=plate,plate_raw=raw,ocr_confidence=minimum,ocr_mean_confidence=mean,
                        det_confidence=detection.confidence,box=detection.box,crop=crop,
                        detector=self.detector.name,candidates=len(detections),country='ecuador',
                        identity_key=plate,lookup_key=plate))
                    continue
                serial=clean_text(raw)
                try:
                    state=self.state_reader(crop)
                except RuntimeError:
                    state={'jurisdiction_status':'unavailable'}
                jurisdiction=state.get('jurisdiction_abbreviation') or None
                identity=None
                if jurisdiction and serial:
                    try:
                        identity=normalize_identity(serial,'usa',jurisdiction)
                    except ValueError:
                        pass
                readings.append(Recognition(
                    plate=serial or None,plate_raw=raw,ocr_confidence=minimum,ocr_mean_confidence=mean,
                    det_confidence=detection.confidence,box=detection.box,crop=crop,
                    detector=self.detector.name,candidates=len(detections),country='usa',
                    jurisdiction=jurisdiction,jurisdiction_name=state.get('jurisdiction_name',''),
                    jurisdiction_status=state.get('jurisdiction_status','state_not_read'),
                    identity_key=identity.key if identity else None,
                    lookup_key=identity.lookup_key if identity else None,
                ))
            timings={'detector':(detected_at-start)*1000,'total':(time.perf_counter()-start)*1000}
            if not readings:
                readings=[Recognition(None,detector=self.detector.name,country=self.country,
                    jurisdiction_status='state_not_read' if self.country=='usa' else 'not_applicable')]
            for reading in readings:
                reading.timings_ms=dict(timings)
            return readings

    def recognize(self,image):
        return self.recognize_many(image)[0]
