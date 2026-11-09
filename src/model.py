"""SIRAP inference: RT-DETRv2-S with native OpenVINO Runtime, plus OCR."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence

import numpy as np
from PIL import Image

from src.data_processing import DEFAULT_PATTERNS, clean_text, crop_with_margin, normalize_plate
from src.utils import get_logger, load_config, load_json, resolve_path, timer

logger = get_logger("sirap.model")
DEFAULT_PLATE_CHECKPOINT = "merve/license-plates-rtdetrv2"
DEFAULT_OPENVINO_CHECKPOINT = "models/shared/detector/rtdetrv2_s/openvino"
DEFAULT_IMAGE_SIZE = 640
IMAGE_MEAN = np.asarray([0.485, 0.456, 0.406], dtype=np.float32)
IMAGE_STD = np.asarray([0.229, 0.224, 0.225], dtype=np.float32)


@dataclass
class Detection:
    """Una caja de matrícula detectada; coordenadas xyxy en píxeles."""

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


def _openvino_xml(checkpoint: str | Path | None) -> Path | None:
    if not checkpoint:
        return None
    candidate = resolve_path(checkpoint)
    if candidate.is_file():
        if candidate.suffix.lower() == ".xml":
            return candidate
        raise ValueError(
            f"{candidate} no es un modelo OpenVINO IR. Se requiere el archivo XML y su BIN asociado; "
            "los pesos Transformers, ONNX y YOLO no se cargan directamente en el detector."
        )
    if candidate.is_dir():
        for xml_path in (candidate / "openvino_model.xml", candidate / "model.xml",
                         candidate / "openvino" / "openvino_model.xml",
                         candidate / "openvino" / "model.xml"):
            if xml_path.is_file():
                return xml_path
        if any(candidate.glob("*.onnx")) or any(candidate.glob("*.safetensors")):
            raise ValueError(
                f"{candidate} contiene pesos fuente, pero no un IR OpenVINO. Ejecute "
                "python -m src.export_openvino para convertir el checkpoint antes de iniciar la app."
            )
    return None


class PlateDetector:
    """Carga un IR RT-DETRv2-S y ejecuta inferencia con openvino.Core.

    El checkpoint fino del país tiene prioridad. Si no existe, se utiliza el IR
    compartido creado durante la construcción del Space. El entrenamiento y la
    conversión ocurren antes del despliegue; esta clase no importa Transformers
    ni PyTorch.
    """

    def __init__(self, checkpoint: str | Path | None = None,
                 model_id: str = DEFAULT_PLATE_CHECKPOINT, imgsz: int = DEFAULT_IMAGE_SIZE,
                 conf: float = 0.25, class_id: int = 0, device: str = "CPU",
                 fallback_checkpoint: str | Path | None = DEFAULT_OPENVINO_CHECKPOINT):
        import openvino as ov

        self.imgsz = int(imgsz)
        self.conf = float(conf)
        self.class_id = int(class_id)
        self.device = "CPU" if device.lower() == "auto" else device.upper()
        self.core = ov.Core()

        requested_xml = _openvino_xml(checkpoint)
        shared_xml = _openvino_xml(fallback_checkpoint)
        self.model_path = requested_xml or shared_xml
        if self.model_path is None:
            raise FileNotFoundError(
                "No se encontró un IR OpenVINO de RT-DETRv2-S. Convierta el checkpoint Apache-2.0 "
                f"{model_id!r} y guárdelo en {fallback_checkpoint!s}."
            )
        if not self.model_path.with_suffix(".bin").is_file():
            raise FileNotFoundError(f"Falta el archivo de pesos OpenVINO asociado: {self.model_path.with_suffix('.bin')}")

        self.compiled_model = self.core.compile_model(str(self.model_path), self.device)
        self.manifest = {}
        manifest_path = self.model_path.parent / "sirap_openvino.json"
        if manifest_path.is_file():
            try:
                import json
                self.manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            except (OSError, ValueError) as exc:
                raise ValueError(f"Manifest OpenVINO inválido: {manifest_path}") from exc
        if len(self.compiled_model.inputs) != 2:
            raise ValueError(
                "El IR RT-DETRv2-S debe aceptar pixel_values y pixel_mask. "
                f"Se encontraron {len(self.compiled_model.inputs)} entradas."
            )
        if len(self.compiled_model.outputs) < 2:
            raise ValueError("El IR RT-DETRv2-S debe devolver logits y pred_boxes.")
        self.name = f"RT-DETRv2-S · OpenVINO Runtime · {self.model_path.parent}"
        self.source = str(self.model_path)
        logger.info("Detector cargado: %s (%s)", self.name, self.device)

    @property
    def is_model(self) -> bool:
        return True

    def _preprocess(self, image: np.ndarray) -> tuple[np.ndarray, np.ndarray, tuple[int, int]]:
        height, width = image.shape[:2]
        max_height = min(self.imgsz, int(self.manifest.get("resize_max_height", self.imgsz)))
        max_width = min(self.imgsz, int(self.manifest.get("resize_max_width", self.imgsz)))
        scale = min(max_height / height, max_width / width)
        resized_h = max(1, min(max_height, int(round(height * scale))))
        resized_w = max(1, min(max_width, int(round(width * scale))))
        rgb = np.ascontiguousarray(image[..., :3], dtype=np.uint8)
        resample = self.manifest.get("resample", 2)
        try:
            resampling = Image.Resampling(int(resample))
        except (TypeError, ValueError):
            resampling = Image.Resampling.BILINEAR
        resized = Image.fromarray(rgb).resize((resized_w, resized_h), resampling)
        pixels = np.array(resized, dtype=np.float32, copy=True)
        if self.manifest.get("do_rescale", True):
            pixels *= float(self.manifest.get("rescale_factor", 1.0 / 255.0))
        if self.manifest.get("do_normalize", False):
            mean = np.asarray(self.manifest.get("image_mean", IMAGE_MEAN), dtype=np.float32)
            std = np.asarray(self.manifest.get("image_std", IMAGE_STD), dtype=np.float32)
            pixels = (pixels - mean) / std

        # RTDetrImageProcessor pads after rescaling/normalization and masks padded pixels.
        pad_value = float(self.manifest.get("pad_value_after_normalization", 0.0))
        canvas = np.full((3, self.imgsz, self.imgsz), pad_value, dtype=np.float32)
        canvas[:, :resized_h, :resized_w] = pixels.transpose(2, 0, 1)
        pixel_mask = np.zeros((1, self.imgsz, self.imgsz), dtype=np.int64)
        pixel_mask[:, :resized_h, :resized_w] = 1
        return canvas[None, ...], pixel_mask, (height, width)

    def detect(self, image: np.ndarray, max_detections: int = 5) -> list[Detection]:
        """Devuelve cajas de placa en orden de confianza descendente."""
        if image is None or image.size == 0 or image.ndim != 3:
            return []
        pixel_values, pixel_mask, (height, width) = self._preprocess(image)
        raw = self.compiled_model([pixel_values, pixel_mask])
        logits = np.asarray(raw[self.compiled_model.output(0)], dtype=np.float32)[0]
        boxes = np.asarray(raw[self.compiled_model.output(1)], dtype=np.float32)[0]
        if logits.ndim != 2 or boxes.ndim != 2 or boxes.shape[-1] != 4:
            raise ValueError(f"Salidas OpenVINO inesperadas: logits={logits.shape}, boxes={boxes.shape}.")

        scores = 1.0 / (1.0 + np.exp(-np.clip(logits, -80.0, 80.0)))
        flat_scores = scores.reshape(-1)
        count = min(flat_scores.size, max(1, int(max_detections)))
        indices = np.argpartition(flat_scores, -count)[-count:]
        indices = indices[np.argsort(flat_scores[indices])[::-1]]
        num_classes = scores.shape[-1]
        detections: list[Detection] = []
        for flat_index in indices:
            query_index, label = divmod(int(flat_index), num_classes)
            score = float(flat_scores[flat_index])
            if label != self.class_id or score < self.conf:
                continue
            cx, cy, box_w, box_h = (float(value) for value in boxes[query_index])
            x1 = (cx - box_w / 2) * width
            y1 = (cy - box_h / 2) * height
            x2 = (cx + box_w / 2) * width
            y2 = (cy + box_h / 2) * height
            detections.append(Detection(
                (float(np.clip(x1, 0, width)), float(np.clip(y1, 0, height)),
                 float(np.clip(x2, 0, width)), float(np.clip(y2, 0, height))),
                score,
            ))
        detections.sort(key=lambda detection: detection.confidence, reverse=True)
        return detections


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
    """Detección OpenVINO + OCR + normalización para una imagen."""

    def __init__(self, detector: PlateDetector, reader: PlateReader,
                 patterns: Sequence[Sequence[int]] = DEFAULT_PATTERNS,
                 margin: float = 0.06, max_candidates: int = 5):
        self.detector, self.reader = detector, reader
        self.patterns = patterns
        self.margin = float(margin)
        self.max_candidates = int(max_candidates)

    @classmethod
    def from_config(cls, config: dict[str, Any] | None = None) -> "ALPRPipeline":
        """Construye el pipeline con el IR OpenVINO del país o el compartido."""
        cfg = config or load_config()
        det_cfg, ocr_cfg = cfg["detector"], cfg["ocr"]
        calibrated = load_json("results/metrics/umbrales_rtdetr.json") or {}
        calibrated_conf = calibrated.get("RT-DETRv2-S", {}).get("conf_track")
        conf = float(calibrated_conf or det_cfg.get("conf_minima", 0.25))
        detector = PlateDetector(
            checkpoint=det_cfg.get("checkpoint"),
            model_id=det_cfg.get("model_id", DEFAULT_PLATE_CHECKPOINT),
            imgsz=det_cfg.get("imgsz_inferencia", DEFAULT_IMAGE_SIZE),
            conf=conf,
            class_id=det_cfg.get("class_id", 0),
            device=det_cfg.get("dispositivo", "CPU"),
            fallback_checkpoint=det_cfg.get("fallback_checkpoint", DEFAULT_OPENVINO_CHECKPOINT),
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
