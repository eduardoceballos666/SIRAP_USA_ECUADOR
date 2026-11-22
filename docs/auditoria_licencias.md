# Auditoría de licencias de SIRAP_USA_ECUADOR

Revisión del 2026-11-22 del repositorio de GitHub (`SIRAP_USA_ECUADOR`), del Space `SIRAP_USA_ECUADOR_HF` y del repositorio de modelos `SIRAP_USA_seed2`. Pregunta: ¿el software cumple Apache-2.0 y no incluye componentes de otras licencias que, al venderse, pudieran dar lugar a reclamaciones?

> **No es asesoría legal.** Es una revisión técnica de metadatos, árboles de archivos y lockfiles. Antes de una venta, un abogado de propiedad intelectual debe revisar los puntos abiertos.

## Resumen

- **El código original** declara Apache-2.0 de forma coherente: `LICENSE`, `NOTICE`, insignia del README y metadatos del Space.
- **Se encontraron y corrigieron dos problemas que sí habrían bloqueado una venta**: la biblioteca `Levenshtein` (**GPL-2.0-or-later**) como dependencia de ejecución, y 751 imágenes con sus scripts del conjunto `seg_and_ocr` de OpenALPR (**AGPL-3.0**) dentro del repositorio.
- **Tras esas correcciones no queda ninguna dependencia GPL, LGPL ni AGPL instalada como paquete.** Hay 3 paquetes MPL-2.0 (copyleft solo a nivel de archivo; sin modificar no imponen nada).
- **Quedan riesgos abiertos**, la mayoría **no** son de licencias de software: procedencia de los datos que entrenaron el modelo, condiciones de uso de J.D. Power, historial de Git, derechos sobre fotos y videos, y derechos de autoría del propio equipo. Están en la tabla siguiente, por prioridad.

Una licencia permisiva (MIT, BSD, Apache) no genera cobros por regalías. El riesgo económico real viene de: (1) incumplir una licencia con copyleft o de atribución (GPL, AGPL, CC BY), (2) violar un contrato o condiciones de uso (J.D. Power), (3) usar datos o imágenes sin derecho, (4) coautores o instituciones con derechos sobre el código, y (5) patentes de terceros.

## Riesgos abiertos

| # | Prioridad | Qué | Por qué importa si se vende | Acción recomendada |
|---|---|---|---|---|
| 1 | Alta | **El historial de Git conserva los archivos AGPL** (751 PNG, `groundtruth.csv`, scripts de `openalpr/benchmarks`), aunque ya no están en el árbol. | Quien clone el historial recibe contenido AGPL dentro de un repositorio que se anuncia como Apache-2.0. | Reescribir el historial (`git filter-repo`) o publicar un repositorio nuevo sin ese historial, antes de vender. No se hizo: exige *force-push* y coordinar con el otro autor. El historial del Space no se pudo consultar; su árbol actual no contiene esas imágenes. |
| 2 | Alta | **Las capturas 32 y 33 del manual de EE. UU.** (`docs/manual/screenshots/{es,en}/32_usa_first_frame.png` y `33_usa_confirmed.png`, y los PDF del manual en español e inglés donde se incrustan) usan un recorte de placa de `seg_and_ocr`. | Son una obra derivada de contenido AGPL dentro de la documentación. | Regenerarlas con una placa propia o sintética y reconstruir los PDF. |
| 3 | Alta | **Procedencia del conjunto de recuperación** (249 imágenes de entrenamiento y 79 de validación, `recovery_coco_20261114`) con el que se ajustó el checkpoint **desplegado**. No está documentada en el repositorio. | Si incluye imágenes sin derecho de uso, el modelo (el activo central) queda manchado. Los pesos heredan los problemas de sus datos. | Documentar de dónde salió cada imagen y su licencia o permiso. Si no puede acreditarse, reentrenar con datos propios o con licencia clara. |
| 4 | Alta | **J.D. Power**: la consulta (`api/providers/usa_jdpower.py`, activa en `config/countries/usa.yaml`) automatiza un sitio comercial. No se pudieron leer sus condiciones de uso. | No es un problema de licencia de software sino de **contrato**: puede prohibir la consulta automatizada y el uso comercial de sus datos. El repositorio indica que el propietario del proyecto confirmó acceso autorizado, pero eso no cubre a un comprador. | Obtener permiso o licencia por escrito, o desactivar la función (`vehicle_lookup.enabled: false`) en la versión comercial. |
| 5 | Alta | **Derechos de autoría propios**: el código lo escriben dos autores en un programa de maestría. | Apache-2.0 solo puede concederla quien tiene los derechos. Una universidad, un docente o un colaborador podrían tener derechos o reclamarlos; código copiado de tutoriales o respuestas en línea también cuenta. | Acuerdo escrito entre los autores (quién puede vender y cómo se reparte), revisar la política de propiedad intelectual de la universidad y la procedencia de fragmentos externos. |
| 6 | Media | **Pesos del OCR** `cct-s-v2-global-model` (`fast-plate-ocr`): el código es MIT, pero no se verificó la licencia de los pesos ni los datos con que se entrenaron. | Los pesos pueden tener términos distintos de los del código. | Consultar el repositorio del proyecto o a su autor; si hay duda, entrenar un OCR propio. |
| 7 | Media | **Datos del checkpoint de partida** `merve/license-plates-rtdetrv2` (declara Apache-2.0): no se verificó con qué datos fue ajustado. | Igual que el punto 3, un modelo hereda el riesgo de sus datos. | Revisar la ficha y el dataset citado, o reentrenar desde `PekingU/rtdetr_v2_r18vd`. |
| 8 | Media | **Roboflow European + USA License plates** (CC BY 4.0): la licencia del conjunto no garantiza que quien subió las imágenes tuviera derecho a hacerlo. Se usó en el experimento de tres semillas, no en el checkpoint desplegado. | CC BY exige atribución, indicar cambios y enlazar la licencia; las imágenes de fondo son de terceros. | Mantener la atribución ([`THIRD_PARTY_NOTICES.md`](../THIRD_PARTY_NOTICES.md)); no usar ese experimento como base del producto sin revisar el origen. |
| 9 | Media | **Fotos y videos de garita y de demostración** (`datasets/ecuador/gate/`, `datasets/shared/demo_media/`, `evaluation/ecuador/` y las 6 fotos de `datasets/ecuador/detection_coco/`): no está documentado quién las tomó ni si hubo permiso del sitio o de las personas. | Derechos de imagen y de datos personales (placas y personas). No son licencias de software. | Confirmar autoría y permisos; retirar lo que no pueda respaldarse. |
| 10 | Media | **Atribuciones al empaquetar**: MIT y BSD exigen conservar el aviso de copyright; Vite no incluye los textos de licencia en el paquete de la interfaz, y las ruedas de Python traen sus propios avisos (FFmpeg-LGPL en OpenCV). | Una versión que se entrega a un cliente sin esos avisos incumple esas licencias. | Generar un archivo con todas las licencias del paquete (por ejemplo `pip-licenses --with-license-file` y un complemento de Vite) y entregarlo con el producto. |
| 11 | Baja | **MPL-2.0** en `certifi`, `tqdm` (ejecución) y `lightningcss` (compilación). | Solo obliga si se modifican esos archivos. | No modificarlos; si se cambian, publicar los cambios de esos archivos. |
| 12 | Baja | **LGPL del sistema** (FFmpeg dentro de OpenCV, `libglib2.0-0`, `libgl1`, componentes de Chromium). | Se usan como bibliotecas dinámicas sin modificar. Si se entrega la imagen de Docker, se deben ofrecer sus avisos y fuentes. | Incluir los avisos en el paquete; no enlazar estáticamente. |
| 13 | Baja | **`scripts/archive/yolo11_2026/validar_multisemilla_yolo11.py`** importa `ultralytics` (**AGPL-3.0**). No es dependencia (no está en ningún `requirements`) ni se publica en el Space. | Quien lo ejecute y distribuya el resultado tendría obligaciones AGPL; el resto de la aplicación no depende de él. | Eliminarlo del producto comercial, o dejarlo claramente separado como archivo histórico. |
| 14 | Baja | **Binarios heredados sin uso** en el árbol: `models/usa/detector/rtdetrv2_s/openvino/` (corrida de prueba de 64 imágenes), `models/ecuador/detector/...` (relleno), `datasets/shared/demo_media/video_03.z03`. | Datos de entrenamiento de la corrida de prueba sin documentar. | Borrarlos si no se necesitan. |
| 15 | Baja | **Patentes**: ninguna licencia de código protege de patentes de terceros en detección o lectura de matrículas. | No se evaluó la libertad para operar. | Revisión específica con un especialista si se comercializa. |

## Cambios hechos en esta revisión

1. **`Levenshtein` (GPL-2.0-or-later) → `rapidfuzz` (MIT)** en `src/data_processing.py`, `requirements.in` y los tres lockfiles con huellas. `plate_distance` mantiene una implementación de respaldo sin bibliotecas. Una dependencia GPL enlazada en un programa que se distribuye obliga a ofrecer todo bajo GPL, incompatible con venderlo con código propietario. Hasta ahora era una dependencia directa de `requirements.in` y estaba en la imagen del Space.
2. **Conjunto `seg_and_ocr` de `openalpr/benchmarks` (AGPL-3.0) retirado** de `datasets/usa/` y `datasets/ecuador/` (751 imágenes y scripts en cada carpeta; la de Ecuador era una copia de la de EE. UU.). Quedó un README que explica cómo descargarlo aparte para mediciones de desarrollo.
3. **`THIRD_PARTY_NOTICES.md` y `NOTICE` reescritos**: inventario de modelos, bibliotecas, interfaz, imagen de Docker, datos y servicios; aviso de Apache ECharts (que su `NOTICE` exige reproducir); la licencia de SAVH Guayaquil se corrigió a CC BY 4.0 (antes decía que no se mostraba).
4. **Prueba automática** [`tests/test_license_policy.py`](../tests/test_license_policy.py): falla si reaparecen en las dependencias `Levenshtein`, `ultralytics` u otros paquetes con copyleft fuerte, si el código de la aplicación los importa, si vuelve la carpeta `seg_and_ocr` con archivos, si el Space los publicaría o si falta el aviso de ECharts.
5. **`datasets/ecuador/README.md`** (era una copia del de EE. UU.) y el registro de entrenamiento del checkpoint desplegado en [`optimizacion.md`](optimizacion.md) y [`analisis_datos.md`](analisis_datos.md) (se había atribuido al checkpoint desplegado el experimento de tres semillas; son series de corridas distintas).

## Qué se revisó y cómo

| Alcance | Método | Resultado |
|---|---|---|
| Código original | Revisión de `LICENSE`, `NOTICE`, README, metadatos del Space | Apache-2.0 coherente |
| Python | 188 paquetes distintos en `requirements.txt` (ejecución, 51), `requirements-training.txt` (89) y `requirements-dev.txt` (178), consultados con sus metadatos de PyPI (campo de licencia y clasificadores) | 185 permisivos, 3 MPL-2.0 (`certifi`, `tqdm`, `fqdn`; este último solo en pruebas), 0 GPL/LGPL/AGPL tras retirar `Levenshtein`. No se leyó el texto de cada licencia. |
| Interfaz (npm) | `package-lock.json`: 139 paquetes | 107 MIT, 24 MPL-2.0 (binarios de `lightningcss`, solo compilación), el resto Apache-2.0, ISC, BSD y 0BSD |
| Imagen de Docker | `Dockerfile` | Debian slim, Tesseract (Apache-2.0), Chromium de Playwright, `libgl1`/`libglib2.0-0` (LGPL); no se auditaron uno por uno los paquetes Debian |
| Modelos | Metadatos del Hub de Hugging Face | `PekingU/rtdetr_v2_r18vd`, `merve/license-plates-rtdetrv2` y `SIRAP_USA_seed2` declaran Apache-2.0. El repositorio `SIRAP_USA_seed2` es privado y solo contiene el IR de OpenVINO y dos JSON; no contiene datos |
| Space | Listado de archivos y `README.md` | Declara `license: apache-2.0`, incluye `LICENSE`, `NOTICE` y `THIRD_PARTY_NOTICES.md`. Su árbol no contiene imágenes de `datasets/` |
| Datos | READMEs, rutas en el árbol y registros públicos | CC BY 4.0 (Roboflow, SAVH), AGPL-3.0 (OpenALPR, retirado) |

## Lo que no se pudo verificar

- Condiciones de uso de J.D. Power (el sitio no se pudo descargar desde este entorno).
- Licencia de los pesos y datos del OCR `cct-s-v2-global-model`.
- Datos de ajuste de `merve/license-plates-rtdetrv2` y procedencia del conjunto de recuperación de 249/79 imágenes.
- Derechos de autor y permisos de las fotos y videos de garita y de demostración.
- Historial de commits del Space de Hugging Face.
- Licencias individuales de los paquetes Debian de la imagen.
- Patentes y marcas.

## Cómo repetir la revisión

1. Instalar las dependencias bloqueadas en un entorno limpio y ejecutar `pip-licenses --format=markdown --with-urls` (y `npm ls --all --long` o el `package-lock.json` en `frontend/`).
2. Revisar a mano cualquier paquete cuyo campo de licencia esté vacío o contenga texto libre.
3. Ejecutar `pytest tests/test_license_policy.py`.
4. Al añadir un conjunto de datos o un modelo, registrar fuente, licencia y fecha en [`THIRD_PARTY_NOTICES.md`](../THIRD_PARTY_NOTICES.md) antes de incorporarlo.
