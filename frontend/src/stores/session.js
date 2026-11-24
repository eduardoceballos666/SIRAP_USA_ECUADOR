import { defineStore } from 'pinia'
import { api } from '@/lib/api'
import { localeTag } from '@/i18n'
import { COUNTRY_KEY, initialCountry } from '@/lib/defaultCountry'

const THEME_KEY = 'sirap_theme'

function initialTheme() {
  try {
    const saved = localStorage.getItem(THEME_KEY)
    if (saved === 'dark' || saved === 'light') return saved
  } catch { /* sin almacenamiento */ }

  return 'light'
}

// Estado del puesto de control: garita y movimiento elegidos, datos del sistema, tema, avisos y
// las lecturas hechas en esta sesión (para compararlas; no se guardan en el servidor hasta que se registran).
export const useSessionStore = defineStore('session', {
  state: () => ({
    system: null,
    country: initialCountry(), // EE. UU. por defecto; Ecuador solo si ya se eligió en este navegador
    garita: null,
    movimiento: 'ENTRADA',
    toasts: [],
    theme: initialTheme(),
    lecturas: [],
  }),
  actions: {
    async loadSystem(force = false) {
      if (this.system?.country === this.country && !force) return this.system
      const country = this.country
      const result = await api('/api/system', { params: { country } })
      if (this.country !== country) return this.system
      this.system = result
      if (!this.garita || !this.system.garitas.includes(this.garita)) {
        this.garita = this.system.garitas.find((g) => g.includes('3')) || this.system.garitas[0] || null
      }
      return this.system
    },
    rememberCountry() {
      try { localStorage.setItem(COUNTRY_KEY, this.country) } catch { /* sin almacenamiento */ }
    },
    notify(message, kind = 'ok') {
      const id = Date.now() + Math.random()
      this.toasts.push({ id, message, kind })
      setTimeout(() => { this.toasts = this.toasts.filter((t) => t.id !== id) }, 4500)
    },
    applyTheme() {
      document.documentElement.classList.toggle('dark', this.theme === 'dark')
    },
    toggleTheme() {
      this.theme = this.theme === 'dark' ? 'light' : 'dark'
      try { localStorage.setItem(THEME_KEY, this.theme) } catch { /* sin almacenamiento */ }
      this.applyTheme()
    },
    addLectura(lectura) {
      const country = lectura.country || this.country
      this.lecturas.unshift({ id: Date.now() + Math.random(), hora: new Date().toLocaleTimeString(localeTag.value),
        country, jurisdiction: null, identity_key: country === 'ecuador' ? lectura.placa || '' : '', ...lectura })
      this.lecturas = this.lecturas.slice(0, 50)
    },
    markRegistered(id, accion) {
      const l = this.lecturas.find((x) => x.id === id)
      if (l) l.registro = accion
    },
    clearUnregisteredLecturas(ids) {
      const targets = new Set(ids)
      this.lecturas = this.lecturas.filter((l) => !targets.has(l.id) || l.registro)
    },
    clearLecturas() {
      this.lecturas = []
    },
  },
})

