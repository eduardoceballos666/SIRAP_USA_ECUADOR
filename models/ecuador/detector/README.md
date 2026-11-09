# Detector RT-DETR para Ecuador

Ruta de salida del entrenamiento Transformers: `models/ecuador/detector/rtdetr_r18/`. Los notebooks y `python -m src.train --country ecuador --data-dir <COCO>` generan el checkpoint y su manifest. Antes de adoptar los pesos, evalúalos en un conjunto ecuatoriano reservado y registra las métricas `detector_rtdetr_ecuador_test.json`.

Si aún no hay checkpoint local, SIRAP carga el checkpoint compartido `merve/license-plates-rtdetrv2` (Apache-2.0); su uso provisional no debe describirse como un modelo entrenado o validado en Ecuador.
