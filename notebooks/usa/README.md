# Flujo de notebooks Estados Unidos

Esta carpeta contiene el flujo RT-DETRv2 R18 con Transformers para el perfil USA: exploración, preparación COCO, entrenamiento, optimización, evaluación, OCR, validación multisemilla, inferencia detector-only; la evaluación de video y el flujo OCR punta a punta quedan pendientes de etiquetas y reglas USA validadas. El checkpoint compartido `merve/license-plates-rtdetrv2` tiene licencia Apache-2.0, pero sus métricas no acreditan desempeño en placas de EE. UU.

Define datos COCO representativos de Estados Unidos y conserva test para la evaluación final. Los checkpoints se guardan bajo `models/usa/detector/rtdetr_r18/`. La instancia web actual usa la configuración Ecuador; el perfil USA aún requiere normalización y reglas OCR antes de integrarse a decisiones de acceso. Las versiones YOLO originales permanecen en el historial de Git.
