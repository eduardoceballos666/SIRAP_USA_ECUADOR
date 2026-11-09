# Flujo de notebooks Estados Unidos

Esta carpeta contiene el flujo RT-DETRv2-S con ajuste Transformers/PyTorch y exportación OpenVINO IR para el perfil USA. Incluye exploración, preparación COCO, entrenamiento, optimización, evaluación, OCR, validación multisemilla e inferencia detector-only. La evaluación de video y el flujo OCR punta a punta requieren etiquetas y reglas USA validadas. El checkpoint compartido `merve/license-plates-rtdetrv2` declara Apache-2.0, pero sus métricas no acreditan desempeño en placas de EE. UU.

Define datos COCO representativos y conserva `test` para la evaluación final. Los artefactos se guardan en `models/usa/detector/rtdetrv2_s/transformers/` y `models/usa/detector/rtdetrv2_s/openvino/`. La instancia web usa Ecuador como perfil predeterminado; el perfil USA aún requiere normalización y reglas OCR antes de integrarse a decisiones de acceso.
