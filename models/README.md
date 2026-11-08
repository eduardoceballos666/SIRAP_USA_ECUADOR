# Modelos SIRAP / SIRAP Models

Los modelos se separan por país para que cambiar la configuración activa no reemplace los pesos de Ecuador.

| País | Detector PyTorch | Detector ONNX | OCR afinado (opcional) |
|---|---|---|---|
| Ecuador | `models/ecuador/detector/ecuador_best.pt` | `models/ecuador/detector/ecuador_best.onnx` | `models/ecuador/ocr/ecuador_ocr.onnx` y `ecuador_ocr_plate_config.yaml` |
| Estados Unidos | `models/usa/detector/usa_best.pt` | `models/usa/detector/usa_best.onnx` | `models/usa/ocr/usa_ocr.onnx` y `usa_ocr_plate_config.yaml` |

Los pesos de Ecuador están publicados y son los que referencia `config/countries/ecuador.yaml`. El experimento de afinamiento OCR ecuatoriano no se recomienda para uso en la app; sus artefactos están archivados. Aún no hay pesos estadounidenses designados ni publicados. No renombres ni copies el modelo de Ecuador como si fuera un modelo de EE. UU.

## Exportar el detector ecuatoriano

`python -m src.train --export-only models/ecuador/detector/ecuador_best.pt` actualiza la exportación en la misma carpeta de Ecuador. Las corridas experimentales deben conservar nombres de candidato, por ejemplo `ecuador_candidate_completo.pt`, hasta que se decida adoptar una nueva versión.

## OCR

La app usa el OCR general `cct-s-v2-global-model` mientras no existan los dos archivos OCR afinados indicados en la configuración de ese país. Un OCR afinado solo se activa para el país cuya configuración apunte a sus archivos.
