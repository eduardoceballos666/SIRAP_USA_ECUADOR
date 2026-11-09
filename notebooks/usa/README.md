# Flujo de notebooks Estados Unidos

Esta carpeta contiene el flujo RT-DETRv2-S con ajuste Transformers/PyTorch y exportación OpenVINO IR para el perfil USA. Incluye exploración, preparación COCO, entrenamiento, optimización, evaluación, OCR y validación multisemilla.

El [backend USA](sirap_backend_USA.ipynb) incluye el paso ejecutable para crear COCO desde escenas completas y cajas CSV, el entrenamiento con tres semillas, selección por mAP50-95 de validación, exportación OpenVINO y pruebas de detección, OCR, robustez y latencia.

Prepara el dataset con la [guía COCO](../../datasets/usa/detection_coco/README.md) y el [convertidor](../../scripts/usa_annotations_to_coco.py). El conjunto datasets/usa/seg_and_ocr usa groundtruth.csv y usimages para evaluar OCR sobre recortes; no contiene escenas completas para entrenar detección.

Los artefactos del perfil se guardan en models/usa/detector/rtdetrv2_s/transformers/ y models/usa/detector/rtdetrv2_s/openvino/. El checkpoint compartido merve/license-plates-rtdetrv2 declara Apache-2.0; sus métricas publicadas no acreditan desempeño en matrículas estadounidenses.