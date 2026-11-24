export const US_STATES = {
  AL:'Alabama', AK:'Alaska', AZ:'Arizona', AR:'Arkansas', CA:'California', CO:'Colorado', CT:'Connecticut',
  DE:'Delaware', FL:'Florida', GA:'Georgia', HI:'Hawaii', ID:'Idaho', IL:'Illinois', IN:'Indiana', IA:'Iowa',
  KS:'Kansas', KY:'Kentucky', LA:'Louisiana', ME:'Maine', MD:'Maryland', MA:'Massachusetts', MI:'Michigan',
  MN:'Minnesota', MS:'Mississippi', MO:'Missouri', MT:'Montana', NE:'Nebraska', NV:'Nevada', NH:'New Hampshire',
  NJ:'New Jersey', NM:'New Mexico', NY:'New York', NC:'North Carolina', ND:'North Dakota', OH:'Ohio',
  OK:'Oklahoma', OR:'Oregon', PA:'Pennsylvania', RI:'Rhode Island', SC:'South Carolina', SD:'South Dakota',
  TN:'Tennessee', TX:'Texas', UT:'Utah', VT:'Vermont', VA:'Virginia', WA:'Washington', WV:'West Virginia',
  WI:'Wisconsin', WY:'Wyoming', DC:'District of Columbia',
}

export function profilePayload(country, jurisdiction) {
  if (!['ecuador', 'usa'].includes(country)) throw new Error('País inválido.')
  return { country, jurisdiction: country === 'usa' ? String(jurisdiction || '').toUpperCase() || null : null }
}

// Plate and state exactly as the two boxes show them: these are the two fields sent to J.D. Power.
// Returns null while either one is missing, so no lookup is started with half of the identity.
export function usaLookupInputs(country, plate, jurisdiction) {
  const serial = String(plate || '').toUpperCase().replace(/[^A-Z0-9]/g, '')
  const state = String(jurisdiction || '').toUpperCase()
  if (country !== 'usa' || !serial || !Object.hasOwn(US_STATES, state)) return null
  return { plate: serial, jurisdiction: state }
}

export function plateKey(plate, country = 'ecuador', jurisdiction = null) {
  const serial = String(plate || '').toUpperCase().replace(/[^A-Z0-9]/g, '')
  if (!serial) return ''
  if (country === 'usa') {
    const state = String(jurisdiction || '').toUpperCase()
    return US_STATES[state] ? `US:${state}:${serial}` : ''
  }
  return country === 'ecuador' ? `EC:${serial}` : ''
}

export function automaticUSAReadingAllowed(reading, editedPlate, editedState) {
  return reading?.country === 'usa' && Boolean(reading.evidence_id) && reading.temporal_confirmed === true &&
    Number(reading.confirmation_frames) >= 2 && Number.isFinite(reading.ocr_confidence) &&
    reading.ocr_confidence >= .94 && Number.isFinite(reading.det_confidence) && reading.det_confidence >= .70 &&
    Boolean(plateKey(reading.plate, 'usa', reading.jurisdiction)) &&
    plateKey(reading.plate, 'usa', reading.jurisdiction) === plateKey(editedPlate, 'usa', editedState)
}
