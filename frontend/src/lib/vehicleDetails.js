// Vehicle-details panel of the United States interface: which value fills which label.
//
// The names mirror the J.D. Power columns produced by section 23.2 of
// notebooks/usa/sirap_backend_usa.ipynb (pd.json_normalize(..., sep="_")):
//   "Year and model" <- vehicle_title       (heading of the report, e.g. "2013 Honda Civic")
//   "Color"          <- specs_exterior      (Overview > Exterior, e.g. "Taffeta White")
//   "Body type"      <- vehicle_body_type   (line under the heading, e.g. "Sedan 4D LX I4")
//   "State"          <- state               (issuing state code, e.g. "CA")
// The local registry (anio + marca + modelo, color) is only a fallback for the first two.

const text = (value) => (value === null || value === undefined ? '' : String(value).trim())
const first = (...values) => values.map(text).find(Boolean) || ''

// Status line under the panel once the server answered; `jdpower` is fuentes.jdpower of /api/plates/vehicle-data.
export function usaLookupStatus(jdpower) {
  if (jdpower === 'encontrado') return 'Datos de J.D. Power y del registro local de Estados Unidos.'
  if (!jdpower || jdpower === 'desactivado') return 'Datos del registro local de Estados Unidos.'
  return 'J.D. Power no devolvió datos; se muestran los datos locales disponibles.'
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
