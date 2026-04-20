import { describe, expect, it, vi } from 'vitest'

import Dashboard from '@/views/Dashboard.vue'
import { mountWithApp } from '@/test/mountWithApp'

function makeStore(overrides: Record<string, unknown> = {}) {
  return {
    calorieTarget: 2000,
    summary: {},
    dashboard: {
      current_weight: 75,
      avg_weight_7d: 74.5,
      avg_sleep_7d: 7,
      avg_calories_7d: 2000,
      weight_change_7d: 0,
      total_records: 10,
      last_record_date: '2026-04-01',
    },
    dashboardStatus: { loading: false, error: null },
    summaryStatus: { loading: false, error: null },
    trendsStatus: { loading: false, error: null },
    dashboardPageError: null,
    fetchDashboardBundle: vi.fn().mockResolvedValue(undefined),
    ...overrides,
  }
}

const store = makeStore()
vi.mock('@/stores/analytics', () => ({ useAnalyticsStore: () => store }))

describe('Dashboard view', () => {
  it('shows freshness indicator', () => {
    const wrapper = mountWithApp(Dashboard, { global: { stubs: { Button: true } } })
    expect(wrapper.text()).toContain('Freshness')
  })
})
