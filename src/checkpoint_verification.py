"""Verified RT-DETR checkpoint restoration and validation-only IR checks."""
from __future__ import annotations

import hashlib
import importlib.metadata
import inspect
import json
from pathlib import Path


def runtime_versions():
    versions = {}
    for name in ("torch", "torchvision", "transformers", "accelerate", "openvino", "numpy"):
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    return versions


def file_sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def checkpoint_hashes(directory):
    return {p.name: file_sha256(p) for p in sorted(Path(directory).iterdir())
            if p.is_file() and (p.suffix in {".json", ".safetensors"} or p.name == "pytorch_model.bin")}


def validate_loading_info(info):
    keys = ("missing_keys", "unexpected_keys", "mismatched_keys", "error_msgs")
    if not isinstance(info, dict):
        info = {key: getattr(info, key, []) for key in keys}
    failures = {key: list(info.get(key) or []) for key in keys}
    if any(failures.values()):
        raise ValueError("Checkpoint loading failed verification: " + json.dumps(failures, default=str))
    return failures


def load_verified_checkpoint(source, *, local_files_only=True, revision=None):
    """Apply Transformers' official key conversions and reject loading errors."""
    from transformers import RTDetrV2ForObjectDetection
    model, info = RTDetrV2ForObjectDetection.from_pretrained(
        str(source), trust_remote_code=False, local_files_only=local_files_only,
        output_loading_info=True, ignore_mismatched_sizes=False,
        **({"revision": revision} if revision else {}))
    checked = validate_loading_info(info)
    if model.config.num_labels != 1:
        raise ValueError("Exactly one license-plate class is required.")
    model.eval()
    return model, {"status": "passed", "source": str(source), "revision": revision,
                   "loading_info": checked, "runtime": runtime_versions(),
                   "checkpoint_sha256": checkpoint_hashes(source) if Path(source).is_dir() else {},
                   "loader": "from_pretrained with key conversion"}


def mapping_aware_trainer_class():
    """Restore the best checkpoint through the official loader, then copy strictly."""
    from transformers import Trainer
    class MappingAwareRTDetrTrainer(Trainer):
        def _load_best_model(self):
            if self.args.world_size != 1 or self.is_deepspeed_enabled or self.is_fsdp_enabled:
                raise RuntimeError("Verified restoration supports one training process.")
            if not self.state.best_model_checkpoint:
                raise RuntimeError("Training did not select a best checkpoint.")
            restored, report = load_verified_checkpoint(self.state.best_model_checkpoint)
            self.model.load_state_dict(restored.state_dict(), strict=True)
            self.model.tie_weights()
            self.sirap_best_reload_report = report
            (Path(self.args.output_dir) / "best_checkpoint_reload.json").write_text(
                json.dumps(report, indent=2), encoding="utf-8")
    return MappingAwareRTDetrTrainer


def save_native_checkpoint(model, processor, directory):
    """Save to a new directory and require an exact tensor roundtrip."""
    import torch
    directory = Path(directory)
    if directory.exists() and any(directory.iterdir()):
        raise FileExistsError(f"Preserve the existing candidate: {directory}")
    options = {"safe_serialization": True}
    if "save_original_format" in inspect.signature(model.save_pretrained).parameters:
        options["save_original_format"] = False
    model.save_pretrained(str(directory), **options)
    processor.save_pretrained(str(directory))
    reloaded, report = load_verified_checkpoint(directory)
    for name, tensor in model.state_dict().items():
        if not torch.equal(tensor.detach().cpu(), reloaded.state_dict()[name].detach().cpu()):
            raise ValueError(f"A tensor changed during save/reload: {name}")
    report["tensor_roundtrip"] = "exact"
    (directory / "checkpoint_verification.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def require_verified_ir(directory, country="ecuador"):
    """Bind country and successful validation checks to the exact IR/runtime bytes."""
    root = Path(directory)
    required = ("openvino_model.xml", "openvino_model.bin", "sirap_openvino.json",
                "sirap_training.json", "candidate_verification.json")
    missing = [name for name in required if not (root / name).is_file()]
    if missing:
        raise FileNotFoundError(f"Incomplete verified candidate at {root}: {missing}")
    manifest = json.loads((root / "sirap_training.json").read_text(encoding="utf-8"))
    if manifest.get("country") != country:
        raise ValueError(f"The manifest does not identify {country}; do not relabel another country's weights.")
    report = json.loads((root / "candidate_verification.json").read_text(encoding="utf-8"))
    if (report.get("status") != "passed" or report.get("split") != "val" or not report.get("images")
            or report.get("checkpoint_loading", {}).get("status") != "passed"):
        raise ValueError("Checkpoint and OpenVINO verification are required.")
    for name in ("openvino_model.xml", "openvino_model.bin", "sirap_openvino.json"):
        if report.get("checkpoint_sha256", {}).get(name) != file_sha256(root / name):
            raise ValueError(f"The verification report belongs to different IR bytes: {name}")
    return root


def infer_bbox_coordinate_space(processor, image_size=640):
    """Determine normalized box space using a known rectangular annotation."""
    import numpy as np
    from PIL import Image
    width, height = 800, 400
    expected = np.array([120., 200., 300., 80.])
    encoded = processor(images=Image.new("RGB", (width, height)),
        annotations={"image_id": 1, "annotations": [{"id": 1, "image_id": 1, "category_id": 0,
            "bbox": expected.tolist(), "area": 24000., "iscrowd": 0}]}, return_tensors="pt")
    box = encoded["labels"][0]["boxes"][0].cpu().numpy()
    xywh = np.array([box[0]-box[2]/2, box[1]-box[3]/2, box[2], box[3]])
    original_error = np.max(np.abs(xywh * [width, height, width, height] - expected))
    mask = encoded.get("pixel_mask")
    if mask is None:
        if original_error < 1.:
            return "original_image"
        raise ValueError("Processor geometry cannot be verified without its pixel mask.")
    padded_h, padded_w = encoded["pixel_values"].shape[-2:]
    valid_h = int(mask[0].any(dim=1).sum())
    valid_w = int(mask[0].any(dim=0).sum())
    scales = [padded_w*width/valid_w, padded_h*height/valid_h]*2
    padded_error = np.max(np.abs(xywh * scales - expected))
    if padded_error < 1. and padded_error < original_error:
        return "padded_input"
    if original_error < 1.:
        return "original_image"
    raise ValueError("Processor annotations do not match supported coordinate systems.")


def infer_resize_rounding(processor, image_size=640):
    from PIL import Image
    compatible = {"floor", "round"}
    for width, height in ((801, 403), (799, 503), (403, 801)):
        encoded = processor(images=Image.new("RGB", (width, height)), return_tensors="pt")
        if tuple(encoded["pixel_values"].shape[-2:]) != (image_size, image_size):
            raise ValueError("Export size must match the processor's padded input size.")
        mask = encoded["pixel_mask"][0]
        actual = (int(mask.any(dim=1).sum()), int(mask.any(dim=0).sum()))
        scale = min(processor.size.get("max_height", image_size)/height,
                    processor.size.get("max_width", image_size)/width)
        candidates = {"floor": (max(1, int(height*scale)), max(1, int(width*scale))),
                      "round": (max(1, round(height*scale)), max(1, round(width*scale)))}
        compatible &= {key for key, value in candidates.items() if value == actual}
    if not compatible:
        raise ValueError("Unsupported processor resize geometry.")
    return "floor" if "floor" in compatible else "round"


def verify_openvino_candidate(checkpoint, ir_dir, data_dir, *, split="val", max_images=8):
    """Compare pixels, masks, logits and boxes on validation, never on test."""
    import numpy as np
    import torch
    from PIL import Image
    from transformers import AutoImageProcessor
    from src.coco_evaluation import annotation_file, split_image_path
    from src.model import PlateDetector
    if split not in {"val", "valid"} or max_images < 1:
        raise ValueError("Conversion verification requires validation images.")
    model, loading = load_verified_checkpoint(checkpoint)
    processor = AutoImageProcessor.from_pretrained(str(checkpoint), trust_remote_code=False, use_fast=False)
    detector = PlateDetector(checkpoint=ir_dir, conf=.001, fallback_checkpoint=None)
    expected_space = infer_bbox_coordinate_space(processor, detector.imgsz)
    if detector.manifest.get("bbox_coordinate_space", "original_image") != expected_space:
        raise ValueError("IR box coordinates differ from training annotations; export a new bundle.")
    path = annotation_file(data_dir, split)
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = []
    for row in payload["images"][:max_images]:
        with Image.open(split_image_path(path, row["file_name"])) as original:
            image = np.asarray(original.convert("RGB"))
        encoded = processor(images=image, return_tensors="pt")
        pixels, mask, _ = detector._preprocess(image)
        np.testing.assert_allclose(encoded["pixel_values"].numpy(), pixels, atol=1e-6, rtol=1e-6)
        np.testing.assert_array_equal(encoded["pixel_mask"].numpy(), mask)
        with torch.inference_mode():
            reference = model(pixel_values=encoded["pixel_values"], pixel_mask=encoded["pixel_mask"])
        actual = detector.compiled_model([pixels, mask])
        logits = np.asarray(actual[detector.compiled_model.output(0)])
        boxes = np.asarray(actual[detector.compiled_model.output(1)])
        np.testing.assert_allclose(logits, reference.logits.numpy(), atol=.02, rtol=.01)
        np.testing.assert_allclose(boxes, reference.pred_boxes.numpy(), atol=.001, rtol=.001)
        rows.append({"image_id": row["id"], "max_logit_error": float(np.max(np.abs(logits-reference.logits.numpy()))),
                     "max_box_error": float(np.max(np.abs(boxes-reference.pred_boxes.numpy())))})
    if not rows:
        raise ValueError("Validation must contain at least one image.")
    return {"status": "passed", "split": "val", "images": rows, "checkpoint_loading": loading,
            "bbox_coordinate_space": expected_space,
            "checkpoint_sha256": {name: file_sha256(Path(ir_dir)/name)
                for name in ("openvino_model.xml", "openvino_model.bin", "sirap_openvino.json")}}
