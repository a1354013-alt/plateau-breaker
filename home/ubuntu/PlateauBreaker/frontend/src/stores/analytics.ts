import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

import {
  analyticsApi,
  type DashboardData,
  type TrendsData,
  type SummaryData,
} from '@/services/api'

export const useAnalyticsStore = defineStore('analytics', () => {
  const dashboard = ref<DashboardData | null>(null)
  const trends = ref<TrendsData | null>(null)
  const summary = ref<SummaryData | null>(null) // Contains plateau and reasons data
  const loading = ref(false)
  const error = ref<string | null>(null)
  const calorieTarget = ref(2000) // Default calorie target (always overridden by user input in Analysis.vue)

  async function fetchDashboard() {
    try {
      const res = await analyticsApi.dashboard()
      dashboard.value = res.data
    } catch (e: any) {
      error.value = e?.message || 'Failed to fetch dashboard'
    }
  }

  async function fetchTrends(days: number = 30) {
    try {
      const res = await analyticsApi.trends(days)
      trends.value = res.data
    } catch (e: any) {
      error.value = e?.message || 'Failed to fetch trends'
    }
  }

  async function fetchSummary(target: number) {
    error.value = null
    try {
      const res = await analyticsApi.summary(target)
      summary.value = res.data
    } catch (e: any) {
      error.value = e?.message || 'Failed to fetch summary'
    }
  }

  async function fetchAll(days: number = 30, target?: number) {
    // Centralized loading control: only fetchAll manages loading state
    loading.value = true
    error.value = null
    const targetValue = target ?? calorieTarget.value
    if (target !== undefined) {
      calorieTarget.value = target
    }
    try {
      // Fetch all data in parallel: dashboard, trends, and summary (primary data source)
      await Promise.all([
        fetchDashboard(),
        fetchTrends(days),
        fetchSummary(targetValue),
      ])
    } catch (e: any) {
      error.value = e?.message || 'Failed to fetch analytics data'
    } finally {
      loading.value = false
    }
  }

  // Computed helpers for simplified access to summary data
  const summaryText = computed(() => summary.value?.summary?.summary || '')
  const summaryStatus = computed(() => summary.value?.summary?.status || 'insufficient_data')
  const summaryInsight = computed(() => summary.value?.summary?.insight || '')
  const topReasons = computed(() => summary.value?.summary?.top_reasons || [])
  const plateauStatus = computed(() => summary.value?.plateau?.status || 'insufficient_data')
  const reasonsList = computed(() => summary.value?.reasons?.reasons || [])
  const plateauMessage = computed(() => summary.value?.plateau?.message || '')

  // Computed helpers for Dashboard and Trends to avoid direct access to summary.value.plateau or summary.value.reasons
  const dashboardData = computed(() => dashboard.value)
  const trendsData = computed(() => trends.value)
  const plateauData = computed(() => summary.value?.plateau)
  const reasonsData = computed(() => summary.value?.reasons)

  return {
    // Primary data sources
    summary,
    dashboard: dashboardData,
    trends: trendsData,
    // UI state
    loading,
    error,
    calorieTarget,
    // Computed helpers for simplified access
    summaryText,
    summaryStatus,
    summaryInsight,
    topReasons,
    plateauStatus,
    plateauMessage,
    reasonsList,
    plateau: plateauData,
    reasons: reasonsData,
    // Fetch functions
    fetchAll,
    fetchTrends, // Allow independent trend reload for date range changes
  }
})
