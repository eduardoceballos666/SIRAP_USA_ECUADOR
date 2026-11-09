# Avisos de componentes y recursos de terceros

La licencia [Apache License 2.0](LICENSE) cubre el código original de SIRAP_USA_ECUADOR en esta versión. El aviso de autoría está en [NOTICE](NOTICE). Las versiones publicadas anteriormente bajo MIT conservan los términos de esa licencia. Cada modelo, biblioteca y conjunto de datos mantiene sus propios términos.

## Detector y bibliotecas

- **Checkpoint `merve/license-plates-rtdetrv2`:** RT-DETRv2 R18 ajustado para detectar matrículas, distribuido en Hugging Face bajo **Apache-2.0**. [Ficha del modelo](https://huggingface.co/merve/license-plates-rtdetrv2). Su tarjeta identifica como base a `PekingU/rtdetr_v2_r18vd`.
- **Checkpoint base `PekingU/rtdetr_v2_r18vd`:** RT-DETRv2 R18 para Transformers, Apache-2.0. [Ficha del modelo](https://huggingface.co/PekingU/rtdetr_v2_r18vd).
- **Transformers y PyTorch:** infraestructura de carga, ajuste fino e inferencia del detector. Conservan sus licencias de software respectivas; no se utiliza Ultralytics.
- **fast-plate-ocr:** reconocimiento óptico de caracteres (OCR), MIT.
- **OpenCV (`opencv-python-headless`):** lectura y conversión de imágenes/video. Apache-2.0 ([licencia](https://github.com/opencv/opencv/blob/4.12.0/LICENSE)).

Los checkpoints finos que se produzcan a partir de esos pesos deben conservar la atribución y los avisos aplicables a su checkpoint de origen. Las métricas históricas YOLO no describen RT-DETR.

## Conjuntos de datos

- **License Plate Recognition — Roboflow Universe:** detección de matrículas; el entrenamiento descarga exportación COCO. Atribución CC BY 4.0 según la [ficha del dataset](https://universe.roboflow.com/roboflow-universe-projects/license-plate-recognition-rxg4e).
- **SAVH Guayaquil ANPR Plate Images Dataset — Zenodo:** evaluación OCR ecuatoriana. El registro consultado no muestra licencia para el archivo específico; revise sus condiciones antes de redistribuirlo.

Para el inventario de otras dependencias consulte [agradecimientos y referencias](README.md#agradecimientos-y-referencias).
