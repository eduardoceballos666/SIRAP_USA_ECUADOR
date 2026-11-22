# Detector Estados Unidos

El detector vigente no se guarda aquí: se descarga del repositorio privado y se verifica al iniciar (ver [models/README.md](../../README.md)). `rtdetrv2_s/openvino/` conserva un IR de una corrida de prueba anterior (semilla 1, 64 imágenes de entrenamiento) que la aplicación no carga.

Los candidatos nuevos se entrenan con [`notebooks/usa/sirap_backend_usa.ipynb`](../../../notebooks/usa/sirap_backend_usa.ipynb) o `src/train.py` (salida: `models/usa/detector/rtdetrv2_s/`) y no reemplazan al vigente sin un cambio explícito de `selected_checkpoint.json`.
