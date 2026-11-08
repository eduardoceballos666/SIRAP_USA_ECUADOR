**Purpose:** evaluation/ecuador/savh/artifacts/ocr/afinamiento/README.md contains project files and instructions. This description is in English.

> Purpose: Project documentation and instructions for evaluation/ecuador/savh/artifacts/ocr/afinamiento.

# Modelos experimentales OCR SAVH

Se publican las copias originales de `ocr_afinado.onnx` (4.899.290 bytes) y `ocr_afinado.keras` (16.238.682 bytes) divididas en 3 y 9 partes binarias, respectivamente, debido a los límites del mecanismo de transferencia utilizado. Las partes no son texto base64 ni se han modificado.

Desde una copia de esta carpeta ejecutar:

```bash
python restaurar_modelos.py
```

Se reconstruyen los dos modelos y se verifican con SHA-256. No son los pesos publicados en Hugging Face ni representan un nuevo despliegue.


## English

This folder contains OCR tuning metadata and evidence for the Ecuador SAVH experiments. The large archived model parts are stored under `models/ecuador/ocr/archive/`.
