# Datos de SIRAP: fuentes, preparación y límites

Resume de dónde salen los datos con los que se entrenó, se comprobó y se opera SIRAP, y qué se puede concluir de cada uno. El inventario de carpetas está en [`data/README.md`](../data/README.md) y en `datasets/`.

## Fuentes

| Uso | Fuente | Qué se hizo con ella | Qué **no** demuestra |
|---|---|---|---|
| Entrenar y validar el detector | [European + USA License plates](https://universe.roboflow.com/plateblur/european-usa-license-plates) (Roboflow, versión 1; segmentación con tres etiquetas de placas) | Se toman las cajas `bbox`, se ignoran las máscaras y se unifican las etiquetas en una clase `license_plate` (COCO Detection). Las divisiones se reagrupan por fuente de origen y se retiran duplicados exactos (9 068 imágenes de entrenamiento y 534 de validación en el experimento de tres semillas) | Desempeño en Ecuador ni en una garita concreta; no es una muestra representativa certificada de ningún país. No es el conjunto con el que se ajustó el checkpoint desplegado (fila siguiente) |
| Ajustar el checkpoint desplegado (semilla 2) | Conjunto de recuperación `recovery_coco_20261114`: 249 imágenes de entrenamiento (192 con placa, 57 negativas) y 79 de validación (41 con placa, 38 negativas); grabaciones de una cámara objetivo (23 de marzo para entrenar, 19 de marzo para validar) y un paquete de negativos (corrida `20261114T210050Z`) | Se ajustó a partir de un checkpoint de EE. UU. anterior; detalle en [optimizacion.md](optimizacion.md) | Su procedencia y licencia **no están documentadas en este repositorio**; deben confirmarse antes de comercializar el modelo. Tampoco demuestra desempeño en Ecuador |
| OCR de recortes de EE. UU. | Conjunto `seg_and_ocr` de [`openalpr/benchmarks`](https://github.com/openalpr/benchmarks) (751 recortes con `groundtruth.csv`; **AGPL-3.0, no se redistribuye**, ver `datasets/usa/seg_and_ocr/README.md`) | Evaluación del OCR y de la lectura del estado, por separado del detector | Detección en escenas completas ni un test independiente |
| OCR de recortes de Ecuador | [SAVH Guayaquil](https://zenodo.org/records/21120307) (recortes de matrículas ecuatorianas, predominan placas de Guayas) | Evaluación del OCR por separado del detector | Detección, otras provincias, motos |
| Comprobación de desarrollo de EE. UU. | Ocho fotos revisadas por una persona, más recortes con estado conocido para la lectura del estado | Diagnóstico por la API real (matrícula, estado, detección) | Un test independiente: las fotos se reutilizaron y los recortes de un mismo estado comparten diseño |
| Garita de Ecuador | Imágenes y video de referencia en `datasets/ecuador/gate/` y `evaluation/ecuador/` | Análisis de dominio local, con el alcance de cada referencia | Falsos negativos fuera de los intervalos anotados |
| Interfaz y manuales | `data/samples/` (cuatro imágenes de demostración) y las operaciones de origen `DEMO` | Probar y mostrar la interfaz | Cualquier métrica del modelo |
| Operación | Vehículos, autorizaciones, propietarios, garitas, usuarios y operaciones en CSV, respaldados en el repositorio privado `SIRAP_datos_privados` | Funcionamiento y auditoría de la aplicación | No se publican; las imágenes procesadas no se guardan |

Las métricas de recortes OCR, imágenes completas, detector y video se informan **por separado**: tienen alcances y denominadores distintos y no se combinan en un solo porcentaje. Las cifras vigentes están en [`results/README.md`](../results/README.md).

## Preparación

- Validar la integridad de las imágenes y la coherencia entre anotaciones y dimensiones.
- Convertir las anotaciones a COCO y normalizar la categoría a una sola etiqueta de matrícula.
- Revisar cajas vacías, inválidas, truncadas y duplicadas.
- Mantener juntas las imágenes del mismo vehículo, cámara o sesión antes de dividir en entrenamiento, validación y test, para evitar fuga entre divisiones.
- Registrar procedencia, licencia y restricciones de redistribución de cada conjunto ([THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md)). Los datos descargados (`data/raw/`) y las imágenes reales de garita no se versionan.

## Límites que conviene recordar

- El detector se ajustó con placas de EE. UU. y Europa; el de Ecuador **no está evaluado**.
- Condiciones poco representadas (noche, lluvia, contraluz, placas sucias o pintadas a mano, motos, placas lejanas) pueden degradar la lectura; la regla de acceso envía las dudas a revisión manual.
- Los informes y gráficos de `results/` con YOLO/Ultralytics son históricos y no describen el modelo vigente.
- Entrenamiento y evaluación: [optimizacion.md](optimizacion.md). Privacidad y sesgos: [consideraciones_eticas.md](consideraciones_eticas.md).
