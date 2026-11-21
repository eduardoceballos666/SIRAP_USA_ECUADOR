# Configuración de GitHub Actions para SIRAP_USA_ECUADOR

Los workflows pertenecen a este repositorio; los valores de *Secrets* y *Variables* pertenecen a la configuración de cada repositorio y no se transfieren con los archivos. GitHub no permite leer los *Secrets* guardados: hay que volver a introducirlos en cada repositorio.

## Workflows

| Archivo | Cuándo se ejecuta | Qué hace |
|---|---|---|
| `ci.yml` | En cada push y pull request | **Vue checks** (Node 22: instalar, pruebas y compilación del frontend) y **Python checks** (Python 3.11: dependencias bloqueadas y `pytest`) |
| `deploy-hf-space.yml` | Al hacer push a `main` que cambie `api/`, `src/`, `frontend/`, `config/`, `data/`, `models/`, `results/metrics/`, `docs/`, `notebooks/`, `Dockerfile`, los `requirements*`, `deploy/huggingface/` o el propio workflow; y manualmente desde **Actions → Run workflow** | Ejecuta `deploy/huggingface/sync_space.py` para publicar la aplicación en el Space de Hugging Face |

El despliegue usa `concurrency` (`hf-space`), así que un despliegue nuevo cancela el que esté en curso. Como `docs/**` está entre las rutas, **cambiar la documentación también vuelve a desplegar el Space**.

## Secrets requeridos para el despliegue

En **Settings → Secrets and variables → Actions → New repository secret**:

| Nombre | Uso |
|---|---|
| `HF_TOKEN` | Publicar en el Space (permiso de escritura) y **leer el repositorio de modelos privado** con el detector. El script lo guarda también como secreto del Space `SIRAP_USA_MODEL_TOKEN`, con el que la aplicación descarga el checkpoint al iniciar. |
| `SIRAP_JWT_SECRET` | Firmar las sesiones de la API; se guarda también como secreto del Space. |
| `SIRAP_DEMO_PASSWORD` | Contraseña de las cuentas de demostración; se guarda también como secreto del Space. |
| `SIRAP_DATA_GITHUB_TOKEN` | Acceso al repositorio privado de datos (`eduardoceballos666/SIRAP_datos_privados`). El script comprueba que el repositorio sea privado y que existan los seis CSV antes de publicar, para no desplegar nunca con datos vacíos o antiguos. |

No guardes estos valores en el código ni en la documentación.

Antes de cambiar el Space, el script descarga del repositorio privado de modelos los archivos de `models/usa/selected_checkpoint.json` y comprueba su SHA-256; si algo no coincide, **no despliega**. Más detalle en [usa_app_integration.md](usa_app_integration.md) y [arquitectura.md](arquitectura.md).

## Space de Hugging Face

El destino es [`eduardoceballos/SIRAP_USA_ECUADOR_HF`](https://huggingface.co/spaces/eduardoceballos/SIRAP_USA_ECUADOR_HF). El identificador está fijado en el workflow (`HF_SPACE`) y es el valor predeterminado del script; no hace falta crear esa variable.

El Space es de tipo Docker: construye el frontend Vue con Node 22 y ejecuta la API FastAPI con Python 3.11 en el puerto 7860.

## Antes de ejecutar a mano

1. Confirma que `HF_TOKEN` tenga permiso de escritura sobre el Space.
2. Confirma que `SIRAP_DATA_GITHUB_TOKEN` tenga acceso al repositorio privado de persistencia y que `HF_TOKEN` pueda leer el repositorio privado del modelo.
3. Revisa que `ci.yml` esté en verde en `main`.
