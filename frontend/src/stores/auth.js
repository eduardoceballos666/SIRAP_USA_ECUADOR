import { defineStore } from 'pinia'
import { api, getToken, setToken } from '@/lib/api'
import { useSessionStore } from '@/stores/session'

export const useAuthStore = defineStore('auth', {
  state: () => ({ token: getToken(), user: null }),
  getters: {
    isAuthenticated: (s) => Boolean(s.token),
    role: (s) => s.user?.rol,
  },
  actions: {
    async login(usuario, password, country = 'ecuador', language = 'en') {
      const data = await api('/api/auth/login', { method: 'POST', body: { usuario, password, country, language } })
      this.token = data.access_token
      this.user = data.user
      setToken(this.token)
      this.applyCountry()
    },
    async fetchMe() {
      if (!this.token || this.user) return
      this.user = await api('/api/auth/me')
      this.applyCountry()
    },
    applyCountry() {
      const session = useSessionStore()
      session.country = this.user?.country || 'ecuador'
      session.system = null
      session.rememberCountry()
    },
    logout() {
      this.token = null
      this.user = null
      setToken(null)
      const session = useSessionStore()
      session.system = null
      session.clearLecturas()
    },
    hasRole(...roles) {
      return roles.includes(this.user?.rol)
    },
  },
})

