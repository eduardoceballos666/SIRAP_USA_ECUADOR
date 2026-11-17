"""Import reviewed Ecuador COCO exports into a new, grouped experiment dataset."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import shutil
from collections import defaultdict
from pathlib import Path

import numpy as np
from PIL import Image
from src.coco_evaluation import annotation_file, audit_coco_dataset, normalize_coco, split_image_path


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _dhash(path):
    with Image.open(path) as image:
        pixels = np.asarray(image.convert("L").resize((9, 8), Image.Resampling.BILINEAR))
    return int.from_bytes(np.packbits(pixels[:, 1:] > pixels[:, :-1]).tobytes(), "big")


def write_group_review_template(root, output):
    """Create an empty human-review table; never invent vehicle/session groups."""
    root, output = Path(root), Path(output)
    if output.exists():
        raise FileExistsError(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=["image_path", "source_group"])
        writer.writeheader()
        for split in ("train", "val", "test"):
            try:
                path = annotation_file(root, split)
            except FileNotFoundError:
                continue
            for row in json.loads(path.read_text())["images"]:
                writer.writerow({"image_path": split_image_path(path, row["file_name"]).relative_to(root).as_posix(),
                                 "source_group": ""})
    return output


def prepare_ecuador_dataset(manifest_path, output_dir, *, exclude_dir=None, seed=2):
    """Require reviewed country, classes, groups and real negatives; keep test separate.

    Exact and conservative perceptual duplicates are joined before splitting.
    The six already-inspected photos may be excluded from a fresh study by hash.
    No source files or original train/validation/test splits are overwritten.
    """
    manifest_path, output_dir = Path(manifest_path).resolve(), Path(output_dir).resolve()
    if output_dir.exists():
        raise FileExistsError(f"Use a new output directory: {output_dir}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    excluded = {_sha(p) for p in Path(exclude_dir).rglob("*")
                if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}} if exclude_dir else set()
    rows, exact, provenance = [], {}, []
    for index, source in enumerate(manifest.get("sources", [])):
        if (source.get("country") != "ecuador" or source.get("country_reviewed") is not True
                or source.get("groups_reviewed") is not True or not source.get("license")
                or not source.get("source_url") or not source.get("plate_category_names")):
            raise ValueError("Every source needs reviewed Ecuador country/groups, license, URL and explicit plate classes.")
        root = Path(source["root"]).expanduser()
        root = root.resolve() if root.is_absolute() else (manifest_path.parent/root).resolve()
        groups = {}
        if source.get("groups_csv"):
            group_path = Path(source["groups_csv"])
            group_path = group_path if group_path.is_absolute() else manifest_path.parent/group_path
            for record in csv.DictReader(group_path.open(encoding="utf-8-sig")):
                if record["image_path"] in groups:
                    raise ValueError("Duplicate review-table image path.")
                groups[record["image_path"]] = record["source_group"].strip()
        allowed = {str(name).strip().casefold() for name in source["plate_category_names"]}
        count = 0
        for split in ("train", "val", "test"):
            try:
                path = annotation_file(root, split)
            except FileNotFoundError:
                continue
            payload = json.loads(path.read_text(encoding="utf-8"))
            if any(str(c["name"]).strip().casefold() not in allowed for c in payload["categories"]):
                raise ValueError("Unknown categories require human review; do not silently turn them into plates or negatives.")
            data = normalize_coco(payload)
            by_image = defaultdict(list)
            for ann in data["annotations"]:
                by_image[ann["image_id"]].append((ann["bbox"], ann["iscrowd"]))
            for row in data["images"]:
                image_path = split_image_path(path, row["file_name"])
                with Image.open(image_path) as image:
                    if image.size != (row["width"], row["height"]):
                        raise ValueError("Image dimensions differ from annotations.")
                digest = _sha(image_path)
                if digest in excluded:
                    continue
                group = groups.get(image_path.relative_to(root).as_posix(), row.get("source_group"))
                if not group or not str(group).strip():
                    raise ValueError("Every image needs a reviewed source_group (vehicle/session/scene).")
                annotations = by_image[row["id"]]
                if not annotations and source.get("negatives_reviewed") is not True:
                    raise ValueError("Unannotated images require explicit real-negative review.")
                if digest in exact:
                    previous = rows[exact[digest]]
                    if sorted(previous["annotations"]) != sorted(annotations):
                        raise ValueError("Identical images have conflicting annotations.")
                    previous["group_aliases"].add(str(group))
                    continue
                exact[digest] = len(rows)
                rows.append({"path": image_path, "sha256": digest, "width": row["width"], "height": row["height"],
                             "annotations": annotations, "group_aliases": {str(group)},
                             "dhash": _dhash(image_path), "source": index})
                count += 1
        provenance.append({k: v for k, v in source.items() if k != "root"} | {"imported_images": count})
    if not rows:
        raise ValueError("No reviewed additional images were imported.")
    parent = list(range(len(rows)))
    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    def union(a, b):
        parent[find(a)] = find(b)
    by_alias = {}
    for i, row in enumerate(rows):
        for alias in row["group_aliases"]:
            if alias in by_alias:
                union(i, by_alias[alias])
            by_alias[alias] = i
        for j in range(i):
            if (row["dhash"] ^ rows[j]["dhash"]).bit_count() <= 2:
                union(i, j)
    grouped = defaultdict(list)
    for i, row in enumerate(rows):
        grouped[find(i)].append(row)
    positives, negatives = [], []
    for key, members in grouped.items():
        (positives if any(any(not crowd for _, crowd in m["annotations"]) for m in members) else negatives).append(key)
    if len(positives) < 3:
        raise ValueError("At least three independent positive scene groups are needed for train/validation/test.")
    assignments = {}
    rng = random.Random(seed)
    for keys in (positives, negatives):
        rng.shuffle(keys)
        n = len(keys)
        val_n = max(1, round(n*.15)) if n >= 3 else 0
        test_n = max(1, round(n*.15)) if n >= 3 else 0
        for position, key in enumerate(keys):
            assignments[key] = "valid" if position < val_n else ("test" if position < val_n+test_n else "train")
    output_dir.mkdir(parents=True)
    result = {name: {"info": {"scope": "grouped_ecuador_candidate", "country": "ecuador", "seed": seed},
                     "images": [], "annotations": [], "categories": [{"id": 1, "name": "license_plate"}]}
              for name in ("train", "valid", "test")}
    for group_key, members in grouped.items():
        split = assignments[group_key]
        target = output_dir/split/"images"
        target.mkdir(parents=True, exist_ok=True)
        for row in members:
            image_id = len(result[split]["images"])+1
            filename = row["sha256"]+row["path"].suffix.lower()
            shutil.copy2(row["path"], target/filename)
            result[split]["images"].append({"id": image_id, "file_name": "images/"+filename,
                "width": row["width"], "height": row["height"], "sha256": row["sha256"],
                "source_group": f"group_{group_key}", "source_index": row["source"]})
            for box, crowd in row["annotations"]:
                result[split]["annotations"].append({"id": len(result[split]["annotations"])+1,
                    "image_id": image_id, "category_id": 1, "bbox": box,
                    "area": box[2]*box[3], "iscrowd": crowd})
    for split, payload in result.items():
        path = output_dir/split/"_annotations.coco.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    audit = audit_coco_dataset(output_dir)
    (output_dir/"provenance.json").write_text(json.dumps({"sources": provenance, "audit": audit,
        "excluded_known_images": len(excluded), "near_duplicate_dhash_distance": 2}, indent=2), encoding="utf-8")
    return output_dir


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest")
    parser.add_argument("output_dir")
    parser.add_argument("--exclude-dir")
    args = parser.parse_args()
    print(prepare_ecuador_dataset(args.manifest, args.output_dir, exclude_dir=args.exclude_dir))
