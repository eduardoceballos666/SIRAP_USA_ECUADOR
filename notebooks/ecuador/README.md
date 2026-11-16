# Notebook de Ecuador

El notebook activo es [sirap_backend_ecuador.ipynb](sirap_backend_ecuador.ipynb).
Puedes [abrirlo en Colab](https://colab.research.google.com/github/eduardoceballos666/SIRAP_USA_ECUADOR/blob/main/notebooks/ecuador/sirap_backend_ecuador.ipynb).

Integra RT-DETRv2-S, OCR con reglas ecuatorianas y OpenVINO. Su índice y orden de ejecución
usan secciones consecutivas del 0 al 9:

| Sección | Contenido |
|---|---|
| 0 | Dependencias, rutas Ecuador, controles y persistencia opcional. |
| 1 | Escenas COCO Ecuador, revisión de particiones y recortes SAVH Guayaquil. |
| 2 | Normalización de placas y referencia SAVH revisada. |
| 3 | Entrenamiento opcional, selección del modelo, lista CSV y regla de decisión del experimento. |
| 4 | Carga del IR OpenVINO y pipeline Ecuador. |
| 5 | Prueba básica de inferencia; no mide exactitud. |
| 6 | Video de demostración y consultas opcionales SRI/propietario. |
| 7 | Puente Cloudflare, lector, conexión, sesión de cámara y ejecutor local. |
| 8 | Medición de latencia del detector en CPU sobre validación. |
| 9 | Publicación opcional del bundle IR revisado. |

Prepara escenas ecuatorianas anotadas bajo `datasets/ecuador/detection_coco/`, con `train/`,
`valid/` (o `val/`) y sus JSON COCO; reserva `test/` para evaluación independiente. Los recortes
SAVH sirven para revisar OCR y no sustituyen escenas completas para entrenar el detector.

El entrenamiento opcional parte de `merve/license-plates-rtdetrv2`, usa un máximo de 30 épocas,
paciencia 8 y semilla 2, y selecciona por pérdida de validación. Guarda el candidato
Transformers/OpenVINO en `/content/SIRAP_workspace/ecuador/models/detector/rtdetrv2_s/seed_2/`.
La sección 9 prepara únicamente el IR en `models/ecuador/detector/rtdetrv2_s/openvino/` del clon
GitHub. Los resultados agregados del notebook usan `results/ecuador/metrics/`.

Entrenamiento, inferencia, video, conexiones, consultas externas y publicación empiezan
desactivados. La cámara exige un IR Ecuador y el informe de calibración vinculado a sus
hashes XML/BIN, descrito en 3.2. No se importan métricas USA como resultados Ecuador ni se
ejecuta el test independiente al preparar este notebook. La configuración de pesos de la
aplicación se gestiona aparte del archivo de investigación.
