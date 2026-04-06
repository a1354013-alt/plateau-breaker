import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

import {
  healthRecordsApi,
  type HealthRecord,
  type HealthRecordCreate,
  type HealthRecordUpdate,
} from '@/services/api'

export const useHealthRecordsStore = defineStore('healthRecords', () => {
  const records = ref<HealthRecord[]>([])
  const total = ref(0)
  const loading = ref(false)
  const error = ref<string | null>(null)
  // Store current query parameters to maintain UI consistency after CRUD operations
  const currentQueryParams = ref<{
    skip?: number
    limit?: number
    start_date?: string
    end_date?: string
  }>({ skip: 0, limit: 200 })

  const sortedRecords = computed(() =>
    [...records.value].sort(
      (a, b) => new Date(b.record_date).getTime() - new Date(a.record_date).getTime()
    )
  )

  async function fetchRecords(params?: {
    skip?: number
    limit?: number
    start_date?: string
    end_date?: string
  }) {
    loading.value = true
    error.value = null
    // Update current query params for consistency
    if (params) {
      currentQueryParams.value = params
    }
    try {
      const res = await healthRecordsApi.list(params || currentQueryParams.value)
      records.value = res.data.records
      total.value = res.data.total
    } catch (e: any) {
      error.value = e?.response?.data?.detail || 'Failed to fetch records'
    } finally {
      loading.value = false
    }
  }

  async function createRecord(data: HealthRecordCreate): Promise<HealthRecord | null> {
    error.value = null
    try {
      const res = await healthRecordsApi.create(data)
      // Re-fetch using current query parameters to maintain UI consistency
      // fetchRecords handles loading state centrally
      await fetchRecords(currentQueryParams.value)
      return res.data
    } catch (e: any) {
      error.value = e?.response?.data?.detail || 'Failed to create record'
      return null
    }
  }

  async function updateRecord(id: number, data: HealthRecordUpdate): Promise<HealthRecord | null> {
    error.value = null
    try {
      const res = await healthRecordsApi.update(id, data)
      // Re-fetch using current query parameters to maintain UI consistency
      // fetchRecords handles loading state centrally
      await fetchRecords(currentQueryParams.value)
      return res.data
    } catch (e: any) {
      error.value = e?.response?.data?.detail || 'Failed to update record'
      return null
    }
  }

  async function deleteRecord(id: number): Promise<boolean> {
    error.value = null
    try {
      await healthRecordsApi.delete(id)
      // Re-fetch using current query parameters to maintain UI consistency
      // fetchRecords handles loading state centrally
      await fetchRecords(currentQueryParams.value)
      return true
    } catch (e: any) {
      error.value = e?.response?.data?.detail || 'Failed to delete record'
      return false
    }
  }

  return {
    records,
    total,
    loading,
    error,
    sortedRecords,
    currentQueryParams,
    fetchRecords,
    createRecord,
    updateRecord,
    deleteRecord,
  }
})
