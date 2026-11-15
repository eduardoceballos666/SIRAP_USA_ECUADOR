# USA RT-DETRv2-S notebook

The USA workflow is consolidated in one notebook: [sirap_backend_usa.ipynb](sirap_backend_usa.ipynb). It replaces the former staged USA notebooks, whose versions remain available in Git history.

For the reviewed camera-negative recovery run, use the bounded companion [sirap_negative_recovery.ipynb](sirap_negative_recovery.ipynb). It restores the private train/validation package, starts domain adaptation from the retained seed-1 weights, preserves three new candidates separately, and writes a private validation calibration. See the [geometry and data recovery record](../../docs/usa_camera_recovery_20261114.md). The A100 run completed on 14 November: seed 2 reached mAP50-95 0.7671 on 79 full scenes and 41 TP / 0 FP / 0 FN at confidence 0.70 without the overlay filter. Both seed and threshold were selected on validation; this is not an independent test. The candidate is preserved separately and is not enabled for automatic access decisions. [Aggregate results](../../results/metrics/usa_camera_recovery_validation_20261114.json).

The independent April recording diagnostic is now complete: **96.58% precision, 55.08% recall, 3/119 negative scenes with false detections, and 24/47 exact serial OCR crops**. No usable state was read in 181 detected crops, so all remained manual. The reference is AI-assisted and still needs human audit; this is not a qualified final test. See the [diagnostic report](../../docs/usa_independent_video_diagnostic_20261114.md), [aggregate metrics](../../results/metrics/usa_independent_video_diagnostic_20261114.json), and [read-only result notebook](usa_independent_video_diagnostic_20261114.ipynb). The April recording has been consumed for evaluation and must not be reused as unseen data after tuning.

The notebook is written in English and explains each executable section. It covers USA profile inspection, Roboflow download, COCO conversion, grouped data splitting, label review, hyperparameter search, three-seed fine-tuning, OpenVINO inference, threshold calibration, robustness and CPU latency checks, OCR evaluation, end-to-end scene evaluation, one-time detector testing, optional publishing, Cloudflare remote-camera testing, and a generated on-site edge inference runner.

## Model and runtime

- Detector: RT-DETRv2-S with a ResNet-18vd backbone.
- Starting checkpoint: `merve/license-plates-rtdetrv2`, listed as Apache-2.0.
- Fine-tuning: Transformers and PyTorch.
- Inference and detector evaluation: native Python OpenVINO Runtime.
- Input size: 640 pixels.

The checkpoint's published metrics describe its original evaluation data. They are not SIRAP USA results. Dataset terms are separate from the checkpoint license.

## Validation status (14 November 2026)

The completed recovery uses 249 training scenes (192 positive, 57 negative) and 79 validation scenes (41 positive, 38 negative). The selected recovery seed 2 achieved 41 TP / 0 FP / 0 FN at confidence 0.70 and IoU 0.50; all 38 negative scenes had no detections. On these identical 79 scenes, the retained baseline's mAP50-95 was 0.5757 versus the new candidate's 0.7671. This differs from the grouped Roboflow metric below. The descriptive 95% Wilson interval for the 41/41 observed precision is 91.43%-100%; related scenes and validation selection prevent treating it as a 99% guarantee.

The eight target-camera validation negatives come from one recording/day, separate from the March 23 training recordings. The 30 PKLot negatives remain validation-only. The reserved manual test still has 42 positives and no negatives and was not run here. A new recording from April 6 was subsequently processed as a joint diagnostic: 400 sampled frames, 319 resolved reference scenes and 81 uncertain scenes. It failed detector/OCR/access qualification; the qualified final protocol, reference audit and separate end-to-end coverage remain incomplete. No Space deployment was performed.

### Retained baseline before recovery

The retained original candidate was seed 1, chosen by grouped Roboflow validation at mAP50-95 = 0.8321. Before recovery, manual full-scene validation had 71 images: 41 with plates and 30 PKLot negatives. At the best observed confidence threshold (0.60), it produced 40 true positives, 3 false positives, and 1 false negative (precision 0.9302; recall 0.9756). This misses the 0.99 target, so the calibration report stores a null threshold and `usable_for_inference: false`. Do not use the checkpoint for live or access decisions.

The 30 PKLot scenes remain validation-only. PKLot is CC BY 4.0 and its official page requests citation; its images come from elevated fixed parking cameras in Brazil, and its dataset card says plates are not distinguishable. They are a limited background check, not evidence of USA gate-camera performance. The recovery added separately reviewed, group-disjoint target-camera negatives to training and validation; new recording groups remain necessary for independent testing.

Open Images V7 is a possible supplementary source: its metadata includes original URLs and per-image license fields, and its image-level annotations include verified presence/absence labels for supported classes. The class list includes vehicle registration plate. Google lists the images as CC BY 2.0 but explicitly says it does not warrant each image's license, so verify every original source and keep its attribution before using any image. No Open Images samples have been imported yet. MIO-TCD is closer in camera style and includes US/Canadian traffic scenes, but its official CC BY-NC-SA 4.0 terms require noncommercial use and share-alike; do not use it for SIRAP without confirming that those terms fit the intended use.

The repository already has `results/metrics/rtdetr_usa_independent_test.json`, but its model-selection record identifies a different seed-0 candidate. Treat it as a legacy artifact, not the final test for the selected seed-1 checkpoint. The new recovery seed-2 checkpoint's April recording diagnostic is a separate, failed evaluation described above. All training, evaluation, live-camera, metric-publishing, and Space-publishing switches are off by default.

## Dataset and credentials

The default source is Roboflow's **European + USA License plates**, workspace `plateblur`, project `european-usa-license-plates`, version 1, exported as COCO Segmentation. The notebook reads its boxes and maps the three plate labels to one detector class. Add `ROBOFLOW_API_KEY` to Colab Secrets; do not put the key in the notebook or Git.

An earlier inspection reported 13,143 training images, 386 validation images, and 106 test images. The notebook reads the current counts from the downloaded annotation files. It builds a grouped held-out test with at least 400 images by combining held-out source groups with additional groups reserved from training. This is an internal holdout from the same export, not an external dataset. Without vehicle/session IDs in `source_group_manifest.csv`, grouping is limited to filename families and exact-file hashes.

For complete vehicle or access-lane scenes, the notebook also supports the repository's CSV annotation template and COCO converter. Cropped plate images in `datasets/usa/seg_and_ocr/` are for OCR evaluation; they are not a substitute for full-scene detection data.

## Recommended run

Use a Colab GPU for training. The final recipe allows up to 50 epochs, early-stopping patience 8, and three seeds. Optuna uses at most eight screening trials of up to 12 epochs each. Expensive run switches are off by default.

Train and select the checkpoint and calibrate the operational threshold using validation only. Record the selected checkpoint and validation evidence, then freeze the model. The notebook blocks the held-out detector evaluation unless the test has at least 400 images, the checkpoint and threshold records match, and no prior final report exists.

## Optional remote-camera workflow

Section 16 of the consolidated notebook can create a token-protected camera bridge for a PC that can reach the camera, then connect through Cloudflare Tunnel. Add CAMARA_URL and CAMARA_TOKEN to Colab Secrets; use CF_ACCESS_CLIENT_ID and CF_ACCESS_CLIENT_SECRET when Cloudflare Access service tokens are configured. The live session is disabled by default and does not make access decisions.

Quick Tunnels are suitable for temporary experiments. Use a named tunnel with Cloudflare Access for a stable remote test. Section 16.5 generates a local runner that processes frames beside the camera and saves only confirmed OCR text and confidence metadata under the camera user's home folder. The current API has no dedicated machine-to-machine USA event route, so its optional uploader is disabled; do not send automated edge events to /api/operations. Implement a USA-aware event endpoint that checks authorization before enabling upload. The Colab test-mode CSV, JSON, and optional video remain in /content/SIRAP_workspace/live_camera/ and should not be committed.

## Results

Notebook outputs are not embedded in this README. Structured result files are stored under `results/metrics/`. The original threshold-calibration JSON blocks inference because its 0.99 precision target was not met. The recovery candidate met that empirical threshold on validation only. Its April recording diagnostic subsequently failed qualification, and the separate report keeps `operational_threshold: null` and `usable_for_access_decisions: false`. Read the diagnostic status and failure reasons in `usa_independent_video_diagnostic_20261114.json`; the recording has been evaluated even though the qualified final-test protocol remains incomplete. The existing independent-test JSON is a legacy report for a different seed-0 candidate; do not report it as the retained seed-1 or new recovery seed-2 checkpoint's test result.

## Candidate negative-image sources

- [Open Images V7](https://storage.googleapis.com/openimages/web/factsfigures_v7.html) may provide verified plate-absent scenes; use only records with an image-level verified negative label for vehicle registration plate, inspect them manually, and verify each original image license and attribution at the source URL. [Download metadata](https://storage.googleapis.com/openimages/web/download_v7.html).
- [MIO-TCD](https://tcd.miovision.com/challenge/dataset.html) includes fixed-camera US/Canadian traffic scenes, but its CC BY-NC-SA 4.0 license is not suitable for commercial use without a separate rights review.

Neither source replaces negatives recorded at the target access camera. Keep any external-source negatives separate by source group and split them before training or calibration.

