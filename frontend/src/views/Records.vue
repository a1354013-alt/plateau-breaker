<template>
  <div class="page-container">
    <div class="page-header-row">
      <div>
        <h1 class="page-title">Health Records</h1>
        <p class="page-subtitle">Log and manage your daily health data</p>
      </div>
      <Button label="Add Record" icon="pi pi-plus" @click="openForm(null)" />
    </div>

    <div class="card filter-card">
      <div class="grid-4 filter-grid">
        <div class="filter-field">
          <label>Start Date</label>
          <DatePicker v-model="startDate" dateFormat="yy-mm-dd" showIcon fluid />
        </div>
        <div class="filter-field">
          <label>End Date</label>
          <DatePicker v-model="endDate" dateFormat="yy-mm-dd" showIcon fluid />
        </div>
        <div class="filter-actions">
          <Button label="Apply Filter" icon="pi pi-filter" @click="applyFilter" />
          <Button label="Reset Filter" icon="pi pi-times" severity="secondary" outlined @click="resetFilter" />
        </div>
      </div>
    </div>

    <StatePanel v-if="store.error" variant="error" title="Couldn't load records" :message="store.error">
      <template #action>
        <Button label="Retry" icon="pi pi-refresh" severity="secondary" outlined @click="loadRecords" />
      </template>
    </StatePanel>

    <StatePanel
      v-else-if="!store.loading && store.total === 0"
      variant="empty"
      title="No records yet"
      message="Add your first health record to start tracking trends and insights."
    >
      <template #action>
        <Button label="Add First Record" icon="pi pi-plus" @click="openForm(null)" />
      </template>
    </StatePanel>

    <Dialog v-model:visible="showForm" :header="editingRecord ? 'Edit Record' : 'Add Health Record'" :modal="true" :style="{ width: '520px', maxWidth: '95vw' }" :draggable="false">
      <form class="record-form" @submit.prevent="submitForm">
        <div class="form-row">
          <div class="form-group">
            <label>Date *</label>
            <DatePicker v-model="form.record_date" dateFormat="yy-mm-dd" :maxDate="today" showIcon fluid />
          </div>
          <div class="form-group">
            <label>Weight (kg) *</label>
            <InputNumber ref="weightInputRef" v-model="form.weight" :min="20" :max="500" :minFractionDigits="1" :maxFractionDigits="1" fluid />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>Sleep Hours *</label>
            <InputNumber v-model="form.sleep_hours" :min="0" :max="24" :minFractionDigits="1" :maxFractionDigits="1" fluid />
          </div>
          <div class="form-group">
            <label>Calories (kcal) *</label>
            <InputNumber v-model="form.calories" :min="0" :max="20000" fluid />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>Protein (g)</label>
            <InputNumber v-model="form.protein" :min="0" :max="500" fluid placeholder="Optional" />
          </div>
          <div class="form-group">
            <label>Exercise (min)</label>
            <InputNumber v-model="form.exercise_minutes" :min="0" :max="1440" fluid />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>Exercise Type</label>
            <InputText v-model="form.exercise_type" placeholder="e.g. Running, Cycling" fluid />
          </div>
          <div class="form-group">
            <label>Steps</label>
            <InputNumber v-model="form.steps" :min="0" :max="200000" fluid placeholder="Optional" />
          </div>
        </div>

        <div class="form-group">
          <label>Note</label>
          <Textarea v-model="form.note" rows="2" placeholder="Any notes for today..." fluid />
        </div>

        <div v-if="formError" class="form-error">{{ formError }}</div>

        <div class="form-actions">
          <Button type="button" label="Cancel" severity="secondary" outlined @click="showForm = false" />
          <Button type="submit" :label="editingRecord ? 'Update' : 'Save Record'" :loading="store.loading" />
        </div>
      </form>
    </Dialog>

    <ConfirmDialog />

    <div v-if="!(store.total === 0 && !store.loading && !store.error)" class="card table-card">
      <div class="table-toolbar">
        <span class="table-count">{{ pageRangeText }}</span>
        <Button label="Refresh" icon="pi pi-refresh" severity="secondary" outlined size="small" @click="loadRecords" :loading="store.loading" />
      </div>

      <DataTable :value="store.records" :loading="store.loading" stripedRows responsiveLayout="scroll" lazy :paginator="store.total > rows" :rows="rows" :first="first" :totalRecords="store.total" :rowsPerPageOptions="[20, 50, 100]" @page="onPage" class="records-table">
        <Column field="record_date" header="Date" style="min-width: 110px" />
        <Column field="weight" header="Weight" style="min-width: 90px">
          <template #body="{ data }">{{ data.weight.toFixed(1) }} kg</template>
        </Column>
        <Column field="sleep_hours" header="Sleep" style="min-width: 80px">
          <template #body="{ data }">{{ data.sleep_hours.toFixed(1) }}h</template>
        </Column>
        <Column field="calories" header="Calories" style="min-width: 90px" />
        <Column field="protein" header="Protein" style="min-width: 80px">
          <template #body="{ data }">{{ data.protein ?? '-' }}</template>
        </Column>
        <Column field="note" header="Note" style="min-width: 120px">
          <template #body="{ data }">{{ data.note || '-' }}</template>
        </Column>
        <Column header="Actions" style="min-width: 100px; text-align: right">
          <template #body="{ data }">
            <div class="row-actions">
              <Button icon="pi pi-pencil" severity="secondary" text rounded size="small" @click="openForm(data)" />
              <Button icon="pi pi-trash" severity="danger" text rounded size="small" @click="confirmDelete(data)" />
            </div>
          </template>
        </Column>
      </DataTable>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useConfirm } from 'primevue/useconfirm'
import { useToast } from 'primevue/usetoast'

import Button from 'primevue/button'
import ConfirmDialog from 'primevue/confirmdialog'
import DataTable from 'primevue/datatable'
import type { DataTablePageEvent } from 'primevue/datatable'
import DatePicker from 'primevue/datepicker'
import Dialog from 'primevue/dialog'
import Column from 'primevue/column'
import InputNumber from 'primevue/inputnumber'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'

import StatePanel from '@/components/StatePanel.vue'
import { useHealthRecordsStore } from '@/stores/healthRecords'
import type { HealthRecord } from '@/services/api'

const store = useHealthRecordsStore()
const confirm = useConfirm()
const toast = useToast()
const route = useRoute()
const router = useRouter()

const today = new Date()
const first = computed(() => store.query.skip)
const rows = computed(() => store.query.limit)

const startDate = ref<Date | null>(store.query.start_date ? new Date(`${store.query.start_date}T00:00:00`) : null)
const endDate = ref<Date | null>(store.query.end_date ? new Date(`${store.query.end_date}T00:00:00`) : null)

const pageRangeText = computed(() => {
  if (store.total === 0) return 'No records'
  const start = Math.min(store.query.skip + 1, store.total)
  const end = Math.min(store.query.skip + store.query.limit, store.total)
  return `Showing ${start}-${end} of ${store.total}`
})

const showForm = ref(false)
const editingRecord = ref<HealthRecord | null>(null)
const formError = ref('')
const weightInputRef = ref<{ $el?: HTMLElement } | null>(null)

const defaultForm = () => ({
  record_date: new Date(),
  weight: null as number | null,
  sleep_hours: null as number | null,
  calories: null as number | null,
  protein: null as number | null,
  exercise_minutes: 0,
  exercise_type: '',
  steps: null as number | null,
  note: '',
})

const form = reactive(defaultForm())

function formatDate(date: Date | null): string | undefined {
  if (!date) return undefined
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

async function applyFilter() {
  await store.fetchRecords({
    skip: 0,
    limit: store.query.limit,
    start_date: formatDate(startDate.value),
    end_date: formatDate(endDate.value),
  })
}

async function resetFilter() {
  startDate.value = null
  endDate.value = null
  await store.fetchRecords({ skip: 0, limit: store.query.limit })
}

function openForm(record: HealthRecord | null) {
  formError.value = ''
  if (record) {
    editingRecord.value = record
    Object.assign(form, {
      record_date: new Date(`${record.record_date}T00:00:00`),
      weight: record.weight,
      sleep_hours: record.sleep_hours,
      calories: record.calories,
      protein: record.protein ?? null,
      exercise_minutes: record.exercise_minutes,
      exercise_type: record.exercise_type ?? '',
      steps: record.steps ?? null,
      note: record.note ?? '',
    })
  } else {
    editingRecord.value = null
    Object.assign(form, defaultForm())
  }
  showForm.value = true
}

async function submitForm() {
  formError.value = ''
  if (!form.record_date || form.weight === null || form.sleep_hours === null || form.calories === null) {
    formError.value = 'Please fill in all required fields (Date, Weight, Sleep, Calories).'
    return
  }

  const payload = {
    record_date: formatDate(form.record_date)!,
    weight: form.weight,
    sleep_hours: form.sleep_hours,
    calories: form.calories,
    protein: form.protein ?? undefined,
    exercise_minutes: form.exercise_minutes ?? 0,
    exercise_type: form.exercise_type || undefined,
    steps: form.steps ?? undefined,
    note: form.note || undefined,
  }

  const result = editingRecord.value
    ? await store.updateRecord(editingRecord.value.id, payload)
    : await store.createRecord(payload)

  if (result) {
    toast.add({ severity: 'success', summary: editingRecord.value ? 'Updated' : 'Saved', detail: 'Record saved successfully.', life: 3000 })
    showForm.value = false
  } else {
    formError.value = store.error || 'Failed to save record.'
  }
}

function confirmDelete(record: HealthRecord) {
  confirm.require({
    message: `Delete record for ${record.record_date}?`,
    header: 'Confirm Delete',
    icon: 'pi pi-exclamation-triangle',
    rejectLabel: 'Cancel',
    acceptLabel: 'Delete',
    acceptClass: 'p-button-danger',
    accept: async () => {
      const ok = await store.deleteRecord(record.id)
      if (ok) {
        toast.add({ severity: 'info', summary: 'Deleted', detail: 'Record deleted.', life: 3000 })
      }
    },
  })
}

async function loadRecords() {
  await store.fetchRecords({ ...store.query })
}

async function onPage(event: DataTablePageEvent) {
  await store.fetchRecords({ ...store.query, skip: event.first, limit: event.rows })
}

function dateFromRouteQuery(raw: unknown): Date | null {
  if (typeof raw !== 'string') return null
  if (raw === 'today') {
    const now = new Date()
    return new Date(
      `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}T00:00:00`,
    )
  }
  if (!/^\\d{4}-\\d{2}-\\d{2}$/.test(raw)) return null
  return new Date(`${raw}T00:00:00`)
}

watch(
  () => route.query.date,
  async (rawDate) => {
    const d = dateFromRouteQuery(rawDate)
    if (!d) return
    openForm(null)
    form.record_date = d
    await nextTick()
    const inputEl = weightInputRef.value?.$el?.querySelector('input') as HTMLInputElement | null
    inputEl?.focus()
    void router.replace({ query: { ...route.query, date: undefined } })
  },
  { immediate: true },
)

onMounted(loadRecords)
</script>

<style scoped>
.page-header-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}
.filter-card {
  margin-bottom: 1rem;
}
.filter-grid {
  align-items: end;
}
.filter-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.filter-field label {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--color-text-secondary);
}
.filter-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}
.record-form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}
.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.form-group label {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--color-text-secondary);
}
.form-error {
  color: var(--color-danger);
  font-size: 0.85rem;
  padding: 8px 12px;
  background: #fee2e2;
  border-radius: 6px;
}
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}
.table-card {
  padding: 0;
  overflow: hidden;
}
.table-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--color-border);
}
.table-count {
  font-size: 0.85rem;
  color: var(--color-text-secondary);
  font-weight: 500;
}
.row-actions {
  display: flex;
  gap: 2px;
  justify-content: flex-end;
}
@media (max-width: 640px) {
  .form-row {
    grid-template-columns: 1fr;
  }
  .filter-actions {
    flex-wrap: wrap;
  }
}
</style>
