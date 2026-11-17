# Ecuador notebook

Active file: [sirap_backend_ecuador.ipynb](sirap_backend_ecuador.ipynb).
[Open in Colab](https://colab.research.google.com/github/eduardoceballos666/SIRAP_USA_ECUADOR/blob/main/notebooks/ecuador/sirap_backend_ecuador.ipynb).

Start with **0.0 in the original runtime**, before installing dependencies or updating Git.
It preserves existing Ecuador weights and run files in a new checksum-verified Drive snapshot.
A missing directory is reported; a metrics-only snapshot is not a saved model.

| Section | Contents |
|---|---|
| 0 | Emergency preservation, pinned dependencies, controls and verified backups. |
| 1 | COCO audit, SAVH OCR crops and reviewed additional Ecuador scene intake. |
| 2 | Ecuador plate normalization and reviewed SAVH OCR reference. |
| 3 | Optional training; model identity; CSV rule; 3.5 checkpoint recovery without training. |
| 4 | Load an Ecuador IR bound to a successful conversion verification report. |
| 5 | 5.1 smoke check; 5.2 validation; 5.3 threshold sweep and freeze; 5.4 held-out evaluation. |
| 6 | Video demonstration and optional SRI/owner queries. |
| 7 | Cloudflare bridge, connection check, live session and on-site runner. |
| 8 | CPU latency on validation images. |
| 9 | Optional reviewed IR publication. |
| 10 | Training/validation ground-truth preview. |

## Recover the completed training

The original execution's metrics, 30-epoch table and loading warnings are archived in
[results/ecuador/metrics/archive/20261116_six_photo_user_run](../../results/ecuador/metrics/archive/20261116_six_photo_user_run/).
The complete executed notebook remains in commit `0b7bcb7739f43d1b41f0a1dbc5c58e3f9207f491`.
The active notebook clears outputs so historical results cannot appear to be a new run.

1. Run 0.0 in the original runtime, then setup and the audit in 1.2.
2. Set `RECOVERY_CHECKPOINT` to the real Ecuador Transformers folder, containing its config,
   weights, processor config and original `sirap_training.json`.
   An original manifest stored separately can be specified with `RECOVERY_MANIFEST_PATH`.
3. Enable `RUN_CHECKPOINT_RECOVERY=True` and run 3.5. It restores through official key mappings,
   checks save/reload tensor equality, exports a new IR and compares its raw outputs with
   PyTorch on validation. It does not start training.
4. Enable `RUN_INFERENCE=True`, load the verified candidate in 4 and run validation in 5.2.
5. Inspect validation-only threshold diagnostics in 5.3. Freeze the selected candidate before
   using a fresh held-out test in 5.4.

The candidate found in the Drive Ecuador-named directory identifies itself as **USA seed 1**.
It is rejected as Ecuador. The actual trained Ecuador checkpoint was not available during
this correction; implementation tests with public reference weights do not measure its accuracy.

## What changed

Transformers 5 can serialize checkpoint names differently from names expected by a direct
`load_state_dict`. The mapping-aware Trainer restores the selected best model through
`from_pretrained`, rejects missing/unexpected/mismatched parameters and copies tensors strictly.

New IR exports declare the processor's actual resize rounding, padded box coordinate space
and FP32 inference precision. This corrects rectangular-image preprocessing and padding
inversion and makes CPU OpenVINO comparison reproducible. Older manifests retain their
existing geometry until explicitly re-exported. Verification and calibration bind XML, BIN
and runtime JSON bytes; model origin is never changed to match a directory name.

Drive persistence is enabled by default. Snapshots use unique names, verify every file and
never merge model directories. Restore requires a new destination. Owner, authorization and
camera CSV directories are excluded from experiment backups.

## Data and threshold limits

The six supplied images have 11 plate boxes: **4 train / 1 validation / 1 development test**.
The two views of the same truck remain in training. The original test image has already
been inspected and cannot become a fresh independent acceptance test by renaming it.

AP uses the low confidence floor, while TP/FP/FN use the stated operating threshold.
AP50=1 on one image can coexist with zero accepted predictions at 0.70. Validation now records
the maximum score and accepted count, and caches predictions with image, annotation and model hashes.

The threshold sweep uses validation only, includes real-negative false-positive scenes and
requires documented groups. Default support guards are 50 validation images, 25 positive,
25 negative and 5 groups, with precision/recall/false-positive targets. These configurable
counts are research safeguards, not statistical certification. The tiny positive-only set
cannot enable operational calibration. A separate explicit development freeze flag can
record a diagnostic test at the existing demonstration threshold.

Additional-source candidates and their review status are in
[detection_sources.json](../../datasets/ecuador/detection_sources.json).
**No additional export has been imported.** Optional Roboflow download needs your Colab secret;
classes, country, bounding boxes, real negatives and vehicle/session groups must be reviewed.
The importer creates a separate grouped dataset, joins exact/near duplicates before splitting
and excludes the known six photos from a fresh study. SAVH crops remain OCR data.

Training, recovery, inference, calibration, test, camera and publication flags are initially
false. New training retains the 30-epoch maximum, patience 8 and seed 2, in unique model/run
directories. No application weights were activated or replaced by this correction.
