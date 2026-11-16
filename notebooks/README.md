# SIRAP notebooks

The application runs native OpenVINO inference with the USA-trained seed-2 RT-DETRv2-S detector and verified global serial OCR weights. Ecuador and USA share those frozen weights; country-specific rules interpret OCR differently. Model selection, datasets, interpretation and evaluation evidence must retain their own identities.

| Country | Active notebook | Coverage |
|---|---|---|
| Ecuador | [sirap_backend_ecuador.ipynb](ecuador/sirap_backend_ecuador.ipynb) and [guide](ecuador/README.md) | Consolidated Ecuador training, OCR, evaluation and optional camera workflow |
| United States | [sirap_backend_usa.ipynb](usa/sirap_backend_usa.ipynb) and [guide](usa/README.md) | Frozen seed-2 application pipeline, at most eight reviewed photos, isolated API access-flow checks and optional separate research |

The USA diagnostic keeps detection at **0.70** and minimum OCR character probability at **0.94**. It verifies issuing state + serial and reuses the actual application provider and HTTP handlers. Its eight-photo path does not download a training dataset or request a 400-image review. Set `PILOT8_ROOT` to the private reviewed bundle and enable the pilot and software-check switches; see the USA guide for setup and results.

USA camera modes and the generated edge runner are diagnostic only. Their local confirmations cannot authorize a production opening and do not upload to the interactive operations endpoint. USA vehicle lookup uses the local registry; no browser or external vehicle lookup is required.

Research is off by default. Roboflow download requires `ROBOFLOW_API_KEY` in Secrets; grouped internal holdout creation, Optuna and training require explicit research switches. That internal holdout is not independent external evidence. Full-scene conversion is documented in [the COCO guide](../datasets/usa/detection_coco/README.md) and [converter](../scripts/usa_annotations_to_coco.py).

Historical staged USA notebooks and metrics retain their own model identities in Git history. The independent seed-2 test remains unrun pending a separate reviewed source. Reused photo checks, synthetic software tests and previous checkpoints' reports are not substitutes for it. The notebook does not publish model binaries or operational data.

Fine-tuning uses Transformers/PyTorch and exports OpenVINO IR; the application does not need Transformers for inference. Checkpoint, dataset and component licenses remain separate.
