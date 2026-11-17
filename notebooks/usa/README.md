# USA notebook: frozen seed 2 and an eight-photo development check

The active English notebook is [sirap_backend_usa.ipynb](sirap_backend_usa.ipynb). Its diagnostic path reuses the application's **USA pipeline and `/api/recognize` handler**, with the private seed-2 model, detector confidence **0.70**, minimum OCR character probability **0.94**, and issuing **state + serial** identity. It does not retrain or choose a different checkpoint.

## Run the current diagnostic

1. Open the notebook in Colab and run sections 0–2. Setup installs the application's hashed runtime requirements and Tesseract English data. CPU is sufficient; optional training dependencies preserve Colab's CUDA PyTorch.
2. Add `SIRAP_USA_MODEL_TOKEN` to Colab Secrets (or the environment) with read access to `eduardoceballos/SIRAP_USA_seed2`. Alternatively, supply the already verified artifact folders through `SIRAP_USA_DETECTOR_DIR` and `SIRAP_USA_OCR_DIR`. Credentials are never printed or embedded in the notebook.
3. Extract the existing eight-photo package into a private folder containing `originales/` and `referencia_humana_8_fotos.json`; set `PILOT8_ROOT` accordingly. The photo-5 police-car replacement and the reviewed original hashes are retained.
4. Set `RUN_8_IMAGE_PILOT=True` and `RUN_SOFTWARE_FLOW_CHECKS=True` in section 0. Run the remaining cells in order. Section 20 checks at most eight original photos; section 21 separately checks application behavior with synthetic data.

Every original hash and reference box is checked before inference. A scene with an unresolved region is excluded from complete-scene detector counts; illegible real plates remain physical plates without invented text. No additional 400-image review is required for this path.

`RUN_RESEARCH_WORKFLOW=False` prevents automatic dataset downloads, internal holdout construction, Optuna and training. Camera, robustness, latency, manual-crop OCR, publishing and independent-test switches remain off. The saved output records one local execution of all 29 code cells in source order; setup was skipped in an already prepared environment, and Internet sockets were disabled during that validation. Training, cameras and the independent-test branches were not executed.

## Frozen model and application rules

The immutable [selection record](../../models/usa/selected_checkpoint.json) pins repository revision `ceaf7b0c692df45f9692ac0817571ea006dd8c08` and SHA-256 hashes for the native OpenVINO detector, metadata and global serial OCR files. The provider checks them and refuses a mismatched local artifact; it has no seed-1 or general-detector fallback. A runtime profile records configuration availability, not independent performance qualification.

The live and generated edge diagnostics use the same state reader and evidence rules as the application: two distinct frame IDs **and RGB hashes** within 7.5 seconds, fixed confidence settings, and full USA identity. Their confirmations are local diagnostics and cannot authorize a production opening. The edge runner does not upload to `/api/operations`. The application's USA vehicle lookup reads the local registry and J.D. Power's public report (`api/providers/usa_jdpower.py`); these diagnostics do not use it.

Section 21 tests the actual HTTP handlers for current allowlists, state collisions, unknown-state abstention, confidence, frame uniqueness, receipt expiry/replay/ownership, revocation and persistence before actuation. Lists and barrier are synthetic; no operational registry or physical barrier is used.

## Rechecked development results — 16 November 2026

| Check | Result | Scope |
|---|---:|---|
| Original photos / confirmed physical plates | 8 / 13 | Reused human reference; prior prediction exposure |
| Detector true positives / misses / false positives | 8 / 3 / 0 | Seven complete scene references, IoU 0.50, confidence 0.70 |
| Exact serial | 9 / 10 | Matched detections with known serials |
| Exact issuing state | 2 / 9 | Matched detections with known states; seven abstentions, no wrong assigned state |
| Exact state + serial meeting OCR 0.94 | 1 / 9 | Recognition check, not an authorized opening |
| Access operations from the eight photos | 0 | Separate capture session for each still photo |
| Application software flow | Passed | Synthetic tests, separate from model accuracy |

The [aggregate model report](../../results/metrics/usa_seed2_notebook_development.json) includes model hashes, field denominators, packages and descriptive Wilson/image-cluster bootstrap intervals. The [software report](../../results/metrics/usa_seed2_notebook_software_flow.json) describes the isolated rule checks. The local full Python suite passed 142 tests, including notebook and training-constructor compatibility checks. No detector or OCR weight changed.

This small reused pilot does not measure empty-scene false alarms, independent accuracy or physical barrier performance. Serial scores on detected plates are not full-system recall. An independent recording/source with a completed human reference is still required; these eight photos do not supply it.

## Private outputs and independent evaluation

`PILOT8_OUTPUT_DIR/usa_seed2_pilot_private_rows.csv` contains reference/prediction details, omissions and abstentions. It stays outside Git and may be copied to the configured private Drive evaluation folder. Only aggregate JSONs belong in public metrics. `usa_seed2_runtime_profile.json` is a local configuration record and is not a qualification report.

Section 22 stays off until a separate reviewed COCO source and `independence.json` declaration are supplied. Its declaration is not automatic proof of independence. When the eight-photo bundle is available, exact file overlap is rejected. Reports are keyed to this model revision and preserve an attempt marker; historical seed-0/seed-1 reports cannot qualify seed 2. AP uses a separate metric floor of 0.001; operational detection counts remain at 0.70.

## Optional future research

Roboflow/COCO conversion, grouped internal holdout construction, Optuna and three-seed training remain available only after enabling the research switches. The internal 400-image builder is a research option, not the current eight-photo task or an external independent test. Add `ROBOFLOW_API_KEY` to Secrets only if downloading that source.

USA training retains up to 50 epochs, patience 8 and 5% warmup. The training helper accommodates the installed Transformers API and evaluates loss without concatenating variable-length COCO targets. Constructor compatibility was tested without starting a training run. Candidate outputs go to timestamped experiment folders and never replace the frozen runtime automatically.

Code and compact metrics publish through the existing GitHub-to-Space workflow. The notebook never copies private model binaries or credentials into public source.
