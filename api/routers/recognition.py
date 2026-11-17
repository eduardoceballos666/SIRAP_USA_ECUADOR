"""Reconocimiento y Acceso: reconocer una placa, verificarla a mano y registrar operaciones."""

from __future__ import annotations

import base64
import threading
import time
import uuid
import hashlib
from dataclasses import asdict

import cv2
from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, Response, UploadFile, status
from fastapi.responses import FileResponse

from api import schemas
from api.jsonsafe import plain
from api.deps import current_user, get_barrier, get_config, get_store, get_pipeline, thresholds, profile_country
from src.access_control import AccessDecision, decide_access, decide_usa_access
from src.plate_identity import normalize_identity, public_plate_record
from api.recognition_evidence import evidence_store
from api.providers import usa_jdpower
from src.data_processing import ImageLimits, ImageValidationError, load_image, normalize_plate
from src.storage import StorageError
from src.github_storage import durable_backup_configured
from src.detection_export import append_detection, enrich_detection, _query_sri
from src.utils import ROOT_DIR, get_logger, now_local

logger = get_logger("sirap.api.recognition")
router = APIRouter(prefix="/api", tags=["Reconocimiento y Acceso"])

SAMPLES_DIR = ROOT_DIR / "data" / "samples"

# Estado temporal de las consultas externas, asociado a una placa y a una solicitud.
_VEHICLE_LOOKUP_LOCK = threading.RLock()
_VEHICLE_LOOKUPS: dict[str, dict] = {}


def _load_vehicle_details(request_id: str, plate: str) -> None:
    """Consulta datos vehiculares públicos del SRI y el registro local de SIRAP.

    No consulta EcuadorLegalOnline, cuya información de propietario es de pago.
    """
    sri: dict = {}
    sri_error = ""
    try:
        try:
            sri = _query_sri(plate)
        except Exception as exc:
            sri_error = f"{type(exc).__name__}: {exc}"
            logger.exception("No se pudo consultar el SRI para %s", plate)

        try:
            local = get_store().get_vehicle(plate) or {}
        except Exception:
            logger.exception("No se pudo leer el registro local de %s", plate)
            local = {}

        result = {
            "estado": "completado",
            "placa": plate,
            "vehiculo": {
                "marca": sri.get("sri_marca") or local.get("marca") or "",
                "modelo": sri.get("sri_modelo") or local.get("modelo") or "",
                "anio": sri.get("sri_anio_modelo") or local.get("anio") or local.get("year") or "",
                "propietario": local.get("propietario") or "",
                "transportista": local.get("transportista") or "",
            },
            "fuentes": {
                "sri": "encontrado" if sri.get("sri_encontrado") else ("error" if sri_error else "sin_datos"),
                "ecuadorlegalonline": "no_usado_servicio_de_pago",
                "registro": "encontrado" if local else "sin_registro",
            },
            "detalle_propietario": (
                "EcuadorLegalOnline no se consulta porque su información de propietario es de pago; "
                "solo se muestra el dato del registro local, si existe."
            ),
        }
    except Exception as exc:
        logger.exception("No se pudieron reunir los datos de %s", plate)
        result = {
            "estado": "completado",
            "placa": plate,
            "vehiculo": {"marca": "", "modelo": "", "anio": "", "propietario": "", "transportista": ""},
            "fuentes": {
                "sri": "error",
                "ecuadorlegalonline": "no_usado_servicio_de_pago",
                "registro": "sin_registro",
            },
            "detalle_propietario": (
                "EcuadorLegalOnline no se consulta porque su información de propietario es de pago."
            ),
            "error": f"{type(exc).__name__}: {exc}",
        }
    with _VEHICLE_LOOKUP_LOCK:
        result["_created_at"] = time.monotonic()
        _VEHICLE_LOOKUPS[request_id] = result

def _store_lookup(request_id: str, value: dict) -> None:
    """Guarda el estado de una consulta y descarta las que superan los 15 minutos."""
    with _VEHICLE_LOOKUP_LOCK:
        cutoff = time.monotonic() - 900
        for old_id, old in list(_VEHICLE_LOOKUPS.items()):
            if old.get("_created_at", 0) < cutoff:
                _VEHICLE_LOOKUPS.pop(old_id, None)
        _VEHICLE_LOOKUPS[request_id] = {**value, "_created_at": time.monotonic()}


def _load_us_vehicle_details(request_id: str, serial: str, state: str, base: dict) -> None:
    """Completa una consulta de EE. UU.: registro local (en ``base``) más J.D. Power si responde.

    Si J.D. Power no responde o niega el acceso, se muestran solo los datos locales.
    """
    fuentes = dict(base["fuentes"])
    vehiculo = dict(base["vehiculo"])
    try:
        record = usa_jdpower.lookup(serial, state)
        fuentes["jdpower"] = "encontrado" if record["lookup_status"] == "found" else record["lookup_status"]
        vehiculo.update(usa_jdpower.vehicle_fields(record))
    except Exception:
        logger.exception("No se pudo consultar J.D. Power (%s)", state)
        fuentes["jdpower"] = "error"
    _store_lookup(request_id, {**base, "estado": "completado", "vehiculo": vehiculo, "fuentes": fuentes})


SAMPLE_LABELS = {
    "garita3_PBA-8901.jpg": "Garita 3 · PBA-8901 (lista blanca)",
    "garita2_GBO-0429.jpg": "Garita 2 · GBO-0429 (lista restringida)",
    "garita1_GSA-1234.jpg": "Garita 1 · GSA-1234 (no registrada)",
    "garita3_PCD-5678_desenfocada.jpg": "Garita 3 · imagen desenfocada (verificación)",
}


def _decision_out(decision: AccessDecision) -> schemas.Decision:
    data = asdict(decision)
    data["permite_apertura"] = decision.permite_apertura
    data["vehiculo"] = plain(data.get("vehiculo"))
    return schemas.Decision(**data)


def _decide(plate: str | None, ocr_conf: float, det_conf: float | None,
            country='ecuador', jurisdiction=None, confirmed=False) -> AccessDecision:
    if country=='usa':
        return decide_usa_access(plate,jurisdiction,ocr_conf,get_store(),det_confidence=det_conf,
                                 temporal_confirmed=confirmed,
                                 automatic_enabled=get_config('usa')['automatic_access']['enabled'])
    ocr_threshold, det_threshold, distance = thresholds()
    return decide_access(plate, ocr_conf, get_store(), ocr_threshold, distance,
                         det_confidence=det_conf, det_threshold=det_threshold)

def _identity(raw, country='ecuador', jurisdiction=None):
    try:
        return normalize_identity(raw,country,jurisdiction)
    except ValueError as exc:
        raise HTTPException(422,str(exc)) from exc

def _recognition_out(rec,pipeline,image,receipt=None):
    crop_b64=None
    if rec.crop is not None and rec.crop.size:
        ok,buffer=cv2.imencode('.jpg',cv2.cvtColor(rec.crop,cv2.COLOR_RGB2BGR),[cv2.IMWRITE_JPEG_QUALITY,90])
        crop_b64=base64.b64encode(buffer.tobytes()).decode() if ok else None
    data=rec.as_dict()
    if rec.country=='usa':
        data.update(ocr_confidence=rec.ocr_confidence,det_confidence=rec.det_confidence)
    return schemas.Recognition(**data,detector_is_model=pipeline.detector.is_model,
        crop_jpeg_base64=crop_b64,image_width=int(image.shape[1]),image_height=int(image.shape[0]),
        evidence_id=receipt.id if receipt else None,confirmation_frames=len(receipt.frames) if receipt else 0,
        temporal_confirmed=receipt.confirmed if receipt else False)


@router.get("/samples", summary="Imágenes de ejemplo precargadas")
def list_samples(_: dict = Depends(current_user)) -> list[dict[str, str]]:
    return [{"nombre": name, "etiqueta": label, "url": f"/api/samples/{name}"}
            for name, label in SAMPLE_LABELS.items() if (SAMPLES_DIR / name).exists()]


@router.get("/samples/{name}", summary="Descargar una imagen de ejemplo", include_in_schema=False)
def get_sample(name: str) -> FileResponse:
    if name not in SAMPLE_LABELS:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ejemplo no encontrado.")
    return FileResponse(SAMPLES_DIR / name, media_type="image/jpeg")


@router.post("/recognize", response_model=schemas.RecognizeOut, summary="Reconocer la placa de una imagen")
def recognize(file: UploadFile = File(..., description="JPG, PNG o WEBP; máx. 10 MB"),
              country: schemas.Country = Form('ecuador'),
              garita: str = Form('',max_length=60),
              capture_session: str | None = Form(None,max_length=64),
              frame_id: str | None = Form(None,max_length=64),
              user: dict = Depends(current_user)) -> schemas.RecognizeOut:
    """Detecta la placa con RT-DETRv2, la lee con fast-plate-ocr, la normaliza y aplica la regla de acceso.

    No registra nada: el operador confirma después con ``POST /api/operations``.
    """
    country=profile_country(user,country)
    cfg = get_config(country)["app"]
    try:
        image = load_image(file.file.read(), ImageLimits(cfg["max_tamano_imagen_mb"], cfg["min_lado_imagen_px"]))
    except ImageValidationError as exc:
        raise HTTPException(422, str(exc))
    received_at=time.monotonic()
    try:
        pipeline = get_pipeline('usa') if country=='usa' else get_pipeline()
    except (ValueError,FileNotFoundError,RuntimeError) as exc:
        logger.error('No se pudo cargar el perfil %s: %s',country,exc)
        raise HTTPException(503,f'El modelo del perfil {country} no está disponible. Puede verificar la placa manualmente.') from exc
    try:
        if country=='usa':
            readings=pipeline.recognize_many(image)
            receipts=evidence_store.record(readings,owner=user['usuario'],gate=garita,
                session=capture_session or str(uuid.uuid4()),frame_id=frame_id or str(uuid.uuid4()),
                image_sha256=hashlib.sha256(image.tobytes()).hexdigest(),received_at=received_at)
            candidates=[]
            for rec,receipt in zip(readings,receipts):
                decision=_decide(rec.plate,rec.ocr_confidence,rec.det_confidence,'usa',rec.jurisdiction,receipt.confirmed)
                candidates.append(schemas.CandidateOut(recognition=_recognition_out(rec,pipeline,image,receipt),
                                                       decision=_decision_out(decision)))
            return schemas.RecognizeOut(**candidates[0].model_dump(),candidates=candidates)
        rec = pipeline.recognize(image)
        decision = _decide(rec.plate, rec.ocr_confidence,
                           rec.det_confidence if pipeline.detector.is_model else None)
    except StorageError as exc:
        logger.exception("Almacenamiento CSV: %s", exc)
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "No se pudieron consultar los archivos CSV.")
    recognition = _recognition_out(rec,pipeline,image)
    return schemas.RecognizeOut(recognition=recognition, decision=_decision_out(decision))


@router.post("/plates/vehicle-data", status_code=202, summary="Iniciar consulta de datos del vehículo")
def start_vehicle_data_lookup(body: schemas.VerifyIn, background_tasks: BackgroundTasks,
                              user: dict = Depends(current_user)) -> dict[str, str]:
    """Consulta datos vehiculares del SRI y el registro local; omite la fuente de pago de propietario."""
    profile_country(user,body.country)
    identity=_identity(body.placa,body.country,body.jurisdiction)
    plate=identity.serial
    if body.country=='usa':
        # U.S. plates never go to SRI. They go to J.D. Power only when vehicle_lookup.enabled is true in
        # config/countries/usa.yaml (authorized access); otherwise only the local registry is read.
        local=get_store().get_vehicle(identity.key)
        request_id=str(uuid.uuid4())
        base={'placa':plate,**identity.as_dict(),'vehiculo':public_plate_record(local) if local else {},
              'fuentes':{'local':'consultado','sri':'no_aplica','jdpower':'desactivado'}}
        if identity.jurisdiction and usa_jdpower.lookup_enabled(get_config('usa')):
            _store_lookup(request_id,{**base,'estado':'consultando'})
            background_tasks.add_task(_load_us_vehicle_details,request_id,plate,identity.jurisdiction,base)
            return {'request_id':request_id,'estado':'consultando','placa':plate}
        _store_lookup(request_id,{**base,'estado':'completado'})
        return {'request_id':request_id,'estado':'completado','placa':plate}
    request_id = str(uuid.uuid4())
    with _VEHICLE_LOOKUP_LOCK:
        cutoff = time.monotonic() - 900
        for old_id, value in list(_VEHICLE_LOOKUPS.items()):
            if value.get("_created_at", 0) < cutoff:
                _VEHICLE_LOOKUPS.pop(old_id, None)
        _VEHICLE_LOOKUPS[request_id] = {"estado": "consultando", "placa": plate}
    background_tasks.add_task(_load_vehicle_details, request_id, plate)
    return {"request_id": request_id, "estado": "consultando", "placa": plate}


@router.get("/plates/vehicle-data/{request_id}", summary="Consultar el estado de la búsqueda del vehículo")
def get_vehicle_data_lookup(request_id: str, _: dict = Depends(current_user)) -> dict:
    with _VEHICLE_LOOKUP_LOCK:
        result = _VEHICLE_LOOKUPS.get(request_id)
        if result is None:
            raise HTTPException(404, "La búsqueda ya no está disponible. Vuelva a consultar la placa.")
        return {key: value for key, value in result.items() if not key.startswith("_")}


@router.post("/plates/verify", response_model=schemas.VerifyOut, summary="Verificar una placa escrita a mano")
def verify_plate(body: schemas.VerifyIn, user: dict = Depends(current_user)) -> schemas.VerifyOut:
    profile_country(user,body.country)
    identity=_identity(body.placa,body.country,body.jurisdiction)
    plate=identity.serial
    if body.country=='usa':
        decision=_decide(plate,1.0,None,'usa',identity.jurisdiction)
        return schemas.VerifyOut(placa=plate,country='usa',jurisdiction=identity.jurisdiction,
                                  identity_key=identity.key,decision=_decision_out(decision))
    ocr_threshold, det_threshold, _ = thresholds()
    decision = decide_access(plate, 1.0, get_store(), ocr_threshold, 0)
    return schemas.VerifyOut(placa=plate, decision=_decision_out(decision))


@router.post("/plates/register", status_code=201, summary="Registrar un camión nuevo y, si se confirma, autorizarlo")
def register_vehicle(body: schemas.VehicleIn, user: dict = Depends(current_user)) -> dict[str, str]:
    """Los tres perfiles pueden registrar y autorizar; solo nuevos y con confirmación explícita."""
    profile_country(user,body.country)
    identity=_identity(body.placa,body.country,body.jurisdiction)
    plate=identity.key
    if not body.placa_confirmada:
        raise HTTPException(422, "Confirme visualmente la placa antes de registrar o autorizar.")
    required = {"marca": body.marca, "modelo": body.modelo, "color": body.color,
                "propietario": body.propietario or ""}
    missing = [name for name, value in required.items() if not value.strip()]
    if missing:
        raise HTTPException(422, f"Complete los campos obligatorios: {', '.join(missing)}.")
    try:
        db = get_store()
        db.create_vehicle_from_access(
            plate, body.marca.strip(), body.modelo.strip(), body.color.strip(),
            body.propietario.strip(), (body.transportista or "").strip(), user["usuario"])
    except ValueError as exc:
        if "ya está registrada" in str(exc):
            raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc
        raise HTTPException(422, str(exc)) from exc
    except StorageError as exc:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "No se pudo guardar el camión.") from exc

    if body.autorizar:
        try:
            db.set_authorization(plate, "BLANCA", "Autorización explícita tras verificación visual en garita",
                                 None, user["usuario"])
        except (StorageError, ValueError) as exc:
            logger.exception("Camión registrado sin lista blanca porque falló la autorización de %s", plate)
            raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE,
                                "Camión registrado, pero NO autorizado: falló el guardado de la lista blanca. "
                                "Un Administrador debe revisar el registro.") from exc
        return {"placa": identity.serial, "country":identity.country,"jurisdiction":identity.jurisdiction or '',
                "identity_key":identity.key,"mensaje": f"Camión {identity.lookup_key} registrado y autorizado por {user['usuario']}."}
    return {"placa": identity.serial,"country":identity.country,"jurisdiction":identity.jurisdiction or '',
            "identity_key":identity.key,"mensaje": f"Camión {identity.lookup_key} registrado, pendiente de autorización."}


def _operation_uuid(value):
    try:
        return str(uuid.UUID(value))
    except (ValueError, AttributeError, TypeError) as exc:
        raise HTTPException(422, "Identificador de operación UUID inválido.") from exc


def _operation_status(row, user, country):
    # Never identify an operator by a mutable/non-unique display name.
    owner=row.get('operador_usuario')
    allowed=owner==user['usuario'] or user.get('rol') in ('SUPERVISOR','ADMINISTRADOR')
    if row.get('country','ecuador')!=country or not allowed:
        raise HTTPException(404, 'Operación no encontrada.')
    state=row.get('estado_barrera') or 'INDETERMINADA'
    simulated={'true':True,'false':False}.get(row.get('barrera_simulada',''))
    messages={
        'CONFIRMADA':'Apertura confirmada en el historial. No se envió una nueva orden.',
        'FALLIDA':'El intento falló y está registrado. No se envió una nueva orden.',
        'CANCELADA':'Intento cancelado antes de su aceptación. No se abrió la barrera.',
        'NO_APLICA':'Operación registrada sin apertura.',
    }
    return schemas.OperationStatus(operacion_id=row['operacion_id'],country=country,
        garita=row['garita'],accion=row['accion'],resultado=row['resultado'],estado_barrera=state,
        barrera_abierta=True if state=='CONFIRMADA' else False if state in ('FALLIDA','CANCELADA','NO_APLICA') else None,
        barrera_simulada=simulated,requiere_revision=state not in messages,
        mensaje=messages.get(state,'La apertura no tiene confirmación definitiva. Revise el historial y la barrera; no repita la orden.'))


@router.get('/operations/{operacion_id}/status',response_model=schemas.OperationStatus,
            summary='Consultar una operación persistente sin repetir la orden')
def operation_status(operacion_id: str,response: Response,country: schemas.Country | None=None,
                     user: dict=Depends(current_user)):
    response.headers['Cache-Control']='no-store'
    selected=profile_country(user,country)
    row=get_store().operation(_operation_uuid(operacion_id))
    if row is None:
        raise HTTPException(404,'Operación no encontrada.')
    return _operation_status(row,user,selected)


@router.post('/operations/{operacion_id}/cancel',response_model=schemas.OperationStatus,
             summary='Reservar como cancelado un intento que todavía no fue aceptado')
def cancel_operation(operacion_id: str,body: schemas.CancelOperationIn,response: Response,
                     user: dict=Depends(current_user)):
    response.headers['Cache-Control']='no-store'
    selected=profile_country(user,body.country)
    op_id=_operation_uuid(operacion_id)
    db=get_store()
    row=db.operation(op_id)
    if row is None:
        try:
            # A durable tombstone races with acceptance using the same CSV CAS/UUID.
            # Whichever request is persisted first wins; this endpoint never actuates.
            db.log_operation(garita=body.garita,operador=user['nombre'],
                operador_usuario=user['usuario'],tipo_movimiento=body.tipo_movimiento,
                resultado='VERIFICACION_MANUAL',accion='SOLO_REGISTRO',origen='MANUAL',
                motivo='Cancelación previa de '+body.accion_solicitada,
                operacion_id=op_id,estado_barrera='CANCELADA',country=selected)
        except (ValueError,StorageError):
            # Another worker may have accepted it. Re-read, never repeat a stale write.
            row=db.operation(op_id)
            if row is None:
                raise HTTPException(503,'No se pudo confirmar la cancelación. Consulte el estado de la operación.')
        row=db.operation(op_id)
    return _operation_status(row,user,selected)


@router.post("/operations", response_model=schemas.OperationOut, status_code=201,
             summary="Registrar una operación (y abrir la barrera si corresponde)")
def register_operation(body: schemas.OperationIn, background_tasks: BackgroundTasks, user: dict = Depends(current_user)) -> schemas.OperationOut:
    """El resultado **no** se toma del cliente: se vuelve a calcular en el servidor con la placa final.

    - ``APERTURA_AUTOMATICA`` solo se acepta si la placa está AUTORIZADA.
    - ``APERTURA_MANUAL`` exige un motivo de al menos 10 caracteres.
    """
    profile_country(user,body.country)
    opening = body.accion in ("APERTURA_AUTOMATICA", "APERTURA_MANUAL")
    if opening and not body.operacion_id:
        raise HTTPException(422,'Toda apertura requiere un identificador de operación persistente.')
    op_id=_operation_uuid(body.operacion_id) if body.operacion_id else str(uuid.uuid4())
    db=get_store()
    # The durable ledger survives restarts and expired in-memory recognition receipts.
    if db.operation(op_id) is not None:
        raise HTTPException(409,'Operación duplicada: ya se registró la solicitud. No reintente la apertura.')
    identity=_identity(body.placa_final,body.country,body.jurisdiction) if body.placa_final and (
        body.country=='ecuador' or body.jurisdiction) else None
    plate=identity.serial if identity else None
    receipt=None
    if body.country=='usa' and body.origen=='DETECCION':
        try:
            receipt=evidence_store.get(body.evidence_id,owner=user['usuario'],gate=body.garita,
                                       identity_key=identity.key if identity else None)
        except ValueError as exc:
            raise HTTPException(409,str(exc)) from exc
        rec=receipt.reading
        if body.placa_final and body.placa_final.replace('-','').replace(' ','').upper()!=rec.plate:
            raise HTTPException(409,'La matrícula no coincide con la lectura guardada en el servidor.')
        plate=rec.plate
        body.jurisdiction=rec.jurisdiction
        identity=_identity(plate,'usa',rec.jurisdiction) if plate and rec.jurisdiction else None
        body.confianza_ocr=rec.ocr_confidence
        body.det_confidence=rec.det_confidence
        body.placa_leida=rec.plate_raw
    if body.country=='usa' and body.origen=='MANUAL' and body.accion=='APERTURA_AUTOMATICA':
        raise HTTPException(409,'La apertura automática requiere dos lecturas del detector confirmadas en el servidor.')
    confidence = 1.0 if body.origen == "MANUAL" else (body.confianza_ocr or 0.0)
    decision = _decide(plate, confidence, None if body.origen == "MANUAL" else body.det_confidence,
                       body.country,body.jurisdiction,receipt.confirmed if receipt else False)
    if body.accion == "APERTURA_AUTOMATICA" and not decision.permite_apertura:
        raise HTTPException(status.HTTP_409_CONFLICT,
                            f"No se puede abrir automáticamente: el resultado es {decision.resultado}. "
                            "Use la apertura manual (contingencia) si corresponde.")
    if body.accion == "APERTURA_MANUAL" and len((body.motivo or "").strip()) < 10:
        raise HTTPException(422, "La apertura manual exige un motivo (mín. 10 caracteres).")
    barrier = get_barrier()
    # El almacenamiento efímero no es suficiente para accionar una barrera física.
    if not getattr(barrier, "simulated", True) and not durable_backup_configured():
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE,
                            "Apertura bloqueada: configure primero el respaldo CSV privado y persistente.")
    final = plate if decision.resultado != "VERIFICACION_MANUAL" or body.origen == "MANUAL" else None
    claimed=False
    if body.country=='usa' and body.accion=='APERTURA_AUTOMATICA':
        try:
            receipt=evidence_store.get(body.evidence_id,owner=user['usuario'],gate=body.garita,
                                       identity_key=identity.key,claim=True)
            claimed=True
        except ValueError as exc:
            raise HTTPException(409,str(exc)) from exc

    # 1. Se escribe la solicitud antes de emitir cualquier orden de apertura.
    try:
        db.log_operation(
            garita=body.garita, operador=user["nombre"], tipo_movimiento=body.tipo_movimiento,
            resultado=decision.resultado, accion=body.accion, placa_leida=body.placa_leida, placa_final=final,
            confianza_ocr=body.confianza_ocr, lista=decision.lista, motivo=(body.motivo or None),
            origen=body.origen, tiempo_ms=body.tiempo_ms, operacion_id=op_id,
            estado_barrera="SOLICITADA" if opening else "NO_APLICA",
            country=body.country,jurisdiction=body.jurisdiction,
            identity_key=identity.key if identity else None,
            evidence_id=receipt.id if receipt else None,evidence_json=receipt.audit() if receipt else None,
            det_confidence=body.det_confidence,model_seed=2 if receipt else None,
            operador_usuario=user['usuario'],barrera_simulada=getattr(barrier,'simulated',True))
    except ValueError as exc:
        if claimed:
            evidence_store.release(receipt.id)
        if "Operación duplicada" in str(exc):
            raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc
        raise HTTPException(422, f"No se pudo registrar: {exc}") from exc
    except StorageError as exc:
        if claimed:
            evidence_store.release(receipt.id)
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE,
                            "Apertura bloqueada: no se pudo guardar primero la solicitud en el CSV.") from exc

    if claimed:
        evidence_store.consume(receipt)

    # 2. La barrera solo recibe la orden después de persistir la solicitud.
    opened = False
    barrier_state = "NO_APLICA"
    if opening:
        barrier_state = "INDETERMINADA"  # Un fallo de red no demuestra que una barrera física esté cerrada.
        try:
            if hasattr(barrier,'open_operation'):
                opened=bool(barrier.open_operation(op_id,body.garita,body.accion))
            else:
                opened = bool(barrier.open(body.garita, body.accion))
            barrier_state = "CONFIRMADA" if opened else (
                "FALLIDA" if getattr(barrier, "simulated", False) else "INDETERMINADA")
        except Exception:
            logger.exception("No se pudo confirmar la apertura para operación %s", op_id)
        try:
            db.update_operation_state(op_id, barrier_state)
        except (StorageError, ValueError) as exc:
            logger.exception("No se pudo conciliar el estado de apertura %s; queda solicitud persistida", op_id)
            raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE,
                                f"Estado de apertura no conciliado para operación {op_id}. "
                                "NO vuelva a intentar automáticamente; revise el historial y la barrera.") from exc
        if not opened:
            raise HTTPException(status.HTTP_502_BAD_GATEWAY,
                                f"La barrera no confirmó la apertura. Operación {op_id} registrada "
                                f"con estado {barrier_state}; solicite revisión, no repita automáticamente.")
    export_saved = False
    if body.origen == "DETECCION" and final:
        vehicle = decision.vehiculo or {}
        auth = vehicle.get("autorizacion") or {}
        row = {
            "event_id": str(uuid.uuid4()),
            "fecha_hora": now_local().isoformat(sep=" ", timespec="seconds"),
            "modelo_detector": "RT-DETRv2-S/OpenVINO" if body.det_confidence is not None else "",
            "camara": "",
            "garita": body.garita,
            "operador": user["nombre"],
            "tipo_movimiento": body.tipo_movimiento,
            "accion": body.accion,
            "origen": body.origen,
            "placa": final,
            "country":body.country,"jurisdiction":body.jurisdiction or '',
            "identity_key":identity.key if identity else '',
            "evidence_id":receipt.id if receipt else '',"model_seed":2 if receipt else '',
            "texto_ocr": body.placa_leida or final,
            "formato_valido": True,
            "confianza_ocr": body.confianza_ocr,
            "confianza_detector": body.det_confidence,
            "disparador": "operacion_confirmada",
            "resultado_acceso": decision.resultado,
            "lista": decision.lista,
            "estado_vehiculo_planta": auth.get("lista", ""),
            "transportista": vehicle.get("transportista", ""),
            "marca_planta": vehicle.get("marca", ""),
            "modelo_planta": vehicle.get("modelo", ""),
            "color_planta": vehicle.get("color", ""),
            "tipo_vehiculo_planta": vehicle.get("tipo", ""),
            "propietario_registrado": vehicle.get("propietario", ""),
        }
        try:
            append_detection(row)
            export_saved = True
            if body.country=='ecuador':
                background_tasks.add_task(enrich_detection, row["event_id"], final, row["marca_planta"])
        except Exception as exc:
            logger.exception("No se pudo guardar la detección en GitHub: %s", exc)
    messages = {"APERTURA_AUTOMATICA": "Operación registrada y barrera abierta.",
                "APERTURA_MANUAL": "Apertura manual registrada en el historial.",
                "RECHAZO": "Rechazo registrado; la barrera permanece cerrada.",
                "SOLO_REGISTRO": "Operación registrada sin abrir la barrera."}
    if body.origen == "DETECCION" and final:
        messages[body.accion] += ((' Detección guardada; datos del registro local de Estados Unidos.' if body.country=='usa' else
                                  " Detección guardada en el CSV de GitHub; consultando los datos vehiculares del SRI.")
                                  if export_saved else
                                  " No se guardó en GitHub; revise la configuración del repositorio y el token.")
    return schemas.OperationOut(registrada=True, resultado=decision.resultado, accion=body.accion,
                                barrera_abierta=opened, barrera_simulada=getattr(barrier, "simulated", True),
                                operacion_id=op_id, estado_barrera=barrier_state, mensaje=messages[body.accion])

