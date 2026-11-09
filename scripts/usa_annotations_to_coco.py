"""Build COCO Detection splits for full-scene US license-plate images.

Input CSV columns:
image_file,split,source_group,x,y,width,height

Coordinates use COCO pixel xywh. A negative image has one row with all four
coordinates empty. Multiple positive plates in one image use multiple rows.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from collections import defaultdict
from pathlib import Path, PurePosixPath
from typing import Any

from PIL import Image

SPLITS = ("train", "valid", "test")
REQUIRED_COLUMNS = {
    "image_file", "split", "source_group", "x", "y", "width", "height"
}
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}


def _safe_relative_path(value: str) -> Path:
    path = Path(value.strip())
    if not value.strip():
        raise ValueError("image_file está vacío.")
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"image_file debe ser relativo y no puede subir de carpeta: {value!r}")
    if path.suffix.lower() not in IMAGE_SUFFIXES:
        raise ValueError(f"Formato de imagen no admitido en {value!r}.")
    return path


def _read_bbox(row: dict[str, str], image_file: str) -> tuple[float, float, float, float] | None:
    values = [str(row.get(key, "") or "").strip() for key in ("x", "y", "width", "height")]
    if all(value == "" for value in values):
        return None
    if any(value == "" for value in values):
        raise ValueError(f"La caja de {image_file!r} debe tener x, y, width y height.")
    try:
        x, y, width, height = map(float, values)
    except ValueError as exc:
        raise ValueError(f"Coordenadas no numéricas en {image_file!r}: {values}") from exc
    if width <= 0 or height <= 0 or x < 0 or y < 0:
        raise ValueError(f"Caja no válida para {image_file!r}: {values}")
    return x, y, width, height


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def convert_annotations(
    images_dir: str | Path,
    annotations_csv: str | Path,
    output_dir: str | Path,
    *,
    verify_hashes: bool = True,
) -> dict[str, dict[str, int]]:
    """Validate labels, copy images, and write train/valid/test COCO JSON files."""
    image_root = Path(images_dir).expanduser().resolve()
    csv_path = Path(annotations_csv).expanduser().resolve()
    output_root = Path(output_dir).expanduser().resolve()
    if not image_root.is_dir():
        raise FileNotFoundError(f"No existe la carpeta de imágenes: {image_root}")
    if not csv_path.is_file():
        raise FileNotFoundError(f"No existe el CSV de anotaciones: {csv_path}")

    records: dict[str, dict[str, Any]] = {}
    group_splits: dict[str, str] = {}
    split_files: dict[str, set[str]] = {split: set() for split in SPLITS}

    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        columns = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - columns
        if missing:
            raise ValueError(f"Faltan columnas en el CSV: {', '.join(sorted(missing))}")

        for line_number, row in enumerate(reader, start=2):
            image_rel = _safe_relative_path(str(row.get("image_file", "")))
            image_key = image_rel.as_posix()
            split = str(row.get("split", "") or "").strip().lower()
            if split == "val":
                split = "valid"
            if split not in SPLITS:
                raise ValueError(f"Línea {line_number}: split debe ser train, valid o test.")
            group = str(row.get("source_group", "") or "").strip()
            if not group:
                raise ValueError(
                    f"Línea {line_number}: completa source_group para evitar mezclar "
                    "imágenes de la misma secuencia o vehículo entre splits."
                )

            previous_split = group_splits.setdefault(group, split)
            if previous_split != split:
                raise ValueError(
                    f"El grupo {group!r} aparece en {previous_split} y {split}. "
                    "Mantén cada secuencia/cámara/vehículo en un solo split."
                )

            source_path = (image_root / image_rel).resolve()
            try:
                source_path.relative_to(image_root)
            except ValueError as exc:
                raise ValueError(f"Ruta de imagen fuera de source_images: {image_rel}") from exc
            if not source_path.is_file():
                raise FileNotFoundError(f"Línea {line_number}: no existe {source_path}")

            bbox = _read_bbox(row, image_key)
            try:
                with Image.open(source_path) as image:
                    width, height = image.size
                    image.verify()
            except Exception as exc:
                raise ValueError(f"Imagen ilegible en línea {line_number}: {source_path}") from exc

            record = records.get(image_key)
            if record is None:
                record = {
                    "image_rel": image_rel,
                    "source_path": source_path,
                    "split": split,
                    "group": group,
                    "width": int(width),
                    "height": int(height),
                    "annotations": [],
                    "negative_rows": 0,
                }
                records[image_key] = record
                split_files[split].add(image_key)
            else:
                if record["split"] != split or record["group"] != group:
                    raise ValueError(
                        f"{image_key} está repetida con distintos split o source_group."
                    )
                if record["width"] != width or record["height"] != height:
                    raise ValueError(f"Dimensiones inconsistentes para {image_key}.")

            if bbox is None:
                record["negative_rows"] += 1
                continue

            x, y, box_width, box_height = bbox
            if x + box_width > width + 1e-3 or y + box_height > height + 1e-3:
                raise ValueError(
                    f"Caja fuera de la imagen {image_key}: {bbox}; tamaño {width}x{height}."
                )
            record["annotations"].append(bbox)

    if not records:
        raise ValueError("El CSV no contiene filas de anotación.")
    missing_splits = [split for split in SPLITS if not split_files[split]]
    if missing_splits:
        raise ValueError(
            "Cada partición debe tener imágenes. Faltan: " + ", ".join(missing_splits)
        )

    for image_key, record in records.items():
        if record["negative_rows"] > 1:
            raise ValueError(f"La imagen negativa {image_key} aparece más de una vez sin caja.")
        if record["negative_rows"] and record["annotations"]:
            raise ValueError(
                f"{image_key} mezcla una fila negativa y cajas positivas; elimina la fila vacía."
            )

    if verify_hashes:
        hash_splits: dict[str, tuple[str, str]] = {}
        for image_key, record in records.items():
            digest = _sha256(record["source_path"])
            previous = hash_splits.get(digest)
            if previous and previous[1] != record["split"]:
                raise ValueError(
                    f"Imagen duplicada entre splits: {previous[0]} ({previous[1]}) "
                    f"y {image_key} ({record['split']})."
                )
            hash_splits[digest] = (image_key, record["split"])

    summary: dict[str, dict[str, int]] = {}
    for split in SPLITS:
        image_keys = sorted(split_files[split])
        images, annotations = [], []
        split_root = output_root / split
        target_image_root = split_root / "images"
        target_image_root.mkdir(parents=True, exist_ok=True)
        annotation_id = 1

        for image_id, image_key in enumerate(image_keys, start=1):
            record = records[image_key]
            relative_name = PurePosixPath("images") / PurePosixPath(record["image_rel"].as_posix())
            target_path = split_root.joinpath(*relative_name.parts)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            if record["source_path"] != target_path.resolve():
                shutil.copy2(record["source_path"], target_path)

            images.append({
                "id": image_id,
                "file_name": relative_name.as_posix(),
                "width": record["width"],
                "height": record["height"],
            })
            for x, y, width, height in record["annotations"]:
                annotations.append({
                    "id": annotation_id,
                    "image_id": image_id,
                    "category_id": 1,
                    "bbox": [x, y, width, height],
                    "area": width * height,
                    "iscrowd": 0,
                })
                annotation_id += 1

        payload = {
            "info": {
                "description": "SIRAP USA full-scene license-plate detection",
                "format": "COCO Detection",
            },
            "licenses": [],
            "images": images,
            "annotations": annotations,
            "categories": [
                {"id": 1, "name": "license_plate", "supercategory": "vehicle"}
            ],
        }
        (split_root / "_annotations.coco.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        summary[split] = {
            "images": len(images),
            "positive_images": sum(bool(records[key]["annotations"]) for key in image_keys),
            "negative_images": sum(not records[key]["annotations"] for key in image_keys),
            "boxes": len(annotations),
            "groups": len({records[key]["group"] for key in image_keys}),
        }

    manifest = {
        "dataset": "SIRAP USA license-plate detection",
        "format": "COCO Detection",
        "category": "license_plate",
        "coordinate_format": "pixel xywh",
        "source_csv": csv_path.name,
        "splits": summary,
    }
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "dataset_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Valida anotaciones de escenas USA y genera COCO train/valid/test."
    )
    parser.add_argument("--images-dir", required=True, help="Carpeta con escenas completas.")
    parser.add_argument("--annotations-csv", required=True, help="CSV basado en la plantilla COCO USA.")
    parser.add_argument("--output-dir", required=True, help="Raíz para train, valid y test.")
    parser.add_argument(
        "--skip-hash-check",
        action="store_true",
        help="Omite la comprobación de imágenes idénticas entre particiones.",
    )
    args = parser.parse_args()
    result = convert_annotations(
        args.images_dir,
        args.annotations_csv,
        args.output_dir,
        verify_hashes=not args.skip_hash_check,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
