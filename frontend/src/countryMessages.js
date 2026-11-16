// New country/state flow, in the same six supported languages as the application.
const rows = [
  ['País', 'Country', 'País', 'Pays', 'Land', 'Paese'],
  ['Cambiar país', 'Change country', 'Mudar país', 'Changer de pays', 'Land wechseln', 'Cambia paese'],
  ['El país de la solicitud no coincide con el elegido al iniciar sesión.', 'The requested country does not match the country selected at login.', 'O país solicitado não corresponde ao selecionado no login.', 'Le pays demandé ne correspond pas au pays sélectionné à la connexion.', 'Das angeforderte Land stimmt nicht mit der Auswahl bei der Anmeldung überein.', 'Il paese richiesto non corrisponde a quello selezionato all’accesso.'],
  ['country', 'Country', 'País', 'Pays', 'Land', 'Paese'],
  ['jurisdiction', 'Issuing state', 'Estado emissor', 'État émetteur', 'Ausstellender Bundesstaat', 'Stato emittente'],
  ['Ecuador', 'Ecuador', 'Equador', 'Équateur', 'Ecuador', 'Ecuador'],
  ['ecuador', 'Ecuador', 'Equador', 'Équateur', 'Ecuador', 'Ecuador'],
  ['Estados Unidos', 'United States', 'Estados Unidos', 'États-Unis', 'Vereinigte Staaten', 'Stati Uniti'],
  ['usa', 'United States', 'Estados Unidos', 'États-Unis', 'Vereinigte Staaten', 'Stati Uniti'],
  ['Estado emisor', 'Issuing state', 'Estado emissor', 'État émetteur', 'Ausstellender Bundesstaat', 'Stato emittente'],
  ['Seleccione estado emisor', 'Select issuing state', 'Selecione o estado emissor', 'Sélectionnez l’État émetteur', 'Ausstellenden Bundesstaat wählen', 'Seleziona lo stato emittente'],
  ['Estado desconocido: verificar manualmente', 'Unknown state: verify manually', 'Estado desconhecido: verificar manualmente', 'État inconnu : vérifier manuellement', 'Bundesstaat unbekannt: manuell prüfen', 'Stato sconosciuto: verifica manuale'],
  ['Confirmación en servidor', 'Server confirmation', 'Confirmação no servidor', 'Confirmation du serveur', 'Serverbestätigung', 'Conferma del server'],
  ['Otras placas detectadas', 'Other detected plates', 'Outras placas detectadas', 'Autres plaques détectées', 'Weitere erkannte Kennzeichen', 'Altre targhe rilevate'],
  ['Confirme el estado emisor para consultar el registro local.', 'Confirm the issuing state to search the local registry.', 'Confirme o estado emissor para consultar o registro local.', 'Confirmez l’État émetteur pour consulter le registre local.', 'Bestätigen Sie den Bundesstaat für die Suche im lokalen Register.', 'Conferma lo stato emittente per consultare il registro locale.'],
  ['Consultando el registro local…', 'Searching the local registry…', 'Consultando o registro local…', 'Consultation du registre local…', 'Lokales Register wird durchsucht…', 'Consultazione del registro locale…'],
  ['Datos del registro local de Estados Unidos.', 'Data from the local United States registry.', 'Dados do registro local dos Estados Unidos.', 'Données du registre local des États-Unis.', 'Daten aus dem lokalen US-Register.', 'Dati del registro locale degli Stati Uniti.'],
  ['El modelo seleccionado no está disponible; puede verificar la placa manualmente.', 'The selected model is unavailable; you can verify the plate manually.', 'O modelo selecionado não está disponível; verifique a placa manualmente.', 'Le modèle sélectionné est indisponible ; vérifiez la plaque manuellement.', 'Das ausgewählte Modell ist nicht verfügbar; prüfen Sie das Kennzeichen manuell.', 'Il modello selezionato non è disponibile; verifica la targa manualmente.'],
  ['ESTADO O MATRÍCULA SIN CONFIRMAR', 'STATE OR PLATE UNCONFIRMED', 'ESTADO OU PLACA NÃO CONFIRMADOS', 'ÉTAT OU PLAQUE NON CONFIRMÉS', 'BUNDESSTAAT ODER KENNZEICHEN UNBESTÄTIGT', 'STATO O TARGA NON CONFERMATI'],
  ['CONFIRMACIÓN TEMPORAL PENDIENTE', 'WAITING FOR FRAME CONFIRMATION', 'AGUARDANDO CONFIRMAÇÃO DE QUADROS', 'CONFIRMATION DES IMAGES EN ATTENTE', 'BILDBESTÄTIGUNG AUSSTEHEND', 'CONFERMA DEI FOTOGRAMMI IN ATTESA'],
  ['APERTURA AUTOMÁTICA DESACTIVADA', 'AUTOMATIC OPENING DISABLED', 'ABERTURA AUTOMÁTICA DESATIVADA', 'OUVERTURE AUTOMATIQUE DÉSACTIVÉE', 'AUTOMATISCHE ÖFFNUNG DEAKTIVIERT', 'APERTURA AUTOMATICA DISATTIVATA'],
  ['Se requieren dos cuadros distintos dentro de 7,5 segundos.', 'Two distinct frames within 7.5 seconds are required.', 'São necessários dois quadros distintos em 7,5 segundos.', 'Deux images distinctes en 7,5 secondes sont requises.', 'Zwei unterschiedliche Bilder innerhalb von 7,5 Sekunden sind erforderlich.', 'Servono due fotogrammi distinti entro 7,5 secondi.'],
  ['La confirmación ya no está disponible. Procese de nuevo la imagen o cámara.', 'Confirmation is no longer available. Process the image or camera again.', 'A confirmação não está mais disponível. Processe a imagem ou câmera novamente.', 'La confirmation n’est plus disponible. Traitez à nouveau l’image ou la caméra.', 'Die Bestätigung ist nicht mehr verfügbar. Verarbeiten Sie Bild oder Kamera erneut.', 'La conferma non è più disponibile. Elabora nuovamente l’immagine o la telecamera.'],
  ['La placa o el estado no coinciden con la lectura confirmada en el servidor.', 'The plate or state does not match the server-confirmed reading.', 'A placa ou estado não coincide com a leitura confirmada no servidor.', 'La plaque ou l’État ne correspond pas à la lecture confirmée par le serveur.', 'Kennzeichen oder Bundesstaat stimmen nicht mit der Serverbestätigung überein.', 'La targa o lo stato non corrispondono alla lettura confermata dal server.'],
  ['La confirmación ya se utilizó para una apertura. No repita la orden.', 'This confirmation was already used for opening. Do not repeat the command.', 'Esta confirmação já foi usada para abertura. Não repita o comando.', 'Cette confirmation a déjà servi à ouvrir. Ne répétez pas la commande.', 'Diese Bestätigung wurde bereits zum Öffnen verwendet. Befehl nicht wiederholen.', 'Questa conferma è già stata usata per aprire. Non ripetere il comando.'],
  ['Ya existe una solicitud de apertura para esta confirmación. No repita la orden.', 'An opening request already exists for this confirmation. Do not repeat the command.', 'Já existe uma solicitação de abertura para esta confirmação. Não repita o comando.', 'Une demande d’ouverture existe déjà pour cette confirmation. Ne répétez pas la commande.', 'Für diese Bestätigung besteht bereits eine Öffnungsanforderung. Nicht wiederholen.', 'Esiste già una richiesta di apertura per questa conferma. Non ripetere il comando.'],
  ['La apertura automática requiere dos lecturas del detector confirmadas en el servidor.', 'Automatic opening requires two detector readings confirmed by the server.', 'A abertura automática exige duas leituras do detector confirmadas pelo servidor.', 'L’ouverture automatique nécessite deux lectures du détecteur confirmées par le serveur.', 'Die automatische Öffnung erfordert zwei vom Server bestätigte Detektorlesungen.', 'L’apertura automatica richiede due letture del rilevatore confermate dal server.'],
  ['La matrícula no coincide con la lectura guardada en el servidor.', 'The plate does not match the reading saved on the server.', 'A placa não coincide com a leitura salva no servidor.', 'La plaque ne correspond pas à la lecture enregistrée sur le serveur.', 'Das Kennzeichen stimmt nicht mit der gespeicherten Serverlesung überein.', 'La targa non corrisponde alla lettura salvata sul server.'],
  ['Confirme la matrícula y su estado emisor; no se deduce el estado por ubicación.', 'Confirm the plate and its issuing state; location is not used to infer the state.', 'Confirme a placa e o estado emissor; a localização não determina o estado.', 'Confirmez la plaque et son État émetteur ; l’État n’est pas déduit du lieu.', 'Bestätigen Sie Kennzeichen und Bundesstaat; der Standort bestimmt den Bundesstaat nicht.', 'Conferma la targa e lo stato emittente; lo stato non viene dedotto dalla posizione.'],
  ['La mínima probabilidad por carácter debe ser al menos 0,94.', 'The minimum character probability must be at least 0.94.', 'A probabilidade mínima por caractere deve ser pelo menos 0,94.', 'La probabilité minimale par caractère doit être au moins 0,94.', 'Die kleinste Zeichenwahrscheinlichkeit muss mindestens 0,94 betragen.', 'La probabilità minima per carattere deve essere almeno 0,94.'],
  ['La confianza del detector debe ser al menos 0,70.', 'Detector confidence must be at least 0.70.', 'A confiança do detector deve ser pelo menos 0,70.', 'La confiance du détecteur doit être au moins 0,70.', 'Die Detektorkonfidenz muss mindestens 0,70 betragen.', 'La confidenza del rilevatore deve essere almeno 0,70.'],
  ['Estado y matrícula confirmados en dos cuadros distintos en el servidor.', 'State and plate confirmed in two distinct frames on the server.', 'Estado e placa confirmados em dois quadros distintos no servidor.', 'État et plaque confirmés sur deux images distinctes par le serveur.', 'Bundesstaat und Kennzeichen in zwei unterschiedlichen Bildern vom Server bestätigt.', 'Stato e targa confermati dal server in due fotogrammi distinti.'],
  ['La lista blanca está vigente; faltan dos cuadros distintos confirmados por el servidor.', 'The allowlist entry is current; two distinct server-confirmed frames are still required.', 'A lista de permitidos está vigente; faltam dois quadros distintos confirmados pelo servidor.', 'L’autorisation est valide ; deux images distinctes confirmées par le serveur restent requises.', 'Der Freigabeeintrag ist gültig; zwei unterschiedliche serverbestätigte Bilder fehlen noch.', 'L’autorizzazione è valida; servono ancora due fotogrammi distinti confermati dal server.'],
  ['Consulte o registre la combinación exacta de estado y matrícula.', 'Search or register the exact combination of state and plate.', 'Consulte ou cadastre a combinação exata de estado e placa.', 'Consultez ou enregistrez la combinaison exacte de l’État et de la plaque.', 'Suchen oder registrieren Sie die genaue Kombination aus Bundesstaat und Kennzeichen.', 'Consulta o registra la combinazione esatta di stato e targa.'],
  ['Seleccione el estado emisor de la placa de Estados Unidos.', 'Select the issuing state of the United States plate.', 'Selecione o estado emissor da placa dos Estados Unidos.', 'Sélectionnez l’État émetteur de la plaque américaine.', 'Wählen Sie den ausstellenden Bundesstaat des US-Kennzeichens.', 'Seleziona lo stato emittente della targa statunitense.'],
]
rows.push(...[
  [
    "Misma interfaz y mismos pesos para ambos países.",
    "Same interface and weights for both countries.",
    "Mesma interface e pesos para os dois países.",
    "Même interface et mêmes poids pour les deux pays.",
    "Gleiche Oberfläche und Gewichte für beide Länder.",
    "Stessa interfaccia e stessi pesi per entrambi i paesi."
  ],
  [
    "Semilla 2 compartida",
    "Shared seed 2",
    "Semente 2 compartilhada",
    "Graine 2 partagée",
    "Gemeinsamer Seed 2",
    "Seed 2 condiviso"
  ],
  [
    "Configuración operativa actual",
    "Current operating settings",
    "Configuração operacional atual",
    "Configuration opérationnelle actuelle",
    "Aktuelle Betriebseinstellungen",
    "Configurazione operativa attuale"
  ],
  [
    "Probabilidad mínima por carácter",
    "Minimum character probability",
    "Probabilidade mínima por caractere",
    "Probabilité minimale par caractère",
    "Kleinste Zeichenwahrscheinlichkeit",
    "Probabilità minima per carattere"
  ],
  [
    "El país y el idioma se eligen al iniciar sesión. El reconocimiento, las listas y el historial usan ese país.",
    "Choose the country and language at login. Recognition, lists and history use that country.",
    "Escolha o país e o idioma no login. Reconhecimento, listas e histórico usam esse país.",
    "Choisissez le pays et la langue à la connexion. La reconnaissance, les listes et l’historique utilisent ce pays.",
    "Land und Sprache werden bei der Anmeldung gewählt. Erkennung, Listen und Verlauf verwenden dieses Land.",
    "Scegli paese e lingua all’accesso. Riconoscimento, liste e cronologia usano quel paese."
  ],
  [
    "Ambos países usan el detector entrenado para USA y el mismo OCR global, sin reentrenamiento.",
    "Both countries use the USA-trained detector and the same global OCR, without retraining.",
    "Ambos os países usam o detector treinado para os EUA e o mesmo OCR global, sem novo treinamento.",
    "Les deux pays utilisent le détecteur entraîné pour les États-Unis et le même OCR global, sans réentraînement.",
    "Beide Länder nutzen den für die USA trainierten Detektor und dasselbe globale OCR ohne erneutes Training.",
    "Entrambi i paesi usano il rilevatore addestrato per gli USA e lo stesso OCR globale, senza riaddestramento."
  ],
  [
    "USA conserva letras y números y exige estado emisor más matrícula para identificar un vehículo.",
    "USA preserves letters and digits and requires the issuing state plus plate to identify a vehicle.",
    "EUA preserva letras e números e exige estado emissor mais placa para identificar um veículo.",
    "USA conserve les lettres et les chiffres et exige l’État émetteur et la plaque pour identifier un véhicule.",
    "USA behält Buchstaben und Ziffern bei und benötigt Bundesstaat und Kennzeichen zur Fahrzeugidentifikation.",
    "USA conserva lettere e numeri e richiede stato emittente e targa per identificare un veicolo."
  ],
  [
    "Ecuador aplica su formato de matrícula, por ejemplo ABC-1234, sin exigir un estado emisor.",
    "Ecuador applies its plate format, such as ABC-1234, without requiring an issuing state.",
    "Equador aplica seu formato de placa, como ABC-1234, sem exigir estado emissor.",
    "Équateur applique son format de plaque, par exemple ABC-1234, sans exiger d’État émetteur.",
    "Ecuador verwendet sein Kennzeichenformat, etwa ABC-1234, ohne einen Bundesstaat zu verlangen.",
    "Ecuador applica il proprio formato, ad esempio ABC-1234, senza richiedere uno stato emittente."
  ],
  [
    "La apertura normal requiere lista blanca vigente y dos cuadros distintos confirmados por el servidor en 7,5 segundos.",
    "Normal opening requires a current allowlist entry and two distinct frames confirmed by the server within 7.5 seconds.",
    "A abertura normal exige autorização vigente e dois quadros distintos confirmados pelo servidor em 7,5 segundos.",
    "L’ouverture normale exige une autorisation valide et deux images distinctes confirmées par le serveur en 7,5 secondes.",
    "Normales Öffnen erfordert eine gültige Freigabe und zwei unterschiedliche, innerhalb von 7,5 Sekunden serverbestätigte Bilder.",
    "L’apertura normale richiede autorizzazione valida e due fotogrammi distinti confermati dal server entro 7,5 secondi."
  ],
  [
    "Cada operación queda en el historial con usuario, garita y hora. La barrera configurada es simulada.",
    "Each operation records the user, gate and time in history. The configured barrier is simulated.",
    "Cada operação registra usuário, guarita e hora no histórico. A barreira configurada é simulada.",
    "Chaque opération conserve l’utilisateur, le poste et l’heure dans l’historique. La barrière configurée est simulée.",
    "Jeder Vorgang speichert Benutzer, Tor und Uhrzeit im Verlauf. Die konfigurierte Schranke ist simuliert.",
    "Ogni operazione registra utente, varco e ora nella cronologia. La barriera configurata è simulata."
  ],
  [
    "El rendimiento del checkpoint compartido con placas ecuatorianas está pendiente de evaluación.",
    "The shared checkpoint has yet to be evaluated on Ecuadorian plates.",
    "O desempenho do checkpoint compartilhado em placas equatorianas ainda precisa ser avaliado.",
    "Les performances du checkpoint partagé sur les plaques équatoriennes restent à évaluer.",
    "Die Leistung des gemeinsamen Checkpoints für ecuadorianische Kennzeichen muss noch bewertet werden.",
    "Le prestazioni del checkpoint condiviso sulle targhe ecuadoriane devono ancora essere valutate."
  ],
  [
    "Diagnóstico de desarrollo con ocho fotos reutilizadas; no es un test final independiente.",
    "Development diagnostic using eight reused photos; this is not an independent final test.",
    "Diagnóstico de desenvolvimento com oito fotos reutilizadas; não é um teste final independente.",
    "Diagnostic de développement sur huit photos réutilisées ; ce n’est pas un test final indépendant.",
    "Entwicklungsdiagnose mit acht wiederverwendeten Fotos; kein unabhängiger Abschlusstest.",
    "Diagnosi di sviluppo con otto foto riutilizzate; non è un test finale indipendente."
  ],
  [
    "Matrículas exactas entre las detectadas",
    "Exact plates among detections",
    "Placas exatas entre as detectadas",
    "Plaques exactes parmi les détections",
    "Exakte Kennzeichen unter den Erkennungen",
    "Targhe esatte tra quelle rilevate"
  ],
  [
    "Estados correctos entre los conocidos",
    "Correct states among known states",
    "Estados corretos entre os conhecidos",
    "États corrects parmi les États connus",
    "Richtige Bundesstaaten unter den bekannten",
    "Stati corretti tra quelli noti"
  ],
  [
    "Escenas con referencia completa",
    "Scenes with complete reference",
    "Cenas com referência completa",
    "Scènes avec référence complète",
    "Szenen mit vollständiger Referenz",
    "Scene con riferimento completo"
  ],
  [
    "Placas detectadas / omitidas",
    "Plates detected / missed",
    "Placas detectadas / perdidas",
    "Plaques détectées / manquées",
    "Erkannte / übersehene Kennzeichen",
    "Targhe rilevate / mancate"
  ],
  [
    "Una imagen conserva una región dudosa; queda fuera del recuento por escenas completas.",
    "One image retains an uncertain region and is excluded from complete-scene counts.",
    "Uma imagem tem uma região duvidosa e fica fora da contagem de cenas completas.",
    "Une image conserve une zone incertaine et est exclue du comptage des scènes complètes.",
    "Ein Bild enthält einen unklaren Bereich und ist von der Zählung vollständiger Szenen ausgeschlossen.",
    "Un’immagine conserva una regione incerta ed è esclusa dal conteggio delle scene complete."
  ],
  [
    "Cambiar reglas OCR no equivale a entrenar un modelo para otro país.",
    "Changing OCR rules does not train a model for another country.",
    "Alterar regras de OCR não equivale a treinar um modelo para outro país.",
    "Modifier les règles OCR ne revient pas à entraîner un modèle pour un autre pays.",
    "Das Ändern von OCR-Regeln trainiert kein Modell für ein anderes Land.",
    "Cambiare le regole OCR non equivale ad addestrare un modello per un altro paese."
  ],
  [
    "Los estados desconocidos, las lecturas incompletas y las confianzas bajas requieren revisión manual.",
    "Unknown states, incomplete readings and low confidence require manual review.",
    "Estados desconhecidos, leituras incompletas e baixa confiança exigem revisão manual.",
    "Les États inconnus, les lectures incomplètes et les faibles confiances exigent une vérification manuelle.",
    "Unbekannte Bundesstaaten, unvollständige Lesungen und geringe Konfidenz erfordern manuelle Prüfung.",
    "Stati sconosciuti, letture incomplete e bassa confidenza richiedono revisione manuale."
  ],
  [
    "Las pruebas del software comprueban reglas y persistencia con una barrera simulada; no miden la exactitud real del modelo.",
    "Software tests check rules and persistence with a simulated barrier; they do not measure actual model accuracy.",
    "Os testes de software verificam regras e persistência com uma barreira simulada; não medem a exatidão real do modelo.",
    "Les tests logiciels vérifient les règles et la persistance avec une barrière simulée ; ils ne mesurent pas l’exactitude réelle du modèle.",
    "Softwaretests prüfen Regeln und Speicherung mit einer simulierten Schranke; sie messen nicht die tatsächliche Modellgenauigkeit.",
    "I test software verificano regole e persistenza con una barriera simulata; non misurano l’accuratezza reale del modello."
  ]
])
export const countryMessages = Object.fromEntries(['en', 'pt', 'fr', 'de', 'it'].map((language, index) =>
  [language, Object.fromEntries(rows.map((row) => [row[0], row[index + 1]]))]))
