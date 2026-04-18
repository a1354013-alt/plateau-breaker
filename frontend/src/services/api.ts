import axios from 'axios'

import type { components, paths } from '@/generated/api'

export function getApiBaseUrl(
  env: Pick<ImportMetaEnv, 'VITE_API_BASE_URL'> = import.meta.env,
): string {
  const raw = (env.VITE_API_BASE_URL ?? '').trim()
  if (!raw) return ''
  return raw.endsWith('/') ? raw.slice(0, -1) : raw
}

const api = axios.create({
  baseURL: getApiBaseUrl(),
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

type ApiPath = keyof paths

const API_PATHS = {
  healthRecords: '/api/health-records' as const satisfies ApiPath,
  analyticsDashboard: '/api/analytics/dashboard' as const satisfies ApiPath,
  analyticsTrends: '/api/analytics/trends' as const satisfies ApiPath,
  analyticsPlateau: '/api/analytics/plateau' as const satisfies ApiPath,
  analyticsReasons: '/api/analytics/reasons' as const satisfies ApiPath,
  analyticsSummary: '/api/analytics/summary' as const satisfies ApiPath,
  profile: '/api/profile' as const,
  weeklyReport: '/api/report/weekly' as const,
} as const

export type HealthRecord = components['schemas']['HealthRecordResponse']
export type HealthRecordCreate = components['schemas']['HealthRecordCreate']
export type HealthRecordUpdate = components['schemas']['HealthRecordUpdate']
export type HealthRecordListResponse = components['schemas']['HealthRecordListResponse']

export type DashboardData = components['schemas']['DashboardResponse']
export type TrendPoint = components['schemas']['TrendPoint']
export type TrendsData = components['schemas']['TrendsResponse']
export type PlateauData = components['schemas']['PlateauResponse']
export type ReasonItem = components['schemas']['ReasonItem']
export type ReasonsData = components['schemas']['ReasonsResponse'] & {
  missing_dates?: string[]
}

type SummaryPayloadBase = {
  text: string
  insight: string
  status: string
  top_reasons: string[]
}

export type FactorContribution = {
  factor: string
  impact_percent: number
  confidence: number
}

export type Recommendation = {
  priority: number
  message: string
  confidence: number
}

export type SummaryData = {
  plateau: PlateauData
  reasons: ReasonsData
  summary: SummaryPayloadBase & { factor_contributions?: FactorContribution[] }
  recommendations?: Recommendation[]
}

export type ProfileData = {
  id: number
  target_weight: number | null
  daily_calorie_target: number
  protein_target: number | null
  weekly_workout_target: number | null
  created_at: string
  updated_at: string
}

export type ProfileUpdate = {
  target_weight: number | null
  daily_calorie_target: number
  protein_target: number | null
  weekly_workout_target: number | null
}

export type WeeklyReportData = {
  summary: SummaryData['summary']
  metrics: DashboardData
  plateau_status: string
  reasons: ReasonItem[]
  recommendations: Recommendation[]
}

export const healthRecordsApi = {
  list(params?: { skip?: number; limit?: number; start_date?: string; end_date?: string }) {
    return api.get<HealthRecordListResponse>(API_PATHS.healthRecords, { params })
  },

  get(id: number) {
    return api.get<HealthRecord>(`${API_PATHS.healthRecords}/${id}`)
  },

  create(data: HealthRecordCreate) {
    return api.post<HealthRecord>(API_PATHS.healthRecords, data)
  },

  update(id: number, data: HealthRecordUpdate) {
    return api.put<HealthRecord>(`${API_PATHS.healthRecords}/${id}`, data)
  },

  delete(id: number) {
    return api.delete(`${API_PATHS.healthRecords}/${id}`)
  },
}

export const analyticsApi = {
  dashboard() {
    return api.get<DashboardData>(API_PATHS.analyticsDashboard)
  },

  trends(days: number = 30) {
    return api.get<TrendsData>(API_PATHS.analyticsTrends, { params: { days } })
  },

  plateau() {
    return api.get<PlateauData>(API_PATHS.analyticsPlateau)
  },

  reasons(calorieTarget: number) {
    return api.get<ReasonsData>(API_PATHS.analyticsReasons, {
      params: { calorie_target: calorieTarget },
    })
  },

  summary(calorieTarget?: number) {
    return api.get<SummaryData>(API_PATHS.analyticsSummary, {
      params: calorieTarget ? { calorie_target: calorieTarget } : {},
    })
  },

  weeklyReport() {
    return api.get<WeeklyReportData>(API_PATHS.weeklyReport)
  },
}

export const profileApi = {
  get() {
    return api.get<ProfileData>(API_PATHS.profile)
  },

  update(data: ProfileUpdate) {
    return api.put<ProfileData>(API_PATHS.profile, data)
  },
}

export default api
