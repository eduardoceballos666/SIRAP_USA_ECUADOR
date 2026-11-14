import pytest

from src.camera_regions import CH06_TIMESTAMP_PROFILE, filter_camera_overlays
from src.model import Detection


def test_profile_is_opt_in_and_preserves_plate_outside_timestamp():
    stamp = Detection((24, 6, 236, 24), 0.91)
    plate = Detection((300, 300, 390, 335), 0.88)
    assert filter_camera_overlays([stamp, plate], (458,690))[0] == [stamp,plate]
    kept, removed = filter_camera_overlays([stamp,plate],(458,690),CH06_TIMESTAMP_PROFILE)
    assert kept == [plate]
    assert removed == [stamp]


def test_mere_overlap_with_timestamp_does_not_remove_a_box():
    box = Detection((220,20,300,70),0.9)
    kept, removed = filter_camera_overlays([box],(458,690),CH06_TIMESTAMP_PROFILE)
    assert kept == [box] and removed == []


def test_unknown_profile_is_rejected():
    with pytest.raises(ValueError,match='Unknown camera'):
        filter_camera_overlays([], (458,690), 'different_camera')


def test_invalid_camera_geometry_is_rejected():
    with pytest.raises(ValueError,match='height and width'):
        filter_camera_overlays([], (0,690), CH06_TIMESTAMP_PROFILE)
