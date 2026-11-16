import test from 'node:test'
import assert from 'node:assert/strict'
import { language, setLanguage, t } from '../src/i18n.js'

test('country codes render localized labels without replacing canonical Spanish names', () => {
  const initial = language.value
  try {
    for (const [locale, country, usa, ecuador] of [
      ['es', 'País', 'Estados Unidos', 'Ecuador'],
      ['en', 'Country', 'United States', 'Ecuador'],
      ['pt', 'País', 'Estados Unidos', 'Equador'],
      ['fr', 'Pays', 'États-Unis', 'Équateur'],
      ['de', 'Land', 'Vereinigte Staaten', 'Ecuador'],
      ['it', 'Paese', 'Stati Uniti', 'Ecuador'],
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
