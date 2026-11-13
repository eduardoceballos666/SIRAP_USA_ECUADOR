# USA RT-DETRv2-S notebook

The USA workflow is consolidated in one notebook: [sirap_backend_usa.ipynb](sirap_backend_usa.ipynb). It replaces the former staged USA notebooks, whose versions remain available in Git history.

The notebook is written in English and explains each executable section. It covers USA profile inspection, Roboflow download, COCO conversion, grouped data splitting, label review, hyperparameter search, three-seed fine-tuning, OpenVINO inference, threshold calibration, robustness and CPU latency checks, OCR evaluation, end-to-end scene evaluation, one-time detector testing, optional publishing, Cloudflare remote-camera testing, and a generated on-site edge inference runner.

## Model and runtime

- Detector: RT-DETRv2-S with a ResNet-18vd backbone.
- Starting checkpoint: `merve/license-plates-rtdetrv2`, listed as Apache-2.0.
- Fine-tuning: Transformers and PyTorch.
- Inference and detector evaluation: native Python OpenVINO Runtime.
- Input size: 640 pixels.

The checkpoint's published metrics describe its original evaluation data. They are not SIRAP USA results. Dataset terms are separate from the checkpoint license.

## Current validation status (13 November 2026)

The selected candidate is seed 1, chosen by grouped Roboflow validation at mAP50-95 = 0.8321. The current manual full-scene validation has 71 images: 41 with plates and 30 PKLot negatives. At the best observed confidence threshold (0.60), it produced 40 true positives, 3 false positives, and 1 false negative (precision 0.9302; recall 0.9756). This misses the 0.99 target, so the calibration report stores a null threshold and `usable_for_inference: false`. Do not use the checkpoint for live or access decisions.

The 30 PKLot scenes remain validation-only. PKLot is CC BY 4.0 and its official page requests citation; its images come from elevated fixed parking cameras in Brazil, and its dataset card says plates are not distinguishable. They are a limited background check, not evidence of USA gate-camera performance. Before retraining, add separately reviewed, group-disjoint negatives from the target camera to training and validation.

The repository already has `results/metrics/rtdetr_usa_independent_test.json`, but its model-selection record identifies a different seed-0 candidate. Treat it as a legacy artifact, not the final test for the selected seed-1 checkpoint. The selected checkpoint's independent test remains unrun. All training, evaluation, live-camera, metric-publishing, and Space-publishing switches are off by default.

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

Notebook outputs are not embedded in this README. Structured result files are stored under `results/metrics/`. The threshold-calibration JSON currently blocks inference because the 0.99 precision target was not met. The existing independent-test JSON is a legacy report for a different seed-0 candidate; do not report it as the selected seed-1 checkpoint's test result.
