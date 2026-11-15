"""Box mapping regressions for actual landscape and portrait camera inputs."""
import numpy as np
import pytest

from src.model import PlateDetector


class CompiledOutputStub:
    def __init__(self, box):
        self.box = box

    def output(self, index):
        return index

    def __call__(self, inputs):
        return {0: np.array([[[8.0]]], dtype=np.float32),
                1: np.array([[self.box]], dtype=np.float32)}


def detector_for(box):
    detector = PlateDetector.__new__(PlateDetector)
    detector.imgsz = 640
    detector.manifest = {}
    detector.conf = 0.6
    detector.class_id = 0
    detector.compiled_model = CompiledOutputStub(box)
    return detector


@pytest.mark.parametrize('height,width', [(320,640),(640,320),(640,640),(458,690)])
def test_predicted_box_returns_to_original_frame(height,width):
    # A plate at [20%,55%,60%,75%] in the original frame, encoded in
    # padded-canvas coordinates exactly as the raw OpenVINO output is.
    scale = min(640/height,640/width)
    rh,rw = round(height*scale),round(width*scale)
    box = [0.4*rw/640,0.65*rh/640,0.4*rw/640,0.2*rh/640]
    result=detector_for(box).detect(np.zeros((height,width,3),dtype=np.uint8))
    assert len(result)==1
    assert result[0].box == pytest.approx((0.2*width,0.55*height,0.6*width,0.75*height),abs=0.001)


def test_box_wholly_inside_bottom_padding_is_discarded():
    assert detector_for([0.5,0.9,0.2,0.1]).detect(np.zeros((320,640,3),dtype=np.uint8)) == []


def test_box_crossing_padding_is_clipped_to_camera_frame():
    result=detector_for([0.5,0.45,0.2,0.3]).detect(np.zeros((320,640,3),dtype=np.uint8))
    assert result[0].box == pytest.approx((256,192,384,320),abs=0.001)
