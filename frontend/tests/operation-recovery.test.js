import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test from 'node:test'
import vm from 'node:vm'
import { pendingOperationKey, readPendingOperation, startPendingOperation, clearPendingOperation,
  recoverPendingOperation, cancelUnacceptedOperation, operationIsSettled } from '../src/lib/operationRecovery.js'
import { api, ApiError } from '../src/lib/api.js'

const scope = { usuario: 'synthetic-operator', country: 'usa' }
const ID = '00000000-0000-4000-8000-000000000001'
const OTHER_ID = '00000000-0000-4000-8000-000000000002'
const context = { operacion_id: ID, accion: 'APERTURA_MANUAL', garita: 'Synthetic Gate', tipo_movimiento: 'ENTRADA' }
const status = (state = 'CONFIRMADA') => ({ operacion_id: ID, country: 'usa', accion: 'APERTURA_MANUAL',
  estado_barrera: state, requiere_revision: ['SOLICITADA', 'INDETERMINADA'].includes(state), mensaje: state })

class MemoryStorage {
  values = new Map()
  getItem(key) { return this.values.get(key) ?? null }
  setItem(key, value) { this.values.set(key, String(value)) }
  removeItem(key) { this.values.delete(key) }
}

test('a reload retains the original ID and recovery uses only a status GET', async () => {
  const storage = new MemoryStorage()
  await startPendingOperation(scope, context, { storage })
  const restarted = new MemoryStorage()
  restarted.values = new Map(storage.values)
  assert.equal(readPendingOperation(scope, restarted).operacion_id, ID)
  const requests = []
  const recovered = await recoverPendingOperation(scope, async (path, options) => {
    requests.push({ path, method: options.method || 'GET' })
    return status()
  }, restarted)
  assert.equal(recovered.result.estado_barrera, 'CONFIRMADA')
  assert.deepEqual(requests, [{ path: `/api/operations/${ID}/status`, method: 'GET' }])
  assert.equal(readPendingOperation(scope, restarted), null)
})

test('an unknown outcome survives connection loss, reconnection and another page load', async () => {
  const storage = new MemoryStorage()
  await startPendingOperation(scope, context, { storage })
  await assert.rejects(recoverPendingOperation(scope, async () => { throw new ApiError(0, 'offline') }, storage))
  for (const state of ['SOLICITADA', 'INDETERMINADA']) {
    const out = await recoverPendingOperation(scope, async () => status(state), storage)
    assert.equal(operationIsSettled(out.result), false)
    assert.equal(readPendingOperation(scope, storage).operacion_id, ID)
  }
})

test('404 is not proof of cancellation and does not discard the original ID', async () => {
  const storage = new MemoryStorage()
  await startPendingOperation(scope, context, { storage })
  await assert.rejects(recoverPendingOperation(scope, async () => { throw new ApiError(404, 'missing') }, storage))
  assert.equal(readPendingOperation(scope, storage).operacion_id, ID)
  const reserved = await startPendingOperation(scope, { ...context, operacion_id: OTHER_ID }, { storage })
  assert.equal(reserved.reused, true)
  assert.equal(reserved.attempt.operacion_id, ID)
})

test('explicit cancellation sends the same ID and clears it only after a durable result', async () => {
  const storage = new MemoryStorage()
  await startPendingOperation(scope, context, { storage })
  const requests = []
  const request = async (path, options) => { requests.push({ path, options }); return status('CANCELADA') }
  await cancelUnacceptedOperation(scope, request, storage)
  assert.equal(requests[0].path, `/api/operations/${ID}/cancel`)
  assert.equal(requests[0].options.method, 'POST')
  assert.equal(requests[0].options.body.accion_solicitada, 'APERTURA_MANUAL')
  assert.equal(readPendingOperation(scope, storage), null)
})

test('cancellation cannot hide an operation the server has already accepted', async () => {
  const storage = new MemoryStorage()
  await startPendingOperation(scope, context, { storage })
  const out = await cancelUnacceptedOperation(scope, async () => status('SOLICITADA'), storage)
  assert.equal(out.result.requiere_revision, true)
  assert.equal(readPendingOperation(scope, storage).operacion_id, ID)
})

test('simultaneous reservations keep one ID and no plate, image, OCR or token', async () => {
  const storage = new MemoryStorage()
  const extra = { ...context, placa: 'PRIVATE123', token: 'private-test-token', image: 'private-image' }
  const attempts = await Promise.all([
    startPendingOperation(scope, extra, { storage }),
    startPendingOperation(scope, { ...context, operacion_id: OTHER_ID }, { storage }),
  ])
  assert.equal(attempts.filter(x => !x.reused).length, 1)
  assert.ok(attempts.every(x => x.attempt.operacion_id === ID))
  const saved = storage.getItem(pendingOperationKey(scope))
  assert.ok(!saved.includes('PRIVATE123') && !saved.includes('private-test-token') && !saved.includes('private-image'))
})

test('account/country scope and compare-before-clear protect another pending request', async () => {
  const storage = new MemoryStorage()
  await startPendingOperation(scope, context, { storage })
  assert.equal(readPendingOperation({ ...scope, usuario: 'other' }, storage), null)
  assert.equal(readPendingOperation({ ...scope, country: 'ecuador' }, storage), null)
  assert.equal(clearPendingOperation(scope, OTHER_ID, storage), false)
  await assert.rejects(recoverPendingOperation(scope, async () => ({ ...status(), country: 'ecuador' }), storage))
  assert.equal(readPendingOperation(scope, storage).operacion_id, ID)
})

test('unavailable or corrupt local storage fails before a command can be sent', async () => {
  const storage = new MemoryStorage()
  storage.setItem = () => { throw new Error('quota') }
  await assert.rejects(startPendingOperation(scope, context, { storage }), /No se envió la orden/)
  const corrupt = new MemoryStorage()
  corrupt.setItem(pendingOperationKey(scope), '{broken')
  await assert.rejects(startPendingOperation(scope, context, { storage: corrupt }), /Revise el historial/)
  assert.equal(corrupt.getItem(pendingOperationKey(scope)), '{broken')
})

async function componentHarness(t, request, storage) {
  const source = await readFile(new URL('../src/views/RecognitionView.vue', import.meta.url), 'utf8')
  const definitions = [
    source.match(/^function operationScope\(\) \{.*\}$/m)?.[0],
    source.match(/^async function recoverOperation\(\) \{[\s\S]*?^\}/m)?.[0],
    source.match(/^async function register\(accion\) \{[\s\S]*?^\}/m)?.[0],
  ]
  assert.ok(definitions.every(Boolean))
  const oldStorage = globalThis.localStorage
  globalThis.localStorage = storage
  t.after(() => { globalThis.localStorage = oldStorage })
  const ref = value => ({ value })
  const sandbox = { busy: ref(false), loading: ref(false), recoveryBusy: ref(false),
    recoveryBlocked: ref(false), pendingAttempt: ref(null), recoveryMissing: ref(false), recoveryMessage: ref(''),
    decision: ref({ permite_apertura: true }), operationAttemptId: ref(null), done: ref(false),
    origin: ref('MANUAL'), recognition: ref(null), manualJurisdiction: ref('CA'), plateShown: ref('DEMO123'),
    motivo: ref('Synthetic recovery verification'), manualOpen: ref(false), lecturaId: ref(1),
    auth: { user: { usuario: scope.usuario } },
    session: { country: 'usa', garita: context.garita, movimiento: 'ENTRADA', notify() {}, markRegistered() {} },
    crypto: { randomUUID: () => ID }, profilePayload: (country, jurisdiction) => ({ country, jurisdiction }),
    readPendingOperation, startPendingOperation, clearPendingOperation, recoverPendingOperation,
    operationIsSettled, api: request, nextTick: async () => {}, clearCurrentReading() {},
    setTimeout: callback => { callback(); return 1 },
  }
  const realm = vm.createContext(sandbox)
  vm.runInContext(definitions.join('\n'), realm)
  return sandbox
}

test('the actual Vue register handler recovers a lost response without a second POST', async t => {
  const storage = new MemoryStorage()
  const requests = []
  const state = await componentHarness(t, async (path, options = {}) => {
    requests.push({ path, method: options.method || 'GET' })
    if (path === '/api/operations') throw new ApiError(0, 'Synthetic response lost after acceptance')
    return status()
  }, storage)
  await state.register('APERTURA_MANUAL')
  assert.deepEqual(requests.map(x => x.method), ['POST', 'GET'])
  assert.equal(state.done.value, true)
  assert.equal(state.recoveryBlocked.value, false)
  assert.equal(readPendingOperation(scope, storage), null)
})

test('after a reload the actual Vue handler queries an uncertain attempt and refuses to reopen', async t => {
  const storage = new MemoryStorage()
  await startPendingOperation(scope, context, { storage })
  const requests = []
  const state = await componentHarness(t, async (path, options = {}) => {
    requests.push(options.method || 'GET'); return status('SOLICITADA')
  }, storage)
  await state.recoverOperation()
  await state.register('APERTURA_MANUAL')
  assert.deepEqual(requests, ['GET', 'GET'])
  assert.equal(state.recoveryBlocked.value, true)
  assert.equal(readPendingOperation(scope, storage).operacion_id, ID)
})

test('a recovered confirmation consumes the current action and a second click cannot post', async t => {
  const storage = new MemoryStorage()
  await startPendingOperation(scope, context, { storage })
  const requests = []
  const state = await componentHarness(t, async (path, options = {}) => {
    requests.push(options.method || 'GET'); return status('CONFIRMADA')
  }, storage)
  // A click beats the page's initial recovery callback; it must reuse the old ID.
  await state.register('APERTURA_MANUAL')
  await state.register('APERTURA_MANUAL')
  assert.deepEqual(requests, ['GET'])
  assert.equal(state.done.value, true)
  assert.equal(state.operationAttemptId.value, null)
})

test('the actual Vue handler never posts when the attempt ID cannot be persisted', async t => {
  const storage = new MemoryStorage(); storage.setItem = () => { throw new Error('quota') }
  let requests = 0
  const state = await componentHarness(t, async () => { requests++; return status() }, storage)
  await state.register('APERTURA_MANUAL')
  assert.equal(requests, 0)
})

test('HTTP timeout, invalid response and service-unavailable errors never retry a POST', async t => {
  const old = { window: globalThis.window, fetch: globalThis.fetch, localStorage: globalThis.localStorage }
  t.after(() => Object.assign(globalThis, old))
  globalThis.window = { location: { origin: 'https://synthetic.invalid' } }
  globalThis.localStorage = new MemoryStorage()
  let requests = 0
  globalThis.fetch = (_url, options) => {
    requests++
    assert.equal(options.cache, 'no-store')
    return new Promise((_, reject) => options.signal.addEventListener('abort', () => reject(new Error('timeout'))))
  }
  await assert.rejects(api('/api/operations', { method: 'POST', body: {}, timeoutMs: 5 }), e => e.status === 0)
  assert.equal(requests, 1)
  globalThis.fetch = async () => { requests++; return { status: 200, ok: true, json() { throw new SyntaxError() } } }
  await assert.rejects(api('/api/operations', { method: 'POST', body: {} }), e => e.status === 0)
  assert.equal(requests, 2)
  globalThis.fetch = async () => { requests++; return { status: 503, ok: false, json: async () => ({ detail: 'offline' }) } }
  await assert.rejects(api('/api/operations', { method: 'POST', body: {} }), e => e.status === 503)
  assert.equal(requests, 3)
})
