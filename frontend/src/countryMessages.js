// New country/state flow, in the same six supported languages as the application.
const rows = [
  ['País', 'Country', 'País', 'Pays', 'Land', 'Paese'],
  ['Cambiar país', 'Change country', 'Mudar país', 'Changer de pays', 'Land wechseln', 'Cambia paese'],
  ['El país de la solicitud no coincide con el elegido al iniciar sesión.', 'The requested country does not match the country selected at login.', 'O país solicitado não corresponde ao selecionado no login.', 'Le pays demandé ne correspond pas au pays sélectionné à la connexion.', 'Das angeforderte Land stimmt nicht mit der Auswahl bei der Anmeldung überein.', 'Il paese richiesto non corrisponde a quello selezionato all’accesso.'],
  ['country', 'Country', 'País', 'Pays', 'Land', 'Paese'],
  ['jurisdiction', 'Issuing state', 'Estado emissor', 'État émetteur', 'Ausstellender Bundesstaat', 'Stato emittente'],
  ['Ecuador', 'Ecuador', 'Equador', 'Équateur', 'Ecuador', 'Ecuador'],
  ['ecuador', 'Ecuador', 'Equador', 'Équateur', 'Ecuador', 'Ecuador'],
  ['Estados Unidos', 'USA', 'USA', 'USA', 'USA', 'USA'],
  ['usa', 'USA', 'USA', 'USA', 'USA', 'USA'],
  ['Estado emisor', 'Issuing state', 'Estado emissor', 'État émetteur', 'Ausstellender Bundesstaat', 'Stato emittente'],
  ['Seleccione estado emisor', 'Select issuing state', 'Selecione o estado emissor', 'Sélectionnez l’État émetteur', 'Ausstellenden Bundesstaat wählen', 'Seleziona lo stato emittente'],
  ['Estado desconocido: verificar manualmente', 'Unknown state: verify manually', 'Estado desconhecido: verificar manualmente', 'État inconnu : vérifier manuellement', 'Bundesstaat unbekannt: manuell prüfen', 'Stato sconosciuto: verifica manuale'],
  ['Confirmación en servidor', 'Server confirmation', 'Confirmação no servidor', 'Confirmation du serveur', 'Serverbestätigung', 'Conferma del server'],
  ['Otras placas detectadas', 'Other detected plates', 'Outras placas detectadas', 'Autres plaques détectées', 'Weitere erkannte Kennzeichen', 'Altre targhe rilevate'],
  ['Confirme el estado emisor para consultar el registro local.', 'Confirm the issuing state to search the local registry.', 'Confirme o estado emissor para consultar o registro local.', 'Confirmez l’État émetteur pour consulter le registre local.', 'Bestätigen Sie den Bundesstaat für die Suche im lokalen Register.', 'Conferma lo stato emittente per consultare il registro locale.'],
  ['Consultando el registro local…', 'Searching the local registry…', 'Consultando o registro local…', 'Consultation du registre local…', 'Lokales Register wird durchsucht…', 'Consultazione del registro locale…'],
  ['Datos del registro local de Estados Unidos de América.', 'Data from the local registry of the United States of America.', 'Dados do registro local dos Estados Unidos da América.', 'Données du registre local des États-Unis d’Amérique.', 'Daten aus dem lokalen Register der Vereinigten Staaten von Amerika.', 'Dati del registro locale degli Stati Uniti d’America.'],
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
  ['Seleccione el estado emisor de la placa de Estados Unidos de América.', 'Select the issuing state of the plate from the United States of America.', 'Selecione o estado emissor da placa dos Estados Unidos da América.', 'Sélectionnez l’État émetteur de la plaque des États-Unis d’Amérique.', 'Wählen Sie den ausstellenden Bundesstaat des Kennzeichens der Vereinigten Staaten von Amerika.', 'Seleziona lo stato emittente della targa degli Stati Uniti d’America.'],
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
rows.push(...[
  ['Operación pendiente de confirmar', 'Operation awaiting confirmation', 'Operação aguardando confirmação', 'Opération en attente de confirmation', 'Vorgang wartet auf Bestätigung', 'Operazione in attesa di conferma'],
  ['Consulte el resultado antes de abrir otra vez. La recuperación no reenvía la orden de apertura.', 'Check the result before opening again. Recovery does not resend the opening command.', 'Consulte o resultado antes de abrir novamente. A recuperação não reenvia o comando de abertura.', 'Consultez le résultat avant de rouvrir. La récupération ne renvoie pas la commande d’ouverture.', 'Prüfen Sie das Ergebnis vor einer erneuten Öffnung. Die Wiederherstellung sendet keinen Öffnungsbefehl erneut.', 'Controlla il risultato prima di aprire di nuovo. Il recupero non reinvia il comando di apertura.'],
  ['Consultar resultado', 'Check result', 'Consultar resultado', 'Consulter le résultat', 'Ergebnis prüfen', 'Controlla risultato'],
  ['Cancelar intento no registrado', 'Cancel unregistered attempt', 'Cancelar tentativa não registrada', 'Annuler la tentative non enregistrée', 'Nicht registrierten Versuch abbrechen', 'Annulla tentativo non registrato'],
  ['Ver historial', 'View history', 'Ver histórico', 'Voir l’historique', 'Verlauf anzeigen', 'Visualizza cronologia'],
  ['Inicie sesión para recuperar la operación pendiente.', 'Sign in to recover the pending operation.', 'Entre para recuperar a operação pendente.', 'Connectez-vous pour récupérer l’opération en attente.', 'Melden Sie sich an, um den ausstehenden Vorgang abzurufen.', 'Accedi per recuperare l’operazione in sospeso.'],
  ['No se puede recuperar el identificador pendiente. Revise el historial antes de abrir otra vez.', 'The pending ID cannot be recovered. Check history before opening again.', 'Não foi possível recuperar o identificador pendente. Verifique o histórico antes de abrir novamente.', 'Impossible de récupérer l’identifiant en attente. Vérifiez l’historique avant de rouvrir.', 'Die ausstehende Kennung kann nicht abgerufen werden. Prüfen Sie den Verlauf vor einer erneuten Öffnung.', 'Impossibile recuperare l’identificativo in sospeso. Controlla la cronologia prima di aprire di nuovo.'],
  ['No se pudo conservar el identificador de la operación. No se envió la orden.', 'The operation ID could not be saved. The command was not sent.', 'Não foi possível salvar o identificador da operação. O comando não foi enviado.', 'L’identifiant de l’opération n’a pas pu être enregistré. La commande n’a pas été envoyée.', 'Die Vorgangskennung konnte nicht gespeichert werden. Der Befehl wurde nicht gesendet.', 'Impossibile salvare l’identificativo dell’operazione. Il comando non è stato inviato.'],
  ['La respuesta no corresponde a la operación pendiente.', 'The response does not match the pending operation.', 'A resposta não corresponde à operação pendente.', 'La réponse ne correspond pas à l’opération en attente.', 'Die Antwort gehört nicht zum ausstehenden Vorgang.', 'La risposta non corrisponde all’operazione in sospeso.'],
  ['El intento aún no figura en el historial. Consulte otra vez o cancele este identificador antes de crear otra operación.', 'The attempt is not in history yet. Check again or cancel this ID before creating another operation.', 'A tentativa ainda não consta no histórico. Consulte novamente ou cancele este identificador antes de criar outra operação.', 'La tentative ne figure pas encore dans l’historique. Vérifiez à nouveau ou annulez cet identifiant avant de créer une autre opération.', 'Der Versuch ist noch nicht im Verlauf. Prüfen Sie erneut oder stornieren Sie diese Kennung vor einem neuen Vorgang.', 'Il tentativo non è ancora nella cronologia. Ricontrolla o annulla questo identificativo prima di creare un’altra operazione.'],
  ['Apertura confirmada en el historial. No se envió una nueva orden.', 'Opening confirmed in history. No new command was sent.', 'Abertura confirmada no histórico. Nenhum novo comando foi enviado.', 'Ouverture confirmée dans l’historique. Aucune nouvelle commande n’a été envoyée.', 'Öffnung im Verlauf bestätigt. Kein neuer Befehl wurde gesendet.', 'Apertura confermata nella cronologia. Nessun nuovo comando è stato inviato.'],
  ['El intento falló y está registrado. No se envió una nueva orden.', 'The failed attempt is recorded. No new command was sent.', 'A tentativa falhou e está registrada. Nenhum novo comando foi enviado.', 'La tentative échouée est enregistrée. Aucune nouvelle commande n’a été envoyée.', 'Der fehlgeschlagene Versuch ist gespeichert. Kein neuer Befehl wurde gesendet.', 'Il tentativo fallito è registrato. Nessun nuovo comando è stato inviato.'],
  ['Intento cancelado antes de su aceptación. No se abrió la barrera.', 'Attempt cancelled before acceptance. It did not open the barrier.', 'Tentativa cancelada antes da aceitação. Ela não abriu a barreira.', 'Tentative annulée avant son acceptation. Elle n’a pas ouvert la barrière.', 'Versuch vor Annahme abgebrochen. Er hat die Schranke nicht geöffnet.', 'Tentativo annullato prima dell’accettazione. Non ha aperto la barriera.'],
  ['Operación registrada sin apertura.', 'Operation recorded without opening.', 'Operação registrada sem abertura.', 'Opération enregistrée sans ouverture.', 'Vorgang ohne Öffnung gespeichert.', 'Operazione registrata senza apertura.'],
  ['La apertura no tiene confirmación definitiva. Revise el historial y la barrera; no repita la orden.', 'Opening has no final confirmation. Check history and the barrier; do not repeat the command.', 'A abertura não tem confirmação definitiva. Verifique o histórico e a barreira; não repita o comando.', 'L’ouverture n’a pas de confirmation définitive. Vérifiez l’historique et la barrière ; ne répétez pas la commande.', 'Die Öffnung ist nicht abschließend bestätigt. Prüfen Sie Verlauf und Schranke; wiederholen Sie den Befehl nicht.', 'L’apertura non ha una conferma definitiva. Controlla cronologia e barriera; non ripetere il comando.'],
  ['No se pudo confirmar la cancelación. Consulte el estado de la operación.', 'Cancellation could not be confirmed. Check the operation status.', 'Não foi possível confirmar o cancelamento. Consulte o estado da operação.', 'L’annulation n’a pas pu être confirmée. Consultez l’état de l’opération.', 'Der Abbruch konnte nicht bestätigt werden. Prüfen Sie den Vorgangsstatus.', 'Impossibile confermare l’annullamento. Controlla lo stato dell’operazione.'],
  ['Toda apertura requiere un identificador de operación persistente.', 'Every opening requires a persistent operation ID.', 'Toda abertura exige um identificador de operação persistente.', 'Toute ouverture exige un identifiant d’opération persistant.', 'Jede Öffnung benötigt eine dauerhafte Vorgangskennung.', 'Ogni apertura richiede un identificativo di operazione persistente.'],
  ['Almacenamiento temporalmente no disponible. Consulte el estado de la operación antes de reintentar.', 'Storage is temporarily unavailable. Check the operation status before trying again.', 'Armazenamento temporariamente indisponível. Consulte o estado da operação antes de tentar novamente.', 'Stockage temporairement indisponible. Consultez l’état de l’opération avant de réessayer.', 'Speicher vorübergehend nicht verfügbar. Prüfen Sie den Vorgangsstatus vor einem erneuten Versuch.', 'Archivio temporaneamente non disponibile. Controlla lo stato dell’operazione prima di riprovare.'],
  ['CANCELADA', 'CANCELLED', 'CANCELADA', 'ANNULÉE', 'ABGEBROCHEN', 'ANNULLATA'],
])
// Labels of the vehicle-details panel in the United States interface (Ecuador keeps Marca/Modelo/Año/Cia. de transporte).
rows.push(...[
  ['Año y modelo', 'Year and model', 'Ano e modelo', 'Année et modèle', 'Baujahr und Modell', 'Anno e modello'],
  ['Color', 'Color', 'Cor', 'Couleur', 'Farbe', 'Colore'],
  ['Tipo de carrocería', 'Body type', 'Tipo de carroceria', 'Type de carrosserie', 'Karosserieform', 'Tipo di carrozzeria'],
  ['Estado', 'State', 'Estado', 'État', 'Bundesstaat', 'Stato'],
  ['Consultando J.D. Power y el registro local…', 'Checking J.D. Power and the local registry…', 'Consultando a J.D. Power e o registro local…', 'Consultation de J.D. Power et du registre local…', 'J.D. Power und das lokale Register werden abgefragt…', 'Consultazione di J.D. Power e del registro locale…'],
  ['Datos de J.D. Power y del registro local de Estados Unidos de América.', 'Data from J.D. Power and the local registry of the United States of America.', 'Dados da J.D. Power e do registro local dos Estados Unidos da América.', 'Données de J.D. Power et du registre local des États-Unis d’Amérique.', 'Daten von J.D. Power und aus dem lokalen Register der Vereinigten Staaten von Amerika.', 'Dati di J.D. Power e del registro locale degli Stati Uniti d’America.'],
  ['J.D. Power no devolvió datos; se muestran los datos locales disponibles.', 'J.D. Power returned no data; the available local data is shown.', 'A J.D. Power não retornou dados; são exibidos os dados locais disponíveis.', 'J.D. Power n’a renvoyé aucune donnée ; les données locales disponibles sont affichées.', 'J.D. Power hat keine Daten geliefert; die verfügbaren lokalen Daten werden angezeigt.', 'J.D. Power non ha restituito dati; vengono mostrati i dati locali disponibili.'],
  ['J.D. Power no permite el acceso desde este servidor (acceso denegado). No se reintenta ni se evita; se muestran los datos locales disponibles.', 'J.D. Power does not allow access from this server (access denied). It is not retried or bypassed; the available local data is shown.', 'A J.D. Power não permite o acesso a partir deste servidor (acesso negado). Não há nova tentativa nem contorno; são exibidos os dados locais disponíveis.', 'J.D. Power n’autorise pas l’accès depuis ce serveur (accès refusé). Aucune nouvelle tentative ni contournement n’est effectué ; les données locales disponibles sont affichées.', 'J.D. Power erlaubt den Zugriff von diesem Server aus nicht (Zugriff verweigert). Es wird weder wiederholt noch umgangen; die verfügbaren lokalen Daten werden angezeigt.', 'J.D. Power non consente l’accesso da questo server (accesso negato). Non si ritenta né si aggira; vengono mostrati i dati locali disponibili.'],
  ['J.D. Power limitó las consultas (demasiadas solicitudes). No se reintenta; inténtelo más tarde. Se muestran los datos locales disponibles.', 'J.D. Power limited the requests (too many requests). It is not retried; try again later. The available local data is shown.', 'A J.D. Power limitou as consultas (solicitações demais). Não há nova tentativa; tente mais tarde. São exibidos os dados locais disponíveis.', 'J.D. Power a limité les requêtes (trop de requêtes). Aucune nouvelle tentative n’est effectuée ; réessayez plus tard. Les données locales disponibles sont affichées.', 'J.D. Power hat die Anfragen begrenzt (zu viele Anfragen). Es wird nicht wiederholt; versuchen Sie es später erneut. Die verfügbaren lokalen Daten werden angezeigt.', 'J.D. Power ha limitato le richieste (troppe richieste). Non si ritenta; riprovi più tardi. Vengono mostrati i dati locali disponibili.'],
  ['El navegador que consulta a J.D. Power no está disponible en el servidor; se muestran los datos locales disponibles.', 'The browser that queries J.D. Power is not available on the server; the available local data is shown.', 'O navegador que consulta a J.D. Power não está disponível no servidor; são exibidos os dados locais disponíveis.', 'Le navigateur qui interroge J.D. Power n’est pas disponible sur le serveur ; les données locales disponibles sont affichées.', 'Der Browser für die Abfrage bei J.D. Power ist auf dem Server nicht verfügbar; die verfügbaren lokalen Daten werden angezeigt.', 'Il browser che interroga J.D. Power non è disponibile sul server; vengono mostrati i dati locali disponibili.'],
  ['J.D. Power no respondió o devolvió un error; se muestran los datos locales disponibles.', 'J.D. Power did not respond or returned an error; the available local data is shown.', 'A J.D. Power não respondeu ou retornou um erro; são exibidos os dados locais disponíveis.', 'J.D. Power n’a pas répondu ou a renvoyé une erreur ; les données locales disponibles sont affichées.', 'J.D. Power hat nicht geantwortet oder einen Fehler geliefert; die verfügbaren lokalen Daten werden angezeigt.', 'J.D. Power non ha risposto o ha restituito un errore; vengono mostrati i dati locali disponibili.'],
  ['J.D. Power no mostró un informe para esta placa y este estado; revise que ambos sean correctos. Se muestran los datos locales disponibles.', 'J.D. Power did not show a report for this plate and state; check that both are correct. The available local data is shown.', 'A J.D. Power não exibiu um relatório para esta placa e este estado; verifique se ambos estão corretos. São exibidos os dados locais disponíveis.', 'J.D. Power n’a affiché aucun rapport pour cette plaque et cet État ; vérifiez que les deux sont corrects. Les données locales disponibles sont affichées.', 'J.D. Power hat für dieses Kennzeichen und diesen Bundesstaat keinen Bericht angezeigt; prüfen Sie, ob beides stimmt. Die verfügbaren lokalen Daten werden angezeigt.', 'J.D. Power non ha mostrato un rapporto per questa targa e questo stato; verifichi che entrambi siano corretti. Vengono mostrati i dati locali disponibili.'],
  ['La consulta a J.D. Power falló por un error del servidor; se muestran los datos locales disponibles.', 'The J.D. Power lookup failed because of a server error; the available local data is shown.', 'A consulta à J.D. Power falhou por um erro do servidor; são exibidos os dados locais disponíveis.', 'La consultation de J.D. Power a échoué à cause d’une erreur du serveur ; les données locales disponibles sont affichées.', 'Die Abfrage bei J.D. Power ist wegen eines Serverfehlers fehlgeschlagen; die verfügbaren lokalen Daten werden angezeigt.', 'La consultazione di J.D. Power non è riuscita per un errore del server; vengono mostrati i dati locali disponibili.'],
  ['La placa o el estado no son válidos para consultar a J.D. Power; se muestran los datos locales disponibles.', 'The plate or the state is not valid for a J.D. Power lookup; the available local data is shown.', 'A placa ou o estado não são válidos para consultar a J.D. Power; são exibidos os dados locais disponíveis.', 'La plaque ou l’État n’est pas valide pour interroger J.D. Power ; les données locales disponibles sont affichées.', 'Kennzeichen oder Bundesstaat sind für eine Abfrage bei J.D. Power nicht gültig; die verfügbaren lokalen Daten werden angezeigt.', 'La targa o lo stato non sono validi per consultare J.D. Power; vengono mostrati i dati locali disponibili.'],
  ['Bandera de Ecuador', 'Flag of Ecuador', 'Bandeira do Equador', 'Drapeau de l’Équateur', 'Flagge von Ecuador', 'Bandiera dell’Ecuador'],
  ['Bandera de Estados Unidos de América', 'Flag of the United States of America', 'Bandeira dos Estados Unidos da América', 'Drapeau des États-Unis d’Amérique', 'Flagge der Vereinigten Staaten von Amerika', 'Bandiera degli Stati Uniti d’America'],
  ['Ver detalles del vehículo en J.D. Power', 'See Vehicle Details on J.D. Power', 'Ver detalhes do veículo no J.D. Power', 'Voir les détails du véhicule sur J.D. Power', 'Fahrzeugdetails auf J.D. Power ansehen', 'Vedi i dettagli del veicolo su J.D. Power'],
  ['Ver detalles del vehículo en J.D. Power (se abre en una pestaña nueva)', 'See Vehicle Details on J.D. Power (opens in a new tab)', 'Ver detalhes do veículo no J.D. Power (abre em uma nova aba)', 'Voir les détails du véhicule sur J.D. Power (s’ouvre dans un nouvel onglet)', 'Fahrzeugdetails auf J.D. Power ansehen (wird in einem neuen Tab geöffnet)', 'Vedi i dettagli del veicolo su J.D. Power (si apre in una nuova scheda)'],
])
export const countryMessages = Object.fromEntries(['en', 'pt', 'fr', 'de', 'it'].map((language, index) =>
  [language, Object.fromEntries(rows.map((row) => [row[0], row[index + 1]]))]))
