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
