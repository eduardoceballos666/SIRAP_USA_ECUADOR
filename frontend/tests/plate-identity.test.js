import assert from 'node:assert/strict'
import test from 'node:test'
import { US_STATES, plateKey, profilePayload, automaticUSAReadingAllowed } from '../src/lib/plateIdentity.js'

test('USA identities preserve characters and distinguish states from Ecuador', () => {
  assert.equal(Object.keys(US_STATES).length, 51)
  assert.equal(plateKey('01I-OB8', 'usa', 'CA'), 'US:CA:01IOB8')
  assert.notEqual(plateKey('ABC1234', 'usa', 'CA'), plateKey('ABC1234', 'usa', 'NY'))
  assert.notEqual(plateKey('ABC1234', 'usa', 'CA'), plateKey('ABC1234', 'ecuador'))
  assert.equal(plateKey('ABC1234', 'usa', ''), '')
  assert.deepEqual(profilePayload('ecuador', 'CA'), { country: 'ecuador', jurisdiction: null })
  assert.deepEqual(profilePayload('usa', 'ny'), { country: 'usa', jurisdiction: 'NY' })
})

test('automatic USA action requires server evidence and unchanged state/serial', () => {
  const reading = { country: 'usa', plate: 'DEMO123', jurisdiction: 'CA', ocr_confidence: .94,
    det_confidence: .70, evidence_id: 'server-evidence', temporal_confirmed: true, confirmation_frames: 2 }
  assert.equal(automaticUSAReadingAllowed(reading, 'DEMO123', 'CA'), true)
  for (const change of [{ evidence_id: null }, { temporal_confirmed: false }, { confirmation_frames: 1 },
    { ocr_confidence: .939999 }, { det_confidence: .699999 }, { jurisdiction: null }, { ocr_confidence: NaN }]) {
    assert.equal(automaticUSAReadingAllowed({ ...reading, ...change }, 'DEMO123', 'CA'), false)
  }
  assert.equal(automaticUSAReadingAllowed(reading, 'DEMO123', 'NY'), false)
  assert.equal(automaticUSAReadingAllowed(reading, 'DEMO124', 'CA'), false)
})
