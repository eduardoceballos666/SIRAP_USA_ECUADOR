import test from 'node:test'
import assert from 'node:assert/strict'
import { language, setLanguage, t } from '../src/i18n.js'
import { usaVehicleDetails } from '../src/lib/vehicleDetails.js'

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
