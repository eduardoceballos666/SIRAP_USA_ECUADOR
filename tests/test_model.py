"""Pruebas del pipeline de reconocimiento, la regla de decisión y las métricas.

Las pruebas del OCR descargan el modelo de fast-plate-ocr (≈5 MB) la primera vez; si no hay
red se omiten.
"""

import pytest

from src.access_control import decide_access
from src.evaluate import character_error_rate, exact_match_rate, f1_score
from src.model import Detection, PlateDetector

# ---- regla de decisión ----------------------------------------------------------------------
@pytest.mark.parametrize("plate, conf, expected", [
    ("PBA-8901", 0.98, "AUTORIZADO"),          # lista blanca
    ("GBO-0429", 0.98, "DENEGADO"),            # lista restringida
    ("GSA-1234", 0.98, "NO_REGISTRADO"),       # no está en la base
    ("PBA-8907", 0.98, "VERIFICACION_MANUAL"),  # a un carácter de una placa registrada
    ("PBA-8901", 0.40, "VERIFICACION_MANUAL"),  # confianza baja
    (None, 0.0, "VERIFICACION_MANUAL"),        # sin lectura
])
def test_decide_access(seeded_db, plate, conf, expected):
    decision = decide_access(plate, conf, seeded_db, confidence_threshold=0.85)
    assert decision.resultado == expected
    assert decision.permite_apertura == (expected == "AUTORIZADO")


def test_decision_suggests_similar_plate(seeded_db):
    assert decide_access("PBA-8907", 0.99, seeded_db).sugerencia == "PBA-8901"


def test_authorized_vehicle_details(seeded_db):
    vehicle = decide_access("PBA-8901", 0.99, seeded_db).vehiculo
    assert vehicle["marca"] == "Toyota" and vehicle["propietario"] == "Juan Pérez"


def test_revoked_vehicle_is_not_authorized(seeded_db):
    seeded_db.revoke_authorization("PBA-8901")
    assert decide_access("PBA-8901", 0.99, seeded_db).resultado == "NO_REGISTRADO"


# ---- métricas ---------------------------------------------------------------------------------
def test_metrics():
    assert exact_match_rate(["PBA8901", "GBO-0429", None], ["PBA-8901", "GBO-0428", "GSA-1234"]) == pytest.approx(1 / 3)
    assert character_error_rate(["PBA8901"], ["PBA8901"]) == 0.0
    assert character_error_rate(["PBA8907"], ["PBA8901"]) == pytest.approx(1 / 7)
    assert f1_score(0.9, 0.8) == pytest.approx(0.8470588, rel=1e-5)
    assert f1_score(0, 0) == 0.0


# ---- detector -------------------------------------------------------------------------------
def test_detector_rejects_legacy_onnx_checkpoint(tmp_path):
    legacy = tmp_path / "old_detector.onnx"
    legacy.write_bytes(b"legacy checkpoint")
    with pytest.raises(ValueError, match="no es un modelo OpenVINO IR"):
        PlateDetector(legacy, model_id="merve/license-plates-rtdetrv2")


def test_detection_area():
    assert Detection((0, 0, 10, 5), 0.9).area == 50


# ---- pipeline (componentes simulados para no asumir métricas del checkpoint público) --------
def test_pipeline_combines_detection_and_ocr():
    import numpy as np
    from src.model import ALPRPipeline

    class DetectorStub:
        is_model = True
        name = "RT-DETRv2-S/OpenVINO (stub)"

        def detect(self, image, max_detections=5):
            return [Detection((10, 10, 90, 40), 0.98)]

    class ReaderStub:
        model_name = "OCR (stub)"

        def read(self, crop):
            assert crop.size > 0
            return "PBA8901", 0.99, 0.99

    pipeline = ALPRPipeline(DetectorStub(), ReaderStub())
    result = pipeline.recognize(np.zeros((80, 120, 3), dtype=np.uint8))
    assert result.plate == "PBA-8901"
    assert result.det_confidence == pytest.approx(0.98)
    assert result.ocr_confidence == pytest.approx(0.99)
    assert result.timings_ms["total"] >= 0


def test_pipeline_without_detection_requires_manual_review(seeded_db):
    import numpy as np
    from src.model import ALPRPipeline

    class DetectorStub:
        is_model = True
        name = "RT-DETRv2-S/OpenVINO (stub)"

        def detect(self, image, max_detections=5):
            return []

    class ReaderStub:
        model_name = "OCR (stub)"

        def read(self, crop):
            raise AssertionError("El OCR no debe ejecutarse sin una detección")

    result = ALPRPipeline(DetectorStub(), ReaderStub()).recognize(
        np.zeros((80, 120, 3), dtype=np.uint8)
    )
    decision = decide_access(result.plate, result.ocr_confidence, seeded_db, confidence_threshold=0.85)
    assert decision.resultado == "VERIFICACION_MANUAL"


def test_low_detector_confidence_goes_to_manual(seeded_db):
    decision = decide_access("PBA-8901", 1.0, seeded_db, det_confidence=0.2, det_threshold=0.30)
    assert decision.resultado == "VERIFICACION_MANUAL" and "DETECCIÓN" in decision.detalle
    assert decide_access("PBA-8901", 1.0, seeded_db, det_confidence=0.8, det_threshold=0.30).resultado == "AUTORIZADO"


def test_reader_falls_back_to_hub_model_without_finetuned_files(tmp_path):
    """Si no existen los archivos del OCR afinado, se usa el modelo del hub."""
    try:
        from src.model import PlateReader

        reader = PlateReader("cct-s-v2-global-model", "cpu", tmp_path / "no.onnx", tmp_path / "no.yaml")
    except Exception as exc:  # noqa: BLE001 — sin red no se descarga el OCR
        pytest.skip(f"OCR no disponible: {exc}")
    assert reader.model_name == "cct-s-v2-global-model"
