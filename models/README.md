# Modelos SIRAP

La app ejecuta **RT-DETRv2-S (ResNet-18vd)** con OpenVINO Runtime Python. El checkpoint compartido `merve/license-plates-rtdetrv2` declara Apache-2.0; el Dockerfile lo convierte a OpenVINO IR durante la construcción si no hay un artefacto compartido ya publicado.

| Perfil | Artefactos | Estado |
|---|---|---|
| Ecuador | `models/ecuador/detector/rtdetrv2_s/transformers/` y `models/ecuador/detector/rtdetrv2_s/openvino/` | Se generan al entrenar con datos ecuatorianos; falta publicar y validar el modelo nacional. |
| Estados Unidos | `models/usa/detector/rtdetrv2_s/transformers/` y `models/usa/detector/rtdetrv2_s/openvino/` | Ruta independiente; requiere datos, ajuste y validación de placas estadounidenses. |
| Compartido | `models/shared/detector/rtdetrv2_s/openvino/` | IR de respaldo creado desde el checkpoint Apache-2.0 para la app/Space. No valida desempeño por país. |

`transformers/` contiene los pesos Safetensors y el procesador usados para entrenamiento/exportación. `openvino/` contiene `openvino_model.xml`, `openvino_model.bin`, `sirap_openvino.json` y, para modelos finos, `sirap_training.json`. La aplicación solo carga el IR. Los artefactos generados están excluidos de Git por defecto; para publicarlos junto con la app, ejecuta la celda opcional del notebook 03 (`publish_detector_ir`) después de revisar el entrenamiento. El commit activa GitHub Actions, que sincroniza ese IR con el Space. El OCR sigue separado y usa `fast-plate-ocr` salvo que la configuración indique archivos afinados válidos.
