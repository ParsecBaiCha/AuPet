export type Sample = { x: number; y: number; label: number }
export type Network = { w: number[][]; b: number[]; v: number[]; c: number }
export function random(seed: number) {
  return () => { seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0; return seed / 4294967296 }
}
export function dataset(kind: string, noise: number, seed = 42, count = 80): Sample[] {
  const rng = random(seed)
  return Array.from({ length: count }, () => {
    const x = rng() * 2 - 1, y = rng() * 2 - 1
    let label = Number(kind === 'circle' ? x * x + y * y < 0.5 : y > x * 0.6)
    if (rng() < noise) label = 1 - label
    return { x, y, label }
  })
}
export function network(): Network {
  const rng = random(17)
  return { w: Array.from({ length: 4 }, () => [rng() * 2 - 1, rng() * 2 - 1]), b: [0, 0, 0, 0], v: Array.from({ length: 4 }, () => rng() * 2 - 1), c: 0 }
}
export function forward(n: Network, x: number, y: number) {
  const h = n.w.map((w, i) => Math.tanh(w[0] * x + w[1] * y + n.b[i]))
  const z = h.reduce((sum, a, i) => sum + a * n.v[i], n.c)
  return { h, p: 1 / (1 + Math.exp(-z)) }
}
export function train(n: Network, samples: Sample[], rate: number) {
  const dw = n.w.map(() => [0, 0]), db = [0, 0, 0, 0], dv = [0, 0, 0, 0]
  let dc = 0
  for (const s of samples) {
    const { h, p } = forward(n, s.x, s.y), delta = p - s.label
    dc += delta
    h.forEach((a, i) => {
      dv[i] += delta * a
      const d = delta * n.v[i] * (1 - a * a)
      dw[i][0] += d * s.x; dw[i][1] += d * s.y; db[i] += d
    })
  }
  const step = rate / samples.length
  n.w.forEach((w, i) => { w[0] -= step * dw[i][0]; w[1] -= step * dw[i][1]; n.b[i] -= step * db[i]; n.v[i] -= step * dv[i] })
  n.c -= step * dc
}
export function metrics(n: Network, samples: Sample[]) {
  let loss = 0, correct = 0
  samples.forEach(s => {
    const p = Math.max(1e-9, Math.min(1 - 1e-9, forward(n, s.x, s.y).p))
    loss -= s.label * Math.log(p) + (1 - s.label) * Math.log(1 - p)
    correct += Number(Number(p >= 0.5) === s.label)
  })
  return { loss: loss / samples.length, accuracy: correct / samples.length }
}
