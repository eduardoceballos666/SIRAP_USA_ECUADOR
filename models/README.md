# Modelos de SIRAP

La aplicación ejecuta **un único detector para Ecuador y Estados Unidos**: **RT-DETRv2-S (ResNet-18vd)** con OpenVINO Runtime, la **semilla 2** entrenada con placas de EE. UU. a partir de [`merve/license-plates-rtdetrv2`](https://huggingface.co/merve/license-plates-rtdetrv2) (Apache-2.0). Ecuador usa los mismos pesos; solo cambian las reglas con que se interpreta el texto leído. **No existe un detector ecuatoriano**, y su desempeño con placas de Ecuador todavía no se ha evaluado.

## Cómo llega el modelo a la aplicación

El modelo **no está en Git ni en la imagen de Docker, y el Dockerfile no entrena ni convierte ningún modelo**. Los pesos viven en un repositorio de modelos privado de Hugging Face (`eduardoceballos/SIRAP_USA_seed2`):

1. [`usa/selected_checkpoint.json`](usa/selected_checkpoint.json) es el registro inmutable de la selección: repositorio, **commit** y **SHA-256** del detector, de los metadatos y del OCR.
2. Al iniciar, `src/usa_pipeline.py` descarga esos archivos con el secreto `SIRAP_USA_MODEL_TOKEN` a `models/shared/detector/rtdetrv2_s/seed_2/openvino/` (la ruta que usan `config/config.yaml` y `config/countries/*.yaml`; esa carpeta está en `.gitignore`).
3. Antes de inferir se comprueba cada huella. Si un archivo no coincide, la aplicación **se niega a cargar el detector**; no hay un modelo de reserva.
4. El workflow de despliegue (`deploy/huggingface/sync_space.py`) hace la misma comprobación contra el repositorio privado antes de actualizar el Space.

Para una instalación local puede apuntarse a artefactos ya verificados con `SIRAP_USA_DETECTOR_DIR` y `SIRAP_USA_OCR_DIR`; una ruta equivocada produce un error y no se sustituye el modelo.

El **OCR** es `cct-s-v2-global-model` de `fast-plate-ocr` (ONNX Runtime), con los mismos pesos para ambos países. Se descarga al construir la imagen y su huella también está en `selected_checkpoint.json`. La inferencia no instala PyTorch ni Transformers.

## Qué hay en cada carpeta

| Ruta | Contenido | ¿Lo usa la app? |
|---|---|---|
| `usa/selected_checkpoint.json` | Registro de la semilla 2 (commit, SHA-256, umbrales 0,70 y 0,94) | **Sí** |
| `shared/detector/rtdetrv2_s/seed_2/openvino/` | Destino de la descarga del detector verificado (`openvino_model.xml/.bin`, `sirap_openvino.json`, `sirap_training.json`); no se versiona | **Sí** (se crea al iniciar) |
| `usa/detector/rtdetrv2_s/openvino/` | IR de una corrida de prueba anterior (semilla 1, 64 imágenes de entrenamiento); no es la selección vigente | No |
| `ecuador/detector/rtdetrv2_s/openvino/` | Archivos de relleno (`dummy`) de una publicación de prueba; no hay pesos | No |
| `ecuador/ocr/archive/` | Archivo, en partes, de un OCR afinado anterior | No |

## Cambiar de modelo

Un candidato nuevo (de [notebooks/usa](../notebooks/usa/) o `src/train.py`) **nunca** sustituye al vigente por sí solo. Para adoptarlo hay que publicarlo en el repositorio privado, evaluarlo por separado y actualizar `usa/selected_checkpoint.json` (commit y huellas) en un cambio explícito. El procedimiento y los resultados de validación están en [docs/optimizacion.md](../docs/optimizacion.md); la arquitectura, en [docs/arquitectura.md](../docs/arquitectura.md).

Las licencias del código, del checkpoint base y de los datos son independientes: consulte [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md).
