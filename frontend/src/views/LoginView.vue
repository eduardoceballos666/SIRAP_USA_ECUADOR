<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import SirapLogo from '@/components/SirapLogo.vue'
import { useAuthStore } from '@/stores/auth'
import { useSessionStore } from '@/stores/session'
import LanguageSwitcher from '@/components/LanguageSwitcher.vue'
import { language } from '@/i18n'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const session = useSessionStore()
const country = ref(['usa', 'ecuador'].includes(route.query.country) ? route.query.country : session.country)
const usuario = ref('operador')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(usuario.value, password.value, country.value, language.value)
    router.push({ name: 'recognition', params: { country: country.value } })
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="grid min-h-screen place-items-center bg-navy-900 p-4">
    <div class="w-full max-w-md">
      <SirapLogo class="mb-6" />
      <form class="card space-y-4" @submit.prevent="submit">
        <h1 class="text-xl font-bold">{{ $t("Iniciar sesión") }}</h1>
        <div class="login-profile-fields grid grid-cols-2 gap-3">
          <LanguageSwitcher />
          <div><label class="field-label" for="login-country">{{ $t('País') }}</label>
            <select id="login-country" v-model="country" class="field" :disabled="loading" required>
              <option value="ecuador">{{ $t('Ecuador') }}</option><option value="usa">{{ $t('Estados Unidos') }}</option>
            </select>
          </div>
        </div>
        <div>
          <label class="field-label" for="u">{{ $t("Usuario") }}</label>
          <input id="u" v-model.trim="usuario" class="field" autocomplete="username" required />
        </div>
        <div>
          <label class="field-label" for="p">{{ $t("Contraseña") }}</label>
          <input id="p" v-model="password" type="password" class="field" autocomplete="current-password" required />
        </div>
        <p v-if="error" class="rounded-lg bg-bad-soft px-3 py-2 text-sm font-semibold text-bad">{{ $t(error) }}</p>
        <button class="btn-primary w-full" :disabled="loading">{{ $t(loading ? 'Ingresando…' : 'Ingresar') }}</button>
        <p class="text-xs text-muted">
          {{ $t("Usuarios de demostración:") }} <b>{{ $t("operador") }}</b>{{ $t(",") }} <b>{{ $t("supervisor") }}</b> {{ $t("y") }} <b>{{ $t("admin") }}</b>{{ $t(". La contraseña de demostración\n          se define con") }} <code>{{ $t("SIRAP_DEMO_PASSWORD") }}</code> {{ $t("en el servidor.") }}
        </p>
      </form>
    </div>
  </div>
</template>

