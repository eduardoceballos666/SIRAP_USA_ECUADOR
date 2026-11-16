"""COCO dataset checks and detection metrics without a training runtime.

AP uses COCO's standard IoU .50:.95 and maximum 100 detections per image.
Precision, recall and F1 use actual matches at a fixed confidence and IoU.
"""
from __future__ import annotations

import contextlib
import copy
import hashlib
import io
import json
import math
from pathlib import Path

import numpy as np


def _integer(value, label):
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{label} must be an integer.")
    return value


def normalize_coco(payload):
    """Validate detection labels and merge declared plate categories into class 1."""
    data = copy.deepcopy(payload)
    for field in ("images", "annotations", "categories"):
        if not isinstance(data.get(field), list):
            raise ValueError(f"COCO requires a {field} list.")
    if not data["images"] or not data["categories"]:
        raise ValueError("COCO requires at least one image and category.")
    category_ids = [_integer(c["id"], "category id") for c in data["categories"]]
    if len(set(category_ids)) != len(category_ids):
        raise ValueError("Duplicate category ids.")
    images = {}
    for row in data["images"]:
        image_id = _integer(row["id"], "image id")
        if image_id in images:
            raise ValueError("Duplicate image ids.")
        for field in ("width", "height"):
            if _integer(row[field], field) <= 0:
                raise ValueError("Image dimensions must be positive.")
        if not isinstance(row.get("file_name"), str) or not row["file_name"]:
            raise ValueError("An image file_name is required.")
        images[image_id] = row
    annotation_ids = set()
    for index, ann in enumerate(data["annotations"], 1):
        old_id = _integer(ann["id"], "annotation id")
        if old_id in annotation_ids:
            raise ValueError("Duplicate annotation ids.")
        annotation_ids.add(old_id)
        image = images.get(_integer(ann["image_id"], "annotation image_id"))
        if image is None:
            raise ValueError("Annotation references an unknown image.")
        if ann["category_id"] not in category_ids:
            raise ValueError("Annotation references an unknown category.")
        if not isinstance(ann.get("bbox"), (list, tuple)) or len(ann["bbox"]) != 4:
            raise ValueError("bbox must contain x, y, width, height.")
        x, y, w, h = map(float, ann["bbox"])
        if (not all(math.isfinite(v) for v in (x, y, w, h)) or min(x, y) < 0
                or min(w, h) <= 0 or x + w > image["width"] + 1e-6
                or y + h > image["height"] + 1e-6):
            raise ValueError(f"Invalid or out-of-bounds box: {old_id}.")
        area = float(ann.get("area", w * h))
        if not math.isfinite(area) or area <= 0:
            raise ValueError("Annotation area must be positive and finite.")
        crowd = ann.get("iscrowd", 0)
        if crowd not in (0, 1):
            raise ValueError("iscrowd must be zero or one.")
        # COCO uses zero as its unmatched sentinel. Source id 0 must be remapped.
        ann.update(id=index, category_id=1, bbox=[x, y, w, h], area=area, iscrowd=int(crowd))
    data["categories"] = [{"id": 1, "name": "license_plate", "supercategory": "license_plate"}]
    data.setdefault("info", {})
    return data


def annotation_file(root, split):
    root = Path(root)
    aliases = ("valid", "val") if split in ("valid", "val") else (split,)
    for alias in aliases:
        for name in ("_annotations.coco.json", "annotations.json", f"instances_{split}.json"):
            candidate = root / alias / name
            if candidate.is_file():
                return candidate
    raise FileNotFoundError(f"Missing COCO labels for {split}: {root}/{aliases[0]}/_annotations.coco.json")


def split_image_path(annotation_path, file_name):
    """Resolve only inside this split; never search another split by basename."""
    split_root = Path(annotation_path).parent.resolve()
    relative = Path(file_name)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"Image path must be relative to its split: {file_name}")
    candidate = (split_root / relative).resolve()
    if not candidate.is_relative_to(split_root):
        raise ValueError(f"Image escapes its split: {file_name}")
    if not candidate.is_file():
        raise FileNotFoundError(f"Missing image in this split: {candidate}")
    return candidate


def audit_coco_dataset(root, required_splits=("train", "val", "test")):
    """Check labels, image dimensions, hashes and scene groups across splits."""
    from PIL import Image

    seen_hashes, seen_groups, summary, fingerprint = {}, {}, [], hashlib.sha256()
    for split in required_splits:
        path = annotation_file(root, split)
        original = json.loads(path.read_text(encoding="utf-8"))
        data = normalize_coco(original)
        fingerprint.update(split.encode())
        fingerprint.update(json.dumps(data, sort_keys=True, separators=(",", ":")).encode())
        for row in data["images"]:
            image_path = split_image_path(path, row["file_name"])
            with Image.open(image_path) as image:
                image.load()
                if image.size != (row["width"], row["height"]):
                    raise ValueError(f"Incorrect image dimensions: {image_path}")
            digest = hashlib.sha256(image_path.read_bytes()).hexdigest()
            if digest in seen_hashes:
                raise ValueError(f"Duplicate image content in {seen_hashes[digest]} and {split}.")
            seen_hashes[digest] = split
            if row.get("sha256") and row["sha256"] != digest:
                raise ValueError(f"Image checksum mismatch: {image_path}")
            fingerprint.update(digest.encode())
            for key in ("source_group", "vehicle_id", "clip_id", "session_id"):
                if row.get(key) is not None:
                    group = (key, str(row[key]))
                    if group in seen_groups and seen_groups[group] != split:
                        raise ValueError(f"Group {key} shared between {seen_groups[group]} and {split}.")
                    seen_groups[group] = split
        positives = {a["image_id"] for a in data["annotations"] if not a["iscrowd"]}
        if split in ("train", "valid", "val") and not positives:
            raise ValueError(f"{split} needs at least one non-crowd annotated plate.")
        summary.append({"split": split, "images": len(data["images"]),
                        "plates": len(data["annotations"]),
                        "negative_images": len(data["images"]) - len({a["image_id"] for a in data["annotations"]})})
    return {"splits": summary, "dataset_sha256": fingerprint.hexdigest(),
            "class": "license_plate", "status": "ready"}


def coco_detection_metrics(payload, predictions, operating_threshold=0.70, iou_threshold=0.50):
    """Evaluate AP and threshold-specific counts, including empty predictions."""
    from pycocotools.coco import COCO
    from pycocotools.cocoeval import COCOeval

    if not 0 <= operating_threshold <= 1 or not 0 < iou_threshold <= 1:
        raise ValueError("Invalid confidence or IoU threshold.")
    source_categories = {c["id"] for c in payload["categories"]}
    data = normalize_coco(payload)
    image_ids = {row["id"] for row in data["images"]}
    detections = []
    for row in predictions:
        if row["image_id"] not in image_ids or row["category_id"] not in source_categories:
            raise ValueError("Prediction references an unknown image or category.")
        box = list(map(float, row["bbox"]))
        score = float(row["score"])
        if (len(box) != 4 or not all(math.isfinite(v) for v in (*box, score))
                or min(box[2:]) <= 0 or not 0 <= score <= 1):
            raise ValueError("Invalid predicted box or confidence.")
        detections.append({"image_id": row["image_id"], "category_id": 1, "bbox": box, "score": score})

    def detection_coco(rows):
        if rows:
            return ground_truth.loadRes(rows)
        empty = COCO()
        empty.dataset = {"info": {}, "images": copy.deepcopy(data["images"]),
                         "categories": copy.deepcopy(data["categories"]), "annotations": []}
        empty.createIndex()
        return empty

    with contextlib.redirect_stdout(io.StringIO()):
        ground_truth = COCO()
        ground_truth.dataset = data
        ground_truth.createIndex()
        evaluator = COCOeval(ground_truth, detection_coco(detections), "bbox")
        evaluator.params.imgIds = sorted(image_ids)
        evaluator.params.catIds = [1]
        evaluator.evaluate()
        evaluator.accumulate()
        evaluator.summarize()
        stats = evaluator.stats.copy()
        selected = [row for row in detections if row["score"] >= operating_threshold]
        operating = COCOeval(ground_truth, detection_coco(selected), "bbox")
        operating.params.imgIds = sorted(image_ids)
        operating.params.catIds = [1]
        operating.params.iouThrs = np.array([iou_threshold])
        operating.evaluate()
    tp = fp = fn = ignored = 0
    for entry in operating.evalImgs:
        if entry is None or list(entry["aRng"]) != list(operating.params.areaRng[0]):
            continue
        matched = np.asarray(entry["dtMatches"][0]) > 0
        dt_ignore = np.asarray(entry["dtIgnore"][0], dtype=bool)
        gt_ignore = np.asarray(entry["gtIgnore"], dtype=bool)
        tp += int(np.sum(matched & ~dt_ignore))
        fp += int(np.sum(~matched & ~dt_ignore))
        fn += int(np.sum((np.asarray(entry["gtMatches"][0]) == 0) & ~gt_ignore))
        ignored += int(np.sum(dt_ignore))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else None
    f1 = 2 * precision * recall / (precision + recall) if recall is not None and precision + recall else 0.0
    names = ("map50_95", "map50", "map75", "map50_95_small", "map50_95_medium", "map50_95_large")
    result = {name: float(stats[i]) if stats[i] >= 0 else None for i, name in enumerate(names)}
    result.update(images=len(data["images"]), plates=len(data["annotations"]), predictions=len(detections),
                  tp=tp, fp=fp, fn=fn, ignored_predictions=ignored, precision=precision, recall=recall, f1=f1,
                  operating_threshold=float(operating_threshold), operating_iou=float(iou_threshold),
                  max_detections_per_image=100,
                  metric_note="AP uses all supplied scores; P/R/F1 use matches at the stated confidence and IoU. "
                              "Undefined AP/recall are null; precision with no predictions is zero.")
    return result
