# Entrenamiento y optimización de RT-DETR

## Flujo vigente

El detector actual es **RT-DETRv2 R18 con Transformers**, iniciado desde `merve/license-plates-rtdetrv2` (Apache-2.0). `src/train.py` recibe un dataset COCO Detection y guarda el checkpoint de país, el procesador y `sirap_training.json`. Los pesos anteriores YOLO/Ultralytics no son compatibles con este pipeline.

Parámetros iniciales de referencia: 30 épocas, batch 8, AdamW/Trainer, tasa de aprendizaje 5e-5, weight decay 1e-4 y semilla 42. Son valores de partida, no resultados óptimos confirmados. Revisa memoria GPU, tamaño de imagen y batch en el runtime antes de correr un entrenamiento completo.

## Datos y protocolo

1. Divide datos por vehículo/captura, evitando que imágenes duplicadas o casi idénticas queden a la vez en train y test.
2. Ajusta pesos y umbral con train/validación; reserva test hasta que termine selección de hiperparámetros.
3. Usa COCO Detection con una categoría de matrícula. El convertidor desde etiquetas YOLO es solo para compatibilidad con insumos antiguos.
4. Para Ecuador y Estados Unidos, crea checkpoints, manifests y métricas independientes.
5. Guarda versión del dataset, checkpoint base, semilla, hiperparámetros, código y hardware en cada corrida.

## Búsqueda de hiperparámetros

`notebooks/<país>/04_optimizacion.ipynb` contiene un ejemplo Optuna apagado por defecto. La función objetivo usa mAP@0.5:0.95 en validación. No importes el estudio Optuna de YOLO ni compares sus valores con RT-DETR: arquitectura, preprocesamiento y pipeline de evaluación son diferentes.

## Evaluación y calibración

`src/evaluate.py detector` calcula métricas COCO, guardadas como `detector_rtdetr_<país>_<split>.json`. Usa un umbral bajo para la evaluación de mAP. Calibra el umbral operativo en validación y publica su protocolo en `umbrales_rtdetr.json`. `evaluate_end_to_end` requiere un CSV etiquetado con `image_path,plate_gt` y genera métricas del sistema completo.

Aún no se registran métricas de test RT-DETR de dominio Ecuador/USA en el repositorio. Los números YOLO que aparecen en resultados anteriores son históricos y no describen este modelo. No afirmes equivalencia ni mejora hasta volver a medir con protocolo y datos comparables.
