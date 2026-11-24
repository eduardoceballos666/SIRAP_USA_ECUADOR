# Ecuador y Estados Unidos en la aplicación

El login FastAPI/Vue permite elegir **idioma y país: Ecuador o Estados Unidos**.
El token queda vinculado al país elegido. Las rutas `/ecuador/…` y `/usa/…` usan los
mismos componentes. El servidor rechaza solicitudes de otro país en esa sesión.
La selección se aplica a imágenes, video/cámara, verificaciones, registros y operaciones.
En Estados Unidos se leen por separado estado emisor y matrícula. No se corrigen
letras o dígitos por las posiciones del formato ecuatoriano.

## Modelo y umbrales

- Detector compartido: RT-DETRv2-S/OpenVINO, **semilla 2 ajustada para USA**, detección **0,70**.
- Ambos perfiles comparten la misma instancia del detector y los mismos pesos OCR.
  Ecuador solo cambia normalización y validación del texto; no se reentrena.
  No exige estado emisor; normaliza, por ejemplo, `ABC1234` a `ABC-1234`.
- El rendimiento del checkpoint con placas ecuatorianas sigue pendiente de evaluación.
- OCR: `cct-s-v2-global-model`, mínimo por carácter **0,94**.
- Las huellas de detector, manifiesto y OCR se verifican antes de inferir.
- Se deshace el relleno de las cajas declaradas como `padded_input` antes de recortar.
- No se usa silenciosamente la semilla 1 ni un detector alternativo para ningún país.
- Tesseract lee la leyenda del estado mediante vistas generales y bandas superiores.
  Los puntajes de similitud y Tesseract no son probabilidades calibradas.

El checkpoint se mantiene en un repositorio de modelos privado de Hugging Face,
identificado por commit y huellas en `models/usa/selected_checkpoint.json`.
El workflow comprueba acceso e integridad antes de actualizar el Space; configura
`SIRAP_USA_MODEL_TOKEN` como secreto de ejecución. Los pesos se recuperan al iniciar
la aplicación y no se publican en el código del Space.

Para una instalación local, también pueden indicarse `SIRAP_USA_DETECTOR_DIR` y
`SIRAP_USA_OCR_DIR`, apuntando a los artefactos verificados existentes. Una ruta
explícita equivocada produce un error; no se sobrescribe ni se sustituye el modelo.
Si faltan artefactos o Tesseract, las lecturas incompletas no habilitan apertura.

## Apertura normal habilitada para USA

`automatic_access.enabled: true` habilita el flujo **Registrar y abrir barrera**.
El reconocimiento por sí solo no mueve una barrera. Antes de aceptar esa acción,
el servidor comprueba:

1. Matrícula y estado completos, con detección ≥0,70 y OCR ≥0,94.
2. Dos identificadores de cuadro y dos imágenes RGB diferentes, recibidos dentro
   de 7,5 segundos, en la misma sesión de captura, usuario, garita e identidad.
3. Un comprobante emitido por el servidor, de hasta 30 segundos. No se confía en
   probabilidades o contadores enviados por el navegador. Una placa escrita a mano
   no puede simular dos lecturas del detector.
4. La lista blanca vigente se consulta nuevamente al registrar la apertura; una
   restricción o revocación impide abrir.
5. Se persiste la solicitud antes de accionar la barrera. El comprobante se reserva
   contra solicitudes concurrentes y se consume antes de abrir. Si la barrera falla,
   no se vuelve a utilizar esa confirmación para repetir automáticamente la orden.

Una sola foto estática, o el reenvío del mismo cuadro, no confirma dos cuadros.
La cámara/video puede proporcionar dos cuadros diferentes. El contenido distinto
es una comprobación informática; no demuestra por sí solo una captura física
independiente ni resuelve placas clonadas.

Los comprobantes son temporales por proceso. El Space usa un worker. Para varios
workers se necesita un almacén de comprobantes compartido; después de reiniciar,
las confirmaciones previas ya no sirven y se deben obtener dos cuadros nuevos.

## Registro, listas e historial

La identidad interna USA se guarda como `US:CA:DEMO123` en los CSV existentes.
La misma matrícula de otro estado tiene otra clave. Las filas anteriores de Ecuador
conservan sus claves `XXX-0000`; no se migran ni se vuelven a interpretar.

La API y la interfaz muestran matrícula, país y estado por separado. Administración
utiliza `identity_key` para editar o seleccionar filas sin mezclar estados.
El historial y sus exportaciones incluyen país, estado, clave, comprobante, semilla
y evidencia de los cuadros de una apertura. Dashboard cuenta identidades completas.
Vehículos, listas, propietarios e historial de demostración se filtran por país;
usuarios, roles y garitas son comunes. Cambiar de país requiere volver al login.

Las placas de EE. UU. consultan el registro local y, con `vehicle_lookup.enabled: true`
en `config/countries/usa.yaml`, el informe público de J.D. Power (año y modelo, color,
tipo de carrocería; el estado es el confirmado). Solo se envían matrícula y estado
confirmado, nunca al SRI. El OCR llena las casillas de placa y de estado y la consulta sale sola;
si no leyó el estado y la persona lo elige en la casilla, la consulta sale en ese momento con la placa y el estado que
muestran las casillas, sin esperar a «Verificar». La interfaz de EE. UU. no muestra el resultado de esa
consulta: el panel «Detalles del vehículo» solo trae el botón «Ver detalles del vehículo en J.D. Power»
(en los seis idiomas de la interfaz), que abre en una pestaña nueva la página pública del informe con la
matrícula y el estado de las casillas, para que la persona lo lea ella misma. Lo abre su navegador; el servidor
no lo usa. Si J.D. Power niega el acceso al servidor (HTTP 401/403, 429), no se reintenta ni se evita. Con
`enabled: false` no se hace la consulta automática. Registrar una matrícula para una
prueba OCR no la añade a una lista blanca operativa; esa autorización sigue siendo
una acción explícita del usuario en Registro o Administración.

## Evidencia disponible

La recuperación de aperturas para ambos países conserva el UUID del intento entre
recargas y consultas de estado. El historial persistente rechaza ese UUID incluso
después de reiniciar y perder los comprobantes temporales. No se reenvía una orden
al reconectar. Las solicitudes no aceptadas pueden reservarse como canceladas;
las aceptadas sin resultado definitivo requieren revisión. Consulta el
[protocolo y las pruebas de recuperación](recuperacion_fallos.md).

Las ocho fotos ya revisadas son un lote de desarrollo. En el diagnóstico previo,
el flujo completo recuperó 9/10 matrículas legibles y 2/9 estados conocidos;
los recortes manuales pasaron de 3/9 a 5/9 estados. En las 7 escenas con referencia
completa hubo 8 placas detectadas, 3 omitidas y 0 falsas detecciones. La foto 3
conserva una región adicional dudosa y queda fuera de ese recuento por escenas. Estos resultados no constituyen un test final independiente
ni una estimación de falsas alarmas en escenas vacías.

Las pruebas automáticas del software usan matrículas, listas, imágenes y barrera
sintéticas. Verifican las reglas y la persistencia; no califican la exactitud real
del modelo ni accionan dispositivos físicos. El modo de barrera se sigue tomando
de la configuración existente, sin activar un controlador físico nuevo.

El endpoint público `/api/health` informa el commit desplegado, disponibilidad por
perfil y si ambos perfiles comparten la misma instancia del detector. Los resultados
históricos de otros modelos no se atribuyen al checkpoint actual en Acerca del modelo.
