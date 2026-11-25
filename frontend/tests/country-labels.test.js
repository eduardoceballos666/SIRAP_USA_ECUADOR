import test from 'node:test'
import assert from 'node:assert/strict'
import { language, setLanguage, t } from '../src/i18n.js'

test('the United States profile is labelled "USA" in every language and Ecuador keeps its localized name', () => {
  const initial = language.value
  try {
    for (const [locale, country, usa, ecuador] of [
      ['es', 'País', 'USA', 'Ecuador'],
      ['en', 'Country', 'USA', 'Ecuador'],
      ['pt', 'País', 'USA', 'Equador'],
      ['fr', 'Pays', 'USA', 'Équateur'],
      ['de', 'Land', 'USA', 'Ecuador'],
      ['it', 'Paese', 'USA', 'Ecuador'],
    ]) {
      setLanguage(locale)
      assert.equal(t('country'), country)
      assert.equal(t('usa'), usa)
      assert.equal(t('ecuador'), ecuador)
    }
    setLanguage('es')
    assert.equal(t('Ecuador'), 'Ecuador')
    assert.equal(t('jurisdiction'), 'Estado emisor')
  } finally {
    setLanguage(initial)
  }
})

test('sentences spell out the full country name, while the short labels stay "USA"', () => {
  const initial = language.value
  const full = {
    es: 'Estados Unidos de América', en: 'United States of America', pt: 'Estados Unidos da América',
    fr: 'États-Unis d’Amérique', de: 'Vereinigten Staaten von Amerika', it: 'Stati Uniti d’America',
  }
  try {
    for (const locale of ['en', 'es', 'pt', 'fr', 'de', 'it']) {
      setLanguage(locale)
      assert.equal(t('usa'), 'USA', locale)
      for (const key of ['Datos del registro local de Estados Unidos de América.', 'Seleccione el estado emisor de la placa de Estados Unidos de América.', 'Bandera de Estados Unidos de América']) {
        assert.ok(t(key).includes(full[locale]), `${locale}: ${key} -> ${t(key)}`)
      }
    }
  } finally {
    setLanguage(initial)
  }
})
