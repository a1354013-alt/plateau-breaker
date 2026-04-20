import { describe, expect, it, vi } from 'vitest'
import { flushPromises } from '@vue/test-utils'

import Profile from '@/views/Profile.vue'
import { mountWithApp } from '@/test/mountWithApp'
import { profileApi } from '@/services/api'

vi.mock('@/services/api', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/services/api')>()
  return {
    ...actual,
    profileApi: {
      ...actual.profileApi,
      get: vi.fn(),
      update: vi.fn(),
    },
  }
})

vi.mock('primevue/usetoast', () => ({ useToast: () => ({ add: vi.fn() }) }))

describe('Profile view', () => {
  it('loads profile on mount', async () => {
    vi.mocked(profileApi.get).mockResolvedValueOnce({
      data: {
        id: 1,
        target_weight: 70,
        daily_calorie_target: 2100,
        protein_target: 120,
        weekly_workout_target: 3,
        created_at: '2026-04-01T00:00:00Z',
        updated_at: '2026-04-01T00:00:00Z',
      },
    } as never)

    const wrapper = mountWithApp(Profile)
    await flushPromises()

    expect(vi.mocked(profileApi.get)).toHaveBeenCalledTimes(1)
    expect(wrapper.text()).toContain('Profile & Goals')
    expect(wrapper.text()).toContain('Save Goals')
  })

  it('saves profile changes', async () => {
    vi.mocked(profileApi.get).mockResolvedValueOnce({
      data: {
        id: 1,
        target_weight: null,
        daily_calorie_target: 2000,
        protein_target: null,
        weekly_workout_target: null,
        created_at: '2026-04-01T00:00:00Z',
        updated_at: '2026-04-01T00:00:00Z',
      },
    } as never)
    vi.mocked(profileApi.update).mockResolvedValueOnce({ data: {} } as never)

    const wrapper = mountWithApp(Profile)
    await flushPromises()

    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(vi.mocked(profileApi.update)).toHaveBeenCalledTimes(1)
  })
})

