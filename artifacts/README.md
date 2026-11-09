# Artefactos pesados de SIRAP

El repositorio contiene código, datos de referencia aprobados, métricas agregadas y notebooks. Los medios grandes se distribuyen por Releases; los registros operativos permanecen en el repositorio privado.

| Artefacto | Ubicación/estado | Uso |
|---|---|---|
| Video fuente de garita | Release `datos-garita-v1` | Evaluación solo junto a la referencia temporal correspondiente. |
| Imágenes de garita | `datasets/ecuador/gate/` | Conjunto pequeño de evaluación con referencia. |
| Recortes SAVH | Descarga desde Zenodo al runtime | Evaluación OCR por separado. |
| RT-DETRv2-S / OpenVINO IR | Checkpoint Hugging Face `merve/license-plates-rtdetrv2`; ajuste fino local bajo `models/<país>/detector/rtdetrv2_s/` | Apache-2.0; checkpoints de entrenamiento en `transformers/`, archivos de inferencia en `openvino/`. |
| Corridas y resultados YOLO | Historial de Git y artefactos históricos de `results/` | Solo referencia histórica; no son salidas del detector vigente. |

Para Roboflow, configura `ROBOFLOW_API_KEY` en Secrets de Colab. Descarga salidas nuevas desde el runtime; no se publican automáticamente pesos o datos privados.
