import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { language, setLanguage, t } from '../src/i18n.js'
import {
  ECUADOR_FLAG, USA_FLAG, USA_STAR_RADIUS, WAVES_ALONG_FLAG, flagSize, starPoints, usaStarCenters, waveStrips,
} from '../src/lib/flags.js'

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
  // The United States flag is inline vector; Ecuador's is the official artwork, an image that ships with the app: nothing is fetched from the network.
  assert.match(flag, /import ecuadorFlagUrl from '@\/assets\/flags\/ecuador\.webp'/)
  assert.match(flag, /<image :href="ecuadorFlagUrl" width="150" height="100"/)
  assert.doesNotMatch(flag, /https?:\/\/(?!www\.w3\.org\/2000\/svg)/, 'no network address')
  assert.doesNotMatch(flag, /EcuadorCoatOfArms/, 'the coat of arms is the official one, not a hand-drawn copy')
  const css = source('../src/style.css')
  assert.match(css, /@media \(max-height:740px\) \{ \.sidebar-flag \{ display:none; \} \}/)
  const initial = language.value
  try {
    for (const locale of ['en', 'pt', 'fr', 'de', 'it']) {
      setLanguage(locale)
      for (const label of ['Bandera de Ecuador', 'Bandera de Estados Unidos de América']) {
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

test('the login screen has no demo-users hint and lists the country by its translated name', () => {
  const login = source('../src/views/LoginView.vue')
  assert.doesNotMatch(login, /SIRAP_DEMO_PASSWORD|Usuarios de demostración/)
  assert.match(login, /<option value="usa">\{\{ \$t\('Estados Unidos'\) \}\}<\/option>/)
})

test('"USA" names the United States in every language, for the key and for the country code', () => {
  const initial = language.value
  try {
    for (const locale of ['en', 'es', 'pt', 'fr', 'de', 'it']) {
      setLanguage(locale)
      assert.equal(t('Estados Unidos'), 'USA', locale)
      assert.equal(t('usa'), 'USA', locale)
      assert.equal(t('USA'), 'USA', locale)
    }
  } finally {
    setLanguage(initial)
  }
})

test('the official Ecuador flag ships as a 3:2 image, with its source and licence recorded', () => {
  const file = readFileSync(new URL('../src/assets/flags/ecuador.webp', import.meta.url))
  assert.equal(file.toString('latin1', 0, 4), 'RIFF')
  assert.equal(file.toString('latin1', 8, 12), 'WEBP')
  assert.ok(file.length > 5_000 && file.length < 200_000, `size ${file.length}`)
  // VP8 (lossy) key frame: width and height are 14-bit values at bytes 26-29
  assert.equal(file.toString('latin1', 12, 16), 'VP8 ')
  const width = file.readUInt16LE(26) & 0x3fff
  const height = file.readUInt16LE(28) & 0x3fff
  assert.equal(width / height, ECUADOR_FLAG.width / ECUADOR_FLAG.height)
  const notices = readFileSync(new URL('../../THIRD_PARTY_NOTICES.md', import.meta.url), 'utf8')
  assert.match(notices, /frontend\/src\/assets\/flags\/ecuador\.webp/)
  assert.match(notices, /Wikimedia Commons/)
})

test('the waving flag is cut into strips that follow one wave, calm at the hoist and wide at the free end', () => {
  const width = ECUADOR_FLAG.width
  const strips = waveStrips(80, width)
  assert.equal(strips.length, 80)
  assert.equal(waveStrips(2, width).length, 8, 'at least eight strips')
  strips.forEach((strip, i) => {
    assert.equal(strip.i, i)
    if (i > 0) {
      const previous = strips[i - 1]
      assert.ok(previous.x + previous.width > strip.x, 'neighbouring strips overlap, so no gap shows')
      assert.ok(strip.amplitude > previous.amplitude && strip.phase > previous.phase && strip.tilt > previous.tilt)
    }
  })
  const [first, last] = [strips[0], strips[strips.length - 1]]
  assert.ok(first.x === 0 && Math.abs(last.x + (last.width - 0.7) - width) < 1e-9, 'the strips cover the whole flag')
  assert.ok(first.amplitude < 1.2 && last.amplitude > 3.5 && last.amplitude < 4.5)
  assert.ok(last.phase < WAVES_ALONG_FLAG && last.phase > WAVES_ALONG_FLAG * 0.98)
  // the tilt is the slope of the wave there: amplitude x 2 pi x waves per unit of length, as an angle
  const slope = (last.amplitude * 2 * Math.PI * WAVES_ALONG_FLAG) / width
  assert.ok(Math.abs(Math.tan((last.tilt * Math.PI) / 180) - slope) < 1e-9)
  assert.ok(last.tilt > 5 && last.tilt < 20, `tilt ${last.tilt}`)
  assert.ok(strips.every((strip) => strip.shade > 0 && strip.shade < 0.3 && strip.light > 0 && strip.light < 0.2))
})

test('the strips are cut once on their own layer, so no seam shows, and the shade is painted wider than the cut', () => {
  const flag = source('../src/components/CountryFlag.vue')
  assert.match(flag, /\.flag-cut \{ opacity:\.999; \}/)
  assert.match(flag, /class="flag-shade" :x="strip\.x - 2" y="0" :width="strip\.width \+ 4"/)
  // reduced motion freezes the wave in place instead of flattening or hiding the flag
  assert.match(flag, /prefers-reduced-motion: reduce\) \{[^}]*animation-play-state:paused/)
})
