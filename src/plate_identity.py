"""Country-specific registration identities used by API, lists and history.

Legacy Ecuador keys stay XXX-0000. USA keys are US:STATE:SERIAL in the existing
CSV plate column, so no migration or reinterpretation of legacy rows is needed.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
from src.data_processing import normalize_plate

US_STATES = frozenset('AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY DC'.split())

@dataclass(frozen=True)
class PlateIdentity:
    country: str
    serial: str
    jurisdiction: str | None = None

    @property
    def key(self):
        return f'US:{self.jurisdiction}:{self.serial}' if self.country=='usa' else self.serial

    @property
    def lookup_key(self):
        return f'{self.jurisdiction}:{self.serial}' if self.country=='usa' else self.serial

    def as_dict(self):
        return dict(country=self.country,jurisdiction=self.jurisdiction,
                    identity_key=self.key,lookup_key=self.lookup_key)

def normalize_identity(raw, country='ecuador', jurisdiction=None):
    if country not in ('ecuador','usa'):
        raise ValueError('País inválido: seleccione Ecuador o Estados Unidos de América.')
    text=str(raw or '').strip().upper()
    if country=='ecuador':
        if text.startswith('US:') or jurisdiction:
            raise ValueError('La matrícula y el estado no corresponden al perfil Ecuador.')
        plate=normalize_plate(text)
        if not plate:
            raise ValueError('Placa inválida: use 3 letras y 3 o 4 dígitos (ej.: PBA-8901).')
        return PlateIdentity(country,plate)
    state=str(jurisdiction or '').strip().upper()
    if state not in US_STATES:
        raise ValueError('Seleccione el estado emisor de la placa de Estados Unidos de América.')
    if not re.fullmatch(r'[A-Z0-9\s-]+',text):
        raise ValueError('Matrícula inválida: use letras, números, espacios o guiones.')
    serial=re.sub(r'[\s-]','',text)
    if not 1<=len(serial)<=12:
        raise ValueError('La matrícula debe contener entre 1 y 12 letras o números.')
    return PlateIdentity(country,serial,state)

def identity_from_key(value):
    text=str(value or '').strip().upper()
    if text.startswith('US:'):
        parts=text.split(':')
        if len(parts)!=3:
            raise ValueError('Clave de placa de Estados Unidos de América inválida.')
        return normalize_identity(parts[2],'usa',parts[1])
    return normalize_identity(text)

def public_plate_record(row):
    """Expose serial and country separately while retaining a stable CRUD identifier."""
    result=dict(row)
    if result.get('placa'):
        identity=identity_from_key(result['placa'])
        result.update(identity.as_dict(),placa=identity.serial)
    if result.get('autorizacion'):
        result['autorizacion']=public_plate_record(result['autorizacion'])
    return result
