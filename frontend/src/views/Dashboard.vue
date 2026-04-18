<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">Dashboard</h1>
      <p class="page-subtitle">Your health overview and recent trends</p>
    </div>

    <StatePanel v-if="initialLoading" variant="loading" title="Loading dashboard..." message="Fetching your latest records and analytics." />
    <StatePanel v-else-if="pageError" variant="error" title="Couldn't load dashboard" :message="pageError">
      <template #action><Button label="Retry" icon="pi pi-refresh" severity="secondary" outlined @click="refreshAll" /></template>
    </StatePanel>
    <StatePanel v-else-if="isEmpty" variant="empty" title="No records yet" message="Add records to see KPIs and trends.">
      <template #action><router-link to="/records"><Button label="Add Records" icon="pi pi-plus" /></router-link></template>
    </StatePanel>

    <template v-else>
      <div class="card" style="margin-bottom: 1rem;">
        <div>Last record: {{ dashboard?.last_record_date ?? 'N/A' }}</div>
        <div>Freshness: <strong>{{ freshnessLabel }}</strong></div>
      </div>

      <div v-if="isStale" class="stale-warning">
        <span>? Your data is outdated</span>
        <router-link to="/records?date=today"><Button label="Add Today's Record" size="small" /></router-link>
      </div>

      <div class="grid-4" style="margin-bottom: 1.5rem;">
        <KpiCard label="Latest Weight" :value="dashboard?.current_weight" unit="kg" :decimals="1" icon="pi pi-user" icon-color="#6366f1" icon-bg="#eef2ff" />
        <KpiCard label="7-Day Avg Weight" :value="dashboard?.avg_weight_7d" unit="kg" :decimals="1" icon="pi pi-chart-line" icon-color="#8b5cf6" icon-bg="#f5f3ff" />
        <KpiCard label="7-Day Avg Sleep" :value="dashboard?.avg_sleep_7d" unit="h" :decimals="1" icon="pi pi-moon" icon-color="#0ea5e9" icon-bg="#e0f2fe" />
        <KpiCard label="7-Day Avg Calories" :value="dashboard?.avg_calories_7d" unit="kcal" :decimals="0" icon="pi pi-bolt" icon-color="#f59e0b" icon-bg="#fef3c7" />
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import Button from 'primevue/button'
import KpiCard from '@/components/KpiCard.vue'
import StatePanel from '@/components/StatePanel.vue'
import { useAnalyticsStore } from '@/stores/analytics'

const analyticsStore = useAnalyticsStore()
const selectedDays = ref(7)

const dashboard = computed(() => analyticsStore.dashboard)
const initialLoading = computed(() => {
  const needsData = analyticsStore.dashboard == null || analyticsStore.summary == null
  const loading = analyticsStore.dashboardStatus.loading || analyticsStore.summaryStatus.loading
  return needsData && loading
})
const pageError = computed(() => analyticsStore.dashboardPageError)
const isEmpty = computed(() => dashboard.value != null && dashboard.value.total_records === 0)

const MS_PER_DAY = 24 * 60 * 60 * 1000
function parseIsoDateToUtcDay(iso: string): number | null {
  const parts = iso.split('-').map((x) => Number(x))
  if (parts.length !== 3 || parts.some((n) => Number.isNaN(n))) return null
  const [y, m, d] = parts
  return Date.UTC(y, m - 1, d)
}

const lastRecordAgeDays = computed(() => {
  const iso = dashboard.value?.last_record_date
  if (!iso) return null
  if (iso === 'today') return 0
  const recordUtcDay = parseIsoDateToUtcDay(iso)
  if (recordUtcDay === null) return null
  const today = new Date()
  const todayUtcDay = Date.UTC(today.getFullYear(), today.getMonth(), today.getDate())
  return Math.max(0, Math.floor((todayUtcDay - recordUtcDay) / MS_PER_DAY))
})

const isStale = computed(() => lastRecordAgeDays.value !== null && lastRecordAgeDays.value > 7)
const freshnessLabel = computed(() => {
  if (!dashboard.value?.last_record_date) return 'Missing'
  if (isStale.value) return 'Stale'
  return 'Fresh'
})

async function refreshAll() {
  await analyticsStore.fetchDashboardBundle(selectedDays.value, analyticsStore.calorieTarget)
}

onMounted(async () => {
  await refreshAll()
})
</script>

<style scoped>
.page-header {
  margin-bottom: 1.5rem;
}
.stale-warning {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  border: 1px solid #fecaca;
  border-radius: var(--radius-md);
  background: #fff1f2;
  color: #991b1b;
  margin-bottom: 1rem;
}
</style>
