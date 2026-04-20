import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { flushPromises } from '@vue/test-utils'
import { defineComponent } from 'vue'
import { createMemoryHistory, createRouter } from 'vue-router'

import Records from '@/views/Records.vue'
import { healthRecordsApi } from '@/services/api'
import { mountWithApp } from '@/test/mountWithApp'

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
  })

  it('sends start_date and end_date when applying filter', async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [{ path: '/records', component: Records }],
    })
    await router.push('/records')
    await router.isReady()

    const AppHost = defineComponent({ template: '<RouterView />' })

    const wrapper = mountWithApp(AppHost, {
      global: {
        plugins: [router],
        stubs: { ConfirmDialog: true },
      },
    })

    await flushPromises()
    expect(vi.mocked(healthRecordsApi.list)).toHaveBeenCalled()

    const buttons = wrapper.findAll('button')
    const apply = buttons.find((b) => b.text().includes('Apply Filter'))
    const reset = buttons.find((b) => b.text().includes('Reset Filter'))
    expect(apply).toBeTruthy()
    expect(reset).toBeTruthy()

    await apply!.trigger('click')
    await reset!.trigger('click')
    await flushPromises()

    expect(vi.mocked(healthRecordsApi.list).mock.calls.length).toBeGreaterThanOrEqual(3)

    const addRecord = buttons.find((b) => b.text().includes('Add Record'))
    expect(addRecord).toBeTruthy()
    await addRecord!.trigger('click')

    const form = wrapper.find('form.record-form')
    expect(form.exists()).toBe(true)
    await form.trigger('submit')
    await flushPromises()
    const formError = wrapper.find('.form-error')
    expect(formError.exists()).toBe(true)
    expect(formError.text()).toContain('Please fill in all required fields')
  })

  it('opens add form when date query exists', async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [{ path: '/records', component: Records }],
    })
    await router.push({ path: '/records', query: { date: '2026-04-10' } })
    await router.isReady()

    const AppHost = defineComponent({ template: '<RouterView />' })

    const wrapper = mountWithApp(AppHost, {
      global: { plugins: [router], stubs: { ConfirmDialog: true } },
    })

    await router.isReady()
    expect(router.currentRoute.value.fullPath).toContain('/records')
    await wrapper.vm.$nextTick()
    await flushPromises()
    await flushPromises()
    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('Health Records')
    expect(router.currentRoute.value.query.date).toBeUndefined()
    const dialog = wrapper.findComponent({ name: 'Dialog' })
    expect(dialog.exists()).toBe(true)
    expect(dialog.props('visible')).toBe(true)
  })
})
