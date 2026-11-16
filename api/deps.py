"""Dependencias compartidas: archivos CSV, pipeline ALPR, barrera y usuario autenticado."""

from __future__ import annotations

from functools import lru_cache
from typing import Any, Callable

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from api.security import decode_token, ensure_credentials_table
from api.settings import settings
from src.access_control import barrier_from_config
from src.storage import CsvStore
from src.model import ALPRPipeline
from src.utils import load_config, load_json
from copy import deepcopy

_bearer = HTTPBearer(auto_error=False)


@lru_cache(maxsize=2)
def _config_for_country(country: str) -> dict[str, Any]:
    if country not in ('ecuador','usa'):
        raise ValueError('País inválido.')
    cfg=deepcopy(load_config())
    if country=='usa':
        profile=load_config('config/countries/usa.yaml')
        cfg.update(profile)
        cfg['decision']={'umbral_confianza_ocr':.94,'distancia_max_similar':0}
    return cfg

def get_config(country: str = 'ecuador') -> dict[str, Any]:
    return _config_for_country(country)

get_config.cache_clear = _config_for_country.cache_clear


@lru_cache(maxsize=1)
def get_store() -> CsvStore:
    """Usa el archivo local de demostración configurado para la API."""
    db = CsvStore(data_dir=settings.data_dir)
    ensure_credentials_table(db)
    return db


@lru_cache(maxsize=2)
def _pipeline_for_country(country: str) -> ALPRPipeline:
    """The same detector/OCR resources serve both country interpretation profiles."""
    cfg=get_config(country)
    return _shared_pipeline().for_country(country,cfg.get('placas',{}).get('patrones'))

@lru_cache(maxsize=1)
def _shared_pipeline():
    from src.usa_pipeline import USAPipeline
    return USAPipeline.from_config(get_config('usa'))

def get_pipeline(country: str = 'ecuador') -> ALPRPipeline:
    return _pipeline_for_country(country)

def _clear_pipelines():
    _pipeline_for_country.cache_clear()
    clear=getattr(_shared_pipeline,'cache_clear',None)
    if clear: clear()

get_pipeline.cache_clear = _clear_pipelines


@lru_cache(maxsize=1)
def get_barrier():
    return barrier_from_config(get_config())


def thresholds(country: str = 'ecuador') -> tuple[float, float, int]:
    """(umbral OCR, umbral de decisión del detector, distancia de «casi coincide»)."""
    if country=='usa':
        return .94,.70,0
    cfg = get_config()
    det = cfg['detector'].get('conf_decision',.70)
    return float(cfg["decision"]["umbral_confianza_ocr"]), float(det), int(cfg["decision"]["distancia_max_similar"])


def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(_bearer)) -> dict[str, Any]:
    """Usuario del token ``Authorization: Bearer …``."""
    if credentials is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Inicie sesión.", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = decode_token(credentials.credentials)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "La sesión expiró; vuelva a iniciar sesión.")
    except jwt.PyJWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token inválido.")
    store = get_store()
    if not store.is_user_active(payload["sub"]):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "El usuario está inactivo; vuelva a iniciar sesión con otra cuenta.")
    rows = store.table("usuarios")
    rows = rows[rows["usuario"].astype(str) == payload["sub"]]
    if rows.empty:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "El usuario ya no existe; vuelva a iniciar sesión.")
    row = rows.iloc[-1]
    # Lee nombre y rol vigentes desde el CSV para aplicar de inmediato cambios administrativos.
    country=payload.get('country','ecuador')
    if country not in ('ecuador','usa'):
        raise HTTPException(401,'País de sesión inválido; vuelva a iniciar sesión.')
    return {"usuario": payload["sub"], "nombre": row["nombre"], "rol": row["rol"],
            'country':country,'language':payload.get('language','en')}

def profile_country(user,requested=None):
    selected=user.get('country')
    if selected is not None and requested is not None and requested!=selected:
        raise HTTPException(403,'El país de la solicitud no coincide con el elegido al iniciar sesión.')
    return selected or requested or 'ecuador'


def require_roles(*roles: str) -> Callable[..., dict[str, Any]]:
    """Dependencia que exige uno de los roles indicados."""

    def checker(user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]:
        if user["rol"] not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Su rol no tiene permiso para esta acción.")
        return user

    return checker

