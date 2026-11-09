# Datos de SIRAP

| Carpeta | Contenido | Publicación |
|---|---|---|
| `raw/` | Descargas originales de Roboflow y SAVH | No se versionan; el notebook o `src/train.py` las descarga al entorno de trabajo. |
| `processed/` | Datos locales temporales y CSV de trabajo | Los registros de producción se guardan en el repositorio privado. |
| `samples/` | Imágenes sintéticas para probar la interfaz | Sí. No forman parte de la evaluación del modelo. |

## Detección de placas

La fuente de Roboflow `roboflow-universe-projects/license-plate-recognition-rxg4e`, versión 11, tiene 10.125 imágenes y una clase de matrícula. El entrenamiento activo solicita exportación **COCO Detection** y ajusta RT-DETRv2-S con Transformers/PyTorch; la app usa el IR OpenVINO correspondiente. El dataset enseña detección general de matrículas, no representa por sí solo a Ecuador ni a Estados Unidos. Las etiquetas YOLO heredadas solo se admiten como formato de entrada opcional para convertirlas a COCO; no se usa el detector Ultralytics.

## SAVH Guayaquil

El [dataset SAVH en Zenodo](https://zenodo.org/records/21120307) contiene recortes de matrículas ecuatorianas. Se utiliza para evaluar OCR de forma separada del detector. El registro consultado no muestra licencia para el archivo específico; revise sus condiciones antes de redistribuirlo.

## Garita e historial operativo

Las imágenes autorizadas de la garita y sus referencias se describen en `datasets/ecuador/gate/` y `evaluation/ecuador/`. La referencia de video solo permite evaluar intervalos anotados y no estima falsos negativos fuera de ellos. Los datos operativos, credenciales y eventos enriquecidos se almacenan en `SIRAP_datos_privados`; no se publiquen en este repositorio.

## Métricas y límites

Los archivos existentes con nombres `*yolo11*`, junto con `detector_test.json`, `entrenamiento.json` y `umbrales.json`, son históricos y no se muestran como evaluación RT-DETR. Los resultados nuevos usan nombres `*_rtdetr*`; no habrá métricas del modelo por país hasta ajustar y evaluar ese perfil con datos reservados.
