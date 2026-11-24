// Country profile a browser starts with: the United States, unless the person already chose Ecuador there.
// `storage` is injectable for tests; without it the browser's localStorage is used (and may throw or be absent).
export const COUNTRY_KEY = 'sirap_country'

export function initialCountry(storage) {
  try {
    const store = storage ?? localStorage
    return store.getItem(COUNTRY_KEY) === 'ecuador' ? 'ecuador' : 'usa'
  } catch {
    return 'usa'
  }
}
