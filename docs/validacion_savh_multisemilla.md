# Protocolo de validación de RT-DETR por semillas

## Estado actual

Las corridas multisemilla de YOLO11 que existían antes de la migración son históricas y no describen RT-DETR. No hay todavía resultados multisemilla RT-DETR publicados. El notebook activo `notebooks/ecuador/07_validacion_multisemilla.ipynb` sirve como plantilla de ejecución; queda apagado por defecto para evitar entrenamientos costosos accidentales.

## Protocolo recomendado

1. Fijar versiones de código, Transformers, PyTorch, dataset COCO y checkpoint base Apache-2.0.
2. Definir antes de entrenar las configuraciones base y candidata; usar semillas emparejadas (por ejemplo, 0, 1, 2).
3. Seleccionar hiperparámetros exclusivamente con train/validación.
4. Guardar un checkpoint y manifest independientes por semilla.
5. Evaluar una sola vez en test reservado, salvo que el protocolo aprobado indique otra cosa.
6. Informar mAP50:95, mAP50, precisión, recall, tamaño de muestra, tiempo/hardware y las diferencias pareadas; no confundir una media descriptiva con significación estadística.
7. Publicar nuevas métricas con sufijo `rtdetr`, junto con el protocolo y límites del dataset.

Ecuador y Estados Unidos requieren estudios independientes. SAVH se usa para evaluar OCR de recortes; no reemplaza un conjunto de detección ni una evaluación punta a punta.
