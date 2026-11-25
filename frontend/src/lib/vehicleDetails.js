// Vehicle-details panel of the United States interface: which value fills which label.
//
// The names mirror the J.D. Power columns produced by section 23.2 of
// notebooks/usa/sirap_backend_usa.ipynb (pd.json_normalize(..., sep="_")):
//   "Year and model" <- vehicle_title       (heading of the report, e.g. "2013 Honda Civic")
//   "Color"          <- specs_exterior      (Overview > Exterior, e.g. "Taffeta White")
//   "Body type"      <- vehicle_body_type   (line under the heading, e.g. "Sedan 4D LX I4")
//   "State"          <- state               (issuing state code, e.g. "CA")
// The local registry (anio + marca + modelo, color) is only a fallback for the first two.

import { US_STATES } from './plateIdentity.js'

const text = (value) => (value === null || value === undefined ? '' : String(value).trim())
const first = (...values) => values.map(text).find(Boolean) || ''

// Why J.D. Power gave no data, by `fuentes.jdpower` of /api/plates/vehicle-data (statuses of api/providers/usa_jdpower.py).
// Every message ends by saying that the local data is shown; the first sentence names the cause so it can be acted on.
const LOOKUP_FAILURES = [
  [/^access_limited_(401|403)$/, 'J.D. Power no permite el acceso desde este servidor (acceso denegado). No se reintenta ni se evita; se muestran los datos locales disponibles.'],
  [/^access_limited_429$/, 'J.D. Power limitó las consultas (demasiadas solicitudes). No se reintenta; inténtelo más tarde. Se muestran los datos locales disponibles.'],
  [/^browser_unavailable$/, 'El navegador que consulta a J.D. Power no está disponible en el servidor; se muestran los datos locales disponibles.'],
  [/^(no_response|http_\d+)$/, 'J.D. Power no respondió o devolvió un error; se muestran los datos locales disponibles.'],
  [/^(form_failed|report_not_ready|no_report_title)$/, 'J.D. Power no mostró un informe para esta placa y este estado; revise que ambos sean correctos. Se muestran los datos locales disponibles.'],
  [/^error$/, 'La consulta a J.D. Power falló por un error del servidor; se muestran los datos locales disponibles.'],
  [/^invalid_input$/, 'La placa o el estado no son válidos para consultar a J.D. Power; se muestran los datos locales disponibles.'],
]

// Status line under the panel once the server answered; `jdpower` is fuentes.jdpower of /api/plates/vehicle-data.
export function usaLookupStatus(jdpower) {
  if (jdpower === 'encontrado') return 'Datos de J.D. Power y del registro local de USA.'
  if (!jdpower || jdpower === 'desactivado') return 'Datos del registro local de USA.'
  const failure = LOOKUP_FAILURES.find(([pattern]) => pattern.test(String(jdpower)))
  return failure ? failure[1] : 'J.D. Power no devolvió datos; se muestran los datos locales disponibles.'
}

export function usaVehicleDetails({ lookup, vehicle, jurisdiction, plate } = {}) {
  const empty = { yearModel: '', color: '', bodyType: '', state: '' }
  if (!text(plate)) return empty
  const pick = (...keys) => first(...[lookup, vehicle].flatMap((source) => keys.map((key) => source?.[key])))
  const localYearModel = [pick('anio', 'year'), pick('marca', 'make'), pick('modelo', 'model')].filter(Boolean).join(' ')
  return {
    yearModel: pick('vehicle_title') || localYearModel,
    color: pick('specs_exterior') || pick('color'),
    bodyType: pick('vehicle_body_type'),
    state: (pick('state', 'jurisdiction') || text(jurisdiction)).toUpperCase(),
  }
}

// Public J.D. Power report page for a plate and state. The person opens it in their own browser tab to read it
// themselves; the server never uses this link. Same address as `report_url` in api/providers/usa_jdpower.py.
export function jdPowerReportUrl(plate, jurisdiction) {
  const serial = text(plate).toUpperCase().replace(/[^A-Z0-9]/g, '')
  const state = text(jurisdiction).toUpperCase()
  if (!serial || !Object.hasOwn(US_STATES, state)) return ''
  return `https://www.jdpower.com/cars/license-plate-lookup-and-decoder/${serial.toLowerCase()}-${state.toLowerCase()}-license-plate-report`
}
