# Configuración de GitHub Actions para SIRAP_USA_ECUADOR

Los archivos y workflows de SIRAP_2 se copiaron a este repositorio. Los valores de Secrets y Variables pertenecen a la configuración de cada repositorio y no se transfieren con los archivos.

## Secrets requeridos para el despliegue

En **Settings → Secrets and variables → Actions → New repository secret**, introduce estos valores directamente en GitHub:

| Nombre | Uso |
|---|---|
| `HF_TOKEN` | Publicar en el Space de Hugging Face de SIRAP_USA_ECUADOR. |
| `SIRAP_JWT_SECRET` | Firmar las sesiones de la API. |
| `SIRAP_DEMO_PASSWORD` | Contraseña de las cuentas de demostración. |
| `SIRAP_DATA_GITHUB_TOKEN` | Acceso al repositorio privado de datos configurado para la aplicación. |

No guardes esos valores en este archivo ni en el código.

## Variable requerida

En **Settings → Secrets and variables → Actions → Variables → New repository variable**, configura:

| Nombre | Valor |
|---|---|
| `HF_SPACE` | Identificador del Space creado para SIRAP_USA_ECUADOR. |

No copies el destino del Space original sin comprobarlo. El workflow de despliegue de este repositorio se dejó en modo manual para evitar publicar accidentalmente sobre el Space de SIRAP. Comprueba también el valor de `SIRAP_DATA_GITHUB_REPO` en el workflow antes de desplegar.

## Workflows

- `ci.yml` ejecuta comprobaciones de frontend y backend.
- `deploy-hf-space.yml` permite iniciar el despliegue manualmente desde **Actions**.
- `import-sirap-2.yml` contiene el proceso de importación desde el repositorio público SIRAP_2.

GitHub no permite leer los valores guardados de Secrets para transferirlos. Debes volver a ingresarlos de forma segura en este repositorio.
