"""Bilingual text of the SIRAP user manual, part 2: actions, history, dashboard, administration, model, phones,
cases, troubleshooting, checklist and appendices. Same conventions as ``manual_content.py``.
"""
from __future__ import annotations


def build(d) -> None:
    ch_actions(d)
    ch_history(d)
    ch_dashboard(d)
    ch_admin(d)
    ch_model(d)
    ch_mobile(d)
    ch_cases(d)
    ch_trouble(d)
    ch_checklist(d)
    appendix_glossary(d)
    appendix_reference(d)


# ---------------------------------------------------------------------------------------------------------------
def ch_actions(d) -> None:
    d.h1("Recording actions, the barrier and contingencies",
         "Registrar acciones, barrera y contingencias")
    d.p(
        "A reading is only a proposal until the operator records an action. Readings are saved to the history <b>only when "
        "an action is confirmed</b>; clearing the screen never deletes an operation that was already recorded.",
        "Una lectura es solo una propuesta hasta que el operador registra una acción. Las lecturas se guardan en el historial "
        "<b>solo cuando se confirma una acción</b>; limpiar la pantalla nunca borra una operación ya registrada.",
    )
    d.h2("Which action is available", "Qué acción está disponible")
    d.table(
        [("Button", "Botón"), ("When it is enabled", "Cuándo se habilita"), ("What it records", "Qué registra")],
        [
            [("Register and open gate (yellow)", "Registrar y abrir barrera (amarillo)"),
             ("Only when the result is <b>Authorized</b>.", "Solo cuando el resultado es <b>Autorizado</b>."),
             ("The operation and a barrier opening request. In the default configuration the barrier is <b>simulated</b>.",
              "La operación y una solicitud de apertura de barrera. En la configuración por defecto la barrera es <b>simulada</b>.")],
            [("Record rejection", "Registrar rechazo"),
             ("When the result is <b>Denied</b>.", "Cuando el resultado es <b>Denegado</b>."),
             ("The rejection; the barrier stays closed.", "El rechazo; la barrera permanece cerrada.")],
            [("Record without opening", "Registrar sin abrir"),
             ("When the result does not allow opening (not registered, manual review, no authorization).",
              "Cuando el resultado no permite abrir (no registrado, verificación manual, sin autorización)."),
             ("The reading and the decision, without opening the barrier.", "La lectura y la decisión, sin abrir la barrera.")],
            [("Manual opening (contingency) (blue)", "Apertura manual (Contingencia) (azul)"),
             ("When there is a decision on screen. Requires a written reason.", "Cuando hay una decisión en pantalla. Exige un motivo escrito."),
             ("A manual opening with your username and the reason.", "Una apertura manual con su usuario y el motivo.")],
        ],
        caption=("Action buttons on Recognition and Access.", "Botones de acción en Reconocimiento y Acceso."),
        widths=[27, 38, 35],
    )
    d.note("danger", ("The barrier never opens by itself", "La barrera nunca se abre sola"),
           "Even for an authorized plate the gate opens only after the operator presses <b>Register and open gate</b>. The server "
           "checks the authorization again at that moment and saves the request <b>before</b> sending the order to the barrier. "
           "If the record cannot be saved, the opening is blocked.",
           "Incluso con una placa autorizada, la barrera se abre solo cuando el operador pulsa <b>Registrar y abrir barrera</b>. "
           "El servidor vuelve a comprobar la autorización en ese momento y guarda la solicitud <b>antes</b> de enviar la orden "
           "a la barrera. Si el registro no puede guardarse, la apertura se bloquea.")
    d.h2("Manual opening for a contingency", "Apertura manual por contingencia")
    d.p(
        "Use it only under the contingency procedure authorized by your organization, for example when the plate is dirty but "
        "the driver and the vehicle have been identified by other means.",
        "Úsela solo bajo el procedimiento de contingencia autorizado por su organización, por ejemplo cuando la placa está "
        "sucia pero el conductor y el vehículo se identificaron por otros medios.",
    )
    d.steps([
        ("Press <b>Manual opening (contingency)</b>.", "Pulse <b>Apertura manual (Contingencia)</b>."),
        ("Write the <b>reason</b>: at least 10 characters (the limit is 250). Say who verified what and how.",
         "Escriba el <b>motivo</b>: al menos 10 caracteres (el máximo es 250). Indique quién verificó qué y cómo."),
        ("United States of America profile only: confirm the <b>issuing state</b> of the plate in the window.",
         "Solo en el perfil de Estados Unidos de América: confirme el <b>estado emisor</b> de la placa en la ventana."),
        ("Press <b>Open and record</b>. The operation is saved with your username, the reason and the result of the barrier.",
         "Pulse <b>Abrir y registrar</b>. La operación se guarda con su usuario, el motivo y el resultado de la barrera."),
    ])
    d.fig("10_contingency",
          "The contingency window: the reason is mandatory and is stored with the operation.",
          "La ventana de contingencia: el motivo es obligatorio y se guarda con la operación.")
    d.h2("Recent readings of the session", "Lecturas recientes de la sesión")
    d.p(
        "The strip under the image lists the latest readings of this session. <b>View all</b> opens the full list; from there "
        "<b>Export CSV</b> downloads the session readings and <b>Clear</b> empties that list. Neither action touches the "
        "History, which only contains recorded operations.",
        "La franja bajo la imagen lista las últimas lecturas de esta sesión. <b>Ver todas</b> abre la lista completa; desde "
        "allí <b>Exportar CSV</b> descarga las lecturas de la sesión y <b>Limpiar</b> vacía esa lista. Ninguna de las dos "
        "acciones afecta al Historial, que solo contiene operaciones registradas.",
    )
    d.fig("11_session_readings",
          "Readings from this session: time, image, plate and result.",
          "Lecturas de esta sesión: hora, imagen, placa y resultado.")
    d.h2("If the connection fails during an operation", "Si la conexión falla durante una operación")
    d.p(
        "Before sending an attempt, the screen keeps its unique identifier. If the answer is lost (the page is reloaded, the "
        "connection drops, the session expires) a notice <b>Operation awaiting confirmation</b> appears with the checkpoint "
        "and the identifier. Press <b>Check result</b> to read the saved state; this never sends the order again. If the "
        "server confirms that the attempt was never accepted, <b>Cancel unregistered attempt</b> reserves that identifier as "
        "cancelled so that a late arrival cannot open the barrier.",
        "Antes de enviar un intento, la pantalla conserva su identificador único. Si se pierde la respuesta (se recarga la "
        "página, se cae la conexión, caduca la sesión) aparece el aviso <b>Operación pendiente de confirmar</b> con la garita "
        "y el identificador. Pulse <b>Consultar resultado</b> para leer el estado guardado; esto nunca vuelve a enviar la "
        "orden. Si el servidor confirma que el intento nunca fue aceptado, <b>Cancelar intento no registrado</b> reserva ese "
        "identificador como cancelado para que una llegada tardía no pueda abrir la barrera.",
    )
    d.table(
        [("Saved state", "Estado guardado"), ("Meaning", "Significado"), ("What to do", "Qué hacer")],
        [
            [("CONFIRMED", "CONFIRMADA"), ("The controller confirmed the order.", "El controlador confirmó la orden."),
             ("Nothing; the result is shown.", "Nada; se muestra el resultado.")],
            [("FAILED", "FALLIDA"), ("The barrier reported a failure.", "La barrera informó un fallo."),
             ("A new opening needs a new explicit action.", "Una nueva apertura exige una nueva acción explícita.")],
            [("NOT APPLICABLE", "NO APLICA"), ("A record without opening.", "Un registro sin apertura."),
             ("Nothing.", "Nada.")],
            [("CANCELLED", "CANCELADA"), ("The attempt was cancelled before being accepted.", "El intento se canceló antes de ser aceptado."),
             ("You may start a new operation.", "Puede iniciar una nueva operación.")],
            [("REQUESTED / INDETERMINATE", "SOLICITADA / INDETERMINADA"),
             ("The request was accepted but the final result is unknown.", "La solicitud fue aceptada pero se desconoce el resultado final."),
             ("Check the barrier and the History. <b>Do not repeat the opening.</b>", "Revise la barrera y el Historial. <b>No repita la apertura.</b>")],
        ],
        caption=("Barrier states shown in the History.", "Estados de barrera que muestra el Historial."),
        widths=[24, 38, 38],
    )
    d.note("warn", ("Uncertain result", "Resultado incierto"),
           "A missing answer does not prove that the barrier stayed closed. Inspect the barrier and the controller log before "
           "reconciling, and never change the identifier to repeat an order whose result you do not know yet.",
           "La ausencia de respuesta no demuestra que la barrera siguió cerrada. Inspeccione la barrera y el registro del "
           "controlador antes de conciliar, y nunca cambie el identificador para repetir una orden cuyo resultado aún no conoce.")


# ---------------------------------------------------------------------------------------------------------------
def ch_history(d) -> None:
    d.h1("History of operations", "Historial de operaciones")
    d.p(
        "<b>History</b> lists the actions that were recorded for the country of your session. It is the right place to check "
        "an operation that is already closed. All roles can search it; <b>Supervisor</b> and <b>Administrator</b> can also "
        "export the filtered results.",
        "<b>Historial</b> lista las acciones registradas para el país de su sesión. Es el lugar adecuado para consultar una "
        "operación ya cerrada. Todos los perfiles pueden buscar en él; <b>Supervisor</b> y <b>Administrador</b> pueden además "
        "exportar los resultados filtrados.",
    )
    d.fig("12_history",
          "Operations history (Ecuador): filters on top, one row per recorded operation below. The columns continue to the "
          "right (list, reason, origin, operator).",
          "Historial de operaciones (Ecuador): filtros arriba y una fila por operación registrada debajo. Las columnas "
          "continúan a la derecha (lista, motivo, origen, operador).")
    d.h2("Search and export", "Buscar y exportar")
    d.steps([
        ("Open <b>History</b> in the left menu.", "Abra <b>Historial</b> en el menú izquierdo."),
        ("Choose <b>From</b> and <b>To</b>. By default the last seven days are shown.",
         "Elija <b>Desde</b> y <b>Hasta</b>. Por defecto se muestran los últimos siete días."),
        ("Optionally filter by plate, checkpoint, result and movement (entry or exit). United States of America profile: also by "
         "<b>issuing state</b>.",
         "Si lo desea, filtre por placa, garita, resultado y movimiento (entrada o salida). Perfil de Estados Unidos de América: también "
         "por <b>estado emisor</b>."),
        ("Press <b>Search</b>.", "Pulse <b>Buscar</b>."),
        ("Supervisors and administrators can press <b>Export CSV</b> to download the rows that match the filters.",
         "Supervisores y administradores pueden pulsar <b>Exportar CSV</b> para descargar las filas que coinciden con los filtros."),
    ])
    d.h2("Reading the columns", "Cómo interpretar las columnas")
    d.table(
        [("Column", "Columna"), ("Meaning", "Significado")],
        [
            [("Date and time", "Fecha y hora"), ("When the operation was recorded (time zone of the installation).", "Cuándo se registró la operación (zona horaria de la instalación).")],
            [("Checkpoint · Move", "Garita · Movimiento"), ("Where it happened and whether it was an entry or an exit.", "Dónde ocurrió y si fue entrada o salida.")],
            [("Read plate", "Placa leída"), ("What the OCR proposed.", "Lo que propuso el OCR.")],
            [("Final plate", "Placa final"), ("The text confirmed before recording, including any correction. United States of America: issuing state shown below it.",
                                              "El texto confirmado antes de registrar, con la corrección si la hubo. Estados Unidos de América: debajo se muestra el estado emisor.")],
            [("OCR conf.", "Conf. OCR"), ("Lowest per-character probability of the reading.", "Probabilidad mínima por carácter de la lectura.")],
            [("Result", "Resultado"), ("The access decision at that moment: Authorized, Denied, Not registered, Manual review…",
                                      "La decisión de acceso en ese momento: Autorizado, Denegado, No registrado, Verificación manual…")],
            [("Action", "Acción"), ("Automatic opening, manual opening, rejection or record only; the reason when it was a contingency.",
                                   "Apertura automática, apertura manual, rechazo o solo registro; el motivo si fue una contingencia.")],
            [("Gate status", "Estado de la barrera"), ("Confirmed, failed, cancelled, requested or not applicable (see chapter 7).",
                                                        "Confirmada, fallida, cancelada, solicitada o no aplica (véase el capítulo 7).")],
            [("Operation ID", "ID de operación"), ("Unique identifier of the attempt; a repeated identifier is rejected.",
                                                    "Identificador único del intento; un identificador repetido se rechaza.")],
            [("Operator · Origin", "Operador · Origen"), ("Who recorded it and whether it came from a detection or is a DEMO row.",
                                                           "Quién lo registró y si proviene de una detección o es una fila DEMO.")],
        ],
        caption=("Columns of the operations history.", "Columnas del historial de operaciones."),
        widths=[24, 76],
    )
    d.fig("34_usa_history",
          "History with the United States of America profile: an <b>Issuing state</b> filter is added and each final plate shows its state.",
          "Historial con el perfil de Estados Unidos de América: se añade el filtro <b>Estado emisor</b> y cada placa final muestra su estado.")
    d.note("info", ("Tips", "Consejos"),
           "To investigate a correction, compare <i>Read plate</i> and <i>Final plate</i>. To report real operations, exclude the "
           "DEMO rows. Store exported CSV files in an authorized place, share them only with authorized people and delete them "
           "according to your organization's policy.",
           "Para investigar una corrección, compare <i>Placa leída</i> y <i>Placa final</i>. Para informar operaciones reales, "
           "excluya las filas DEMO. Guarde los CSV exportados en un lugar autorizado, compártalos solo con personas autorizadas "
           "y elimínelos según la política de su organización.")


# ---------------------------------------------------------------------------------------------------------------
def ch_dashboard(d) -> None:
    d.h1("Dashboard", "Dashboard")
    d.p(
        "The <b>Dashboard</b> summarizes the recorded operations of your country: how many vehicles came in and out, how many "
        "different plates were identified, which results were produced and where the alerts are.",
        "El <b>Dashboard</b> resume las operaciones registradas de su país: cuántos vehículos entraron y salieron, cuántas "
        "placas distintas se identificaron, qué resultados se produjeron y dónde están las alertas.",
    )
    d.fig("13_dashboard",
          "Operations dashboard (Ecuador, last 7 days, with demo operations included).",
          "Dashboard de operaciones (Ecuador, últimos 7 días, con operaciones de demostración incluidas).")
    d.h2("Controls and indicators", "Controles e indicadores")
    d.table(
        [("Element", "Elemento"), ("What it shows", "Qué muestra")],
        [
            [("Period", "Periodo"), ("Today, Last 7 days or Last 30 days.", "Hoy, Últimos 7 días o Últimos 30 días.")],
            [("Include demo operations", "Incluir operaciones de demostración"),
             ("Adds or removes the generated DEMO rows. Turn it off before presenting real figures.",
              "Añade o quita las filas DEMO generadas. Desactívela antes de presentar cifras reales.")],
            [("Entries · Exits", "Ingresos · Salidas"), ("Number of recorded operations of each movement type.", "Número de operaciones registradas de cada tipo de movimiento.")],
            [("Plates identified", "Placas identificadas"), ("Number of <i>different</i> plates (United States of America: state + serial).",
                                                              "Número de placas <i>distintas</i> (Estados Unidos de América: estado + matrícula).")],
            [("Alerts", "Alertas"), ("Denied, not registered and manual-opening operations.", "Operaciones denegadas, no registradas y aperturas manuales.")],
            [("Operations by hour", "Operaciones por hora"), ("Stacked bars by result for each hour of the day.", "Barras apiladas por resultado para cada hora del día.")],
            [("Access result", "Resultado de acceso"), ("Share of each result in the period.", "Proporción de cada resultado en el periodo.")],
            [("Entries by checkpoint", "Ingresos por garita"), ("Entries and exits at each checkpoint.", "Ingresos y salidas en cada garita.")],
            [("Recent alerts", "Alertas recientes"), ("The latest alert rows with checkpoint, plate, result, action and operator.",
                                                        "Las últimas filas de alerta con garita, placa, resultado, acción y operador.")],
        ],
        caption=("Dashboard elements.", "Elementos del Dashboard."),
        widths=[28, 72],
    )
    d.p(
        "Press <b>Refresh</b> to load the figures again. If a chart looks empty, check the period and whether DEMO rows are "
        "included before assuming there is no activity. The theme button (moon icon, bottom left) switches between light and "
        "dark mode.",
        "Pulse <b>Actualizar</b> para cargar de nuevo las cifras. Si un gráfico aparece vacío, revise el periodo y si se "
        "incluyen las filas DEMO antes de suponer que no hay actividad. El botón de tema (icono de luna, abajo a la izquierda) "
        "alterna entre modo claro y oscuro.",
    )
    d.pair("14_dashboard_dark",
           ("The same dashboard in dark mode.", "El mismo dashboard en modo oscuro."),
           "35_usa_dashboard",
           ("Dashboard of the United States of America profile (separate data, same layout).",
            "Dashboard del perfil de Estados Unidos de América (datos separados, misma disposición)."))
    d.note("warn", ("Each country has its own data", "Cada país tiene sus propios datos"),
           "Ecuador and United States of America history, lists and indicators are kept apart. To see the other country, sign out and sign "
           "in again choosing it.",
           "El historial, las listas y los indicadores de Ecuador y Estados Unidos de América están separados. Para ver el otro país, cierre "
           "sesión e ingrese de nuevo eligiéndolo.")


# ---------------------------------------------------------------------------------------------------------------
def ch_admin(d) -> None:
    d.h1("Administration", "Administración")
    d.p(
        "<b>Administration</b> holds the master data SIRAP needs: vehicles, allowlist and restricted lists, owners, checkpoints "
        "and users. Only the <b>Administrator</b> can create or change data here; the <b>Supervisor</b> can view it read-only; the "
        "Operator does not see this menu. Registrations and authorizations keep the user who made them.",
        "<b>Administración</b> reúne los datos maestros que SIRAP necesita: vehículos, listas blanca y restringida, "
        "propietarios, garitas y usuarios. Solo el <b>Administrador</b> puede crear o modificar datos aquí; el <b>Supervisor</b> "
        "puede consultarlos en modo de solo lectura; el Operador no ve este menú. Los registros y las autorizaciones conservan "
        "el usuario que los hizo.",
    )
    d.h2("Vehicles", "Vehículos")
    d.fig("15_admin_vehicles",
          "Vehicles: form on the left, table on the right. Select rows to authorize or remove authorization in bulk.",
          "Vehículos: formulario a la izquierda y tabla a la derecha. Seleccione filas para autorizar o quitar la autorización "
          "de forma masiva.")
    d.steps([
        ("Choose the <b>Country</b> and type the plate (Ecuador: ABC-1234; United States of America: choose the issuing state and the serial).",
         "Elija el <b>País</b> y escriba la placa (Ecuador: ABC-1234; Estados Unidos de América: elija el estado emisor y la matrícula)."),
        ("Fill in make, model, color, type (heavy or light vehicle), owner and transport company. All fields are required.",
         "Complete marca, modelo, color, tipo (pesado o liviano), propietario y transportista. Todos los campos son obligatorios."),
        ("Press <b>Save vehicle</b>. If the plate already exists, SIRAP asks you to confirm the update after you review the changes.",
         "Pulse <b>Guardar vehículo</b>. Si la placa ya existe, SIRAP le pide confirmar la actualización tras revisar los cambios."),
        ("To authorize or revoke several vehicles at once, tick their rows and press <b>Authorize selected</b> or "
         "<b>Remove authorization</b>.",
         "Para autorizar o revocar varios vehículos a la vez, marque sus filas y pulse <b>Autorizar seleccionados</b> o "
         "<b>Quitar autorización</b>."),
    ])
    d.h2("Allowlist and restricted list", "Lista blanca y lista restringida")
    d.fig("16_admin_lists",
          "Lists: assign a plate to the allowlist or to the restricted list with a reason and an expiry date.",
          "Listas: asigne una placa a la lista blanca o a la lista restringida con un motivo y una fecha de vigencia.")
    d.steps([
        ("Open the <b>Lists</b> tab and type the registered plate (the vehicle must exist).",
         "Abra la pestaña <b>Listas</b> y escriba la placa registrada (el vehículo debe existir)."),
        ("Select <b>Allowlist</b> or <b>Restricted list</b>, write the <b>reason</b> and set <b>Valid until</b>.",
         "Seleccione <b>Lista blanca</b> o <b>Lista restringida</b>, escriba el <b>motivo</b> y fije <b>Vigente hasta</b>."),
        ("Press <b>Assign</b>. To withdraw a decision use <b>Remove from lists</b>.",
         "Pulse <b>Asignar</b>. Para retirar una decisión use <b>Quitar de listas</b>."),
    ])
    d.note("danger", ("Security priority", "Prioridad de seguridad"),
           "A current restriction always prevails over an allowlist entry, and an expired entry no longer authorizes. Do not "
           "consider a plate authorized just because it appears in an old list.",
           "Una restricción vigente prevalece siempre sobre una entrada de la lista blanca, y una entrada vencida ya no autoriza. "
           "No considere autorizada una placa solo porque aparece en una lista antigua.")
    d.h2("Owners and checkpoints", "Propietarios y garitas")
    d.p(
        "<b>Owners</b> is a read-only view of the owner and transport company linked to each vehicle; it is not an entry "
        "permission. In <b>Checkpoints</b> the administrator adds a checkpoint (name and location) and activates or deactivates "
        "existing ones with the selection buttons.",
        "<b>Propietarios</b> es una vista de solo lectura del propietario y la compañía de transporte vinculados a cada vehículo; "
        "no es un permiso de ingreso. En <b>Garitas</b> el administrador agrega una garita (nombre y ubicación) y activa o "
        "inactiva las existentes con los botones de selección.",
    )
    d.fig("18_admin_gates",
          "Checkpoints: add a new one or activate and deactivate the selected ones.",
          "Garitas: agregue una nueva o active e inactive las seleccionadas.")
    d.h2("Users", "Usuarios")
    d.fig("20_admin_users",
          "Users: create accounts, edit name and role, reset a password, activate or deactivate. (Names are fictitious.)",
          "Usuarios: cree cuentas, edite nombre y rol, restablezca una contraseña, active o inactive. (Los nombres son ficticios.)")
    d.ul([
        ("Username: 3 to 40 characters (letters, digits, <code>_</code>, <code>.</code>, <code>-</code>). Initial password: at least 8 characters.",
         "Usuario: de 3 a 40 caracteres (letras, dígitos, <code>_</code>, <code>.</code>, <code>-</code>). Contraseña inicial: al menos 8 caracteres."),
        ("Roles: Operator, Supervisor or Administrator (see chapter 2). Users are shared by both countries.",
         "Roles: Operador, Supervisor o Administrador (véase el capítulo 2). Los usuarios son comunes a ambos países."),
        ("The last active administrator cannot be deactivated.", "No se puede inactivar al último administrador activo."),
        ("<b>Edit</b> changes the name and role or resets the password; deactivating an account keeps its history.",
         "<b>Editar</b> cambia el nombre y el rol o restablece la contraseña; inactivar una cuenta conserva su historial."),
    ])
    d.h2("Demo data", "Datos de demostración")
    d.p(
        "<b>Demo data</b> generates simulated operations (origin DEMO) so that the dashboard can be shown or tested, and deletes "
        "them afterwards. They are not real model results and have no operational validity. Generating or deleting them affects "
        "only the DEMO rows of the current country.",
        "<b>Datos demo</b> genera operaciones simuladas (origen DEMO) para poder mostrar o probar el dashboard, y las borra "
        "después. No son resultados reales del modelo y no tienen validez operativa. Generarlas o borrarlas afecta solo a las "
        "filas DEMO del país actual.",
    )
    d.fig("21_admin_demo",
          "Demo data: number of operations to generate and the delete button.",
          "Datos demo: cantidad de operaciones a generar y botón para borrarlas.", narrow=True)


# ---------------------------------------------------------------------------------------------------------------
def ch_model(d) -> None:
    d.h1("About the model", "Acerca del modelo")
    d.p(
        "<b>About the model</b> explains, for transparency, which technology reads the images, with which settings, and what "
        "its limits are. It does not replace the operator's verification of each access.",
        "<b>Acerca del modelo</b> explica, por transparencia, qué tecnología lee las imágenes, con qué parámetros y cuáles son "
        "sus límites. No sustituye la verificación del operador en cada acceso.",
    )
    d.fig("19_about",
          "About the model (Ecuador profile).", "Acerca del modelo (perfil Ecuador).", narrow=True)
    d.table(
        [("Item", "Elemento"), ("Value", "Valor"), ("Meaning", "Significado")],
        [
            [("Detector", "Detector"), ("RT-DETRv2-S on OpenVINO", "RT-DETRv2-S con OpenVINO"),
             ("Finds the plate in the image. The same checkpoint (“shared seed 2”) serves both countries.",
              "Ubica la placa en la imagen. El mismo punto de control («semilla compartida 2») sirve a ambos países.")],
            [("Detector threshold", "Umbral del detector"), ("0.70", "0,70"),
             ("Lower detector confidence goes to manual review.", "Una confianza del detector menor pasa a verificación manual.")],
            [("OCR threshold", "Umbral OCR"), ("94 %", "94 %"),
             ("Minimum probability of <i>every</i> character for an automatic read.", "Probabilidad mínima de <i>cada</i> carácter para una lectura automática.")],
        ],
        caption=("Parameters shown by the screen.", "Parámetros que muestra la pantalla."),
        widths=[22, 28, 50],
    )
    d.h2("Limitations", "Limitaciones")
    d.ul([
        ("The shared detector was trained and checked with United States of America plates. <b>Its performance on Ecuadorian plates has "
         "not been evaluated yet</b>, and changing the OCR rules does not train a model for another country.",
         "El detector compartido fue entrenado y verificado con placas de Estados Unidos de América. <b>Su desempeño con placas de Ecuador "
         "aún no se ha evaluado</b>, y cambiar las reglas del OCR no entrena un modelo para otro país."),
        ("Unknown states, incomplete readings and low confidence require manual review.",
         "Los estados desconocidos, las lecturas incompletas y la confianza baja exigen verificación manual."),
        ("Poor light, glare, dirt, motion blur and small or distant plates reduce accuracy.",
         "La poca luz, los reflejos, la suciedad, el desenfoque por movimiento y las placas pequeñas o lejanas reducen la precisión."),
        ("The software tests verify rules and persistence with a simulated barrier; they do not measure real-world accuracy.",
         "Las pruebas de software verifican reglas y persistencia con una barrera simulada; no miden la precisión en condiciones reales."),
        ("SIRAP is meant for access control, not for indiscriminate surveillance or tracking.",
         "SIRAP está pensado para el control de acceso, no para la vigilancia indiscriminada ni el seguimiento de personas."),
    ])


# ---------------------------------------------------------------------------------------------------------------
def ch_mobile(d) -> None:
    d.h1("Using SIRAP on tablets and phones", "Usar SIRAP en tabletas y teléfonos")
    d.p(
        "SIRAP is a web application: it works in the browser of a computer, a tablet or a phone, with no separate app to "
        "install, as long as the device can reach the server. On small screens the side menu shrinks to icons and the panels "
        "stack in one column, so you scroll down to see the plate, the result and the action buttons.",
        "SIRAP es una aplicación web: funciona en el navegador de una computadora, una tableta o un teléfono, sin instalar una "
        "aplicación aparte, siempre que el dispositivo pueda llegar al servidor. En pantallas pequeñas el menú lateral se reduce "
        "a iconos y los paneles se apilan en una columna, de modo que se desplaza hacia abajo para ver la placa, el resultado y "
        "los botones de acción.",
    )
    d.pair("22_mobile_login", ("Sign-in on a phone.", "Ingreso desde un teléfono."),
           "23_mobile_result", ("Recognition and Access on a phone; the plate panel and the result continue below the image.",
                                "Reconocimiento y Acceso en un teléfono; el panel de la placa y el resultado continúan debajo de la imagen."))
    d.steps([
        ("Open the address of your SIRAP installation in an up-to-date browser and sign in with your own user.",
         "Abra la dirección de su instalación de SIRAP en un navegador actualizado e ingrese con su propio usuario."),
        ("Choose the checkpoint and the movement. Use <b>Upload file</b> to take or select a photo, or <b>Local camera</b> if "
         "the browser offers it (grant the camera permission only to the authorized page).",
         "Elija la garita y el movimiento. Use <b>Subir archivo</b> para tomar o seleccionar una foto, o <b>Cámara local</b> si "
         "el navegador la ofrece (conceda el permiso de cámara solo a la página autorizada)."),
        ("Frame the whole plate, sharp and without glare, then review the plate and the result.",
         "Encuadre la placa completa, nítida y sin reflejos, y revise la placa y el resultado."),
        ("Record only the action that your permissions and procedure allow, and sign out when you finish.",
         "Registre solo la acción que sus permisos y su procedimiento permiten, y cierre sesión al terminar."),
    ])
    d.ul([
        ("Hold the phone upright to operate controls and scroll to the full result before authorizing or rejecting; avoid recording "
         "openings while moving or with an unstable connection. Security and roles are the same as on a computer.",
         "Sostenga el teléfono en vertical para operar los controles y desplácese hasta el resultado completo antes de autorizar o "
         "rechazar; evite registrar aperturas mientras se mueve o con una conexión inestable. La seguridad y los roles son los mismos que en una computadora."),
    ])


# ---------------------------------------------------------------------------------------------------------------
def ch_cases(d) -> None:
    d.h1("Worked examples", "Casos prácticos")
    d.h2("Case A. An authorized truck (Ecuador)", "Caso A. Un camión autorizado (Ecuador)")
    d.steps([
        ("The operator selects <b>Garita 3</b> and <b>Entry</b> and uploads the photo.", "El operador elige <b>Garita 3</b> y <b>Entrada</b> y sube la foto."),
        ("SIRAP reads <b>PBA-8901</b> with 100 % confidence and finds a current allowlist entry: <b>Authorized</b>.",
         "SIRAP lee <b>PBA-8901</b> con 100 % de confianza y encuentra una entrada vigente en la lista blanca: <b>Autorizado</b>."),
        ("The operator checks that the plate matches the truck in front of the gate and presses <b>Register and open gate</b>.",
         "El operador comprueba que la placa coincide con el camión que está frente a la barrera y pulsa <b>Registrar y abrir barrera</b>."),
        ("The confirmation appears and the operation is listed in the History.", "Aparece la confirmación y la operación figura en el Historial."),
    ])
    d.h2("Case B. A truck that is not registered", "Caso B. Un camión sin registro")
    d.steps([
        ("SIRAP reads <b>GSA-1234</b> and answers <b>Not registered</b>; the gate stays closed.",
         "SIRAP lee <b>GSA-1234</b> y responde <b>No registrado</b>; la barrera sigue cerrada."),
        ("The operator asks the supervisor. If the truck must be added, the operator presses <b>Yes, register</b>, fills in the data and "
         "confirms the plate.",
         "El operador consulta al supervisor. Si hay que incorporar el camión, pulsa <b>Sí, registrar</b>, completa los datos y "
         "confirma la placa."),
        ("Registering does not authorize. Only if the procedure allows it, the operator ticks <b>Authorize now</b> (or an "
         "administrator assigns the allowlist later, with reason and expiry).",
         "Registrar no autoriza. Solo si el procedimiento lo permite, el operador marca <b>Autorizar ahora</b> (o un "
         "administrador asigna después la lista blanca, con motivo y vigencia)."),
        ("The decision taken is recorded; nobody assumes that creating the vehicle grants access.",
         "Se registra la decisión tomada; nadie da por hecho que crear el vehículo concede el acceso."),
    ])
    d.h2("Case C. A blurred reading", "Caso C. Una lectura desenfocada")
    d.steps([
        ("The OCR shows doubtful characters or the result is <b>Manual review</b>.",
         "El OCR muestra caracteres dudosos o el resultado es <b>Verificación manual</b>."),
        ("Take a sharper photo, or compare the image with the text.", "Tome una foto más nítida o compare la imagen con el texto."),
        ("If, and only if, you can verify the characters visually, correct the plate and press <b>Verify</b>.",
         "Si, y solo si, puede comprobar los caracteres visualmente, corrija la placa y pulse <b>Verificar</b>."),
        ("Read the new result before any access action. A plate one character away from a registered one is never opened automatically.",
         "Lea el nuevo resultado antes de cualquier acción de acceso. Una placa a un carácter de distancia de una registrada nunca se abre automáticamente."),
    ])
    d.h2("Case D. A United States of America truck", "Caso D. Un camión de Estados Unidos de América")
    d.steps([
        ("Sign in choosing <b>USA</b>. Upload a video (or use a camera) where the plate is visible.",
         "Ingrese eligiendo <b>USA</b>. Suba un video (o use una cámara) donde se vea la placa."),
        ("SIRAP reads the serial <b>KDM4827</b> and the state <b>TX</b> from the plate itself. The counter shows <b>1/2</b>; the "
         "result stays on manual review.",
         "SIRAP lee la matrícula <b>KDM4827</b> y el estado <b>TX</b> de la propia placa. El contador muestra <b>1/2</b>; el "
         "resultado sigue en verificación manual."),
        ("A second, distinct frame confirms the same state and serial (<b>2/2</b>): the plate is on the allowlist and the result "
         "becomes <b>Authorized</b>.",
         "Un segundo cuadro distinto confirma el mismo estado y matrícula (<b>2/2</b>): la placa está en la lista blanca y el "
         "resultado pasa a <b>Autorizado</b>."),
        ("If the operator wants to compare the vehicle with its public description, they press <b>See Vehicle Details on J.D. "
         "Power</b>: the report opens in a new tab and the SIRAP screen stays as it was.",
         "Si el operador quiere comparar el vehículo con su descripción pública, pulsa <b>Ver detalles del vehículo en J.D. "
         "Power</b>: el informe se abre en una pestaña nueva y la pantalla de SIRAP queda como estaba."),
        ("The operator presses <b>Register and open gate</b> within the confirmation window (30 seconds).",
         "El operador pulsa <b>Registrar y abrir barrera</b> dentro de la ventana de confirmación (30 segundos)."),
    ])
    d.h2("Case E. Consulting the History from a phone", "Caso E. Consultar el Historial desde el teléfono")
    d.steps([
        ("Sign in on the phone, open <b>History</b>, set a short date range and search by plate.",
         "Ingrese desde el teléfono, abra <b>Historial</b>, defina un intervalo breve y busque por placa."),
        ("Check result, checkpoint and time. Supervisors and administrators can export the CSV.",
         "Revise resultado, garita y hora. Supervisores y administradores pueden exportar el CSV."),
    ])


# ---------------------------------------------------------------------------------------------------------------
def ch_trouble(d) -> None:
    d.h1("Troubleshooting and frequently asked questions", "Solución de problemas y preguntas frecuentes")
    d.h2("Common situations", "Situaciones frecuentes")
    d.table(
        [("Situation", "Situación"), ("What to check", "Qué revisar")],
        [
            [("I cannot sign in", "No puedo ingresar"),
             ("Check user, password and the connection; make sure you chose the right country. Contact your administrator.",
              "Compruebe usuario, contraseña y conexión; verifique que eligió el país correcto. Contacte al administrador.")],
            [("The photo does not load", "La foto no carga"),
             ("Use JPG, JPEG, PNG or WEBP, at most 10 MB, with the shortest side of at least 160 px.",
              "Use JPG, JPEG, PNG o WEBP, de máximo 10 MB, con el lado más corto de al menos 160 px.")],
            [("The plate is not recognized", "No reconoce la placa"),
             ("Improve light and focus, avoid glare, and capture again with the whole plate in view.",
              "Mejore la luz y el enfoque, evite reflejos y capture de nuevo con toda la placa a la vista.")],
            [("The result is Manual review", "El resultado es Verificación manual"),
             ("Compare the characters, correct only what you can verify, and read the reason shown. United States of America: state or serial not "
              "confirmed, or fewer than two confirmed frames.",
              "Compare los caracteres, corrija solo lo que pueda comprobar y lea el motivo que se muestra. Estados Unidos de América: estado o "
              "matrícula sin confirmar, o menos de dos cuadros confirmados.")],
            [("The local camera does not work", "No funciona la cámara local"),
             ("Check the browser permission, whether another app is using the camera, and the connection.",
              "Revise el permiso del navegador, si otra aplicación usa la cámara y la conexión.")],
            [("The camera URL does not play", "La cámara por URL no reproduce"),
             ("Check the signal type, HTTPS access and browser compatibility. RTSP streams need a web bridge.",
              "Revise el tipo de señal, el acceso HTTPS y la compatibilidad con el navegador. Las señales RTSP requieren un puente web.")],
            [("I cannot find an operation in History", "No encuentro una operación en el Historial"),
             ("Widen the dates, clear filters, and remember that only recorded actions appear, not mere readings.",
              "Amplíe las fechas, quite filtros y recuerde que solo aparecen acciones registradas, no simples lecturas.")],
            [("There is no Export CSV button", "No aparece Exportar CSV"),
             ("It is only available to Supervisor and Administrator.", "Solo está disponible para Supervisor y Administrador.")],
            [("The barrier does not move", "La barrera no se mueve"),
             ("The default barrier is simulated. Do not repeat the opening; check the History and the barrier state first.",
              "La barrera por defecto es simulada. No repita la apertura; revise primero el Historial y el estado de la barrera.")],
            [("The Dashboard looks empty", "El Dashboard aparece vacío"),
             ("Check the period and the “Include demo operations” box.", "Revise el periodo y la casilla «Incluir operaciones de demostración».")],
            [("Vehicle details are missing (Ecuador)", "Faltan los detalles del vehículo (Ecuador)"),
             ("The SRI did not answer; the panel says so and shows local values. This does not change the access decision.",
              "El SRI no respondió; el panel lo indica y muestra valores locales. Esto no cambia la decisión de acceso.")],
            [("The J.D. Power button is missing (United States of America)", "Falta el botón de J.D. Power (Estados Unidos de América)"),
             ("The button needs a plate with a valid format and an issuing state. Type or correct the plate and choose the state "
              "in the boxes. If the J.D. Power page does not show the vehicle, rely on what you see and on the registry: this does "
              "not change the access decision.",
              "El botón necesita una placa con formato válido y un estado emisor. Escriba o corrija la placa y elija el estado en "
              "las casillas. Si la página de J.D. Power no muestra el vehículo, guíese por lo que ve y por el registro: esto no "
              "cambia la decisión de acceso.")],
            [("SIRAP or the connection is unavailable", "SIRAP o la conexión no están disponibles"),
             ("Keep the barrier closed and follow the authorized contingency procedure. Write down date and time, checkpoint, plate, "
              "reason and person in charge. When the service returns, check the History to avoid duplicates.",
              "Mantenga cerrada la barrera y siga el procedimiento de contingencia autorizado. Anote fecha y hora, garita, placa, "
              "motivo y responsable. Al restablecerse el servicio, revise el Historial para evitar duplicados.")],
        ],
        caption=("Troubleshooting guide.", "Guía de solución de problemas."),
        widths=[30, 70],
    )
    d.h2("Frequently asked questions", "Preguntas frecuentes")
    d.h3("Is a recognized plate authorized?", "¿Una placa reconocida queda autorizada?")
    d.p("No. Recognition only proposes a plate. Authorization comes from the current lists, and the operator must verify the result.",
        "No. El reconocimiento solo propone una placa. La autorización proviene de las listas vigentes y el operador debe verificar el resultado.")
    d.h3("Does the barrier open automatically?", "¿La barrera se abre automáticamente?")
    d.p("No. The operator starts the action and the server validates the authorization again. In the default configuration the "
        "barrier is simulated; a real controller needs the HTTP barrier mode, an HTTPS address and an access token configured by the administrator.",
        "No. El operador inicia la acción y el servidor vuelve a validar la autorización. En la configuración por defecto la "
        "barrera es simulada; un controlador real requiere el modo de barrera HTTP, una dirección HTTPS y un token de acceso configurados por el administrador.")
    d.h3("Does registering a new truck authorize it?", "¿Registrar un camión nuevo lo autoriza?")
    d.p("Not by itself. The truck is saved without a permit unless the person registering expressly ticks <b>Authorize now</b> "
        "after confirming the plate. An existing or restricted plate can never be overwritten from that form.",
        "No por sí solo. El camión se guarda sin permiso, salvo que quien lo registra marque expresamente <b>Autorizar ahora</b> "
        "tras confirmar la placa. Una placa existente o restringida nunca puede sobrescribirse desde ese formulario.")
    d.h3("Does SIRAP keep the images and videos?", "¿SIRAP conserva las imágenes y los videos?")
    d.p("They are processed to recognize the plate and are not kept as permanent files. What is kept is the recorded operation "
        "(plate, result, action, operator, time).",
        "Se procesan para reconocer la placa y no se conservan como archivos permanentes. Lo que se conserva es la operación "
        "registrada (placa, resultado, acción, operador, hora).")
    d.h3("What happens if saving fails during an opening?", "¿Qué pasa si falla el guardado durante una apertura?")
    d.p("The request must be saved before the order is sent; if it cannot be saved, the opening is blocked. If the final result "
        "cannot be saved afterwards, the state stays <i>requested</i> and needs a manual check. See chapter 7.",
        "La solicitud debe guardarse antes de enviar la orden; si no puede guardarse, la apertura se bloquea. Si después no puede "
        "guardarse el resultado final, el estado queda <i>solicitada</i> y requiere una comprobación manual. Véase el capítulo 7.")
    d.h3("Can I use SIRAP for both countries?", "¿Puedo usar SIRAP para los dos países?")
    d.p("Yes. You choose the country at sign-in; lists, history and indicators are separate for each. The same user account works in both.",
        "Sí. Elige el país al ingresar; las listas, el historial y los indicadores son independientes para cada uno. La misma cuenta "
        "de usuario sirve en ambos.")


# ---------------------------------------------------------------------------------------------------------------
def ch_checklist(d) -> None:
    d.h1("Operator checklist", "Lista de comprobación del operador")
    d.p("Use it at the start of the shift and for every access.", "Úsela al comenzar el turno y en cada acceso.")
    d.checklist([
        ("Correct country, checkpoint and operation (<b>Entry</b> or <b>Exit</b>).",
         "País, garita y operación (<b>Entrada</b> o <b>Salida</b>) correctos."),
        ("Image or video visible and the whole plate legible.", "Imagen o video visible y placa completa legible."),
        ("The plate read by the OCR matches the vehicle in front of the gate (United States of America: state and serial both match).",
         "La placa leída por el OCR coincide con el vehículo frente a la barrera (Estados Unidos de América: coinciden estado y matrícula)."),
        ("Result and validity of the authorization reviewed.", "Resultado y vigencia de la autorización revisados."),
        ("Action chosen according to the procedure; the barrier is opened only for an <b>Authorized</b> result.",
         "Acción elegida según el procedimiento; la barrera se abre solo con un resultado <b>Autorizado</b>."),
        ("Contingency opening has a clear reason and a person in charge.", "La apertura de contingencia tiene un motivo claro y un responsable."),
        ("Confirmation message read; the operation is visible in the History.", "Mensaje de confirmación leído; la operación es visible en el Historial."),
        ("Uncertain results checked (<b>Operation awaiting confirmation</b>) without repeating the opening.",
         "Resultados inciertos revisados (<b>Operación pendiente de confirmar</b>) sin repetir la apertura."),
        ("Session closed at the end, especially on shared or mobile devices.", "Sesión cerrada al terminar, sobre todo en dispositivos compartidos o móviles."),
    ])


# ---------------------------------------------------------------------------------------------------------------
def appendix_glossary(d) -> None:
    d.h1_plain("Appendix A. Glossary", "Apéndice A. Glosario")
    d.table(
        [("Term", "Término"), ("Plain explanation", "Explicación sencilla")],
        [
            [("ALPR / OCR", "ALPR / OCR"), ("Technology that finds a plate and reads its letters and digits.", "Tecnología que ubica una placa y lee sus letras y dígitos.")],
            [("RT-DETRv2-S", "RT-DETRv2-S"), ("The detector that locates the plate in the image; it runs with OpenVINO Runtime.", "El detector que ubica la placa en la imagen; se ejecuta con OpenVINO Runtime.")],
            [("Garita / Checkpoint", "Garita / Punto de control"), ("A gate or access post where vehicles are checked.", "Una barrera o puesto de acceso donde se controlan los vehículos.")],
            [("Allowlist (lista blanca)", "Lista blanca"), ("Plates with a current authorization.", "Placas con una autorización vigente.")],
            [("Restricted list", "Lista restringida"), ("Plates that must be denied while the restriction is in force.", "Placas que deben denegarse mientras la restricción esté vigente.")],
            [("Read plate / Final plate", "Placa leída / Placa final"), ("The text proposed by the OCR / the text confirmed before recording.", "El texto propuesto por el OCR / el texto confirmado antes de registrar.")],
            [("Confidence", "Confianza"), ("How sure a prediction is; it is not a permission to enter.", "Qué tan segura es una predicción; no es un permiso de ingreso.")],
            [("Issuing state", "Estado emisor"), ("United States of America: the state that issued the plate. It is read from the plate, never guessed.", "Estados Unidos de América: el estado que emitió la placa. Se lee de la propia placa, nunca se supone.")],
            [("Serial", "Matrícula (serial)"), ("The letters and digits of the plate itself.", "Las letras y dígitos de la placa en sí.")],
            [("Confirmation frames", "Cuadros de confirmación"), ("United States of America: two distinct frames confirmed by the server before a normal opening.", "Estados Unidos de América: dos cuadros distintos confirmados por el servidor antes de una apertura normal.")],
            [("SRI", "SRI"), ("Ecuador's tax service; source of public vehicle data.", "Servicio de Rentas Internas de Ecuador; fuente de datos públicos de vehículos.")],
            [("J.D. Power", "J.D. Power"), ("Company whose public license-plate report opens from the <b>See Vehicle Details on J.D. Power</b> button for United States of America plates. SIRAP does not copy its data.", "Empresa cuyo informe público de placas se abre desde el botón <b>Ver detalles del vehículo en J.D. Power</b> para placas de Estados Unidos de América. SIRAP no copia sus datos.")],
            [("DEMO", "DEMO"), ("Simulated operation used for tests and training.", "Operación simulada utilizada para pruebas y capacitación.")],
            [("CSV", "CSV"), ("Table format that opens in a spreadsheet.", "Formato de tabla que se abre en una hoja de cálculo.")],
            [("Idempotency", "Idempotencia"), ("Sending the same operation twice never opens the barrier twice.", "Enviar dos veces la misma operación nunca abre la barrera dos veces.")],
        ],
        widths=[28, 72],
    )


def appendix_reference(d) -> None:
    d.h1_plain("Appendix B. Quick reference", "Apéndice B. Referencia rápida")
    d.table(
        [("Result", "Resultado"), ("Meaning", "Significado"), ("Allowed action", "Acción permitida")],
        [
            [("Authorized", "Autorizado"), ("Valid plate, current allowlist entry, readings confirmed.", "Placa válida, entrada vigente en lista blanca, lecturas confirmadas."),
             ("Register and open gate", "Registrar y abrir barrera")],
            [("Denied", "Denegado"), ("The plate is on the restricted list.", "La placa está en la lista restringida."),
             ("Record rejection", "Registrar rechazo")],
            [("Not registered", "No registrado"), ("The plate has no record.", "La placa no tiene registro."),
             ("Record without opening, or register a new truck", "Registrar sin abrir, o registrar un camión nuevo")],
            [("No authorization", "Sin autorización"), ("Registered, but without a current allowlist entry.", "Registrada, pero sin una entrada vigente en la lista blanca."),
             ("Record without opening", "Registrar sin abrir")],
            [("Manual review", "Verificación manual"), ("Invalid plate, low confidence, a plate one character away from a registered one, or (US) state/serial not confirmed.",
                                                       "Placa inválida, confianza baja, una placa a un carácter de una registrada o (EE. UU.) estado/matrícula sin confirmar."),
             ("Correct and Verify, capture again, or record without opening", "Corregir y Verificar, capturar de nuevo o registrar sin abrir")],
        ],
        caption=("Access results and the action each allows.", "Resultados de acceso y la acción que permite cada uno."),
        widths=[20, 48, 32],
    )
    d.table(
        [("Item", "Elemento"), ("Ecuador", "Ecuador"), ("United States of America", "Estados Unidos de América")],
        [
            [("Plate identity", "Identidad de la placa"), ("3 letters + 3 or 4 digits (ABC-1234).", "3 letras + 3 o 4 dígitos (ABC-1234)."),
             ("Issuing state + serial (TX KDM4827), read from the plate.", "Estado emisor + matrícula (TX KDM4827), leídos de la placa.")],
            [("Normal opening requires", "La apertura normal requiere"), ("Current allowlist entry and a confident reading.", "Entrada vigente en lista blanca y una lectura segura."),
             ("Current allowlist entry and two distinct confirmed frames within 7.5 s.", "Entrada vigente en lista blanca y dos cuadros distintos confirmados en 7,5 s.")],
            [("Vehicle data", "Datos del vehículo"), ("SRI + local registry.", "SRI + registro local."), ("Button to the J.D. Power report + local registry.", "Botón al informe de J.D. Power + registro local.")],
            [("Detector / OCR thresholds", "Umbrales detector / OCR"), ("0.70 / 94 %", "0,70 / 94 %"), ("0.70 / 94 %", "0,70 / 94 %")],
            [("Image limits", "Límites de imagen"), ("JPG, JPEG, PNG, WEBP · 10 MB · shortest side ≥ 160 px", "JPG, JPEG, PNG, WEBP · 10 MB · lado menor ≥ 160 px"),
             ("Same", "Igual")],
            [("Session", "Sesión"), ("12 hours by default", "12 horas por defecto"), ("Same", "Igual")],
        ],
        caption=("Differences between the two profiles.", "Diferencias entre los dos perfiles."),
        widths=[24, 38, 38],
    )
    d.p(
        "If this manual differs from the deployed application, the configuration verified by your system administrator prevails. "
        "Source code and technical documentation: github.com/eduardoceballos666/SIRAP_USA_ECUADOR (Apache License 2.0; third-party models and assets keep their own licenses).",
        "Si este manual difiere de la aplicación desplegada, prevalece la configuración vigente verificada por el administrador "
        "del sistema. Código fuente y documentación técnica: github.com/eduardoceballos666/SIRAP_USA_ECUADOR (Licencia Apache 2.0; los modelos y recursos de terceros conservan sus propias licencias).",
    )
