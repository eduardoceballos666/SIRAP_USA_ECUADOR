"""Evaluación COCO de RT-DETRv2 y medición punta a punta del pipeline SIRAP."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd

from src.data_processing import clean_text, load_image, normalize_plate, plate_distance
from src.model import ALPRPipeline, PlateDetector
from src.train import CocoPlateDataset, DEFAULT_MODEL_ID
from src.utils import get_logger, load_config, resolve_path, save_json

logger = get_logger("sirap.evaluate")


def exact_match_rate(predictions: Iterable[str | None], references: Iterable[str | None]) -> float:
    pairs = list(zip(predictions, references))
    if not pairs:
        return 0.0
    hits = sum(1 for prediction, reference in pairs
               if prediction is not None and normalize_plate(prediction) == normalize_plate(reference))
    return hits / len(pairs)


def character_error_rate(predictions: Iterable[str | None], references: Iterable[str | None]) -> float:
    errors = total = 0
    for prediction, reference in zip(predictions, references):
        ref = clean_text(reference)
        errors += plate_distance(prediction or "", ref)
        total += len(ref)
    return errors / total if total else 0.0


def f1_score(precision: float, recall: float) -> float:
    return 2 * precision * recall / (precision + recall) if precision + recall else 0.0


def evaluate_detector(data_dir: str | Path, country: str = "ecuador", split: str = "test",
                      checkpoint: str | Path | None = None, model_id: str = DEFAULT_MODEL_ID,
                      threshold: float = 0.001,
                      result_path: str | Path | None = None,
                      operating_threshold: float | None = None) -> dict[str, Any]:
    """Measure standard COCO AP and actual TP/FP/FN at a fixed confidence."""
    import hashlib
    import io
    from PIL import Image
    from src.coco_evaluation import (annotation_file, split_image_path, normalize_coco,
                                     coco_detection_metrics)

    if country not in {"ecuador", "usa"}:
        raise ValueError("country must be 'ecuador' or 'usa'.")
    if not 0 <= threshold <= 1:
        raise ValueError("The AP confidence floor must be between zero and one.")
    operating_threshold = threshold if operating_threshold is None else operating_threshold
    if not threshold <= operating_threshold <= 1:
        raise ValueError("The operating threshold must be at least the AP confidence floor.")
    labels_path = annotation_file(resolve_path(data_dir), split)
    payload = json.loads(labels_path.read_text(encoding="utf-8"))
    normalize_coco(payload)
    category_id = int(payload["categories"][0]["id"])
    checkpoint_path = checkpoint or f"models/{country}/detector/rtdetrv2_s/openvino"
    # Evaluation must fail when this exact candidate is missing, without substituting weights.
    detector = PlateDetector(checkpoint=checkpoint_path, model_id=model_id, conf=threshold,
                             class_id=0, device="CPU", fallback_checkpoint=None)
    predictions = []
    fingerprint = hashlib.sha256(labels_path.read_bytes())
    for record in payload["images"]:
        image_path = split_image_path(labels_path, record["file_name"])
        image_bytes = image_path.read_bytes()
        fingerprint.update(hashlib.sha256(image_bytes).digest())
        # COCO coordinates refer to the stored pixels, without EXIF rotation or UI size limits.
        with Image.open(io.BytesIO(image_bytes)) as image_file:
            image = np.asarray(image_file.convert("RGB"))
        for detection in detector.detect(image, max_detections=300):
            x1, y1, x2, y2 = detection.box
            if x2 > x1 and y2 > y1:
                predictions.append({"image_id": int(record["id"]), "category_id": category_id,
                                    "bbox": [x1, y1, x2 - x1, y2 - y1],
                                    "score": float(detection.confidence)})
    result = coco_detection_metrics(payload, predictions, operating_threshold=operating_threshold)
    model_path = Path(detector.model_path)
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
              for p in (model_path, model_path.with_suffix(".bin"))}
    result.update(country=country, detector="RT-DETRv2-S", inference_runtime="OpenVINO Runtime",
                  checkpoint=detector.source, checkpoint_sha256=hashes,
                  split=split, threshold_for_ap=threshold,
                  split_sha256=fingerprint.hexdigest(), source_categories=len(payload["categories"]),
                  evaluated_classes=["license_plate"], dataset_scope=payload.get("info", {}).get("scope", "unspecified"))
    # Preserve keys used by existing reports.
    result.update(imagenes=result["images"], placas=result["plates"],
                  map50_95_pequenas=result["map50_95_small"],
                  map50_95_medianas=result["map50_95_medium"],
                  map50_95_grandes=result["map50_95_large"])
    output_path = result_path or f"results/metrics/detector_rtdetr_{country}_{split}.json"
    save_json(result, output_path)
    logger.info("Detector RT-DETRv2-S/OpenVINO (%s): %s", split, result)
    return result


def evaluate_end_to_end(csv_path: str, pipeline: ALPRPipeline | None = None,
                        result_path: str = "results/metrics/e2e_rtdetr.json") -> dict[str, Any]:
    """Mide EMR, CER y tiempo con un CSV que tenga ``image_path`` y ``plate_gt``."""
    pipeline = pipeline or ALPRPipeline.from_config()
    df = pd.read_csv(resolve_path(csv_path))
    if not {"image_path", "plate_gt"} <= set(df.columns):
        raise ValueError("El CSV debe tener las columnas image_path y plate_gt.")
    rows = []
    for _, row in df.iterrows():
        try:
            image = load_image(resolve_path(row["image_path"]).read_bytes())
            recognition = pipeline.recognize(image)
            rows.append({"image_path": row["image_path"], "plate_gt": normalize_plate(row["plate_gt"]),
                         "plate_pred": recognition.plate, "ocr_confidence": recognition.ocr_confidence,
                         "det_confidence": recognition.det_confidence,
                         "tiempo_ms": recognition.timings_ms.get("total")})
        except Exception as exc:  # una imagen dañada no detiene la evaluación completa
            logger.error("No se pudo evaluar %s: %s", row["image_path"], exc)
            rows.append({"image_path": row["image_path"], "plate_gt": normalize_plate(row["plate_gt"]),
                         "plate_pred": None, "ocr_confidence": 0.0, "det_confidence": 0.0,
                         "tiempo_ms": None})
    output = pd.DataFrame(rows)
    output.to_csv(resolve_path("results/metrics/e2e_rtdetr_predicciones.csv"), index=False)
    targets = load_config()["metas"]
    result = {
        "detector": pipeline.detector.name,
        "checkpoint": pipeline.detector.source,
        "n": len(output),
        "emr": exact_match_rate(output["plate_pred"], output["plate_gt"]),
        "cer": character_error_rate(output["plate_pred"], output["plate_gt"]),
        "tiempo_ms_promedio": float(output["tiempo_ms"].dropna().mean())
        if output["tiempo_ms"].notna().any() else None,
        "meta_emr": targets["emr"],
        "meta_tiempo_s": targets["tiempo_e2e_s"],
    }
    save_json(result, result_path)
    logger.info("Evaluación punta a punta RT-DETRv2: %s", result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluación RT-DETRv2 de SIRAP")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_detector = sub.add_parser("detector")
    p_detector.add_argument("--data-dir", required=True, help="Raíz de un dataset COCO Detection")
    p_detector.add_argument("--country", choices=("ecuador", "usa"), default="ecuador")
    p_detector.add_argument("--split", choices=("train", "val", "valid", "test"), default="test")
    p_detector.add_argument("--checkpoint", default=None)
    p_detector.add_argument("--model-id", default=DEFAULT_MODEL_ID)
    p_detector.add_argument("--threshold", type=float, default=0.001)
    p_detector.add_argument("--operating-threshold", type=float, default=None)
    p_e2e = sub.add_parser("e2e")
    p_e2e.add_argument("--csv", required=True)
    args = parser.parse_args()
    if args.cmd == "detector":
        evaluate_detector(args.data_dir, args.country, args.split, args.checkpoint,
                          args.model_id, args.threshold, operating_threshold=args.operating_threshold)
    else:
        evaluate_end_to_end(args.csv)


if __name__ == "__main__":
    main()
