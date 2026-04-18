import { describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'

import Analysis from '@/views/Analysis.vue'

const push = vi.fn()
vi.mock('vue-router', async (importOriginal) => {
  const actual = await importOriginal<typeof import('vue-router')>()
  return {
    ...actual,
    useRouter: () => ({ push }),
  }
})

function makeStore(overrides: Record<string, unknown> = {}) {
  return {
    calorieTarget: 2000,
    summary: {
      plateau: { status: 'plateau' },
      reasons: { missing_dates: ['2026-04-10'] },
      summary: { text: 'x', factor_contributions: [] },
      recommendations: [],
    },
    summaryStatus: { loading: false, error: null },
    analysisPageError: null,
    summaryText: 'ok',
    plateauStatus: 'plateau',
    reasonsData: { missing_dates: ['2026-04-10'] },
    fetchAnalysisBundle: vi.fn().mockResolvedValue(undefined),
    ...overrides,
  }
}

let store = makeStore()
vi.mock('@/stores/analytics', () => ({ useAnalyticsStore: () => store }))
vi.mock('@/services/api', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/services/api')>()
  return {
    ...actual,
    analyticsApi: {
      ...actual.analyticsApi,
      weeklyReport: vi.fn().mockResolvedValue({ data: {} }),
    },
  }
})

describe('Analysis view', () => {
  it('renders missing days and routes to record add page', async () => {
    store = makeStore()
    const wrapper = mount(Analysis, { global: { stubs: { RouterLink: true } } })
    expect(wrapper.text()).toContain('Missing Days')
    const addBtn = wrapper.findAll('button').find((b) => b.text().includes('Add'))
    expect(addBtn).toBeTruthy()
    await addBtn!.trigger('click')
    expect(push).toHaveBeenCalled()
  })
})
