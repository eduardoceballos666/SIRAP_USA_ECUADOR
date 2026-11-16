"""Regression tests for COCO matching, empty results and split isolation."""
import copy
import json
from pathlib import Path

import pytest
from PIL import Image

from src.coco_evaluation import (audit_coco_dataset, coco_detection_metrics,
                                  normalize_coco, split_image_path)


def labels(negative=False, crowd=False):
    return {"images": [{"id": 1, "file_name": "images/a.png", "width": 100, "height": 80},
                       {"id": 2, "file_name": "images/b.png", "width": 100, "height": 80}],
            "categories": [{"id": 0, "name": "plate"}],
            "annotations": [] if negative else [
                {"id": 0, "image_id": 1, "category_id": 0, "bbox": [10, 10, 20, 10], "iscrowd": int(crowd)}]}


def prediction(image=1, score=.9, box=None):
    return {"image_id": image, "category_id": 0, "bbox": box or [10, 10, 20, 10], "score": score}


def test_perfect_with_zero_source_annotation_id():
    result = coco_detection_metrics(labels(), [prediction()])
    assert result["map50_95"] == pytest.approx(1)
    assert (result["tp"], result["fp"], result["fn"]) == (1, 0, 0)
    assert result["precision"] == result["recall"] == result["f1"] == 1


def test_empty_predictions_have_zero_ap_and_one_false_negative():
    result = coco_detection_metrics(labels(), [])
    assert result["map50_95"] == 0
    assert (result["tp"], result["fp"], result["fn"]) == (0, 0, 1)
    assert result["recall"] == result["f1"] == 0


def test_negative_image_false_positive_changes_precision():
    result = coco_detection_metrics(labels(), [prediction(), prediction(image=2)])
    assert (result["tp"], result["fp"], result["fn"]) == (1, 1, 0)
    assert result["precision"] == .5
    assert result["f1"] == pytest.approx(2 / 3)


def test_confidence_counts_are_separate_from_ap():
    result = coco_detection_metrics(labels(), [prediction(score=.3)], operating_threshold=.7)
    assert result["map50"] == pytest.approx(1)
    assert (result["tp"], result["fp"], result["fn"]) == (0, 0, 1)


def test_duplicate_detection_is_a_false_positive():
    result = coco_detection_metrics(labels(), [prediction(), prediction(score=.8)])
    assert (result["tp"], result["fp"], result["fn"]) == (1, 1, 0)


def test_wrong_box_is_false_positive_and_false_negative():
    result = coco_detection_metrics(labels(), [prediction(box=[70, 50, 10, 10])])
    assert result["map50"] == 0
    assert (result["tp"], result["fp"], result["fn"]) == (0, 1, 1)


def test_negative_only_ap_and_recall_are_undefined():
    result = coco_detection_metrics(labels(negative=True), [prediction()])
    assert result["map50"] is None and result["recall"] is None
    assert (result["tp"], result["fp"], result["fn"]) == (0, 1, 0)


def test_crowd_detection_is_ignored():
    result = coco_detection_metrics(labels(crowd=True), [prediction()])
    assert (result["tp"], result["fp"], result["fn"]) == (0, 0, 0)
    assert result["ignored_predictions"] == 1


@pytest.mark.parametrize("change", ["duplicate", "category", "box", "image"])
def test_invalid_labels_fail(change):
    data = labels()
    if change == "duplicate":
        data["annotations"].append(copy.deepcopy(data["annotations"][0]))
    elif change == "category":
        data["annotations"][0]["category_id"] = 7
    elif change == "box":
        data["annotations"][0]["bbox"] = [99, 0, 20, 10]
    else:
        data["annotations"][0]["image_id"] = 5
    with pytest.raises(ValueError):
        normalize_coco(data)


def write_split(root, split, color, group):
    folder = root / split
    (folder / "images").mkdir(parents=True)
    Image.new("RGB", (100, 80), color).save(folder / "images/a.png")
    data = labels()
    data["images"] = data["images"][:1]
    data["images"][0]["source_group"] = group
    (folder / "_annotations.coco.json").write_text(json.dumps(data))
    return folder


def test_group_leakage_is_rejected(tmp_path):
    write_split(tmp_path, "train", "red", "same_truck")
    write_split(tmp_path, "valid", "green", "same_truck")
    with pytest.raises(ValueError, match="Group"):
        audit_coco_dataset(tmp_path, ("train", "val"))


def test_duplicate_bytes_are_rejected(tmp_path):
    write_split(tmp_path, "train", "red", "one")
    write_split(tmp_path, "valid", "red", "two")
    with pytest.raises(ValueError, match="Duplicate image"):
        audit_coco_dataset(tmp_path, ("train", "val"))


def test_missing_file_cannot_be_found_in_another_split(tmp_path):
    train = write_split(tmp_path, "train", "red", "one")
    valid = write_split(tmp_path, "valid", "green", "two")
    (valid / "images/a.png").unlink()
    with pytest.raises(FileNotFoundError):
        split_image_path(valid / "_annotations.coco.json", "images/a.png")
    with pytest.raises(ValueError):
        split_image_path(train / "_annotations.coco.json", "../valid/images/a.png")


def test_supplied_six_photos_have_disjoint_splits():
    root = Path(__file__).resolve().parents[1] / "datasets/ecuador/detection_coco"
    result = audit_coco_dataset(root)
    assert [(r["images"], r["plates"]) for r in result["splits"]] == [(4, 9), (1, 1), (1, 1)]


def test_evaluation_wrapper_records_hashes_and_uses_explicit_checkpoint(tmp_path, monkeypatch):
    from types import SimpleNamespace
    import src.evaluate as evaluation
    write_split(tmp_path, "test", "blue", "held_out")
    xml = tmp_path / "candidate/openvino_model.xml"
    xml.parent.mkdir()
    xml.write_text("test model identity")
    xml.with_suffix(".bin").write_bytes(b"test weights identity")

    class Detector:
        def __init__(self, **kwargs):
            assert kwargs["fallback_checkpoint"] is None
            assert kwargs["checkpoint"] == xml.parent
            assert kwargs["conf"] == .001
            self.model_path, self.source = xml, str(xml)
        def detect(self, image, max_detections):
            return [SimpleNamespace(box=(10, 10, 30, 20), confidence=.9)]

    monkeypatch.setattr(evaluation, "PlateDetector", Detector)
    output = tmp_path / "metrics/report.json"
    result = evaluation.evaluate_detector(tmp_path, checkpoint=xml.parent,
                threshold=.001, operating_threshold=.7, result_path=output)
    assert result["tp"] == 1 and result["map50"] == pytest.approx(1)
    assert set(result["checkpoint_sha256"]) == {"openvino_model.xml", "openvino_model.bin"}
    assert json.loads(output.read_text())["operating_threshold"] == .7


def test_evaluation_missing_candidate_does_not_fall_back(tmp_path, monkeypatch):
    import src.evaluate as evaluation
    write_split(tmp_path, "test", "blue", "held_out")
    class Missing:
        def __init__(self, **kwargs):
            assert kwargs["fallback_checkpoint"] is None
            raise FileNotFoundError("requested candidate missing")
    monkeypatch.setattr(evaluation, "PlateDetector", Missing)
    output = tmp_path / "must_not_exist.json"
    with pytest.raises(FileNotFoundError, match="requested candidate"):
        evaluation.evaluate_detector(tmp_path, checkpoint=tmp_path / "missing", result_path=output)
    assert not output.exists()
