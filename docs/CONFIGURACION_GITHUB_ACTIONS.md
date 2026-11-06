# Configuración de GitHub Actions para SIRAP_USA_ECUADOR

El código del repositorio SIRAP_2 se copió a este repositorio. Los valores de Secrets y Variables de Actions pertenecen a la configuración de cada repositorio y no forman parte de los archivos versionados.

## Secrets requeridos para el despliegue

En **Settings → Secrets and variables → Actions → New repository secret**, crea estos secretos e ingresa sus valores directamente en GitHub:

| Nombre | Uso |
|---|---|
| `HF_TOKEN` | Publicar en el Space de Hugging Face correspondiente a SIRAP_USA_ECUADOR. |
| `SIRAP_JWT_SECRET` | Firmar las sesiones de la API. |
| `SIRAP_DEMO_PASSWORD` | Contraseña de las cuentas de demostración. |
| `SIRAP_DATA_GITHUB_TOKEN` | Acceso al repositorio privado de datos configurado para la aplicación. |

No guardes esos valores en este archivo ni en el código.

## Variable requerida

En **Settings → Secrets and variables → Actions → Variables → New repository variable**, configura:

| Nombre | Valor |
|---|---|
| `HF_SPACE` | Identificador del Space de Hugging Face creado para SIRAP_USA_ECUADOR. |

No copies aquí el destino del Space original sin comprobarlo: el workflow de despliegue de este repositorio quedó limitado a ejecución manual para evitar publicar accidentalmente sobre el Space de SIRAP.

## Workflows copiados

- `ci.yml` ejecuta las comprobaciones de frontend y backend.
- `deploy-hf-space.yml` conserva el proceso de despliegue, pero solo se puede iniciar manualmente desde **Actions**. Antes de ejecutarlo, configura los secretos y la variable anteriores y verifica el destino de datos indicado en el workflow.
- `import-sirap-2.yml` importa los archivos públicos de SIRAP_2. La sincronización usa el token integrado de Actions y no requiere copiar un PAT.

Los Secrets no se pueden leer de vuelta desde GitHub para transferirlos. Debes introducir los valores de forma segura en este repositorio.
