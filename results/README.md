# Resultados y métricas

## Métricas vigentes de RT-DETR

Los comandos de `src/evaluate.py` guardan los resultados nuevos con nombres `*_rtdetr*.json` en esta carpeta. Por ejemplo, la evaluación COCO produce `detector_rtdetr_<país>_<split>.json`; el entrenamiento genera `entrenamiento_rtdetr.json`. Los resultados solo serán válidos después de definir dataset, partición, checkpoint y protocolo en cada archivo.

A la fecha de esta migración no hay métricas de test RT-DETR específicas de Ecuador ni de Estados Unidos versionadas en el repositorio. El modelo público de matrículas sirve de checkpoint inicial; no equivale a un modelo validado para esos países. Los umbrales de detección heredados de YOLO no se reutilizan: los valores de configuración están marcados como provisionales y deben calibrarse en validación.

## Artefactos YOLO históricos

Los CSV, JSON y gráficos existentes cuyo nombre, contenido o fuente indica YOLO/Ultralytics pertenecen a corridas anteriores. También son históricos `detector_test.json`, `entrenamiento.json`, `entrenamiento_yolo11_*.json`, `e2e.json`, `velocidad.json`, `umbrales.json`, los logs de decisiones y las figuras YOLO. No se deben mostrar, comparar ni atribuir al checkpoint RT-DETR. Las versiones anteriores de notebooks se conservan en el historial de Git.

## Datos y privacidad

Los registros de acceso de producción se mantienen en `SIRAP_datos_privados`. No agregues CSV operativos ni imágenes de matrículas identificables a este repositorio. Las referencias de evaluación publicadas deben conservar el alcance y las limitaciones descritos en `evaluation/`.
