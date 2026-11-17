# SIRAP Backend Ecuador — Notebook guide / Guía del notebook

[English](#english) · [Español](#español)

**Notebook:** [sirap_backend_ecuador.ipynb](sirap_backend_ecuador.ipynb) · [Open in Google Colab / Abrir en Google Colab](https://colab.research.google.com/github/eduardoceballos666/SIRAP_USA_ECUADOR/blob/main/notebooks/ecuador/sirap_backend_ecuador.ipynb)

This guide describes the **actual code**, including its demonstration overrides, in the notebook reviewed at [commit `678356e`](https://github.com/eduardoceballos666/SIRAP_USA_ECUADOR/commit/678356ed403996e1deca4fa5f05cbf5df9461abc) on November 17, 2026: **92 cells, including 53 code cells**. This README update does not execute or change the notebook.

Esta guía describe el **código real**, incluidas sus modificaciones de demostración, del notebook revisado en el [commit `678356e`](https://github.com/eduardoceballos666/SIRAP_USA_ECUADOR/commit/678356ed403996e1deca4fa5f05cbf5df9461abc) el 17 de noviembre de 2026: **92 celdas, incluidas 53 de código**. Esta actualización del README no ejecuta ni modifica el notebook.

## English

### Purpose and current state

The notebook brings together the Ecuador license-plate workflow: dataset inspection, OCR label review, optional RT-DETRv2 training and recovery, OpenVINO inference, COCO evaluation, an experimental authorization rule, video processing, vehicle/owner lookups, live cameras, timing and optional model publication.

Its real inference route is **image → plate detector → plate crop → OCR → Ecuador normalization → confidence/list decision → CSV records**. The detector uses Transformers/PyTorch for training and native OpenVINO for inference. OCR uses `fast-plate-ocr` with the `cct-s-v2-global-model` ONNX artifact. The notebook imports the reusable `USAPipeline` class but configures its country and plate patterns for Ecuador; its class name does not establish where the detector was trained.

**The current file mixes real implementation with simulation and manual overrides.** The opening description still says execution flags are disabled, but later cells change that behavior. Read the control table and the following evidence notes before using **Run all**:

| Current code or artifact | What it actually means |
|---|---|
| A cell after model loading forces `MODEL_IS_COUNTRY_FINETUNED=True` and can instantiate `MockDetector`. | The flag alone does not prove that an Ecuador model was loaded. The mock returns a fixed box and score rather than running a neural detector. |
| An extra cell in 5.3 writes dummy validation predictions and replaces `calibrate_from_validation_cache` with a lambda. | It returns predefined counts and forces `usable_for_inference=True`; this is simulated calibration and bypasses the real data-support checks. |
| The current 5.4 writes a predefined report with precision/recall `1.0` and `ap=0.95`. | These values are hard-coded. That cell does not run COCO evaluation or enforce the earlier frozen-test plan. It deletes an existing report at the same path before writing. |
| The video cell creates a black sample video when the configured file is missing. | That file is a synthetic workflow input, not independent Ecuador video evidence. |
| Later cells copy a training manifest and set its `country` field to `ecuador`. | Editing metadata does not retrain weights or demonstrate Ecuador provenance. |
| The published Ecuador bundle in the reviewed snapshot contains an 8-byte XML and a 5-byte BIN. Its manifest references a USA dataset and USA seed-1 training paths. | These are placeholder-sized files, not a usable trained OpenVINO detector. A JSON field saying `passed` does not replace a successful model load and measured verification. |
| Extra SAVH cells write `ok` into several review rows. | They programmatically confirm suggestions; running them does not constitute an independent visual review. |

Consequently, saved outputs from these simulated branches must not be presented as detector accuracy, operational calibration, genuine model latency or proof of Ecuador training. The notebook records experimental access decisions; it contains no physical barrier actuator.

### Sections and subsections

#### 0. Environment, preservation and persistence

- **0.0 — Preserve the original runtime.** A standalone standard-library cell looks for existing seed-2 Transformers/run weights or an OpenVINO BIN before package installation or Git updates. When present, it mounts Drive and copies explicit model, run and aggregate-metric directories into a uniquely named backup. It verifies SHA256 checksums, reports missing directories and does not merge snapshots. If it finds no weights, it says that no model backup was created.
- **0.1 — Dependencies.** Installs Transformers `5.23.0`, OpenVINO `2026.4.1` and the dataset, COCO, image, plotting, CSV and download dependencies. Colab's CUDA-enabled PyTorch is retained. Intel CPUs select the OCR package with the OpenVINO Execution Provider; other CPUs use ONNX Runtime CPU. A requested runtime restart should follow a successful backup.
- **0.2 — Repository and controls.** Clones this repository, or fetches and fast-forwards an existing clone without resetting local work. Loads `config/countries/ecuador.yaml`, creates working/result directories, defines thresholds and stage flags, mounts Drive when enabled, and creates an experiment ID. It also reloads selected helper modules in a reused runtime. An added cell immediately enables inference again.
- **0.3 — OCR and output helpers.** Defines the OCR reader, checks the selected ONNX provider, copies individual files to Drive, creates verified directory snapshots, and offers explicit publication of selected aggregate metric files. Defining the reader does not itself recognize an image. Single-file copying can replace the selected destination; the experiment-directory backup helper instead creates unique snapshots.
- **0.4 — Backup/recovery helpers.** `backup_ecuador_experiment()` saves explicit model, run and metric directories. `verify_backup()` checks file integrity; `restore_backup()` requires a new destination. These experiment snapshots do not include the separate owner, authorization or camera-session CSV directories. Camera sessions have their own persistence path.

#### 1. Data and exploratory analysis

- **1.1 — Detector inputs and experiment settings.** Selects the Ecuador COCO root and model/run directories, including environment overrides. The initial plate checkpoint is `merve/license-plates-rtdetrv2`, pinned to revision `ed6be0966b37eb0e78fe3680e6485c788a0d61f1`. Settings are 640-pixel padded inputs, a maximum of 30 epochs, patience 8, batch size 4 and seed 2. The AP score floor is `0.001`.
- **1.2 — Dataset audit.** Checks COCO labels, positive boxes, image dimensions, file hashes and groups shared across splits. Builds the train/validation/test dataset objects, displays counts and a dataset fingerprint, and sets `DATA_READY` only when the audit succeeds.
- **1.3 — SAVH Guayaquil OCR crops.** Extracts the versioned ZIP into the local workspace after checking that ZIP paths stay inside the extraction directory. Reads `ground_truth.csv`, assigns review-row numbers and displays available crop counts. If the archive is absent, this part is skipped. These are cropped plates for OCR review, not complete detector scenes.
- **1.4 — Additional Ecuador scenes.** An optional Roboflow COCO download uses `ROBOFLOW_API_KEY` and creates a review table with blank group labels. Downloading does not automatically add data to training. A separate import requires a reviewed source manifest with country, license, plate classes, negative-scene and group decisions. The importer rejects unknown classes and conflicting exact duplicates, joins exact/near duplicates before grouped splitting, excludes the known six photos from a fresh study, writes a separate dataset and provenance report, and requires a new audit. The import is disabled in the reviewed notebook.

The included development dataset is **six Ecuador images with 11 plate boxes**: four training images/nine boxes, one validation image/one box and one development-test image/one box. Both views of the same truck stay in training. All six scenes contain plates; they cannot measure false-positive behavior on real negative scenes.

#### 2. Preprocessing and OCR reference review

- **2.1 — Ecuador plate normalization.** Removes separators and the printed `ECUADOR` header, searches OCR text segments, applies position-dependent letter/digit confusion corrections with at most two changes, and checks the configured three-letter plus three-/four-digit patterns. Display/storage formatting uses `XXX-0000`; an older three-digit serial receives a leading zero. It also defines minimum-character OCR confidence and runs local normalization assertions.
- **2.2 — Reviewed SAVH reference.** Reads the versioned review CSV by default, or an explicitly configured Google Sheet. Applies confirmed, corrected and excluded responses, records unconfirmed suggestions separately, groups identical images by hash and propagates the selected response within each duplicate group. Writes the review snapshot and corrected reference, displays status counts and pending images, and exports unique accepted labels for a possible future OCR split.
- **Added review cells.** Display pending cases and the doubtful case, then write `ok` for review row `7` and rows `1, 4, 5, 10, 11, 12, 15` in the local clone's review CSV and rebuild the reference. Inspect the images and intended transcriptions before running these write cells. Their programmatic confirmations must not be counted as new independent human evidence. They do not by themselves publish the CSV to GitHub.

The notebook prepares OCR references and runs normalization/extraction checks. It does not train a separate OCR model or turn these crops into a detector test set.

#### 3. Modeling, model identity and experimental decision rule

- **3.1 — Optional real detector training.** Requires an audited dataset and new model/run directories. Uses RT-DETRv2 through Transformers, learning rate `5e-5`, weight decay `1e-4`, a 5% warmup, CUDA mixed precision when available, early stopping and selection by the lowest validation loss; test images are not used for selection. A mapping-aware Trainer reloads the best checkpoint through the official key conversion and copies its tensors strictly. The save/reload helper checks exact tensor equality. Source weights are backed up before OpenVINO export; the export records resize rounding, padded-box coordinates and FP32 inference precision. PyTorch/OpenVINO preprocessing, masks, logits and boxes are compared on validation, and artifacts are backed up on exit. This stage is initially disabled.
- **3.2 — Candidate and camera checks.** Defines the candidate directories and functions that require an Ecuador manifest, bundle files and a validation verification report tied to XML/BIN/runtime-JSON hashes. Live calibration must name Ecuador, contain a finite threshold, declare itself usable and match the selected bytes. Such checks bind files to reports; they cannot make manually fabricated reports or relabeled weights authentic.
- **3.3 — Authorization CSV.** Loads `authorized_plates.csv`, normalizes its entries and creates an empty file if absent. It also defines an edit-distance check for possible one-character OCR errors.
- **3.4 — Decision labels.** Missing plates, non-finite confidence or scores below the detector/OCR thresholds produce `VERIFICACION_MANUAL`. An exact authorized-list match produces `AUTORIZADO`; a match within one edit requires manual review; other readings produce `NO_REGISTRADO`. These are notebook labels, not commands to open a gate.
- **3.5 — Recover without retraining.** Loads an actual existing Ecuador Transformers checkpoint and its original training manifest. Saves a new candidate, verifies loading and tensor roundtrip, exports IR, compares it with PyTorch on validation and backs up the result. It rejects a source manifest that identifies another country. `RECOVERY_MANIFEST_PATH` can identify an original manifest stored separately. This recovery route is initially disabled.

#### 4. Model loading and the mock fallback

The main cell can restore an explicitly selected Drive IR, prioritize `VERIFIED_IR_DIR`, or choose the local/published Ecuador candidate. It calls the candidate checks before creating a CPU `PlateDetector` and the Ecuador OCR pipeline. Separate switches allow an initial-model technical smoke check or a shared-model route; neither establishes Ecuador fine-tuning.

**The following added cell changes the behavior:** it forces the fine-tuned flag, tries another direct load, and catches any error by installing `MockDetector`, which returns a fixed box with confidence `0.85`. This can keep later workflow cells running, but it does not repair missing or invalid model weights. Check the actual detector object and provenance, not just `MODEL_IS_COUNTRY_FINETUNED`.

#### 5. Detector checks, COCO and calibration

- **5.1 — Smoke check.** Runs the active detector on a blank image to check its interface. A successful call is not an accuracy measurement; a mock can also return a result.
- **5.2 — Real COCO validation route.** When enabled, requires the audited data and verified candidate, then calls `evaluate_detector` on validation. Separates AP50–95/AP50/AP75 from TP/FP/FN, precision, recall and F1 at the operating confidence. Records maximum score and accepted prediction count, caches predictions with image/annotation/model/runtime hashes, preserves existing report paths and backs up the result.
- **5.3 — Real threshold-sweep route.** The original cell uses only the validation cache. Its default support requirements are 50 validation images, 25 positive, 25 real negative and five documented groups; target precision is at least `0.95`, recall at least `0.80`, and negative-scene false-positive rate at most `0.05`. These configurable research safeguards are not statistical certification. A tiny development set cannot enable a real operational threshold. A frozen plan binds the candidate, dataset, geometry verification, calibration and thresholds before test.
- **5.3 — Added simulation override.** A later cell overwrites the prediction cache with dummy data, deletes an existing sweep file, monkey-patches the calibration function and writes a live calibration record marked usable. Its counts and `0.70` threshold are predefined. It can also affect subsequent calls in the same runtime until the module is reloaded.
- **5.4 — Current simulated test.** The current cell enables test, deletes a same-name test report and writes fixed counts/precision/recall/AP. It does not call the real evaluator or validate the frozen plan. It is a demonstration report, not held-out COCO evidence.

AP uses many confidence levels above the low score floor; TP/FP/FN describe one selected operating confidence. Nonzero AP can coexist with zero accepted detections at `0.70`. Separately, hard-coded metrics are not measured AP at any threshold. The already-inspected one-image development test cannot become a fresh independent test by renaming it.

#### 6. Video, CSV records and optional external lookups

- **6.1 — Video input.** Selects `SIRAP_ECUADOR_VIDEO_PATH` or the repository demo path. The current `DOWNLOAD_DEMO_VIDEO=True` branch requires a nonempty `VIDEO_ID` when video is enabled at that point. For an existing local file, disable that download branch.
- **6.2 — Sampling.** Uses one sampled frame every 2.5 seconds, with a maximum of eight analyzed frames.
- **6.3 — CSV and SRI.** Maintains session readings and SRI/owner tables under `WORK_DIR/registros_csv`. Authorization comes only from the local plate list. The optional SRI verifier queries vehicle details and, when enabled, registration charges with a single background worker, a 24-hour cache, a two-second minimum interval and a 15-second request timeout. `SRI_VERIFICAR=False` in the current file. SRI results enrich records; they do not automatically authorize a vehicle. CSV-to-GitHub synchronization is disabled in this store.
- **6.4 — Public owner name.** The current `PROPIETARIO_WEB_ACTIVO=True` cell prepares Playwright/Chromium. The lookup targets the visible `Nombre` field on the configured EcuadorLegalOnline page, rejects hidden placeholders and checks the returned plate. It records query outcomes, current names and ownership-name changes in local CSVs. Requests run one at a time, with a 12-second interval, 25-second page timeout and cache age zero. Page restrictions, missing results or browser errors can prevent enrichment; the code does not obtain restricted identifiers or paid reports.
- **6.5 — Local extraction checks.** Tests name extraction against sample text, including rejection of masked names, without contacting the website. Also previews the owner tables. Helper functions can explicitly query a plate or fill missing names in registered records.
- **6.6 — Current video execution.** Sets `RUN_VIDEO=True`, patches the mock box to include an `area` field and creates a 50-frame black MP4 if the input is missing. Samples the selected video, recognizes plates, records decision labels, submits enabled lookups, waits for their completion and writes prediction/enriched CSVs. With a mock detector or generated black video, this is workflow simulation, not end-to-end recognition evidence.

#### 7. Live camera and on-site inference

- **7.1 — Camera-PC bridge generator.** Writes `live_camera/bridge_camera.py` and optionally persists the script. The generated server reads a USB/URL/video source and exposes `/snapshot.jpg`, `/video` and `/status`, protected by `X-Camera-Token`. It creates or reuses a local token file. Generating the script does not launch the camera PC server or create a Cloudflare tunnel; those are separate setup steps.
- **7.2 — Reader and recognition setup.** Reads camera and optional Cloudflare Access secrets. Supports automatic, MJPEG, snapshot or OpenCV capture, a latest-frame buffer, startup/stale-frame limits and a calibrated Ecuador pipeline. Defaults include a 120-second session, processing at most five frames/second, up to five candidates and preview at two frames/second.
- **7.3 — Connectivity check.** A five-second test measures incoming frames, approximate camera FPS and resolution and shows the last frame, without requiring OCR/model inference. Its actual switch is `RUN_CAMERA_CONNECTION_CHECK=True` to run; one printed disabled message incorrectly says to set it to `False`.
- **7.4 — Live session.** Currently sets `LIVE_ENABLED=True`. With configured camera access and passing model/calibration checks, records a plate after two accepted observations within three seconds, with a 15-second duplicate cooldown. Writes a session `readings.csv`, `summary.json` and optional `annotated.mp4`, and persists the session when enabled. It skips processing when camera access is absent. The simulated calibration record is not a valid basis for operational use.
- **7.5 — On-site runner generator.** Writes `edge_inference_ecuador.py` for recognition on the camera PC, keeping images there. It accepts a source, actual IR, calibration file, OCR threshold, timing and confirmation parameters, saves a local CSV, and optionally displays a preview. `--upload-events` sends confirmed plate text and metadata only when a dedicated HTTPS endpoint and bearer token are configured. Event upload is optional and does not implement a physical gate actuator.

#### 8. Detector latency

The current cell sets `RUN_LATENCY_TEST=True`, caches up to 200 validation images, performs ten warmup calls and at least 30 timed detector calls. It reports median, p95, p99 and FPS derived from median latency, plus image count, CPU, size and threshold, in `openvino_ecuador_latency.json`.

It measures the **active detector call**, not the full camera/OCR/lookup workflow. If `MockDetector` is active, these timings measure the mock and must not be described as OpenVINO model performance. Repeated images support timing only, not additional statistical accuracy samples.

#### 9. Manifest inspection and publication

Diagnostic cells list the model directory, search `/content` for `sirap_training.json`, copy a Drive manifest, display it and explicitly change its country to Ecuador. These cells modify metadata, not model training history.

The publication cell currently sets `PUBLISH_IR_TO_SPACE=True`. After its file/report and staged-Git checks, it stages the IR at `models/ecuador/detector/rtdetrv2_s/openvino/` and calls `publish_detector_ir`. It can replace the target directory when copying another candidate. Publication needs a GitHub token, and repository automation can synchronize the bundle to the Space. Application model configuration is separate. Do not publish the current placeholders or treat relabeled manifests as verified Ecuador weights.

#### 10. Annotation preview

Currently enabled with `REVIEW_COCO_TRAIN_VALID=True`. Draws the versioned ground-truth rectangles on all training and validation images, prints filename/group information and displays resized previews. It does not display test images, change bounding boxes or measure model accuracy.

### Controls: initial settings versus later assignments

Python uses the most recently executed assignment. Editing only 0.2 does not disable a later cell that sets a flag again. The table describes source assignments; whether a later action completes depends on prerequisites and cell execution order.

| Control | Initial/configured value | Later behavior in the current file |
|---|---|---|
| `RUN_TRAIN_ECUADOR` | `False` | Real training remains opt-in. |
| `RUN_CHECKPOINT_RECOVERY` | `False` | Real recovery remains opt-in. |
| `USE_ECUADOR_TRAINED_MODEL`, `USE_BASE_MODEL_FOR_SMOKE`, `RESTORE_ECUADOR_IR_FROM_DRIVE` | `True`, `False`, `False` | Select the Ecuador route, initial-model smoke route or explicit Drive restore. |
| `FREEZE_DEVELOPMENT_TEST_PLAN` | `False` | The real sweep can freeze a diagnostic development plan when explicitly enabled; it does not validate the simulated test. |
| `RUN_COCO_VALIDATION` | `False` | Real validation remains opt-in. |
| `RUN_INFERENCE` | `False` | Extra cells set it to `True`; the fallback can be a mock. |
| `RUN_THRESHOLD_CALIBRATION` | `False` | An added cell sets it to `True` and installs simulated calibration. |
| `RUN_FINAL_TEST_EVALUATION` | `False` | Current 5.4 sets it to `True` and writes a simulated report. |
| `RUN_VIDEO` | `False` | 6.6 sets it to `True`; may create a black video. |
| `PERSIST_OUTPUTS_TO_DRIVE` | `True` | Setup mounts Drive and enabled persistence writes there. |
| `RUN_DOWNLOAD_EXTRA_ECUADOR_DATA`, `RUN_IMPORT_REVIEWED_ECUADOR_DATA` | `False` | Extra data requires explicit download/review/import. |
| `SRI_VERIFICAR` | `False` | SRI queries remain disabled unless changed. |
| `PROPIETARIO_WEB_ACTIVO` | `True` in 6.4 | Prepares Chromium; submitted plate lookups can use the website. |
| `RUN_CAMERA_CONNECTION_CHECK` | `False` | Set to `True` for the five-second connection test. |
| `LIVE_ENABLED` | `True` in 7.4 | Attempts a live session when camera inputs and checks permit it. |
| `RUN_LATENCY_TEST` | `True` in 8 | Times the current detector, including a mock if present. |
| `PUBLISH_SMALL_METRICS_TO_GITHUB` | `False` | Aggregate-metric publication helper is disabled. |
| `PUBLISH_IR_TO_SPACE` | `True` in 9 | Can publish the IR when credentials and checks permit it. |
| `REVIEW_COCO_TRAIN_VALID` | `True` in 10 | Displays annotated train/validation images. |

Initial demonstration confidence is **detector `0.70` / OCR `0.94`**. Neither the fixed values nor the simulated calibration establish Ecuador operating accuracy.

### Files, credentials and execution

| Purpose | Location or output |
|---|---|
| Country configuration | [`config/countries/ecuador.yaml`](../../config/countries/ecuador.yaml) |
| Detector scenes and annotations | [`datasets/ecuador/detection_coco/`](../../datasets/ecuador/detection_coco/) |
| Additional-source registry/template | [`detection_sources.json`](../../datasets/ecuador/detection_sources.json), [`detection_sources.example.json`](../../datasets/ecuador/detection_sources.example.json) |
| SAVH crops and review CSV | `datasets/ecuador/savh/` |
| Default local workspace | `/content/SIRAP_workspace/ecuador/` |
| New training candidates and runs | `WORK_DIR/models/detector/rtdetrv2_s/<EXPERIMENT_ID>/`, `WORK_DIR/runs/rtdetrv2_s/<EXPERIMENT_ID>/` |
| Recovered candidates | `WORK_DIR/recovered_models/<EXPERIMENT_ID>/` |
| Corrected OCR reference | `WORK_DIR/ocr/savh_ground_truth_corregido.csv` |
| Authorization list | `WORK_DIR/authorized_plates.csv` |
| Video output and session tables | `WORK_DIR/decisions_rtdetr_ecuador.csv`; `WORK_DIR/registros_csv/{lecturas,consultas_sri,propietarios,historial_propietarios,consultas_propietario,lecturas_enriquecidas}.csv` |
| Aggregate evaluation, predictions, calibration and latency | `results/ecuador/metrics/` |
| Camera scripts and local sessions | `WORK_DIR/live_camera/` |
| Default Drive root | `/content/drive_sirap/MyDrive/SIRAP_USA_ECUADOR/` |
| Verified experiment snapshots | `DRIVE_ROOT/backups/ecuador/`; camera sessions use a separate private camera path |
| Staged/published IR | `models/ecuador/detector/rtdetrv2_s/openvino/` |

Environment overrides include `SIRAP_REPO_ROOT`, `SIRAP_ECUADOR_WORK_DIR`, `SIRAP_ECUADOR_COCO_DIR`, `SIRAP_ECUADOR_MODEL_DIR`, `SIRAP_ECUADOR_RUN_DIR`, `SIRAP_ECUADOR_EXPERIMENT_ID`, `SIRAP_ECUADOR_RECOVERY_CHECKPOINT`, `SIRAP_ECUADOR_RECOVERY_MANIFEST`, `SIRAP_ECUADOR_VERIFIED_IR` and `SIRAP_ECUADOR_VIDEO_PATH`. The emergency cell separately supports `SIRAP_ECUADOR_EXISTING_MODEL_DIR` and `SIRAP_ECUADOR_EXISTING_RUN_DIR`.

| Optional operation | Required access/configuration |
|---|---|
| Drive backups | Colab Google Drive authorization. |
| Roboflow export | `ROBOFLOW_API_KEY` in Colab Secrets or the supported environment. |
| Model/metric publication | `GITHUB_TOKEN` with the required repository write access. |
| Shared protected-model route | `SIRAP_USA_MODEL_TOKEN`, if required by that configured source. |
| Cloud camera | `CAMARA_URL`, `CAMARA_TOKEN`; optionally `CF_ACCESS_CLIENT_ID`, `CF_ACCESS_CLIENT_SECRET`. |
| Google Sheet review | Enable `USE_GOOGLE_SHEET`, configure `REVIEW_SHEET_ID` and the Google/gspread dependencies and authorization. The default uses the versioned CSV. |
| On-site event upload | `SIRAP_EDGE_EVENTS_URL`, `SIRAP_EDGE_EVENTS_TOKEN` and `--upload-events`. |

For a genuine experiment, preserve any original runtime with 0.0 first. Review every later enabling assignment, skip the mock/calibration/test and automatic-review override cells, and disable publication while preparing inputs. Then audit real data, recover or train actual Ecuador weights, verify the IR, run real validation and the unmodified calibration helper, freeze the candidate and run an actual held-out evaluator. **The current 5.4 must be replaced by a real evaluation route before it can provide test evidence.** Keep operational CSVs and camera recordings out of public aggregate-metric publication.

Historical measured results and warnings from the earlier six-photo run remain in the [execution archive](../../results/ecuador/metrics/archive/20261116_six_photo_user_run/). The [implementation verification report](../../results/ecuador/metrics/recovery_implementation_verification_20261117.json) concerns public reference weights; it does not validate the later placeholder bundle or simulated outputs.

## Español

### Propósito y estado actual

El notebook reúne el flujo ecuatoriano de reconocimiento de placas: inspección de datos, revisión de etiquetas OCR, entrenamiento y recuperación opcionales de RT-DETRv2, inferencia con OpenVINO, evaluación COCO, una regla experimental de autorización, procesamiento de video, consultas de vehículo/propietario, cámaras en vivo, medición de tiempos y publicación opcional del modelo.

Su ruta real de inferencia es **imagen → detector de placa → recorte → OCR → normalización ecuatoriana → decisión por confianza/lista → registros CSV**. El detector usa Transformers/PyTorch para entrenar y OpenVINO nativo para inferencia. El OCR usa `fast-plate-ocr` con el artefacto ONNX `cct-s-v2-global-model`. Se reutiliza la clase `USAPipeline`, configurada con el país y los patrones de Ecuador; el nombre de esa clase no demuestra dónde se entrenó el detector.

**El archivo actual mezcla implementación real con simulaciones y modificaciones manuales.** La introducción todavía indica que las banderas de ejecución están desactivadas, pero celdas posteriores cambian ese comportamiento. Antes de usar **Ejecutar todo**, revisa la tabla de controles y estas observaciones:

| Código o artefacto actual | Qué significa realmente |
|---|---|
| Una celda posterior a la carga fuerza `MODEL_IS_COUNTRY_FINETUNED=True` y puede crear `MockDetector`. | La bandera no demuestra que se haya cargado un modelo ecuatoriano. El detector simulado devuelve una caja y confianza fijas, sin ejecutar una red neuronal. |
| Una celda adicional de 5.3 escribe predicciones ficticias y sustituye `calibrate_from_validation_cache` por una función lambda. | Devuelve conteos predefinidos y fuerza `usable_for_inference=True`; es calibración simulada que omite las comprobaciones reales de suficiencia de datos. |
| La sección 5.4 actual escribe un informe predefinido con precisión/recall `1.0` y `ap=0.95`. | Esos valores están escritos en el código. La celda no ejecuta la evaluación COCO ni exige el plan de test previamente congelado. Elimina el informe existente en esa ruta antes de escribir. |
| La celda de video crea un video negro si falta el archivo configurado. | Es una entrada sintética para probar el flujo, no evidencia de un video independiente de Ecuador. |
| Celdas posteriores copian un manifiesto de entrenamiento y cambian su campo `country` a `ecuador`. | Cambiar metadatos no reentrena pesos ni demuestra procedencia ecuatoriana. |
| El paquete ecuatoriano publicado en la versión revisada contiene un XML de 8 bytes y un BIN de 5 bytes. Su manifiesto menciona un dataset de USA y rutas de entrenamiento de USA con semilla 1. | Son archivos de tamaño propio de marcadores de posición, no un detector OpenVINO entrenado y utilizable. Un campo JSON que diga `passed` no sustituye una carga correcta ni una verificación medida. |
| Celdas adicionales de SAVH escriben `ok` en varias filas de revisión. | Confirman sugerencias mediante código; ejecutarlas no constituye una revisión visual independiente. |

Por tanto, las salidas guardadas de estas ramas simuladas no deben presentarse como exactitud del detector, calibración operativa, latencia real del modelo ni prueba de entrenamiento con Ecuador. El notebook registra decisiones experimentales de acceso; no contiene un actuador de barrera física.

### Secciones y subsecciones

#### 0. Entorno, conservación y persistencia

- **0.0 — Conservar el runtime original.** Una celda independiente, basada en la biblioteca estándar, busca pesos Transformers/de ejecución de semilla 2 o un BIN de OpenVINO antes de instalar paquetes o actualizar Git. Si los encuentra, monta Drive y copia directorios explícitos de modelos, ejecuciones y métricas agregadas a un respaldo con nombre único. Verifica SHA256, informa directorios faltantes y no mezcla respaldos. Si no encuentra pesos, indica que no se creó un respaldo del modelo.
- **0.1 — Dependencias.** Instala Transformers `5.23.0`, OpenVINO `2026.4.1` y dependencias de datasets, COCO, imágenes, gráficos, CSV y descargas. Conserva el PyTorch con CUDA de Colab. En CPU Intel selecciona el paquete OCR con OpenVINO Execution Provider; en otras CPU usa ONNX Runtime CPU. Si se solicita reiniciar el runtime, primero debe existir un respaldo correcto.
- **0.2 — Repositorio y controles.** Clona este repositorio o descarga cambios y avanza una copia existente mediante fast-forward, sin restablecer el trabajo local. Lee `config/countries/ecuador.yaml`, crea directorios de trabajo/resultados, define umbrales y banderas, monta Drive si está habilitado y genera un identificador de experimento. También recarga ciertos módulos auxiliares en un runtime reutilizado. Una celda agregada inmediatamente después vuelve a habilitar la inferencia.
- **0.3 — OCR y funciones de salida.** Define el lector OCR, comprueba el proveedor ONNX, copia archivos individuales a Drive, crea respaldos verificados de directorios y permite publicar explícitamente métricas agregadas seleccionadas. Definir el lector no reconoce imágenes por sí solo. La copia de un archivo individual puede reemplazar el destino elegido; el respaldo de directorios del experimento crea nombres únicos.
- **0.4 — Funciones de respaldo y recuperación.** `backup_ecuador_experiment()` guarda directorios explícitos de modelos, ejecuciones y métricas. `verify_backup()` comprueba integridad y `restore_backup()` exige un destino nuevo. Estos respaldos del experimento no incluyen los directorios separados de CSV de propietarios, autorizaciones o sesiones de cámara. Las sesiones de cámara tienen su propia ruta de persistencia.

#### 1. Datos y análisis exploratorio

- **1.1 — Entradas del detector y configuración.** Selecciona la raíz COCO de Ecuador y las rutas de modelos/ejecuciones, con opciones de configuración mediante variables de entorno. El checkpoint inicial es `merve/license-plates-rtdetrv2`, fijado a la revisión `ed6be0966b37eb0e78fe3680e6485c788a0d61f1`. Usa entradas de 640 píxeles con relleno, máximo 30 épocas, paciencia 8, batch 4 y semilla 2. El límite inferior de confianza para AP es `0.001`.
- **1.2 — Auditoría del dataset.** Comprueba etiquetas COCO, cajas positivas, dimensiones, hashes y grupos compartidos entre particiones. Construye los objetos train/validación/test, muestra conteos y la huella del dataset y activa `DATA_READY` sólo si la auditoría termina correctamente.
- **1.3 — Recortes OCR de SAVH Guayaquil.** Extrae el ZIP versionado al área local después de comprobar que sus rutas no salgan del directorio de extracción. Lee `ground_truth.csv`, asigna números de fila para revisión y muestra conteos. Si falta el archivo, omite esta parte. Son recortes de placas para OCR, no escenas completas del detector.
- **1.4 — Escenas adicionales de Ecuador.** La descarga opcional COCO de Roboflow usa `ROBOFLOW_API_KEY` y crea una tabla de revisión con los grupos por completar. Descargar no incorpora automáticamente imágenes al entrenamiento. Una importación separada exige un manifiesto revisado con país, licencia, clases de placas, negativos y grupos. El importador rechaza clases desconocidas y duplicados exactos con etiquetas contradictorias, agrupa duplicados exactos/casi idénticos antes de dividir, excluye las seis fotos conocidas de un estudio nuevo, crea un dataset separado con procedencia y exige repetir la auditoría. La importación está desactivada en el notebook revisado.

El dataset de desarrollo incluido contiene **seis imágenes ecuatorianas con 11 cajas de placas**: cuatro imágenes/nueve cajas de entrenamiento, una imagen/una caja de validación y una imagen/una caja de test de desarrollo. Las dos vistas del mismo camión permanecen en entrenamiento. Todas las escenas contienen placas; no permiten medir falsos positivos en escenas negativas reales.

#### 2. Preprocesamiento y revisión de la referencia OCR

- **2.1 — Normalización de placas ecuatorianas.** Elimina separadores y el encabezado impreso `ECUADOR`, busca segmentos del texto OCR, aplica correcciones letra/dígito según posición con un máximo de dos cambios y comprueba los patrones configurados de tres letras más tres/cuatro dígitos. Para mostrar/guardar usa `XXX-0000`; los seriales antiguos de tres dígitos reciben un cero inicial. Define confianza OCR por el carácter menos confiable y ejecuta pruebas locales de normalización.
- **2.2 — Referencia SAVH revisada.** Lee por defecto el CSV versionado, o una hoja de Google configurada expresamente. Aplica respuestas confirmadas, corregidas y excluidas; conserva por separado las sugerencias no confirmadas, agrupa imágenes idénticas por hash y propaga la respuesta elegida dentro de cada grupo. Guarda la copia de revisión y la referencia corregida, muestra conteos y pendientes y exporta etiquetas únicas aceptadas para una futura partición OCR.
- **Celdas de revisión agregadas.** Muestran casos pendientes y el caso dudoso; después escriben `ok` para la fila de revisión `7` y las filas `1, 4, 5, 10, 11, 12, 15` en el CSV de la copia local y reconstruyen la referencia. Revisa las imágenes y transcripciones antes de ejecutar esas celdas de escritura. Sus confirmaciones por código no deben contarse como nueva evidencia humana independiente. No publican el CSV en GitHub por sí solas.

El notebook prepara referencias OCR y ejecuta comprobaciones de normalización/extracción. No entrena un OCR separado ni convierte estos recortes en un test del detector.

#### 3. Modelado, identidad del modelo y regla experimental

- **3.1 — Entrenamiento real opcional.** Exige datos auditados y directorios nuevos de modelo/ejecución. Usa RT-DETRv2 mediante Transformers, tasa de aprendizaje `5e-5`, weight decay `1e-4`, calentamiento del 5%, precisión mixta si hay CUDA, parada temprana y selección por la menor pérdida de validación; no selecciona con test. El Trainer adaptado vuelve a cargar el mejor checkpoint mediante la conversión oficial de nombres y copia estrictamente sus tensores. La función de guardado/recarga comprueba igualdad exacta. Respalda pesos antes de exportar a OpenVINO; la exportación registra redondeo del redimensionado, coordenadas de cajas respecto del relleno y precisión FP32. Compara preprocesamiento, máscaras, logits y cajas PyTorch/OpenVINO en validación y respalda al salir. Esta etapa comienza desactivada.
- **3.2 — Comprobaciones de candidato y cámara.** Define rutas y funciones que exigen manifiesto ecuatoriano, archivos del paquete e informe de verificación en validación vinculado a hashes XML/BIN/JSON de ejecución. La calibración en vivo debe indicar Ecuador, tener umbral finito, declararse utilizable y coincidir con los archivos seleccionados. Estas comprobaciones vinculan archivos con informes; no autentican informes inventados ni pesos cuyo país se cambió manualmente.
- **3.3 — CSV de autorizaciones.** Lee `authorized_plates.csv`, normaliza entradas y crea un archivo vacío si falta. También define la distancia de edición para posibles errores OCR de un carácter.
- **3.4 — Etiquetas de decisión.** Placa ausente, confianza no finita o valores bajo los umbrales de detector/OCR producen `VERIFICACION_MANUAL`. Una coincidencia exacta con la lista produce `AUTORIZADO`; una diferencia de hasta una edición exige revisión manual; las demás lecturas producen `NO_REGISTRADO`. Son etiquetas del notebook, no órdenes para abrir una barrera.
- **3.5 — Recuperar sin reentrenar.** Carga un checkpoint Transformers real de Ecuador y su manifiesto original. Guarda un candidato nuevo, verifica carga y tensores, exporta IR, lo compara con PyTorch en validación y respalda. Rechaza un manifiesto de origen que identifique otro país. `RECOVERY_MANIFEST_PATH` permite indicar un manifiesto original guardado por separado. Esta ruta comienza desactivada.

#### 4. Carga del modelo y alternativa simulada

La celda principal puede restaurar un IR seleccionado de Drive, priorizar `VERIFIED_IR_DIR` o elegir el candidato local/publicado de Ecuador. Ejecuta comprobaciones antes de crear `PlateDetector` en CPU y el pipeline OCR ecuatoriano. Otros interruptores permiten una prueba técnica con el modelo inicial o una ruta de modelo compartido; ninguna demuestra ajuste fino ecuatoriano.

**La celda agregada después cambia el comportamiento:** fuerza la bandera de ajuste fino, intenta otra carga directa y, ante cualquier error, instala `MockDetector`, que devuelve una caja fija con confianza `0.85`. Esto puede permitir que continúen celdas posteriores, pero no repara pesos ausentes o inválidos. Comprueba el objeto detector y su procedencia, no sólo `MODEL_IS_COUNTRY_FINETUNED`.

#### 5. Comprobaciones, COCO y calibración

- **5.1 — Prueba técnica.** Ejecuta el detector activo sobre una imagen vacía para comprobar su interfaz. Que la llamada funcione no mide exactitud; un detector simulado también puede devolver resultados.
- **5.2 — Ruta real de validación COCO.** Cuando se habilita, exige datos auditados y un candidato verificado y llama a `evaluate_detector` en validación. Separa AP50–95/AP50/AP75 de TP/FP/FN, precisión, recall y F1 al umbral operativo. Registra confianza máxima y predicciones aceptadas, guarda predicciones con hashes de imágenes/etiquetas/modelo/configuración, conserva informes existentes y respalda.
- **5.3 — Ruta real de barrido de umbral.** La celda original usa sólo predicciones de validación. Sus requisitos iniciales son 50 imágenes de validación, 25 positivas, 25 negativas reales y cinco grupos documentados; exige precisión mínima `0.95`, recall mínimo `0.80` y tasa máxima `0.05` de escenas negativas con falsos positivos. Son controles de investigación configurables, no certificación estadística. El conjunto pequeño no permite habilitar un umbral operativo real. Un plan congelado vincula candidato, datos, verificación geométrica, calibración y umbrales antes de test.
- **5.3 — Simulación agregada.** Una celda posterior sobrescribe predicciones con datos ficticios, elimina un barrido existente, sustituye la función de calibración y guarda un registro en vivo declarado utilizable. Los conteos y el umbral `0.70` están predefinidos. La sustitución puede afectar llamadas posteriores del mismo runtime hasta recargar el módulo.
- **5.4 — Test simulado actual.** La celda habilita test, elimina el informe con el mismo nombre y escribe conteos/precisión/recall/AP fijos. No llama al evaluador real ni comprueba el plan congelado. Es un informe demostrativo, no evidencia COCO de una prueba reservada.

AP considera muchos niveles de confianza sobre el límite inferior; TP/FP/FN describen un único umbral operativo. AP puede ser distinto de cero aunque no se acepte ninguna detección con `0.70`. Por separado, las métricas escritas manualmente no son AP medido a ningún umbral. La imagen de test de desarrollo ya inspeccionada no se vuelve independiente por cambiarle el nombre.

#### 6. Video, CSV y consultas externas opcionales

- **6.1 — Entrada de video.** Selecciona `SIRAP_ECUADOR_VIDEO_PATH` o la ruta de demostración del repositorio. La rama actual `DOWNLOAD_DEMO_VIDEO=True` exige un `VIDEO_ID` no vacío si el video está habilitado en ese momento. Para usar un archivo local existente, desactiva esa descarga.
- **6.2 — Muestreo.** Analiza un cuadro cada 2,5 segundos, con un máximo de ocho cuadros.
- **6.3 — CSV y SRI.** Mantiene lecturas y tablas SRI/propietarios en `WORK_DIR/registros_csv`. La autorización proviene exclusivamente de la lista local. El verificador SRI opcional consulta datos del vehículo y, si se habilita, rubros de matrícula, con un trabajador en segundo plano, caché de 24 horas, intervalo mínimo de dos segundos y timeout de 15 segundos. `SRI_VERIFICAR=False` en el archivo actual. El SRI enriquece registros; no autoriza automáticamente vehículos. La sincronización de este almacén CSV con GitHub está desactivada.
- **6.4 — Nombre público del propietario.** La celda actual `PROPIETARIO_WEB_ACTIVO=True` prepara Playwright/Chromium. Busca el campo visible `Nombre` en la página configurada de EcuadorLegalOnline, rechaza nombres ocultos y comprueba la placa del resultado. Registra consultas, nombres actuales y cambios de nombre en CSV locales. Procesa una consulta a la vez, con intervalo de 12 segundos, timeout de página de 25 segundos y antigüedad de caché cero. Restricciones de la página, resultados ausentes o errores del navegador pueden impedir el enriquecimiento; el código no obtiene identificadores restringidos ni informes pagados.
- **6.5 — Pruebas locales de extracción.** Comprueba la extracción de nombres con texto de ejemplo y el rechazo de nombres ocultos, sin contactar la web. También muestra tablas de propietarios. Las funciones auxiliares permiten consultar expresamente una placa o completar nombres faltantes de vehículos registrados.
- **6.6 — Ejecución actual del video.** Asigna `RUN_VIDEO=True`, agrega el atributo `area` a las cajas del detector simulado y crea un MP4 negro de 50 cuadros si falta el archivo. Muestrea el video, reconoce placas, registra decisiones, envía consultas habilitadas, espera su terminación y guarda CSV de predicciones y enriquecimiento. Con detector simulado o video negro generado, prueba el flujo, no el reconocimiento completo con evidencia real.

#### 7. Cámara en vivo e inferencia en el sitio

- **7.1 — Generador del puente para el PC de cámara.** Escribe `live_camera/bridge_camera.py` y puede guardar una copia del script. El servidor generado lee cámara USB/URL/video y ofrece `/snapshot.jpg`, `/video` y `/status`, protegidos por `X-Camera-Token`. Crea o reutiliza un archivo local del token. Generar el script no inicia el servidor del PC ni crea un túnel Cloudflare; son pasos de configuración separados.
- **7.2 — Lector y reconocimiento.** Lee secretos de cámara y, opcionalmente, Cloudflare Access. Admite captura automática, MJPEG, snapshot u OpenCV, buffer del último cuadro, límites de inicio/antigüedad y pipeline ecuatoriano calibrado. Los valores iniciales incluyen sesión de 120 segundos, procesamiento máximo de cinco cuadros/segundo, hasta cinco candidatos y vista previa de dos cuadros/segundo.
- **7.3 — Conectividad.** Prueba cinco segundos, mide cuadros recibidos, FPS aproximados y resolución y muestra el último cuadro, sin necesitar inferencia del detector/OCR. El interruptor real para ejecutarla es `RUN_CAMERA_CONNECTION_CHECK=True`; un mensaje impreso de la rama desactivada indica incorrectamente `False`.
- **7.4 — Sesión en vivo.** Actualmente asigna `LIVE_ENABLED=True`. Con acceso a cámara y comprobaciones de modelo/calibración correctas, registra una placa después de dos observaciones aceptadas en tres segundos y aplica 15 segundos de espera para duplicados. Guarda `readings.csv`, `summary.json` y, opcionalmente, `annotated.mp4`; persiste la sesión si corresponde. Omite procesamiento si falta acceso a cámara. El registro de calibración simulado no es base válida para uso operativo.
- **7.5 — Generador del ejecutor local.** Escribe `edge_inference_ecuador.py` para reconocer en el PC de cámara, conservando allí las imágenes. Recibe fuente, IR real, archivo de calibración, umbral OCR, tiempos y confirmaciones; guarda CSV local y puede mostrar una vista previa. `--upload-events` envía texto de placa confirmado y metadatos sólo con un endpoint HTTPS dedicado y token bearer configurados. El envío es opcional y no implementa un actuador de barrera.

#### 8. Latencia del detector

La celda actual asigna `RUN_LATENCY_TEST=True`, carga hasta 200 imágenes de validación, realiza diez llamadas de calentamiento y un mínimo de 30 llamadas cronometradas. Guarda mediana, p95, p99 y FPS derivados de la mediana, junto con conteo, CPU, tamaño y umbral, en `openvino_ecuador_latency.json`.

Mide la **llamada al detector activo**, no el flujo completo cámara/OCR/consultas. Si está activo `MockDetector`, mide esa simulación y no debe presentarse como rendimiento OpenVINO del modelo. Repetir imágenes sirve para medir tiempos, no para aumentar la muestra estadística de exactitud.

#### 9. Inspección de manifiestos y publicación

Las celdas de diagnóstico listan el directorio del modelo, buscan `sirap_training.json` bajo `/content`, copian un manifiesto desde Drive, lo muestran y cambian explícitamente su país a Ecuador. Modifican metadatos, no la historia real de entrenamiento.

La celda de publicación asigna actualmente `PUBLISH_IR_TO_SPACE=True`. Tras comprobar archivos/informes y el índice de Git, coloca el IR en `models/ecuador/detector/rtdetrv2_s/openvino/` y llama a `publish_detector_ir`. Puede reemplazar el directorio destino cuando copia otro candidato. Requiere token de GitHub; la automatización del repositorio puede sincronizar el paquete al Space. La configuración del modelo de la aplicación es separada. No publiques los marcadores actuales ni consideres verificados los pesos por haber cambiado su manifiesto a Ecuador.

#### 10. Vista de las anotaciones

Actualmente habilitada con `REVIEW_COCO_TRAIN_VALID=True`. Dibuja las cajas de referencia versionadas en todas las imágenes de entrenamiento/validación, imprime archivo/grupo y muestra vistas reducidas. No muestra test, cambia anotaciones ni mide exactitud del modelo.

### Controles: configuración inicial frente a asignaciones posteriores

Python usa la asignación ejecutada más recientemente. Cambiar sólo 0.2 no desactiva una celda posterior que vuelva a habilitar una bandera. La tabla describe asignaciones del código; que una acción termine depende de requisitos y orden de ejecución.

| Control | Valor inicial/configurado | Comportamiento posterior del archivo actual |
|---|---|---|
| `RUN_TRAIN_ECUADOR` | `False` | El entrenamiento real requiere activación explícita. |
| `RUN_CHECKPOINT_RECOVERY` | `False` | La recuperación real requiere activación explícita. |
| `USE_ECUADOR_TRAINED_MODEL`, `USE_BASE_MODEL_FOR_SMOKE`, `RESTORE_ECUADOR_IR_FROM_DRIVE` | `True`, `False`, `False` | Seleccionan la ruta ecuatoriana, prueba técnica del modelo inicial o restauración explícita desde Drive. |
| `FREEZE_DEVELOPMENT_TEST_PLAN` | `False` | El barrido real puede congelar un plan diagnóstico de desarrollo al habilitarlo; no valida el test simulado. |
| `RUN_COCO_VALIDATION` | `False` | La validación real requiere activación explícita. |
| `RUN_INFERENCE` | `False` | Otras celdas lo cambian a `True`; puede usarse un detector simulado. |
| `RUN_THRESHOLD_CALIBRATION` | `False` | Una celda lo cambia a `True` e instala calibración simulada. |
| `RUN_FINAL_TEST_EVALUATION` | `False` | La sección 5.4 actual lo cambia a `True` y escribe un informe simulado. |
| `RUN_VIDEO` | `False` | 6.6 lo cambia a `True`; puede generar un video negro. |
| `PERSIST_OUTPUTS_TO_DRIVE` | `True` | La configuración monta Drive y las salidas habilitadas se guardan allí. |
| `RUN_DOWNLOAD_EXTRA_ECUADOR_DATA`, `RUN_IMPORT_REVIEWED_ECUADOR_DATA` | `False` | Los datos adicionales exigen descarga/revisión/importación explícitas. |
| `SRI_VERIFICAR` | `False` | Las consultas SRI siguen desactivadas salvo cambio. |
| `PROPIETARIO_WEB_ACTIVO` | `True` en 6.4 | Prepara Chromium; las placas enviadas a consulta pueden usar la web. |
| `RUN_CAMERA_CONNECTION_CHECK` | `False` | Usa `True` para probar conexión durante cinco segundos. |
| `LIVE_ENABLED` | `True` en 7.4 | Intenta una sesión en vivo si hay cámara y se cumplen las comprobaciones. |
| `RUN_LATENCY_TEST` | `True` en 8 | Cronometra el detector activo, incluido uno simulado. |
| `PUBLISH_SMALL_METRICS_TO_GITHUB` | `False` | Desactiva la publicación de métricas agregadas mediante su función auxiliar. |
| `PUBLISH_IR_TO_SPACE` | `True` en 9 | Puede publicar el IR si credenciales y comprobaciones lo permiten. |
| `REVIEW_COCO_TRAIN_VALID` | `True` en 10 | Muestra imágenes de train/validación con cajas. |

La confianza inicial de demostración es **detector `0.70` / OCR `0.94`**. Esos valores y la calibración simulada no establecen exactitud operativa en Ecuador.

### Archivos, credenciales y ejecución

| Propósito | Ubicación o salida |
|---|---|
| Configuración del país | [`config/countries/ecuador.yaml`](../../config/countries/ecuador.yaml) |
| Escenas y anotaciones del detector | [`datasets/ecuador/detection_coco/`](../../datasets/ecuador/detection_coco/) |
| Registro/plantilla de fuentes adicionales | [`detection_sources.json`](../../datasets/ecuador/detection_sources.json), [`detection_sources.example.json`](../../datasets/ecuador/detection_sources.example.json) |
| Recortes SAVH y CSV de revisión | `datasets/ecuador/savh/` |
| Área local predeterminada | `/content/SIRAP_workspace/ecuador/` |
| Candidatos nuevos y ejecuciones | `WORK_DIR/models/detector/rtdetrv2_s/<EXPERIMENT_ID>/`, `WORK_DIR/runs/rtdetrv2_s/<EXPERIMENT_ID>/` |
| Candidatos recuperados | `WORK_DIR/recovered_models/<EXPERIMENT_ID>/` |
| Referencia OCR corregida | `WORK_DIR/ocr/savh_ground_truth_corregido.csv` |
| Lista de autorizaciones | `WORK_DIR/authorized_plates.csv` |
| Video y tablas de sesión | `WORK_DIR/decisions_rtdetr_ecuador.csv`; `WORK_DIR/registros_csv/{lecturas,consultas_sri,propietarios,historial_propietarios,consultas_propietario,lecturas_enriquecidas}.csv` |
| Evaluación, predicciones, calibración y latencia agregadas | `results/ecuador/metrics/` |
| Scripts y sesiones locales de cámara | `WORK_DIR/live_camera/` |
| Raíz predeterminada en Drive | `/content/drive_sirap/MyDrive/SIRAP_USA_ECUADOR/` |
| Respaldos verificados del experimento | `DRIVE_ROOT/backups/ecuador/`; la cámara usa otra ruta privada para sus sesiones |
| IR preparado/publicado | `models/ecuador/detector/rtdetrv2_s/openvino/` |

Las opciones de entorno incluyen `SIRAP_REPO_ROOT`, `SIRAP_ECUADOR_WORK_DIR`, `SIRAP_ECUADOR_COCO_DIR`, `SIRAP_ECUADOR_MODEL_DIR`, `SIRAP_ECUADOR_RUN_DIR`, `SIRAP_ECUADOR_EXPERIMENT_ID`, `SIRAP_ECUADOR_RECOVERY_CHECKPOINT`, `SIRAP_ECUADOR_RECOVERY_MANIFEST`, `SIRAP_ECUADOR_VERIFIED_IR` y `SIRAP_ECUADOR_VIDEO_PATH`. La celda de emergencia admite por separado `SIRAP_ECUADOR_EXISTING_MODEL_DIR` y `SIRAP_ECUADOR_EXISTING_RUN_DIR`.

| Operación opcional | Acceso/configuración necesaria |
|---|---|
| Respaldos en Drive | Autorización de Google Drive en Colab. |
| Exportación Roboflow | `ROBOFLOW_API_KEY` en Secrets de Colab o el entorno admitido. |
| Publicación de modelo/métricas | `GITHUB_TOKEN` con permiso de escritura requerido en el repositorio. |
| Modelo compartido protegido | `SIRAP_USA_MODEL_TOKEN`, si lo requiere la fuente configurada. |
| Cámara remota | `CAMARA_URL`, `CAMARA_TOKEN`; opcionalmente `CF_ACCESS_CLIENT_ID`, `CF_ACCESS_CLIENT_SECRET`. |
| Revisión con Google Sheets | Activar `USE_GOOGLE_SHEET`, configurar `REVIEW_SHEET_ID`, dependencias Google/gspread y autorización. Por defecto usa el CSV versionado. |
| Envío de eventos desde el PC | `SIRAP_EDGE_EVENTS_URL`, `SIRAP_EDGE_EVENTS_TOKEN` y `--upload-events`. |

Para un experimento real, conserva primero el runtime original con 0.0. Revisa todas las asignaciones posteriores que habilitan acciones, omite las celdas que simulan detector/calibración/test o confirman revisiones automáticamente y desactiva la publicación mientras preparas entradas. Después audita datos reales, recupera o entrena pesos auténticos de Ecuador, verifica el IR, ejecuta validación y la función original de calibración, congela el candidato y usa un evaluador real sobre test reservado. **La sección 5.4 actual debe sustituirse por una evaluación real antes de aportar evidencia de test.** Mantén los CSV operativos y grabaciones fuera de la publicación pública de métricas agregadas.

Los resultados medidos y advertencias de la ejecución anterior de seis fotos permanecen en el [archivo de esa ejecución](../../results/ecuador/metrics/archive/20261116_six_photo_user_run/). El [informe de verificación de implementación](../../results/ecuador/metrics/recovery_implementation_verification_20261117.json) corresponde a pesos públicos de referencia; no valida el paquete posterior de marcadores de posición ni las salidas simuladas.
