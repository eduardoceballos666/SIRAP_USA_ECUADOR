# Formato heredado de anotaciones para Ecuador

Esta carpeta conserva el nombre histórico de la ruta. El detector activo es RT-DETRv2-S con inferencia OpenVINO; el entrenamiento previo usa Transformers/PyTorch y formato COCO. Si solo dispones de un dataset con cajas YOLO normalizadas, `python -m src.train --convert-yolo --data-yaml <data.yaml> --output-dir <destino>` lo transforma a COCO sin instalar ni ejecutar Ultralytics. Preferimos descargar la exportación COCO desde Roboflow.
