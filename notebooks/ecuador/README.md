# Notebooks de SIRAP: Ecuador

> **Propósito:** índice y guía de ejecución de los notebooks del perfil de Ecuador.

## Español

Esta carpeta contiene los notebooks de exploración, preparación de datos, modelado, optimización y evaluación de SIRAP para placas ecuatorianas. El flujo de EE. UU. se mantiene separado en [`../usa/`](../usa/README.md).

### Índice

| Notebook | Uso |
|---|---|
| [`01_exploracion.ipynb`](01_exploracion.ipynb) | Exploración del dataset de detección y de los datos SAVH. |
| [`02_preprocesamiento.ipynb`](02_preprocesamiento.ipynb) | Preparación del dataset YOLO y de los insumos de evaluación. |
| [`03_modelado.ipynb`](03_modelado.ipynb) | Entrenamiento e integración del detector y el OCR. |
| [`04_optimizacion.ipynb`](04_optimizacion.ipynb) | Búsqueda y análisis de configuraciones de entrenamiento. |
| [`05_evaluacion.ipynb`](05_evaluacion.ipynb) | Métricas del detector, OCR y componentes del sistema. |
| [`06_afinamiento_ocr.ipynb`](06_afinamiento_ocr.ipynb) | Experimento de afinamiento del OCR para placas ecuatorianas. |
| [`07_validacion_multisemilla.ipynb`](07_validacion_multisemilla.ipynb) | Comparación de corridas del detector con distintas semillas. |
| [`sirap_backend.ipynb`](sirap_backend.ipynb) | Notebook principal: ejecución del pipeline, calibración y evaluaciones de imagen y video. |
| [`Evaluacion_video_ground_truth.ipynb`](Evaluacion_video_ground_truth.ipynb) | Crear o revisar la referencia por intervalos y evaluar un CSV de decisiones contra ella. |
| [`old_SIRAP_backend.ipynb`](old_SIRAP_backend.ipynb) | Copia histórica del backend; no es el flujo principal vigente. |

### Orden sugerido

Para estudiar el flujo de datos y entrenamiento, sigue del notebook 01 al 07 según la tarea. Para ejecutar el pipeline o repetir las evaluaciones integradas, abre primero [`sirap_backend.ipynb`](sirap_backend.ipynb) y sigue sus secciones en orden. El notebook de ground truth es complementario: úsalo para anotar o evaluar video con la referencia correspondiente.

### Ejecución y archivos

Los notebooks están preparados para trabajar con el repositorio [`SIRAP_USA_ECUADOR`](https://github.com/eduardoceballos666/SIRAP_USA_ECUADOR). Revisa la celda de configuración de cada notebook antes de ejecutarlo y usa el mismo entorno de Colab/Jupyter para sus celdas dependientes.

- El dataset de entrenamiento descargado se mantiene en el almacenamiento temporal del entorno. Para Roboflow, configura `ROBOFLOW_API_KEY` en los Secrets de Colab; no incluyas la llave en una celda ni en un commit. Para una fuente local, consulta el notebook y coloca el ZIP YOLO en `datasets/ecuador/yolo/`.
- Los insumos se organizan bajo `datasets/ecuador/`: `yolo/` para detección, `savh/` para SAVH y `gate/` para imágenes de garita. Las referencias de video están en `evaluation/ecuador/blind_evaluation/`; los artefactos experimentales de SAVH, en `evaluation/ecuador/savh/`.
- Los pesos publicados del detector están en `models/ecuador/detector/ecuador_best.pt`. Los umbrales y resultados agregados se consultan en `results/metrics/`; las figuras, en `results/figures/`.
- Los resultados nuevos pueden quedar en el almacenamiento temporal de Colab. Descárgalos si necesitas conservar una copia. Si el notebook ofrece una celda para publicar cambios, usa un secreto `GITHUB_TOKEN` con permisos de contenido para el repositorio; nunca pegues el token en el código. GitHub no permite publicar archivos de 90 MiB o más mediante la API de contenidos.

### Evaluación de video

[`Evaluacion_video_ground_truth.ipynb`](Evaluacion_video_ground_truth.ipynb) compara lecturas solo cuando su `frame_index` cae dentro de un intervalo anotado. Las lecturas sin una referencia correspondiente quedan sin clasificar; por eso esas métricas no representan por sí solas todos los vehículos del video. Para comparar con la referencia publicada, utiliza el video original al que corresponde. El clip de demostración permite probar el notebook, pero no puntuarlo contra esa referencia.

Consulta los informes y datos asociados en [`results/metrics/`](../../results/metrics/) y [`evaluation/ecuador/`](../../evaluation/ecuador/). El índice de todos los notebooks del proyecto está en [`../README.md`](../README.md).

## English

This folder contains the SIRAP notebooks for Ecuadorian plates, covering data exploration, preprocessing, modeling, optimization, and evaluation. The U.S. workflow is kept separately in [`../usa/`](../usa/README.md).

### Notebook index

| Notebook | Purpose |
|---|---|
| [`01_exploracion.ipynb`](01_exploracion.ipynb) | Explore the detection dataset and SAVH data. |
| [`02_preprocesamiento.ipynb`](02_preprocesamiento.ipynb) | Prepare the YOLO dataset and evaluation inputs. |
| [`03_modelado.ipynb`](03_modelado.ipynb) | Train and integrate the detector and OCR. |
| [`04_optimizacion.ipynb`](04_optimizacion.ipynb) | Search and analyze training configurations. |
| [`05_evaluacion.ipynb`](05_evaluacion.ipynb) | Evaluate detector, OCR, and system components. |
| [`06_afinamiento_ocr.ipynb`](06_afinamiento_ocr.ipynb) | Experiment with OCR tuning for Ecuadorian plates. |
| [`07_validacion_multisemilla.ipynb`](07_validacion_multisemilla.ipynb) | Compare detector runs with different random seeds. |
| [`sirap_backend.ipynb`](sirap_backend.ipynb) | Main notebook for the pipeline, calibration, and integrated image and video evaluations. |
| [`Evaluacion_video_ground_truth.ipynb`](Evaluacion_video_ground_truth.ipynb) | Create or review interval-based ground truth and evaluate a decision log against it. |
| [`old_SIRAP_backend.ipynb`](old_SIRAP_backend.ipynb) | Historical backend copy; it is not the current primary workflow. |

### Suggested workflow

Use notebooks 01–07 in order when following the data and training workflow, selecting the notebooks relevant to your task. To run the pipeline or repeat its integrated evaluations, start with [`sirap_backend.ipynb`](sirap_backend.ipynb) and follow its sections. The ground-truth notebook is supplementary and is intended for video annotation or evaluation against the matching reference.

### Running notebooks and file locations

The notebooks are designed to work with the [`SIRAP_USA_ECUADOR`](https://github.com/eduardoceballos666/SIRAP_USA_ECUADOR) repository. Review each notebook's setup cells before running it, and keep dependent cells in the same Colab/Jupyter runtime.

- Downloaded training data stays in the runtime's temporary storage. For Roboflow, store `ROBOFLOW_API_KEY` in Colab Secrets; do not put the key in a code cell or commit. For a local source, follow the notebook instructions and place the YOLO ZIP under `datasets/ecuador/yolo/`.
- Inputs are organized under `datasets/ecuador/`: `yolo/` for detection, `savh/` for SAVH, and `gate/` for gate images. Video references are under `evaluation/ecuador/blind_evaluation/`; SAVH experiment artifacts are under `evaluation/ecuador/savh/`.
- The published detector checkpoint is `models/ecuador/detector/ecuador_best.pt`. Thresholds and aggregated results are under `results/metrics/`; figures are under `results/figures/`.
- New outputs may remain in Colab's temporary storage. Download anything you need to retain. If a notebook provides a publishing cell, use a `GITHUB_TOKEN` secret with repository Contents permission; never paste the token into code. GitHub's Contents API cannot publish files of 90 MiB or larger.

### Video evaluation

[`Evaluacion_video_ground_truth.ipynb`](Evaluacion_video_ground_truth.ipynb) compares a read with ground truth only when its `frame_index` falls within an annotated interval. Reads without a corresponding reference remain unclassified, so these metrics alone do not represent every vehicle in the video. Use the original video that matches the published reference. The demo clip can be used to try the notebook, but not scored against that reference.

See the related reports and data in [`results/metrics/`](../../results/metrics/) and [`evaluation/ecuador/`](../../evaluation/ecuador/). The project-wide notebook index is [`../README.md`](../README.md).
