# Recuperación de operaciones tras reinicios o cortes de conexión

La interfaz conserva el identificador de cada intento antes de enviarlo. Al recargar
la página, volver a iniciar sesión con el mismo usuario y país, o recuperar conexión,
consulta el resultado persistente sin repetir la orden de apertura. Esta protección
se aplica tanto a Ecuador como a USA y mantiene el modelo y los umbrales vigentes.

## Qué verá el operador

Si se perdió la respuesta, aparece **Operación pendiente de confirmar**, con la
garita y el ID. **Consultar resultado** lee el historial privado. Una respuesta
confirmada recupera el resultado; no mueve otra vez la barrera. Cambiar de garita,
limpiar una lectura o cerrar sesión no borra un intento incierto.

| Estado guardado | Interpretación | Recuperación |
|---|---|---|
| `CONFIRMADA` | El controlador confirmó la orden y el resultado quedó guardado | Mostrar el resultado, sin repetir la apertura |
| `FALLIDA` | Fallo confirmado por la barrera simulada | Mostrar el fallo; una nueva operación exige otra acción explícita |
| `NO_APLICA` | Registro sin apertura | Recuperar el registro |
| `CANCELADA` | Se reservó el ID como cancelado antes de aceptar una apertura | Permitir una nueva operación explícita; una llegada tardía del ID anterior se rechaza |
| `SOLICITADA` o `INDETERMINADA` | Hay una solicitud aceptada sin resultado definitivo | Mantener el aviso y exigir revisión del historial y del controlador; no reenviar automáticamente |

Un `404` tampoco demuestra que la orden no llegó: el primer envío puede seguir en
tránsito. **Cancelar intento no registrado** intenta reservar ese mismo ID como
cancelado. Si la apertura ya fue aceptada, devuelve su estado sin cancelarla ni
accionarla. Si la cancelación gana la escritura persistente, el envío original que
llegue después no podrá ordenar una apertura. La cancelación queda en el historial.

Si el estado es incierto, inspeccione la barrera y el registro del controlador antes
de conciliar el resultado. La aplicación conserva esa incertidumbre; una ausencia
de respuesta no demuestra que la barrera esté cerrada. No cambie el identificador
para repetir una orden cuyo resultado todavía no conoce.

## Persistencia y API

- GitHub privado sigue siendo la fuente de verdad de los CSV. Al reiniciar se
  recuperan sus datos; una caída remota no habilita el uso de una copia local vieja.
- Se guarda `SOLICITADA` antes de contactar al controlador. Una escritura sin
  confirmación impide despachar la orden, aunque el servidor remoto haya alcanzado
  a guardar la solicitud.
- El UUID se comprueba en todo el historial, aunque ya no aparezca en las últimas
  5.000 filas de la vista. Un UUID duplicado recibe `409` y no acciona la barrera.
- Las actualizaciones de CSV comparan su SHA. Un conflicto se aborta sin volver a
  escribir una copia antigua. La copia local se sincroniza con el disco antes del reemplazo.
- Las filas nuevas conservan `operador_usuario` y `barrera_simulada`. El nombre
  visible del operador no se utiliza como identidad. Las filas antiguas permanecen
  en el historial; no se borran ni se inicializan de nuevo.
- El navegador guarda solamente usuario, país, ID, acción, garita, movimiento y
  fecha del intento. No añade placas, imágenes, tokens ni probabilidades a ese
  registro. No caduca ni olvida automáticamente un intento incierto.

| Endpoint | Función |
|---|---|
| `POST /api/operations` | Aceptar una operación; las aperturas requieren un UUID persistente |
| `GET /api/operations/{uuid}/status` | Consultar su resultado, sin efectos sobre la barrera |
| `POST /api/operations/{uuid}/cancel` | Reservar como cancelado un intento aún no aceptado; nunca ordena una apertura |

Las consultas requieren autenticación y respetan el país de la sesión. Solo el
usuario original o un Supervisor/Administrador del mismo país pueden recuperar
el resultado. Para filas antiguas sin `operador_usuario`, se requiere uno de esos
roles de supervisión. Las respuestas de estado no se almacenan en caché. Una caída
del almacenamiento devuelve `503`, conservando el identificador pendiente.

El controlador HTTP recibe `operacion_id` en JSON y en `Idempotency-Key`. Se hace
un único intento de transporte, sin reintentos ni redirecciones. Para deduplicar
también dentro del dispositivo, su implementación debe reconocer y conservar esa
clave. El código de SIRAP evita volver a despachar una misma solicitud aceptada;
no certifica por sí solo la posición física de una barrera.

## Comprobaciones del 16 de noviembre de 2026

Las **19 pruebas de recuperación** pasaron con transporte GitHub y controlador
simulados. Tres terminan abruptamente un proceso y crean otro con una copia local
nueva, recuperada desde un almacén persistente de prueba:

1. Corte tras guardar la solicitud: una fila conservada, cero órdenes al dispositivo.
2. Corte tras accionar, antes de guardar el resultado: una fila `SOLICITADA`, una
   sola orden y resultado físico sin confirmar.
3. Corte tras guardar la confirmación, antes de responder: una fila `CONFIRMADA`,
   una sola orden y recuperación mediante consulta.

En los tres casos, reenviar el mismo UUID al proceso nuevo recibió `409` sin emitir
otra orden. También se verificaron pérdida de conexión antes/después de confirmar
escrituras, fallo de la copia local, solicitudes concurrentes, cancelación frente a
una llegada tardía, identidades con el mismo nombre visible, historial de 5.001
filas, timeout y redirección del controlador.

La suite local obtuvo **160 pruebas Python aprobadas y una omitida**, además de
**22 pruebas de interfaz aprobadas** y compilación Vue correcta. La prueba omitida
descarga un OCR externo; la ejecución de Python bloqueó conexiones de Internet y
esa prueba no forma parte de las 19 comprobaciones de recuperación. Las pruebas
de interfaz ejecutan las funciones reales de registro y recuperación del componente.

El [informe agregado](../results/metrics/operation_recovery_software.json) contiene el
alcance, los casos y las huellas del código. No se cortó una conexión de producción,
no se crearon operaciones en el registro real y no se accionó una barrera física.
Estos resultados comprueban recuperación de software; no son métricas de OCR ni
sustituyen la prueba con el equipo físico definitivo.
