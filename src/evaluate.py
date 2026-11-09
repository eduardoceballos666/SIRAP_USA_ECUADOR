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
                      result_path: str | Path | None = None) -> dict[str, Any]:
    """Calcula mAP COCO, AP50, AP75, precisión y recall en un split COCO."""
    from pycocotools.coco import COCO
    from pycocotools.cocoeval import COCOeval

    if country not in {"ecuador", "usa"}:
        raise ValueError("country debe ser 'ecuador' o 'usa'.")
    dataset = CocoPlateDataset(data_dir, split, image_processor=None)
    coco_gt = COCO(str(dataset.annotation_path))
    categories = coco_gt.dataset.get("categories", [])
    if not categories:
        raise ValueError(f"El JSON COCO no define categorías: {dataset.annotation_path}")
    category_id = int(categories[0]["id"])
    source_category_count = len(categories)
    # SIRAP entrena un detector de una clase; unifica etiquetas equivalentes de placas.
    for annotation in coco_gt.dataset.get("annotations", []):
        annotation["category_id"] = category_id
    coco_gt.dataset["categories"] = [{
        "id": category_id,
        "name": "license_plate",
        "supercategory": "license_plate",
    }]
    coco_gt.createIndex()
    checkpoint_path = checkpoint or f"models/{country}/detector/rtdetrv2_s/openvino"
    detector = PlateDetector(checkpoint=checkpoint_path, model_id=model_id,
                             conf=threshold, class_id=0, device="CPU")
    predictions = []
    for record in dataset.images:
        image_path = dataset._image_path(record["file_name"])
        image = np.asarray(load_image(image_path.read_bytes()))
        for detection in detector.detect(image, max_detections=300):
            x1, y1, x2, y2 = detection.box
            predictions.append({
                "image_id": int(record["id"]),
                "category_id": category_id,
                "bbox": [x1, y1, max(0.0, x2 - x1), max(0.0, y2 - y1)],
                "score": detection.confidence,
            })

    result: dict[str, Any] = {
        "country": country,
        "detector": "RT-DETRv2-S",
        "inference_runtime": "OpenVINO Runtime",
        "checkpoint": detector.source,
        "source_categories": source_category_count,
        "evaluated_classes": ["license_plate"],
        "split": split,
        "images": len(dataset),
        "imagenes": len(dataset),
        "plates": sum(len(items) for items in dataset.annotations_by_image.values()),
        "placas": sum(len(items) for items in dataset.annotations_by_image.values()),
        "predictions": len(predictions),
        "threshold_for_ap": threshold,
        "map50_95": None,
        "map50": None,
        "map75": None,
        "precision": None,
        "recall": None,
        "f1": None,
    }
    if predictions:
        coco_dt = coco_gt.loadRes(predictions)
        evaluator = COCOeval(coco_gt, coco_dt, "bbox")
        evaluator.params.imgIds = [int(image["id"]) for image in dataset.images]
        evaluator.params.catIds = [category_id]
        evaluator.evaluate()
        evaluator.accumulate()
        evaluator.summarize()
        precision_values = evaluator.eval["precision"][0, :, :, 0, -1]
        recall_values = evaluator.eval["recall"][0, :, 0, -1]
        valid_precision = precision_values[precision_values > -1]
        valid_recall = recall_values[recall_values > -1]
        precision = float(valid_precision.mean()) if valid_precision.size else 0.0
        recall = float(valid_recall.mean()) if valid_recall.size else 0.0
        stats = evaluator.stats
        result.update({
            "map50_95": float(stats[0]), "map50": float(stats[1]), "map75": float(stats[2]),
            "map50_95_small": float(stats[3]), "map50_95_medium": float(stats[4]),
            "map50_95_large": float(stats[5]), "precision": precision, "recall": recall,
            "f1": f1_score(precision, recall),
            "map50_95_pequenas": float(stats[3]), "map50_95_medianas": float(stats[4]),
            "map50_95_grandes": float(stats[5]),
        })
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
    p_detector.add_argument("--split", choices=("train", "val", "test"), default="test")
    p_detector.add_argument("--checkpoint", default=None)
    p_detector.add_argument("--model-id", default=DEFAULT_MODEL_ID)
    p_detector.add_argument("--threshold", type=float, default=0.001)
    p_e2e = sub.add_parser("e2e")
    p_e2e.add_argument("--csv", required=True)
    args = parser.parse_args()
    if args.cmd == "detector":
        evaluate_detector(args.data_dir, args.country, args.split, args.checkpoint,
                          args.model_id, args.threshold)
    else:
        evaluate_end_to_end(args.csv)


if __name__ == "__main__":
    main()
