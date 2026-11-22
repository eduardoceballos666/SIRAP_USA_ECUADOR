---
title: SIRAP_USA_ECUADOR_HF
emoji: 🚗
colorFrom: yellow
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
license: apache-2.0
short_description: RT-DETRv2-S con OpenVINO y OCR de placas
---

# SIRAP_USA_ECUADOR_HF · Sistema de Detección y Reconocimiento Automático de Placas

**Reconocimiento de placas y control de acceso (RT-DETRv2-S/OpenVINO + OCR)**

**Versión del producto: SIRAP_USA_ECUADOR_HF 1.0.** La API y el paquete npm del frontend usan el identificador técnico 2.0.0. El tag de GitHub `v2.0` identifica el corte del código con arquitectura FastAPI + Vue 3; no es la versión del producto. El [código fuente y la documentación](https://github.com/eduardoceballos666/SIRAP_USA_ECUADOR) se mantienen en GitHub.

## Acceso, idioma y país

Abre la [aplicación SIRAP_USA_ECUADOR_HF](https://huggingface.co/spaces/eduardoceballos/SIRAP_USA_ECUADOR_HF). El idioma inicial es inglés. Puedes seleccionar Español, English, Português, Français, Deutsch o Italiano en el control **Idioma** de la pantalla de inicio de sesión o en el menú común una vez dentro. La preferencia se conserva en ese navegador. En el mismo login se elige **Ecuador o Estados Unidos**. Ambos países comparten la interfaz y los pesos; el país de sesión define las reglas OCR y los registros visibles.

Las cuentas de demostración son `operador`, `supervisor` y `admin`. La contraseña se puede configurar mediante el secreto `SIRAP_DEMO_PASSWORD`. Si no se define, la API usa el valor predeterminado configurado en `api/settings.py`; para el Space público, configura explícitamente un valor propio y no publiques el valor del secreto. Los registros de demostración son ficticios y la barrera está simulada.

## Despliegue

Este repositorio publica la aplicación en el Space [SIRAP_USA_ECUADOR_HF](https://huggingface.co/spaces/eduardoceballos/SIRAP_USA_ECUADOR_HF). El workflow [deploy-hf-space.yml](https://github.com/eduardoceballos666/SIRAP_USA_ECUADOR/blob/main/.github/workflows/deploy-hf-space.yml) despliega automáticamente la aplicación, notebooks y documentación que cambien en `main` dentro de las rutas configuradas. También puede iniciarse manualmente desde GitHub Actions.

El destino está configurado como `eduardoceballos/SIRAP_USA_ECUADOR_HF` en el workflow y como valor predeterminado del script. No se necesita la variable de Actions `HF_SPACE`. Para desplegar, configura los secretos `HF_TOKEN` y `SIRAP_DATA_GITHUB_TOKEN`; `SIRAP_JWT_SECRET` y `SIRAP_DEMO_PASSWORD` son opcionales. Si el Space aún no existe, el script intenta crearlo con el token de Hugging Face.

## Persistencia y datos consultados

### Registros de la aplicación

`SIRAP_DATA_GITHUB_TOKEN` permite a la aplicación restaurar y guardar vehículos, autorizaciones, operaciones, garitas, usuarios y credenciales en el repositorio privado `eduardoceballos666/SIRAP_datos_privados`. El almacenamiento local del Space es temporal; los CSV privados permiten conservar los registros entre reinicios. Si falta el acceso requerido al repositorio privado, el sistema no debe tratar una copia local vacía como respaldo persistente.

### Exportación enriquecida de detecciones

La exportación de detecciones usa la misma configuración privada: `SIRAP_DATA_GITHUB_TOKEN` y `SIRAP_DATA_GITHUB_REPO`. Los eventos enriquecidos se guardan en `data/processed/detecciones.csv`; no se usan las variables antiguas `GITHUB_TOKEN`, `GITHUB_DATA_REPOSITORY`, `GITHUB_DATA_BRANCH` ni `GITHUB_DATA_PATH`.

Solo el perfil Ecuador consulta datos vehiculares públicos del SRI en segundo plano y guarda el resultado en el repositorio privado. USA consulta su registro local (estado emisor más matrícula) y el informe público de J.D. Power (año y modelo, color, tipo de carrocería y estado) con la matrícula y el estado confirmado; si J.D. Power no responde, se muestran solo los datos locales. SIRAP_USA_ECUADOR_HF no consulta EcuadorLegalOnline porque la información de propietario que ofrece ese servicio es de pago. El nombre del propietario, cuando aparece en la aplicación, procede del registro local.

| Dato | Uso |
|---|---|
| `SIRAP_DATA_GITHUB_TOKEN` | Secreto para leer y escribir los CSV en el repositorio privado |
| `SIRAP_DATA_GITHUB_REPO` | Repositorio privado de persistencia; el despliegue configura `eduardoceballos666/SIRAP_datos_privados` |
| `data/processed/*.csv` | Registros operativos de la aplicación |
| `data/processed/detecciones.csv` | Eventos de detección con enriquecimiento del SRI |

## Detector y licencia

Ambos países ejecutan **el mismo RT-DETRv2-S/OpenVINO ajustado para USA, semilla 2**. El modelo está en el repositorio privado `eduardoceballos/SIRAP_USA_seed2`, fijado por commit y SHA-256 en `models/usa/selected_checkpoint.json`. El despliegue verifica acceso e integridad y guarda `SIRAP_USA_MODEL_TOKEN` como secreto del Space para descargarlo al iniciar. Los pesos privados no se copian al código público ni se entrena un modelo durante la construcción. El OCR global conserva los mismos pesos para ambos países.

Ecuador normaliza su formato (por ejemplo `ABC-1234`); USA conserva letras y números y requiere estado emisor más matrícula. No hay un reentrenamiento ecuatoriano en esta integración. El rendimiento del checkpoint compartido en Ecuador sigue pendiente de evaluación. Los informes históricos de otros modelos no son métricas de estos pesos.

## Umbrales y apertura

Detección **0,70**, OCR **0,94** (probabilidad mínima por carácter), sin cambiar la semilla 2. Para USA, **Registrar y abrir barrera** requiere lista blanca vigente y dos identificadores de cuadro y hashes RGB distintos recibidos dentro de 7,5 segundos. El servidor comprueba la evidencia, usuario y garita; la confirmación vence en 30 segundos y se utiliza una sola vez. Persiste la operación antes de accionar la barrera. Una sola foto estática repetida no cumple esta confirmación.

Las lecturas incompletas, bajas confianzas y estados desconocidos requieren revisión manual. La barrera configurada sigue siendo **simulada**. El diagnóstico de ocho fotos reutilizadas es desarrollo, no un test final independiente. La inferencia de la aplicación se realiza en CPU.

## Enlaces

- **Hugging Face Space:** [SIRAP_USA_ECUADOR_HF](https://huggingface.co/spaces/eduardoceballos/SIRAP_USA_ECUADOR_HF)
- **Aplicación:** [Abrir SIRAP_USA_ECUADOR_HF](https://huggingface.co/spaces/eduardoceballos/SIRAP_USA_ECUADOR_HF)
- **API interactiva:** ruta `/docs` de la aplicación desplegada
- **Código fuente:** [GitHub SIRAP_USA_ECUADOR](https://github.com/eduardoceballos666/SIRAP_USA_ECUADOR)
- **Manual de usuario (PDF):** [español](https://github.com/eduardoceballos666/SIRAP_USA_ECUADOR/blob/main/docs/manual/SIRAP_Manual_ES.pdf) · [English](https://github.com/eduardoceballos666/SIRAP_USA_ECUADOR/blob/main/docs/manual/SIRAP_Manual_EN.pdf)
- **Notebook Ecuador:** [sirap_backend_ecuador.ipynb](https://github.com/eduardoceballos666/SIRAP_USA_ECUADOR/blob/main/notebooks/ecuador/sirap_backend_ecuador.ipynb)

SIRAP_USA_ECUADOR_HF 1.0 ofrece interfaz en español, inglés, portugués, francés, alemán e italiano. La configuración del Space y su despliegue se administran desde este repositorio.


## English

This folder contains the Hugging Face Space deployment guide and synchronization script. Login selects country and language. Ecuador and USA share the same USA-trained seed-2 detector and global OCR weights; only country interpretation and validation rules differ. USA requires state plus serial and server-confirmed distinct frames for normal opening. Ecuador performance remains unvalidated. Both profiles use the existing private CSV storage; USA vehicle lookup uses the local registry plus J.D. Power's public report; if J.D. Power does not answer, only local data is shown.

## Licencia

El código original de SIRAP_USA_ECUADOR se distribuye bajo **Apache License 2.0**. Consulta el texto en [LICENSE](https://github.com/eduardoceballos666/SIRAP_USA_ECUADOR/blob/main/LICENSE) y el aviso de autoría en [NOTICE](https://github.com/eduardoceballos666/SIRAP_USA_ECUADOR/blob/main/NOTICE). Las versiones publicadas anteriormente bajo MIT conservan los términos de esa licencia. Los modelos, pesos, bibliotecas y datos de terceros mantienen sus licencias y condiciones; consulta [THIRD_PARTY_NOTICES.md](https://github.com/eduardoceballos666/SIRAP_USA_ECUADOR/blob/main/THIRD_PARTY_NOTICES.md).

## License

Original SIRAP_USA_ECUADOR code is distributed under **Apache License 2.0**. See [LICENSE](https://github.com/eduardoceballos666/SIRAP_USA_ECUADOR/blob/main/LICENSE) and [NOTICE](https://github.com/eduardoceballos666/SIRAP_USA_ECUADOR/blob/main/NOTICE). Previously published versions under MIT remain subject to that license. Third-party models, weights, libraries, and datasets retain their respective licenses and terms.

