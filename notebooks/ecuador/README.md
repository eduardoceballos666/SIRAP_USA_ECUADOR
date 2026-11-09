# Flujo de notebooks Ecuador

Este flujo ajusta RT-DETRv2-S (ResNet-18vd) con Transformers/PyTorch y exporta cada checkpoint a OpenVINO IR para la inferencia de la app. Usa como inicialización `merve/license-plates-rtdetrv2`, que declara Apache-2.0. Incluye exploración, preparación COCO, entrenamiento, optimización, evaluación del detector y OCR, validación multisemilla, inferencia y video con ground truth.

Antes de entrenar, define un dataset COCO con `train/`, `valid/` y opcionalmente `test/`; guarda las llaves de Roboflow en Secrets. Los artefactos se generan en `models/ecuador/detector/rtdetrv2_s/transformers/` y `models/ecuador/detector/rtdetrv2_s/openvino/`. Aún no hay métricas locales de Ecuador: el ajuste y la evaluación reservada están pendientes.
