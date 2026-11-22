# docs · Documentación de SIRAP (Ecuador y Estados Unidos)

Todo lo que hay en esta carpeta describe la aplicación vigente: FastAPI + Vue 3, detector RT-DETRv2-S con OpenVINO (un único checkpoint compartido, semilla 2) y OCR `cct-s-v2-global-model`. El README principal ([root](../README.md)) está en inglés y español; los documentos técnicos de abajo están en español.

*Everything in this folder describes the current application: FastAPI + Vue 3, an RT-DETRv2-S/OpenVINO detector (one shared checkpoint, seed 2) and the `cct-s-v2-global-model` OCR. The [main README](../README.md) is bilingual; the technical documents below are written in Spanish.*

## Manual de usuario · User manual

| Documento | Contenido |
|---|---|
| [`manual/SIRAP_Manual_ES.pdf`](manual/SIRAP_Manual_ES.pdf) · [`manual/SIRAP_Manual_EN.pdf`](manual/SIRAP_Manual_EN.pdf) | Manual de 41 páginas con capturas: todas las pantallas de los perfiles de Ecuador y EE. UU. / 41-page manual with screenshots of every screen for both country profiles |
| [`manual/`](manual/) | Fuentes de los manuales y cómo regenerarlos / Sources and how to rebuild them |

## Documentación técnica

| Documento | Contenido |
|---|---|
| [`arquitectura.md`](arquitectura.md) | Flujo de una lectura, detector y OCR, reglas por país, capas y despliegue |
| [`usa_app_integration.md`](usa_app_integration.md) | Perfil de EE. UU.: identidad estado + matrícula, confirmación en dos cuadros, apertura, consulta de J.D. Power y evidencia disponible |
| [`recuperacion_fallos.md`](recuperacion_fallos.md) | Recuperación de operaciones tras reinicios y cortes de conexión |
| [`optimizacion.md`](optimizacion.md) | Entrenamiento, exportación a OpenVINO, evaluación y protocolo para probar candidatos |
| [`analisis_datos.md`](analisis_datos.md) | Fuentes de datos, preparación y límites de cada una |
| [`consideraciones_eticas.md`](consideraciones_eticas.md) | Sesgos, equidad, privacidad, transparencia, responsabilidad, uso dual y limitaciones |
| [`CONFIGURACION_GITHUB_ACTIONS.md`](CONFIGURACION_GITHUB_ACTIONS.md) | Workflows, secretos y despliegue al Space de Hugging Face |
| [`auditoria_licencias.md`](auditoria_licencias.md) | Revisión de licencias (Apache-2.0 y terceros): hallazgos corregidos, riesgos abiertos y lo que no se pudo verificar |

Las métricas están en [`../results/README.md`](../results/README.md) y los avisos de terceros en [`../THIRD_PARTY_NOTICES.md`](../THIRD_PARTY_NOTICES.md).
