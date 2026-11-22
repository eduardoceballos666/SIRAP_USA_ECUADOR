# Consideraciones éticas – SIRAP 1.0

> **Versionado:** SIRAP es el producto versión **1.0**. API 2.0.0, paquete frontend 2.0.0 y tag GitHub `v2.0` son identificadores técnicos de componentes/código; no cambian la versión del producto.

SIRAP lee placas de vehículos de **Ecuador y Estados Unidos**, las asocia con personas y empresas y decide si una barrera se abre. Una placa no es
solo un número: **identifica indirectamente a una persona** y, acumulada en un historial, revela sus horarios y
movimientos. Este documento analiza los riesgos del sistema y lo que se hizo para mitigarlos.

Ambos países comparten un único detector (RT-DETRv2-S, semilla 2, entrenada con placas de EE. UU.) y el mismo OCR. **El desempeño en Ecuador no se ha evaluado**, y en EE. UU. solo existe una comprobación de desarrollo con fotos ya revisadas, no un test independiente (ver [`results/README.md`](../results/README.md)). Por eso este documento no cita cifras de exactitud como garantía: las de modelos anteriores (YOLO11) son históricas y no describen el sistema vigente.

---

## 1. Análisis de sesgos

### 1.1 Sesgos del dataset

| Sesgo | Dónde | Efecto posible |
|---|---|---|
| **Geográfico** | El checkpoint compartido se ajustó con un dataset de placas europeas y de EE. UU.; no hay evaluación en Ecuador y la de EE. UU. es de desarrollo | La precisión en tipografías, colores y marcos ecuatorianos todavía no está cuantificada, y puede diferir entre estados de EE. UU. |
| **Estado emisor (EE. UU.)** | La leyenda del estado se lee con Tesseract; los nombres estilizados o en cursiva (p. ej. California, Tennessee, Dakota del Sur, Ohio) no se leen | La app se abstiene y exige revisión manual: los conductores de esos estados esperan más, aunque no se les rechaza automáticamente |
| **Provincial** | El OCR se validó con SAVH **Guayaquil**, donde predominan las placas de Guayas (`G…`) | Rendimiento no verificado para placas de otras provincias |
| **Tipo de vehículo** | El caso original fue la entrada de camiones a una planta; el dataset de detección mezcla autos y motos (placas extranjeras de dos filas) | Las placas de camiones (sucias, a veces pintadas) pueden leerse peor; el OCR no se evaluó con motos ecuatorianas |
| **Condiciones de captura** | Imágenes mayormente diurnas y con buena iluminación | Más errores de noche, con lluvia, contraluz o placas deterioradas |
| **Estado de la placa** | Placas legibles sobrerrepresentadas tras la revisión de SAVH (472 legibles de 739) | Las métricas de OCR sobre SAVH no reflejan las 267 ilegibles, que deben ir a verificación manual |
| **Tamaño (distancia)** | Aún falta medir el detector vigente por tamaño de placa | Es posible que las placas lejanas sean más difíciles; debe medirse con el modelo y los datos vigentes |

### 1.2 ¿A quién podría perjudicar?

El riesgo que más afecta a una persona es el **falso rechazo**: un residente o proveedor autorizado cuya placa se lee
mal y queda esperando. Este error se concentra en quienes tienen **placas antiguas, dañadas, sucias, de otras
provincias o de estados de EE. UU. cuya leyenda no se lee**, y en vehículos de carga — es decir, con más frecuencia en conductores de vehículos más viejos o de
trabajo. El **falso acceso** (abrir a quien no debía) afecta a la seguridad de toda la comunidad.

## 2. Equidad (fairness)

SIRAP no usa atributos demográficos y no clasifica personas. La pregunta de equidad es si **el error del sistema se
reparte igual** entre grupos de vehículos/placas. Por eso:

- Se debe medir el mAP por tamaño (pequeñas / medianas / grandes) con el detector vigente y reportar el tamaño de cada muestra; aún no existe esa medición.
- **Lectura del estado en EE. UU.** (medición de desarrollo, 751 recortes con estado conocido): se leyeron 523 (69,6 %), los 523 correctos y 0 erróneos; en el resto la app se abstiene. Es un diagnóstico de desarrollo, no un test independiente. La consecuencia para la equidad es **más revisión manual** para los estados cuya leyenda no se lee, no una decisión automática distinta.
- Las cifras de modelos anteriores (YOLO11) y los informes históricos de SAVH no predicen el desempeño del detector vigente ni una tasa de autorizaciones en producción.
- Se recomienda medir el EMR por **formato** (3 vs 4 dígitos: placas antiguas vs nuevas), por **provincia**
  (primera letra) en Ecuador y por **estado emisor** en EE. UU. cuando haya datos suficientes; esa métrica de paridad queda como trabajo futuro.

**Mitigaciones implementadas**

| Mitigación | Dónde |
|---|---|
| Las placas antiguas de 3 dígitos se normalizan (`GMS-429 → GMS-0429`) y no se rechazan por formato | `src/data_processing.py` |
| Corrección de confusiones letra/dígito según la posición (solo Ecuador; en EE. UU. no se aplica el formato ecuatoriano) | `normalize_plate` |
| Estado de EE. UU. ilegible o desconocido: la app se abstiene y pide revisión manual, en lugar de asignar un estado equivocado | `src/usa_jurisdiction.py`, `decide_usa_access` |
| Una lectura dudosa **nunca** se rechaza automáticamente: va a verificación manual | `src/access_control.py` |
| Lecturas a un carácter de una placa registrada se marcan «¿quiso decir…?» en lugar de «no registrado» | `decide_access` |
| El operador puede **corregir la placa a mano** y reevaluar | Módulo Reconocimiento y Acceso |

## 3. Privacidad

### 3.1 Datos personales tratados

| Dato | ¿Personal? | Tratamiento |
|---|---|---|
| Imagen del vehículo | Sí (puede mostrar conductor, otras placas) | **No se guarda** en la base; solo se procesa en memoria |
| Placa | Sí (identifica indirectamente al propietario) | Se guarda solo cuando se registra una operación |
| Propietario registrado localmente | Sí | Nombre y datos que registra el administrador para la operación; no se requieren cédula, domicilio ni teléfono |
| Nombre devuelto por consulta pública | Sí | La API lo conserva temporalmente en memoria; la exportación enriquecida independiente puede guardarlo si se configura |
| Matrícula y estado enviados a J.D. Power (EE. UU.) | Sí (identifican indirectamente al propietario) | Solo se envían la matrícula y el estado confirmado, nunca la imagen ni datos del propietario; el resultado se muestra al operador y se conserva en una caché temporal en memoria; no se guarda automáticamente en los CSV |
| Historial (fecha, hora, garita) | Sí (patrón de movimientos) | Solo inserción; acceso restringido al personal de la instalación |

### 3.2 Medidas

- **Minimización:** el esquema solo pide lo necesario para el control de acceso.
- **Datos ficticios** en la demo pública (archivos CSV de demostración); las imágenes reales de la garita y los registros de la
  planta **no** se publican (`data/README.md`).
- **Secretos fuera del código:** contraseñas y llaves se leen de variables de entorno; en el despliegue se guardan
  como Secrets de GitHub Actions y del Space. No se publican en el repositorio.
- **Validación de las entradas** (esquemas Pydantic) y escape de HTML en la interfaz; el almacenamiento es CSV, sin consultas SQL.
- En el Space, los secretos configurados permiten restaurar y sincronizar las tablas CSV con el repositorio privado
  `SIRAP_datos_privados`. El contenedor conserva una copia de trabajo temporal; el respaldo privado es la fuente de
  persistencia entre reinicios. En instalaciones propias, restrinja el repositorio y los permisos de acceso.
- **Versión web (producto SIRAP 1.0):** la imagen viaja por HTTPS hasta la API, se procesa en memoria y se descarta; la respuesta
  devuelve temporalmente el recorte para mostrarlo al operador. Las «lecturas de esta sesión» se guardan en la
  memoria del navegador hasta que se registran. Los CSV de datos de la demo son ficticios y se respaldan en el
  repositorio privado configurado; las imágenes reales de la garita no se publican.
- **Contraseñas y sesiones:** nunca se guardan en texto plano (PBKDF2-SHA256, 240 000 iteraciones); el token de
  sesión se guarda en el navegador y vence a las 12 h; la clave de firma (`SIRAP_JWT_SECRET`) es un *secret* del
  despliegue, no del código.

### 3.3 Cumplimiento normativo

En Ecuador aplica la **Ley Orgánica de Protección de Datos Personales (LOPDP, 2021)**, comparable al RGPD europeo.
Para un despliegue real la instalación (responsable del tratamiento) debe:

1. **Informar** con un letrero visible en la garita que existe reconocimiento automático de placas, su finalidad y
   a quién dirigirse.
2. Tener una **base legal** (interés legítimo de seguridad o consentimiento de residentes/proveedores).
3. Definir un **plazo de conservación** del historial (sugerido: 90 días, salvo incidentes) y borrarlo después.
4. Atender **derechos** de acceso, rectificación y eliminación de los titulares.
5. No ceder los datos a terceros sin base legal.

#### Estados Unidos

No existe una ley federal única de protección de datos que cubra este uso: las reglas sobre lectores automáticos de placas, privacidad y acceso a registros de vehículos **varían por estado y por tipo de instalación**. Antes de un despliegue real, la instalación debe revisar la normativa que le aplica y obtener asesoría legal; este documento no la sustituye. Los puntos 1 a 5 de arriba (aviso, base legal, plazo de conservación, derechos y no cesión) son buenas prácticas igualmente aplicables.

La consulta a J.D. Power se activó (`vehicle_lookup.enabled` en `config/countries/usa.yaml`) tras confirmar el propietario del proyecto que contaba con acceso autorizado. No intenta eludir controles de acceso: si el sitio responde 401, 403 o 429 no reintenta y la interfaz conserva los datos del registro local. Con `enabled: false` solo se consulta el registro local.

#### Consulta pública del SRI y privacidad

La aplicación consulta información **pública del vehículo** en los servicios del SRI y muestra marca, modelo y año en
la ficha. El propio SRI ofrece consultas vehiculares por placa y publica los datos del vehículo que resultan de esas
consultas ([servicios de impuestos vehiculares del SRI](https://www.sri.gob.ec/impuestos-vehiculares)). En el alcance
descrito aquí, la app descarga y presenta esos campos vehiculares; no obtiene del SRI el nombre, la cédula, el
domicilio ni el teléfono del propietario. Consultar y descargar esos datos públicos del vehículo, por sí solo, no
significa acceder a información privada ni vulnera la privacidad de una persona.

La información de propietario ofrecida por **EcuadorLegalOnline es de pago**; por esa razón, SIRAP no integra
ni consulta ese servicio, no muestra datos obtenidos de esa fuente y no los guarda. Si la ficha muestra un propietario,
el dato proviene del registro local de vehículos de SIRAP.

Que los datos públicos del SRI sean consultables no autoriza cualquier uso posterior de información que identifique
a una persona. Una placa, un nombre o su combinación con imágenes e historial pueden hacer identificable a alguien.
Por eso SIRAP limita la consulta a su finalidad de apoyo al control de acceso, minimiza los campos y no presenta el
resultado como verificación oficial de identidad o titularidad. La LOPDP regula el tratamiento de datos personales y
la SPDP aclara que la disponibilidad pública no elimina por sí sola las obligaciones de finalidad, proporcionalidad,
minimización y seguridad ([LOPDP](https://spdp.gob.ec/wp-content/uploads/2024/12/03.pdf.pdf);
[criterio de la SPDP sobre fuentes públicas](https://www.spdp.gob.ec/docs/consultas-absueltas/2026-2/oficio-n-spdp-ird-2026-0242-o/)).

Estas consultas no intervienen en la regla de autorización ni intentan eludir CAPTCHA o controles de acceso. Las
fuentes pueden cambiar, devolver datos incompletos o no responder; la interfaz conserva los datos locales disponibles
y muestra que la consulta externa no pudo completarse.

## 4. Transparencia y explicabilidad

- El sistema es **interpretable por diseño** en lo que decide: la regla de acceso es explícita y está documentada
  ([arquitectura.md](arquitectura.md) y `src/access_control.py`). La parte de «caja negra» (detector y OCR) se acota con salidas verificables por un humano.
- La interfaz muestra **por qué** decidió: la caja de la placa sobre la imagen, el **recorte que leyó el OCR**, el
  texto crudo leído, la **confianza OCR** con color, la lista aplicada y el motivo (p. ej. «Confianza OCR 48 % <
  umbral 94 %»).
- El módulo **Acerca del modelo** explica el funcionamiento, las métricas y las limitaciones (incluido que el
  rendimiento en Ecuador no está evaluado) y muestra el estado del detector cargado y los errores que impiden el reconocimiento.
- No se usan SHAP/LIME porque la decisión final no depende de atributos tabulares; la evidencia visual (caja +
  recorte + probabilidad por carácter) es la explicación pertinente para un operador.

## 5. Impacto social

| Positivo | Negativo posible |
|---|---|
| Menos colas y tiempo de espera en la garita | Pérdida o cambio de tareas del personal de garita |
| Menos errores de transcripción | Sensación de vigilancia constante |
| Historial auditable ante incidentes | Uso del historial para controlar horarios de personas (p. ej. empleadas domésticas, proveedores) |
| Listas actualizadas en tiempo real | Exclusión de quien tiene placa ilegible si se elimina al guardia |

**Beneficiados:** administración, residentes, empresas. **Posibles perjudicados:** conductores con placas
deterioradas o antiguas, trabajadores sometidos a control horario no consentido y el personal de garita si el
sistema se usa para reemplazarlo en lugar de asistirlo. SIRAP se diseñó como **asistente del operador**, no como
sustituto: siempre hay un humano que confirma.

## 6. Responsabilidad (accountability)

- **Si el modelo falla, la decisión final es del operador**, que confirma cada apertura; el sistema no abre solo.
- La **apertura manual** exige motivo (≥ 10 caracteres) y confirmación explícita, y queda registrada con nombre.
- El **historial es de solo inserción**: la app no permite editar ni borrar operaciones.
- **Autenticación por usuario (SIRAP 1.0):** cada persona inicia sesión con su contraseña (guardada solo como hash
  PBKDF2-SHA256 con sal) y recibe una sesión firmada (JWT) que vence a las 12 h. Cada operación queda asociada al
  usuario autenticado, no a un nombre escrito a mano, lo que permite auditar quién abrió la barrera.
- **Permisos por rol:** los tres perfiles autenticados pueden consultar las tablas administrativas mediante `GET /api/admin/{table}`. El Operador puede hacerlo desde la API, aunque la interfaz no muestra la sección Administración; el Supervisor la consulta desde la interfaz en modo de solo lectura y también puede exportar el Historial. Solo el Administrador puede modificar vehículos, listas, garitas y usuarios. Las operaciones de escritura se restringen en el servidor.
- **La interfaz no puede forzar una apertura:** antes de registrar, la API vuelve a calcular la decisión con la placa
  final; solo abre automáticamente un AUTORIZADO y la apertura manual exige motivo.
- **En EE. UU., la apertura exige más evidencia:** estado y matrícula completos, dos cuadros distintos confirmados por
  el servidor en 7,5 s (comprobante de un solo uso, 30 s) y una nueva consulta de la lista vigente al registrar
  ([usa_app_integration.md](usa_app_integration.md)).
- **Responsables:** la instalación que opera SIRAP es responsable del tratamiento de datos; el equipo desarrollador
  responde por los defectos del software documentados aquí.

**Plan de monitoreo y actualización**

| Qué | Cada cuánto | Acción si empeora |
|---|---|---|
| % de lecturas enviadas a verificación manual | Semanal (Dashboard) | Revisar cámara/iluminación; reentrenar con imágenes locales |
| Aperturas manuales y su motivo | Semanal | Auditar abusos o fallas recurrentes |
| EMR sobre una muestra etiquetada de la garita | Mensual | Ajustar umbral o reentrenar |
| Vigencia de listas | Mensual | Depurar autorizaciones vencidas |

## 7. Uso dual y mal uso

El mismo sistema podría usarse para **rastrear vehículos y personas** fuera del control de acceso (vigilancia
masiva, seguimiento de una persona concreta, perfiles de movimiento, venta de datos).

**Salvaguardas**

- La app funciona **por captura en un punto de control**: no busca placas en video público ni cruza cámaras.
- Sin búsqueda de «dónde estuvo esta placa» fuera de la instalación. El historial se limita a cada instalación; en el Space, los CSV operativos se restauran y sincronizan con el repositorio privado `SIRAP_datos_privados`. En una instalación local, se guardan en los archivos CSV configurados en el servidor.
- Imágenes no almacenadas; datos mínimos.
- Licencia y documentación declaran los usos prohibidos (abajo).

**Usos prohibidos:** vigilancia de vía pública, seguimiento de personas, decisiones automáticas sin operador,
sanciones o multas automáticas, cruce con bases de datos sin base legal, discriminación de acceso por cualquier
característica de las personas.

## 8. Limitaciones reconocidas

**No usar SIRAP**

- como único control en instalaciones de alta seguridad sin operador humano;
- para multas, sanciones o pruebas legales;
- con placas de motos ni de países distintos de Ecuador y Estados Unidos (no se evaluaron);
- como sistema validado en Ecuador: el detector compartido no se ha evaluado con placas ecuatorianas;
- con cámaras que no encuadren la placa de frente o con placas que ocupen menos de ≈0,2 % del cuadro.

**Casos donde no es confiable:** noche sin iluminación infrarroja, lluvia o niebla, placas sucias, dobladas,
tapadas, con stickers o marcos que tapan caracteres, placas pintadas a mano en camiones, ángulos mayores a ≈30°,
contraluz fuerte.

**Advertencias a los usuarios** (también en la app): la confianza OCR no es una garantía; ante cualquier duda el
operador debe verificar visualmente; la versión publicada usa una barrera simulada y datos ficticios.


## Aplicación publicada y documentación

La aplicación y el repositorio permiten revisar el sistema y sus límites de uso:

- [Aplicación desplegada en Hugging Face](https://eduardoceballos-sirap-usa-ecuador-hf.hf.space)
- [Hugging Face Space y despliegue](https://huggingface.co/spaces/eduardoceballos/SIRAP_USA_ECUADOR_HF)
- [Código fuente y documentos de SIRAP_USA_ECUADOR](https://github.com/eduardoceballos666/SIRAP_USA_ECUADOR)
- [API interactiva](https://eduardoceballos-sirap-usa-ecuador-hf.hf.space/docs) · Manual de usuario ([ES](manual/SIRAP_Manual_ES.pdf) · [EN](manual/SIRAP_Manual_EN.pdf))

La interfaz está disponible en seis idiomas (inglés, español, portugués, francés, alemán e italiano). Las lecturas de placas requieren verificación humana cuando existe duda; la demostración no autoriza decisiones automáticas reales ni sustituye las medidas de privacidad descritas arriba. Más información en el [README](../README.md).
