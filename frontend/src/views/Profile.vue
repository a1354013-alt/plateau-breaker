<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">Profile & Goals</h1>
      <p class="page-subtitle">Set your goals so analysis can personalize recommendations.</p>
    </div>

    <StatePanel v-if="loading && !loaded" variant="loading" title="Loading profile..." message="Fetching your goal settings." />

    <StatePanel v-else-if="error && !loaded" variant="error" title="Couldn't load profile" :message="error">
      <template #action>
        <Button label="Retry" icon="pi pi-refresh" severity="secondary" outlined @click="load" />
      </template>
    </StatePanel>

    <form v-else class="card profile-form" @submit.prevent="save">
      <div class="grid-2">
        <div class="field">
          <label>Target Weight (kg)</label>
          <InputNumber v-model="form.target_weight" :min="20" :max="500" :minFractionDigits="1" :maxFractionDigits="1" fluid />
        </div>
        <div class="field">
          <label>Daily Calories</label>
          <InputNumber v-model="form.daily_calorie_target" :min="1000" :max="5000" fluid />
        </div>
        <div class="field">
          <label>Protein Target (g)</label>
          <InputNumber v-model="form.protein_target" :min="0" :max="500" fluid />
        </div>
        <div class="field">
          <label>Workout Target (days/week)</label>
          <InputNumber v-model="form.weekly_workout_target" :min="0" :max="50" fluid />
        </div>
      </div>

      <div class="actions">
        <Button type="button" label="Reset" severity="secondary" outlined @click="load" />
        <Button type="submit" label="Save Goals" :loading="saving" />
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useToast } from 'primevue/usetoast'
import Button from 'primevue/button'
import InputNumber from 'primevue/inputnumber'

import StatePanel from '@/components/StatePanel.vue'
import { profileApi, type ProfileUpdate } from '@/services/api'
import { getApiErrorMessage } from '@/services/errors'

const toast = useToast()
const loading = ref(false)
const loaded = ref(false)
const saving = ref(false)
const error = ref<string | null>(null)

const form = reactive<ProfileUpdate>({
  target_weight: null,
  daily_calorie_target: 2000,
  protein_target: null,
  weekly_workout_target: null,
})

async function load() {
  loading.value = true
  error.value = null
  try {
    const res = await profileApi.get()
    Object.assign(form, {
      target_weight: res.data.target_weight,
      daily_calorie_target: res.data.daily_calorie_target,
      protein_target: res.data.protein_target,
      weekly_workout_target: res.data.weekly_workout_target,
    })
    loaded.value = true
  } catch (e: unknown) {
    error.value = getApiErrorMessage(e, 'Failed to load profile')
  } finally {
    loading.value = false
  }
}

async function save() {
  saving.value = true
  error.value = null
  try {
    await profileApi.update({ ...form })
    toast.add({ severity: 'success', summary: 'Saved', detail: 'Profile goals updated.', life: 3000 })
    loaded.value = true
  } catch (e: unknown) {
    error.value = getApiErrorMessage(e, 'Failed to save profile')
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.profile-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.field label {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--color-text-secondary);
}
.actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}
</style>
