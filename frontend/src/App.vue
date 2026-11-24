<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppIcon from '@/components/AppIcon.vue'
import SirapLogo from '@/components/SirapLogo.vue'
import ToastStack from '@/components/ToastStack.vue'
import LanguageSwitcher from '@/components/LanguageSwitcher.vue'
import CountryFlag from '@/components/CountryFlag.vue'
import { language, localeTag, t } from '@/i18n'
import { useAuthStore } from '@/stores/auth'
import { useSessionStore } from '@/stores/session'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const session = useSessionStore()
const now = ref(new Date())
let timer
onMounted(() => { timer = setInterval(() => (now.value = new Date()), 1000) })
onBeforeUnmount(() => clearInterval(timer))

const items = computed(() => [
  { name: 'recognition', label: 'Reconocimiento y Acceso', icon: 'scan' },
  { name: 'history', label: 'Historial', icon: 'history' },
  { name: 'admin', label: 'Administración', icon: 'settings', roles: ['ADMINISTRADOR', 'SUPERVISOR'] },
  { name: 'dashboard', label: 'Dashboard', icon: 'dashboard' },
].filter((i) => !i.roles || auth.hasRole(...i.roles)).map((i) => ({ ...i, to: { name: i.name, params: { country: session.country } } })))

const clock = computed(() => now.value.toLocaleString(localeTag.value, { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' }))
const isPublic = computed(() => route.meta.public)
const roleLabel = { OPERADOR: 'Operador', SUPERVISOR: 'Supervisor', ADMINISTRADOR: 'Administrador' }

watch([language, route], () => {
  document.title = `SIRAP_USA_ECUADOR_HF · ${t(route.meta.title || (isPublic.value ? 'Iniciar sesión' : 'Control de acceso'))}`
}, { immediate: true })

function logout() {
  auth.logout()
  router.push({ name: 'login' })
}
function switchCountry() {
  const country = session.country === 'usa' ? 'ecuador' : 'usa'
  auth.logout()
  router.push({ name: 'login', query: { country } })
}
</script>

<template>
  <div v-if="isPublic" class="public-shell">
    <RouterView />
  </div>
  <div v-else class="app-shell">
    <aside class="app-topbar" :aria-label='$t("Navegación principal")'>
      <RouterLink :to="{ name: 'recognition', params: { country: session.country } }" class="sidebar-brand" :aria-label='$t("SIRAP_USA_ECUADOR_HF: reconocimiento")'><SirapLogo /></RouterLink>
      <LanguageSwitcher />
      <button class="country-profile-button" :title="$t('Cambiar país')" @click="switchCountry">{{ $t(session.country) }}</button>
      <nav class="top-navigation" :aria-label='$t("Módulos")'>
        <RouterLink v-for="i in items" :key="i.name" :to="i.to" active-class="selected"><AppIcon :name="i.icon" :size="19" /><span>{{ $t(i.label) }}</span></RouterLink>
      </nav>
      <div class="sidebar-flag"><CountryFlag :country="session.country" waving /></div>
      <div class="sidebar-bottom">
        <RouterLink :to="{ name: 'about', params: { country: session.country } }" class="about-link" active-class="selected"><AppIcon name="info" :size="19" /><span>{{ $t("Acerca del modelo") }}</span></RouterLink>
        <div class="top-user">
          <span class="user-name" :title="$t(roleLabel[auth.user?.rol])">{{ auth.user?.nombre }} {{ $t("·") }} {{ $t(roleLabel[auth.user?.rol]) }}</span>
          <button :aria-label="$t(session.theme === 'dark' ? 'Cambiar a tema claro' : 'Cambiar a tema oscuro')" @click="session.toggleTheme()"><AppIcon :name="session.theme === 'dark' ? 'sun' : 'moon'" :size="17" /></button>
          <button :title='$t("Cerrar sesión")' :aria-label='$t("Cerrar sesión")' @click="logout"><AppIcon name="logout" :size="17" /></button>
        </div>
      </div>
    </aside>
    <main class="app-content" :class="{ 'access-content': route.name === 'recognition' }">
      <header v-if="route.name !== 'recognition'" class="page-heading"><h1>{{ $t(route.meta.title) }}</h1><span>{{ clock }}</span></header>
      <RouterView />
    </main>
  </div>
  <ToastStack />
</template>

