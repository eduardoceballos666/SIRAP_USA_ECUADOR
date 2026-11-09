"""Modelos de SIRAP: RT-DETRv2 R18 con Transformers, OCR y pipeline ALPR.

El detector predeterminado es el checkpoint público
``merve/license-plates-rtdetrv2`` (Apache-2.0), ajustado para detectar matrículas.
Cuando existe un checkpoint local del país, tiene prioridad sobre el checkpoint público.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence

import numpy as np

from src.data_processing import DEFAULT_PATTERNS, clean_text, crop_with_margin, normalize_plate
from src.utils import get_logger, load_config, load_json, resolve_path, timer

logger = get_logger("sirap.model")
DEFAULT_PLATE_CHECKPOINT = "merve/license-plates-rtdetrv2"


@dataclass
class Detection:
    """Una caja de matrícula detectada; coordenadas xyxy en píxeles de la imagen original."""

    box: tuple[float, float, float, float]
    confidence: float

    @property
    def area(self) -> float:
        x1, y1, x2, y2 = self.box
        return max(0.0, x2 - x1) * max(0.0, y2 - y1)


@dataclass
class Recognition:
    """Resultado completo del reconocimiento de una imagen."""

    plate: str | None
    plate_raw: str = ""
    ocr_confidence: float = 0.0
    ocr_mean_confidence: float = 0.0
    det_confidence: float = 0.0
    box: tuple[float, float, float, float] | None = None
    crop: np.ndarray | None = field(default=None, repr=False)
    detector: str = ""
    timings_ms: dict[str, float] = field(default_factory=dict)
    candidates: int = 0

    @property
    def found(self) -> bool:
        return self.plate is not None

    def as_dict(self) -> dict[str, Any]:
        """Versión serializable para registrar o exportar, sin incluir el recorte."""
        return {
            "plate": self.plate,
            "plate_raw": self.plate_raw,
            "ocr_confidence": round(self.ocr_confidence, 4),
            "ocr_mean_confidence": round(self.ocr_mean_confidence, 4),
            "det_confidence": round(self.det_confidence, 4),
            "box": [round(v, 1) for v in self.box] if self.box else None,
            "detector": self.detector,
            "timings_ms": {k: round(v, 1) for k, v in self.timings_ms.items()},
        }


class PlateDetector:
    """Carga y ejecuta RT-DETRv2 mediante Transformers y PyTorch.

    Args:
        checkpoint: carpeta local creada por ``src.train``. Si no existe, se usa
            ``model_id`` desde el Hub de Hugging Face.
        model_id: checkpoint compatible con ``RTDetrV2ForObjectDetection``.
        imgsz: resolución cuadrada configurada por el procesador del checkpoint.
        conf: confianza mínima de una detección.
        class_id: clase que representa la matrícula en el checkpoint.
        device: ``"auto"``, ``"cpu"`` o un dispositivo PyTorch como ``"cuda"``.
    """

    def __init__(self, checkpoint: str | Path | None = None,
                 model_id: str = DEFAULT_PLATE_CHECKPOINT, imgsz: int = 640,
                 conf: float = 0.25, class_id: int = 0, device: str = "auto"):
        import torch
        from transformers import AutoImageProcessor, RTDetrV2ForObjectDetection

        self.imgsz = int(imgsz)
        self.conf = float(conf)
        self.class_id = int(class_id)
        self._torch = torch
        self.device = torch.device(
            "cuda" if device == "auto" and torch.cuda.is_available()
            else "cpu" if device == "auto" else device
        )

        local_dir = resolve_path(checkpoint) if checkpoint else None
        if local_dir is not None and local_dir.is_dir() and (local_dir / "config.json").exists():
            source = str(local_dir)
        else:
            source = model_id
            if local_dir is not None and local_dir.exists():
                raise ValueError(
                    f"{local_dir} no es una carpeta Transformers. Los pesos YOLO/ONNX no son compatibles; "
                    "ejecute el notebook 03 para generar un checkpoint RT-DETRv2."
                )

        self.source = source
        self._processor = AutoImageProcessor.from_pretrained(source, trust_remote_code=False, use_fast=False)
        self._model = RTDetrV2ForObjectDetection.from_pretrained(source, trust_remote_code=False)
        self._model.to(self.device)
        self._model.eval()
        num_labels = int(getattr(self._model.config, "num_labels", 0))
        if self.class_id < 0 or self.class_id >= num_labels:
            raise ValueError(
                f"class_id={self.class_id} no existe en {source}; el checkpoint tiene {num_labels} clases."
            )
        self.name = f"RT-DETRv2 R18 · Transformers · {source}"
        logger.info("Detector cargado: %s (%s)", self.name, self.device)

    @property
    def is_model(self) -> bool:
        return self._model is not None

    def detect(self, image: np.ndarray, max_detections: int = 5) -> list[Detection]:
        """Devuelve cajas de matrícula en orden descendente de confianza."""
        if image is None or image.size == 0 or image.ndim != 3:
            return []
        height, width = image.shape[:2]
        rgb = np.ascontiguousarray(image[..., :3], dtype=np.uint8)
        inputs = self._processor(images=rgb, return_tensors="pt")
        inputs = {key: value.to(self.device) for key, value in inputs.items()}
        with self._torch.inference_mode():
            outputs = self._model(**inputs)
        target_sizes = self._torch.tensor([(height, width)], dtype=self._torch.int64)
        result = self._processor.post_process_object_detection(
            outputs, target_sizes=target_sizes, threshold=self.conf
        )[0]
        boxes = result["boxes"].detach().cpu().numpy()
        scores = result["scores"].detach().cpu().numpy()
        labels = result["labels"].detach().cpu().numpy()
        detections = []
        for box, score, label in zip(boxes, scores, labels):
            if int(label) != self.class_id:
                continue
            x1, y1, x2, y2 = (float(v) for v in box)
            detections.append(Detection(
                (float(np.clip(x1, 0, width)), float(np.clip(y1, 0, height)),
                 float(np.clip(x2, 0, width)), float(np.clip(y2, 0, height))),
                float(score),
            ))
        detections.sort(key=lambda detection: detection.confidence, reverse=True)
        return detections[:max_detections]


class PlateReader:
    """Lee caracteres de un recorte de matrícula con fast-plate-ocr."""

    def __init__(self, model_name: str = "cct-s-v2-global-model", device: str = "cpu",
                 onnx_path: str | Path | None = None, plate_config_path: str | Path | None = None):
        from fast_plate_ocr import LicensePlateRecognizer

        onnx_file = resolve_path(onnx_path) if onnx_path else None
        config_file = resolve_path(plate_config_path) if plate_config_path else None
        if onnx_file and config_file and onnx_file.exists() and config_file.exists():
            self.model_name = f"{model_name} afinado ({onnx_file.name})"
            self._model = LicensePlateRecognizer(onnx_model_path=onnx_file,
                                                 plate_config_path=config_file, device=device)
        else:
            self.model_name = model_name
            self._model = LicensePlateRecognizer(model_name, device=device)

    def read(self, crop: np.ndarray) -> tuple[str, float, float]:
        """Devuelve texto, mínima confianza por carácter y confianza promedio."""
        if crop is None or crop.size == 0:
            return "", 0.0, 0.0
        prediction = self._model.run(np.ascontiguousarray(crop), return_confidence=True)[0]
        text = clean_text(prediction.plate)
        probs = np.asarray(prediction.char_probs, dtype=np.float32).ravel()
        used = probs[:max(len(text), 1)]
        if not used.size:
            return text, 0.0, 0.0
        return text, float(used.min()), float(used.mean())


class ALPRPipeline:
    """Detección + OCR + normalización para una imagen."""

    def __init__(self, detector: PlateDetector, reader: PlateReader,
                 patterns: Sequence[Sequence[int]] = DEFAULT_PATTERNS,
                 margin: float = 0.06, max_candidates: int = 5):
        self.detector, self.reader = detector, reader
        self.patterns = patterns
        self.margin = float(margin)
        self.max_candidates = int(max_candidates)

    @classmethod
    def from_config(cls, config: dict[str, Any] | None = None) -> "ALPRPipeline":
        """Construye el pipeline con el checkpoint Transformers configurado."""
        cfg = config or load_config()
        det_cfg, ocr_cfg = cfg["detector"], cfg["ocr"]
        calibrated = load_json("results/metrics/umbrales_rtdetr.json") or {}
        calibrated_conf = calibrated.get("RT-DETRv2", {}).get("conf_track")
        conf = float(calibrated_conf or det_cfg.get("conf_minima", 0.25))
        detector = PlateDetector(
            checkpoint=det_cfg.get("checkpoint"),
            model_id=det_cfg.get("model_id", DEFAULT_PLATE_CHECKPOINT),
            imgsz=det_cfg.get("imgsz_inferencia", 640),
            conf=conf,
            class_id=det_cfg.get("class_id", 0),
            device=det_cfg.get("dispositivo", "auto"),
        )
        reader = PlateReader(ocr_cfg.get("modelo", "cct-s-v2-global-model"),
                             ocr_cfg.get("dispositivo", "cpu"),
                             ocr_cfg.get("onnx_afinado"),
                             ocr_cfg.get("plate_config_afinado"))
        patterns = [tuple(pattern) for pattern in cfg.get("placas", {}).get("patrones", DEFAULT_PATTERNS)]
        return cls(detector, reader, patterns, det_cfg.get("margen_recorte", 0.06))

    def recognize(self, image: np.ndarray) -> Recognition:
        """Reconoce la matrícula principal de ``image`` (RGB)."""
        timings: dict[str, float] = {}
        with timer() as t_det:
            detections = self.detector.detect(image, self.max_candidates)
        timings["deteccion"] = t_det["ms"]
        best: Recognition | None = None
        with timer() as t_ocr:
            for detection in detections:
                crop = crop_with_margin(image, detection.box, self.margin)
                raw, confidence, mean_confidence = self.reader.read(crop)
                candidate = Recognition(
                    normalize_plate(raw, self.patterns), raw, confidence, mean_confidence,
                    detection.confidence, detection.box, crop, self.detector.name,
                )
                key = (candidate.found, candidate.ocr_confidence, candidate.det_confidence)
                if best is None or key > (best.found, best.ocr_confidence, best.det_confidence):
                    best = candidate
                if candidate.found:
                    break
        timings["ocr"] = t_ocr["ms"]
        timings["total"] = timings["deteccion"] + timings["ocr"]
        result = best or Recognition(None, detector=self.detector.name)
        result.timings_ms = timings
        result.candidates = len(detections)
        logger.info("Reconocimiento: placa=%s raw=%s conf=%.3f detector=%s %.0f ms",
                    result.plate, result.plate_raw, result.ocr_confidence,
                    self.detector.name, timings["total"])
        return result
