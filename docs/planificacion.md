# Migración del detector SIRAP

## Objetivo

La aplicación usa **Transformers + RT-DETRv2 R18** en lugar del detector YOLO11/Ultralytics anterior. OCR, reglas de acceso, API, interfaz e historial se mantienen; Ecuador y Estados Unidos tienen rutas de checkpoint independientes para su preparación. El checkpoint compartido `merve/license-plates-rtdetrv2` tiene licencia Apache-2.0.

## Alcance técnico

- Inferencia RT-DETRv2 por Transformers en `src/model.py` y API/Space.
- Entrenamiento COCO con Transformers en `src/train.py` y evaluación en `src/evaluate.py`.
- Notebooks nuevos por país; versiones YOLO archivadas e identificadas como históricas.
- Configuración independiente Ecuador/USA, dependencias y licencias actualizadas.
- Eliminación de checkpoints YOLO del paquete activo y sincronización automática del Space.

## Estado y tareas para completar la validación

| Tema | Estado |
|---|---|
| Checkpoint de matrículas Apache-2.0 | Integrado como modelo base de la aplicación |
| Carga e inferencia Transformers | Implementada en el módulo de modelo |
| Entrenamiento y evaluación | Flujos disponibles; falta ejecutar con splits finales de cada país |
| Umbral de detección | Provisional; requiere calibración con validación RT-DETR |
| Ecuador | Falta publicar el checkpoint fino y métricas nuevas de test |
| Estados Unidos | Falta dataset representativo, ajuste, evaluación y validación OCR/reglas |
| Space HF | Se despliega desde `main` por Actions; confirmar el resultado del workflow tras publicar los cambios |

## Historial

Las etapas anteriores probaron varias familias de detectores, incluida la corrida YOLO11. Sus notebooks se mantienen en el historial de Git y sus métricas históricas en `results/` para trazabilidad; no forman parte del entrenamiento ni la inferencia activos. Las métricas históricas no se atribuyen a RT-DETR.
