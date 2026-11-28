<script>
let nextFlagId = 0
</script>

<script setup>
// Flag of the active country profile. `waving` animates it with no pole (the sidebar); without it the
// flag is a plain still picture (the control strip). The United States flag is drawn as inline SVG; Ecuador's is the
// official artwork, as an image that ships with the app (so it needs no network), cut into strips when it waves.
import { computed } from 'vue'
import ecuadorFlagUrl from '@/assets/flags/ecuador.webp'
import { FLAG_COLORS as C, FLAG_SIZES, USA_FLAG, USA_STAR_RADIUS, starPoints, usaStarCenters, waveStrips } from '@/lib/flags'

const props = defineProps({
  country: { type: String, required: true },
  waving: { type: Boolean, default: false },
  strips: { type: Number, default: 80 },
})

const uid = `flag${(nextFlagId += 1)}`
const isEcuador = computed(() => props.country === 'ecuador')
const size = computed(() => FLAG_SIZES[isEcuador.value ? 'ecuador' : 'usa'])
const label = computed(() => (isEcuador.value ? 'Bandera de Ecuador' : 'Bandera de Estados Unidos de América'))
const viewBox = computed(() => {
  const { width, height } = size.value
  return props.waving ? `-1 -10 ${width + 2} ${height + 20}` : `0 0 ${width} ${height}`
})
const stripeHeight = USA_FLAG.height / USA_FLAG.stripes
const redStripes = Array.from({ length: 7 }, (_, i) => i * 2 * stripeHeight)
const stars = usaStarCenters().map(({ x, y }) => starPoints(x, y, USA_STAR_RADIUS))
const waves = computed(() => waveStrips(props.strips, size.value.width))
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
          <!-- The official flag with its coat of arms (a bitmap of the public-domain artwork, see THIRD_PARTY_NOTICES.md), over the three bands, which show until it loads. -->
          <image :href="ecuadorFlagUrl" width="150" height="100" preserveAspectRatio="none" />
        </template>
        <template v-else>
          <rect :width="USA_FLAG.width" :height="USA_FLAG.height" :fill="C.white" />
          <rect v-for="y in redStripes" :key="y" :y="y" :width="USA_FLAG.width" :height="stripeHeight" :fill="C.usaRed" />
          <rect :width="USA_FLAG.cantonWidth" :height="USA_FLAG.cantonHeight" :fill="C.usaBlue" />
          <polygon v-for="points in stars" :key="points" :points="points" :fill="C.white" />
        </template>
        <!-- light from the upper left over the whole cloth: a little brighter at the hoist, a little darker at the free end -->
        <rect v-if="waving" :width="size.width" :height="size.height" :fill="`url(#${uid}-sheen)`" />
      </g>
      <linearGradient :id="`${uid}-sheen`" gradientUnits="userSpaceOnUse" x1="0" y1="0" :x2="size.width" y2="0">
        <stop offset="0" stop-color="#fff" stop-opacity=".12" />
        <stop offset=".38" stop-color="#fff" stop-opacity="0" />
        <stop offset=".7" stop-color="#000" stop-opacity="0" />
        <stop offset="1" stop-color="#000" stop-opacity=".18" />
      </linearGradient>
      <clipPath v-for="strip in waves" :key="strip.i" :id="`${uid}-c${strip.i}`">
        <rect :x="strip.x" y="-20" :width="strip.width" :height="size.height + 40" />
      </clipPath>
    </defs>

    <template v-if="waving">
      <g
        v-for="strip in waves" :key="strip.i" class="flag-strip"
        :style="{ '--amp': strip.amplitude.toFixed(2), '--phase': strip.phase.toFixed(3) }"
      >
        <g class="flag-tilt" :style="{ '--tilt': strip.tilt.toFixed(2), transformOrigin: `${strip.centre.toFixed(2)}px 0px` }">
          <g :clip-path="`url(#${uid}-c${strip.i})`">
            <g class="flag-cut">
              <use :href="`#${uid}-art`" />
              <rect
                class="flag-shade" :x="strip.x - 2" y="0" :width="strip.width + 4" :height="size.height"
                :style="{ '--lo': strip.shade.toFixed(3), '--hi': strip.light.toFixed(3) }"
              />
            </g>
          </g>
        </g>
      </g>
    </template>
    <template v-else>
      <use :href="`#${uid}-art`" />
      <rect class="flag-outline" :width="size.width" :height="size.height" fill="none" />
    </template>
  </svg>
</template>

<style scoped>
.country-flag { display:block; overflow:visible; }
.flag-outline { stroke:var(--flag-outline, rgb(255 255 255 / .55)); stroke-width:1; vector-effect:non-scaling-stroke; }
/*
  Every strip moves like a point of a wave that runs from the hoist to the free end: it goes up and down
  (.flag-strip), its cloth tilts with the slope of that wave (.flag-tilt, a quarter of a period later, so the
  strips stay edge to edge), and it is lit or shaded by that tilt (.flag-shade, same timing). A negative delay
  puts each strip at its own point of the wave from the first frame.
*/
.is-waving { --period:3.6s; --ease:cubic-bezier(.37, 0, .63, 1); }
.flag-strip {
  transform:translateY(calc(var(--amp) * -1px));
  animation:flag-wave var(--period) var(--ease) infinite;
  animation-delay:calc((var(--phase) - 2) * var(--period));
}
.flag-tilt {
  transform:skewY(calc(var(--tilt) * -1deg));
  animation:flag-tilt var(--period) var(--ease) infinite;
  animation-delay:calc((var(--phase) - 1.75) * var(--period));
}
.flag-cut { opacity:.999; } /* the strip is drawn on its own layer and cut once, so no light seam shows where two strips meet */
.flag-shade {
  fill:rgb(255 255 255 / 0);
  animation:flag-shade var(--period) linear infinite;
  animation-delay:calc((var(--phase) - 1.75) * var(--period));
}
@keyframes flag-wave {
  0%, 100% { transform:translateY(calc(var(--amp) * -1px)); }
  50% { transform:translateY(calc(var(--amp) * 1px)); }
}
@keyframes flag-tilt {
  0%, 100% { transform:skewY(calc(var(--tilt) * -1deg)); }
  50% { transform:skewY(calc(var(--tilt) * 1deg)); }
}
@keyframes flag-shade {
  0%, 100% { fill:rgb(255 255 255 / var(--hi)); }
  12.5%, 87.5% { fill:rgb(255 255 255 / calc(var(--hi) * .71)); }
  25%, 75% { fill:rgb(255 255 255 / 0); }
  37.5%, 62.5% { fill:rgb(0 0 0 / calc(var(--lo) * .71)); }
  50% { fill:rgb(0 0 0 / var(--lo)); }
}
@media (prefers-reduced-motion: reduce) {
  /* No movement: the flag stays still in one gentle wave, each strip frozen at its own point of the animation. */
  .flag-strip, .flag-tilt, .flag-shade { animation-play-state:paused; }
}
</style>
