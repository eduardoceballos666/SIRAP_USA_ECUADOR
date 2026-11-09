# SIRAP notebooks

The active detector is RT-DETRv2-S (ResNet-18vd). Fine-tuning uses Transformers/PyTorch and exports OpenVINO IR; inference uses the native Python OpenVINO Runtime. The plate checkpoint `merve/license-plates-rtdetrv2` is listed as Apache-2.0. Dataset and third-party component licenses remain separate.

| Country | Active notebook | Coverage |
|---|---|---|
| Ecuador | [Ecuador backend](ecuador/sirap_backend.ipynb) and [notebook guide](ecuador/README.md) | Ecuador profile, training, and inference workflow |
| United States | [sirap_backend_usa.ipynb](usa/sirap_backend_usa.ipynb) and [USA notebook guide](usa/README.md) | One consolidated English workflow for exploration, Roboflow/COCO data, grouped holdout creation, training, tuning, evaluation, OCR, OpenVINO, and publishing |

The former USA notebooks for exploration, preprocessing, modeling, optimization, evaluation, OCR, and multi-seed validation have been merged into the consolidated USA notebook and removed from the active folder. Their prior revisions remain in Git history.

For USA training, add `ROBOFLOW_API_KEY` to Colab Secrets before downloading the default Roboflow dataset. The consolidated USA notebook includes both a disabled-by-default Cloudflare camera test and an on-site OpenVINO edge runner. The remote test reads `CAMARA_URL` and `CAMARA_TOKEN` from Colab Secrets. The local runner saves confirmed OCR events without video; its optional uploader stays disabled because the current API has no dedicated machine-to-machine USA event route. Do not automate the interactive operations endpoint. The notebook also supports full-scene USA annotations through [the COCO dataset guide](../datasets/usa/detection_coco/README.md) and [the converter](../scripts/usa_annotations_to_coco.py).

The USA test builder creates a grouped internal holdout with at least 400 images from the selected source export. It is not an external dataset; vehicle/session separation is guaranteed only when those identifiers are provided. The model test is locked until the checkpoint and threshold are selected using validation and frozen.

Ecuador and USA models, datasets, OCR inputs, and metrics must remain separate. The removed video ground-truth experiment is not part of the active notebook workflows.
