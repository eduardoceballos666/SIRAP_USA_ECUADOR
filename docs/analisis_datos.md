# Análisis de datos para RT-DETR

## Datos de detección

El entrenamiento usa exportación COCO Detection del proyecto de Roboflow `license-plate-recognition-rxg4e` (versión 11): imágenes de matrículas con una categoría. La exportación COCO es el formato activo. El convertidor incluido acepta temporalmente anotaciones YOLO normalizadas de datasets existentes; no usa Ultralytics ni ejecuta inferencia.

Este dataset contiene vehículos y escenas de distintas fuentes. No es una muestra representativa certificada de Ecuador ni de Estados Unidos. Cada perfil debe reunir datos etiquetados y separados por origen/vehículo, documentar cobertura, y reservar un test sin fuga de imágenes.

## Datos de OCR y evaluación local

SAVH Guayaquil aporta recortes de placas ecuatorianas para evaluar OCR, no la detección en escenas completas. Las imágenes de garita y el video de referencia permiten análisis de dominio local con su alcance descrito en `evaluation/`. Las métricas de recortes OCR, imágenes completas, detector y video deben informarse por separado.

## Preparación

- Validar integridad de imágenes y consistencia entre anotaciones y dimensiones.
- Convertir anotaciones a COCO y normalizar el id de la categoría de matrícula a una sola etiqueta.
- Revisar cajas vacías, inválidas, truncadas y duplicadas.
- Mantener la separación por vehículo, cámara y sesión de captura entre splits.
- Registrar procedencia, licencia y restricciones de redistribución para cada conjunto.

## Limitaciones y cambio de modelo

Las métricas en `results/` con origen YOLO/Ultralytics son históricas. El checkpoint RT-DETR de Hugging Face tiene licencia Apache-2.0, pero no se considera validado para los países objetivo hasta realizar ajuste fino y evaluación independiente. Las configuraciones de confianza heredadas se marcan como provisionales; se deben recalibrar en el nuevo pipeline.
