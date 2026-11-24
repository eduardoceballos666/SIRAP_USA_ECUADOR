// Geometry of the two national flags drawn by components/CountryFlag.vue.
//
// United States: proportions of Executive Order 10834 (hoist 1, fly 1.9, canton 0.76 x 7/13 of the hoist,
// 13 stripes, 50 stars in nine rows of 6 and 5). Ecuador: 3:2, yellow half, blue and red quarters.
// Units are the SVG user units of each flag's own viewBox.

export const USA_FLAG = { width: 190, height: 100, stripes: 13, cantonWidth: 76, cantonHeight: (100 * 7) / 13 }
export const ECUADOR_FLAG = { width: 150, height: 100 }
export const FLAG_COLORS = {
  usaRed: '#b22234', usaBlue: '#3c3b6e', white: '#ffffff',
  ecuadorYellow: '#ffd100', ecuadorBlue: '#034ea2', ecuadorRed: '#ed1c24',
}
export const FLAG_SIZES = { usa: USA_FLAG, ecuador: ECUADOR_FLAG }
const STAR_DIAMETER = 6.16 // 0.0616 of the hoist

// Centers of the 50 stars: rows 1, 3, 5, 7, 9 hold six, rows 2, 4, 6, 8 hold five (shifted half a step).
export function usaStarCenters() {
  const { cantonWidth: w, cantonHeight: h } = USA_FLAG
  const centers = []
  for (let row = 0; row < 9; row += 1) {
    const y = ((row + 1) * h) / 10
    const six = row % 2 === 0
    for (let column = 0; column < (six ? 6 : 5); column += 1) {
      centers.push({ x: ((six ? 2 * column + 1 : 2 * column + 2) * w) / 12, y })
    }
  }
  return centers
}

export const USA_STAR_RADIUS = STAR_DIAMETER / 2

// SVG `points` of a five-pointed star with one point straight up.
export function starPoints(cx, cy, radius) {
  const inner = radius * 0.381966
  const points = []
  for (let i = 0; i < 10; i += 1) {
    const r = i % 2 === 0 ? radius : inner
    const angle = -Math.PI / 2 + (i * Math.PI) / 5
    points.push(`${(cx + r * Math.cos(angle)).toFixed(3)},${(cy + r * Math.sin(angle)).toFixed(3)}`)
  }
  return points.join(' ')
}

export function flagSize(country) {
  return FLAG_SIZES[country === 'ecuador' ? 'ecuador' : 'usa']
}
