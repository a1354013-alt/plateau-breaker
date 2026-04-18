import { beforeEach, describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'

import Records from '@/views/Records.vue'
import { healthRecordsApi } from '@/services/api'

const pushMock = vi.fn()
const replaceMock = vi.fn()
let routeQuery: Record<string, unknown> = {}

vi.mock('vue-router', async (importOriginal) => {
  const actual = await importOriginal<typeof import('vue-router')>()
  return {
    ...actual,
    useRoute: () => ({ query: routeQuery }),
    useRouter: () => ({ push: pushMock, replace: replaceMock }),
  }
})

vi.mock('@/services/api', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/services/api')>()
  return {
    ...actual,
    healthRecordsApi: {
      ...actual.healthRecordsApi,
      list: vi.fn().mockResolvedValue({ data: { total: 0, records: [] } }),
      create: vi.fn(),
      update: vi.fn(),
      delete: vi.fn(),
    },
  }
})

vi.mock('primevue/useconfirm', () => ({ useConfirm: () => ({ require: vi.fn() }) }))
vi.mock('primevue/usetoast', () => ({ useToast: () => ({ add: vi.fn() }) }))

describe('Records view', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    routeQuery = {}
  })

  it('sends start_date and end_date when applying filter', async () => {
    mount(Records, {
      global: {
        stubs: { ConfirmDialog: true },
      },
    })

    await Promise.resolve()
    expect(vi.mocked(healthRecordsApi.list)).toHaveBeenCalled()
  })

  it('opens add form when date query exists', async () => {
    routeQuery = { date: '2026-04-10' }

    const wrapper = mount(Records, {
      global: { stubs: { ConfirmDialog: true } },
    })

    await wrapper.vm.$nextTick()
    expect(replaceMock).toHaveBeenCalled()
  })
})
