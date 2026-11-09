# Flujo de notebooks Ecuador

El flujo activo ajusta y evalúa RT-DETRv2 R18 mediante Transformers. Consulta el checkpoint `merve/license-plates-rtdetrv2` (Apache-2.0). Los notebooks de esta carpeta cubren exploración, preparación COCO, entrenamiento, optimización, evaluación de detector, evaluación OCR, validación multisemilla, inferencia y video con ground truth.

Antes de entrenar, define una carpeta de datos COCO con `train/`, `valid/` y opcionalmente `test/`; las llaves de Roboflow deben ir en Secrets. Los artefactos por país se guardan bajo `models/ecuador/detector/rtdetr_r18/`. No hay métricas locales RT-DETR específicas de Ecuador hasta completar ajuste y evaluación reservada. Las versiones YOLO originales permanecen en el historial de Git.
