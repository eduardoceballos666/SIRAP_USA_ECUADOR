# Configuración de GitHub Actions para SIRAP_USA_ECUADOR

Los workflows incluidos pertenecen a este repositorio. Los valores de Secrets y Variables pertenecen a la configuración de cada repositorio y no se transfieren con los archivos.

## Secrets requeridos para el despliegue

En **Settings → Secrets and variables → Actions → New repository secret**, introduce estos valores directamente en GitHub:

| Nombre | Uso |
|---|---|
| `HF_TOKEN` | Publicar en el Space de Hugging Face de SIRAP_USA_ECUADOR. |
| `SIRAP_JWT_SECRET` | Firmar las sesiones de la API. |
| `SIRAP_DEMO_PASSWORD` | Contraseña de las cuentas de demostración. |
| `SIRAP_DATA_GITHUB_TOKEN` | Acceso al repositorio privado de datos configurado para la aplicación. |

No guardes esos valores en este archivo ni en el código.

## Space de Hugging Face

El despliegue apunta a [`eduardoceballos/SIRAP_USA_ECUADOR_HF`](https://huggingface.co/spaces/eduardoceballos/SIRAP_USA_ECUADOR_HF). El identificador está fijado en el workflow y en el valor predeterminado del script; no hace falta crear la variable `HF_SPACE`.

El workflow despliega automáticamente los cambios relevantes a `main`; también puedes iniciarlo manualmente desde **Actions**. Antes de ejecutarlo, confirma que `HF_TOKEN` tenga permiso de escritura sobre ese Space. También revisa que `SIRAP_DATA_GITHUB_TOKEN` tenga acceso al repositorio privado de persistencia configurado en el workflow.

## Workflows

- `ci.yml` ejecuta comprobaciones de frontend y backend.
- `deploy-hf-space.yml` permite iniciar el despliegue manualmente desde **Actions**.
- El workflow de importación desde el repositorio anterior fue retirado; este repositorio es ahora la fuente del despliegue.

GitHub no permite leer los valores guardados de Secrets para transferirlos. Debes volver a ingresarlos de forma segura en este repositorio.
