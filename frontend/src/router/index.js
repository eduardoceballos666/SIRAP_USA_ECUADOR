import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { setUnauthorizedHandler } from '@/lib/api'
import { useSessionStore } from '@/stores/session'

const pages = [
  { path: 'reconocimiento', name: 'recognition', component: () => import('@/views/RecognitionView.vue'),
    meta: { title: 'Reconocimiento automático y control de acceso' } },
  { path: 'dashboard', name: 'dashboard', component: () => import('@/views/DashboardView.vue'),
    meta: { title: 'Dashboard de operaciones' } },
  { path: 'historial', name: 'history', component: () => import('@/views/HistoryView.vue'),
    meta: { title: 'Historial de operaciones' } },
  { path: 'administracion', name: 'admin', component: () => import('@/views/AdminView.vue'),
    meta: { title: 'Administración', roles: ['ADMINISTRADOR', 'SUPERVISOR'] } },
  { path: 'modelo', name: 'about', component: () => import('@/views/AboutView.vue'),
    meta: { title: 'Acerca del modelo' } },
]

const selectedCountry = () => useAuthStore().user?.country || useSessionStore().country
const routes = [
  { path: '/login', name: 'login', component: () => import('@/views/LoginView.vue'), meta: { public: true, title: 'Iniciar sesión' } },
  { path: '/:country(usa|ecuador)', children: [
    { path: '', redirect: (to) => ({ name: 'recognition', params: { country: to.params.country } }) }, ...pages,
  ] },
  ...pages.map((page) => ({ path: '/' + page.path, redirect: () => ({ name: page.name, params: { country: selectedCountry() } }) })),
  { path: '/:pathMatch(.*)*', redirect: () => ({ name: 'recognition', params: { country: selectedCountry() } }) },
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  if (to.meta.public) return auth.isAuthenticated && to.name === 'login'
    ? { name: 'recognition', params: { country: selectedCountry() } } : true
  if (!auth.isAuthenticated) return { name: 'login', query: { next: to.fullPath, country: to.params.country || selectedCountry() } }
  try {
    await auth.fetchMe()
  } catch {
    auth.logout()
    return { name: 'login' }
  }
  if (to.params.country && to.params.country !== auth.user.country) {
    return { name: to.name, params: { ...to.params, country: auth.user.country }, query: to.query }
  }
  if (to.meta.roles && !auth.hasRole(...to.meta.roles)) return { name: 'recognition', params: { country: selectedCountry() } }
  document.title = `SIRAP_USA_ECUADOR_HF · ${to.meta.title || 'Control de acceso'}`
  return true
})

setUnauthorizedHandler(() => {
  useAuthStore().logout()
  router.push({ name: 'login' })
})

export default router

