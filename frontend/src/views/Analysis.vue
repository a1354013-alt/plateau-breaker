<template>
  <div class="page-container">
    <div class="page-header-row">
      <div class="page-header">
        <h1 class="page-title">Analysis</h1>
        <p class="page-subtitle">Deep dive into your weight plateau causes</p>
      </div>
      <div class="header-controls">
        <span class="target-label">Calorie Target:</span>
        <InputNumber v-model="calorieTarget" suffix=" kcal" :min="1000" :max="5000" :useGrouping="false" :inputStyle="{ width: '100px', textAlign: 'center' }" @blur="refresh" />
        <Button icon="pi pi-refresh" @click="refresh" :loading="analyticsStore.summaryStatus.loading" severity="secondary" text rounded />
      </div>
    </div>

    <div class="actions-row">
      <Button label="Export Weekly Report" icon="pi pi-download" severity="secondary" outlined @click="exportWeeklyReport" :loading="exporting" />
    </div>

    <StatePanel v-if="analyticsStore.summaryStatus.loading && analyticsStore.summary == null" variant="loading" title="Analyzing..." message="Running plateau detection and reason analysis." />
    <StatePanel v-else-if="pageError" variant="error" title="Couldn't load analysis" :message="pageError">
      <template #action><Button label="Retry" icon="pi pi-refresh" severity="secondary" outlined @click="refresh" /></template>
    </StatePanel>

    <template v-else-if="plateauStatus !== 'insufficient_data'">
      <div class="card" style="margin-bottom: 1rem;">
        <h3 class="section-title">Status</h3>
        <div>{{ statusTitle }}</div>
        <div class="text-muted">{{ analyticsStore.summaryText || '-' }}</div>
      </div>

      <div v-if="missingDates.length > 0" class="card" style="margin-bottom: 1rem;">
        <h3 class="section-title">Missing Days</h3>
        <p>You are missing records for:</p>
        <div class="missing-list">
          <div v-for="day in missingDates" :key="day" class="missing-item">
            <span>[ {{ day }} ]</span>
            <Button label="Add" size="small" @click="goAddDay(day)" />
          </div>
        </div>
      </div>

      <div class="card" style="margin-bottom: 1rem;">
        <h3 class="section-title">Factor Breakdown</h3>
        <div v-if="factorContributions.length">
          <div v-for="factor in factorContributions" :key="factor.factor" class="factor-row">
            <span>{{ factorLabel(factor.factor) }} - {{ factor.impact_percent }}% impact</span>
            <span>confidence {{ Math.round(factor.confidence * 100) }}%</span>
          </div>
        </div>
        <div v-else class="text-muted">No factor contribution data.</div>
      </div>

      <div class="card" style="margin-bottom: 1rem;">
        <h3 class="section-title">Recommended Actions</h3>
        <div v-if="recommendations.length">
          <div v-for="rec in recommendations" :key="`${rec.priority}-${rec.message}`" class="factor-row">
            <span>#{{ rec.priority }} {{ rec.message }}</span>
            <span>confidence {{ Math.round(rec.confidence * 100) }}%</span>
          </div>
        </div>
        <div v-else class="text-muted">No recommendations yet.</div>
      </div>
    </template>

    <StatePanel v-else variant="empty" title="Not enough data for analysis" message="Log at least 5 recent days of health records to unlock analysis.">
      <template #action>
        <router-link to="/records"><Button label="Add Records" icon="pi pi-plus" /></router-link>
      </template>
    </StatePanel>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { saveAs } from './analysisDownload'
import Button from 'primevue/button'
import InputNumber from 'primevue/inputnumber'
import StatePanel from '@/components/StatePanel.vue'
import { analyticsApi } from '@/services/api'
import { useAnalyticsStore } from '@/stores/analytics'

const analyticsStore = useAnalyticsStore()
const router = useRouter()
const exporting = ref(false)

const calorieTarget = computed<number | null>({
  get: () => analyticsStore.calorieTarget,
  set: (val) => {
    analyticsStore.calorieTarget = val ?? 2000
  },
})

const plateauStatus = computed(() => analyticsStore.plateauStatus)
const pageError = computed(() => analyticsStore.analysisPageError)
const factorContributions = computed(() => analyticsStore.summary?.summary.factor_contributions ?? [])
const recommendations = computed(() => [...(analyticsStore.summary?.recommendations ?? [])].sort((a, b) => a.priority - b.priority))
const missingDates = computed(() => analyticsStore.reasonsData?.missing_dates ?? [])

const statusTitle = computed(() => {
  const map: Record<string, string> = {
    plateau: 'Weight Plateau Detected',
    losing: 'You Are Losing Weight',
    gaining: 'Weight is Increasing',
    insufficient_data: 'Insufficient Data',
  }
  return map[plateauStatus.value] || 'Unknown Status'
})

function factorLabel(code: string): string {
  const map: Record<string, string> = {
    calorie_over: 'Calories over target',
    low_sleep: 'Low sleep quality',
    weekend_overeating: 'Weekend overeating',
    exercise_drop: 'Reduced exercise',
    missing_data: 'Missing data',
  }
  return map[code] ?? code
}

function goAddDay(day: string) {
  void router.push(`/records?date=${day}`)
}

async function exportWeeklyReport() {
  exporting.value = true
  try {
    const res = await analyticsApi.weeklyReport()
    saveAs(res.data)
  } finally {
    exporting.value = false
  }
}

async function refresh() {
  await analyticsStore.fetchAnalysisBundle(calorieTarget.value ?? 2000)
}

onMounted(async () => {
  await refresh()
})
</script>

<style scoped>
.page-header-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}
.header-controls {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}
.target-label {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--color-text-secondary);
}
.actions-row {
  margin-bottom: 1rem;
}
.section-title {
  font-size: 1rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}
.factor-row {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--color-border);
}
.missing-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.missing-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
</style>
