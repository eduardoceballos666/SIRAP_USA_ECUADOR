# Dataset COCO de detección — Estados Unidos

Este directorio prepara el dataset de escenas completas USA que necesita el detector RT-DETRv2-S.

## Diferencia entre detección y OCR

Las imágenes de datasets/usa/seg_and_ocr/usimages son recortes de matrículas con texto real en groundtruth.csv. Sirven para medir OCR; no contienen vehículos completos ni cajas de matrícula dentro de una escena. No las uses como sustituto de escenas para entrenar el detector.

## Preparación

1. Copia escenas completas con vehículos a source_images/. Puedes usar imágenes fijas o cuadros seleccionados de cámaras, siempre que tengas permiso para usarlos.
2. Copia annotations_template.csv como annotations.csv.
3. Anota una fila por cada caja de matrícula usando coordenadas en píxeles: x, y, width, height. El recuadro debe ajustarse a la matrícula.
4. Escribe train, valid o test en split. Conserva todos los cuadros de la misma sesión, secuencia, cámara o vehículo en un único split.
5. Escribe un source_group estable para cada secuencia o vehículo. Las escenas negativas llevan una fila con las cuatro coordenadas vacías.
6. En Colab, ejecuta la celda de conversión del notebook USA o este comando:

    python scripts/usa_annotations_to_coco.py --images-dir datasets/usa/detection_coco/source_images --annotations-csv datasets/usa/detection_coco/annotations.csv --output-dir datasets/usa/detection_coco

El convertidor comprueba archivos, dimensiones, cajas dentro de la imagen, grupos entre particiones y duplicados exactos; luego copia las escenas y genera _annotations.coco.json para train, valid y test. El notebook consume esa raíz mediante DATA_DIR.

## Columnas del CSV

| Columna | Contenido |
|---|---|
| image_file | Nombre o ruta relativa a source_images/ |
| split | train, valid o test |
| source_group | Identificador de sesión, cámara, recorrido o vehículo para evitar fuga entre splits |
| x, y | Esquina superior izquierda de la caja, en píxeles |
| width, height | Ancho y alto de la caja, en píxeles |

Las imágenes y anotaciones no vienen incluidas: deben cargarse y etiquetarse por el equipo. El repositorio conserva la plantilla y el proceso de conversión.