<script setup>
import { language, setLanguage } from '@/i18n'

function changeLanguage(event) {
  setLanguage(event.target.value)
}
</script>

<template>
  <label class="language-switcher">
    <span>{{ $t('Idioma') }}</span>
    <select :value="language" :aria-label="$t('Idioma')" @change="changeLanguage">
      <option value="en">English</option>
      <option value="es">Español</option>
      <option value="pt">Português (Brasil)</option>
      <option value="fr">Français</option>
      <option value="de">Deutsch</option>
    </select>
  </label>
</template>
