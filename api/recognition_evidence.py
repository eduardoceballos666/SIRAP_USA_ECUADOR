"""Server-owned frame evidence for USA automatic access. No client confidences are trusted."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass,replace
import math
import threading
import time
import uuid

@dataclass
class Evidence:
    id: str
    owner: str
    gate: str
    session: str
    reading: object
    created_at: float
    frames: tuple
    claimed: bool=False

    @property
    def confirmed(self):
        return len(self.frames)>=2

    def audit(self):
        return dict(evidence_id=self.id,country='usa',identity_key=self.reading.identity_key,
                    seed=2,detector_threshold=.70,ocr_threshold=.94,
                    detector_confidence=self.reading.det_confidence,ocr_confidence=self.reading.ocr_confidence,
                    frames=[dict(frame_id=f[0],image_sha256=f[1],received_at_monotonic=f[2]) for f in self.frames])

class EvidenceStore:
    def __init__(self,window=7.5,ttl=30.,maximum=1000,clock=None):
        self.window=window;self.ttl=ttl;self.maximum=maximum
        self.clock=clock or time.monotonic
        self._lock=threading.RLock();self._receipts={};self._tracks={};self._reservations={}

    def _purge(self,now):
        self._receipts={k:v for k,v in self._receipts.items() if now-v.created_at<=self.ttl}
        self._reservations={k:v for k,v in self._reservations.items() if v in self._receipts}
        self._tracks={k:v for k,v in self._tracks.items() if v and now-v[-1][2]<=self.window}
        while len(self._receipts)>=self.maximum:
            self._receipts.pop(next(iter(self._receipts)))
        while len(self._tracks)>self.maximum:
            self._tracks.pop(next(iter(self._tracks)))

    def record(self,readings,*,owner,gate,session,frame_id,image_sha256,received_at):
        """One receipt per candidate; require two unique frame IDs AND image hashes."""
        now=self.clock()
        prefix=(owner,gate,session)
        with self._lock:
            self._purge(now)
            eligible=[r for r in readings if r.identity_key and math.isfinite(r.ocr_confidence)
                      and r.ocr_confidence>=.94 and math.isfinite(r.det_confidence) and r.det_confidence>=.70]
            current={r.identity_key for r in eligible}
            eligible_ids={id(r) for r in eligible}
            # A missing/changed identity interrupts confirmation, rather than reusing an old car.
            for key in list(self._tracks):
                if key[:3]==prefix and key[3] not in current:
                    self._tracks.pop(key,None)
            output=[]
            for reading in readings:
                frames=deque()
                if id(reading) in eligible_ids:
                    key=(*prefix,reading.identity_key)
                    frames=self._tracks.setdefault(key,deque())
                    while frames and received_at-frames[0][2]>self.window:
                        frames.popleft()
                    if frames and received_at<frames[-1][2]:
                        frames=deque()
                    if not any(frame_id==f[0] or image_sha256==f[1] for f in frames):
                        frames.append((frame_id,image_sha256,received_at))
                    self._tracks[key]=frames
                receipt=Evidence(str(uuid.uuid4()),owner,gate,session,replace(reading,crop=None),now,tuple(frames)[-2:])
                self._receipts[receipt.id]=receipt
                output.append(receipt)
            return output

    def get(self,evidence_id,*,owner,gate,identity_key=None,claim=False):
        with self._lock:
            self._purge(self.clock())
            receipt=self._receipts.get(str(evidence_id or ''))
            if receipt is None or receipt.owner!=owner or receipt.gate!=gate:
                raise ValueError('La confirmación ya no está disponible. Procese de nuevo la imagen o cámara.')
            if identity_key is not None and receipt.reading.identity_key!=identity_key:
                raise ValueError('La placa o el estado no coinciden con la lectura confirmada en el servidor.')
            if receipt.claimed:
                raise ValueError('La confirmación ya se utilizó para una apertura. No repita la orden.')
            if claim:
                if not receipt.confirmed:
                    raise ValueError('Se requieren dos cuadros distintos dentro de 7,5 segundos.')
                binding=(receipt.owner,receipt.gate,receipt.session,receipt.reading.identity_key)
                if binding in self._reservations:
                    raise ValueError('Ya existe una solicitud de apertura para esta confirmación. No repita la orden.')
                self._reservations[binding]=receipt.id
                receipt.claimed=True
            return receipt

    def release(self,evidence_id):
        with self._lock:
            receipt=self._receipts.get(evidence_id)
            if receipt:
                receipt.claimed=False
                binding=(receipt.owner,receipt.gate,receipt.session,receipt.reading.identity_key)
                if self._reservations.get(binding)==evidence_id:
                    self._reservations.pop(binding,None)

    def consume(self,receipt):
        with self._lock:
            # Older receipts from the same vehicle/session must not open a second time.
            for item in self._receipts.values():
                if (item.owner,item.gate,item.session,item.reading.identity_key)==(
                    receipt.owner,receipt.gate,receipt.session,receipt.reading.identity_key):
                    item.claimed=True
            self._tracks.pop((receipt.owner,receipt.gate,receipt.session,receipt.reading.identity_key),None)

evidence_store=EvidenceStore()
