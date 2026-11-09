# Entrenamiento, exportación y optimización

## Flujo vigente

SIRAP usa **RT-DETRv2-S (ResNet-18vd)**. El checkpoint Apache-2.0 [`merve/license-plates-rtdetrv2`](https://huggingface.co/merve/license-plates-rtdetrv2) sirve como inicialización general de matrículas. `src/train.py` ajusta el modelo con PyTorch/Transformers usando un dataset COCO Detection; al terminar, exporta los pesos finos a OpenVINO IR con `src/export_openvino.py`. La app ejecuta ese IR con OpenVINO Runtime nativo en Python.

Los artefactos quedan en `models/<país>/detector/rtdetrv2_s/transformers/` y `models/<país>/detector/rtdetrv2_s/openvino/`. El entrenamiento requiere `requirements-training.txt` o las dependencias de Colab; el runtime de la app se define en `requirements.txt`. La imagen Docker descarga y convierte el checkpoint compartido durante el build, y el runtime final no instala PyTorch ni Transformers.

Parámetros iniciales de referencia: 30 épocas, batch 8, AdamW/Trainer, tasa de aprendizaje 5e-5, weight decay 1e-4 y semilla 42. Son valores de partida, no resultados óptimos confirmados. Revisa memoria GPU, tamaño de imagen y batch antes de entrenar.

## Datos y protocolo

1. Divide datos por vehículo/captura, evitando que imágenes duplicadas o casi idénticas queden a la vez en train y test.
2. Ajusta pesos y umbral con train/validación; reserva test hasta que termine la selección de hiperparámetros.
3. Usa COCO Detection con una categoría de matrícula. El convertidor desde etiquetas YOLO solo admite formato rectangular y sirve para insumos antiguos.
4. Entrena variantes independientes para Ecuador y EE. UU.; no intercambies sus pesos ni métricas.
5. Guarda versión del dataset, checkpoint base, semilla, hiperparámetros, código y hardware en cada corrida.
6. Conserva el checkpoint Transformers y el IR exportado juntos; el manifest `sirap_openvino.json` registra arquitectura, licencia de origen y preprocesamiento.

## Búsqueda de hiperparámetros

`notebooks/<país>/04_optimizacion.ipynb` contiene un ejemplo Optuna apagado por defecto. La función objetivo usa mAP@0.5:0.95 en validación. Cada prueba exporta un IR OpenVINO para que la evaluación mida la misma ruta de inferencia que usa la app. No importes el estudio Optuna de YOLO ni compares sus valores directamente con RT-DETR.

## Evaluación y calibración

`src/evaluate.py detector` usa el runtime OpenVINO para calcular métricas COCO y las guarda como `detector_rtdetr_<país>_<split>.json`. Usa un umbral bajo para mAP; calibra el umbral operativo en validación y publica el protocolo en `umbrales_rtdetr.json`. `evaluate_end_to_end` requiere un CSV con `image_path,plate_gt` y mide el sistema completo, incluido OCR.

Aún no se registran métricas de test RT-DETR de dominio Ecuador/EE. UU. en el repositorio. Los números YOLO de informes anteriores son históricos y no describen este modelo. No afirmes equivalencia ni mejora hasta volver a medir con datos y protocolo comparables.
