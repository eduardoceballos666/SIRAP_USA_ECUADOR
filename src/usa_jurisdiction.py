"""Printed U.S. jurisdiction OCR; no inference from location, plate design or registry.

The string similarity score and Tesseract confidence are diagnostics, not probabilities.
This development reader does not authorize access or alter the serial OCR model.
"""
from __future__ import annotations

import re
import shutil
import csv
import io
import shlex
import subprocess
from difflib import SequenceMatcher
from collections import defaultdict
import cv2
import numpy as np

STATE_ABBR_TO_NAME = {
    'AL':'Alabama','AK':'Alaska','AZ':'Arizona','AR':'Arkansas','CA':'California',
    'CO':'Colorado','CT':'Connecticut','DE':'Delaware','FL':'Florida','GA':'Georgia',
    'HI':'Hawaii','ID':'Idaho','IL':'Illinois','IN':'Indiana','IA':'Iowa','KS':'Kansas',
    'KY':'Kentucky','LA':'Louisiana','ME':'Maine','MD':'Maryland','MA':'Massachusetts',
    'MI':'Michigan','MN':'Minnesota','MS':'Mississippi','MO':'Missouri','MT':'Montana',
    'NE':'Nebraska','NV':'Nevada','NH':'New Hampshire','NJ':'New Jersey',
    'NM':'New Mexico','NY':'New York','NC':'North Carolina','ND':'North Dakota',
    'OH':'Ohio','OK':'Oklahoma','OR':'Oregon','PA':'Pennsylvania','RI':'Rhode Island',
    'SC':'South Carolina','SD':'South Dakota','TN':'Tennessee','TX':'Texas',
    'UT':'Utah','VT':'Vermont','VA':'Virginia','WA':'Washington','WV':'West Virginia',
    'WI':'Wisconsin','WY':'Wyoming','DC':'District of Columbia',
}
LEXICAL_SIMILARITY_MIN = 0.84
LEXICAL_MARGIN_MIN = 0.08
TESSERACT_WORD_CONFIDENCE_MIN = 30.0

def normalize_ocr_word(value):
    return re.sub('[^A-Z]', '', str(value).upper())

def match_state_name(tokens, confidences):
    """Require a unique name match; prefer complete multiword names over substrings."""
    candidates = []
    for code, name in STATE_ABBR_TO_NAME.items():
        target = ' '.join(normalize_ocr_word(w) for w in name.split())
        for size in range(max(1,len(name.split())-1),min(3,len(name.split())+1)+1):
            for start in range(len(tokens)-size+1):
                confidence = float(np.mean(confidences[start:start+size]))
                if confidence < TESSERACT_WORD_CONFIDENCE_MIN:
                    continue
                score = SequenceMatcher(None,' '.join(tokens[start:start+size]),target).ratio()
                if score >= LEXICAL_SIMILARITY_MIN:
                    candidates.append(dict(code=code,name=name,score=score,
                                           confidence=confidence,width=size,start=start))
    exact = [c for c in candidates if c['score']==1.0]
    if exact:
        exact = [c for c in exact if not any(
            other['width']>c['width'] and other['start']<=c['start']
            and other['start']+other['width']>=c['start']+c['width'] for other in exact)]
        if len({c['code'] for c in exact}) > 1:
            return None
        return max(exact,key=lambda c:c['confidence'])
    best = {}
    for candidate in candidates:
        code=candidate['code']
        if code not in best or (candidate['score'],candidate['confidence']) > (best[code]['score'],best[code]['confidence']):
            best[code]=candidate
    ranked=sorted(best.values(),key=lambda c:(c['score'],c['confidence']),reverse=True)
    if not ranked or (len(ranked)>1 and ranked[0]['score']-ranked[1]['score']<LEXICAL_MARGIN_MIN):
        return None
    return ranked[0]

def select_evidence(observations):
    """Abstain on conflicting names; fuzzy names need agreement in two views."""
    matches=[]
    for observation in observations:
        m=match_state_name(observation['words'],observation['confidences'])
        if m is not None:
            matches.append(dict(m,source=observation['view']))
    codes={m['code'] for m in matches}
    if len(codes)>1:
        return None,'conflicting_state_names'
    if len(codes)==1:
        if any(m['score']==1.0 for m in matches) or len({m['source'] for m in matches})>=2:
            return max(matches,key=lambda m:(m['score'],m['confidence'])),'name_read'
    # Two-letter words also occur in slogans; one isolated code is insufficient.
    abbreviations=defaultdict(list)
    for observation in observations:
        if 'header' not in observation['view'] or len(observation['words'])!=1:
            continue
        for word,confidence in zip(observation['words'],observation['confidences']):
            if word in STATE_ABBR_TO_NAME and confidence>=70:
                abbreviations[word].append((observation['view'],confidence))
    supported={code:items for code,items in abbreviations.items()
               if len({view for view,_ in items})>=2}
    if len(supported)==1 and not codes:
        code,items=next(iter(supported.items()))
        source,confidence=max(items,key=lambda item:item[1])
        return dict(code=code,name=STATE_ABBR_TO_NAME[code],score=1.0,
                    confidence=confidence,source=source),'repeated_code_read'
    return None,'state_not_read'

def _tesseract_data(view, psm, extra):
    """Read TSV from the native executable; no Python OCR wrapper or runtime installs."""
    ok, encoded = cv2.imencode('.png', view)
    if not ok:
        raise RuntimeError('Cannot encode the state crop.')
    command = ['tesseract', 'stdin', 'stdout', '--oem', '1', '--psm', str(psm),
               '--dpi', '300', *shlex.split(extra), 'tsv']
    try:
        result = subprocess.run(command, input=encoded.tobytes(), capture_output=True,
                                timeout=4, check=True)
    except (subprocess.SubprocessError, OSError) as exc:
        raise RuntimeError('State OCR failed or timed out.') from exc
    rows = list(csv.DictReader(io.StringIO(result.stdout.decode('utf-8')),
                               delimiter='\t', quoting=csv.QUOTE_NONE))
    return {'text': [row.get('text', '') for row in rows],
            'conf': [row.get('conf', '-1') for row in rows]}

def read_usa_jurisdiction(crop_rgb):
    """Read all views with a bounded OCR timeout. No system installs at inference time."""
    if not shutil.which('tesseract'):
        raise RuntimeError('Install the tesseract-ocr executable before running state OCR.')
    image=np.asarray(crop_rgb)
    empty=dict(jurisdiction_name='',jurisdiction_abbreviation='',jurisdiction_raw_ocr='',
               jurisdiction_ocr_source='',jurisdiction_match_score=0.0,
               tesseract_confidence_mean=0.0,jurisdiction_status='state_not_read',
               jurisdiction_evidence=[])
    if image.ndim!=3 or image.shape[2]<3 or image.size==0:
        return empty
    height,width=image.shape[:2]
    gray=cv2.cvtColor(image[:,:,:3],cv2.COLOR_RGB2GRAY)
    enhanced=cv2.createCLAHE(clipLimit=2.0,tileGridSize=(8,8)).apply(gray)
    views=[]
    for label,view,psm in [('full_plate',enhanced,11),
                           ('upper_band',enhanced[:max(1,round(height*.45))],7),
                           ('lower_band',enhanced[round(height*.55):],7)]:
        scale=max(2,min(5,round(180/max(1,view.shape[0]))))
        views.append((label,cv2.resize(view,None,fx=scale,fy=scale,interpolation=cv2.INTER_CUBIC),
                      psm,'-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'))
    # Narrow headers isolate the printed state from the much larger serial characters.
    for band_index,(top,bottom) in enumerate(((0,.30),(.04,.26),(.05,.36))):
        band=gray[int(height*top):max(int(height*top)+1,int(height*bottom)),
                  int(width*.03):max(int(width*.03)+1,int(width*.97))]
        scale=max(2,min(10,80/max(1,band.shape[0])))
        enlarged=cv2.resize(band,None,fx=scale,fy=scale,interpolation=cv2.INTER_CUBIC)
        for kind in ('gray','otsu'):
            view=enlarged.copy()
            if kind=='otsu':
                view=cv2.threshold(view,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]
            if np.median(view)<127:
                view=255-view
            view=cv2.copyMakeBorder(view,10,10,10,10,cv2.BORDER_CONSTANT,value=255)
            for psm in (7,11):
                views.append((f'header_{band_index}_{kind}_psm{psm}',view,psm,''))
    observations=[]
    for name,view,psm,extra in views:
        try:
            data=_tesseract_data(view,psm,extra)
        except RuntimeError:
            observations.append(dict(view=name,text='',words=[],confidences=[],error='ocr_error_or_timeout'))
            continue
        words=[];confidences=[]
        for token,conf in zip(data['text'],data['conf']):
            word=normalize_ocr_word(token)
            try:
                confidence=float(conf)
            except (TypeError,ValueError):
                continue
            if word and confidence>=0:
                words.append(word);confidences.append(confidence)
        observations.append(dict(view=name,text=' '.join(words),words=words,confidences=confidences))
    selected,status=select_evidence(observations)
    result=dict(empty,jurisdiction_status=status,jurisdiction_evidence=observations,
                jurisdiction_raw_ocr=' | '.join(f"{v['view']}: {v['text']}" for v in observations if v['text']))
    if selected:
        result.update(jurisdiction_name=selected['name'],jurisdiction_abbreviation=selected['code'],
                      jurisdiction_ocr_source=selected['source'],jurisdiction_match_score=float(selected['score']),
                      tesseract_confidence_mean=float(selected['confidence']))
    return result
