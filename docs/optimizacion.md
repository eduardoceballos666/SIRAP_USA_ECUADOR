# Entrenamiento, validación y optimización del detector

Este documento explica cómo se obtuvo el detector que usa SIRAP y cómo se debe entrenar, evaluar y cambiar un candidato nuevo sin afectar la aplicación desplegada.

## Qué ejecuta la aplicación hoy

- **Detector:** RT-DETRv2-S (ResNet-18vd) en OpenVINO IR, inicializado desde [`merve/license-plates-rtdetrv2`](https://huggingface.co/merve/license-plates-rtdetrv2) (Apache-2.0) y ajustado con placas de EE. UU.
- **Un solo checkpoint para los dos países:** la **semilla 2**, fijada por commit y huellas SHA-256 en [`models/usa/selected_checkpoint.json`](../models/usa/selected_checkpoint.json) y alojada en un repositorio privado de Hugging Face. Ecuador usa esos mismos pesos; solo cambian las reglas de interpretación del OCR.
- **Umbrales:** detección 0,70 y probabilidad mínima por carácter del OCR 0,94.
- **Congelado:** ejecutar un notebook o entrenar un candidato **nunca** reemplaza ese checkpoint. Cambiarlo exige publicar el candidato en el repositorio privado y actualizar `selected_checkpoint.json` (commit y huellas) en una decisión explícita.

Cómo se carga y se verifica en el servidor: [arquitectura.md](arquitectura.md).

## Registro del entrenamiento del checkpoint desplegado (semilla 2)

Fuente: `sirap_training.json` del repositorio privado del checkpoint, cuyas huellas fija [`selected_checkpoint.json`](../models/usa/selected_checkpoint.json).

| Parámetro | Valor |
|---|---|
| Datos | Conjunto de recuperación `recovery_coco_20261114` (COCO Detection, una clase de matrícula): **249 imágenes de entrenamiento** (192 con placa y 57 negativas) y **79 de validación** (41 con placa y 38 negativas). Combina grabaciones de una cámara objetivo con un paquete de negativos (`negative_pack_20261114`), agrupadas por día: todo el 23 de marzo en entrenamiento y el 19 de marzo en validación. El origen de cada imagen no está documentado en este repositorio |
| Punto de partida | Checkpoint Transformers de EE. UU. anterior, derivado de [`merve/license-plates-rtdetrv2`](https://huggingface.co/merve/license-plates-rtdetrv2) |
| Corrida | `20261114T210050Z`, semilla 2; mejor checkpoint: `checkpoint-288` |
| Épocas | máximo 50, parada temprana con paciencia 8 |
| Lote / tasa de aprendizaje / decaimiento | 8 / 5e-5 / 1e-4 (AdamW con el `Trainer` de Transformers) |
| Salida | OpenVINO IR (`openvino_model.xml/.bin`) con `sirap_openvino.json` y `sirap_training.json` |

**Cómo se eligió la semilla 2.** La corrida `20261114T210050Z` entrenó las semillas 0, 1 y 2 con ese conjunto y eligió por mAP@0,5:0,95 en validación (`candidates.json` y `selected_checkpoint.json` de la corrida, guardados en Google Drive y no versionados aquí): **0,7460** (semilla 0), **0,7575** (semilla 1) y **0,7671** (semilla 2). El checkpoint de partida obtiene 0,5757 en esa misma validación. Son 79 imágenes de un solo día y la misma validación sirvió para elegir, así que las cifras son optimistas; el **test final no se evaluó** porque falta una grabación o un día de la cámara objetivo, con negativos, que no se haya examinado antes.

**Experimento de tres semillas (otra serie de corridas)** ([`rtdetr_usa_three_seed_validation.json`](../results/metrics/rtdetr_usa_three_seed_validation.json) y [`entrenamiento_rtdetr.json`](../results/metrics/entrenamiento_rtdetr.json)): se entrenaron las semillas 0, 1 y 2 con European + USA License Plates (Roboflow), con las divisiones reagrupadas por fuente de origen antes de separarlas (9 068 imágenes de entrenamiento y 534 de validación). El mAP@0,5:0,95 en validación fue 0,827 (semilla 0), 0,832 (semilla 1) y 0,828 (semilla 2); las diferencias son pequeñas y no se presentan como significativas, y el informe marcó la semilla 1 como la mejor de esa serie.

**Esas corridas no son el checkpoint desplegado.** La «semilla 2» de la aplicación es la del conjunto de recuperación de arriba, con otros datos y otro punto de partida, de modo que las cifras de las tres semillas no describen su rendimiento. Los dos rankings no se contradicen: hay dos series con datos y validaciones distintas, y en la que produjo el modelo desplegado la semilla 2 es la mejor en validación. La fuente de verdad del modelo desplegado es `selected_checkpoint.json`.

**Búsqueda Optuna** ([`rtdetr_usa_optuna_summary.json`](../results/metrics/rtdetr_usa_optuna_summary.json)): ocho pruebas de hasta 12 épocas (tasa de aprendizaje, decaimiento y lote). Su mAP@0,5:0,95 de validación quedó cerca de cero (el mejor valor fue 0,0001), así que no se usó para elegir hiperparámetros: el entrenamiento final conservó los valores por defecto de la tabla anterior.

## Qué falta evaluar

- **Ecuador:** el rendimiento del checkpoint con placas ecuatorianas no se ha evaluado.
- **EE. UU.:** el test independiente de la semilla 2 sigue pendiente de una fuente nueva con referencia revisada. La comprobación vigente es de desarrollo (ocho fotos reutilizadas y lectura del estado sobre recortes), no un test independiente. Detalle y cifras: [`results/README.md`](../results/README.md).
- **Umbrales:** las calibraciones publicadas corresponden a otros candidatos y no respaldan por sí solas el umbral 0,70 de la semilla 2; ese valor es una decisión operativa conservada por el propietario del proyecto.
- Los informes y gráficos con YOLO/Ultralytics en `results/` son históricos y no describen el modelo vigente.

## Cómo reproducir o probar un candidato

Dónde está cada paso:

| Paso | Herramienta |
|---|---|
| Preparar datos COCO Detection (una clase de matrícula) | [`notebooks/usa/sirap_backend_usa.ipynb`](../notebooks/usa/sirap_backend_usa.ipynb), secciones 4–8 (opcionales, apagadas por defecto); [`scripts/usa_annotations_to_coco.py`](../scripts/usa_annotations_to_coco.py) |
| Entrenar y exportar | `python -m src.train --country usa --data-dir <coco> --seed <n>` (exporta a OpenVINO IR al terminar); `src/export_openvino.py` convierte un checkpoint ya entrenado |
| Búsqueda Optuna y tres semillas | secciones 9–12 del notebook de EE. UU. (`RUN_OPTUNA` y `RUN_FINAL_TRAINING` apagados por defecto; 8 pruebas × 12 épocas; semillas 0, 1 y 2; máximo 50 épocas, paciencia 8) |
| Evaluar el detector | `python -m src.evaluate detector --country usa --data-dir <coco> --split test --checkpoint <ruta/openvino>` (métricas COCO con el mismo runtime OpenVINO de la app) |
| Evaluar el sistema completo | `python -m src.evaluate e2e --csv <archivo.csv>` con columnas `image_path,plate_gt`; incluye el OCR |
| Verificar el modelo desplegado | secciones 13–15 y 20–21 del notebook de EE. UU. (usan el mismo proveedor y los mismos manejadores HTTP de la API) |
| Flujo de Ecuador | [`notebooks/ecuador/sirap_backend_ecuador.ipynb`](../notebooks/ecuador/sirap_backend_ecuador.ipynb): datos y SAVH, OCR, evaluación COCO, video, cámara, latencia y publicación opcional |

El entrenamiento requiere `requirements-training.txt` (o las dependencias de Colab) y GPU; el runtime de la aplicación (`requirements.txt`) no instala PyTorch ni Transformers.

## Protocolo para comparar semillas o hiperparámetros

1. Fijar de antemano las versiones de código, Transformers/PyTorch (entrenamiento), OpenVINO (inferencia), el dataset COCO y el checkpoint base.
2. Definir antes de entrenar la configuración base y la candidata; usar semillas emparejadas (por ejemplo 0, 1 y 2).
3. Agrupar las imágenes relacionadas (mismo vehículo, cámara o sesión) **antes** de dividir, de modo que no haya fuga entre entrenamiento, validación y test.
4. Elegir hiperparámetros y semilla solo con entrenamiento y validación; nunca con el test.
5. Guardar, por semilla, el checkpoint Transformers y su IR con el manifiesto (`sirap_openvino.json`, `sirap_training.json`) y la versión del dataset.
6. Evaluar **una sola vez** en un test reservado y de procedencia independiente. Informar mAP@0,5:0,95, mAP@0,5, precisión, recall, tamaño de muestra, hardware y diferencias pareadas; una media descriptiva no es significación estadística.
7. Calibrar el umbral operativo en validación, y medir falsas detecciones en escenas sin placa.
8. Evaluar la lectura de matrículas por separado (recortes OCR, imágenes completas, video): son métricas con alcances distintos y no se combinan en un solo porcentaje. SAVH Guayaquil sirve para OCR de recortes; no reemplaza un conjunto de detección ni una evaluación de punta a punta.
9. Publicar las métricas con el nombre del modelo, el protocolo y los límites del dataset, y no atribuirlas a la selección vigente sin comprobarlo.
