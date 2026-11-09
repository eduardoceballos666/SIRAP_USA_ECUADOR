# Notebooks de SIRAP

Los notebooks activos ajustan RT-DETRv2-S (ResNet-18vd) con Transformers/PyTorch y evalúan la inferencia con OpenVINO Runtime nativo en Python. El checkpoint de matrículas merve/license-plates-rtdetrv2 declara Apache-2.0. El ajuste fino exporta un IR antes del despliegue.

| Flujo | Ecuador | Estados Unidos |
|---|---|---|
| Explorar datos | [01](ecuador/01_exploracion.ipynb) | [01](usa/01_exploracion.ipynb) |
| Preparar COCO | [02](ecuador/02_preprocesamiento.ipynb) | [02](usa/02_preprocesamiento.ipynb) |
| Entrenar y exportar RT-DETRv2-S | [03](ecuador/03_modelado.ipynb) | [03](usa/03_modelado.ipynb) |
| Optimizar | [04](ecuador/04_optimizacion.ipynb) | [04](usa/04_optimizacion.ipynb) |
| Evaluar | [05](ecuador/05_evaluacion.ipynb) | [05](usa/05_evaluacion.ipynb) |
| Evaluar OCR | [06](ecuador/06_afinamiento_ocr.ipynb) | [06](usa/06_afinamiento_ocr.ipynb) |
| Varias semillas | [07](ecuador/07_validacion_multisemilla.ipynb) | [07](usa/07_validacion_multisemilla.ipynb) |
| Backend e inferencia completa | [Backend](ecuador/sirap_backend.ipynb) | [Backend USA](usa/sirap_backend_USA.ipynb) |
| Evaluación adicional de Ecuador | [Notebook](ecuador/Evaluacion_video_ground_truth.ipynb) | — |

Los modelos se guardan bajo models/<país>/detector/rtdetrv2_s/: transformers/ para continuar el ajuste y openvino/ para inferencia. La celda opcional publish_detector_ir del notebook 03 envía el IR revisado a GitHub; GitHub Actions lo sincroniza con el Space. Si descargas datos de Roboflow, configura ROBOFLOW_API_KEY en Secrets.

El backend USA usa exclusivamente las escenas anotadas que se configuren en COCO y el conjunto de recortes de datasets/usa/seg_and_ocr para evaluar OCR. No mezcles métricas ni imágenes entre países.