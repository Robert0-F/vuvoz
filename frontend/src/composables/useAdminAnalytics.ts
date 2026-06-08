import { ref, reactive, computed } from 'vue'
import { api } from '@/api/axios'

export interface AnalyticsFilters {
  company_id: number | null
  company_name: string | null
  institution_id: number | null
  institution_name: string | null
  institution_type: string | null
  material_type: string | null
  material_type_display: string | null
}

export interface KpiCard {
  key: string
  label: string
  value: string | number
  trend?: number | null
  icon?: string
  color?: string
}

export interface AnalyticsData {
  period: { date_from: string; date_to: string; basis: string }
  filters?: AnalyticsFilters
  kpis: Record<string, number | boolean>
  materials: { material_type: string; material_type_display: string; total_kg: number; request_count: number }[]
  top_companies: { company_id: number; company_name: string; total_kg: number; request_count: number }[]
  institutions_per_company: { company_id: number; company_name: string; institution_count: number }[]
  top_organizations: { institution_id: number; institution_name: string; institution_type: string; total_kg: number; request_count: number }[]
  institution_type_breakdown: { institution_type: string; total_kg: number; request_count: number }[]
  requests_by_status: { status: string; status_display: string; count: number }[]
  weight_over_time: { period_label: string; date_start: string; total_kg: number }[]
  requests_over_time: { period_label: string; date_start: string; count: number }[]
  completion_rate_by_company: { company_id: number; company_name: string; total: number; completed: number; completion_rate_percent: number }[]
  avg_completion_hours: number | null
  bonus_over_time: { period_label: string; total_points: number }[]
  top_point_institutions: { institution_id: number; institution_name: string; total_points: number }[]
  popular_products: { product_id: number; product_name: string; total_quantity: number; order_count: number }[]
  requests_insights: {
    funnel: { status: string; label: string; count: number; percent: number }[]
    backlog: { new: number; accepted: number; total: number }
    urgency_breakdown: { urgency: string; urgency_display: string; count: number }[]
    completion_time_buckets: { bucket: string; label: string; count: number }[]
    estimated_vs_actual: {
      request_count: number
      total_estimated_kg: number
      total_actual_kg: number
      avg_estimated_kg: number
      avg_actual_kg: number
      deviation_percent: number
    }
    status_over_time: { period_label: string; new: number; accepted: number; completed: number; cancelled: number }[]
  }
  public_pickup: {
    kpis: { total_period: number; new: number; done: number; total_kg: number; total_payout: number }
    by_status: { status: string; status_display: string; count: number }[]
    materials: { material_type: string; material_type_display: string; total_kg: number; request_count: number }[]
    over_time: { period_label: string; count: number }[]
  }
}

export interface FilterOption { title: string; value: string }
export interface InstitutionOption { id: number; institution_name: string; parent_company: number }

export function formatKg(n: number) {
  if (n >= 1000) return (n / 1000).toFixed(1) + ' т'
  return String(Math.round(n))
}

export function formatNum(n: number) {
  return new Intl.NumberFormat('ru-RU').format(Math.round(n))
}

export function formatRuDate(iso: string) {
  if (!iso) return '—'
  const [y, m, d] = iso.split('-')
  return `${d}.${m}.${y}`
}

export function formatPeriodLabel(period?: { date_from: string; date_to: string; basis: string }) {
  if (!period) return ''
  const basis = period.basis === 'completed' ? 'по дате завершения' : 'по дате создания'
  return `${formatRuDate(period.date_from)} — ${formatRuDate(period.date_to)} (${basis})`
}

export function useAdminAnalytics() {
  const loading = ref(false)
  const error = ref('')
  const data = ref<AnalyticsData | null>(null)
  const sectionTab = ref('summary')
  const datePreset = ref('year')
  const filtersExpanded = ref(false)

  const filters = reactive({
    date_from: '',
    date_to: '',
    basis: 'created',
    company_id: '',
    institution_id: '',
    institution_type: '',
    material_type: '',
  })

  const allInstitutions = ref<InstitutionOption[]>([])
  const companyFilterItems = ref<FilterOption[]>([{ title: 'Все компании', value: '' }])
  const materialFilterItems = ref<FilterOption[]>([{ title: 'Все материалы', value: '' }])

  const datePresetItems = [
    { title: 'Неделя', value: 'week' },
    { title: 'Месяц', value: 'month' },
    { title: 'Квартал', value: 'quarter' },
    { title: 'Год', value: 'year' },
    { title: 'Свой', value: 'custom' },
  ]
  const basisItems = [
    { title: 'По дате создания', value: 'created' },
    { title: 'По дате завершения', value: 'completed' },
  ]

  const institutionFilterItems = computed(() => {
    let list = allInstitutions.value
    if (filters.company_id) {
      list = list.filter((i) => String(i.parent_company) === filters.company_id)
    }
    return [
      { title: 'Все организации', value: '' },
      ...list.map((i) => ({ title: i.institution_name, value: String(i.id) })),
    ]
  })

  const activeFilterChips = computed(() => {
    const chips: { key: string; label: string }[] = []
    if (filters.company_id) {
      const name = companyFilterItems.value.find((c) => c.value === filters.company_id)?.title
      if (name && name !== 'Все компании') chips.push({ key: 'company_id', label: `Компания: ${name}` })
    }
    if (filters.institution_id) {
      const name = institutionFilterItems.value.find((i) => i.value === filters.institution_id)?.title
      if (name && name !== 'Все организации') chips.push({ key: 'institution_id', label: `Организация: ${name}` })
    }
    if (filters.material_type) {
      const name = materialFilterItems.value.find((m) => m.value === filters.material_type)?.title
      if (name) chips.push({ key: 'material_type', label: `Материал: ${name}` })
    }
    if (filters.institution_type) {
      chips.push({ key: 'institution_type', label: `Тип: ${filters.institution_type}` })
    }
    return chips
  })

  const completionSummary = computed(() => {
    const statuses = data.value?.requests_by_status ?? []
    const total = statuses.reduce((sum, s) => sum + s.count, 0)
    const completed = statuses.find((s) => s.status === 'completed')?.count ?? 0
    return { total, completed, percent: total ? Math.round((completed / total) * 100) : 0 }
  })

  function applyDatePreset(preset: string) {
    const end = new Date()
    const start = new Date()
    if (preset === 'week') start.setDate(start.getDate() - 7)
    else if (preset === 'month') start.setMonth(start.getMonth() - 1)
    else if (preset === 'quarter') start.setMonth(start.getMonth() - 3)
    else if (preset === 'year') start.setFullYear(start.getFullYear() - 1)
    else return
    filters.date_from = start.toISOString().slice(0, 10)
    filters.date_to = end.toISOString().slice(0, 10)
  }

  function onCompanyFilterChange() {
    if (!filters.institution_id) return
    const stillValid = institutionFilterItems.value.some((i) => i.value === filters.institution_id)
    if (!stillValid) filters.institution_id = ''
  }

  function removeFilterChip(key: string) {
    if (key in filters) (filters as Record<string, string>)[key] = ''
    loadAnalytics()
  }

  function resetFilters() {
    filters.company_id = ''
    filters.institution_id = ''
    filters.institution_type = ''
    filters.material_type = ''
    filters.basis = 'created'
    datePreset.value = 'year'
    applyDatePreset('year')
    loadAnalytics()
  }

  function drillDownCompany(companyId: number) {
    filters.company_id = String(companyId)
    filters.institution_id = ''
    filtersExpanded.value = true
    sectionTab.value = 'partners'
    loadAnalytics()
  }

  function drillDownInstitution(institutionId: number) {
    const inst = allInstitutions.value.find((i) => i.id === institutionId)
    if (inst) filters.company_id = String(inst.parent_company)
    filters.institution_id = String(institutionId)
    filtersExpanded.value = true
    sectionTab.value = 'partners'
    loadAnalytics()
  }

  async function loadCompaniesForFilter() {
    try {
      const { data: list } = await api.get<{ id: number; company_name: string }[]>('/company-profiles/')
      companyFilterItems.value = [
        { title: 'Все компании', value: '' },
        ...list.map((c) => ({ title: c.company_name, value: String(c.id) })),
      ]
    } catch {
      companyFilterItems.value = [{ title: 'Все компании', value: '' }]
    }
  }

  async function loadInstitutionsForFilter() {
    try {
      const { data: list } = await api.get<InstitutionOption[]>('/institutions/')
      allInstitutions.value = list.map((i) => ({
        id: i.id,
        institution_name: i.institution_name,
        parent_company: i.parent_company,
      }))
    } catch {
      allInstitutions.value = []
    }
  }

  async function loadMaterialsForFilter() {
    try {
      const { data: list } = await api.get<{ code: string; name: string }[]>('/materials/')
      materialFilterItems.value = [
        { title: 'Все материалы', value: '' },
        ...list.map((m) => ({ title: m.name, value: m.code })),
      ]
    } catch {
      materialFilterItems.value = [{ title: 'Все материалы', value: '' }]
    }
  }

  async function loadAnalytics() {
    loading.value = true
    error.value = ''
    try {
      const params: Record<string, string> = {
        date_from: filters.date_from,
        date_to: filters.date_to,
        basis: filters.basis,
      }
      if (filters.company_id) params.company_id = filters.company_id
      if (filters.institution_id) params.institution_id = filters.institution_id
      if (filters.institution_type) params.institution_type = filters.institution_type
      if (filters.material_type) params.material_type = filters.material_type
      const { data: res } = await api.get<AnalyticsData>('/analytics/dashboard/', { params })
      data.value = res
    } catch (e: unknown) {
      const ax = e as { response?: { data?: { detail?: string } } }
      error.value = ax.response?.data?.detail ?? 'Ошибка загрузки аналитики'
    } finally {
      loading.value = false
    }
  }

  function init() {
    applyDatePreset('year')
    loadCompaniesForFilter()
    loadInstitutionsForFilter()
    loadMaterialsForFilter()
    loadAnalytics()
  }

  return {
    loading,
    error,
    data,
    sectionTab,
    datePreset,
    filtersExpanded,
    filters,
    datePresetItems,
    basisItems,
    companyFilterItems,
    materialFilterItems,
    institutionFilterItems,
    activeFilterChips,
    completionSummary,
    applyDatePreset,
    onCompanyFilterChange,
    removeFilterChip,
    resetFilters,
    drillDownCompany,
    drillDownInstitution,
    loadAnalytics,
    init,
  }
}
