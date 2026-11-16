"""API REST de SIRAP_USA_ECUADOR_HF (FastAPI).

Ejecutar desde la raíz del repositorio::

    uvicorn api.main:app --reload

Documentación interactiva en http://localhost:8000/docs. Si existe ``frontend/dist`` (``npm run build``),
la misma API sirve el frontend Vue en ``/``.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
import json

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from api import __version__
from api.deps import get_store, get_pipeline
from api.routers import admin, auth, recognition, reports
from api.settings import settings
from src.utils import ROOT_DIR, get_logger

logger = get_logger("sirap.api")


@asynccontextmanager
async def lifespan(_: FastAPI):
    get_store()
    app.state.profile_status={}
    detectors=[]
    for country in ('ecuador','usa'):
        try:
            pipeline=get_pipeline(country)
            detectors.append(pipeline.detector)
            app.state.profile_status[country]={'model_ready':True,'seed':2,'training_country':'usa'}
        except Exception as exc:  # noqa: BLE001 - la API conserva la verificación manual
            logger.error("No se pudo precargar el perfil %s: %s",country,exc)
            app.state.profile_status[country]={'model_ready':False,'seed':2,'training_country':'usa'}
    app.state.shared_detector=len(detectors)==2 and detectors[0] is detectors[1]
    yield


app = FastAPI(
    title="SIRAP_USA_ECUADOR_HF API",
    version=__version__,
    description="Sistema de Detección y Reconocimiento Automático de Placas · RT-DETRv2-S/OpenVINO + fast-plate-ocr.",
    lifespan=lifespan,
)
app.add_middleware(CORSMiddleware, allow_origins=list(settings.cors_origins), allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])

for module in (auth, recognition, reports, admin):
    app.include_router(module.router)


@app.get("/api/health", tags=["Sistema"], summary="Prueba de vida")
def health() -> dict:
    build_path=ROOT_DIR/'BUILD_INFO.json'
    try:
        build=json.loads(build_path.read_text()).get('commit','development')
    except (OSError,ValueError):
        build='development'
    return {"estado":"ok","version":__version__,'build':build,
            'profiles':getattr(app.state,'profile_status',{}),
            'shared_detector':getattr(app.state,'shared_detector',False)}


_dist = (ROOT_DIR / settings.frontend_dist).resolve()
if (_dist / "index.html").exists():
    if (_dist / "assets").is_dir():
        app.mount("/assets", StaticFiles(directory=_dist / "assets"), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    def spa(path: str) -> FileResponse:
        if path.startswith("api/"):
            raise HTTPException(404, "Ruta no encontrada.")
        file = (_dist / path).resolve()
        if path and file.is_file() and _dist in file.parents:
            return FileResponse(file)
        return FileResponse(_dist / "index.html")

