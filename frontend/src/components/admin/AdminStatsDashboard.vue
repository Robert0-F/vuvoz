<template>
  <div class="admin-stats-dashboard">
    <!-- Filters -->
    <v-card class="dashboard-filters rounded-lg mb-4" elevation="1">
      <v-card-text class="pa-4">
        <div class="d-flex flex-wrap align-center ga-3">
          <v-select
            v-model="datePreset"
            :items="datePresetItems"
            label="Период"
            density="compact"
            variant="outlined"
            hide-details
            style="max-width: 180px"
            @update:model-value="applyDatePreset"
          />
          <v-text-field
            v-model="filters.date_from"
            label="С"
            type="date"
            density="compact"
            variant="outlined"
            hide-details
            style="max-width: 150px"
          />
          <v-text-field
            v-model="filters.date_to"
            label="По"
            type="date"
            density="compact"
            variant="outlined"
            hide-details
            style="max-width: 150px"
          />
          <v-select
            v-model="filters.basis"
            :items="basisItems"
            label="Основа"
            density="compact"
            variant="outlined"
            hide-details
            style="max-width: 200px"
          />
          <v-select
            v-model="filters.company_id"
            :items="companyFilterItems"
            label="Компания"
            density="compact"
            variant="outlined"
            hide-details
            clearable
            style="max-width: 220px"
          />
          <v-text-field
            v-model="filters.institution_type"
            label="Тип организации"
            density="compact"
            variant="outlined"
            hide-details
            clearable
            style="max-width: 180px"
          />
          <v-select
            v-model="filters.material_type"
            :items="materialFilterItems"
            label="Материал"
            density="compact"
            variant="outlined"
            hide-details
            clearable
            style="max-width: 200px"
          />
          <v-btn color="primary" :loading="loading" @click="loadAnalytics">
            Применить
          </v-btn>
        </div>
      </v-card-text>
    </v-card>

    <v-progress-linear v-if="loading" indeterminate color="primary" class="mb-4" />

    <template v-else-if="data">
      <!-- KPI Cards -->
      <section class="kpi-section mb-6">
        <h2 class="text-h6 mb-3">Ключевые показатели</h2>
        <v-row dense>
          <v-col v-for="kpi in kpiCards" :key="kpi.key" xs="6" sm="4" md="3" lg="2">
            <v-card class="kpi-card rounded-lg" elevation="1">
              <v-card-text class="pa-3">
                <div class="text-caption text-medium-emphasis">{{ kpi.label }}</div>
                <div class="text-h6 font-weight-bold mt-1">{{ kpi.value }}</div>
                <div v-if="kpi.trend != null" class="text-caption mt-1" :class="kpi.trend >= 0 ? 'text-success' : 'text-error'">
                  {{ kpi.trend >= 0 ? '↑' : '↓' }} {{ Math.abs(kpi.trend) }}% к пред. периоду
                </div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </section>

      <!-- Charts & Tables in tabs -->
      <v-tabs v-model="sectionTab" class="dashboard-tabs mb-4" color="primary">
        <v-tab value="materials">Материалы</v-tab>
        <v-tab value="companies">Компании</v-tab>
        <v-tab value="institutions">Организации</v-tab>
        <v-tab value="trends">Динамика</v-tab>
        <v-tab value="status">Статусы и эффективность</v-tab>
        <v-tab value="bonus">Бонусы</v-tab>
      </v-tabs>

      <v-window v-model="sectionTab">
        <!-- Materials -->
        <v-window-item value="materials">
          <v-row>
            <v-col cols="12" md="6">
              <v-card class="rounded-lg" elevation="1">
                <v-card-title>Доля по типам материалов (кг)</v-card-title>
                <v-card-text>
                  <div class="chart-wrap" style="height: 300px">
                    <canvas ref="chartMaterialsPie"></canvas>
                  </div>
                </v-card-text>
              </v-card>
            </v-col>
            <v-col cols="12" md="6">
              <v-card class="rounded-lg" elevation="1">
                <v-card-title>Топ материалов по весу</v-card-title>
                <v-card-text>
                  <v-table density="compact">
                    <thead>
                      <tr>
                        <th>Материал</th>
                        <th class="text-right">кг</th>
                        <th class="text-right">Заявок</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="m in data.materials" :key="m.material_type">
                        <td>{{ m.material_type_display }}</td>
                        <td class="text-right">{{ formatKg(m.total_kg) }}</td>
                        <td class="text-right">{{ m.request_count }}</td>
                      </tr>
                      <tr v-if="!data.materials.length"><td colspan="3" class="text-center text-medium-emphasis">Нет данных</td></tr>
                    </tbody>
                  </v-table>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </v-window-item>

        <!-- Companies -->
        <v-window-item value="companies">
          <v-row>
            <v-col cols="12" md="6">
              <v-card class="rounded-lg" elevation="1">
                <v-card-title>Топ компаний по объёму (кг)</v-card-title>
                <v-card-text>
                  <div class="chart-wrap" style="height: 320px">
                    <canvas ref="chartCompaniesBar"></canvas>
                  </div>
                </v-card-text>
              </v-card>
            </v-col>
            <v-col cols="12" md="6">
              <v-card class="rounded-lg" elevation="1">
                <v-card-title>Организаций у компаний</v-card-title>
                <v-card-text>
                  <v-table density="compact">
                    <thead>
                      <tr>
                        <th>Компания</th>
                        <th class="text-right">Организаций</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="c in data.institutions_per_company" :key="c.company_id">
                        <td>{{ c.company_name }}</td>
                        <td class="text-right">{{ c.institution_count }}</td>
                      </tr>
                      <tr v-if="!data.institutions_per_company.length"><td colspan="2" class="text-center text-medium-emphasis">Нет данных</td></tr>
                    </tbody>
                  </v-table>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </v-window-item>

        <!-- Institutions -->
        <v-window-item value="institutions">
          <v-row>
            <v-col cols="12" md="6">
              <v-card class="rounded-lg" elevation="1">
                <v-card-title>Топ организаций по объёму (кг)</v-card-title>
                <v-card-text>
                  <div class="chart-wrap" style="height: 360px">
                    <canvas ref="chartInstitutionsBar"></canvas>
                  </div>
                </v-card-text>
              </v-card>
            </v-col>
            <v-col cols="12" md="6">
              <v-card class="rounded-lg" elevation="1">
                <v-card-title>По типам организаций</v-card-title>
                <v-card-text>
                  <div class="chart-wrap" style="height: 280px">
                    <canvas ref="chartInstitutionTypePie"></canvas>
                  </div>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </v-window-item>

        <!-- Trends -->
        <v-window-item value="trends">
          <v-row>
            <v-col cols="12">
              <v-card class="rounded-lg" elevation="1">
                <v-card-title>Объём по периодам (кг)</v-card-title>
                <v-card-text>
                  <div class="chart-wrap" style="height: 300px">
                    <canvas ref="chartWeightOverTime"></canvas>
                  </div>
                </v-card-text>
              </v-card>
            </v-col>
            <v-col cols="12">
              <v-card class="rounded-lg" elevation="1">
                <v-card-title>Количество заявок по периодам</v-card-title>
                <v-card-text>
                  <div class="chart-wrap" style="height: 280px">
                    <canvas ref="chartRequestsOverTime"></canvas>
                  </div>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </v-window-item>

        <!-- Status & Efficiency -->
        <v-window-item value="status">
          <v-row>
            <v-col cols="12" md="6">
              <v-card class="rounded-lg" elevation="1">
                <v-card-title>Заявки по статусам</v-card-title>
                <v-card-text>
                  <div class="chart-wrap" style="height: 260px">
                    <canvas ref="chartStatusBar"></canvas>
                  </div>
                </v-card-text>
              </v-card>
            </v-col>
            <v-col cols="12" md="6">
              <v-card class="rounded-lg" elevation="1">
                <v-card-title>Эффективность</v-card-title>
                <v-card-text>
                  <p v-if="data.avg_completion_hours != null" class="text-body-2">
                    Среднее время от создания до завершения заявки: <strong>{{ data.avg_completion_hours }} ч</strong>
                  </p>
                  <p v-else class="text-body-2 text-medium-emphasis">Нет данных за период</p>
                </v-card-text>
              </v-card>
            </v-col>
            <v-col cols="12">
              <v-card class="rounded-lg" elevation="1">
                <v-card-title>% завершённых заявок по компаниям</v-card-title>
                <v-card-text>
                  <v-table density="compact">
                    <thead>
                      <tr>
                        <th>Компания</th>
                        <th class="text-right">Всего</th>
                        <th class="text-right">Завершено</th>
                        <th class="text-right">%</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="r in data.completion_rate_by_company" :key="r.company_id">
                        <td>{{ r.company_name }}</td>
                        <td class="text-right">{{ r.total }}</td>
                        <td class="text-right">{{ r.completed }}</td>
                        <td class="text-right">{{ r.completion_rate_percent }}%</td>
                      </tr>
                      <tr v-if="!data.completion_rate_by_company.length"><td colspan="4" class="text-center text-medium-emphasis">Нет данных</td></tr>
                    </tbody>
                  </v-table>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </v-window-item>

        <!-- Bonus -->
        <v-window-item value="bonus">
          <v-row>
            <v-col cols="12" md="6">
              <v-card class="rounded-lg" elevation="1">
                <v-card-title>Начисление баллов по месяцам</v-card-title>
                <v-card-text>
                  <div class="chart-wrap" style="height: 260px">
                    <canvas ref="chartBonusOverTime"></canvas>
                  </div>
                </v-card-text>
              </v-card>
            </v-col>
            <v-col cols="12" md="6">
              <v-card class="rounded-lg" elevation="1">
                <v-card-title>Топ организаций по баллам</v-card-title>
                <v-card-text>
                  <v-table density="compact">
                    <thead>
                      <tr>
                        <th>Организация</th>
                        <th class="text-right">Баллов</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="t in data.top_point_institutions" :key="t.institution_id">
                        <td>{{ t.institution_name }}</td>
                        <td class="text-right">{{ t.total_points }}</td>
                      </tr>
                      <tr v-if="!data.top_point_institutions.length"><td colspan="2" class="text-center text-medium-emphasis">Нет данных</td></tr>
                    </tbody>
                  </v-table>
                </v-card-text>
              </v-card>
            </v-col>
            <v-col cols="12">
              <v-card class="rounded-lg" elevation="1">
                <v-card-title>Популярные товары (каталог баллов)</v-card-title>
                <v-card-text>
                  <v-table density="compact">
                    <thead>
                      <tr>
                        <th>Товар</th>
                        <th class="text-right">Заказов</th>
                        <th class="text-right">Штук</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="p in data.popular_products" :key="p.product_id">
                        <td>{{ p.product_name }}</td>
                        <td class="text-right">{{ p.order_count }}</td>
                        <td class="text-right">{{ p.total_quantity }}</td>
                      </tr>
                      <tr v-if="!data.popular_products.length"><td colspan="3" class="text-center text-medium-emphasis">Нет данных</td></tr>
                    </tbody>
                  </v-table>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </v-window-item>
      </v-window>
    </template>

    <v-alert v-else-if="error" type="error" class="mt-4">{{ error }}</v-alert>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted, nextTick } from 'vue'
import { api } from '@/api/axios'
import {
  Chart,
  ArcElement,
  BarController,
  BarElement,
  CategoryScale,
  Legend,
  LinearScale,
  LineController,
  LineElement,
  PointElement,
  Tooltip,
} from 'chart.js'

Chart.register(
  ArcElement,
  BarController,
  BarElement,
  CategoryScale,
  Legend,
  LinearScale,
  LineController,
  LineElement,
  PointElement,
  Tooltip,
)

interface AnalyticsData {
  period: { date_from: string; date_to: string; basis: string }
  kpis: Record<string, number>
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
}

const loading = ref(false)
const error = ref('')
const data = ref<AnalyticsData | null>(null)
const sectionTab = ref('materials')
const datePreset = ref('year')

const filters = reactive({
  date_from: '',
  date_to: '',
  basis: 'created',
  company_id: '',
  institution_type: '',
  material_type: '',
})

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
const companyFilterItems = ref<{ title: string; value: string }[]>([])
const materialFilterItems = ref<{ title: string; value: string }[]>([])

function setDefaultDates() {
  const end = new Date()
  const start = new Date()
  start.setFullYear(start.getFullYear() - 1)
  filters.date_from = start.toISOString().slice(0, 10)
  filters.date_to = end.toISOString().slice(0, 10)
}

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

const kpiCards = computed(() => {
  if (!data.value?.kpis) return []
  const k = data.value.kpis
  return [
    { key: 'companies', label: 'Компаний', value: k.total_companies ?? 0, trend: null },
    { key: 'institutions', label: 'Организаций', value: k.total_institutions ?? 0, trend: null },
    { key: 'requests_all', label: 'Заявок (всего)', value: k.total_requests_all_time ?? 0, trend: null },
    { key: 'requests_month', label: 'Заявок (мес)', value: k.total_requests_this_month ?? 0, trend: null },
    { key: 'weight_all', label: 'Собрано кг (всего)', value: formatKg(k.total_weight_kg_all_time ?? 0), trend: null },
    { key: 'weight_period', label: 'Собрано кг (период)', value: formatKg(k.total_weight_kg_period ?? 0), trend: k.weight_trend_percent },
    { key: 'avg_weight', label: 'Средний вес заявки (кг)', value: k.avg_weight_per_request ?? 0, trend: null },
    { key: 'estimated', label: 'Ориент. стоимость (руб)', value: formatNum(k.total_estimated_value ?? 0), trend: null },
    { key: 'actual', label: 'Факт. стоимость (руб)', value: formatNum(k.total_actual_value ?? 0), trend: null },
  ]
})

let chartInstances: Chart[] = []

function formatKg(n: number) {
  if (n >= 1000) return (n / 1000).toFixed(1) + ' т'
  return String(Math.round(n))
}
function formatNum(n: number) {
  return new Intl.NumberFormat('ru-RU').format(Math.round(n))
}

async function loadCompaniesForFilter() {
  try {
    const { data: list } = await api.get<{ id: number; company_name: string }[]>('/company-profiles/')
    companyFilterItems.value = list.map((c) => ({ title: c.company_name, value: String(c.id) }))
  } catch {
    companyFilterItems.value = []
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
    if (filters.institution_type) params.institution_type = filters.institution_type
    if (filters.material_type) params.material_type = filters.material_type
    const { data: res } = await api.get<AnalyticsData>('/analytics/dashboard/', { params })
    data.value = res
    materialFilterItems.value = [
      { title: 'Все', value: '' },
      ...res.materials.map((m) => ({ title: m.material_type_display, value: m.material_type })),
    ]
    await nextTick()
    drawCharts()
  } catch (e: unknown) {
    const ax = e as { response?: { data?: { detail?: string } } }
    error.value = ax.response?.data?.detail ?? 'Ошибка загрузки аналитики'
  } finally {
    loading.value = false
  }
}

function drawCharts() {
  disposeCharts()
  if (!data.value) return
  const d = data.value

  if (d.materials.length && chartMaterialsPie.value) {
    chartInstances.push(
      new Chart(chartMaterialsPie.value, {
        type: 'doughnut',
        data: {
          labels: d.materials.map((m) => m.material_type_display),
          datasets: [{ data: d.materials.map((m) => m.total_kg), backgroundColor: ['#0d9488', '#059669', '#0ea5e9', '#8b5cf6', '#f59e0b', '#ef4444'].slice(0, d.materials.length) }],
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'right' } } },
      })
    )
  }

  if (d.top_companies.length && chartCompaniesBar.value) {
    chartInstances.push(
      new Chart(chartCompaniesBar.value, {
        type: 'bar',
        data: {
          labels: d.top_companies.map((c) => c.company_name.slice(0, 15)),
          datasets: [{ label: 'кг', data: d.top_companies.map((c) => c.total_kg), backgroundColor: '#0d9488' }],
        },
        options: { indexAxis: 'y', responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } },
      })
    )
  }

  if (d.top_organizations.length && chartInstitutionsBar.value) {
    chartInstances.push(
      new Chart(chartInstitutionsBar.value, {
        type: 'bar',
        data: {
          labels: d.top_organizations.slice(0, 15).map((o) => o.institution_name.slice(0, 12)),
          datasets: [{ label: 'кг', data: d.top_organizations.slice(0, 15).map((o) => o.total_kg), backgroundColor: '#059669' }],
        },
        options: { indexAxis: 'y', responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } },
      })
    )
  }

  if (d.institution_type_breakdown.length && chartInstitutionTypePie.value) {
    chartInstances.push(
      new Chart(chartInstitutionTypePie.value, {
        type: 'pie',
        data: {
          labels: d.institution_type_breakdown.map((i) => i.institution_type || '—'),
          datasets: [{ data: d.institution_type_breakdown.map((i) => i.total_kg), backgroundColor: ['#0ea5e9', '#8b5cf6', '#f59e0b', '#10b981', '#6366f1'] }],
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'right' } } },
      })
    )
  }

  if (d.weight_over_time.length && chartWeightOverTime.value) {
    chartInstances.push(
      new Chart(chartWeightOverTime.value, {
        type: 'line',
        data: {
          labels: d.weight_over_time.map((w) => w.period_label),
          datasets: [{ label: 'кг', data: d.weight_over_time.map((w) => w.total_kg), borderColor: '#0d9488', fill: true, tension: 0.3 }],
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } },
      })
    )
  }

  if (d.requests_over_time.length && chartRequestsOverTime.value) {
    chartInstances.push(
      new Chart(chartRequestsOverTime.value, {
        type: 'line',
        data: {
          labels: d.requests_over_time.map((r) => r.period_label),
          datasets: [{ label: 'Заявок', data: d.requests_over_time.map((r) => r.count), borderColor: '#059669', fill: true, tension: 0.3 }],
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } },
      })
    )
  }

  if (d.requests_by_status.length && chartStatusBar.value) {
    chartInstances.push(
      new Chart(chartStatusBar.value, {
        type: 'bar',
        data: {
          labels: d.requests_by_status.map((s) => s.status_display),
          datasets: [{ label: 'Заявок', data: d.requests_by_status.map((s) => s.count), backgroundColor: ['#f59e0b', '#0ea5e9', '#059669', '#6b7280'] }],
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } },
      })
    )
  }

  if (d.bonus_over_time.length && chartBonusOverTime.value) {
    chartInstances.push(
      new Chart(chartBonusOverTime.value, {
        type: 'line',
        data: {
          labels: d.bonus_over_time.map((b) => b.period_label),
          datasets: [{ label: 'Баллов', data: d.bonus_over_time.map((b) => b.total_points), borderColor: '#8b5cf6', fill: true, tension: 0.3 }],
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } },
      })
    )
  }
}

const chartMaterialsPie = ref<HTMLCanvasElement | null>(null)
const chartCompaniesBar = ref<HTMLCanvasElement | null>(null)
const chartInstitutionsBar = ref<HTMLCanvasElement | null>(null)
const chartInstitutionTypePie = ref<HTMLCanvasElement | null>(null)
const chartWeightOverTime = ref<HTMLCanvasElement | null>(null)
const chartRequestsOverTime = ref<HTMLCanvasElement | null>(null)
const chartStatusBar = ref<HTMLCanvasElement | null>(null)
const chartBonusOverTime = ref<HTMLCanvasElement | null>(null)

function disposeCharts() {
  chartInstances.forEach((c) => c.destroy())
  chartInstances = []
}

watch(sectionTab, () => nextTick(() => drawCharts()))

onMounted(() => {
  setDefaultDates()
  applyDatePreset('year')
  loadCompaniesForFilter()
  loadAnalytics()
})

defineExpose({ loadAnalytics })
</script>

<style scoped>
.admin-stats-dashboard { padding: 0 4px; }
.kpi-card { transition: transform 0.2s, box-shadow 0.2s; }
.kpi-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
.chart-wrap { position: relative; width: 100%; }
.dashboard-tabs :deep(.v-tab) { text-transform: none; font-weight: 500; }
@media (max-width: 600px) {
  .admin-stats-dashboard { padding: 0; }
  .kpi-section .v-col { flex: 0 0 50%; max-width: 50%; }
}
</style>
