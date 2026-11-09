# USA RT-DETRv2-S notebook

The USA workflow is consolidated in one notebook: [sirap_backend_usa.ipynb](sirap_backend_usa.ipynb). It replaces the former staged USA notebooks, whose versions remain available in Git history.

The notebook is written in English and explains each executable section. It covers USA profile inspection, Roboflow download, COCO conversion, grouped data splitting, label review, hyperparameter search, three-seed fine-tuning, OpenVINO inference, threshold calibration, robustness and CPU latency checks, OCR evaluation, end-to-end scene evaluation, one-time detector testing, and optional publishing.

## Model and runtime

- Detector: RT-DETRv2-S with a ResNet-18vd backbone.
- Starting checkpoint: `merve/license-plates-rtdetrv2`, listed as Apache-2.0.
- Fine-tuning: Transformers and PyTorch.
- Inference and detector evaluation: native Python OpenVINO Runtime.
- Input size: 640 pixels.

The checkpoint's published metrics describe its original evaluation data. They are not SIRAP USA results. Dataset terms are separate from the checkpoint license.

## Dataset and credentials

The default source is Roboflow's **European + USA License plates**, workspace `plateblur`, project `european-usa-license-plates`, version 1, exported as COCO Segmentation. The notebook reads its boxes and maps the three plate labels to one detector class. Add `ROBOFLOW_API_KEY` to Colab Secrets; do not put the key in the notebook or Git.

An earlier inspection reported 13,143 training images, 386 validation images, and 106 test images. The notebook reads the current counts from the downloaded annotation files. It builds a grouped held-out test with at least 400 images by combining held-out source groups with additional groups reserved from training. This is an internal holdout from the same export, not an external dataset. Without vehicle/session IDs in `source_group_manifest.csv`, grouping is limited to filename families and exact-file hashes.

For complete vehicle or access-lane scenes, the notebook also supports the repository's CSV annotation template and COCO converter. Cropped plate images in `datasets/usa/seg_and_ocr/` are for OCR evaluation; they are not a substitute for full-scene detection data.

## Recommended run

Use a Colab GPU for training. The final recipe allows up to 50 epochs, early-stopping patience 8, and three seeds. Optuna uses at most eight screening trials of up to 12 epochs each. Expensive run switches are off by default.

Train and select the checkpoint and calibrate the operational threshold using validation only. Record the selected checkpoint and validation evidence, then freeze the model. The notebook blocks the held-out detector evaluation unless the test has at least 400 images, the checkpoint and threshold records match, and no prior final report exists.

## Optional remote-camera workflow

Section 16 of the consolidated notebook can create a token-protected camera bridge for a PC that can reach the camera, then connect through Cloudflare Tunnel. Add CAMARA_URL and CAMARA_TOKEN to Colab Secrets; use CF_ACCESS_CLIENT_ID and CF_ACCESS_CLIENT_SECRET when Cloudflare Access service tokens are configured. The live session is disabled by default and does not make access decisions.

Quick Tunnels are suitable for temporary experiments. Use a named tunnel with Cloudflare Access for a stable remote test. For routine production use, run inference on-site and send only the required recognition events through an authenticated API. Temporary CSV, JSON, and optional video outputs are written under /content/SIRAP_workspace/live_camera/ and should not be committed to the public repository.

## Results

No training or evaluation metrics are embedded yet. When run, the notebook saves split audits, trial and three-seed validation results, the selected training manifest, threshold calibration, robustness and latency diagnostics, OCR results, end-to-end results, and the final detector report under `results/metrics/` or the generated dataset folder. The final detector report is `rtdetr_usa_independent_test.json`; evaluate it once after model selection is complete.
