# Avisos de componentes y recursos de terceros

La licencia [Apache License 2.0](LICENSE) cubre el **código original** de SIRAP_USA_ECUADOR. El aviso de autoría está en [NOTICE](NOTICE). Las versiones publicadas anteriormente bajo MIT conservan los términos de esa licencia. Cada modelo, biblioteca, conjunto de datos y servicio de terceros mantiene sus propios términos; esta licencia **no** los cambia.

El resultado de la última revisión (2026-11-22), con lo verificado y lo pendiente, está en [`docs/auditoria_licencias.md`](docs/auditoria_licencias.md). Esa revisión no es asesoría legal.

## Modelos

| Componente | Uso en SIRAP | Licencia declarada | Observaciones |
|---|---|---|---|
| [`PekingU/rtdetr_v2_r18vd`](https://huggingface.co/PekingU/rtdetr_v2_r18vd) | Checkpoint base RT-DETRv2 (ResNet-18vd), entrenado con COCO | Apache-2.0 | Artículo: [arXiv 2407.17140](https://arxiv.org/abs/2407.17140) |
| [`merve/license-plates-rtdetrv2`](https://huggingface.co/merve/license-plates-rtdetrv2) | Punto de partida del detector de placas | Apache-2.0 (ficha del modelo) | Deriva del anterior. **No se verificó** con qué datos fue ajustado. |
| Checkpoint desplegado (semilla 2), repositorio privado `eduardoceballos/SIRAP_USA_seed2` | Único detector para Ecuador y EE. UU. | Apache-2.0 (declarado por el propietario) | Entrenado con un conjunto de recuperación de 249 imágenes de entrenamiento y 79 de validación (grabaciones de una cámara objetivo y un paquete de negativos) cuya procedencia y permisos **no están documentados en este repositorio**. |
| `cct-s-v2-global-model` de [`fast-plate-ocr`](https://github.com/ankandrew/fast-plate-ocr) | OCR de matrículas (ONNX Runtime) | El código es MIT. **La licencia de los pesos y de sus datos de entrenamiento no se verificó.** | Se descarga al construir la imagen. |

Los checkpoints derivados de un modelo Apache-2.0 deben conservar los avisos de sus fuentes. Las métricas históricas con YOLO no describen RT-DETRv2-S.

## Bibliotecas de Python

Las dependencias bloqueadas (`requirements.txt`, `requirements-training.txt`, `requirements-dev.txt`) son 188 paquetes distintos; según sus metadatos de PyPI, 185 tienen licencias permisivas (MIT, BSD, Apache-2.0, PSF, HPND) y 3 usan MPL-2.0. Ninguna es GPL, LGPL ni AGPL. Las principales del tiempo de ejecución:

| Paquete | Licencia |
|---|---|
| FastAPI, PyJWT, PyYAML, Plotly, rapidfuzz, ONNX Runtime, fast-plate-ocr, Pillow (MIT-CMU/HPND) | MIT |
| Starlette, Uvicorn, pandas, NumPy | BSD-3-Clause |
| OpenVINO, OpenCV (`opencv-python-headless`), Playwright, requests, python-multipart | Apache-2.0 |
| `certifi`, `tqdm` | **MPL-2.0** (`tqdm`: MPL-2.0 y MIT) |

- **MPL-2.0 (`certifi`, `tqdm`):** copyleft a nivel de archivo. Usarlos sin modificarlos no impone obligaciones sobre el código de SIRAP; si se modifica uno de sus archivos, esos cambios deben publicarse bajo MPL-2.0. Código fuente: [certifi](https://github.com/certifi/python-certifi), [tqdm](https://github.com/tqdm/tqdm).
- **Distancia de edición:** se usa `rapidfuzz` (MIT). El paquete `Levenshtein` es **GPL-2.0-or-later** y se eliminó de las dependencias; no debe volver a añadirse.
- **Entrenamiento y exportación** (PyTorch, Transformers, Accelerate, Optuna, Roboflow): solo en `requirements-training.txt`; la aplicación no los instala.
- **OpenCV** empaqueta FFmpeg (LGPL-2.1) y otras bibliotecas en su rueda; se usan como biblioteca dinámica sin modificar. Si se distribuye una imagen o un instalador, deben acompañarse sus avisos y la oferta de código fuente de esas partes.

## Interfaz (npm)

| Paquete | Licencia |
|---|---|
| Vue, Pinia, Vue Router, vue-echarts | MIT |
| [Apache ECharts](https://echarts.apache.org/) | Apache-2.0 (su aviso está en [NOTICE](NOTICE)) |
| ZRender (dependencia de ECharts) | BSD-3-Clause, Baidu |
| tslib | 0BSD |

Las herramientas de compilación (Vite, Tailwind CSS, `lightningcss` [MPL-2.0]) se ejecutan al construir la imagen y no se distribuyen dentro de la aplicación. Los avisos de copyright de estos paquetes deben acompañar a una versión empaquetada de la interfaz (ver el informe de auditoría).

## Imagen de Docker y servicios del sistema

| Componente | Licencia | Uso |
|---|---|---|
| Python 3.11 (`python:3.11-slim`, Debian) | PSF-2.0 y las licencias de cada paquete Debian | Base de la imagen |
| Tesseract OCR y datos `eng` | Apache-2.0 | Lectura auxiliar |
| `libgl1`, `libglib2.0-0` | LGPL (enlace dinámico) | Dependencias de OpenCV |
| Chromium de Playwright | BSD-3-Clause y licencias de sus componentes (incluye FFmpeg, LGPL) | Consulta de J.D. Power en el perfil de EE. UU. |

## Conjuntos de datos

- **European + USA License plates** (Roboflow Universe, por PlateBlur): versión 1, usado para el ajuste de detectores en las corridas de tres semillas. Licencia **CC BY 4.0**: exige atribución, indicación de cambios y enlace a la licencia. [Ficha del dataset](https://universe.roboflow.com/plateblur/european-usa-license-plates). Las imágenes no se redistribuyen en este repositorio.
- **SAVH Guayaquil ANPR Plate Images Dataset** (Zenodo, [registro](https://zenodo.org/records/21120307)): recortes de matrículas ecuatorianas para evaluar el OCR. Licencia **CC BY 4.0** según el registro; cite a los autores si se redistribuye cualquier parte (el repositorio conserva un subconjunto de referencia en `datasets/ecuador/savh/`).
- **`openalpr/benchmarks`, conjunto `seg_and_ocr`** (751 recortes de matrículas de EE. UU.): licencia **GNU AGPL-3.0**. **Se retiró del repositorio** y no debe copiarse en `datasets/`, `docs/`, imágenes de Docker ni en el Space. Solo se usa para mediciones de desarrollo descargándolo aparte; ver [`datasets/usa/seg_and_ocr/README.md`](datasets/usa/seg_and_ocr/README.md).
- **Imágenes y videos de garita y de demostración** (`datasets/ecuador/gate/`, `datasets/shared/demo_media/`, `evaluation/ecuador/`): capturas del proyecto. Su autoría, el permiso de quienes aparecen y la autorización del sitio **deben ser confirmados por los autores**; no se verificaron.
- **`data/samples/`:** cuatro imágenes de demostración de la interfaz, sin valor de evaluación.

## Servicios externos

- **J.D. Power (consulta de valor de vehículos de EE. UU.)** (`api/providers/usa_jdpower.py`): consulta una página pública con un navegador automatizado. Sus condiciones de uso **no se pudieron revisar** y podrían prohibir la consulta automatizada ni su uso comercial. Antes de una versión comercial debe obtenerse permiso por escrito o desactivarse la función.

## Fuentes tipográficas de los manuales

Los PDF de `docs/manual/` se generan con las fuentes Inter (SIL Open Font License 1.1) y DejaVu Sans Mono (licencia libre de Bitstream Vera/DejaVu). Ambas permiten incrustarse en documentos.
