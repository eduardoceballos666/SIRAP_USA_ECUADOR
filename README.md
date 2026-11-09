# SIRAP_USA_ECUADOR

[![Detector](https://img.shields.io/badge/Detector-RT--DETRv2%20R18-0b2a6b)](https://huggingface.co/merve/license-plates-rtdetrv2)
[![Framework](https://img.shields.io/badge/Framework-Transformers-yellow)](https://huggingface.co/docs/transformers)
[![License](https://img.shields.io/badge/Checkpoint-Apache--2.0-green)](https://huggingface.co/merve/license-plates-rtdetrv2)

**SIRAP** reconoce matrículas y apoya el control de acceso vehicular. La aplicación web combina detector de placas, OCR, reglas de autorización, historial y una barrera de demostración.

- **Aplicación:** [SIRAP_USA_ECUADOR_HF](https://huggingface.co/spaces/eduardoceballos/SIRAP_USA_ECUADOR_HF)
- **API:** `/docs` en la URL del Space.
- **Código y notebooks:** este repositorio.

## Detector vigente

La detección usa **Transformers + RT-DETRv2 R18** con el checkpoint de matrículas [`merve/license-plates-rtdetrv2`](https://huggingface.co/merve/license-plates-rtdetrv2), cuya ficha declara licencia **Apache-2.0**. El modelo base es [`PekingU/rtdetr_v2_r18vd`](https://huggingface.co/PekingU/rtdetr_v2_r18vd). El código carga un ajuste fino local bajo `models/<país>/detector/rtdetr_r18/` si está disponible; si no, usa el checkpoint público compartido.

Ese checkpoint compartido no se ha validado específicamente para Ecuador ni Estados Unidos. Las métricas y umbrales YOLO anteriores no se transfieren a RT-DETR. A la fecha no hay métricas RT-DETR por país versionadas; los umbrales del detector en configuración son provisionales. Para adopción de un modelo nacional, hay que ajustar y evaluar con datos propios y test reservado.

El OCR `fast-plate-ocr`, las reglas de acceso, la API y la interfaz se mantienen como componentes separados. Para arquitectura y licencias, consulta [arquitectura](docs/arquitectura.md), [avisos de terceros](THIRD_PARTY_NOTICES.md) y [manual de usuario](docs/manual_usuario.md).

## Entrenamiento y evaluación

El entrenamiento y evaluación activos están en `src/train.py` y `src/evaluate.py`; usan **COCO Detection** y `transformers.Trainer`. Los notebooks Ecuador y USA están organizados por separado en [`notebooks/`](notebooks/README.md). El entrenamiento guarda checkpoints Safetensors y un manifest con la configuración.

```bash
# Instalar el entorno de desarrollo CPU
python -m pip install -r requirements-dev.txt

# Entrenar con un dataset COCO que tenga train/ y valid/ (test opcional)
python -m src.train --country ecuador --data-dir /ruta/dataset-coco --epochs 30

# Evaluar en un split COCO reservado
python -m src.evaluate detector --country ecuador --data-dir /ruta/dataset-coco --split test
```

Configura `ROBOFLOW_API_KEY` como secreto del entorno si usas `--roboflow`; no pegues llaves en notebooks ni las guardes en Git. La exportación COCO es preferida. Existe una función opcional para convertir anotaciones heredadas a COCO; no instala ni usa Ultralytics.

En Colab con GPU, usa la celda de instalación del notebook y conserva el PyTorch con CUDA que ofrece Colab; `requirements-dev.txt` instala la variante CPU para desarrollo local.

Las corridas multisemilla y la búsqueda Optuna consumen GPU y están apagadas por defecto en los notebooks. Consulta [optimización](docs/optimizacion.md) y el [protocolo multisemilla](docs/validacion_savh_multisemilla.md) antes de ejecutarlas.

## Notebooks

| Tarea | Ecuador | Estados Unidos |
|---|---|---|
| Preparación de datos | [02](notebooks/ecuador/02_preprocesamiento.ipynb) | [02](notebooks/usa/02_preprocesamiento.ipynb) |
| Entrenamiento | [03](notebooks/ecuador/03_modelado.ipynb) | [03](notebooks/usa/03_modelado.ipynb) |
| Optimización y evaluación | [04–05](notebooks/ecuador/04_optimizacion.ipynb) · [evaluación](notebooks/ecuador/05_evaluacion.ipynb) | [04–05](notebooks/usa/04_optimizacion.ipynb) · [evaluación](notebooks/usa/05_evaluacion.ipynb) |
| Inferencia / video | [Backend RT-DETR + OCR](notebooks/ecuador/sirap_backend.ipynb) | [Detección RT-DETR](notebooks/usa/sirap_backend.ipynb) |

El notebook USA aún no declara lecturas OCR ni decisiones de acceso; requiere normalización y datos de placas estadounidenses. Las versiones anteriores de notebooks y backend permanecen en el historial de Git; no forman parte del flujo activo.

## Aplicación web

La app integra Reconocimiento y Acceso, Historial, Dashboard y Administración con perfiles de operador, supervisor y administrador. La interfaz está disponible en español, inglés, portugués, francés y alemán. El Space utiliza el perfil Ecuador por defecto; el flujo USA de notebooks evalúa detector por separado y aún requiere normalización/OCR específicos antes de decisiones de acceso.

Los registros de operación persisten en el repositorio privado configurado mediante secretos de Hugging Face; no subas datos operativos a este repo. Los cambios de `main` se sincronizan al Space mediante [GitHub Actions](.github/workflows/deploy-hf-space.yml).

## Resultados y limitaciones

Los archivos antiguos con `yolo11` en el nombre y sus reportes describen experimentos anteriores. No deben citarse como métricas del checkpoint RT-DETR. Los resultados nuevos se guardan con sufijo `rtdetr`; revisa [`results/README.md`](results/README.md) para distinguirlos.

SAVH se utiliza para OCR en recortes; la evaluación de detección necesita escenas completas anotadas. La validación de video por intervalos solo cubre tramos con ground truth y no determina todos los falsos negativos. Los perfiles Ecuador y USA necesitan datasets, normalización y evaluación independientes.

## Licencias

El código de este repositorio se distribuye bajo [Apache License 2.0](LICENSE); consulte [NOTICE](NOTICE). El checkpoint RT-DETRv2 de matrículas también declara Apache-2.0 en su ficha. Transformers, PyTorch, OCR y datasets conservan sus licencias de terceros: [inventario de licencias](THIRD_PARTY_NOTICES.md).

---

# SIRAP_USA_ECUADOR (English)

SIRAP is a vehicle license-plate recognition and access-control application. It uses **Transformers + RT-DETRv2 R18**, with the license-plate checkpoint [`merve/license-plates-rtdetrv2`](https://huggingface.co/merve/license-plates-rtdetrv2), listed as **Apache-2.0**. A country-specific fine-tuned checkpoint under `models/<country>/detector/rtdetr_r18/` takes precedence; otherwise the shared Hub checkpoint is used.

The shared checkpoint has not been validated specifically for Ecuador or the United States. Previous YOLO metrics and confidence thresholds are not carried over. No country-specific RT-DETR test metrics are currently versioned; configured detector thresholds are provisional. Fine-tune and evaluate each profile using representative data and a reserved test split.

Training and evaluation use COCO Detection in `src/train.py` and `src/evaluate.py`. Country-specific notebooks are indexed in [`notebooks/README.md`](notebooks/README.md). The Hugging Face Space is [SIRAP_USA_ECUADOR_HF](https://huggingface.co/spaces/eduardoceballos/SIRAP_USA_ECUADOR_HF). Previous YOLO notebooks remain available in Git history.
