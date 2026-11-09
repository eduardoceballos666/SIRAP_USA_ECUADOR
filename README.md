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

Ese checkpoint compartido no se ha validado específicamente para Ecuador ni Estados Unidos. Las métricas y umbrales YOLO anteriores no se transfieren a RT-DETR. A la fecha no hay métricas RT-DETR por país versionadas; los umbrales del detector en configuración son provisionales. Para adopción de un modelo nacional, hay que ajustar y evaluar con datos propios y test reservado.

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

El notebook USA unificado incluye pruebas separadas de OCR y de extremo a extremo; estas no activan decisiones de acceso en la app. La integración USA en la aplicación requiere reglas y normalización específicas del país. Los notebooks USA por etapas fueron consolidados y sus versiones previas permanecen en el historial de Git.

## Aplicación web

La app integra Reconocimiento y Acceso, Historial, Dashboard y Administración con perfiles de operador, supervisor y administrador. La interfaz está disponible en español, inglés, portugués, francés y alemán. El Space utiliza el perfil Ecuador por defecto. El notebook USA incluye evaluaciones separadas de detección y OCR; la integración de ese perfil en decisiones de acceso requiere reglas específicas del país.

Los registros de operación persisten en el repositorio privado configurado mediante secretos de Hugging Face; no subas datos operativos a este repo. Los cambios de `main` se sincronizan al Space mediante [GitHub Actions](.github/workflows/deploy-hf-space.yml).

## Resultados y limitaciones

Los archivos antiguos con `yolo11` en el nombre y sus reportes describen experimentos anteriores. No deben citarse como métricas del checkpoint RT-DETR. Los resultados nuevos se guardan con sufijo `rtdetr`; revisa [`results/README.md`](results/README.md) para distinguirlos.

SAVH se utiliza para OCR en recortes; la evaluación de detección necesita escenas completas anotadas. Los perfiles Ecuador y USA requieren datasets, normalización y evaluación independientes.

## Licencias

El código de este repositorio se distribuye bajo [Apache License 2.0](LICENSE); consulte [NOTICE](NOTICE). El checkpoint RT-DETRv2 de matrículas y OpenVINO declaran Apache-2.0. Transformers, PyTorch, OCR y datasets conservan sus licencias de terceros: [inventario de licencias](THIRD_PARTY_NOTICES.md).

---

# SIRAP_USA_ECUADOR (English)

SIRAP is a vehicle license-plate recognition and access-control application. Its detector is **RT-DETRv2-S (ResNet-18vd)**, running natively through the **OpenVINO Runtime Python API**. Fine-tuning happens before deployment with Transformers/PyTorch; the app loads an OpenVINO IR (`openvino_model.xml` and `.bin`). The source license-plate checkpoint [`merve/license-plates-rtdetrv2`](https://huggingface.co/merve/license-plates-rtdetrv2) is listed as **Apache-2.0**. Country-specific fine-tuned IRs take precedence over the shared IR.

The shared checkpoint has not been validated specifically for Ecuador or the United States. Previous YOLO metrics and confidence thresholds are not carried over. No country-specific RT-DETR test metrics are currently versioned; configured detector thresholds are provisional. Fine-tune and evaluate each profile using representative data and a reserved test split.

Training uses COCO Detection in `src/train.py`, then `src/export_openvino.py` creates the IR. The Roboflow downloader uses `plateblur/european-usa-license-plates` v1 as COCO Segmentation and maps its bounding boxes to one plate class. The consolidated USA notebook builds a grouped internal holdout of at least 400 images from the same export; it is not an external dataset, and vehicle/session separation requires supplied identifiers. Ecuador retains staged notebooks; the USA workflow is in [sirap_backend_usa.ipynb](notebooks/usa/sirap_backend_usa.ipynb). The Hugging Face Space is [SIRAP_USA_ECUADOR_HF](https://huggingface.co/spaces/eduardoceballos/SIRAP_USA_ECUADOR_HF). Earlier staged USA notebooks remain in Git history.
