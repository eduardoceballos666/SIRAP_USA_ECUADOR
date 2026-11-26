import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { language, setLanguage, t } from '../src/i18n.js'

// A user name is data: the Administration table must show the name that is typed at login,
// not a translation of it ("operador" used to appear as "operator", "opérateur", "Bediener").
const usernames = ['operador', 'supervisor', 'admin']

test('user names are not translated in any language', () => {
  const initial = language.value
  try {
    for (const locale of ['es', 'en', 'pt', 'fr', 'de', 'it']) {
      setLanguage(locale)
      assert.deepEqual(usernames.map(t), usernames, locale)
    }
  } finally {
    setLanguage(initial)
  }
})

test('the Administration table prints the user name without translating it', () => {
  const admin = readFileSync(new URL('../src/views/AdminView.vue', import.meta.url), 'utf8')
  assert.ok(admin.includes("{{ c === 'usuario' ? fmt(r[c]) : $t(fmt(r[c])) }}"))
})
