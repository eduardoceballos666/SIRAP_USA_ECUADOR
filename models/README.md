# Modelos SIRAP

El detector de la aplicación Ecuador se ejecuta con **Transformers + RT-DETRv2 R18**. El checkpoint público `merve/license-plates-rtdetrv2` tiene licencia Apache-2.0 y se carga automáticamente cuando no existe un ajuste fino local.

| Perfil | Checkpoint local | Estado |
|---|---|---|
| Ecuador | `models/ecuador/detector/rtdetr_r18/` | El flujo de entrenamiento lo crea; requiere ajuste y validación local antes de presentarlo como modelo ecuatoriano. |
| Estados Unidos | `models/usa/detector/rtdetr_r18/` | Ruta independiente; requiere datos, ajuste y validación de placas estadounidenses. |
| Compartido | `merve/license-plates-rtdetrv2` en Hugging Face | RT-DETRv2 R18 para matrículas; Apache-2.0. No es una validación del dominio de cada país. |

La API de la app carga por defecto `config/countries/ecuador.yaml`; el directorio USA se reserva para el entrenamiento independiente hasta completar integración de OCR y reglas. Cada checkpoint fino incluye `config.json`, pesos Safetensors, procesador y `sirap_training.json`. No cargues archivos `.pt` o `.onnx` de YOLO como si fueran pesos Transformers. OCR se mantiene separado y sigue usando `fast-plate-ocr` salvo que la configuración indique archivos afinados válidos.
