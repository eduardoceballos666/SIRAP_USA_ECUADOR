# Datasets de Estados Unidos

Este directorio separa los datos para OCR de los datos requeridos para detección.

- seg_and_ocr/: recortes de matrículas USA y groundtruth.csv para evaluación OCR.
- detection_coco/: preparación de escenas completas y cajas COCO para ajustar RT-DETRv2-S.

Para entrenar detección, sigue la [guía del dataset COCO](detection_coco/README.md). Los recortes de seg_and_ocr no reemplazan las escenas completas anotadas.

El conjunto de escenas y sus cajas debe contener splits independientes train, valid y test; conserva juntas las imágenes de la misma secuencia, cámara o vehículo.