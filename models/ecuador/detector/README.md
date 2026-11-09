# Detector Ecuador

`python -m src.train --country ecuador --data-dir <COCO>` entrena RT-DETRv2-S con Transformers/PyTorch y exporta OpenVINO IR. La carpeta `rtdetrv2_s/` contiene `transformers/` (checkpoint Safetensors y procesador) y `openvino/` (XML/BIN, manifest de preprocesamiento y manifest de entrenamiento). La app utiliza únicamente el IR.

Antes de adoptar estos pesos, evalúalos en un conjunto ecuatoriano reservado y registra las métricas en `detector_rtdetr_ecuador_test.json`. El checkpoint público Apache-2.0 sirve como fallback general, no como resultado validado para Ecuador.
