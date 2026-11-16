<script setup>
import { useId } from 'vue'
import { US_STATES } from '@/lib/plateIdentity'
defineProps({ country: { type: String, default: 'ecuador' }, jurisdiction: { type: String, default: '' }, disabled: Boolean, lockCountry: Boolean })
const emit = defineEmits(['update:country', 'update:jurisdiction'])
const id = useId()
function changeCountry(event) {
  emit('update:country', event.target.value)
  emit('update:jurisdiction', '')
}
</script>

<template>
  <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
    <div><label class="field-label" :for="id + '-country'">{{ $t('País') }}</label>
      <select :id="id + '-country'" :value="country" class="field" :disabled="disabled || lockCountry" @change="changeCountry">
        <option value="ecuador">{{ $t('Ecuador') }}</option><option value="usa">{{ $t('Estados Unidos') }}</option>
      </select></div>
    <div v-if="country === 'usa'"><label class="field-label" :for="id + '-state'">{{ $t('Estado emisor') }}</label>
      <select :id="id + '-state'" :value="jurisdiction" class="field" :disabled="disabled" required @change="emit('update:jurisdiction', $event.target.value)">
        <option value="">{{ $t('Seleccione estado emisor') }}</option>
        <option v-for="(name, code) in US_STATES" :key="code" :value="code">{{ code }} · {{ name }}</option>
      </select></div>
  </div>
</template>
