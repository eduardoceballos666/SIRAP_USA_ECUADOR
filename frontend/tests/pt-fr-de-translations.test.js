import test from 'node:test'
import assert from 'node:assert/strict'
import { language, messages, setLanguage, t } from '../src/i18n.js'

// Texts that are written the same way in English and in the language.
const sameAsEnglish = {
  pt: ['Estados Unidos', 'usa'],
  fr: [
    'Estados Unidos', 'usa', 'Módulos', 'Administración', 'imágenes,', 'imágenes', 'Imágenes', 'Imagen', 'IMAGEN',
    'Acción', 'Acciones', 'accion', 'ACTIVA', 'INACTIVA', 'activa', 'Fuente', 'fuente', 'tipo',
  ],
  de: ['Estados Unidos', 'usa', 'Administrador', 'ADMINISTRADOR', 'ecuador', ', en'],
}

for (const locale of ['pt', 'fr', 'de']) {
  test(`every ${locale} text is translated, none falls back to English`, () => {
    const english = messages.en
    const dictionary = messages[locale]
    const untranslated = Object.keys(english).filter((key) => (
      !sameAsEnglish[locale].includes(key) && dictionary[key] === english[key] && key !== english[key]
    ))
    assert.deepEqual(untranslated, [])
    // Technical texts (file names, e-mail addresses, units) are the same in every language.
    assert.deepEqual(Object.keys(english).filter((key) => !dictionary[key] && english[key] !== key), [])
  })

  test(`${locale} keeps the leading and trailing spaces of text fragments`, () => {
    for (const key of Object.keys(messages.en)) {
      if (!/^\s|\s$/.test(key)) continue
      const value = messages[locale][key]
      assert.equal(/^\s/.test(value), /^\s/.test(key), `${locale} leading space: ${JSON.stringify(key)}`)
      assert.equal(/\s$/.test(value), /\s$/.test(key), `${locale} trailing space: ${JSON.stringify(key)}`)
    }
  })
}

const samples = {
  pt: {
    texts: ['Color *', 'Marca *', 'Imágenes', 'ACCESO AUTORIZADO', 'Placa inválida (3 letras y 3 o 4 dígitos).'],
    expected: ['Cor *', 'Marca *', 'Imagens', 'ACESSO AUTORIZADO', 'Placa inválida (3 letras e 3 ou 4 dígitos).'],
    dynamic: ['A placa PBA-8901 agora está na lista BLANCA.', 'Guarita 4 adicionada.', '3 guarita(s) atualizada(s).', 'Confirmando a mesma placa: 1/2 quadros', 'Preencha os campos obrigatórios: marca, modelo'],
  },
  fr: {
    texts: ['Color *', 'Marca *', 'Imágenes', 'ACCESO AUTORIZADO', 'Placa inválida (3 letras y 3 o 4 dígitos).'],
    expected: ['Couleur *', 'Marque *', 'Images', 'ACCÈS AUTORISÉ', 'Plaque invalide (3 lettres et 3 ou 4 chiffres).'],
    dynamic: ['La plaque PBA-8901 est maintenant dans la liste BLANCA.', 'Poste de contrôle 4 ajouté.', '3 poste(s) de contrôle mis à jour.', 'Confirmation de la même plaque : 1/2 images', 'Renseignez les champs obligatoires : marca, modelo'],
  },
}

test('main screens read in Portuguese and French', () => {
  const initial = language.value
  try {
    for (const locale of ['pt', 'fr']) {
      setLanguage(locale)
      assert.deepEqual(samples[locale].texts.map(t), samples[locale].expected, locale)
      const spanish = [
        'La placa PBA-8901 ahora está en la lista BLANCA.',
        'Garita 4 agregada.',
        '3 garita(s) actualizada(s).',
        'Confirmando la misma placa: 1/2 cuadros',
        'Complete los campos obligatorios: marca, modelo',
      ]
      assert.deepEqual(spanish.map(t), samples[locale].dynamic, locale)
    }
  } finally {
    setLanguage(initial)
  }
})

test('main screens read in German', () => {
  const initial = language.value
  try {
    setLanguage('de')
    assert.ok(!/^(Color|Make) \*$/.test(t('Color *')), 'Color * translated')
    for (const key of ['Imágenes', 'ACCESO AUTORIZADO', 'Placa inválida (3 letras y 3 o 4 dígitos).', 'Los videos y cámaras se analizan cada segundo hasta confirmar una placa válida con al menos 94 % de confianza OCR. Si un video termina sin placa confirmada, no se repite: la detección espera 15 segundos adicionales y luego se detiene para validación manual.']) {
      assert.notEqual(t(key), messages.en[key], key)
      assert.notEqual(t(key), key, key)
    }
    // Messages with a variable part.
    const plate = t('La placa PBA-8901 ahora está en la lista BLANCA.')
    assert.ok(plate.includes('PBA-8901') && plate.includes('BLANCA') && !/ now |\bis\b/.test(plate), plate)
    const confirming = t('Confirmando la misma placa: 1/2 cuadros')
    assert.ok(confirming.includes('1/2') && !/frames|Confirming/.test(confirming), confirming)
  } finally {
    setLanguage(initial)
  }
})

test('the English interface keeps its messages with a variable part', () => {
  const initial = language.value
  try {
    setLanguage('en')
    assert.equal(t('Garita 4 agregada.'), 'Checkpoint 4 added.')
  } finally {
    setLanguage(initial)
  }
})
