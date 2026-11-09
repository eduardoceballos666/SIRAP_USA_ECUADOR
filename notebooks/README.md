# Notebooks de SIRAP

Los notebooks activos utilizan **Transformers + RT-DETRv2 R18** y el checkpoint de matrículas `merve/license-plates-rtdetrv2` (Apache-2.0). Ecuador tiene pipeline de inferencia con el OCR existente; el notebook USA se limita a detección hasta completar reglas OCR específicas. El entrenamiento de cada perfil guarda una variante bajo `models/<país>/detector/rtdetr_r18/`. Las versiones YOLO anteriores están disponibles en el historial de Git y no forman parte del flujo activo.

| Flujo | Ecuador | Estados Unidos |
|---|---|---|
| Explorar datos | [01](ecuador/01_exploracion.ipynb) | [01](usa/01_exploracion.ipynb) |
| Preparar COCO | [02](ecuador/02_preprocesamiento.ipynb) | [02](usa/02_preprocesamiento.ipynb) |
| Entrenar RT-DETR | [03](ecuador/03_modelado.ipynb) | [03](usa/03_modelado.ipynb) |
| Optimizar | [04](ecuador/04_optimizacion.ipynb) | [04](usa/04_optimizacion.ipynb) |
| Evaluar | [05](ecuador/05_evaluacion.ipynb) | [05](usa/05_evaluacion.ipynb) |
| Evaluar OCR | [06](ecuador/06_afinamiento_ocr.ipynb) | [06](usa/06_afinamiento_ocr.ipynb) |
| Varias semillas | [07](ecuador/07_validacion_multisemilla.ipynb) | [07](usa/07_validacion_multisemilla.ipynb) |
| Inferencia | [Backend](ecuador/sirap_backend.ipynb) | [Backend](usa/sirap_backend.ipynb) |
| Ground truth de video | [Evaluación](ecuador/Evaluacion_video_ground_truth.ipynb) | [Evaluación](usa/Evaluacion_video_ground_truth.ipynb) |

Configura `ROBOFLOW_API_KEY` en Secrets de Colab si descargas desde Roboflow. Para EE. UU. crea anotaciones del dominio local y revisa las reglas de OCR: no interpretes el checkpoint compartido ni los resultados de Ecuador como validación estadounidense. Los modelos por país deben entrenarse y evaluarse de forma independiente.
