"""Dashboard, Historial y Acerca del modelo."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Optional

import pandas as pd
from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response

from api.jsonsafe import plain
from api.deps import current_user, get_barrier, get_store, get_pipeline, get_config, require_roles, thresholds, profile_country
from api.schemas import Country
from src.utils import load_json, now_local

router = APIRouter(prefix="/api", tags=["Dashboard, Historial y Modelo"])

RESULT_LABELS = {"AUTORIZADO": "Autorizado", "DENEGADO": "Denegado", "NO_REGISTRADO": "No registrado",
                 "VERIFICACION_MANUAL": "Verificación manual"}

def _runtime_info(country):
    cfg=get_config(country)
    name=cfg['ocr'].get('model',cfg['ocr'].get('modelo','cct-s-v2-global-model'))
    info={'country':country,'detector':f'RT-DETRv2-S · OpenVINO · {country}',
          'detector_es_modelo':False,'ocr':name,'model_ready':False,
          'model_seed':2,'model_training_country':'usa','country_validation_pending':country=='ecuador',
          'automatic_access_enabled':cfg.get('automatic_access',{}).get('enabled',True)}
    try:
        pipeline=get_pipeline('usa') if country=='usa' else get_pipeline()
    except (ValueError,FileNotFoundError,RuntimeError,ImportError):
        info['model_message']='El modelo seleccionado no está disponible; puede verificar la placa manualmente.'
        return info
    info.update(detector=pipeline.detector.name,detector_es_modelo=pipeline.detector.is_model,
                ocr=pipeline.reader.model_name,model_ready=True)
    return info


def _records(df: pd.DataFrame) -> list[dict[str, Any]]:
    if df.empty:
        return []
    out = df.copy()
    if "fecha_hora" in out:
        out["fecha_hora"] = out["fecha_hora"].dt.strftime("%Y-%m-%d %H:%M:%S")
    return plain(out.to_dict(orient="records"))


@router.get("/system", summary="Estado del sistema")
def system(country: Optional[Country]=None, user: dict = Depends(current_user)) -> dict[str, Any]:
    country=profile_country(user,country)
    db, barrier = get_store(), get_barrier()
    ocr_threshold, det_threshold, _ = thresholds(country)
    return {**_runtime_info(country),"base_datos": db.engine,
            "barrera": "simulada" if getattr(barrier, "simulated", True) else "conectada",
            "umbral_ocr": ocr_threshold, "umbral_detector": det_threshold, "garitas": db.garitas(),
            "countries":[{'code':'ecuador','name':'Ecuador'},{'code':'usa','name':'Estados Unidos'}]}


@router.get("/operations", summary="Historial filtrado")
def operations(desde: Optional[date] = None, hasta: Optional[date] = None, placa: Optional[str] = None,
               garita: Optional[str] = None, resultado: Optional[str] = None,
               tipo_movimiento: Optional[str] = None, limit: int = Query(1000, ge=1, le=5000),
               country: Optional[Country]=None,jurisdiction: Optional[str]=None,
               user: dict = Depends(current_user)) -> list[dict[str, Any]]:
    country=profile_country(user,country)
    return _records(get_store().operations(desde, hasta, placa, garita, resultado, tipo_movimiento, limit,
                                          country=country,jurisdiction=jurisdiction))


@router.get("/operations/export.csv", summary="Exportar el historial filtrado a CSV")
def export_csv(desde: Optional[date] = None, hasta: Optional[date] = None, placa: Optional[str] = None,
               garita: Optional[str] = None, resultado: Optional[str] = None,
               tipo_movimiento: Optional[str] = None,
               country: Optional[Country]=None,jurisdiction: Optional[str]=None,
               user: dict = Depends(require_roles("SUPERVISOR", "ADMINISTRADOR"))) -> Response:
    country=profile_country(user,country)
    df = get_store().operations(desde, hasta, placa, garita, resultado, tipo_movimiento,
                               country=country,jurisdiction=jurisdiction)
    name = f"sirap_historial_{now_local():%Y%m%d}.csv"
    return Response(df.to_csv(index=False).encode("utf-8-sig"), media_type="text/csv",
                    headers={"Content-Disposition": f'attachment; filename="{name}"'})


@router.get("/dashboard", summary="Indicadores y datos para los gráficos")
def dashboard(days: int = Query(7, ge=1, le=365), include_demo: bool = True,
              country: Optional[Country]=None,
              user: dict = Depends(current_user)) -> dict[str, Any]:
    country=profile_country(user,country)
    today = now_local().date()
    df = get_store().operations(desde=today - timedelta(days=days - 1), hasta=today,country=country)
    if not include_demo and not df.empty:
        df = df[df["origen"] != "DEMO"]
    if df.empty:
        return {"kpis": {"ingresos": 0, "salidas": 0, "identificados": 0, "alertas": 0},
                "por_hora": [], "por_resultado": [], "por_garita": [], "alertas": []}
    df["resultado_txt"] = df["resultado"].map(RESULT_LABELS).fillna(df["resultado"])
    alerts = df[df["resultado"].isin(["DENEGADO", "NO_REGISTRADO"]) | (df["accion"] == "APERTURA_MANUAL")]
    by_hour = df.assign(hora=df["fecha_hora"].dt.hour).groupby(["hora", "resultado_txt"]).size()
    return {
        "kpis": {"ingresos": int((df["tipo_movimiento"] == "ENTRADA").sum()),
                 "salidas": int((df["tipo_movimiento"] == "SALIDA").sum()),
                 "identificados": int(df["identity_key"].replace('',pd.NA).dropna().nunique()),
                 "alertas": int(len(alerts))},
        "por_hora": [{"hora": int(h), "resultado": r, "n": int(n)} for (h, r), n in by_hour.items()],
        "por_resultado": [{"resultado": r, "n": int(n)} for r, n in df["resultado_txt"].value_counts().items()],
        "por_garita": [{"garita": g, "movimiento": m, "n": int(n)}
                       for (g, m), n in df.groupby(["garita", "tipo_movimiento"]).size().items()],
        "alertas": _records(alerts[["fecha_hora", "garita", "placa_final", "country", "jurisdiction", "resultado_txt", "accion", "operador"]]
                            .head(12)),
    }


@router.get("/model/info", summary="Métricas y descripción del modelo")
def model_info(country: Optional[Country]=None, user: dict = Depends(current_user)) -> dict[str, Any]:
    country=profile_country(user,country)
    if country=='usa':
        return {**_runtime_info('usa'),'metricas':{'detector_test':None,
            'development':load_json('results/metrics/usa_runtime_development.json')},
            'umbral_ocr':.94,'umbral_detector':.70}
    # Historical Ecuador reports describe other weights, not the current shared seed 2.
    metrics = dict.fromkeys(('detector_test','ocr_savh','e2e','velocidad','entrenamiento',
                             'umbrales','ocr_afinamiento','regla_decision_savh','optimizacion_resumen'))
    ocr_threshold, det_threshold, _ = thresholds()
    return {"metricas": metrics,**_runtime_info('ecuador'),
            "umbral_ocr": ocr_threshold, "umbral_detector": det_threshold}

