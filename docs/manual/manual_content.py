"""Bilingual text of the SIRAP user manual, part 1: introduction, sign-in, the main screen, capture, Ecuador, United States.

Every string is an (English, Spanish) pair. Inline HTML (<b>, <code>) is allowed; use &amp; for ampersands.
"""
from __future__ import annotations

import manual_content2


def build(d) -> None:
    preface(d)
    ch_about(d)
    ch_signin(d)
    ch_screen(d)
    ch_capture(d)
    ch_ecuador(d)
    ch_usa(d)
    manual_content2.build(d)


# ---------------------------------------------------------------------------------------------------------------
def preface(d) -> None:
    d.h1_plain("How to use this manual", "Cómo utilizar este manual")
    d.p(
        "This manual describes every screen of SIRAP for both country profiles, explains what each control does and walks "
        "through the procedures from start to finish. If you are new, read chapters 1 to 5 (or 1 to 4 and 6 for the United "
        "States) and the operator checklist in chapter 15; the rest is reference material.",
        "Este manual describe cada pantalla de SIRAP para los dos perfiles de país, explica qué hace cada control y recorre "
        "los procedimientos de principio a fin. Si es la primera vez, lea los capítulos 1 a 5 (o 1 a 4 y 6 para Estados "
        "Unidos) y la lista de comprobación del operador del capítulo 15; el resto es material de consulta.",
    )
    d.h2("Quick route: record an entry", "Ruta rápida: registrar una entrada")
    d.steps([
        ("Sign in, choosing your language and the country (Ecuador or United States).",
         "Ingrese eligiendo su idioma y el país (Ecuador o Estados Unidos)."),
        ("Choose the checkpoint and set the operation to <b>Entry</b>.",
         "Elija la garita y deje la operación en <b>Entrada</b>."),
        ("Upload a photo or video, or use a camera.", "Suba una foto o un video, o use una cámara."),
        ("Read the identified plate and the access result. If the plate is wrong, correct it and press <b>Verify</b>.",
         "Revise la placa identificada y el resultado de acceso. Si la placa es incorrecta, corríjala y pulse <b>Verificar</b>."),
        ("Do only the action the screen allows and your procedure permits, then check the confirmation message.",
         "Realice solo la acción que la pantalla habilita y que su procedimiento permite, y compruebe el mensaje de confirmación."),
        ("Open <b>History</b> to confirm that the operation was recorded.",
         "Abra <b>Historial</b> para confirmar que la operación quedó registrada."),
    ])
    d.note("danger", ("Fundamental rule", "Regla fundamental"),
           "A recognized plate is not an authorization. SIRAP checks the current lists, and the operator must verify the result "
           "before acting. The barrier never opens by itself.",
           "Una placa reconocida no es una autorización. SIRAP consulta las listas vigentes y el operador debe verificar el "
           "resultado antes de actuar. La barrera nunca se abre sola.")
    d.h2("About the screenshots", "Sobre las capturas de pantalla")
    d.p(
        "All screenshots were taken from a test installation of SIRAP with <b>demonstration data</b>: sample photographs, "
        "fictitious plates, companies and users, and generated DEMO operations. Plate reading, decision rules and screens are "
        "the real ones. Two things are illustrative only: the vehicle-data lookups (SRI and J.D. Power) were replaced by "
        "fixed example values, and the United States video is a composite built from sample photographs with a Texas plate "
        "image added. None of it represents a real operation or a real vehicle.",
        "Todas las capturas provienen de una instalación de prueba de SIRAP con <b>datos de demostración</b>: fotografías de "
        "ejemplo, placas, empresas y usuarios ficticios, y operaciones DEMO generadas. La lectura de placas, las reglas de "
        "decisión y las pantallas son las reales. Solo dos cosas son ilustrativas: las consultas de datos del vehículo (SRI y "
        "J.D. Power) se sustituyeron por valores de ejemplo fijos, y el video de Estados Unidos es un montaje hecho con "
        "fotografías de ejemplo a las que se añadió la imagen de una placa de Texas. Nada de esto representa una operación "
        "ni un vehículo reales.",
    )
    d.p(
        "If this guide differs from the deployed application, the configuration verified by your system administrator prevails.",
        "Si esta guía difiere de la aplicación desplegada, prevalece la configuración vigente verificada por el administrador "
        "del sistema.",
    )


# ---------------------------------------------------------------------------------------------------------------
def ch_about(d) -> None:
    d.h1("What SIRAP does", "Qué es y qué hace SIRAP")
    d.p(
        "SIRAP is a web application that helps a vehicle checkpoint (<i>garita</i>) identify license plates in photos, video "
        "frames or camera images, check them against the access lists and keep a record of every decision. It has two "
        "country profiles, <b>Ecuador</b> and the <b>United States</b>. They share the same screens, the same plate detector "
        "and the same OCR engine, but they interpret the plate and apply the access rules differently.",
        "SIRAP es una aplicación web que ayuda a una garita vehicular a identificar placas en fotos, fotogramas de video o "
        "imágenes de cámara, compararlas con las listas de acceso y dejar constancia de cada decisión. Tiene dos perfiles de "
        "país, <b>Ecuador</b> y <b>Estados Unidos</b>. Comparten las mismas pantallas, el mismo detector de placas y el "
        "mismo motor OCR, pero interpretan la placa y aplican las reglas de acceso de forma distinta.",
    )
    d.h2("What it does", "Qué hace")
    d.ul([
        ("<b>Detects</b> the plate in the image with an RT-DETRv2-S detector running on OpenVINO Runtime (minimum detector "
         "confidence 0.70).",
         "<b>Detecta</b> la placa en la imagen con un detector RT-DETRv2-S ejecutado con OpenVINO Runtime (confianza mínima "
         "del detector: 0,70)."),
        ("<b>Reads</b> its characters with a global OCR model (<code>fast-plate-ocr</code>, <code>cct-s-v2-global-model</code>). "
         "A reading is accepted automatically only when the <i>lowest</i> per-character probability is at least 0.94.",
         "<b>Lee</b> sus caracteres con un modelo OCR global (<code>fast-plate-ocr</code>, <code>cct-s-v2-global-model</code>). "
         "Una lectura se acepta automáticamente solo si la probabilidad <i>mínima</i> por carácter es de al menos 0,94."),
        ("<b>Checks</b> the plate in the country's registry and applies the allowlist and restricted-list rules.",
         "<b>Consulta</b> la placa en el registro del país y aplica las reglas de lista blanca y lista restringida."),
        ("<b>Shows vehicle details</b> next to the registry data (Ecuador: SRI; United States: J.D. Power).",
         "<b>Muestra los datos del vehículo</b> junto a los del registro (Ecuador: SRI; Estados Unidos: J.D. Power)."),
        ("<b>Records the operator's action</b>: open the barrier, reject, record without opening, or open manually "
         "for a contingency with a written reason.",
         "<b>Registra la acción del operador</b>: abrir la barrera, rechazar, registrar sin abrir o abrir manualmente por "
         "contingencia con un motivo escrito."),
        ("<b>Keeps the history</b> with filters, CSV export and a dashboard, and offers administration of vehicles, lists, "
         "checkpoints and users.",
         "<b>Conserva el historial</b> con filtros, exportación a CSV y un dashboard, y ofrece la administración de "
         "vehículos, listas, garitas y usuarios."),
        ("Works in <b>six languages</b> (English, Spanish, Portuguese, French, German, Italian), in light or dark mode, on "
         "computers, tablets and phones.",
         "Funciona en <b>seis idiomas</b> (inglés, español, portugués, francés, alemán, italiano), en modo claro u oscuro, "
         "en computadoras, tabletas y teléfonos."),
    ])
    d.h2("Ecuador and the United States at a glance", "Ecuador y Estados Unidos de un vistazo")
    d.table(
        [("Topic", "Tema"), "Ecuador", ("United States", "Estados Unidos")],
        [
            [("Plate identity", "Identidad de la placa"),
             ("The plate itself, written <code>ABC-1234</code> (3 letters + 3 or 4 digits).",
              "La placa misma, escrita <code>ABC-1234</code> (3 letras + 3 o 4 dígitos)."),
             ("Issuing state + serial, for example <b>TX · BM5T299</b> (stored as <code>US:TX:BM5T299</code>).",
              "Estado emisor + matrícula, por ejemplo <b>TX · BM5T299</b> (se guarda como <code>US:TX:BM5T299</code>).")],
            [("Issuing state", "Estado emisor"),
             ("Not used.", "No se usa."),
             ("Read from the state band of the plate. It is never guessed from the location or the design; if it cannot be "
              "read the operator chooses it and the result stays in manual review.",
              "Se lee en la franja del estado de la placa. Nunca se deduce de la ubicación ni del diseño; si no puede leerse, "
              "el operador lo elige y el resultado queda en verificación manual.")],
            [("Near matches", "Coincidencias cercanas"),
             ("A reading that differs by one character from a registered plate goes to manual verification (“Did you mean …?”).",
              "Una lectura que difiere en un carácter de una placa registrada pasa a verificación manual («¿Quiso decir …?»)."),
             ("Exact match only: state and serial must both match.",
              "Solo coincidencia exacta: deben coincidir el estado y la matrícula.")],
            [("Normal opening requires", "La apertura normal exige"),
             ("A current allowlist entry, OCR ≥ 94 % and the operator's confirmation.",
              "Una entrada vigente en la lista blanca, OCR ≥ 94 % y la confirmación del operador."),
             ("A current allowlist entry, detector ≥ 0.70, OCR ≥ 94 %, and the same plate confirmed in <b>two distinct frames</b> "
              "by the server within 7.5 seconds.",
              "Una entrada vigente en la lista blanca, detector ≥ 0,70, OCR ≥ 94 % y la misma placa confirmada en "
              "<b>dos cuadros distintos</b> por el servidor en 7,5 segundos.")],
            [("Vehicle data", "Datos del vehículo"),
             ("Servicio de Rentas Internas (SRI) plus the local registry.", "Servicio de Rentas Internas (SRI) más el registro local."),
             ("J.D. Power plate lookup plus the local U.S. registry.", "Consulta de placas de J.D. Power más el registro local de EE. UU.")],
            [("Registry, lists, history", "Registro, listas, historial"),
             ("Separate for each country.", "Separados por país."), ("Separate for each country.", "Separados por país.")],
        ],
        caption=("Differences between the two country profiles. Screens, roles, detector, OCR and thresholds are shared.",
                 "Diferencias entre los dos perfiles de país. Las pantallas, los roles, el detector, el OCR y los umbrales son compartidos."),
        widths=[19, 41, 40],
    )
    d.h2("How a reading is processed", "Cómo se procesa una lectura")
    d.table(
        [("Stage", "Etapa"), ("What happens", "Qué sucede"), ("Who", "Responsable")],
        [
            [("1. Capture", "1. Captura"), ("An image, video or camera frame is obtained.", "Se obtiene una imagen, video o fotograma de cámara."),
             ("Operator / device", "Operador / dispositivo")],
            [("2. Identification", "2. Identificación"), ("The detector finds the plate and the OCR proposes its characters (and, in the United States, the state).",
                                                         "El detector ubica la placa y el OCR propone sus caracteres (y, en Estados Unidos, el estado)."),
             ("AI model", "Modelo de IA")],
            [("3. Verification", "3. Verificación"), ("The registry and the current lists are checked; the access rules produce a result.",
                                                     "Se consultan el registro y las listas vigentes; las reglas de acceso producen un resultado."),
             "SIRAP"],
            [("4. Decision", "4. Decisión"), ("The operator confirms, corrects, rejects or asks for manual validation.",
                                             "El operador confirma, corrige, rechaza o solicita validación manual."),
             ("Operator", "Operador")],
            [("5. Record", "5. Registro"), ("The action is stored in the history before any barrier order is sent.",
                                           "La acción se guarda en el historial antes de enviar cualquier orden a la barrera."),
             ("Application", "Aplicación")],
        ],
        caption=("Stages of recognition and access control.", "Etapas del reconocimiento y del control de acceso."),
        widths=[20, 56, 24],
    )
    d.h2("What you need", "Qué necesita")
    d.ul([
        ("A modern browser (Chrome, Edge, Firefox or Safari) with access to the application address.",
         "Un navegador moderno (Chrome, Edge, Firefox o Safari) con acceso a la dirección de la aplicación."),
        ("A username and password enabled by the administrator.", "Un usuario y una contraseña habilitados por el administrador."),
        ("A sharp image or an available camera, depending on how you capture.",
         "Una imagen nítida o una cámara disponible, según el método de captura."),
        ("Permissions and connectivity to use a camera or stream video.",
         "Permisos y conectividad para usar una cámara o transmitir video."),
    ])
    d.note("warn", ("Demonstration mode", "Modo de demostración"),
           "The barrier configured in the published version is <b>simulated</b>: recording an opening does not move a physical "
           "device. A real barrier needs an HTTPS controller and a token and must be tested and authorized separately. Sample "
           "images and DEMO data are for learning only and are not evidence of a real operation.",
           "La barrera configurada en la versión publicada es <b>simulada</b>: registrar una apertura no mueve ningún "
           "dispositivo físico. Una barrera real requiere un controlador HTTPS y un token, y debe probarse y autorizarse por "
           "separado. Las imágenes de ejemplo y los datos DEMO sirven solo para aprender y no son evidencia de una operación real.")


# ---------------------------------------------------------------------------------------------------------------
def ch_signin(d) -> None:
    d.h1("Signing in and getting around", "Ingreso y navegación")
    d.h2("Sign in", "Iniciar sesión")
    d.steps([
        ("Open the SIRAP address in your browser.", "Abra la dirección de SIRAP en su navegador."),
        ("Choose the interface <b>Language</b> and the <b>Country</b>: Ecuador or United States.",
         "Elija el <b>Idioma</b> de la interfaz y el <b>País</b>: Ecuador o Estados Unidos."),
        ("Type your <b>Username</b> and <b>Password</b>.", "Escriba su <b>Usuario</b> y su <b>Contraseña</b>."),
        ("Press <b>Sign in</b>. You arrive at <b>Recognition and Access</b>.",
         "Pulse <b>Ingresar</b>. Llegará a <b>Reconocimiento y Acceso</b>."),
    ])
    d.fig("01_login", "Sign-in screen with language and country selectors.",
          "Pantalla de inicio de sesión con los selectores de idioma y país.", narrow=True)
    d.note("info", ("Country and session", "País y sesión"),
           "The country you choose is attached to your session: recognition, registry, lists, history, dashboard and demo data "
           "all belong to that country. To work in the other country, sign out and sign in again. Users and checkpoints are "
           "shared by both countries. Sessions last 12 hours by default; sign out when you leave the computer unattended.",
           "El país que elige queda asociado a su sesión: el reconocimiento, el registro, las listas, el historial, el "
           "dashboard y los datos de demostración pertenecen a ese país. Para trabajar en el otro país, cierre sesión e "
           "ingrese de nuevo. Los usuarios y las garitas son comunes a ambos países. Las sesiones duran 12 horas de forma "
           "predeterminada; cierre sesión cuando deje el equipo sin supervisión.")
    d.h2("Roles", "Roles")
    d.table(
        [("Role", "Rol"), ("Menu", "Menú"), ("What it can do", "Qué puede hacer")],
        [
            [("Operator", "Operador"), ("Recognition and Access, History, Dashboard", "Reconocimiento y Acceso, Historial, Dashboard"),
             ("Captures and verifies plates, records actions, and can register a <b>new</b> truck and — after visually confirming "
              "the plate — expressly authorize it. Cannot change existing records.",
              "Captura y verifica placas, registra acciones y puede registrar un camión <b>nuevo</b> y, tras confirmar "
              "visualmente la placa, autorizarlo expresamente. No puede modificar registros existentes.")],
            [("Supervisor", "Supervisor"), ("Operator menu + Administration (read-only)", "Menú del operador + Administración (solo lectura)"),
             ("Everything an operator does, plus <b>CSV export</b> of the history. Can view the administration data without editing it.",
              "Todo lo del operador, además de la <b>exportación a CSV</b> del historial. Puede ver los datos de administración sin editarlos.")],
            [("Administrator", "Administrador"), ("All screens", "Todas las pantallas"),
             ("Everything above, plus creating and updating vehicles, lists, checkpoints and users, and generating or deleting demo data.",
              "Todo lo anterior, además de crear y actualizar vehículos, listas, garitas y usuarios, y generar o borrar datos de demostración.")],
        ],
        caption=("User roles and available functions.", "Roles de usuario y funciones disponibles."),
        widths=[16, 30, 54],
    )
    d.note("warn", ("Existing plates are protected", "Las placas existentes están protegidas"),
           "From Recognition and Access nobody can overwrite an existing plate, especially one on the restricted list. Only the "
           "Administrator changes existing data, from Administration. Do not use another person's credentials.",
           "Desde Reconocimiento y Acceso nadie puede sobrescribir una placa existente, en especial una de la lista "
           "restringida. Solo el Administrador cambia datos existentes, desde Administración. No use las credenciales de otra persona.")
    d.h2("Language and appearance", "Idioma y apariencia")
    d.p(
        "SIRAP is available in <b>English</b> (default), <b>Español</b>, <b>Português</b>, <b>Français</b>, <b>Deutsch</b> and "
        "<b>Italiano</b>. Choose the language at sign-in or with the <b>Language</b> selector at the top of the left menu; the "
        "choice is remembered in that browser. At the bottom of the menu you will find <b>About the model</b>, your name and "
        "role, a <b>light/dark</b> switch (moon icon) and the <b>sign-out</b> button.",
        "SIRAP está disponible en <b>inglés</b> (predeterminado), <b>español</b>, <b>portugués</b>, <b>francés</b>, "
        "<b>alemán</b> e <b>italiano</b>. Elija el idioma al ingresar o con el selector <b>Idioma</b> de la parte superior "
        "del menú izquierdo; la elección se recuerda en ese navegador. Al final del menú están <b>Acerca del modelo</b>, su "
        "nombre y rol, el interruptor de modo <b>claro/oscuro</b> (icono de luna) y el botón para <b>cerrar sesión</b>.",
    )


# ---------------------------------------------------------------------------------------------------------------
def ch_screen(d) -> None:
    d.h1("The Recognition and Access screen", "La pantalla Reconocimiento y Acceso")
    d.p(
        "This is the screen the checkpoint uses for every entry or exit. It gathers the context, the capture source, the "
        "identified plate, the access result and the available actions in one view.",
        "Es la pantalla que usa la garita en cada entrada o salida. Reúne en una sola vista el contexto, la fuente de captura, "
        "la placa identificada, el resultado de acceso y las acciones disponibles.",
    )
    d.fig("02_recognition", "Recognition and Access, before any image is loaded (Ecuador profile).",
          "Reconocimiento y Acceso antes de cargar una imagen (perfil Ecuador).")
    d.table(
        [("Zone", "Zona"), ("What it is for", "Para qué sirve")],
        [
            [("Control bar (top)", "Barra de control (arriba)"),
             ("Shows the country and operator, and lets you choose the <b>Checkpoint</b> and the <b>Operation</b> (Entry or Exit). "
              "Also the <b>Help</b> button and the date and time.",
              "Muestra el país y el operador, y permite elegir la <b>Garita</b> y la <b>Operación</b> (Entrada o Salida). "
              "También están el botón <b>Ayuda</b> y la fecha y hora.")],
            [("Vehicle reading (left)", "Lectura del vehículo (izquierda)"),
             ("Source buttons <b>Upload file</b>, <b>Local camera</b> and <b>Camera URL</b>; <b>Full screen</b>; the preview; the "
              "<b>OCR analysis</b> bar; <b>Clear reading</b>, <b>Reprocess</b>; and the <b>Recent readings</b> strip.",
              "Botones de fuente <b>Subir archivo</b>, <b>Cámara local</b> y <b>Cámara URL</b>; <b>Pantalla completa</b>; la "
              "vista previa; la barra de <b>análisis OCR</b>; <b>Limpiar lectura</b>, <b>Reprocesar</b>; y la franja de "
              "<b>Lecturas recientes</b>.")],
            [("Identified plate", "Placa identificada"),
             ("The plate in large type, a box to <b>correct or type</b> it and the <b>Verify</b> button. In the United States it also "
              "shows the <b>Issuing state</b> selector and the server confirmation counter.",
              "La placa en letra grande, un cuadro para <b>corregirla o escribirla</b> y el botón <b>Verificar</b>. En "
              "Estados Unidos incluye además el selector de <b>Estado emisor</b> y el contador de confirmación del servidor.")],
            [("Access result", "Resultado de acceso"),
             ("The outcome (Authorized, Denied, Not registered or Without authorization, Manual review), the reason, and the "
              "<b>OCR confidence</b> meter.",
              "El resultado (Autorizado, Denegado, No registrado o Sin autorización, Verificación manual), el motivo y el "
              "medidor de <b>confianza OCR</b>.")],
            [("Vehicle details", "Detalles del vehículo"),
             ("Make, model, year and transport company (Ecuador) or year and model, color, body type and state (United States). "
              "<b>More details</b> opens the full record.",
              "Marca, modelo, año y compañía de transporte (Ecuador) o año y modelo, color, tipo de carrocería y estado "
              "(Estados Unidos). <b>Más datos</b> abre la ficha completa.")],
            [("Actions", "Acciones"),
             ("<b>Register and open gate</b>, <b>Run automatic detection</b> and <b>Manual opening (contingency)</b>.",
              "<b>Registrar y abrir barrera</b>, <b>Procesar detección automática</b> y <b>Apertura manual (Contingencia)</b>.")],
        ],
        caption=("Zones of the Recognition and Access screen.", "Zonas de la pantalla Reconocimiento y Acceso."),
        widths=[24, 76],
    )
    d.fig("03_help", "The <b>Help</b> button opens short instructions about the access flow.",
          "El botón <b>Ayuda</b> abre instrucciones breves sobre el flujo de acceso.")
    d.h2("Controls", "Controles")
    d.table(
        [("Control", "Control"), ("What it does", "Qué hace")],
        [
            [("Help", "Ayuda"), ("Opens the short instructions.", "Abre las instrucciones breves.")],
            [("Full screen", "Pantalla completa"), ("Enlarges the image area so you can check details.", "Amplía el área de imagen para revisar detalles.")],
            [("Clear reading", "Limpiar lectura"), ("Clears the reading on screen. It does not delete the history.",
                                                    "Borra la lectura en pantalla. No borra el historial.")],
            [("Reprocess / Run automatic detection", "Reprocesar / Procesar detección automática"),
             ("Analyzes the loaded image, or the current video frame, again with the detector and OCR.",
              "Vuelve a analizar la imagen cargada, o el fotograma actual del video, con el detector y el OCR.")],
            [("Verify", "Verificar"), ("Checks the plate shown or the one you typed against the registry and the lists.",
                                      "Consulta la placa mostrada o la que usted escribió en el registro y las listas.")],
        ],
        widths=[32, 68],
    )
    d.note("info", ("OCR confidence", "Confianza OCR"),
           "OCR confidence is the <i>lowest</i> probability among the characters of the plate. It tells you how sure the reader "
           "is; it does not say whether the vehicle may enter. Access depends on the current lists.",
           "La confianza OCR es la probabilidad <i>mínima</i> entre los caracteres de la placa. Indica qué tan segura está la "
           "lectura; no dice si el vehículo puede ingresar. El acceso depende de las listas vigentes.")


# ---------------------------------------------------------------------------------------------------------------
def ch_capture(d) -> None:
    d.h1("Loading images, videos and cameras", "Cargar imágenes, videos y cámaras")
    d.h2("Upload a photo", "Subir una fotografía")
    d.steps([
        ("Confirm the checkpoint and whether it is an <b>Entry</b> or an <b>Exit</b>.",
         "Confirme la garita y si se trata de una <b>Entrada</b> o una <b>Salida</b>."),
        ("Press <b>Upload file</b>, then the blue <b>Choose image or video</b> button.",
         "Pulse <b>Subir archivo</b> y luego el botón azul <b>Elegir imagen o video</b>."),
        ("Select a JPG, PNG or WEBP image. It is analyzed as soon as you select it.",
         "Seleccione una imagen JPG, PNG o WEBP. Se analiza en cuanto la selecciona."),
        ("Review the proposed plate and the result before doing anything else.",
         "Revise la placa propuesta y el resultado antes de hacer cualquier otra cosa."),
    ])
    d.h2("Analyze a video", "Analizar un video")
    d.p(
        "Choose an MP4 or WebM file the same way. Videos are analyzed about once per second until a valid plate is confirmed "
        "with at least 94 % OCR confidence in two frames. Buttons next to the video let you <b>Analyze frame</b> on demand, "
        "analyze automatically every 2.5 s, or <b>Stop analysis</b>. If the video ends without a confirmed plate it is not "
        "replayed: the detector waits 15 more seconds and then stops so you can validate manually. Other formats (MOV, M4V) "
        "depend on the browser's codecs; convert them to MP4 (H.264) if they do not play.",
        "Elija un archivo MP4 o WebM de la misma forma. Los videos se analizan aproximadamente una vez por segundo hasta "
        "confirmar una placa válida con al menos 94 % de confianza OCR en dos cuadros. Los botones junto al video permiten "
        "<b>Analizar cuadro</b> a demanda, analizar automáticamente cada 2,5 s o <b>Detener análisis</b>. Si el video termina "
        "sin una placa confirmada no se repite: el detector espera 15 segundos más y luego se detiene para que usted valide "
        "manualmente. Otros formatos (MOV, M4V) dependen de los códecs del navegador; conviértalos a MP4 (H.264) si no se "
        "reproducen.",
    )
    d.h2("Use the local camera", "Usar la cámara local")
    d.steps([
        ("Connect the camera, or use the device's built-in camera.", "Conecte la cámara o use la cámara integrada del dispositivo."),
        ("Choose <b>Local camera</b> and allow camera access when the browser asks.",
         "Elija <b>Cámara local</b> y autorice el acceso a la cámara cuando el navegador lo solicite."),
        ("Place the plate fully inside the visible area, with good light and focus.",
         "Coloque la placa completa dentro del área visible, con buena iluminación y enfoque."),
        ("Press <b>Capture and recognize</b> and check the reading.", "Pulse <b>Capturar y reconocer</b> y revise la lectura."),
    ])
    d.h2("Use a camera URL", "Usar una cámara por URL")
    d.p(
        "Choose <b>Camera URL</b>, select the stream format (<b>web video MP4/WebM</b> or <b>MJPEG</b>) and enter an "
        "HTTP/HTTPS address the browser can play. HLS works only where the browser supports it. RTSP cameras need a bridge "
        "server that republishes the stream; do not assume any address will work directly in the browser.",
        "Elija <b>Cámara URL</b>, seleccione el formato de la transmisión (<b>video web MP4/WebM</b> o <b>MJPEG</b>) e "
        "introduzca una dirección HTTP/HTTPS que el navegador pueda reproducir. HLS funciona solo donde el navegador lo admite. "
        "Las cámaras RTSP necesitan un servidor puente que republique la señal; no asuma que cualquier dirección funcionará "
        "directamente en el navegador.",
    )
    d.h2("Image quality and limits", "Calidad de captura y límites")
    d.table(
        [("Item", "Elemento"), ("Limit or recommendation", "Límite o recomendación")],
        [
            [("Photo formats", "Formatos de foto"), "JPG, JPEG, PNG, WEBP"],
            [("Maximum photo size", "Tamaño máximo de foto"), ("10 MB", "10 MB")],
            [("Minimum photo size", "Tamaño mínimo de foto"), ("Shorter side of at least 160 pixels", "Lado menor de al menos 160 píxeles")],
            [("Video formats", "Formatos de video"), "MP4, WebM"],
            [("Framing", "Encuadre"), ("The whole plate, large enough to read; no glare, backlight, dirt or motion blur.",
                                      "La placa completa y suficientemente grande; sin reflejos, contraluz, suciedad ni desenfoque por movimiento.")],
        ],
        caption=("Capture requirements.", "Requisitos de captura."),
        widths=[30, 70],
    )
    d.p(
        "When in doubt, retake the shot and never accept characters you cannot check visually.",
        "En caso de duda, repita la toma y no acepte caracteres que no pueda comprobar visualmente.",
    )
    d.note("info", ("Privacy and storage", "Privacidad y almacenamiento"),
           "Images and videos are processed temporarily to read the plate and are not kept as permanent files. Operations are "
           "stored as records (CSV) in the private data repository configured for SIRAP; the hosting disk is only a working copy.",
           "Las imágenes y los videos se procesan temporalmente para leer la placa y no se conservan como archivos permanentes. "
           "Las operaciones se guardan como registros (CSV) en el repositorio privado de datos configurado para SIRAP; el disco "
           "del hosting es solo una copia de trabajo.")


# ---------------------------------------------------------------------------------------------------------------
def ch_ecuador(d) -> None:
    d.h1("Ecuador: results and actions", "Ecuador: resultados y acciones")
    d.p(
        "With the Ecuador profile the plate is read as three letters and three or four digits (for example PBA-8901) and "
        "looked up in the Ecuadorian registry. The result card uses one of the following outcomes.",
        "Con el perfil Ecuador la placa se lee como tres letras y tres o cuatro dígitos (por ejemplo PBA-8901) y se busca en "
        "el registro ecuatoriano. La tarjeta de resultado usa uno de los siguientes estados.",
    )
    d.table(
        [("Result", "Resultado"), ("Meaning", "Significado"), ("Safe action", "Acción segura")],
        [
            [("Authorized", "Autorizado"), ("Plate recognized with a current allowlist permission.", "Placa reconocida con permiso vigente en lista blanca."),
             ("Compare plate and vehicle, then record the normal action if your procedure allows it.",
              "Contraste placa y vehículo y registre la acción normal si su procedimiento lo permite.")],
            [("Denied", "Denegado"), ("Plate on a current restricted list.", "Placa en una lista restringida vigente."),
             ("Keep the gate closed and record the rejection.", "Mantenga el acceso cerrado y registre el rechazo.")],
            [("Without authorization", "Sin autorización"), ("The vehicle exists but has no current permission.",
                                                            "El vehículo existe pero no tiene un permiso vigente."),
             ("Do not open normally; ask for review and record what applies.", "No abra de forma normal; solicite revisión y registre lo que corresponda.")],
            [("Not registered", "No registrado"), ("The plate has no record.", "La placa no tiene ficha."),
             ("Do not open; ask for review; register the truck only if you confirmed the plate.",
              "No abra; solicite revisión; registre el camión solo si confirmó la placa.")],
            [("Manual review", "Verificación manual"),
             ("Invalid or unreadable plate, low detector or OCR confidence, or one character away from a registered plate.",
              "Placa inválida o ilegible, baja confianza del detector u OCR, o a un carácter de una placa registrada."),
             ("Compare with the image, correct what you can verify and press Verify.",
              "Compare con la imagen, corrija lo que pueda comprobar y pulse Verificar.")],
        ],
        caption=("Access results and the safe action for each.", "Resultados de acceso y la acción segura para cada uno."),
        widths=[19, 41, 40],
    )
    d.h2("Authorized plate", "Placa autorizada")
    d.fig("04_authorized", "Authorized: PBA-8901 is on the allowlist. The yellow <b>Register and open gate</b> button is now enabled.",
          "Autorizado: PBA-8901 está en la lista blanca. El botón amarillo <b>Registrar y abrir barrera</b> queda habilitado.")
    d.steps([
        ("Check that the final decision is <b>Authorized</b>.", "Compruebe que la decisión final es <b>Autorizado</b>."),
        ("Verify the checkpoint, Entry/Exit and that the plate matches the truck in front of you.",
         "Verifique la garita, Entrada/Salida y que la placa coincide con el camión que tiene delante."),
        ("Press <b>Register and open gate</b> only if your local procedure allows it.",
         "Pulse <b>Registrar y abrir barrera</b> solo si su procedimiento local lo permite."),
        ("Wait for the confirmation. About 3 seconds after a successful registration the reading clears by itself; the "
         "operation stays in the history.",
         "Espere la confirmación. Unos 3 segundos después de un registro exitoso la lectura se limpia sola; la operación "
         "permanece en el historial."),
    ])
    d.fig("05_registered", "After registering: the reading is saved (“Reading recorded in history”) and the action buttons are locked "
          "so the same operation cannot be sent twice.",
          "Tras registrar: la lectura queda guardada («Lectura registrada en el historial») y los botones de acción se bloquean "
          "para que la misma operación no se envíe dos veces.")
    d.h2("Denied plate", "Placa denegada")
    d.fig("06_denied", "Denied: GBO-0429 is on the restricted list. Use <b>Record rejection</b>; the gate stays closed.",
          "Denegado: GBO-0429 está en la lista restringida. Use <b>Registrar rechazo</b>; la barrera permanece cerrada.")
    d.p(
        "A current restriction always prevails over an allowlist entry. Manual intervention is allowed only under an "
        "authorized contingency procedure (see chapter 7).",
        "Una restricción vigente prevalece siempre sobre una entrada de la lista blanca. La intervención manual solo se "
        "permite bajo un procedimiento de contingencia autorizado (véase el capítulo 7).",
    )
    d.h2("Not registered: register a new truck", "No registrado: registrar un camión nuevo")
    d.fig("08_unregistered", "Not registered: GSA-1234 has no record. SIRAP offers to register the truck (<b>Yes, register</b>) or to "
          "continue without registering.",
          "No registrado: GSA-1234 no tiene ficha. SIRAP ofrece registrar el camión (<b>Sí, registrar</b>) o continuar sin registrar.")
    d.steps([
        ("Confirm visually that the plate matches the vehicle in front of you. Do not rely on the OCR alone.",
         "Confirme visualmente que la placa coincide con el vehículo que tiene delante. No confíe solo en el OCR."),
        ("Press <b>Yes, register</b> and complete <b>Make</b>, <b>Model</b>, <b>Color</b> and <b>Owner</b> (required); "
         "<b>Carrier</b> is optional.",
         "Pulse <b>Sí, registrar</b> y complete <b>Marca</b>, <b>Modelo</b>, <b>Color</b> y <b>Propietario</b> (obligatorios); "
         "<b>Transportista</b> es opcional."),
        ("Tick <b>I confirm I compared the plate with the vehicle</b>. Tick <b>Authorize this truck now on the allowlist</b> "
         "only if you verified that entry is permitted; otherwise leave it empty and the truck is saved without permission.",
         "Marque <b>Confirmo que comparé la placa con el vehículo</b>. Marque <b>Autorizar ahora este camión en la lista "
         "blanca</b> solo si verificó que el ingreso está permitido; si no, déjela vacía y el camión se guarda sin permiso."),
        ("Press <b>Save truck</b>. <b>Cancel</b> closes the window without saving.",
         "Pulse <b>Guardar camión</b>. <b>Cancelar</b> cierra la ventana sin guardar."),
    ])
    d.fig("09_register_truck", "The <b>Register new truck</b> form. Registering is not authorizing: the allowlist needs the explicit "
          "second checkbox.",
          "El formulario <b>Registrar camión nuevo</b>. Registrar no es autorizar: la lista blanca requiere la segunda casilla "
          "marcada de forma expresa.")
    d.note("warn", ("Registering never opens the gate", "Registrar nunca abre la barrera"),
           "Registering or authorizing a truck does not open the barrier. The form never modifies an existing plate; if the plate "
           "already exists or is restricted, the change must be made by an Administrator.",
           "Registrar o autorizar un camión no abre la barrera. El formulario nunca modifica una placa existente; si la placa ya "
           "existe o está restringida, el cambio debe hacerlo un Administrador.")
    d.h2("Manual review", "Verificación manual")
    d.fig("07_manual_check", "Manual review: the reading <b>GSA-1234</b> differs by one character from the registered plate GSA-1284, so "
          "SIRAP asks “Did you mean GSA-1284?” instead of calling it unregistered.",
          "Verificación manual: la lectura <b>GSA-1234</b> difiere en un carácter de la placa registrada GSA-1284, por lo que "
          "SIRAP pregunta «¿Quiso decir GSA-1284?» en lugar de darla por no registrada.")
    d.steps([
        ("Enlarge the image (<b>Full screen</b>) if needed.", "Amplíe la imagen (<b>Pantalla completa</b>) si es necesario."),
        ("Compare every character of the reading with the original image.",
         "Compare cada carácter de la lectura con la imagen original."),
        ("If the visible plate lets you confirm it, correct the text and press <b>Verify</b>.",
         "Si la placa visible permite confirmarla, corrija el texto y pulse <b>Verificar</b>."),
        ("Wait for the updated lookup; do not record an opening using the previous result.",
         "Espere la consulta actualizada; no registre una apertura con el resultado anterior."),
        ("If doubt remains, ask for authorization according to the checkpoint protocol.",
         "Si persiste la duda, solicite autorización según el protocolo de la garita."),
    ])
    d.note("info", ("Example", "Ejemplo"),
           "The camera returns PBA-890I but the image clearly shows PBA-8901. Correct only the last character, press Verify and "
           "read the new access decision.",
           "La cámara devuelve PBA-890I pero la imagen muestra con claridad PBA-8901. Corrija solo el último carácter, pulse "
           "Verificar y lea la nueva decisión de acceso.")
    d.h2("Vehicle details and the SRI", "Detalles del vehículo y el SRI")
    d.p(
        "After a plate is verified, the <b>Vehicle details</b> panel shows make, model, year and transport company. SIRAP asks "
        "Ecuador's tax service (<b>SRI</b>) for public vehicle data and merges it with the local registry. When the SRI does "
        "not answer, the panel says so (“SRI did not return all data; available local values are shown”) and uses the local "
        "values. Descriptive data never grant access by themselves, and if they disagree with the vehicle you see, ask for "
        "review instead of changing data to force an authorization.",
        "Tras verificar una placa, el panel <b>Detalles del vehículo</b> muestra marca, modelo, año y compañía de transporte. "
        "SIRAP consulta al servicio de rentas de Ecuador (<b>SRI</b>) los datos públicos del vehículo y los combina con el "
        "registro local. Cuando el SRI no responde, el panel lo indica («El SRI no devolvió todos los datos; se muestran los "
        "valores locales disponibles») y usa los valores locales. Los datos descriptivos nunca otorgan acceso por sí solos y, "
        "si no coinciden con el vehículo que usted ve, solicite revisión en lugar de cambiar datos para forzar una autorización.",
    )


# ---------------------------------------------------------------------------------------------------------------
def ch_usa(d) -> None:
    d.h1("United States: state, serial and two-frame confirmation",
         "Estados Unidos: estado, matrícula y confirmación en dos cuadros")
    d.p(
        "United States plates are not identified by the serial alone: two states can issue the same serial. SIRAP therefore "
        "identifies a vehicle by the <b>issuing state plus the serial</b> (for example TX · BM5T299), reads the state from the "
        "plate itself, and requires stronger evidence before a normal opening.",
        "Las placas de Estados Unidos no se identifican solo por la matrícula: dos estados pueden emitir la misma matrícula. "
        "Por eso SIRAP identifica un vehículo por el <b>estado emisor más la matrícula</b> (por ejemplo TX · BM5T299), lee el "
        "estado en la propia placa y exige evidencia más sólida antes de una apertura normal.",
    )
    d.h2("State and serial", "Estado y matrícula")
    d.fig("31_usa_recognition", "Recognition and Access with the United States profile: the plate panel has an <b>Issuing state</b> "
          "selector and a server confirmation counter.",
          "Reconocimiento y Acceso con el perfil de Estados Unidos: el panel de la placa incluye un selector de <b>Estado emisor</b> "
          "y un contador de confirmación del servidor.")
    d.ul([
        ("The state is read from the state band of the plate (including stylized names). It is <b>never inferred</b> from the "
         "camera location or from the plate design.",
         "El estado se lee en la franja de estado de la placa (incluidos nombres estilizados). <b>Nunca se deduce</b> de la "
         "ubicación de la cámara ni del diseño de la placa."),
        ("If the state cannot be read, the selector shows <i>Unknown state: verify manually</i>. Choose the state you can see on "
         "the plate; the result stays in <b>Manual review</b> until the state and serial are confirmed.",
         "Si el estado no puede leerse, el selector muestra <i>Estado desconocido: verifique manualmente</i>. Elija el estado "
         "que ve en la placa; el resultado permanece en <b>Verificación manual</b> hasta confirmar estado y matrícula."),
        ("Lookups use the exact combination. There is no “Did you mean …?” suggestion for United States plates.",
         "Las consultas usan la combinación exacta. No hay sugerencia «¿Quiso decir …?» para placas de Estados Unidos."),
    ])
    d.h2("Two-frame server confirmation", "Confirmación del servidor en dos cuadros")
    d.p(
        "A normal opening needs the <b>same plate in two distinct frames</b> (different frame identifiers and different image "
        "content) analyzed by the server within <b>7.5 seconds</b>. The counter <b>Server confirmation: n/2</b> shows the "
        "progress. A single still photo, or the same photo sent twice, never reaches 2/2: use a video or a camera, which send "
        "successive frames.",
        "Una apertura normal necesita la <b>misma placa en dos cuadros distintos</b> (identificadores de cuadro distintos y "
        "contenido de imagen distinto) analizados por el servidor en <b>7,5 segundos</b>. El contador <b>Confirmación del "
        "servidor: n/2</b> muestra el avance. Una sola foto fija, o la misma foto enviada dos veces, nunca llega a 2/2: use un "
        "video o una cámara, que envían cuadros sucesivos.",
    )
    d.fig("32_usa_first_frame", "First frame read: BM5T299, state TX. The plate is on the allowlist, but the counter shows 1/2, so "
          "the result is <b>Manual review — waiting for frame confirmation</b>.",
          "Primer cuadro leído: BM5T299, estado TX. La placa está en la lista blanca, pero el contador marca 1/2, por lo que el "
          "resultado es <b>Verificación manual — confirmación de cuadros pendiente</b>.")
    d.fig("33_usa_confirmed", "Second distinct frame confirmed (2/2): the result becomes <b>Authorized</b> and <b>Register and open "
          "gate</b> is enabled.",
          "Segundo cuadro distinto confirmado (2/2): el resultado pasa a <b>Autorizado</b> y se habilita <b>Registrar y abrir "
          "barrera</b>.")
    d.h2("Vehicle details from J.D. Power", "Detalles del vehículo desde J.D. Power")
    d.p(
        "For United States plates the <b>Vehicle details</b> panel shows <b>Year and model</b>, <b>Color</b>, <b>Body type</b> and "
        "<b>State</b>, taken from the J.D. Power plate lookup and the local United States registry. The lookup is polite by "
        "design: one request at a time, results are cached, and an access-denied or rate-limit answer is recorded and never "
        "retried. The page gives vehicle information only, never an owner's name or address. If the lookup is unavailable the "
        "panel falls back to the local registry. Descriptive data do not grant access.",
        "Para placas de Estados Unidos el panel <b>Detalles del vehículo</b> muestra <b>Año y modelo</b>, <b>Color</b>, <b>Tipo "
        "de carrocería</b> y <b>Estado</b>, obtenidos de la consulta de placas de J.D. Power y del registro local de Estados "
        "Unidos. La consulta es cortés por diseño: una solicitud a la vez, resultados en caché, y una respuesta de acceso "
        "denegado o de límite de uso se registra y nunca se reintenta. La página entrega solo información del vehículo, nunca "
        "el nombre ni la dirección de un propietario. Si la consulta no está disponible, el panel recurre al registro local. "
        "Los datos descriptivos no otorgan acceso.",
    )
    d.h2("When normal opening is allowed", "Cuándo se permite la apertura normal")
    d.table(
        [("Situation", "Situación"), ("Result", "Resultado")],
        [
            [("State or serial not confirmed", "Estado o matrícula sin confirmar"), ("Manual review", "Verificación manual")],
            [("OCR below 94 % or detector below 0.70", "OCR inferior a 94 % o detector inferior a 0,70"), ("Manual review", "Verificación manual")],
            [("Exact plate on the restricted list", "Placa exacta en la lista restringida"), ("Denied", "Denegado")],
            [("On the current allowlist but fewer than 2 confirmed frames", "En la lista blanca vigente pero con menos de 2 cuadros confirmados"),
             ("Manual review (waiting for frame confirmation)", "Verificación manual (confirmación de cuadros pendiente)")],
            [("On the current allowlist with 2 distinct confirmed frames", "En la lista blanca vigente con 2 cuadros distintos confirmados"),
             ("Authorized", "Autorizado")],
            [("Registered without a current permission, or not registered", "Registrada sin permiso vigente, o no registrada"),
             ("Without authorization / Not registered", "Sin autorización / No registrado")],
        ],
        caption=("Decision for United States plates.", "Decisión para placas de Estados Unidos."),
        widths=[60, 40],
    )
    d.p(
        "The server issues a single-use confirmation tied to the user, checkpoint and session; it expires after 30 seconds and "
        "cannot be forged by sending confidence values from the browser. The request is saved before the barrier order is sent and "
        "the allowlist is checked again at that moment.",
        "El servidor emite una confirmación de un solo uso ligada al usuario, la garita y la sesión; caduca a los 30 segundos y "
        "no puede falsificarse enviando valores de confianza desde el navegador. La solicitud se guarda antes de enviar la orden "
        "a la barrera y la lista blanca se vuelve a comprobar en ese momento.",
    )
    d.h2("Registering a new United States vehicle", "Registrar un vehículo nuevo de Estados Unidos")
    d.p(
        "The flow is the same as in Ecuador (<b>Yes, register</b>, the form, the confirmation checkbox and the optional "
        "<b>Authorize now</b>), but the record is created for the exact combination of <b>state and serial</b> shown on screen. "
        "Check both before saving.",
        "El flujo es el mismo que en Ecuador (<b>Sí, registrar</b>, el formulario, la casilla de confirmación y la opción "
        "<b>Autorizar ahora</b>), pero la ficha se crea para la combinación exacta de <b>estado y matrícula</b> que muestra la "
        "pantalla. Revise ambos antes de guardar.",
    )
