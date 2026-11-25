import test from 'node:test'
import assert from 'node:assert/strict'
import { language, setLanguage, t } from '../src/i18n.js'
import { readFileSync } from 'node:fs'
import { jdPowerReportUrl, usaLookupStatus, usaVehicleDetails } from '../src/lib/vehicleDetails.js'

test('United States vehicle panel labels are translated in every language', () => {
  const initial = language.value
  const expected = {
    es: ['Año y modelo', 'Color', 'Tipo de carrocería', 'Estado'],
    en: ['Year and model', 'Color', 'Body type', 'State'],
    pt: ['Ano e modelo', 'Cor', 'Tipo de carroceria', 'Estado'],
    fr: ['Année et modèle', 'Couleur', 'Type de carrosserie', 'État'],
    de: ['Baujahr und Modell', 'Farbe', 'Karosserieform', 'Bundesstaat'],
    it: ['Anno e modello', 'Colore', 'Tipo di carrozzeria', 'Stato'],
  }
  try {
    for (const [locale, labels] of Object.entries(expected)) {
      setLanguage(locale)
      assert.deepEqual(['Año y modelo', 'Color', 'Tipo de carrocería', 'Estado'].map(t), labels, locale)
    }
  } finally {
    setLanguage(initial)
  }
})

test('Ecuador vehicle panel labels are unchanged', () => {
  const initial = language.value
  try {
    setLanguage('en')
    assert.deepEqual(['Marca', 'Modelo', 'Año', 'Cia. de transporte'].map(t), ['Make', 'Model', 'Year', 'Transport company'])
  } finally {
    setLanguage(initial)
  }
})

test('J.D. Power values fill the four United States fields', () => {
  const details = usaVehicleDetails({
    plate: '6ZGY984',
    jurisdiction: 'ca',
    lookup: {
      vehicle_title: '2013 Honda Civic',
      vehicle_body_type: 'Sedan 4D LX I4',
      specs_exterior: 'Taffeta White',
      state: 'CA',
    },
  })
  assert.deepEqual(details, { yearModel: '2013 Honda Civic', color: 'Taffeta White', bodyType: 'Sedan 4D LX I4', state: 'CA' })
})

test('J.D. Power wins over the local registry, which only fills gaps', () => {
  const local = { anio: 2019, marca: 'Chevrolet', modelo: 'NLR Reward', color: 'Blanco', jurisdiction: 'TX' }
  assert.deepEqual(
    usaVehicleDetails({ plate: 'CX9S159', jurisdiction: 'TX', lookup: { specs_exterior: 'Summit White' }, vehicle: local }),
    { yearModel: '2019 Chevrolet NLR Reward', color: 'Summit White', bodyType: '', state: 'TX' },
  )
  assert.deepEqual(
    usaVehicleDetails({ plate: 'CX9S159', jurisdiction: 'TX', lookup: {}, vehicle: local }),
    { yearModel: '2019 Chevrolet NLR Reward', color: 'Blanco', bodyType: '', state: 'TX' },
  )
})

test('state comes from the confirmed state and nothing shows without a plate', () => {
  assert.deepEqual(
    usaVehicleDetails({ plate: 'ABC1234', jurisdiction: 'ny', lookup: {}, vehicle: undefined }),
    { yearModel: '', color: '', bodyType: '', state: 'NY' },
  )
  assert.deepEqual(
    usaVehicleDetails({ plate: '', jurisdiction: 'NY', lookup: { vehicle_title: '2013 Honda Civic' } }),
    { yearModel: '', color: '', bodyType: '', state: '' },
  )
  assert.deepEqual(usaVehicleDetails(), { yearModel: '', color: '', bodyType: '', state: '' })
})

test('status line tells where the United States data came from', () => {
  const initial = language.value
  try {
    assert.equal(usaLookupStatus('encontrado'), 'Datos de J.D. Power y del registro local de Estados Unidos de América.')
    for (const local of [undefined, 'desactivado']) {
      assert.equal(usaLookupStatus(local), 'Datos del registro local de Estados Unidos de América.')
    }
    assert.equal(usaLookupStatus('algo_nuevo'), 'J.D. Power no devolvió datos; se muestran los datos locales disponibles.')
    for (const [locale, found] of [
      ['en', 'Data from J.D. Power and the local registry of the United States of America.'],
      ['pt', 'Dados da J.D. Power e do registro local dos Estados Unidos da América.'],
      ['fr', 'Données de J.D. Power et du registre local des États-Unis d’Amérique.'],
      ['de', 'Daten von J.D. Power und aus dem lokalen Register der Vereinigten Staaten von Amerika.'],
      ['it', 'Dati di J.D. Power e del registro locale degli Stati Uniti d’America.'],
    ]) {
      setLanguage(locale)
      assert.equal(t(usaLookupStatus('encontrado')), found, locale)
      assert.notEqual(t('Consultando J.D. Power y el registro local…'), 'Consultando J.D. Power y el registro local…', locale)
      assert.notEqual(t(usaLookupStatus('error')), usaLookupStatus('error'), locale)
    }
  } finally {
    setLanguage(initial)
  }
})

test('each J.D. Power failure names its own cause and is translated', () => {
  const causes = {
    access_limited_401: /no permite el acceso/,
    access_limited_403: /no permite el acceso/,
    access_limited_429: /limitó las consultas/,
    browser_unavailable: /navegador .* no está disponible/,
    no_response: /no respondió o devolvió un error/,
    http_500: /no respondió o devolvió un error/,
    form_failed: /no mostró un informe para esta placa y este estado/,
    report_not_ready: /no mostró un informe para esta placa y este estado/,
    no_report_title: /no mostró un informe para esta placa y este estado/,
    error: /falló por un error del servidor/,
    invalid_input: /no son válidos/,
  }
  const initial = language.value
  try {
    for (const [status, cause] of Object.entries(causes)) {
      const message = usaLookupStatus(status)
      assert.match(message, cause, status)
      assert.match(message, /datos locales disponibles/, status)
      assert.notEqual(message, usaLookupStatus('algo_nuevo'), status)
    }
    // A blocked answer is reported as it is: the text never promises a retry or a workaround.
    assert.match(usaLookupStatus('access_limited_403'), /No se reintenta ni se evita/)
    assert.match(usaLookupStatus('access_limited_429'), /No se reintenta/)
    for (const locale of ['en', 'pt', 'fr', 'de', 'it']) {
      setLanguage(locale)
      const seen = new Set()
      for (const status of Object.keys(causes)) {
        const message = usaLookupStatus(status)
        const translated = t(message)
        assert.notEqual(translated, message, `${locale} ${status}`)
        seen.add(translated)
      }
      // 401/403 share one text, 500/no_response one, the three "no report" statuses one: 7 causes in total.
      assert.equal(seen.size, 7, locale)
    }
  } finally {
    setLanguage(initial)
  }
})

test('the J.D. Power report link carries the plate and the state and rejects anything else', () => {
  assert.equal(
    jdPowerReportUrl('6zgy-984', 'ca'),
    'https://www.jdpower.com/cars/license-plate-lookup-and-decoder/6zgy984-ca-license-plate-report',
  )
  assert.equal(jdPowerReportUrl(' ab 123 ', 'MA'), 'https://www.jdpower.com/cars/license-plate-lookup-and-decoder/ab123-ma-license-plate-report')
  for (const [plate, state] of [['', 'CA'], ['6ZGY984', ''], ['6ZGY984', 'ZZ'], ['6ZGY984', '../x'], ['---', 'CA'], [null, null]]) {
    assert.equal(jdPowerReportUrl(plate, state), '', `${plate}/${state}`)
  }
  // Only letters and digits reach the address, so nothing typed in the plate box can change the path or the host.
  assert.equal(
    jdPowerReportUrl('A/../B?x=1#', 'TX'),
    'https://www.jdpower.com/cars/license-plate-lookup-and-decoder/abx1-tx-license-plate-report',
  )
})

test('the J.D. Power button opens the report in a new tab, only in the United States profile', () => {
  const view = readFileSync(new URL('../src/views/RecognitionView.vue', import.meta.url), 'utf8')
  const button = view.match(/<a\s[^>]*v-if="jdPowerUrl"[^>]*>/)
  assert.ok(button, 'button missing')
  assert.match(button[0], /class="jdpower-button"/)
  assert.match(button[0], /:href="jdPowerUrl"/)
  assert.match(button[0], /target="_blank"/)
  assert.match(button[0], /rel="noopener noreferrer"/)
  assert.match(button[0], /:aria-label="\$t\('Ver detalles del vehículo en J\.D\. Power \(se abre en una pestaña nueva\)'\)"/)
  assert.match(view, /\{\{ \$t\("Ver detalles del vehículo en J\.D\. Power"\) \}\}/)
  assert.match(view, /const jdPowerUrl = computed\(\(\) => \(isUSA\.value \? jdPowerReportUrl\(plateShown\.value, manualJurisdiction\.value\) : ''\)\)/)
})

test('the United States panel no longer shows the vehicle grid or the lookup status; Ecuador keeps its rows', () => {
  const view = readFileSync(new URL('../src/views/RecognitionView.vue', import.meta.url), 'utf8')
  const panel = view.slice(view.indexOf('<section class="card vehicle-panel"'), view.indexOf('<div class="access-action-bar"'))
  assert.doesNotMatch(panel, /vehicle-rows-usa|usaDetails/)
  for (const row of ['Año y modelo', 'Color', 'Tipo de carrocería']) assert.ok(!panel.includes(`$t("${row}")`), row)
  assert.match(panel, /<dl v-if="!isUSA" class="vehicle-rows">/)
  assert.match(panel, /<p v-if="vehicleLookupStatus && !isUSA" class="registered-note"/)
  for (const row of ['Marca', 'Modelo', 'Año', 'Cia. de transporte']) assert.ok(panel.includes(`$t("${row}")`), row)
})

test('the J.D. Power button text and its screen-reader label exist in the six interface languages', () => {
  const labels = {
    es: ['Ver detalles del vehículo en J.D. Power', 'Ver detalles del vehículo en J.D. Power (se abre en una pestaña nueva)'],
    en: ['See Vehicle Details on J.D. Power', 'See Vehicle Details on J.D. Power (opens in a new tab)'],
    fr: ['Voir les détails du véhicule sur J.D. Power', 'Voir les détails du véhicule sur J.D. Power (s’ouvre dans un nouvel onglet)'],
    de: ['Fahrzeugdetails auf J.D. Power ansehen', 'Fahrzeugdetails auf J.D. Power ansehen (wird in einem neuen Tab geöffnet)'],
    it: ['Vedi i dettagli del veicolo su J.D. Power', 'Vedi i dettagli del veicolo su J.D. Power (si apre in una nuova scheda)'],
    pt: ['Ver detalhes do veículo no J.D. Power', 'Ver detalhes do veículo no J.D. Power (abre em uma nova aba)'],
  }
  const [text, aria] = labels.es
  const initial = language.value
  try {
    for (const [locale, [expectedText, expectedAria]] of Object.entries(labels)) {
      setLanguage(locale)
      assert.equal(t(text), expectedText, `${locale} text`)
      assert.equal(t(aria), expectedAria, `${locale} aria-label`)
    }
  } finally {
    setLanguage(initial)
  }
})
