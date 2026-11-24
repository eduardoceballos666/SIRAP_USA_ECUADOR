import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test from 'node:test'
import { usaLookupInputs } from '../src/lib/plateIdentity.js'

test('J.D. Power receives the plate and the state exactly as the two boxes show them', () => {
  assert.deepEqual(usaLookupInputs('usa', '6zgy-984', 'ca'), { plate: '6ZGY984', jurisdiction: 'CA' })
  assert.deepEqual(usaLookupInputs('usa', 'ABC 123', 'DC'), { plate: 'ABC123', jurisdiction: 'DC' })
})

test('no lookup starts with only half of the identity or outside the United States profile', () => {
  assert.equal(usaLookupInputs('usa', '6ZGY984', ''), null, 'sin estado')
  assert.equal(usaLookupInputs('usa', '', 'CA'), null, 'sin placa')
  assert.equal(usaLookupInputs('usa', '6ZGY984', 'ZZ'), null, 'estado inexistente')
  assert.equal(usaLookupInputs('ecuador', 'PBA-8901', 'CA'), null, 'Ecuador no consulta J.D. Power')
})

test('choosing the state by hand starts the lookup only on a user change of the select', async () => {
  const source = await readFile(new URL('../src/views/RecognitionView.vue', import.meta.url), 'utf8')
  assert.match(source, /<select id="manual-jurisdiction"[^>]*@change="onStateChosen"/, 'El cambio hecho por la persona dispara la consulta')
  const handler = source.match(/function onStateChosen\(\) \{([\s\S]*?)\n\}\n/)
  assert.ok(handler, 'Debe existir onStateChosen')
  assert.match(handler[1], /usaLookupInputs\(session\.country, manualPlate\.value \|\| plateShown\.value, manualJurisdiction\.value\)/)
  assert.match(handler[1], /loading\.value \|\| busy\.value/, 'No consulta mientras se procesa otra lectura')
  assert.match(handler[1], /loadVehicleDetails\(query\.plate\)/)
  // El OCR ya consulta por su cuenta; un watcher sobre la casilla duplicaría la consulta a J.D. Power.
  assert.doesNotMatch(source, /watch\(manualJurisdiction/)
})
