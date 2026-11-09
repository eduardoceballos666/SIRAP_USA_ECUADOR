---
title: SIRAP_USA_ECUADOR_HF
emoji: 🚗
colorFrom: yellow
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
license: apache-2.0
short_description: Reconocimiento de placas y control de acceso (YOLO11 + OCR)
---

# SIRAP_USA_ECUADOR_HF · Sistema de Detección y Reconocimiento Automático de Placas

**Reconocimiento de placas y control de acceso (YOLO11 + OCR)**

**Versión del producto: SIRAP_USA_ECUADOR_HF 1.0.** La API y el paquete npm del frontend usan el identificador técnico 2.0.0. El tag de GitHub `v2.0` identifica el corte del código con arquitectura FastAPI + Vue 3; no es la versión del producto. El [código fuente y la documentación](https://github.com/eduardoceballos666/SIRAP_USA_ECUADOR) se mantienen en GitHub.

## Acceso e idioma

Abre la [aplicación SIRAP_USA_ECUADOR_HF](https://huggingface.co/spaces/eduardoceballos/SIRAP_USA_ECUADOR_HF). Español es el idioma inicial. Para cambiar a inglés, selecciona **English** en el control **Idioma** de la pantalla de inicio de sesión o en el menú común una vez dentro. Selecciona **Español** para volver. Ambas opciones usan la misma dirección y la preferencia se conserva en ese navegador.

Las cuentas de demostración son `operador`, `supervisor` y `admin`. La contraseña se puede configurar mediante el secreto `SIRAP_DEMO_PASSWORD`. Si no se define, la API usa el valor predeterminado configurado en `api/settings.py`; para el Space público, configura explícitamente un valor propio y no publiques el valor del secreto. Los registros de demostración son ficticios y la barrera está simulada.

## Despliegue

Este repositorio publica la aplicación en el Space [SIRAP_USA_ECUADOR_HF](https://huggingface.co/spaces/eduardoceballos/SIRAP_USA_ECUADOR_HF). El workflow [deploy-hf-space.yml](https://github.com/eduardoceballos666/SIRAP_USA_ECUADOR/blob/main/.github/workflows/deploy-hf-space.yml) despliega automáticamente los cambios de la aplicación en `main` que coinciden con las rutas configuradas. También puede iniciarse manualmente desde GitHub Actions.

El destino está configurado como `eduardoceballos/SIRAP_USA_ECUADOR_HF` en el workflow y como valor predeterminado del script. No se necesita la variable de Actions `HF_SPACE`. Para desplegar, configura los secretos `HF_TOKEN` y `SIRAP_DATA_GITHUB_TOKEN`; `SIRAP_JWT_SECRET` y `SIRAP_DEMO_PASSWORD` son opcionales. Si el Space aún no existe, el script intenta crearlo con el token de Hugging Face.

## Persistencia y datos consultados

### Registros de la aplicación

`SIRAP_DATA_GITHUB_TOKEN` permite a la aplicación restaurar y guardar vehículos, autorizaciones, operaciones, garitas, usuarios y credenciales en el repositorio privado `eduardoceballos666/SIRAP_datos_privados`. El almacenamiento local del Space es temporal; los CSV privados permiten conservar los registros entre reinicios. Si falta el acceso requerido al repositorio privado, el sistema no debe tratar una copia local vacía como respaldo persistente.

### Exportación enriquecida de detecciones

La exportación de detecciones usa la misma configuración privada: `SIRAP_DATA_GITHUB_TOKEN` y `SIRAP_DATA_GITHUB_REPO`. Los eventos enriquecidos se guardan en `data/processed/detecciones.csv`; no se usan las variables antiguas `GITHUB_TOKEN`, `GITHUB_DATA_REPOSITORY`, `GITHUB_DATA_BRANCH` ni `GITHUB_DATA_PATH`.

El enriquecimiento consulta datos vehiculares públicos del SRI en segundo plano y guarda el resultado en el repositorio privado. SIRAP_USA_ECUADOR_HF no consulta EcuadorLegalOnline porque la información de propietario que ofrece ese servicio es de pago. El nombre del propietario, cuando aparece en la aplicación, procede del registro local.

| Dato | Uso |
|---|---|
| `SIRAP_DATA_GITHUB_TOKEN` | Secreto para leer y escribir los CSV en el repositorio privado |
| `SIRAP_DATA_GITHUB_REPO` | Repositorio privado de persistencia; el despliegue configura `eduardoceballos666/SIRAP_datos_privados` |
| `data/processed/*.csv` | Registros operativos de la aplicación |
| `data/processed/detecciones.csv` | Eventos de detección con enriquecimiento del SRI |

## Umbral y revisión humana

La configuración vigente en [config/countries/ecuador.yaml](https://github.com/eduardoceballos666/SIRAP_USA_ECUADOR/blob/main/config/countries/ecuador.yaml) establece una confianza OCR mínima de **94 %**. Las lecturas por debajo del umbral requieren verificación manual. En modo continuo de video o cámara, la interfaz espera que la misma placa alcance al menos 94 % de confianza OCR en dos cuadros aceptados dentro de 7,5 segundos antes de mostrar y registrar la decisión. Estas medidas reducen decisiones basadas en una lectura aislada; no reemplazan la revisión del operador cuando hay dudas.

La aplicación de demostración se ejecuta en CPU, sin GPU dedicada. Por eso, las mediciones de GPU del notebook no representan la latencia del Space.

## Enlaces

- **Hugging Face Space:** [SIRAP_USA_ECUADOR_HF](https://huggingface.co/spaces/eduardoceballos/SIRAP_USA_ECUADOR_HF)
- **Aplicación:** [Abrir SIRAP_USA_ECUADOR_HF](https://huggingface.co/spaces/eduardoceballos/SIRAP_USA_ECUADOR_HF)
- **API interactiva:** ruta `/docs` de la aplicación desplegada
- **Código fuente:** [GitHub SIRAP_USA_ECUADOR](https://github.com/eduardoceballos666/SIRAP_USA_ECUADOR)
- **Manual de usuario:** [docs/manual_usuario.md](https://github.com/eduardoceballos666/SIRAP_USA_ECUADOR/blob/main/docs/manual_usuario.md)
- **Videos de presentación:** [README principal](https://github.com/eduardoceballos666/SIRAP_USA_ECUADOR#videos-de-entrega)

SIRAP_USA_ECUADOR_HF 1.0 ofrece interfaz en español e inglés. La configuración del Space y su despliegue se administran desde este repositorio.


## English

This folder contains the Hugging Face Space deployment guide and synchronization script. Deployment uses the shared application code and the Ecuador configuration by default. The U.S. lookup provider is not active until J.D. Power authorizes an API integration or grants written permission for automation.

## Licencia

El código original de SIRAP_USA_ECUADOR se distribuye bajo **Apache License 2.0**. Consulta el texto en [LICENSE](https://github.com/eduardoceballos666/SIRAP_USA_ECUADOR/blob/main/LICENSE) y el aviso de autoría en [NOTICE](https://github.com/eduardoceballos666/SIRAP_USA_ECUADOR/blob/main/NOTICE). Las versiones publicadas anteriormente bajo MIT conservan los términos de esa licencia. Los modelos, pesos, bibliotecas y datos de terceros mantienen sus licencias y condiciones; consulta [THIRD_PARTY_NOTICES.md](https://github.com/eduardoceballos666/SIRAP_USA_ECUADOR/blob/main/THIRD_PARTY_NOTICES.md).

## License

Original SIRAP_USA_ECUADOR code is distributed under **Apache License 2.0**. See [LICENSE](https://github.com/eduardoceballos666/SIRAP_USA_ECUADOR/blob/main/LICENSE) and [NOTICE](https://github.com/eduardoceballos666/SIRAP_USA_ECUADOR/blob/main/NOTICE). Previously published versions under MIT remain subject to that license. Third-party models, weights, libraries, and datasets retain their respective licenses and terms.
