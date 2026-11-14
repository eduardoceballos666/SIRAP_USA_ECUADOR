# USA camera recovery — 14 November 2026

## Confirmed problems and corrections

The OpenVINO postprocessor on the inspected main revision mapped normalized
boxes directly to original image dimensions, although its preprocessing had
resized the scene and padded it to a square input. Landscape boxes were
compressed upwards; portrait boxes were compressed along the horizontal axis.
The correction uses the actual non-padded dimensions from pixel_mask to undo
padding before returning boxes to the source frame. Boxes entirely in padding
are discarded; partially overlapping boxes are clipped. Square images keep
their mapping. The IR weights are unchanged.

All seven false detections on the eight target-camera validation negatives
cover the date/time overlay. `src.camera_regions.filter_camera_overlays` adds an
explicit, opt-in profile only for these reviewed CH06 recordings. It excludes
a detection only when at least 95% of its area is inside the documented
timestamp region. It does not alter image pixels or scores and is not a
general USA detector setting. The setting was chosen after inspecting
validation; it is not evidence from an independent camera test.

## Validation recheck with the retained seed-1 IR

The recheck used 79 validation scenes: 41 positive, 30 pre-existing PKLot
negatives and eight target-camera negatives. At confidence 0.60 and IoU 0.50:

| Postprocessing | TP | FP | FN | Precision | Recall |
|---|---:|---:|---:|---:|---:|
| Corrected padded-input geometry | 40 | 10 | 1 | 0.8000 | 0.9756 |
| Corrected geometry and explicit CH06 overlay profile | 40 | 3 | 1 | 0.9302 | 0.9756 |

The seven known timestamp detections are excluded, leaving zero detections in
those eight selected negative scenes. This is a same-validation diagnostic,
not an estimate of field performance. Neither configuration met the existing
0.99 precision requirement anywhere in the 0.05–0.95 threshold grid with at
least 11 true positives. Access decisions remain blocked; no operational
threshold is promoted. The private JSON records runtime, model hashes, every
threshold and per-image predictions. OpenVINO 2026.4.1 used its BF16 CPU hint;
confidence values vary slightly from the previous Colab CPU, while the
threshold-0.60 counts reproduce the known timestamp failure.

## Reviewed data prepared for domain adaptation

Two additional user-provided March 23 clips supplied 49 newly reviewed
full-frame negatives. Together with the original candidates:

| Split | Positive images | Negative images | Total |
|---|---:|---:|---:|
| Train | 192 | 57 | 249 |
| Validation | 41 | 38 | 79 |

Every March 23 target-camera clip stays in train. March 19 stays in validation;
the 30 PKLot images also stay in validation. Recording-day groups and exact
hashes are checked for overlap. Full scenes retain timestamps and the original
source watermark; no synthetic negative images were used. Source indexes,
hashes, private data and row-level diagnostics remain outside GitHub.

`scripts/usa_prepare_negative_recovery.py` creates train/valid COCO data using
the existing manifest and reviewed pack. The converter's default still requires
all three partitions. Its explicit train/valid mode skips test rows before
opening their images, enabling this preparation without consuming the test.

## Pending execution and independent data

The companion recovery notebook uses three seeds, a 50-epoch cap and patience
8, starting from the retained seed-1 Transformers weights. It keeps the old
checkpoint and calibration intact and saves candidates to a new private Drive
run folder. TrainingArguments compatibility handles the previously observed
removal of warmup_ratio/save_safetensors without silently dropping other
settings. No GPU training has run for this recovery revision.

Colab currently requires Google sign-in. The available manual test has 42
positive scenes and no negatives. March 18 has prior review exposure; March 19
is validation; March 23 is training. A new, previously unexamined recording/day
is needed for target-camera final-test negatives. Do not relabel the reviewed
train/validation scenes as test. The main notebook's separate holdout-size and
calibration guards must also be satisfied before a final detector evaluation.

Fourteen focused regression cases passed for landscape/portrait/square box
mapping, padding clipping, opt-in overlay behavior, argument compatibility,
train/valid-only conversion and recording-day separation. This validates the
code changes and data preparation, not new trained-model performance.
