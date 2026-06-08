import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/api/axios'
import type { CollectionRequest, InstitutionProfile } from '@/types'

export interface DashboardKpis {
  new_requests: number
  active_requests: number
  completed_this_month: number
  weight_kg_this_month: number
  institutions_count: number
  requests_by_status: { new: number; accepted: number; completed: number }
}

export interface MonthlyWeight {
  month: string
  weight_kg: number
}

export interface MaterialBreakdownItem {
  material_type: string
  material_type_display: string
  weight_kg: number
}

export interface CompanyDashboardData {
  new_requests: number
  active_requests: number
  completed_this_month: number
  weight_kg_this_month: number
  institutions_count: number
  monthly_weights: MonthlyWeight[]
  material_breakdown: MaterialBreakdownItem[]
  requests_by_status: { new: number; accepted: number; completed: number }
  selected_month?: string
  month_start?: string
  month_end?: string
}

export const useCompanyDashboardStore = defineStore('companyDashboard', () => {
  const requests = ref<CollectionRequest[]>([])
  const institutions = ref<InstitutionProfile[]>([])
  const dashboard = ref<CompanyDashboardData | null>(null)
  const loadingRequests = ref(false)
  const loadingInstitutions = ref(false)
  const loadingDashboard = ref(false)
  const dashboardError = ref<string | null>(null)
  const dashboardMonth = ref('')

  const newRequests = computed(() => requests.value.filter((r) => r.status === 'new'))
  const activeRequests = computed(() => requests.value.filter((r) => r.status === 'accepted'))
  const completedRequests = computed(() => requests.value.filter((r) => r.status === 'completed'))

  async function fetchRequests() {
    loadingRequests.value = true
    try {
      const { data } = await api.get<CollectionRequest[]>('/collection-requests/')
      requests.value = data
      return data
    } finally {
      loadingRequests.value = false
    }
  }

  async function fetchInstitutions() {
    loadingInstitutions.value = true
    try {
      const { data } = await api.get<InstitutionProfile[]>('/institutions/')
      institutions.value = data
      return data
    } finally {
      loadingInstitutions.value = false
    }
  }

  function defaultMonth() {
    const d = new Date()
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
  }

  async function fetchDashboard(month?: string) {
    loadingDashboard.value = true
    dashboardError.value = null
    const m = month || dashboardMonth.value || defaultMonth()
    dashboardMonth.value = m
    try {
      const { data } = await api.get<CompanyDashboardData>('/stats/company/dashboard/', {
        params: { month: m },
      })
      dashboard.value = data
      return data
    } catch (e) {
      dashboardError.value = e instanceof Error ? e.message : 'Не удалось загрузить статистику'
      return null
    } finally {
      loadingDashboard.value = false
    }
  }

  /** Load all dashboard data (requests, institutions, KPIs/charts). */
  async function loadAll() {
    await Promise.all([fetchRequests(), fetchInstitutions(), fetchDashboard()])
  }

  /** Refresh only KPIs (e.g. for polling new request count). */
  async function refreshKpis() {
    const data = await fetchDashboard()
    return data
  }

  function clearDashboardError() {
    dashboardError.value = null
  }

  return {
    requests,
    institutions,
    dashboard,
    loadingRequests,
    loadingInstitutions,
    loadingDashboard,
    dashboardError,
    newRequests,
    activeRequests,
    completedRequests,
    fetchRequests,
    fetchInstitutions,
    fetchDashboard,
    loadAll,
    refreshKpis,
    clearDashboardError,
    dashboardMonth,
    defaultMonth,
  }
})
