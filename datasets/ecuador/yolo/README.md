# Formato heredado de anotaciones para Ecuador

Esta carpeta conserva el nombre histórico de la ruta. El detector activo usa Transformers + RT-DETRv2 R18 y entrenamiento COCO. Si solo dispones de un dataset con cajas YOLO normalizadas, `python -m src.train --convert-yolo --data-yaml <data.yaml> --output-dir <destino>` lo transforma a COCO sin instalar ni ejecutar Ultralytics. Preferimos descargar la exportación COCO desde Roboflow.
