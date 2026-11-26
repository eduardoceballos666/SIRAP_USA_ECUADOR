import test from 'node:test'
import assert from 'node:assert/strict'
import { language, messages, setLanguage, t } from '../src/i18n.js'

// Texts that are written the same way in English and Italian.
const sameInEnglishAndItalian = new Set([
  'Contraseña', 'Contraseña * (mín. 8)', 'Archivo', ', en', 'ecuador', 'Estados Unidos', 'usa',
])

test('every Italian text is translated, none falls back to English', () => {
  const english = messages.en
  const italian = messages.it
  const untranslated = Object.keys(english).filter((key) => (
    !sameInEnglishAndItalian.has(key) && italian[key] === english[key] && key !== english[key]
  ))
  assert.deepEqual(untranslated, [])
  const missing = Object.keys(english).filter((key) => !italian[key])
  assert.deepEqual(missing, [])
})

test('Italian keeps the leading and trailing spaces of text fragments', () => {
  for (const key of Object.keys(messages.en)) {
    if (!/^\s|\s$/.test(key)) continue
    const value = messages.it[key]
    assert.equal(/^\s/.test(value), /^\s/.test(key), `leading space: ${JSON.stringify(key)}`)
    assert.equal(/\s$/.test(value), /\s$/.test(key), `trailing space: ${JSON.stringify(key)}`)
  }
})

test('main screens read in Italian', () => {
  const initial = language.value
  try {
    setLanguage('it')
    assert.deepEqual(
      ['Modelo', 'Año', 'Propietario', 'Detalles del vehículo', 'Placa', 'Garita', 'Historial de operaciones', 'Reconocimiento y Acceso', 'Cancelar', 'Aceptar'].map(t),
      ['Modello', 'Anno', 'Proprietario', 'Dettagli del veicolo', 'Targa', 'Varco', 'Cronologia delle operazioni', 'Riconoscimento e accesso', 'Annulla', 'Conferma'],
    )
    assert.deepEqual(
      ['Color *', 'color', 'Conf. OCR', 'Supervisor', 'SUPERVISOR', 'MANUAL', 'Seleccione tipo *'].map(t),
      ['Colore *', 'colore', 'Aff. OCR', 'Supervisore', 'SUPERVISORE', 'MANUALE', 'Scegli tipo *'],
    )
    // User names shown in the Administration table stay as typed at login.
    assert.deepEqual(['operador', 'supervisor', 'admin'].map(t), ['operador', 'supervisor', 'admin'])
    assert.equal(t('ACCESO AUTORIZADO'), 'ACCESSO AUTORIZZATO')
    assert.equal(t('Imágenes'), 'Immagini')
  } finally {
    setLanguage(initial)
  }
})

test('Italian messages with a variable part are translated', () => {
  const initial = language.value
  try {
    setLanguage('it')
    assert.equal(t('La placa PBA-8901 ahora está en la lista BLANCA.'), 'La targa PBA-8901 è ora nella lista BLANCA.')
    assert.equal(t('Garita 4 agregada.'), 'Varco 4 aggiunto.')
    assert.equal(t('1 garita(s) actualizada(s).'), '1 varco aggiornato.')
    assert.equal(t('3 garita(s) actualizada(s).'), '3 varchi aggiornati.')
    assert.equal(t('2 usuario(s) actualizado(s).'), '2 utenti aggiornati.')
    assert.equal(t('Confirmando la misma placa: 1/2 cuadros'), 'Conferma della stessa targa: 1/2 fotogrammi')
    assert.equal(t('Camión PBA-8901 registrado, pendiente de autorización.'), 'Camion PBA-8901 registrato, in attesa di autorizzazione.')
    assert.equal(t('Complete los campos obligatorios: marca, modelo'), 'Compila i campi obbligatori: marca, modelo')
    assert.equal(t('¿QUISO DECIR PBA-8901?'), 'INTENDEVI PBA-8901?')
    // Other languages keep their previous behaviour.
    setLanguage('en')
    assert.equal(t('Garita 4 agregada.'), 'Checkpoint 4 added.')
  } finally {
    setLanguage(initial)
  }
})
