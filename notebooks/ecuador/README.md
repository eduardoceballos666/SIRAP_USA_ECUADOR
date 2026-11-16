# Ecuador notebook

The active file is [sirap_backend_ecuador.ipynb](sirap_backend_ecuador.ipynb).
[Open it in Colab](https://colab.research.google.com/github/eduardoceballos666/SIRAP_USA_ECUADOR/blob/main/notebooks/ecuador/sirap_backend_ecuador.ipynb).

The six supplied Ecuador photos are annotated in
`datasets/ecuador/detection_coco/`: four training images with nine boxes,
one validation image with one box, and one held-out development test image with one box.
The two views of the same truck stay together in training.

| Section | Contents |
|---|---|
| 0 | Dependencies, Ecuador paths, execution flags and optional persistence. |
| 1 | Labeled COCO scenes, image/box/group audit and SAVH Guayaquil crops. |
| 2 | Ecuador plate normalization and reviewed SAVH OCR references. |
| 3 | Optional training, candidate identity, CSV authorization list and experimental decision rule. |
| 4 | Load a complete Ecuador OpenVINO IR without changing its training manifest. |
| 5 | 5.1 smoke check; 5.2 COCO validation and candidate freeze; 5.3 held-out development test. |
| 6 | Video demonstration and optional SRI/owner queries. |
| 7 | Cloudflare bridge, camera reader, connection check, session and local executor. |
| 8 | Detector CPU latency on validation images. |
| 9 | Optional publication of a reviewed IR bundle. |
| 10 | Ground-truth annotation preview for training and validation. |

Run setup and the audit first. Enable `RUN_TRAIN_ECUADOR=True` in a GPU Colab runtime
and run 3.1. Training starts from `merve/license-plates-rtdetrv2`, uses at most
30 epochs, patience 8 and seed 2, and selects by validation loss.
It saves Transformers weights and OpenVINO IR under
`/content/SIRAP_workspace/ecuador/models/detector/rtdetrv2_s/seed_2/`.
Enable optional Drive persistence before training to retain these artifacts across resets.

Then enable `RUN_INFERENCE=True`, load the candidate in 4, and enable
`RUN_COCO_VALIDATION=True` for 5.2. After selecting the candidate and threshold using
validation only, enable `RUN_FINAL_TEST_EVALUATION=True` for 5.3.
The held-out test checks the candidate's XML/BIN hashes, dataset fingerprint and thresholds
against the frozen validation plan and preserves an existing report.

COCO AP50–95/AP50/AP75 and threshold-specific TP/FP/FN, precision, recall and F1
are computed separately. A blank-image smoke check is not an accuracy evaluation.
Six positive images are a development check; field acceptance and negative-scene testing need more data.
Preparing this notebook does not execute training or produce model metrics.

Execution and publication flags start disabled. Existing model manifests are never relabeled
as Ecuador. Camera sessions require an Ecuador calibration report bound to the exact IR;
a single validation image does not provide that operational calibration.
Section 9 publishes only `models/ecuador/detector/rtdetrv2_s/openvino/`.
The application's configured checkpoint is managed separately.
