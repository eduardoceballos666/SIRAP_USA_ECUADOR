"""Ajuste fino de RT-DETRv2 R18 con Transformers para los perfiles Ecuador y USA.

Entrena desde el checkpoint Apache-2.0 de matrículas ``merve/license-plates-rtdetrv2``.
Los datasets se leen en COCO Detection; ``convert-yolo`` permite convertir un dataset
local YOLO antiguo sin instalar ni usar Ultralytics.

Ejemplos::

    python -m src.train --country ecuador --data-dir /content/license-plates-coco
    python -m src.train --country usa --data-dir /content/us-plates-coco --epochs 30
    python -m src.train --country ecuador --roboflow
    python -m src.train --convert-yolo --data-yaml /content/dataset/data.yaml --output-dir /content/dataset-coco
"""

from __future__ import annotations

import argparse
import json
import shutil
from collections import defaultdict
from pathlib import Path
from typing import Any

from PIL import Image

from src.utils import get_logger, get_secret, resolve_path, save_json

logger = get_logger("sirap.train")
DEFAULT_MODEL_ID = "merve/license-plates-rtdetrv2"
BASE_MODEL_ID = "PekingU/rtdetr_v2_r18vd"
RF_WORKSPACE = "roboflow-universe-projects"
RF_PROJECT = "license-plate-recognition-rxg4e"
RF_VERSION = 11


def _annotation_file(data_dir: str | Path, split: str) -> Path:
    """Encuentra el JSON COCO de un split exportado por Roboflow."""
    root = resolve_path(data_dir)
    names = ("_annotations.coco.json", "annotations.json", f"instances_{split}.json")
    split_names = ("valid", "val") if split == "val" else (split,)
    for split_name in split_names:
        folder = root / split_name
        for name in names:
            candidate = folder / name
            if candidate.is_file():
                return candidate
    raise FileNotFoundError(
        f"No se encontró el JSON COCO de {split!r} bajo {root}. "
        "Se espera <dataset>/<train|valid|test>/_annotations.coco.json."
    )


def download_roboflow_dataset(target_dir: str | Path = "data/raw", api_key: str | None = None) -> Path:
    """Descarga la versión de Roboflow como COCO Detection y devuelve la carpeta."""
    key = api_key or get_secret("ROBOFLOW_API_KEY")
    if not key:
        raise RuntimeError("Falta ROBOFLOW_API_KEY en el entorno o en Secrets de Colab.")
    from roboflow import Roboflow  # importación diferida: solo se necesita al descargar

    location = resolve_path(target_dir) / f"{RF_PROJECT}-v{RF_VERSION}-coco"
    if location.exists():
        logger.info("Se usará el dataset ya descargado: %s", location)
        return location
    project = Roboflow(api_key=key).workspace(RF_WORKSPACE).project(RF_PROJECT)
    project.version(RF_VERSION).download("coco", location=str(location))
    return location


class CocoPlateDataset:
    """Dataset PyTorch que convierte anotaciones COCO a la entrada de RT-DETRv2."""

    def __init__(self, data_dir: str | Path, split: str, image_processor: Any):
        import json

        self.annotation_path = _annotation_file(data_dir, split)
        self.image_processor = image_processor
        self.image_root = self.annotation_path.parent
        self.data_root = resolve_path(data_dir)
        payload = json.loads(self.annotation_path.read_text(encoding="utf-8"))
        self.images = payload.get("images", [])
        self.annotations_by_image: dict[int, list[dict[str, Any]]] = defaultdict(list)
        for annotation in payload.get("annotations", []):
            self.annotations_by_image[int(annotation["image_id"])].append(annotation)
        self.category_ids = [int(category["id"]) for category in payload.get("categories", [])]
        if not self.category_ids:
            self.category_ids = sorted({int(a["category_id"]) for a in payload.get("annotations", [])})
        if not self.images:
            raise ValueError(f"El COCO no contiene imágenes: {self.annotation_path}")

    def __len__(self) -> int:
        return len(self.images)

    def _image_path(self, filename: str) -> Path:
        candidates = (self.image_root / filename, self.data_root / filename,
                      self.image_root / Path(filename).name)
        for candidate in candidates:
            if candidate.is_file():
                return candidate
        matches = list(self.data_root.rglob(Path(filename).name))
        if matches:
            return matches[0]
        raise FileNotFoundError(f"No se encontró la imagen COCO: {filename}")

    def __getitem__(self, index: int) -> dict[str, Any]:
        record = self.images[index]
        image_id = int(record["id"])
        image = Image.open(self._image_path(record["file_name"])).convert("RGB")
        annotations = []
        for source in self.annotations_by_image.get(image_id, []):
            x, y, width, height = (float(value) for value in source["bbox"])
            if width <= 0 or height <= 0:
                continue
            annotations.append({
                "image_id": image_id,
                "category_id": 0,
                "bbox": [x, y, width, height],
                "area": float(source.get("area", width * height)),
                "iscrowd": int(source.get("iscrowd", 0)),
            })
        return {"image": image, "image_id": image_id, "annotations": annotations}


def detection_collator(batch: list[dict[str, Any]], image_processor: Any) -> dict[str, Any]:
    """Procesa imágenes COCO de tamaño variable y conserva las etiquetas por imagen."""
    encoded = image_processor(
        images=[item["image"] for item in batch],
        annotations=[{"image_id": item["image_id"], "annotations": item["annotations"]}
                     for item in batch],
        return_tensors="pt",
    )
    return encoded


def convert_yolo_to_coco(data_yaml: str | Path, output_dir: str | Path) -> Path:
    """Convierte splits de etiquetas YOLO normalizadas a COCO Detection.

    Copia imágenes y crea ``_annotations.coco.json`` en ``train/``, ``valid/`` y
    ``test/``. Solo admite cajas rectangulares; los polígonos de segmentación se ignoran.
    """
    import yaml

    source_yaml = resolve_path(data_yaml)
    config = yaml.safe_load(source_yaml.read_text(encoding="utf-8"))
    output_root = resolve_path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)
    base = source_yaml.parent
    names = config.get("names", {0: "license_plate"})
    category_name = next(iter(names.values())) if isinstance(names, dict) else names[0]
    for split, aliases in (("train", ("train",)), ("valid", ("valid", "val")), ("test", ("test",))):
        image_spec = next((config.get(key) for key in aliases if config.get(key)), None)
        if not image_spec:
            continue
        image_dir = Path(image_spec)
        if not image_dir.is_absolute():
            image_dir = base / image_dir
        if image_dir.name.lower() != "images" and (image_dir / "images").is_dir():
            image_dir = image_dir / "images"
        label_dir = image_dir.parent / "labels" if image_dir.name.lower() == "images" else image_dir.parent / "labels"
        target_dir = output_root / ("valid" if split == "valid" else split)
        target_images = target_dir / "images"
        target_images.mkdir(parents=True, exist_ok=True)
        coco_images, coco_annotations = [], []
        annotation_id = 1
        for image_id, image_path in enumerate(sorted(p for p in image_dir.rglob("*")
                                                     if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}), 1):
            target = target_images / image_path.name
            if image_path.resolve() != target.resolve():
                shutil.copy2(image_path, target)
            with Image.open(image_path) as image:
                width, height = image.size
            coco_images.append({"id": image_id, "file_name": f"images/{target.name}",
                                "width": width, "height": height})
            label_path = label_dir / f"{image_path.stem}.txt"
            if not label_path.is_file():
                continue
            for line in label_path.read_text(encoding="utf-8").splitlines():
                values = line.split()
                if len(values) < 5:
                    continue
                _, cx, cy, box_w, box_h = values[:5]
                cx, cy, box_w, box_h = (float(value) for value in (cx, cy, box_w, box_h))
                x, y = (cx - box_w / 2) * width, (cy - box_h / 2) * height
                box_w, box_h = box_w * width, box_h * height
                coco_annotations.append({"id": annotation_id, "image_id": image_id, "category_id": 1,
                                         "bbox": [x, y, box_w, box_h], "area": box_w * box_h, "iscrowd": 0})
                annotation_id += 1
        payload = {"images": coco_images, "annotations": coco_annotations,
                   "categories": [{"id": 1, "name": str(category_name), "supercategory": "vehicle"}]}
        (target_dir / "_annotations.coco.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
        logger.info("COCO %s: %s imágenes, %s cajas", split, len(coco_images), len(coco_annotations))
    return output_root


def train_detector(data_dir: str | Path, country: str = "ecuador", model_id: str = DEFAULT_MODEL_ID,
                   output_dir: str | Path | None = None, run_dir: str | Path | None = None,
                   epochs: int = 30, batch_size: int = 8, learning_rate: float = 5e-5,
                   weight_decay: float = 1e-4, seed: int = 42, force: bool = False) -> Path:
    """Ajusta RT-DETRv2 R18 con Transformers y guarda el mejor checkpoint Safetensors."""
    import torch
    from transformers import (AutoImageProcessor, EarlyStoppingCallback, RTDetrV2ForObjectDetection,
                              Trainer, TrainingArguments)

    if country not in {"ecuador", "usa"}:
        raise ValueError("country debe ser 'ecuador' o 'usa'.")
    final_dir = resolve_path(output_dir or f"models/{country}/detector/rtdetr_r18")
    train_dir = resolve_path(run_dir or f"results/runs/{country}/rtdetr_r18")
    if final_dir.exists() and (final_dir / "config.json").exists() and not force:
        logger.info("Ya existe %s; usa --force para volver a entrenar.", final_dir)
        return final_dir
    if force and train_dir.exists():
        shutil.rmtree(train_dir)
    train_dir.mkdir(parents=True, exist_ok=True)
    final_dir.mkdir(parents=True, exist_ok=True)

    torch.manual_seed(seed)
    processor = AutoImageProcessor.from_pretrained(model_id, trust_remote_code=False, use_fast=False)
    train_data = CocoPlateDataset(data_dir, "train", processor)
    val_data = CocoPlateDataset(data_dir, "val", processor)
    model = RTDetrV2ForObjectDetection.from_pretrained(model_id, trust_remote_code=False)
    model.config.id2label = {0: "license_plate"}
    model.config.label2id = {"license_plate": 0}

    args = TrainingArguments(
        output_dir=str(train_dir),
        num_train_epochs=epochs,
        learning_rate=learning_rate,
        weight_decay=weight_decay,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        eval_strategy="epoch",
        save_strategy="epoch",
        save_total_limit=2,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        warmup_ratio=0.05,
        dataloader_num_workers=2,
        remove_unused_columns=False,
        fp16=torch.cuda.is_available(),
        seed=seed,
        data_seed=seed,
        report_to="none",
        logging_steps=25,
        save_safetensors=True,
    )
    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=train_data,
        eval_dataset=val_data,
        data_collator=lambda rows: detection_collator(rows, processor),
        processing_class=processor,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=5)],
    )
    trainer.train()
    trainer.save_model(str(final_dir))
    processor.save_pretrained(str(final_dir))
    manifest = {
        "architecture": "RT-DETRv2 R18",
        "library": "Transformers",
        "base_checkpoint": model_id,
        "base_license": "Apache-2.0",
        "country": country,
        "dataset_dir": str(resolve_path(data_dir)),
        "train_images": len(train_data),
        "validation_images": len(val_data),
        "epochs_requested": epochs,
        "batch_size": batch_size,
        "learning_rate": learning_rate,
        "weight_decay": weight_decay,
        "seed": seed,
        "best_model_checkpoint": trainer.state.best_model_checkpoint,
        "final_checkpoint": str(final_dir),
    }
    (final_dir / "sirap_training.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    save_json(manifest, "results/metrics/entrenamiento_rtdetr.json")
    logger.info("Checkpoint RT-DETRv2 guardado en %s", final_dir)
    return final_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Entrena RT-DETRv2 R18 con Transformers para SIRAP")
    parser.add_argument("--country", choices=("ecuador", "usa"), default="ecuador")
    parser.add_argument("--data-dir", default=None, help="Carpeta del dataset en formato COCO Detection")
    parser.add_argument("--data-yaml", default=None, help="data.yaml de un dataset YOLO local para convertir")
    parser.add_argument("--convert-yolo", action="store_true", help="Convierte --data-yaml a --output-dir en COCO")
    parser.add_argument("--roboflow", action="store_true", help="Descarga el dataset Roboflow en COCO Detection")
    parser.add_argument("--output-dir", default=None, help="Checkpoint final; por defecto models/<country>/detector/rtdetr_r18")
    parser.add_argument("--run-dir", default=None, help="Carpeta de checkpoints temporales del Trainer")
    parser.add_argument("--model-id", default=DEFAULT_MODEL_ID)
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--learning-rate", type=float, default=5e-5)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if args.convert_yolo:
        if not args.data_yaml or not args.output_dir:
            parser.error("--convert-yolo requiere --data-yaml y --output-dir.")
        convert_yolo_to_coco(args.data_yaml, args.output_dir)
        return
    data_dir = download_roboflow_dataset() if args.roboflow else args.data_dir
    if not data_dir:
        parser.error("Indique --data-dir o use --roboflow.")
    train_detector(data_dir, country=args.country, model_id=args.model_id,
                   output_dir=args.output_dir, run_dir=args.run_dir, epochs=args.epochs,
                   batch_size=args.batch_size, learning_rate=args.learning_rate,
                   weight_decay=args.weight_decay, seed=args.seed, force=args.force)


if __name__ == "__main__":
    main()
