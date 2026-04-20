// JSDOM doesn't implement canvas; Chart.js may touch it during module init.
// We stub it globally so view tests don't emit noisy "Not implemented" warnings.
Object.defineProperty(HTMLCanvasElement.prototype, 'getContext', {
  value: () => null,
})

// PrimeVue components (e.g. DatePicker) may use matchMedia for responsive behavior.
// JSDOM doesn't provide it, so we stub a minimal implementation.
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => undefined,
    removeListener: () => undefined,
    addEventListener: () => undefined,
    removeEventListener: () => undefined,
    dispatchEvent: () => false,
  }),
})

// Prevent Chart.js from trying to create real charts in unit tests.
// Tests should verify state/UI logic, not Chart.js rendering internals.
import { vi } from 'vitest'
import { defineComponent, h } from 'vue'

vi.mock('vue-chartjs', () => ({
  Line: defineComponent({ name: 'Line', render: () => h('div', { 'data-test': 'chart-line' }) }),
  Bar: defineComponent({ name: 'Bar', render: () => h('div', { 'data-test': 'chart-bar' }) }),
}))

vi.mock('chart.js', () => ({
  Chart: { register: () => undefined },
  CategoryScale: {},
  LinearScale: {},
  PointElement: {},
  LineElement: {},
  BarElement: {},
  Title: {},
  Tooltip: {},
  Legend: {},
  Filler: {},
}))
