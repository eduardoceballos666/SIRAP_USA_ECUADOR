# Notebooks de SIRAP

Los notebooks activos ajustan **RT-DETRv2-S (ResNet-18vd)** con Transformers/PyTorch y evalúan la misma ruta de inferencia que usa la app: OpenVINO Runtime nativo en Python. El checkpoint de matrículas `merve/license-plates-rtdetrv2` declara Apache-2.0. El ajuste fino exporta un IR antes del despliegue. Ecuador tiene pipeline OCR; el notebook USA se limita a detección hasta validar reglas y OCR específicos.

| Flujo | Ecuador | Estados Unidos |
|---|---|---|
| Explorar datos | [01](ecuador/01_exploracion.ipynb) | [01](usa/01_exploracion.ipynb) |
| Preparar COCO | [02](ecuador/02_preprocesamiento.ipynb) | [02](usa/02_preprocesamiento.ipynb) |
| Entrenar y exportar RT-DETRv2-S | [03](ecuador/03_modelado.ipynb) | [03](usa/03_modelado.ipynb) |
| Optimizar | [04](ecuador/04_optimizacion.ipynb) | [04](usa/04_optimizacion.ipynb) |
| Evaluar | [05](ecuador/05_evaluacion.ipynb) | [05](usa/05_evaluacion.ipynb) |
| Evaluar OCR | [06](ecuador/06_afinamiento_ocr.ipynb) | [06](usa/06_afinamiento_ocr.ipynb) |
| Varias semillas | [07](ecuador/07_validacion_multisemilla.ipynb) | [07](usa/07_validacion_multisemilla.ipynb) |
| Inferencia | [Backend](ecuador/sirap_backend.ipynb) | [Backend](usa/sirap_backend.ipynb) |
| Ground truth de video | [Evaluación](ecuador/Evaluacion_video_ground_truth.ipynb) | [Evaluación](usa/Evaluacion_video_ground_truth.ipynb) |

Los checkpoints de cada país se guardan bajo `models/<país>/detector/rtdetrv2_s/`: `transformers/` para continuar entrenamiento y exportación; `openvino/` para inferencia. En Colab, instala los requisitos de entrenamiento y ejecuta el paso de exportación antes de usar los notebooks de inferencia. La celda opcional `publish_detector_ir` del notebook 03 envía solo el IR revisado a GitHub; GitHub Actions lo sincroniza con el Space. Si descargas desde Roboflow, configura `ROBOFLOW_API_KEY` en Secrets.

Para EE. UU. crea anotaciones del dominio local y revisa las reglas OCR. No uses el checkpoint compartido ni los resultados de Ecuador como validación estadounidense. Las versiones YOLO anteriores son históricas y no forman parte del flujo activo.
