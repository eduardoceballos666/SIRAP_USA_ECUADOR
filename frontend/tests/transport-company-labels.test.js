import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { language, setLanguage, t } from '../src/i18n.js'

// Every place where the Ecuador interface says "transport company" (vehicle-details panel,
// new-truck form, Administration vehicle form).
const keys = ['Cia. de transporte', 'Transportista', 'Transportista *', 'Empresa transportista (opcional)', 'transportista']

const expected = {
  es: ['Cia. de transporte', 'Transportista', 'Transportista *', 'Empresa transportista (opcional)', 'transportista'],
  en: ['Transport company', 'Transport company', 'Transport company *', 'Transport company (optional)', 'transport company'],
  pt: ['Transportadora', 'Transportadora', 'Transportadora *', 'Empresa transportadora (opcional)', 'transportadora'],
  fr: ['Transporteur', 'Transporteur', 'Transporteur *', 'Transporteur (facultatif)', 'transporteur'],
  de: ['Transportunternehmen', 'Transportunternehmen', 'Transportunternehmen *', 'Transportunternehmen (optional)', 'Transportunternehmen'],
  it: ['Società di trasporto', 'Società di trasporto', 'Società di trasporto *', 'Società di trasporto (facoltativo)', 'società di trasporto'],
}

test('"Transport company" is translated in every language of the Ecuador interface', () => {
  const initial = language.value
  try {
    for (const [locale, labels] of Object.entries(expected)) {
      setLanguage(locale)
      assert.deepEqual(keys.map(t), labels, locale)
    }
    for (const locale of ['es', 'pt', 'fr', 'de', 'it']) {
      setLanguage(locale)
      for (const key of keys) assert.ok(!/transport company/i.test(t(key)), `${locale}: ${key} still in English`)
    }
  } finally {
    setLanguage(initial)
  }
})

test('the views use the translated transport-company keys', () => {
  const recognition = readFileSync(new URL('../src/views/RecognitionView.vue', import.meta.url), 'utf8')
  const admin = readFileSync(new URL('../src/views/AdminView.vue', import.meta.url), 'utf8')
  assert.ok(recognition.includes('$t("Cia. de transporte")'))
  assert.ok(recognition.includes('$t("Transportista")'))
  assert.ok(recognition.includes("$t('Empresa transportista (opcional)')"))
  assert.ok(admin.includes('$t("Transportista *")'))
})
