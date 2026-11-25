import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { language, setLanguage, t } from '../src/i18n.js'
import { ECUADOR_FLAG, USA_FLAG, USA_STAR_RADIUS, flagSize, starPoints, usaStarCenters } from '../src/lib/flags.js'

const source = (path) => readFileSync(new URL(path, import.meta.url), 'utf8')

test('the United States flag keeps the official proportions', () => {
  assert.equal(USA_FLAG.width / USA_FLAG.height, 1.9)
  assert.equal(USA_FLAG.stripes, 13)
  assert.ok(Math.abs(USA_FLAG.cantonHeight - (USA_FLAG.height * 7) / 13) < 1e-9)
  assert.equal(USA_FLAG.cantonWidth / USA_FLAG.height, 0.76)
})

test('fifty stars in nine rows of six and five, inside the canton and mirrored left to right', () => {
  const stars = usaStarCenters()
  assert.equal(stars.length, 50)
  const rows = new Map()
  for (const { x, y } of stars) rows.set(y, [...(rows.get(y) || []), x])
  assert.deepEqual([...rows.values()].map((xs) => xs.length), [6, 5, 6, 5, 6, 5, 6, 5, 6])
  for (const { x, y } of stars) {
    assert.ok(x - USA_STAR_RADIUS > 0 && x + USA_STAR_RADIUS < USA_FLAG.cantonWidth, `x ${x}`)
    assert.ok(y - USA_STAR_RADIUS > 0 && y + USA_STAR_RADIUS < USA_FLAG.cantonHeight, `y ${y}`)
  }
  for (const xs of rows.values()) {
    xs.forEach((x, i) => assert.ok(Math.abs(x + xs[xs.length - 1 - i] - USA_FLAG.cantonWidth) < 1e-9))
  }
})

test('a star has ten points and its first one looks straight up', () => {
  const points = starPoints(10, 20, 4).split(' ').map((pair) => pair.split(',').map(Number))
  assert.equal(points.length, 10)
  assert.deepEqual(points[0], [10, 16])
  assert.ok(points.every(([x, y]) => Number.isFinite(x) && Number.isFinite(y)))
})

test('Ecuador is 3:2 and every other profile falls back to the United States flag', () => {
  assert.equal(ECUADOR_FLAG.width / ECUADOR_FLAG.height, 1.5)
  assert.equal(flagSize('ecuador'), ECUADOR_FLAG)
  assert.equal(flagSize('usa'), USA_FLAG)
  assert.equal(flagSize(undefined), USA_FLAG)
})

test('the sidebar shows the waving flag of the active country and the control strip a still one', () => {
  const app = source('../src/App.vue')
  assert.match(app, /import CountryFlag from '@\/components\/CountryFlag\.vue'/)
  const waving = app.match(/<div class="sidebar-flag"><CountryFlag :country="session\.country" waving \/><\/div>/)
  assert.ok(waving, 'sidebar flag missing')
  // between the module links and the "About the model" block
  assert.ok(app.indexOf('</nav>') < app.indexOf('class="sidebar-flag"') && app.indexOf('class="sidebar-flag"') < app.indexOf('class="sidebar-bottom"'))

  const view = source('../src/views/RecognitionView.vue')
  assert.match(view, /import CountryFlag from '@\/components\/CountryFlag\.vue'/)
  const strip = view.match(/<div id="country" class="control-field">.*<\/div>/)
  assert.ok(strip, 'country field missing')
  assert.match(strip[0], /<CountryFlag class="country-flag-simple" :country="session\.country" \/>/)
  assert.doesNotMatch(strip[0], /waving/)
})

test('the flag component draws both countries, moves only when motion is allowed, and is labelled', () => {
  const flag = source('../src/components/CountryFlag.vue')
  assert.match(flag, /props\.country === 'ecuador'/)
  assert.match(flag, /prefers-reduced-motion: reduce/)
  assert.match(flag, /role="img"/)
  assert.match(flag, /:aria-label="\$t\(label\)"/)
  assert.doesNotMatch(flag, /<image\b|\.png|\.jpe?g|https?:\/\/(?!www\.w3\.org\/2000\/svg)/, 'the flags are drawn inline, with no image files or network')
  const css = source('../src/style.css')
  assert.match(css, /@media \(max-height:740px\) \{ \.sidebar-flag \{ display:none; \} \}/)
  const initial = language.value
  try {
    for (const locale of ['en', 'pt', 'fr', 'de', 'it']) {
      setLanguage(locale)
      for (const label of ['Bandera de Ecuador', 'Bandera de Estados Unidos']) {
        assert.notEqual(t(label), label, `${locale} ${label}`)
      }
    }
  } finally {
    setLanguage(initial)
  }
})

test('the login screen shows a small flag beside the country selector from the first paint', () => {
  const login = source('../src/views/LoginView.vue')
  assert.match(login, /import CountryFlag from '@\/components\/CountryFlag\.vue'/)
  const row = login.match(/<div class="login-country-row">[\s\S]*?<\/div>/)
  assert.ok(row, 'country row missing')
  assert.match(row[0], /<select id="login-country" v-model="country"/)
  assert.match(row[0], /<CountryFlag class="login-country-flag" :country="country" \/>/)
  // The flag follows the same reactive value as the selector (the remembered country, or ?country=), so it needs no extra step to appear.
  assert.match(login, /const country = ref\(\['usa', 'ecuador'\]\.includes\(route\.query\.country\) \? route\.query\.country : session\.country\)/)
  assert.doesNotMatch(row[0], /v-if|onMounted|nextTick/)
})

test('a browser with no saved choice starts in the United States, in English; a saved Ecuador is kept', async () => {
  const { COUNTRY_KEY, initialCountry } = await import('../src/lib/defaultCountry.js')
  const storage = (value) => ({ getItem: (key) => (key === COUNTRY_KEY ? value : null) })
  assert.equal(initialCountry(storage(null)), 'usa')
  assert.equal(initialCountry(storage('usa')), 'usa')
  assert.equal(initialCountry(storage('ecuador')), 'ecuador')
  assert.equal(initialCountry(storage('brasil')), 'usa')
  assert.equal(initialCountry({ getItem() { throw new Error('blocked') } }), 'usa')
  assert.equal(initialCountry(), 'usa') // Node has no localStorage: it falls back to the United States
  // English is already the language of a browser with nothing saved (i18n.js), and the store uses this default.
  assert.equal(language.value, 'en')
  assert.match(source('../src/stores/session.js'), /country: initialCountry\(\)/)
  assert.match(source('../src/stores/session.js'), /import \{ COUNTRY_KEY, initialCountry \} from '@\/lib\/defaultCountry'/)
})

test('the login screen has no demo-users hint and names the United States "USA" in English', () => {
  const login = source('../src/views/LoginView.vue')
  assert.doesNotMatch(login, /SIRAP_DEMO_PASSWORD|Usuarios de demostración/)
  assert.match(login, /<option value="usa">\{\{ language === 'en' \? 'USA' : \$t\('Estados Unidos'\) \}\}<\/option>/)
  // the other screens keep the full name
  setLanguage('en')
  assert.equal(t('Estados Unidos'), 'United States')
  setLanguage('es')
  assert.equal(t('Estados Unidos'), 'Estados Unidos')
})
