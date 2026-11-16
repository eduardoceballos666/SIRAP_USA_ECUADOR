// Keep only the attempt ID/context, never a plate, image, token or OCR payload.
const PREFIX = 'sirap_pending_operation_v1:'
const UUID = /^[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}$/i
const ACTIONS = ['APERTURA_AUTOMATICA', 'APERTURA_MANUAL', 'SOLO_REGISTRO', 'RECHAZO']
const SETTLED = ['CONFIRMADA', 'FALLIDA', 'CANCELADA', 'NO_APLICA']

export function pendingOperationKey(scope) {
  if (!scope?.usuario || !['usa', 'ecuador'].includes(scope.country)) {
    throw new Error('Inicie sesión para recuperar la operación pendiente.')
  }
  return PREFIX + encodeURIComponent(scope.country) + ':' + encodeURIComponent(scope.usuario)
}

export function readPendingOperation(scope, storage = globalThis.localStorage) {
  const key = pendingOperationKey(scope)
  try {
    const raw = storage.getItem(key)
    if (!raw) return null
    const entry = JSON.parse(raw)
    if (entry.version !== 1 || entry.usuario !== scope.usuario || entry.country !== scope.country ||
        !UUID.test(entry.operacion_id) || !entry.garita ||
        !['ENTRADA', 'SALIDA'].includes(entry.tipo_movimiento) || !ACTIONS.includes(entry.accion)) throw new Error()
    return entry
  } catch {
    // Losing/corrupting an ID does not prove that the command was never received.
    throw new Error('No se puede recuperar el identificador pendiente. Revise el historial antes de abrir otra vez.')
  }
}

export async function startPendingOperation(scope, context, { storage = globalThis.localStorage,
  locks = globalThis.navigator?.locks } = {}) {
  const key = pendingOperationKey(scope)
  const reserve = () => {
    const existing = readPendingOperation(scope, storage)
    if (existing) return { attempt: existing, reused: true }
    if (!UUID.test(context.operacion_id) || !context.garita || !ACTIONS.includes(context.accion) ||
        !['ENTRADA', 'SALIDA'].includes(context.tipo_movimiento)) throw new Error('Contexto de operación inválido.')
    const attempt = { version: 1, usuario: scope.usuario, country: scope.country,
      operacion_id: context.operacion_id, accion: context.accion, garita: context.garita,
      tipo_movimiento: context.tipo_movimiento, created_at: new Date().toISOString() }
    try {
      storage.setItem(key, JSON.stringify(attempt))
      if (readPendingOperation(scope, storage)?.operacion_id !== attempt.operacion_id) throw new Error()
    } catch {
      throw new Error('No se pudo conservar el identificador de la operación. No se envió la orden.')
    }
    return { attempt, reused: false }
  }
  if (!locks?.request) return reserve()
  // Settle the lock callback normally even when storage fails, then report the
  // error outside the lock. A rejected callback must not strand another tab.
  const outcome = await locks.request(key, () => {
    try { return { value: reserve() } } catch (error) { return { error } }
  })
  if (outcome.error) throw outcome.error
  return outcome.value
}

export function clearPendingOperation(scope, id, storage = globalThis.localStorage) {
  const entry = readPendingOperation(scope, storage)
  if (entry?.operacion_id !== id) return false
  storage.removeItem(pendingOperationKey(scope))
  return true
}

export function operationIsSettled(result) {
  return Boolean(result && !result.requiere_revision && SETTLED.includes(result.estado_barrera))
}

export async function recoverPendingOperation(scope, request, storage = globalThis.localStorage) {
  const attempt = readPendingOperation(scope, storage)
  if (!attempt) return { attempt: null, result: null }
  // Recovery is read-only, including page reload and the browser's online event.
  const result = await request(`/api/operations/${attempt.operacion_id}/status`, {
    params: { country: scope.country }, timeoutMs: 25000,
  })
  if (result.operacion_id !== attempt.operacion_id || result.country !== scope.country) {
    throw new Error('La respuesta no corresponde a la operación pendiente.')
  }
  if (operationIsSettled(result)) clearPendingOperation(scope, attempt.operacion_id, storage)
  return { attempt, result }
}

export async function cancelUnacceptedOperation(scope, request, storage = globalThis.localStorage) {
  const attempt = readPendingOperation(scope, storage)
  if (!attempt) return { attempt: null, result: null }
  // Explicit user action only. The server either reserves this UUID as cancelled
  // or returns the already accepted operation; it never sends an opening command.
  const result = await request(`/api/operations/${attempt.operacion_id}/cancel`, {
    method: 'POST', timeoutMs: 30000, body: { country: scope.country,
      garita: attempt.garita, tipo_movimiento: attempt.tipo_movimiento, accion_solicitada: attempt.accion },
  })
  if (result.operacion_id !== attempt.operacion_id || result.country !== scope.country) {
    throw new Error('La respuesta no corresponde a la operación pendiente.')
  }
  if (operationIsSettled(result)) clearPendingOperation(scope, attempt.operacion_id, storage)
  return { attempt, result }
}
