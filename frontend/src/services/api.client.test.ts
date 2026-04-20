import { describe, expect, it, vi } from 'vitest'

type AxiosInstanceLike = {
  get: ReturnType<typeof vi.fn>
  post: ReturnType<typeof vi.fn>
  put: ReturnType<typeof vi.fn>
  delete: ReturnType<typeof vi.fn>
}

describe('services/api axios wiring', () => {
  it('builds correct endpoint URLs and query params', async () => {
    vi.resetModules()
    const axiosInstance: AxiosInstanceLike = {
      get: vi.fn(),
      post: vi.fn(),
      put: vi.fn(),
      delete: vi.fn(),
    }

    const create = vi.fn(() => axiosInstance)

    vi.doMock('axios', () => ({
      default: {
        create,
        // Keep errors.ts safe if imported transitively.
        isAxiosError: () => false,
      },
    }))

    const mod = await import('@/services/api')

    mod.healthRecordsApi.list({ skip: 10, limit: 20 })
    expect(axiosInstance.get).toHaveBeenCalledWith('/api/health-records', { params: { skip: 10, limit: 20 } })

    mod.healthRecordsApi.get(123)
    expect(axiosInstance.get).toHaveBeenCalledWith('/api/health-records/123')

    mod.healthRecordsApi.create({
      record_date: '2026-04-01',
      weight: 75,
      sleep_hours: 7,
      calories: 2000,
      exercise_minutes: 0,
    })
    expect(axiosInstance.post).toHaveBeenCalledWith('/api/health-records', expect.any(Object))

    mod.healthRecordsApi.update(123, { weight: 76 })
    expect(axiosInstance.put).toHaveBeenCalledWith('/api/health-records/123', { weight: 76 })

    mod.healthRecordsApi.delete(123)
    expect(axiosInstance.delete).toHaveBeenCalledWith('/api/health-records/123')

    mod.analyticsApi.reasons(2000)
    expect(axiosInstance.get).toHaveBeenCalledWith('/api/analytics/reasons', {
      params: { calorie_target: 2000 },
    })

    mod.analyticsApi.dashboard()
    expect(axiosInstance.get).toHaveBeenCalledWith('/api/analytics/dashboard')

    mod.analyticsApi.trends(14)
    expect(axiosInstance.get).toHaveBeenCalledWith('/api/analytics/trends', { params: { days: 14 } })

    mod.analyticsApi.plateau()
    expect(axiosInstance.get).toHaveBeenCalledWith('/api/analytics/plateau')

    mod.analyticsApi.summary()
    expect(axiosInstance.get).toHaveBeenCalledWith('/api/analytics/summary', { params: {} })

    mod.analyticsApi.summary(2100)
    expect(axiosInstance.get).toHaveBeenCalledWith('/api/analytics/summary', { params: { calorie_target: 2100 } })

    mod.analyticsApi.weeklyReport()
    expect(axiosInstance.get).toHaveBeenCalledWith('/api/report/weekly')

    mod.profileApi.get()
    expect(axiosInstance.get).toHaveBeenCalledWith('/api/profile')

    mod.profileApi.update({
      target_weight: null,
      daily_calorie_target: 2000,
      protein_target: null,
      weekly_workout_target: null,
    })
    expect(axiosInstance.put).toHaveBeenCalledWith('/api/profile', expect.any(Object))
  })
})
