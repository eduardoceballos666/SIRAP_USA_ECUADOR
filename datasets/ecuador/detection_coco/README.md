# Ecuador COCO detection development set

This directory contains the six Ecuador photographs supplied for training and testing.
The original files came from the user's public [source folder](https://drive.google.com/drive/folders/1fEsgY7onlFo4ZkJmKBbHWaLbwl-WCyBp).
Only the six requested photos are included; older files in that folder are excluded.

| Split | Images | Plate boxes | Files |
|---|---:|---:|---|
| train | 4 | 9 | ecuador_01.jpg, ecuador_03.jpg, ecuador_04.jpeg, ecuador_06.jpeg |
| valid | 1 | 1 | ecuador_05.jpeg |
| test | 1 | 1 | ecuador_02.jpeg |

Each split has `_annotations.coco.json` and an `images/` directory.
`file_name` resolves relative to its split, for example `images/ecuador_01.jpg`.
`sample_annotations.json` records original filenames, pixel dimensions, SHA256 hashes,
scene groups, split assignments and manually reviewed pixel `[x, y, width, height]` boxes.

The two views showing truck PDE-1577 share `source_group=quito_pde1577` and both stay in train.
All images and groups are disjoint across splits. Visible background plates are annotated,
including a partially occluded bus plate. A plate fully hidden behind the gate barrier is
excluded. Detection labels do not include guessed OCR transcriptions.

Run [the Ecuador notebook](../../../notebooks/ecuador/sirap_backend_ecuador.ipynb):
audit in 1.2, train in 3.1, load the resulting IR in 4, validate in 5.2,
then evaluate the frozen candidate on the held-out development image in 5.3.
The notebook reads this directory directly from its GitHub clone; no Drive download is needed.

The audit rejects missing JSON/images, invalid boxes/categories, incorrect dimensions,
duplicate bytes and shared scene groups. Test data must not select weights, epochs or thresholds.
AP uses COCO IoU .50:.95 with maxDets=100; precision/recall/F1 use actual TP/FP/FN at the fixed
confidence threshold and IoU .50. Empty predictions are evaluated rather than skipped.

**Scope:** this is a six-image, positive-only development set, not an independent field study.
One validation and one test image cannot establish general accuracy or a negative-scene
false-positive rate. Add diverse Ecuador vehicles, sessions, lighting and real negative scenes
before operational evaluation. SAVH crops and USA images are separate sources and are not
silently added to these splits. No trained-model results are claimed by preparing these files.
