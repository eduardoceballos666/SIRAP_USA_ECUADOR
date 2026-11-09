# Avisos de componentes y recursos de terceros

La licencia [Apache License 2.0](LICENSE) cubre el código original de SIRAP_USA_ECUADOR en esta versión. El aviso de autoría está en [NOTICE](NOTICE). Las versiones publicadas anteriormente bajo MIT conservan los términos de esa licencia. Cada modelo, biblioteca y conjunto de datos mantiene sus propios términos.

## Detector y bibliotecas

- **Checkpoint `merve/license-plates-rtdetrv2`:** RT-DETRv2-S para detección de matrículas, publicado en Hugging Face bajo **Apache-2.0**. [Ficha del modelo](https://huggingface.co/merve/license-plates-rtdetrv2). El modelo se basa en `PekingU/rtdetr_v2_r18vd`.
- **Checkpoint base `PekingU/rtdetr_v2_r18vd`:** RT-DETRv2 con backbone ResNet-18vd; Apache-2.0. [Ficha del modelo](https://huggingface.co/PekingU/rtdetr_v2_r18vd).
- **OpenVINO Runtime:** carga y ejecuta el IR en la aplicación; Apache-2.0. [Licencia y distribución](https://github.com/openvinotoolkit/openvino/blob/master/LICENSE).
- **Transformers y PyTorch:** usados para entrenamiento y exportación previos al despliegue, no para inferencia del detector en la app; conservan sus licencias respectivas.
- **ONNX Runtime:** motor del componente OCR `fast-plate-ocr`; licencia MIT.
- **fast-plate-ocr:** reconocimiento óptico de caracteres (OCR), MIT.
- **OpenCV (`opencv-python-headless`):** lectura y conversión de imágenes/video. Apache-2.0 ([licencia](https://github.com/opencv/opencv/blob/4.12.0/LICENSE)).

Los checkpoints finos producidos a partir del modelo Apache-2.0 deben conservar la atribución y avisos aplicables a sus fuentes. Las métricas históricas YOLO no describen RT-DETRv2-S.

## Conjuntos de datos

- **European + USA License plates — Roboflow Universe, por PlateBlur:** versión 1, Instance Segmentation; el notebook descarga COCO Segmentation y usa las cajas para detección. Mantenga la atribución CC BY 4.0 indicada en la [ficha del dataset](https://universe.roboflow.com/plateblur/european-usa-license-plates).
- **SAVH Guayaquil ANPR Plate Images Dataset — Zenodo:** evaluación OCR ecuatoriana. El registro consultado no muestra licencia para el archivo específico; revise sus condiciones antes de redistribuirlo.

Para el inventario de otras dependencias consulte [agradecimientos y referencias](README.md#agradecimientos-y-referencias).
