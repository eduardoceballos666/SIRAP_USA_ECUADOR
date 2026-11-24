<script>
let nextFlagId = 0
</script>

<script setup>
// Flag of the active country profile. `waving` draws it on a pole and animates it (the sidebar); without it the
// flag is a plain still picture (the control strip). Drawn as inline SVG, so it needs no image files.
import { computed } from 'vue'
import { FLAG_COLORS as C, FLAG_SIZES, USA_FLAG, USA_STAR_RADIUS, starPoints, usaStarCenters } from '@/lib/flags'

const props = defineProps({
  country: { type: String, required: true },
  waving: { type: Boolean, default: false },
  strips: { type: Number, default: 40 },
})

const uid = `flag${(nextFlagId += 1)}`
const isEcuador = computed(() => props.country === 'ecuador')
const size = computed(() => FLAG_SIZES[isEcuador.value ? 'ecuador' : 'usa'])
const label = computed(() => (isEcuador.value ? 'Bandera de Ecuador' : 'Bandera de Estados Unidos'))
const viewBox = computed(() => {
  const { width, height } = size.value
  return props.waving ? `-6 -10 ${width + 9} ${height + 20}` : `0 0 ${width} ${height}`
})
const stripeHeight = USA_FLAG.height / USA_FLAG.stripes
const redStripes = Array.from({ length: 7 }, (_, i) => i * 2 * stripeHeight)
const stars = usaStarCenters().map(({ x, y }) => starPoints(x, y, USA_STAR_RADIUS))
const waves = computed(() => {
  const count = Math.max(8, props.strips)
  const width = size.value.width / count
  return Array.from({ length: count }, (_, i) => ({
    i,
    x: i * width,
    width: width + 0.7, // a little overlap, so no hairline shows between neighbours
    amplitude: (0.7 + (2.5 * i) / (count - 1)).toFixed(2), // calm at the pole, wider towards the free end
    phase: ((i / count) * 1.35).toFixed(3), // 1.35 waves along the flag
  }))
})
</script>

<template>
  <svg
    class="country-flag" :class="{ 'is-waving': waving }" :viewBox="viewBox" role="img" :aria-label="$t(label)"
    xmlns="http://www.w3.org/2000/svg" focusable="false"
  >
    <defs>
      <g :id="`${uid}-art`">
        <template v-if="isEcuador">
          <rect width="150" height="50" :fill="C.ecuadorYellow" />
          <rect y="50" width="150" height="25" :fill="C.ecuadorBlue" />
          <rect y="75" width="150" height="25" :fill="C.ecuadorRed" />
          <!-- Coat of arms, simplified: condor, shield (sun, Chimborazo, the Guayas with its steamship), flags, fasces, laurel -->
          <g transform="translate(57 26.5) scale(.36)">
            <g v-for="mirrored in [false, true]" :key="mirrored" :transform="mirrored ? 'translate(100 0) scale(-1 1)' : ''">
              <g transform="rotate(-14 22 72)">
                <line x1="22" y1="40" x2="22" y2="106" stroke="#6b4a2b" stroke-width="1.8" />
                <rect x="3" y="42" width="19" height="7" :fill="C.ecuadorYellow" />
                <rect x="3" y="49" width="19" height="3.5" :fill="C.ecuadorBlue" />
                <rect x="3" y="52.5" width="19" height="3.5" :fill="C.ecuadorRed" />
              </g>
              <path d="M44 112 C28 106 19 92 21 74" fill="none" stroke="#3f8f3a" stroke-width="2.4" stroke-linecap="round" />
              <ellipse cx="21" cy="84" rx="1.8" ry="3.4" transform="rotate(-25 21 84)" fill="#3f8f3a" />
              <ellipse cx="24" cy="97" rx="1.8" ry="3.4" transform="rotate(-50 24 97)" fill="#3f8f3a" />
              <ellipse cx="33" cy="106" rx="1.8" ry="3.4" transform="rotate(-75 33 106)" fill="#3f8f3a" />
              <path d="M52 22 C60 12 74 8 95 12 L90 16 L97 19 L89 22 L95 27 L86 28 L90 33 L78 32 C68 34 58 34 52 32 Z" fill="#3b2a1d" />
              <path d="M58 22 C67 19 78 18 89 19" fill="none" stroke="#e8e2d4" stroke-width="1.4" stroke-linecap="round" />
            </g>
            <path d="M47 33 L50 46 L53 33 Z" fill="#3b2a1d" />
            <ellipse cx="50" cy="27" rx="5.5" ry="9" fill="#3b2a1d" />
            <ellipse cx="50" cy="17.5" rx="4.4" ry="2.2" fill="#f1ede4" />
            <circle cx="50" cy="13.5" r="3.4" fill="#8b5e4b" />
            <path d="M52.6 12.4 L56 14 L53.2 15.4 Z" fill="#d9d2c0" />
            <rect x="48.2" y="96" width="3.6" height="19" fill="#8a5a2b" />
            <rect x="47.4" y="101" width="5.2" height="1.6" fill="#5a3a1c" />
            <rect x="47.4" y="107" width="5.2" height="1.6" fill="#5a3a1c" />
            <ellipse cx="50" cy="70" rx="25" ry="32" fill="#8ec5ee" />
            <g :clip-path="`url(#${uid}-shield)`">
              <rect x="20" y="42" width="60" height="60" fill="#8ec5ee" />
              <polygon points="27,72 40,53 53,72" fill="#6d7a86" />
              <polygon points="40,53 36.5,60 43.5,60" fill="#ffffff" />
              <circle cx="58" cy="52" r="6.2" fill="#f6b800" />
              <circle cx="58" cy="52" r="3.9" fill="#ffd54a" />
              <circle cx="58" cy="52" r="9.6" fill="none" stroke="#c58a00" stroke-width="1.8" stroke-dasharray="2 1.5" />
              <rect x="20" y="70" width="60" height="40" fill="#4f9a3e" />
              <path d="M44 70 Q55 84 46 104 L66 104 Q70 84 58 70 Z" fill="#3b7fc4" />
              <path d="M55 86 L66 86 L63.6 90 L57.4 90 Z" fill="#6b4a2b" />
              <path d="M60.4 78 L60.4 86 M60.4 79 L65 85 L60.4 85" fill="#ffffff" stroke="#6b4a2b" stroke-width=".7" />
            </g>
            <ellipse cx="50" cy="70" rx="25" ry="32" fill="none" stroke="#d49a0b" stroke-width="2.6" />
          </g>
        </template>
        <template v-else>
          <rect :width="USA_FLAG.width" :height="USA_FLAG.height" :fill="C.white" />
          <rect v-for="y in redStripes" :key="y" :y="y" :width="USA_FLAG.width" :height="stripeHeight" :fill="C.usaRed" />
          <rect :width="USA_FLAG.cantonWidth" :height="USA_FLAG.cantonHeight" :fill="C.usaBlue" />
          <polygon v-for="points in stars" :key="points" :points="points" :fill="C.white" />
        </template>
      </g>
      <clipPath :id="`${uid}-shield`"><ellipse cx="50" cy="70" rx="23.5" ry="30.5" /></clipPath>
      <linearGradient :id="`${uid}-pole`" x1="0" x2="1" y1="0" y2="0">
        <stop offset="0" stop-color="#9aa4b2" /><stop offset=".45" stop-color="#f3f6fa" /><stop offset="1" stop-color="#7d8896" />
      </linearGradient>
      <clipPath v-for="strip in waves" :key="strip.i" :id="`${uid}-c${strip.i}`">
        <rect :x="strip.x" y="-20" :width="strip.width" :height="size.height + 40" />
      </clipPath>
    </defs>

    <template v-if="waving">
      <g
        v-for="strip in waves" :key="strip.i" class="flag-strip"
        :style="{ '--amp': strip.amplitude, '--phase': strip.phase }"
      >
        <g :clip-path="`url(#${uid}-c${strip.i})`">
          <use :href="`#${uid}-art`" />
          <rect class="flag-shade" :x="strip.x" y="0" :width="strip.width" :height="size.height" fill="#000" />
        </g>
      </g>
      <rect x="-5.2" y="-9" width="3.2" :height="size.height + 19" rx="1.6" :fill="`url(#${uid}-pole)`" />
      <circle cx="-3.6" cy="-8.6" r="2.4" fill="#f2c230" />
    </template>
    <template v-else>
      <use :href="`#${uid}-art`" />
      <rect class="flag-outline" :width="size.width" :height="size.height" fill="none" />
    </template>
  </svg>
</template>

<style scoped>
.country-flag { display:block; overflow:visible; }
.flag-outline { stroke:rgb(255 255 255 / .55); stroke-width:1; vector-effect:non-scaling-stroke; }
.is-waving { --period:3.2s; }
.flag-strip {
  transform:translateY(calc(var(--amp) * -1px));
  animation:flag-wave var(--period) ease-in-out infinite;
  animation-delay:calc(var(--phase) * var(--period) * -1);
}
.flag-shade {
  opacity:0;
  animation:flag-shade var(--period) ease-in-out infinite;
  animation-delay:calc((var(--phase) + .25) * var(--period) * -1);
}
@keyframes flag-wave {
  0%, 100% { transform:translateY(calc(var(--amp) * -1px)); }
  50% { transform:translateY(calc(var(--amp) * 1px)); }
}
@keyframes flag-shade {
  0%, 100% { opacity:0; }
  50% { opacity:.2; }
}
@media (prefers-reduced-motion: reduce) {
  .flag-strip { animation:none; transform:none; }
  .flag-shade { animation:none; opacity:0; }
}
</style>
