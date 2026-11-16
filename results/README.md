# Resultados y métricas

## Perfil vigente y comprobación de desarrollo

La aplicación usa el checkpoint USA **semilla 2**, fijado por revisión y SHA-256 en [selected_checkpoint.json](../models/usa/selected_checkpoint.json). La detección permanece en **0,70** y la probabilidad mínima por carácter del OCR en **0,94**. Ecuador comparte estos pesos y aplica sus reglas de interpretación; todavía no cuenta con una validación específica.

| Archivo | Qué comprueba |
|---|---|
| [usa_seed2_notebook_development.json](metrics/usa_seed2_notebook_development.json) | Reejecución del notebook por el handler real de la API sobre las ocho fotos revisadas: hashes, denominadores e intervalos descriptivos |
| [usa_seed2_notebook_software_flow.json](metrics/usa_seed2_notebook_software_flow.json) | Reglas de acceso con datos, listas y barrera sintéticos; no mide exactitud del modelo |
| [usa_runtime_development.json](metrics/usa_runtime_development.json) | Diagnóstico anterior de integración sobre las mismas ocho fotos; no es una muestra independiente adicional |

La comprobación del notebook del 16 de noviembre de 2026 acertó 9/10 matrículas y 2/9 estados entre detecciones emparejadas con referencia conocida. En siete escenas completas hubo 8 aciertos del detector, 3 omisiones y 0 falsas detecciones. Una escena conserva una región sin resolver; las placas ilegibles siguen contando como placas físicas. No se estima la tasa de falsas alarmas en escenas vacías. La muestra reutilizada no constituye un test independiente ni valida una barrera física.

Los campos de identidad y los resultados por imagen permanecen en el archivo privado de evaluación. El registro local `usa_seed2_runtime_profile.json` describe disponibilidad y configuración; no certifica rendimiento.

## Experimentos RT-DETR y test independiente

`src/evaluate.py` genera informes con dataset, split, checkpoint y protocolo propios. `detector_rtdetr_<país>_<split>.json` y `entrenamiento_rtdetr.json` no deben atribuirse automáticamente a la selección vigente. Los informes antiguos de semillas 0 o 1 y sus calibraciones corresponden a esos candidatos.

El test independiente de la semilla 2 sigue pendiente de una fuente nueva con referencia revisada. El notebook conserva el interruptor apagado y, si se habilita con esa fuente, escribe un informe específico de la revisión del modelo y reserva un marcador de intento. La evaluación AP usa un piso de puntuación separado; los conteos operativos usan 0,70. No se ajusta el umbral con el test.

## Artefactos YOLO históricos

Los CSV, JSON y gráficos que indican YOLO/Ultralytics pertenecen a corridas anteriores. También son históricos `detector_test.json`, `entrenamiento.json`, `entrenamiento_yolo11_*.json`, `e2e.json`, `velocidad.json`, `umbrales.json`, sus logs de decisiones y figuras. No describen el checkpoint actual. Las versiones anteriores de notebooks permanecen en Git.

## Datos de operación

Los registros de acceso se mantienen en el repositorio privado configurado. Las imágenes originales, transcripciones, CSV de detalle y credenciales no se publican con estos resúmenes agregados.
