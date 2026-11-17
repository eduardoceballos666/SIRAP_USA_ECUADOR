"""Validation-only threshold diagnostics and cache provenance checks."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from src.coco_evaluation import annotation_file, coco_detection_metrics, normalize_coco, split_image_path
from src.checkpoint_verification import file_sha256


def validation_threshold_sweep(payload, predictions, *, split="val", target_precision=.95,
                               minimum_recall=.80, min_images=50, min_positives=25,
                               min_negatives=25, min_groups=5, thresholds=None,
                               max_negative_scene_fp_rate=.05):
    """Tiny development sets produce diagnostics, never an operational threshold.

    Counts are configurable experiment safeguards, not statistical certification.
    False-positive performance requires real, reviewed negative scenes.
    """
    if split not in {"val", "valid"}:
        raise ValueError("Threshold selection must use validation, never test.")
    data = normalize_coco(payload)
    annotated = {a["image_id"] for a in data["annotations"]}
    positive_ids = {a["image_id"] for a in data["annotations"] if not a["iscrowd"]}
    negative_ids = {row["id"] for row in data["images"]} - annotated
    group_values = [row.get("source_group") for row in data["images"]]
    groups = len({str(g) for g in group_values if g})
    settings = list(thresholds) if thresholds is not None else [i/100 for i in range(5, 100, 5)]
    if not settings or any(not 0 <= x <= 1 for x in settings):
        raise ValueError("Provide confidence thresholds between zero and one.")
    rows = []
    for threshold in settings:
        metrics = coco_detection_metrics(payload, predictions, operating_threshold=threshold)
        row = {key: metrics[key] for key in
               ("operating_threshold", "tp", "fp", "fn", "precision", "recall", "f1")}
        fp_scenes = len({p["image_id"] for p in predictions
                         if p["image_id"] in negative_ids and p["score"] >= threshold})
        row.update(fp_negative_images=fp_scenes,
                   negative_scene_fp_rate=fp_scenes/len(negative_ids) if negative_ids else None)
        rows.append(row)
    eligible = [r for r in rows if r["tp"] > 0 and r["precision"] >= target_precision
                and r["recall"] is not None and r["recall"] >= minimum_recall
                and r["negative_scene_fp_rate"] is not None
                and r["negative_scene_fp_rate"] <= max_negative_scene_fp_rate]
    selected = max(eligible, key=lambda r: (r["recall"], r["precision"], r["operating_threshold"])) if eligible else None
    reasons = []
    if len(data["images"]) < min_images: reasons.append("insufficient validation images")
    if len(positive_ids) < min_positives: reasons.append("insufficient positive validation images")
    if len(negative_ids) < min_negatives: reasons.append("insufficient real negative validation images")
    if groups < min_groups or not all(group_values): reasons.append("insufficient documented validation scene groups")
    if payload.get("info", {}).get("scope") in {"development_only", "six_photo_development"}:
        reasons.append("the dataset is explicitly a small development set")
    if selected is None: reasons.append("no threshold meets the precision and recall targets")
    return {"country": "ecuador", "selection_split": "val", "usable_for_inference": not reasons,
            "threshold": selected["operating_threshold"] if not reasons else None,
            "diagnostic_candidate_threshold": selected["operating_threshold"] if selected else None,
            "reasons": reasons, "images": len(data["images"]), "positive_images": len(positive_ids),
            "negative_images": len(negative_ids), "source_groups": groups, "thresholds": rows,
            "policy": {"target_precision": target_precision, "minimum_recall": minimum_recall,
                       "min_images": min_images, "min_positives": min_positives,
                       "min_negatives": min_negatives, "min_groups": min_groups,
                       "max_negative_scene_fp_rate": max_negative_scene_fp_rate},
            "field_acceptance_demonstrated": False}


def calibrate_from_validation_cache(data_dir, checkpoint, prediction_cache, **policy):
    """Reject caches from other images, model/runtime bytes, or test evaluations."""
    cache = json.loads(Path(prediction_cache).read_text(encoding="utf-8"))
    if cache.get("split") not in {"val", "valid"}:
        raise ValueError("The prediction cache must come from validation.")
    requested = policy.get("thresholds") or [.05]
    floor = cache.get("score_floor")
    if not isinstance(floor, (float, int)) or not 0 <= floor <= min(requested):
        raise ValueError("The score floor must cover every calibration threshold.")
    path = annotation_file(data_dir, "val")
    annotation_bytes = path.read_bytes()
    if cache.get("annotation_sha256") != hashlib.sha256(annotation_bytes).hexdigest():
        raise ValueError("Cached predictions belong to other annotations.")
    payload = json.loads(annotation_bytes)
    digest = hashlib.sha256(annotation_bytes)
    for row in payload["images"]:
        digest.update(bytes.fromhex(file_sha256(split_image_path(path, row["file_name"]))))
    if cache.get("split_sha256") != digest.hexdigest():
        raise ValueError("Validation images changed after inference.")
    hashes = {name: file_sha256(Path(checkpoint)/name)
              for name in ("openvino_model.xml", "openvino_model.bin", "sirap_openvino.json")}
    if cache.get("checkpoint_sha256") != hashes:
        raise ValueError("Cached predictions belong to different model/runtime bytes.")
    report = validation_threshold_sweep(payload, cache["predictions"], **policy)
    report.update(checkpoint_sha256=hashes, split_sha256=digest.hexdigest(),
                  prediction_cache_sha256=file_sha256(prediction_cache))
    return report
