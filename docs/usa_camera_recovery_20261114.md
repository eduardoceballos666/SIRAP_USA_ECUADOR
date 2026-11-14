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

## Completed three-seed recovery run

The companion notebook completed run `20261114T210050Z` on an A100 using code
revision `1cc1db8db8324b6cfaefb17ab2391c4bfd8e06df`. Each seed starts from the
retained seed-1 Transformers weights, with a 50-epoch cap, patience 8, batch
size 8 and learning rate 0.00005. Early stopping completed normally:

| Seed | Epochs completed | Best checkpoint epoch | Validation mAP50-95 |
|---|---:|---:|---:|
| 0 | 15 | 7 | 0.7460077444 |
| 1 | 15 | 7 | 0.7574922934 |
| 2 | 17 | 9 | 0.7670810749 |

Within each seed the trainer restores the checkpoint with the lowest
validation loss. Across seeds, the exported OpenVINO candidates are selected
by validation mAP50-95. Seed 2 was selected. All three Transformers and
OpenVINO candidates, trainer states, hashes and metrics are saved in a separate
private Drive run folder. The retained original checkpoint and operational
calibration were not replaced.

At confidence 0.70 and matching IoU 0.50, the selected raw detector produced
41 TP, 0 FP and 0 FN across all 79 validation scenes, without using the
camera-overlay filter. None of the eight target-camera negatives or 30 PKLot
negatives had a detection at this threshold. Thresholds 0.70, 0.75, 0.80 and
0.85 produced the same counts; 0.90 missed two plates. The earliest best-F1
grid point, 0.70, is recorded as a validation candidate only.

The retained baseline was evaluated on the identical 79 scenes, same corrected
geometry and Colab CPU. Its mAP50-95 was 0.5757094402; at confidence 0.70 it
had 40 TP, 9 FP and 1 FN. The new model's 0.7670810749 is directly comparable
to that value. The older 0.8321 result used a different, 534-image grouped
Roboflow validation and must not be used as a before/after comparison.

The aggregate results are in
[`usa_camera_recovery_validation_20261114.json`](../results/metrics/usa_camera_recovery_validation_20261114.json).
Per-image predictions, source names and detailed model records remain private.
The extended-validation cell reproduces the baseline comparison and private
evidence. All training and evaluation switches are off by default.

## Limits and independent data still required

The seed and threshold were both selected on validation. The 41/41 observed
precision and recall yield descriptive 95% Wilson intervals of
91.43%-100% and Clopper-Pearson intervals of 91.40%-100%. They do not establish
a 99% population precision guarantee. The validation split has 42 source
groups; its eight target-camera negatives all come from one recording/day,
and PKLot negatives are retained as one source group. Related scenes further
limit binomial inference.

The available manual test has 42 positive scenes and no negatives. March 18
has prior review exposure; March 19 is validation; March 23 is training. A new,
previously unexamined recording/day is needed for target-camera final-test
negatives. Do not relabel the reviewed train/validation scenes as test. The
main notebook's separate holdout-size and calibration guards must also be
satisfied before a final detector evaluation.

The recovery report keeps `operational_threshold: null`,
`usable_for_access_decisions: false` and `final_test_evaluated: false`.
Independent detector, OCR and end-to-end decision evaluations remain pending;
no Space deployment or automatic authorization was enabled.

Fourteen focused regression cases passed for landscape/portrait/square box
mapping, padding clipping, opt-in overlay behavior, argument compatibility,
train/valid-only conversion and recording-day separation. GitHub CI run
43641023619 also passed all 113 Python cases and the Vue tests/build after API
contract tests were isolated from external IR weights. Those API fixtures
validate the HTTP contract, not detector quality; the real OpenVINO evaluation
above provides model evidence.
