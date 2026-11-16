# SIRAP_USA_ECUADOR

[![Detector](https://img.shields.io/badge/Detector-RT--DETRv2--S-0b2a6b)](https://huggingface.co/merve/license-plates-rtdetrv2)
[![Runtime](https://img.shields.io/badge/Runtime-OpenVINO-0071C5)](https://docs.openvino.ai/)
[![License](https://img.shields.io/badge/Checkpoint-Apache--2.0-green)](https://huggingface.co/merve/license-plates-rtdetrv2)

**SIRAP** reconoce matrículas y apoya el control de acceso vehicular. La aplicación web combina detector de placas, OCR, reglas de autorización, historial y una barrera de demostración.

- **Aplicación:** [SIRAP_USA_ECUADOR_HF](https://huggingface.co/spaces/eduardoceballos/SIRAP_USA_ECUADOR_HF)
- **API:** `/docs` en la URL del Space.
- **Código y notebooks:** este repositorio.

## Detector vigente

La app ejecuta **RT-DETRv2-S (ResNet-18vd)** con **OpenVINO Runtime nativo en Python**. El IR se obtiene del checkpoint de placas [`merve/license-plates-rtdetrv2`](https://huggingface.co/merve/license-plates-rtdetrv2), cuya ficha declara licencia **Apache-2.0** y señala como base a [`PekingU/rtdetr_v2_r18vd`](https://huggingface.co/PekingU/rtdetr_v2_r18vd). El ajuste fino se entrena previamente con Transformers/PyTorch y se exporta a `openvino_model.xml` + `openvino_model.bin`; la aplicación no carga Transformers durante la inferencia.

La aplicación usa ahora el **mismo checkpoint ajustado para USA, semilla 2**, en Ecuador y Estados Unidos. Los pesos privados se fijan por commit y SHA-256 en [selected_checkpoint.json](models/usa/selected_checkpoint.json), se verifican al cargar y no se reemplazan por otro detector. La detección se mantiene en **0,70** y el OCR global en **0,94** (probabilidad mínima por carácter). No se reentrenó para esta integración.

Cambian las reglas OCR: Ecuador normaliza el formato ecuatoriano (`ABC-1234`); USA conserva letras y números e identifica el vehículo por **estado emisor + matrícula**. El rendimiento del detector con placas ecuatorianas sigue pendiente de evaluación. Los resultados históricos de otros modelos no se muestran como métricas de esta semilla.

El OCR `fast-plate-ocr`, las reglas de acceso, la API y la interfaz se mantienen como componentes separados. Para arquitectura y licencias, consulta [arquitectura](docs/arquitectura.md), [avisos de terceros](THIRD_PARTY_NOTICES.md) y [manual de usuario](docs/manual_usuario.md).

## Entrenamiento y evaluación

El entrenamiento y evaluación activos están en `src/train.py` y `src/evaluate.py`; usan **COCO Detection** y `transformers.Trainer`. El entrenamiento guarda el checkpoint Safetensors y exporta un IR; la evaluación utiliza OpenVINO Runtime, igual que la app. Ecuador conserva notebooks por etapa; todo el flujo USA está consolidado en [sirap_backend_usa.ipynb](notebooks/usa/sirap_backend_usa.ipynb). Consulta el [índice de notebooks](notebooks/README.md).

```bash
# Instalar el entorno local de entrenamiento/desarrollo CPU
python -m pip install -r requirements-dev.txt

# Entrenar con un dataset COCO que tenga train/ y valid/ (test opcional)
python -m src.train --country ecuador --data-dir /ruta/dataset-coco --epochs 30

# Evaluar en un split COCO reservado
python -m src.evaluate detector --country ecuador --data-dir /ruta/dataset-coco --split test
```

Configura `ROBOFLOW_API_KEY` como secreto del entorno si descargas datos desde Roboflow; no pegues llaves en notebooks ni las guardes en Git. El descargador usa `plateblur/european-usa-license-plates` v1 y exporta COCO Segmentation; el detector usa las cajas y unifica las tres etiquetas en una clase de placa. El notebook USA crea un test interno agrupado de al menos 400 imágenes a partir de la misma exportación; no es un conjunto externo. Sin IDs de vehículo o sesión, la separación se limita a familias de nombres y hashes exactos. También puede convertir escenas USA anotadas a COCO.

En Colab con GPU, usa la celda de instalación del notebook y conserva el PyTorch con CUDA que ofrece Colab. `requirements.txt` contiene el runtime de la app (incluido OpenVINO); `requirements-training.txt` separa las dependencias de ajuste y exportación; `requirements-dev.txt` añade herramientas de desarrollo y pruebas.

Las corridas multisemilla y la búsqueda Optuna consumen GPU y están apagadas por defecto en los notebooks. Consulta [optimización](docs/optimizacion.md) y el [protocolo multisemilla](docs/validacion_savh_multisemilla.md) antes de ejecutarlas.

## Notebooks

| Perfil | Notebook activo | Flujo |
|---|---|---|
| Ecuador | [Backend RT-DETR + OCR](notebooks/ecuador/sirap_backend.ipynb) | Flujo de Ecuador por etapas |
| Estados Unidos | [sirap_backend_usa.ipynb](notebooks/usa/sirap_backend_usa.ipynb) | Notebook unificado: COCO, entrenamiento, validación, OCR y OpenVINO |

El notebook USA unificado incluye pruebas separadas de OCR y de extremo a extremo. Las pruebas del notebook no crean autorizaciones en la aplicación. La integración de ambos países está descrita en [flujo de aplicación](docs/usa_app_integration.md). Los notebooks USA por etapas fueron consolidados y sus versiones previas permanecen en el historial de Git.

## Aplicación web

Al iniciar sesión se eligen **idioma y país**. Ecuador y Estados Unidos usan los mismos módulos: Reconocimiento y Acceso, Historial, Dashboard y Administración, con roles de operador, supervisor y administrador. La interfaz está disponible en español, inglés, portugués, francés, alemán e italiano. Las rutas `/ecuador/…` y `/usa/…` comparten componentes; la API vincula el país al token de sesión. Para cambiar de país se vuelve al login. Vehículos, listas, propietarios, demostraciones, historial y dashboard se filtran por el país elegido; usuarios y garitas son comunes.

USA permite la apertura normal mediante **Registrar y abrir barrera** cuando se cumplen los umbrales, la lista blanca vigente y dos cuadros con identificadores y hashes RGB distintos dentro de 7,5 segundos. El servidor emite una confirmación de un solo uso ligada al usuario, garita y sesión. Guarda la solicitud antes de accionar la barrera y vuelve a comprobar las autorizaciones. Una foto estática repetida no cumple esa confirmación. La barrera de la configuración publicada sigue siendo simulada.

Los registros de operación persisten en el repositorio privado configurado mediante secretos de Hugging Face; no subas datos operativos a este repo. Los cambios de `main` se sincronizan al Space mediante [GitHub Actions](.github/workflows/deploy-hf-space.yml).

## Resultados y limitaciones

Los archivos antiguos con `yolo11` en el nombre y sus reportes describen experimentos anteriores. No deben citarse como métricas del checkpoint RT-DETR. Los resultados nuevos se guardan con sufijo `rtdetr`; revisa [`results/README.md`](results/README.md) para distinguirlos.

El diagnóstico del flujo real de la API reutilizó **8 fotos**: 9/10 matrículas exactas entre las detectadas y 2/9 estados conocidos correctos; en 7 escenas con referencia completa hubo 8 placas detectadas, 3 omitidas y 0 falsas detecciones. Una región adicional de la foto 3 sigue dudosa. El [resumen agregado](results/metrics/usa_runtime_development.json) no contiene las matrículas ni las imágenes. Es desarrollo, no un test final independiente; no estima falsas alarmas en escenas vacías.

SAVH y los informes anteriores permanecen como evidencia histórica de sus propios modelos. No validan el checkpoint actual ni la adopción en Ecuador. Las pruebas de software usan listas, imágenes y barrera sintéticas.

## Licencias

El código de este repositorio se distribuye bajo [Apache License 2.0](LICENSE); consulte [NOTICE](NOTICE). El checkpoint RT-DETRv2 de matrículas y OpenVINO declaran Apache-2.0. Transformers, PyTorch, OCR y datasets conservan sus licencias de terceros: [inventario de licencias](THIRD_PARTY_NOTICES.md).

---

# SIRAP_USA_ECUADOR (English)

The login now selects **country and language**. Ecuador and USA share the same Vue interface, the **same USA-trained seed-2 RT-DETRv2-S/OpenVINO detector**, and the same verified global OCR weights. There is no retraining in this integration. Country-specific rules interpret the OCR output: Ecuador uses its plate format; USA preserves alphanumeric characters and requires the issuing state plus serial. Detector confidence remains **0.70**; minimum OCR character probability is **0.94**. Ecuador performance is not yet validated.

Country is bound to the session token and to recognition, registry, allowlists and history. Routes `/ecuador/…` and `/usa/…` reuse the same components. Users and gates are shared. USA normal opening requires a current allowlist entry and two distinct server-confirmed frame IDs and RGB hashes within 7.5 seconds. Receipts expire after 30 seconds, are single-use, and cannot be forged by sending client confidence values. Operations are persisted before actuation. The configured barrier remains simulated.

The immutable [model selection](models/usa/selected_checkpoint.json) references a private Hugging Face model repository. Deployment verifies access and hashes before updating the Space and stores the runtime model credential as a Space secret; model binaries are not copied into public Space source. A reused eight-photo diagnostic is [reported as development](results/metrics/usa_runtime_development.json), not as an independent final test. Historical YOLO/Ecuador results are not presented as validation of these weights.

See [application integration](docs/usa_app_integration.md), [notebooks](notebooks/README.md), and the [Hugging Face Space](https://huggingface.co/spaces/eduardoceballos/SIRAP_USA_ECUADOR_HF). Training remains separate from the deployed, pinned model selection.
