<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { api } from '@/lib/api'
import AppIcon from '@/components/AppIcon.vue'
import { num, pct } from '@/lib/format'
import { t } from '@/i18n'
import { useSessionStore } from '@/stores/session'

const session = useSessionStore()
const info = ref(null)
async function loadProfileInfo() {
  info.value = null
  try { info.value = await api('/api/model/info', { params: { country: session.country } }) }
  catch (e) { session.notify(e.message, 'bad') }
}
onMounted(loadProfileInfo)
watch(() => session.country, loadProfileInfo)
const isUSA = computed(() => session.country === 'usa')
const development = computed(() => info.value?.metricas?.development)
const counts = computed(() => development.value?.counts || {})
const cards = computed(() => [
  { label: t('País'), value: t(session.country), sub: t('Misma interfaz y mismos pesos para ambos países.') },
  { label: t('Detector RT-DETRv2-S'), value: 'OpenVINO', sub: t('Semilla 2 compartida') },
  { label: t('Umbral del detector'), value: num(info.value?.umbral_detector, 2), sub: t('Configuración operativa actual') },
  { label: t('Umbral OCR'), value: pct(info.value?.umbral_ocr, 0), sub: t('Probabilidad mínima por carácter') },
])
</script>

<template>
  <section class="card mb-5" aria-labelledby="developers-heading">
    <h2 id="developers-heading" class="card-title">{{ $t('Desarrolladores') }}</h2>
    <div class="space-y-4 leading-snug break-words">
      <div><p class="text-2xl font-bold sm:text-3xl">Eduardo Alejandro Ceballos Jijon</p>
        <a href="mailto:eduardoceballos@yahoo.com" class="mt-1 inline-block text-brand-600 hover:underline">eduardoceballos@yahoo.com</a></div>
      <div><p class="text-2xl font-bold sm:text-3xl">Christian Xavier Valle Maridueña</p>
        <a href="mailto:cvalle130781@gmail.com" class="mt-1 inline-block text-brand-600 hover:underline">cvalle130781@gmail.com</a></div>
    </div>
  </section>
  <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
    <div v-for="card in cards" :key="card.label" class="card">
      <p class="text-sm font-semibold text-muted">{{ card.label }}</p>
      <p class="mt-1 text-3xl font-black">{{ card.value }}</p>
      <p class="mt-1 text-sm text-muted">{{ card.sub }}</p>
    </div>
  </div>
  <div class="mt-5 grid gap-5 xl:grid-cols-2">
    <section class="card space-y-3 leading-relaxed">
      <h2 class="card-title">{{ $t('Cómo funciona') }}</h2>
      <p>{{ $t('El país y el idioma se eligen al iniciar sesión. El reconocimiento, las listas y el historial usan ese país.') }}</p>
      <p>{{ $t('Ambos países usan el detector entrenado para USA y el mismo OCR global, sin reentrenamiento.') }}</p>
      <p v-if="isUSA">{{ $t('USA conserva letras y números y exige estado emisor más matrícula para identificar un vehículo.') }}</p>
      <p v-else>{{ $t('Ecuador aplica su formato de matrícula, por ejemplo ABC-1234, sin exigir un estado emisor.') }}</p>
      <p v-if="isUSA">{{ $t('La apertura normal requiere lista blanca vigente y dos cuadros distintos confirmados por el servidor en 7,5 segundos.') }}</p>
      <p>{{ $t('Cada operación queda en el historial con usuario, garita y hora. La barrera configurada es simulada.') }}</p>
    </section>
    <section class="card space-y-3 leading-relaxed">
      <h2 class="card-title">{{ $t('Entrenamiento y validación') }}</h2>
      <p v-if="!isUSA">{{ $t('El rendimiento del checkpoint compartido con placas ecuatorianas está pendiente de evaluación.') }}</p>
      <template v-else-if="development">
        <p>{{ $t('Diagnóstico de desarrollo con ocho fotos reutilizadas; no es un test final independiente.') }}</p>
        <table class="w-full text-sm"><tbody>
          <tr><th class="py-2 text-left">{{ $t('Imágenes') }}</th><td>{{ counts.source_images }}</td></tr>
          <tr><th class="py-2 text-left">{{ $t('Matrículas exactas entre las detectadas') }}</th><td>{{ counts.serial_exact }} / {{ counts.known_serials }}</td></tr>
          <tr><th class="py-2 text-left">{{ $t('Estados correctos entre los conocidos') }}</th><td>{{ counts.state_exact }} / {{ counts.known_states }}</td></tr>
          <tr><th class="py-2 text-left">{{ $t('Escenas con referencia completa') }}</th><td>{{ counts.complete_scenes }}</td></tr>
          <tr><th class="py-2 text-left">{{ $t('Placas detectadas / omitidas') }}</th><td>{{ counts.complete_scene_tp }} / {{ counts.complete_scene_fn }}</td></tr>
        </tbody></table>
        <p class="text-sm text-muted">{{ $t('Una imagen conserva una región dudosa; queda fuera del recuento por escenas completas.') }}</p>
      </template>
      <p>{{ $t('Cambiar reglas OCR no equivale a entrenar un modelo para otro país.') }}</p>
    </section>
    <section class="card space-y-3 leading-relaxed xl:col-span-2 border-l-4 border-warn">
      <h2 class="card-title"><span class="icon-chip !bg-warn"><AppIcon name="alert" /></span> {{ $t('Limitaciones y advertencias') }}</h2>
      <p>{{ $t('Los estados desconocidos, las lecturas incompletas y las confianzas bajas requieren revisión manual.') }}</p>
      <p>{{ $t('Las pruebas del software comprueban reglas y persistencia con una barrera simulada; no miden la exactitud real del modelo.') }}</p>
    </section>
    <section class="card space-y-3 leading-relaxed xl:col-span-2">
      <h2 class="card-title"><span class="icon-chip"><AppIcon name="info" /></span> {{ $t('Licencia del software') }}</h2>
      <p>{{ $t('El código original de SIRAP_USA_ECUADOR se distribuye bajo Apache License 2.0. Los modelos y recursos de terceros mantienen sus propias licencias.') }}</p>
      <p><a class="underline" href="https://github.com/eduardoceballos666/SIRAP_USA_ECUADOR" target="_blank" rel="noopener noreferrer">{{ $t('Código fuente') }}</a>
        · <a class="underline" href="https://github.com/eduardoceballos666/SIRAP_USA_ECUADOR/blob/main/LICENSE" target="_blank" rel="noopener noreferrer">{{ $t('Licencia Apache-2.0') }}</a></p>
    </section>
  </div>
</template>
