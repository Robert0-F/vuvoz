<template>
  <div class="inst-stats">
    <v-card class="inst-stats__filters-card mb-4" elevation="1" rounded="lg">
      <v-card-text class="pa-4">
        <div class="d-flex flex-wrap align-center ga-3">
          <v-btn-toggle
            :model-value="activePreset === 'custom' ? null : activePreset"
            divided
            density="compact"
            variant="outlined"
            color="primary"
            class="inst-stats__toggle"
            @update:model-value="onPresetToggle"
          >
            <v-btn v-for="p in presets" :key="p.key" :value="p.key" size="small">
              {{ p.label }}
            </v-btn>
          </v-btn-toggle>

          <v-divider vertical class="inst-stats__divider d-none d-sm-flex" />

          <v-text-field
            v-model="statsMonth"
            label="Месяц"
            type="month"
            density="compact"
            variant="outlined"
            hide-details
            class="inst-stats__field-month"
            @update:model-value="onMonthChange"
          />

          <span class="text-caption text-medium-emphasis d-none d-md-inline">или период</span>

          <v-text-field
            v-model="dateFrom"
            label="С"
            type="date"
            density="compact"
            variant="outlined"
            hide-details
            class="inst-stats__field-date"
            @update:model-value="onCustomRange"
          />
          <v-text-field
            v-model="dateTo"
            label="По"
            type="date"
            density="compact"
            variant="outlined"
            hide-details
            class="inst-stats__field-date"
            @update:model-value="onCustomRange"
          />

          <v-btn color="primary" :loading="loading" @click="loadStats">Применить</v-btn>
        </div>

        <div v-if="periodLabel" class="mt-3">
          <v-chip size="small" variant="tonal" color="primary" prepend-icon="mdi-calendar-range">
            {{ periodLabel }}
          </v-chip>
        </div>
      </v-card-text>
    </v-card>

    <v-alert v-if="error" type="error" variant="tonal" density="compact" class="mb-4">{{ error }}</v-alert>

    <div v-if="loading && !stats" class="inst-stats__loading">
      <v-progress-circular indeterminate color="primary" size="44" />
    </div>

    <template v-else-if="stats">
      <div class="inst-stats__kpis">
        <InstitutionStatCard
          title="Заявок"
          :value="stats.total_requests"
          :subtitle="trendLabel(stats.total_requests, stats.previous_period?.total_requests)"
          icon="mdi-clipboard-list-outline"
          color="primary"
        />
        <InstitutionStatCard
          title="Завершено"
          :value="stats.completed_count"
          :subtitle="`${stats.completion_rate_percent ?? 0}% от заявок`"
          icon="mdi-check-circle-outline"
          color="success"
        />
        <InstitutionStatCard
          title="Собрано, кг"
          :value="formatNum(stats.total_weight_period)"
          :subtitle="trendLabelKg(stats.total_weight_period, stats.previous_period?.total_weight_kg)"
          icon="mdi-weight-kilogram"
          color="teal"
        />
        <InstitutionStatCard
          title="Начисления, ₽"
          :value="formatNum(stats.total_earnings_period)"
          :subtitle="trendLabelRub(stats.total_earnings_period, stats.previous_period?.total_earnings_rub)"
          icon="mdi-cash-multiple"
          color="warning"
        />
        <InstitutionStatCard
          title="Баллы за период"
          :value="formatNum(stats.bonus_points_period ?? 0)"
          :subtitle="`Баланс: ${formatNum(stats.bonus_balance ?? 0)}`"
          icon="mdi-leaf"
          color="success"
        />
        <InstitutionStatCard
          title="Ср. вес заявки"
          :value="`${stats.avg_weight_per_request ?? 0} кг`"
          :subtitle="`Всего за всё время: ${formatNum(stats.total_weight_all_time)} кг`"
          icon="mdi-scale-balance"
          color="info"
        />
      </div>

      <div class="inst-stats__grid">
        <section class="inst-stats__card inst-stats__card--wide">
          <h3 class="inst-stats__card-title">Динамика за 6 месяцев</h3>
          <p class="inst-stats__card-sub">Объём вывоза (кг) и количество заявок</p>
          <div class="inst-stats__chart inst-stats__chart--tall">
            <canvas ref="chartDynamics"></canvas>
          </div>
        </section>

        <section class="inst-stats__card">
          <h3 class="inst-stats__card-title">Заявки по статусу</h3>
          <p class="inst-stats__card-sub">За выбранный период</p>
          <div class="inst-stats__chart">
            <canvas ref="chartStatus"></canvas>
          </div>
        </section>

        <section class="inst-stats__card">
          <h3 class="inst-stats__card-title">Баллы</h3>
          <p class="inst-stats__card-sub">Начислено и потрачено за период</p>
          <div class="inst-stats__chart">
            <canvas ref="chartPoints"></canvas>
          </div>
          <p class="inst-stats__points-note">
            Потрачено: <strong>{{ formatNum(stats.points_spent_period ?? 0) }}</strong> баллов
          </p>
        </section>

        <section class="inst-stats__card inst-stats__card--wide">
          <h3 class="inst-stats__card-title">Материалы за период</h3>
          <p class="inst-stats__card-sub">По завершённым заявкам, кг</p>
          <div v-if="!stats.material_breakdown.length" class="inst-stats__empty">Нет данных о материалах</div>
          <div v-else class="inst-stats__chart">
            <canvas ref="chartMaterials"></canvas>
          </div>
        </section>

        <section class="inst-stats__card inst-stats__card--wide">
          <h3 class="inst-stats__card-title">Доход по месяцам</h3>
          <p class="inst-stats__card-sub">Сумма по завершённым заявкам, ₽</p>
          <div class="inst-stats__chart">
            <canvas ref="chartEarnings"></canvas>
          </div>
        </section>
      </div>
    </template>

    <div v-else class="inst-stats__empty inst-stats__empty--page">
      Не удалось загрузить статистику. Нажмите «Обновить».
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import { Chart } from 'chart.js'
import { api } from '@/api/axios'
import InstitutionStatCard from '@/components/institution/InstitutionStatCard.vue'
import {
  CHART_COLORS,
  STATUS_COLORS,
  createChart,
  disposeCharts,
  scheduleChartDraw,
} from '@/components/admin/stats/chartTheme'
import '@/components/admin/stats/chartTheme'

export interface InstitutionStatsData {
  total_requests: number
  completed_count: number
  cancelled_count?: number
  completion_rate_percent?: number
  requests_by_status: Record<string, number>
  total_weight_all_time: number
  total_weight_period: number
  total_earnings_period: number
  avg_weight_per_request?: number
  bonus_balance?: number | string
  bonus_points_period?: number | string
  points_spent_period?: number | string
  period_start: string | null
  period_end: string | null
  material_breakdown: { material_code: string; material_name: string; weight_kg: number }[]
  monthly_series?: {
    period_label: string
    requests_count: number
    weight_kg: number
    earnings_rub: number
  }[]
  previous_period?: {
    total_requests?: number
    total_weight_kg?: number
    total_earnings_rub?: number
  }
}

const presets = [
  { key: 'month', label: 'Этот месяц' },
  { key: 'quarter', label: 'Квартал' },
  { key: 'year', label: 'Год' },
] as const

type PresetKey = (typeof presets)[number]['key']

const stats = ref<InstitutionStatsData | null>(null)
const loading = ref(false)
const error = ref('')
const activePreset = ref<PresetKey | 'custom'>('month')

const chartDynamics = ref<HTMLCanvasElement | null>(null)
const chartStatus = ref<HTMLCanvasElement | null>(null)
const chartPoints = ref<HTMLCanvasElement | null>(null)
const chartMaterials = ref<HTMLCanvasElement | null>(null)
const chartEarnings = ref<HTMLCanvasElement | null>(null)
let charts: Chart[] = []

function defaultMonth() {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
}

const statsMonth = ref(defaultMonth())
const dateFrom = ref('')
const dateTo = ref('')

const periodLabel = computed(() => {
  if (!stats.value?.period_start || !stats.value?.period_end) return ''
  return `${formatRuDate(stats.value.period_start)} — ${formatRuDate(stats.value.period_end)}`
})

function formatRuDate(iso: string) {
  const [y, m, d] = iso.split('-')
  return `${d}.${m}.${y}`
}

function formatNum(v: number | string) {
  const n = typeof v === 'string' ? parseFloat(v) : v
  return (n || 0).toLocaleString('ru-RU', { maximumFractionDigits: 1 })
}

function trendLabel(current: number, prev?: number) {
  if (prev === undefined || prev === null) return undefined
  const diff = current - prev
  if (diff === 0) return 'как в прошлом периоде'
  const sign = diff > 0 ? '+' : ''
  return `${sign}${diff} к прошлому периоду`
}

function trendLabelKg(current: number | string, prev?: number) {
  const c = parseFloat(String(current)) || 0
  return trendLabel(Math.round(c), prev !== undefined ? Math.round(prev) : undefined)
}

function trendLabelRub(current: number | string, prev?: number) {
  const c = parseFloat(String(current)) || 0
  if (prev === undefined) return undefined
  const diff = c - prev
  if (Math.abs(diff) < 0.01) return 'как в прошлом периоде'
  const sign = diff > 0 ? '+' : ''
  return `${sign}${diff.toLocaleString('ru-RU', { maximumFractionDigits: 0 })} ₽ к прошлому периоду`
}

function onPresetToggle(key: PresetKey | null) {
  if (key) applyPreset(key)
}

function applyPreset(key: PresetKey) {
  activePreset.value = key
  const now = new Date()
  dateFrom.value = ''
  dateTo.value = ''
  if (key === 'month') {
    statsMonth.value = defaultMonth()
  } else if (key === 'quarter') {
    const qStart = new Date(now.getFullYear(), Math.floor(now.getMonth() / 3) * 3, 1)
    dateFrom.value = toIso(qStart)
    dateTo.value = toIso(now)
  } else {
    dateFrom.value = `${now.getFullYear()}-01-01`
    dateTo.value = toIso(now)
  }
  loadStats()
}

function toIso(d: Date) {
  return d.toISOString().slice(0, 10)
}

function onMonthChange() {
  activePreset.value = 'custom'
  dateFrom.value = ''
  dateTo.value = ''
  loadStats()
}

function onCustomRange() {
  if (dateFrom.value && dateTo.value) {
    activePreset.value = 'custom'
    loadStats()
  }
}

async function loadStats() {
  loading.value = true
  error.value = ''
  try {
    const params: Record<string, string> = {}
    if (dateFrom.value && dateTo.value) {
      params.start_date = dateFrom.value
      params.end_date = dateTo.value
    } else {
      params.month = statsMonth.value
    }
    const { data } = await api.get<InstitutionStatsData>('/stats/institution/', { params })
    stats.value = data
    scheduleDraw()
  } catch {
    stats.value = null
    error.value = 'Ошибка загрузки статистики'
  } finally {
    loading.value = false
  }
}

function pushChart(canvas: HTMLCanvasElement | null, config: ConstructorParameters<typeof Chart>[1]) {
  if (!canvas) return
  try {
    charts.push(createChart(canvas, config))
  } catch (e) {
    console.error('Institution stats chart error:', e)
  }
}

function drawCharts() {
  charts = disposeCharts(charts)
  const s = stats.value
  if (!s) return

  const series = s.monthly_series ?? []

  pushChart(chartDynamics.value, {
    type: 'bar',
    data: {
      labels: series.map((x) => x.period_label),
      datasets: [
        {
          type: 'bar',
          label: 'кг',
          data: series.map((x) => x.weight_kg),
          backgroundColor: 'rgba(13, 148, 136, 0.55)',
          yAxisID: 'y',
        },
        {
          type: 'line',
          label: 'Заявок',
          data: series.map((x) => x.requests_count),
          borderColor: '#0ea5e9',
          backgroundColor: 'rgba(14, 165, 233, 0.08)',
          tension: 0.3,
          yAxisID: 'y1',
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: { legend: { position: 'top' } },
      scales: {
        y: { position: 'left', beginAtZero: true, title: { display: true, text: 'кг' } },
        y1: { position: 'right', beginAtZero: true, grid: { drawOnChartArea: false }, title: { display: true, text: 'Заявок' } },
      },
    },
  })

  const st = s.requests_by_status ?? {}
  const statusItems = [
    { key: 'new', label: 'Новые', color: STATUS_COLORS.new },
    { key: 'accepted', label: 'Принятые', color: STATUS_COLORS.accepted },
    { key: 'completed', label: 'Завершённые', color: STATUS_COLORS.completed },
    { key: 'cancelled', label: 'Отменённые', color: STATUS_COLORS.cancelled },
  ].filter((x) => (st[x.key] ?? 0) > 0)

  if (statusItems.length) {
    pushChart(chartStatus.value, {
      type: 'doughnut',
      data: {
        labels: statusItems.map((x) => x.label),
        datasets: [{ data: statusItems.map((x) => st[x.key]), backgroundColor: statusItems.map((x) => x.color) }],
      },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } } },
    })
  }

  const earned = parseFloat(String(s.bonus_points_period ?? 0)) || 0
  const spent = parseFloat(String(s.points_spent_period ?? 0)) || 0
  pushChart(chartPoints.value, {
    type: 'bar',
    data: {
      labels: ['Начислено', 'Потрачено'],
      datasets: [{
        data: [earned, spent],
        backgroundColor: ['#059669', '#f59e0b'],
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: { y: { beginAtZero: true } },
    },
  })

  const materials = s.material_breakdown ?? []
  if (materials.length && chartMaterials.value) {
    pushChart(chartMaterials.value, {
      type: 'bar',
      data: {
        labels: materials.map((m) => m.material_name),
        datasets: [{
          label: 'кг',
          data: materials.map((m) => m.weight_kg),
          backgroundColor: CHART_COLORS.slice(0, materials.length),
        }],
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { x: { beginAtZero: true } },
      },
    })
  }

  pushChart(chartEarnings.value, {
    type: 'line',
    data: {
      labels: series.map((x) => x.period_label),
      datasets: [{
        label: '₽',
        data: series.map((x) => x.earnings_rub),
        borderColor: '#059669',
        backgroundColor: 'rgba(5, 150, 105, 0.12)',
        fill: true,
        tension: 0.3,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: { y: { beginAtZero: true } },
    },
  })

  charts.forEach((c) => c.resize())
}

function scheduleDraw() {
  nextTick(() => scheduleChartDraw(drawCharts))
}

watch(stats, () => scheduleDraw(), { deep: true })

onMounted(() => loadStats())
onBeforeUnmount(() => { charts = disposeCharts(charts) })

defineExpose({ loadStats })
</script>

<style scoped lang="scss">
.inst-stats__filters-card {
  border: 1px solid var(--vuvoz-border);
}

.inst-stats__field-month {
  max-width: 168px;
  min-width: 140px;
}

.inst-stats__field-date {
  max-width: 152px;
  min-width: 130px;
}

.inst-stats__divider {
  align-self: stretch;
  min-height: 36px;
}

.inst-stats__toggle {
  flex-shrink: 0;
}

.inst-stats__kpis {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.inst-stats__grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.25rem;
}

.inst-stats__card {
  background: var(--vuvoz-surface-elevated);
  border: 1px solid var(--vuvoz-border);
  border-radius: var(--vuvoz-radius-lg);
  padding: 1.25rem;
  box-shadow: var(--vuvoz-shadow-sm);
  &--wide { grid-column: 1 / -1; }
}

.inst-stats__card-title {
  margin: 0;
  font-size: 1rem;
  font-weight: 700;
  color: var(--vuvoz-text);
}

.inst-stats__card-sub {
  margin: 0.25rem 0 1rem;
  font-size: 0.85rem;
  color: var(--vuvoz-text-muted);
}

.inst-stats__chart {
  position: relative;
  height: 220px;
  width: 100%;
  &--tall { height: 280px; }
}

.inst-stats__points-note {
  margin: 0.75rem 0 0;
  font-size: 0.9rem;
  color: var(--vuvoz-text-muted);
  text-align: center;
}

.inst-stats__loading {
  display: flex;
  justify-content: center;
  padding: 3rem;
}

.inst-stats__empty {
  text-align: center;
  padding: 2rem 1rem;
  color: var(--vuvoz-text-muted);
  &--page { padding: 3rem 1rem; }
}

@media (max-width: 900px) {
  .inst-stats__grid { grid-template-columns: 1fr; }
  .inst-stats__card--wide { grid-column: auto; }
}
</style>
