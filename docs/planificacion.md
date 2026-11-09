# Migración del detector SIRAP

## Objetivo

La aplicación usa **RT-DETRv2-S (ResNet-18vd)** y **OpenVINO Runtime nativo en Python** para la inferencia de detección. El checkpoint de placas `merve/license-plates-rtdetrv2` declara Apache-2.0. El ajuste fino se realiza previamente con Transformers/PyTorch; la app recibe archivos OpenVINO IR. OCR, reglas de acceso, API, interfaz e historial continúan como componentes separados.

## Alcance técnico

- Inferencia RT-DETRv2-S mediante `openvino.Core` en `src/model.py`.
- Entrenamiento COCO con Transformers/PyTorch en `src/train.py` y exportación IR con `src/export_openvino.py`.
- Notebooks Ecuador y EE. UU. para preparación, entrenamiento, optimización y evaluación.
- Artefactos por país guardados en `models/<país>/detector/rtdetrv2_s/`.
- Space Docker con etapa de conversión previa y runtime final sin Torch ni Transformers.
- Dependencias runtime y de entrenamiento separadas; licencias y avisos documentados.

## Estado y tareas para completar la validación

| Tema | Estado |
|---|---|
| Checkpoint de matrículas Apache-2.0 | Integrado como fuente de inicialización general |
| Inferencia OpenVINO Runtime | Implementada para cargar XML/BIN de OpenVINO IR |
| Conversión | Implementada en `src/export_openvino.py`; el build Docker genera el IR compartido |
| Entrenamiento y evaluación | Flujos disponibles; falta ejecutar con los splits finales de cada país |
| Umbral de detección | Provisional; requiere calibración con validación del IR correspondiente |
| Ecuador | Falta publicar el IR fino y las métricas nuevas de test |
| Estados Unidos | Falta dataset representativo, ajuste, evaluación y validación OCR/reglas |
| Space HF | Se despliega desde `main` por Actions; hay que confirmar el resultado tras publicar |

## Historial

Las etapas anteriores probaron varias familias de detectores, incluida YOLO11. Sus notebooks y métricas se mantienen para trazabilidad histórica; no forman parte del entrenamiento ni de la inferencia activos. Las métricas históricas no se atribuyen a RT-DETRv2-S.
