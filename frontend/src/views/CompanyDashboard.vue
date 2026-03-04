<template>
  <div class="company-dashboard">
    <v-app-bar color="primary" density="compact" class="company-dashboard__app-bar">
      <v-app-bar-title class="pl-2">Операционный центр</v-app-bar-title>
      <v-spacer />
      <v-btn variant="text" icon="mdi-refresh" :loading="refreshing" @click="handleRefresh" />
      <v-menu location="bottom">
        <template #activator="{ props: menuProps }">
          <v-btn v-bind="menuProps" variant="text" icon="mdi-bell">
            <v-badge v-if="unreadCount > 0" :content="unreadCount" color="error" />
          </v-btn>
        </template>
        <v-list max-height="320" style="overflow-y: auto">
          <v-list-item
            v-for="n in notifications"
            :key="n.id"
            :title="n.title"
            :subtitle="n.message"
            :class="{ 'bg-grey-lighten-3': !n.read }"
            @click="markNotificationRead(n.id)"
          />
          <v-list-item v-if="!notifications.length" title="Нет уведомлений" />
          <v-list-item v-if="notifications.length" title="Прочитать все" @click="markAllNotificationsRead" />
        </v-list>
      </v-menu>
      <span class="mr-2 text-body-2">{{ userStore.user?.username }}</span>
      <v-btn variant="text" icon="mdi-logout" @click="logout" />
    </v-app-bar>

    <v-main class="company-dashboard__main">
      <v-container fluid class="pa-4">
        <!-- Stats load error -->
        <v-alert
          v-if="store.dashboardError"
          type="warning"
          density="compact"
          closable
          class="mb-4"
          @click:close="store.clearDashboardError"
        >
          {{ store.dashboardError }}
          <template #append>
            <v-btn size="small" variant="text" @click="retryDashboard">Повторить</v-btn>
          </template>
        </v-alert>

        <!-- KPI Header -->
        <section class="company-dashboard__kpis mb-6">
          <v-row dense>
            <v-col cols="12" sm="6" md="4" lg="2">
              <company-stats-widget
                title="Новые заявки"
                :value="kpiNewRequests"
                icon="mdi-inbox"
                :pulse="(dashboard?.new_requests ?? 0) > 0"
              />
            </v-col>
            <v-col cols="12" sm="6" md="4" lg="2">
              <company-stats-widget
                title="В работе"
                :value="kpiActiveRequests"
                icon="mdi-progress-clock"
              />
            </v-col>
            <v-col cols="12" sm="6" md="4" lg="2">
              <company-stats-widget
                title="Завершено за месяц"
                :value="kpiCompletedMonth"
                icon="mdi-check-circle-multiple"
              />
            </v-col>
            <v-col cols="12" sm="6" md="4" lg="2">
              <company-stats-widget
                title="Вес за месяц (кг)"
                :value="kpiWeightMonth"
                icon="mdi-weight-kilogram"
              />
            </v-col>
            <v-col cols="12" sm="6" md="4" lg="2">
              <company-stats-widget
                title="Организаций"
                :value="kpiInstitutions"
                icon="mdi-domain"
              />
            </v-col>
          </v-row>
        </section>

        <!-- Tabs: Requests (primary), Institutions, Statistics -->
        <v-tabs v-model="activeTab" class="company-dashboard__tabs mb-4" color="primary" show-arrows>
          <v-tab value="requests">Заявки</v-tab>
          <v-tab value="institutions">Организации</v-tab>
          <v-tab value="statistics">Статистика</v-tab>
        </v-tabs>

        <v-window v-model="activeTab">
          <!-- Request Inbox -->
          <v-window-item value="requests" class="company-dashboard__window-item">
            <v-card class="rounded-lg" elevation="0" border>
              <v-tabs v-model="requestSubTab" density="compact" class="px-3 pt-2">
                <v-tab value="new">Новые ({{ newRequests.length }})</v-tab>
                <v-tab value="active">В работе ({{ activeRequests.length }})</v-tab>
                <v-tab value="all">Все заявки</v-tab>
              </v-tabs>
              <v-window v-model="requestSubTab" class="mt-0">
                <v-window-item value="new">
                  <div class="pa-4">
                    <div v-if="loadingRequests" class="d-flex justify-center py-8">
                      <v-progress-circular indeterminate color="primary" />
                    </div>
                    <div v-if="!loadingRequests && newRequests.length === 0" class="text-center py-8 text-medium-emphasis">
                      Нет новых заявок
                    </div>
                    <v-row v-else dense class="request-cards-grid">
                      <v-col v-for="r in newRequestsSorted" :key="r.id" cols="12" sm="6" md="4">
                        <company-request-card
                          :request="r"
                          @accept="openAcceptDialog"
                          @view-details="openRequestDetail"
                          @view-institution="openInstitutionByRequest"
                        />
                      </v-col>
                    </v-row>
                  </div>
                </v-window-item>
                <v-window-item value="active">
                  <div class="pa-4">
                    <div v-if="loadingRequests" class="d-flex justify-center py-8">
                      <v-progress-circular indeterminate color="primary" />
                    </div>
                    <div v-else-if="activeRequests.length === 0" class="text-center py-8 text-medium-emphasis">
                      Нет заявок в работе
                    </div>
                    <v-row v-else dense class="request-cards-grid">
                      <v-col v-for="r in activeRequestsSorted" :key="r.id" cols="12" sm="6" md="4">
                        <company-request-card
                          :request="r"
                          @complete="openCompleteDialog"
                          @view-details="openRequestDetail"
                          @view-institution="openInstitutionByRequest"
                        />
                      </v-col>
                    </v-row>
                  </div>
                </v-window-item>
                <v-window-item value="all">
                  <company-request-table
                    :requests="requests"
                    :loading="loadingRequests"
                    :institution-id-filter="institutionIdFilter"
                    @view-details="openRequestDetail"
                    @view-institution="openInstitutionByRequest"
                    @accept="openAcceptDialog"
                    @complete="openCompleteDialog"
                    @clear-institution-filter="institutionIdFilter = null"
                  />
                </v-window-item>
              </v-window>
            </v-card>
          </v-window-item>

          <!-- Institutions (read-only) -->
          <v-window-item value="institutions" class="company-dashboard__window-item">
            <v-card class="rounded-lg" elevation="0" border>
              <v-card-title class="d-flex flex-wrap align-center ga-2 py-3">
                Организации
                <v-spacer />
                <v-text-field
                  v-model="institutionSearch"
                  placeholder="Поиск по названию..."
                  density="compact"
                  hide-details
                  clearable
                  variant="outlined"
                  class="company-dashboard__inst-search"
                  prepend-inner-icon="mdi-magnify"
                />
              </v-card-title>
              <v-divider />
              <div v-if="loadingInstitutions" class="d-flex justify-center py-8">
                <v-progress-circular indeterminate color="primary" />
              </div>
              <v-card-text v-else class="pt-4">
                <v-row dense>
                  <v-col v-for="inst in filteredInstitutions" :key="inst.id" cols="12" sm="6" md="4">
                    <company-institution-card
                      :institution="inst"
                      :request-count="institutionRequestCount(inst.id)"
                      :last-request-date="institutionLastRequestDate(inst.id)"
                      @click="openInstitutionProfile(inst)"
                    />
                  </v-col>
                </v-row>
                <p v-if="!filteredInstitutions.length" class="text-center text-medium-emphasis py-6">
                  Нет организаций
                </p>
              </v-card-text>
            </v-card>
          </v-window-item>

          <!-- Statistics -->
          <v-window-item value="statistics" class="company-dashboard__window-item">
            <v-card class="rounded-lg" elevation="0" border>
              <v-card-title class="d-flex flex-wrap align-center ga-2 py-3">
                Статистика
                <company-date-range-picker @change="onStatsRangeChange" />
              </v-card-title>
              <v-divider />
              <v-card-text class="pt-4">
                <v-row>
                  <v-col cols="12" md="6">
                    <div class="text-subtitle-2 mb-2">Объём по месяцам (кг)</div>
                    <div class="chart-wrap">
                      <canvas ref="monthlyChartRef" height="220" />
                    </div>
                  </v-col>
                  <v-col cols="12" md="6">
                    <div class="text-subtitle-2 mb-2">По типам материала</div>
                    <div class="chart-wrap">
                      <canvas ref="materialChartRef" height="220" />
                    </div>
                    <p v-if="!(dashboard?.material_breakdown?.length) && dashboard" class="text-caption text-medium-emphasis mt-2">
                      Нет данных за выбранный период
                    </p>
                  </v-col>
                  <v-col cols="12" md="6">
                    <div class="text-subtitle-2 mb-2">По статусам заявок</div>
                    <div class="chart-wrap">
                      <canvas ref="statusChartRef" height="200" />
                    </div>
                  </v-col>
                </v-row>
              </v-card-text>
            </v-card>
          </v-window-item>
        </v-window>
      </v-container>
    </v-main>

    <!-- Modals -->
    <company-request-detail-modal
      v-model="requestDetailOpen"
      :request="selectedRequest"
      :fullscreen="fullscreenModal"
      @accept="openAcceptDialog"
      @complete="openCompleteDialog"
      @view-institution="openInstitutionByRequest"
      @saved="handleRequestSaved"
    />
    <company-institution-profile-modal
      v-model="institutionProfileOpen"
      :institution="selectedInstitution"
      :fullscreen="fullscreenModal"
      @view-requests="filterRequestsByInstitution"
    />

    <!-- Status / Complete dialog (reused from original) -->
    <v-dialog v-model="statusDialog" :max-width="fullscreenModal ? undefined : 500" :fullscreen="fullscreenModal" persistent transition="dialog-bottom-transition">
      <v-card v-if="selectedRequest">
        <v-card-title>{{ statusUpdate === 'completed' ? 'Завершить заявку' : 'Изменить статус' }}</v-card-title>
        <v-card-text>
          <template v-if="statusUpdate !== 'completed'">
            <v-select v-model="statusUpdate" :items="statusItems" label="Статус" variant="outlined" class="mb-3" />
            <v-text-field v-model="statusUpdateEstimatedDate" label="Предполагаемая дата вывоза" type="date" variant="outlined" density="comfortable" class="mb-3" hint="Опционально: когда планируете вывезти" persistent-hint />
            <v-text-field v-model="statusUpdateActualDate" label="Фактическая дата вывоза" type="date" variant="outlined" density="comfortable" class="mb-3" hint="Опционально: можно указать позже в карточке заявки" persistent-hint />
            <v-textarea v-model="statusUpdateNotes" label="Внутренние заметки" variant="outlined" rows="2" />
          </template>
          <template v-else>
            <p v-if="hasMultipleMaterials" class="text-body-2 text-medium-emphasis mb-3">
              Укажите фактический вес (кг) по каждому типу сырья.
            </p>
            <template v-if="hasMultipleMaterials">
              <div v-for="(line, idx) in completeActualMaterialLines" :key="idx" class="mb-3">
                <v-text-field
                  v-model="line.amount_kg"
                  :label="`${materialTypeLabel(line.material_type)} — вес (кг) *`"
                  type="number"
                  min="0"
                  step="0.01"
                  variant="outlined"
                  density="comfortable"
                  :error-messages="completeErrors[`line_${idx}`]"
                />
              </div>
            </template>
            <v-text-field
              v-else
              v-model="completeActualAmount"
              label="Фактический вес (кг) *"
              type="number"
              min="1"
              step="0.01"
              variant="outlined"
              density="comfortable"
              :error-messages="completeErrors.actual_amount"
              class="mb-3"
            />
            <v-text-field v-model="completeActualDate" label="Дата вывоза" type="date" variant="outlined" density="comfortable" class="mb-3" />
            <v-textarea v-model="completeInternalNotes" label="Внутренние заметки" variant="outlined" rows="2" />
            <p v-if="completeActualValue != null" class="text-body-2 mt-2">Стоимость: <strong>{{ completeActualValue }} руб.</strong></p>
          </template>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="statusDialog = false">Отмена</v-btn>
          <v-btn color="primary" :loading="updatingStatus" @click="saveStatus">Сохранить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import Chart from 'chart.js/auto'
import { api } from '@/api/axios'
import { useAuthStore } from '@/stores/auth'
import { useUserStore } from '@/stores/user'
import { useCompanyDashboardStore } from '@/stores/companyDashboard'
import { useBreakpoints } from '@/composables/useBreakpoints'
import CompanyStatsWidget from '@/components/company/StatsWidget.vue'
import CompanyDateRangePicker from '@/components/company/DateRangePicker.vue'
import CompanyRequestCard from '@/components/company/RequestCard.vue'
import CompanyRequestTable from '@/components/company/RequestTable.vue'
import CompanyRequestDetailModal from '@/components/company/RequestDetailModal.vue'
import CompanyInstitutionCard from '@/components/company/InstitutionCard.vue'
import CompanyInstitutionProfileModal from '@/components/company/InstitutionProfileModal.vue'
import type { CollectionRequest, InstitutionProfile } from '@/types'

const router = useRouter()
const authStore = useAuthStore()
const userStore = useUserStore()
const store = useCompanyDashboardStore()
const { fullscreenModal } = useBreakpoints()

const requests = computed(() => store.requests)
const institutions = computed(() => store.institutions)
const dashboard = computed(() => store.dashboard)
const loadingRequests = computed(() => store.loadingRequests)
const loadingInstitutions = computed(() => store.loadingInstitutions)
const newRequests = computed(() => store.newRequests)
const activeRequests = computed(() => store.activeRequests)

const newRequestsSorted = computed(() => [...newRequests.value].sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()))
const activeRequestsSorted = computed(() => [...activeRequests.value].sort((a, b) => (a.desired_date && b.desired_date ? new Date(a.desired_date).getTime() - new Date(b.desired_date).getTime() : 0)))

const kpiNewRequests = computed(() => dashboard.value?.new_requests ?? newRequests.value.length)
const kpiActiveRequests = computed(() => dashboard.value?.active_requests ?? activeRequests.value.length)
const kpiCompletedMonth = computed(() => dashboard.value?.completed_this_month ?? 0)
const kpiWeightMonth = computed(() => formatWeight(dashboard.value?.weight_kg_this_month))
const kpiInstitutions = computed(() => dashboard.value?.institutions_count ?? institutions.value.length)

const activeTab = ref('requests')
const institutionIdFilter = ref<number | null>(null)
const requestSubTab = ref('new')
const institutionSearch = ref('')
const refreshing = ref(false)

const requestDetailOpen = ref(false)
const selectedRequest = ref<CollectionRequest | null>(null)
const institutionProfileOpen = ref(false)
const selectedInstitution = ref<InstitutionProfile | null>(null)

const statusDialog = ref(false)
const statusUpdate = ref('')
const statusUpdateEstimatedDate = ref('')
const statusUpdateActualDate = ref('')
const statusUpdateNotes = ref('')
const completeActualAmount = ref('')
const completeActualMaterialLines = ref<{ material_type: string; amount_kg: string }[]>([])
const completeActualDate = ref('')
const completeInternalNotes = ref('')
const completeErrors = reactive<{ actual_amount?: string; [k: string]: string | undefined }>({})
const updatingStatus = ref(false)
const completeActualValue = ref<string | null>(null)

const notifications = ref<{ id: number; title: string; message: string; read: boolean }[]>([])
const unreadCount = ref(0)

const statusItems = [
  { title: 'Новый', value: 'new' },
  { title: 'Принятый', value: 'accepted' },
  { title: 'Завершённый', value: 'completed' },
]

const materialTypeLabels: Record<string, string> = {
  cardboard: 'Картон',
  paper: 'Макулатура',
  canisters: 'Канистры/флаконы',
  polyethylene: 'Полиэтилен/стрейч пленка',
  metal: 'Металл бытовой',
  glass: 'Стекло (бутылки)',
}

function materialTypeLabel(code: string) {
  return materialTypeLabels[code] || code
}

const hasMultipleMaterials = computed(() => {
  const lines = selectedRequest.value?.material_lines
  return Array.isArray(lines) && lines.length > 1
})

const filteredInstitutions = computed(() => {
  let list = institutions.value
  const q = (institutionSearch.value || '').trim().toLowerCase()
  if (q) list = list.filter((i) => (i.institution_name || '').toLowerCase().includes(q))
  return list
})

function institutionRequestCount(instId: number) {
  return requests.value.filter((r) => r.institution === instId).length
}

function institutionLastRequestDate(instId: number) {
  const list = requests.value.filter((r) => r.institution === instId)
  if (!list.length) return ''
  const sorted = [...list].sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
  return sorted[0].created_at
}

function formatWeight(v: number | undefined) {
  if (v == null) return '0'
  return Number(v).toLocaleString('ru-RU', { maximumFractionDigits: 1 })
}

let pollInterval: ReturnType<typeof setInterval> | null = null
const monthlyChartRef = ref<HTMLCanvasElement | null>(null)
const materialChartRef = ref<HTMLCanvasElement | null>(null)
const statusChartRef = ref<HTMLCanvasElement | null>(null)
let monthlyChart: Chart | null = null
let materialChart: Chart | null = null
let statusChart: Chart | null = null

function onStatsRangeChange(_payload: { startDate: string; endDate: string }) {
  // Dashboard API returns fixed current data; charts use dashboard.monthly_weights etc.
  buildCharts()
}

function buildCharts() {
  const d = store.dashboard
  if (!d) return

  const weights = d.monthly_weights ?? []
  if (monthlyChartRef.value && weights.length > 0) {
    if (monthlyChart) monthlyChart.destroy()
    monthlyChart = new Chart(monthlyChartRef.value, {
      type: 'bar',
      data: {
        labels: weights.map((x) => x.month),
        datasets: [{ label: 'кг', data: weights.map((x) => Number(x.weight_kg)), backgroundColor: 'rgba(13, 148, 136, 0.6)' }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true } },
      },
    })
  }

  const breakdown = d.material_breakdown ?? []
  if (materialChartRef.value) {
    if (materialChart) materialChart.destroy()
    if (breakdown.length > 0) {
      const colors = ['#0d9488', '#14b8a6', '#2dd4bf', '#5eead4', '#99f6e4', '#ccfbf1']
      materialChart = new Chart(materialChartRef.value, {
        type: 'doughnut',
        data: {
          labels: breakdown.map((x) => x.material_type_display),
          datasets: [{ data: breakdown.map((x) => Number(x.weight_kg)), backgroundColor: colors }],
        },
        options: { responsive: true, maintainAspectRatio: false },
      })
    }
  }

  if (statusChartRef.value && d.requests_by_status) {
    if (statusChart) statusChart.destroy()
    const rs = d.requests_by_status
    statusChart = new Chart(statusChartRef.value, {
      type: 'pie',
      data: {
        labels: ['Новые', 'Принятые', 'Завершённые'],
        datasets: [{
          data: [Number(rs.new ?? 0), Number(rs.accepted ?? 0), Number(rs.completed ?? 0)],
          backgroundColor: ['#eab308', '#0ea5e9', '#22c55e'],
        }],
      },
      options: { responsive: true, maintainAspectRatio: false },
    })
  }
}

function openRequestDetail(r: CollectionRequest) {
  selectedRequest.value = r
  requestDetailOpen.value = true
}

function openInstitutionProfile(inst: InstitutionProfile) {
  selectedInstitution.value = inst
  institutionProfileOpen.value = true
}

function openInstitutionByRequest(r: CollectionRequest) {
  const inst = institutions.value.find((i) => i.id === r.institution)
  if (inst) openInstitutionProfile(inst)
}

function filterRequestsByInstitution(inst: InstitutionProfile) {
  institutionProfileOpen.value = false
  activeTab.value = 'requests'
  requestSubTab.value = 'all'
  institutionIdFilter.value = inst.id
}

function openAcceptDialog(r: CollectionRequest) {
  selectedRequest.value = r
  statusUpdate.value = 'accepted'
  statusUpdateEstimatedDate.value = r.estimated_collection_date || r.desired_date?.slice(0, 10) || ''
  statusUpdateActualDate.value = r.actual_collection_date?.slice(0, 10) || ''
  statusUpdateNotes.value = r.notes || ''
  statusDialog.value = true
  requestDetailOpen.value = false
}

function openCompleteDialog(r: CollectionRequest) {
  selectedRequest.value = r
  statusUpdate.value = 'completed'
  completeActualDate.value = r.actual_collection_date ?? ''
  completeInternalNotes.value = r.internal_notes ?? ''
  completeErrors.actual_amount = ''
  Object.keys(completeErrors).forEach((k) => { completeErrors[k] = '' })
  completeActualValue.value = r.actual_value ?? null
  const lines = r.material_lines
  if (Array.isArray(lines) && lines.length > 1) {
    completeActualMaterialLines.value = lines.map((l) => ({ material_type: l.material_type, amount_kg: l.amount_kg ?? '' }))
    completeActualAmount.value = ''
  } else {
    completeActualMaterialLines.value = []
    completeActualAmount.value = r.actual_amount ?? ''
  }
  statusDialog.value = true
  requestDetailOpen.value = false
}

watch([() => selectedRequest.value?.id, statusUpdate, completeActualAmount, () => completeActualMaterialLines.value.map((l) => l.amount_kg).join(',')], async () => {
  if (statusUpdate.value !== 'completed' || !selectedRequest.value) {
    completeActualValue.value = null
    return
  }
  if (hasMultipleMaterials.value) {
    const lines = completeActualMaterialLines.value
    const total = lines.reduce((sum, l) => sum + (parseFloat(String(l.amount_kg)) || 0), 0)
    if (total <= 0) { completeActualValue.value = null; return }
    try {
      const { data } = await api.post<{ estimated_value: string }>('/collection-requests/calculate/', { material_lines: lines.map((l) => ({ material_type: l.material_type, amount_kg: l.amount_kg })) })
      completeActualValue.value = data.estimated_value
    } catch {
      completeActualValue.value = null
    }
    return
  }
  const amount = parseFloat(completeActualAmount.value)
  if (isNaN(amount) || amount <= 0) { completeActualValue.value = null; return }
  try {
    const { data } = await api.post<{ estimated_value: string }>('/collection-requests/calculate/', {
      material_type: selectedRequest.value.material_type || 'paper',
      amount_kg: completeActualAmount.value,
    })
    completeActualValue.value = data.estimated_value
  } catch {
    completeActualValue.value = null
  }
})

async function saveStatus() {
  if (!selectedRequest.value) return
  if (statusUpdate.value === 'completed') {
    Object.keys(completeErrors).forEach((k) => { completeErrors[k] = '' })
    if (hasMultipleMaterials.value) {
      const lines = completeActualMaterialLines.value
      let total = 0
      let hasError = false
      lines.forEach((line, idx) => {
        const kg = parseFloat(String(line.amount_kg))
        if (isNaN(kg) || kg < 0) {
          completeErrors[`line_${idx}`] = 'Укажите вес (0 или больше).'
          hasError = true
        } else total += kg
      })
      if (total < 1) {
        completeErrors.actual_amount = 'Суммарный вес не менее 1 кг.'
        hasError = true
      }
      if (hasError) return
      updatingStatus.value = true
      try {
        await api.post(`/collection-requests/${selectedRequest.value.id}/complete/`, {
          actual_material_lines: lines.map((l) => ({ material_type: l.material_type, amount_kg: l.amount_kg })),
          actual_collection_date: completeActualDate.value || null,
          internal_notes: completeInternalNotes.value || '',
        })
        await store.fetchRequests()
        await store.fetchDashboard()
        statusDialog.value = false
        selectedRequest.value = null
      } catch (err: unknown) {
        const ax = err as { response?: { data?: Record<string, string | string[]> } }
        const d = ax.response?.data
        if (d?.actual_material_lines) {
          completeErrors.actual_amount = Array.isArray(d.actual_material_lines) ? d.actual_material_lines.flat().join(' ') : String(d.actual_material_lines)
        }
      } finally {
        updatingStatus.value = false
      }
      return
    }
    const amount = parseFloat(completeActualAmount.value)
    if (isNaN(amount) || amount < 1) {
      completeErrors.actual_amount = 'Укажите вес (мин. 1 кг).'
      return
    }
    updatingStatus.value = true
    try {
      await api.post(`/collection-requests/${selectedRequest.value.id}/complete/`, {
        actual_amount: completeActualAmount.value,
        actual_collection_date: completeActualDate.value || null,
        internal_notes: completeInternalNotes.value || '',
      })
      await store.fetchRequests()
      await store.fetchDashboard()
      statusDialog.value = false
      selectedRequest.value = null
    } catch (err: unknown) {
      const ax = err as { response?: { data?: Record<string, string | string[]> } }
      const d = ax.response?.data
      if (d?.actual_amount) completeErrors.actual_amount = Array.isArray(d.actual_amount) ? d.actual_amount.join(' ') : String(d.actual_amount)
    } finally {
      updatingStatus.value = false
    }
    return
  }
  updatingStatus.value = true
  try {
    const payload: Record<string, unknown> = { status: statusUpdate.value }
    if (statusUpdateEstimatedDate.value) payload.estimated_collection_date = statusUpdateEstimatedDate.value
    else payload.estimated_collection_date = null
    if (statusUpdateActualDate.value) payload.actual_collection_date = statusUpdateActualDate.value
    else payload.actual_collection_date = null
    payload.notes = statusUpdateNotes.value || ''
    await api.patch(`/collection-requests/${selectedRequest.value.id}/`, payload)
    await store.fetchRequests()
    await store.fetchDashboard()
    statusDialog.value = false
    selectedRequest.value = null
  } finally {
    updatingStatus.value = false
  }
}

async function handleRequestSaved() {
  await store.fetchRequests()
  await store.fetchDashboard()
  if (selectedRequest.value?.id) {
    const updated = store.requests.find((r) => r.id === selectedRequest.value!.id)
    if (updated) selectedRequest.value = updated
  }
}

async function retryDashboard() {
  store.clearDashboardError()
  await store.fetchDashboard()
  if (activeTab.value === 'statistics') nextTick(() => buildCharts())
}

async function handleRefresh() {
  refreshing.value = true
  try {
    await store.loadAll()
    if (activeTab.value === 'statistics') nextTick(() => buildCharts())
  } finally {
    refreshing.value = false
  }
}

async function loadNotifications() {
  try {
    const { data } = await api.get<{ id: number; title: string; message: string; read: boolean }[]>('/notifications/')
    notifications.value = data
    unreadCount.value = data.filter((n) => !n.read).length
  } catch {
    // ignore
  }
}

async function markNotificationRead(id: number) {
  try {
    await api.post(`/notifications/${id}/mark_read/`)
    const n = notifications.value.find((x) => x.id === id)
    if (n) n.read = true
    unreadCount.value = Math.max(0, unreadCount.value - 1)
  } catch {
    // ignore
  }
}

async function markAllNotificationsRead() {
  try {
    await api.post('/notifications/mark_all_read/')
    notifications.value.forEach((n) => (n.read = true))
    unreadCount.value = 0
  } catch {
    // ignore
  }
}

function logout() {
  authStore.logout()
  userStore.clearUser()
  router.push({ name: 'Login' })
}

onMounted(async () => {
  try {
    await store.loadAll()
  } catch {
    // loadAll can fail partially; dashboard error is shown via store.dashboardError
  }
  loadNotifications()
  pollInterval = setInterval(() => {
    store.refreshKpis()
  }, 30000)
})

watch([() => activeTab.value, () => store.dashboard], () => {
  if (activeTab.value === 'statistics') {
    nextTick(() => buildCharts())
  }
}, { deep: true })

watch(activeTab, (tab) => {
  if (tab !== 'requests') institutionIdFilter.value = null
})

onUnmounted(() => {
  if (pollInterval) clearInterval(pollInterval)
  monthlyChart?.destroy()
  materialChart?.destroy()
  statusChart?.destroy()
})
</script>

<style lang="scss" scoped>
.company-dashboard__main {
  background: var(--vuvoz-surface, #f8fafc);
}
@media (max-width: 600px) {
  .company-dashboard__main .v-container {
    padding-left: 12px;
    padding-right: 12px;
  }
}
.company-dashboard__inst-search {
  max-width: 260px;
  min-width: 0;
}
@media (max-width: 600px) {
  .company-dashboard__inst-search {
    max-width: none;
    width: 100%;
  }
}
.company-dashboard__kpis :deep(.stats-widget) {
  height: 100%;
}
.chart-wrap {
  position: relative;
  height: 220px;
  max-width: 100%;
}
.request-cards-grid {
  --v-row-gutter: 12px;
}
.request-cards-grid .v-col {
  display: flex;
}
.request-cards-grid .v-col > * {
  width: 100%;
}
</style>
