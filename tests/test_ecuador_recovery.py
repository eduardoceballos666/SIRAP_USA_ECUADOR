"""Regression checks for recovery, provenance, geometry and independent splits."""
import ast
import hashlib
import json
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from src.checkpoint_verification import require_verified_ir, validate_loading_info
from src.detection_calibration import validation_threshold_sweep
from src.experiment_backup import create_backup, restore_backup, verify_backup
from src.model import PlateDetector
from scripts.prepare_ecuador_dataset import prepare_ecuador_dataset


@pytest.mark.parametrize("key", ["missing_keys", "unexpected_keys", "mismatched_keys", "error_msgs"])
def test_unexplained_loading_errors_are_rejected(key):
    with pytest.raises(ValueError, match="failed verification"):
        validate_loading_info({key: ["a changed tensor"]})


def test_snapshots_are_unique_verified_and_restore_without_overwriting(tmp_path):
    source = tmp_path/"model"
    source.mkdir()
    (source/"weights").write_bytes(b"original weights")
    first = create_backup({"model": source, "missing": tmp_path/"absent"}, tmp_path/"backups")
    second = create_backup({"model": source}, tmp_path/"backups")
    assert first != second
    assert "missing" in verify_backup(first)["missing_sources"]
    target = restore_backup(first, tmp_path/"recovered")
    assert (target/"model/weights").read_bytes() == b"original weights"
    with pytest.raises(FileExistsError):
        restore_backup(first, target)
    (first/"model/weights").write_bytes(b"damaged")
    with pytest.raises(ValueError, match="damaged"):
        verify_backup(first)


def test_snapshot_rejects_recursive_destination(tmp_path):
    with pytest.raises(ValueError, match="inside"):
        create_backup({"model": tmp_path}, tmp_path/"nested")


def payload(negative=True):
    images = [{"id": 1, "file_name": "a.jpg", "width": 100, "height": 100, "source_group": "positive"}]
    if negative:
        images.append({"id": 2, "file_name": "b.jpg", "width": 100, "height": 100, "source_group": "negative"})
    return {"images": images, "categories": [{"id": 1, "name": "plate"}],
            "annotations": [{"id": 1, "image_id": 1, "category_id": 1, "bbox": [10, 10, 20, 10]}]}


def test_real_negatives_affect_threshold_choice():
    predictions = [{"image_id": 1, "category_id": 1, "bbox": [10, 10, 20, 10], "score": .9},
                   {"image_id": 2, "category_id": 1, "bbox": [10, 10, 20, 10], "score": .3}]
    result = validation_threshold_sweep(payload(), predictions, thresholds=[.2, .5, .95],
        min_images=2, min_positives=1, min_negatives=1, min_groups=2)
    assert result["usable_for_inference"]
    assert result["threshold"] == .5
    assert result["thresholds"][0]["negative_scene_fp_rate"] == 1
    assert result["field_acceptance_demonstrated"] is False


def test_small_development_set_cannot_enable_inference():
    data = payload()
    data["info"] = {"scope": "development_only"}
    result = validation_threshold_sweep(data, [], thresholds=[.7])
    assert result["usable_for_inference"] is False and result["threshold"] is None
    assert any("development" in reason for reason in result["reasons"])


def test_threshold_selection_cannot_use_test():
    with pytest.raises(ValueError, match="never test"):
        validation_threshold_sweep(payload(), [], split="test")


def test_resize_rounding_and_padded_box_mapping_share_geometry():
    detector = PlateDetector.__new__(PlateDetector)
    detector.imgsz = 640
    detector.manifest = {"resize_rounding": "floor", "bbox_coordinate_space": "padded_input"}
    assert detector._resize_dimensions(648, 1200) == (345, 640)
    assert detector._box_pixel_scales(648, 1200) == (1200, 640*648/345)
    detector.manifest = {}
    assert detector._resize_dimensions(648, 1200) == (346, 640)
    assert detector._box_pixel_scales(648, 1200) == (1200, 648)


def test_candidate_gate_rejects_foreign_country_and_changed_runtime(tmp_path):
    names = ("openvino_model.xml", "openvino_model.bin", "sirap_openvino.json")
    for name in names:
        (tmp_path/name).write_text("{}")
    (tmp_path/"sirap_training.json").write_text(json.dumps({"country": "usa"}))
    report = {"status": "passed", "split": "val", "images": [{"image_id": 1}],
              "checkpoint_loading": {"status": "passed"},
              "checkpoint_sha256": {name: hashlib.sha256((tmp_path/name).read_bytes()).hexdigest() for name in names}}
    (tmp_path/"candidate_verification.json").write_text(json.dumps(report))
    with pytest.raises(ValueError, match="relabel"):
        require_verified_ir(tmp_path)
    (tmp_path/"sirap_training.json").write_text(json.dumps({"country": "ecuador"}))
    assert require_verified_ir(tmp_path) == tmp_path
    (tmp_path/"sirap_openvino.json").write_text('{"resize_rounding":"round"}')
    with pytest.raises(ValueError, match="different IR bytes"):
        require_verified_ir(tmp_path)


def make_source(tmp_path):
    root = tmp_path/"raw"
    split = root/"train"
    split.mkdir(parents=True)
    rng = np.random.default_rng(81)
    data = {"images": [], "annotations": [], "categories": [{"id": 1, "name": "plate"}]}
    for i in range(12):
        name = f"image_{i}.png"
        Image.fromarray(rng.integers(0, 256, (48, 64, 3), dtype=np.uint8)).save(split/name)
        data["images"].append({"id": i+1, "file_name": name, "width": 64, "height": 48,
                               "source_group": f"reviewed_{i}"})
        if i < 6:
            data["annotations"].append({"id": i+1, "image_id": i+1, "category_id": 1,
                                         "bbox": [5, 5, 20, 10], "iscrowd": 0})
    (split/"_annotations.coco.json").write_text(json.dumps(data))
    source = {"root": str(root), "country": "ecuador", "country_reviewed": True, "groups_reviewed": True,
              "negatives_reviewed": True, "license": "CC BY 4.0", "source_url": "https://example.org/reviewed",
              "plate_category_names": ["plate"]}
    manifest = tmp_path/"sources.json"
    manifest.write_text(json.dumps({"sources": [source]}))
    return root, data, source, manifest


def test_import_creates_grouped_splits_and_preserves_original(tmp_path):
    root, data, source, manifest = make_source(tmp_path)
    from src.coco_evaluation import audit_coco_dataset
    result = prepare_ecuador_dataset(manifest, tmp_path/"new")
    audit = audit_coco_dataset(result)
    assert sum(s["images"] for s in audit["splits"]) == 12
    assert all(s["negative_images"] > 0 for s in audit["splits"])
    assert len(json.loads((root/"train/_annotations.coco.json").read_text())["images"]) == 12
    with pytest.raises(FileExistsError):
        prepare_ecuador_dataset(manifest, result)


@pytest.mark.parametrize("problem", ["unknown_class", "missing_group", "unreviewed_negatives"])
def test_import_requires_human_class_group_and_negative_review(tmp_path, problem):
    root, data, source, manifest = make_source(tmp_path)
    if problem == "unknown_class": data["categories"][0]["name"] = "2"
    if problem == "missing_group": data["images"][0].pop("source_group")
    if problem == "unreviewed_negatives": source["negatives_reviewed"] = False
    (root/"train/_annotations.coco.json").write_text(json.dumps(data))
    manifest.write_text(json.dumps({"sources": [source]}))
    with pytest.raises(ValueError):
        prepare_ecuador_dataset(manifest, tmp_path/"rejected")


def test_notebook_and_generated_runners_compile_without_execution():
    root = Path(__file__).resolve().parents[1]
    import nbformat
    notebook = nbformat.read(root/"notebooks/ecuador/sirap_backend_ecuador.ipynb", as_version=4)
    nbformat.validate(notebook)
    sources = []
    for i, cell in enumerate(notebook.cells):
        if cell.cell_type != "code":
            continue
        assert cell.execution_count is None and cell.outputs == []
        sources.append(cell.source)
        tree = ast.parse(cell.source)
        compile(tree, f"ecuador-cell-{i}", "exec", flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                if any(isinstance(t, ast.Name) and t.id in {"BRIDGE_SCRIPT", "EDGE_RUNNER_SCRIPT"} for t in node.targets):
                    compile(node.value.value, "generated-runner", "exec")
    joined = "\n".join(sources)
    for flag in ("RUN_TRAIN_ECUADOR", "RUN_INFERENCE", "RUN_FINAL_TEST_EVALUATION", "RUN_CAMERA_CONNECTION_CHECK", "LIVE_ENABLED"):
        assert f"{flag} = False" in joined
    assert "PERSIST_OUTPUTS_TO_DRIVE = True" in joined
