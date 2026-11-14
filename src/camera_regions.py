"""Explicit camera overlay exclusions for diagnostic and camera-specific use."""
from __future__ import annotations

from typing import Any, Sequence

# This profile is ONLY for the reviewed CH06 recordings from March 2005.
# It must never be enabled as the default USA detector configuration.
CH06_TIMESTAMP_PROFILE = 'savh_ch06_march2005_timestamp'
CH06_TIMESTAMP_REGION = (0.028, 0.0, 0.36, 0.06)


def filter_camera_overlays(detections: Sequence[Any], image_shape: Sequence[int],
                           profile: str | None = None) -> tuple[list[Any], list[Any]]:
    """Return kept/excluded detections without modifying image pixels or scores.

    Only boxes with >=95% of their own area inside the documented overlay
    region are excluded. Unknown profiles and invalid image shapes fail closed
    with an error, instead of silently applying a region to a different camera.
    """
    if not profile:
        return list(detections), []
    if profile != CH06_TIMESTAMP_PROFILE:
        raise ValueError(f'Unknown camera overlay profile: {profile}')
    if len(image_shape) < 2 or image_shape[0] <= 0 or image_shape[1] <= 0:
        raise ValueError('A positive camera height and width are required.')
    height, width = image_shape[:2]
    left, top, right, bottom = CH06_TIMESTAMP_REGION
    region = (left*width, top*height, right*width, bottom*height)
    kept, excluded = [], []
    for detection in detections:
        x1, y1, x2, y2 = detection.box
        area = max(0., x2-x1) * max(0., y2-y1)
        intersection = (max(0., min(x2, region[2])-max(x1, region[0])) *
                        max(0., min(y2, region[3])-max(y1, region[1])))
        if area > 0 and intersection / area >= 0.95:
            excluded.append(detection)
        else:
            kept.append(detection)
    return kept, excluded
