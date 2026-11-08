**Purpose:** frontend/README.md contains project files and instructions. This description is in English.

> Purpose: Shared Vue frontend for the SIRAP application.

# SIRAP · Frontend (Vue 3)

Vue 3 + Vite + Pinia + Vue Router + Tailwind CSS 4 · gráficos con ECharts · tema claro/oscuro (variables CSS en `src/style.css`).

```bash
npm install
npm run dev        # http://localhost:5173 (reenvía /api a http://localhost:8000)
npm run build      # genera dist/, que FastAPI sirve en http://localhost:8000
```

| Carpeta | Contenido |
|---|---|
| `src/views/` | Login, Reconocimiento y Acceso, Dashboard, Historial, Administración, Acerca del modelo |
| `src/components/` | Tarjeta de resultado, visor con la caja de la placa (SVG), íconos, logo, modal, avisos |
| `src/stores/` | Pinia: `auth` (token JWT y rol) y `session` (garita, movimiento, tema claro/oscuro, avisos y lecturas de la sesión) |
| `src/router/` | Rutas protegidas por sesión y por rol |
| `src/lib/` | Cliente HTTP (`api.js`), formatos y configuración de gráficos |

## Idiomas de la interfaz

El frontend ofrece inglés, español, portugués brasileño, francés y alemán. El inglés es el idioma inicial; una selección guardada por la persona usuaria se conserva en `localStorage` (`sirap_language`). El selector **Language / Idioma** aparece en el inicio de sesión y en el menú compartido. El tema claro se usa de forma predeterminada en móviles y escritorio, y una preferencia de tema guardada se mantiene. Las cadenas disponibles se mantienen en `src/i18n.js`; las vistas deben usar `$t()` para que el texto respete el idioma seleccionado. Las cadenas sin traducción específica se muestran en inglés.

## Umbral operativo OCR

La aplicación usa un umbral de confianza OCR de **94 %**, según [`config/countries/ecuador.yaml`](../config/countries/ecuador.yaml). Las lecturas por debajo pasan a verificación manual. En video o cámara continua, la misma placa debe alcanzar el umbral en dos cuadros aceptados dentro de 7,5 segundos; las lecturas inciertas requieren revisión humana.


## Aplicación y repositorio

La versión desplegada de la interfaz se encuentra en [SIRAP en Hugging Face](https://huggingface.co/spaces/eduardoceballos/SIRAP_USA_ECUADOR_HF) y en https://eduardoceballos-sirap-usa-ecuador-hf.hf.space. El [repositorio SIRAP_USA_ECUADOR](https://github.com/eduardoceballos666/SIRAP_USA_ECUADOR) contiene el frontend, la API y la configuración del despliegue. Consulta la [API interactiva](https://eduardoceballos-sirap-usa-ecuador-hf.hf.space/docs), el [manual](../docs/manual_usuario.md) y los videos del [README principal](../README.md).


## English

This is the shared Vue frontend. It presents country-specific vehicle fields using the selected profile, while the API handles the corresponding vehicle lookup. Ecuador is the current operational profile; the U.S. profile is preparatory.
