<template>
  <div class="inst-charts">
    <div class="inst-charts__toolbar">
      <select v-model="dateRange" class="inst-charts__select">
        <option value="6m">Последние 6 месяцев</option>
        <option value="year">Этот год</option>
        <option value="last_year">Прошлый год</option>
      </select>
    </div>

    <div class="inst-charts__grid">
      <div class="inst-charts__card">
        <h4 class="inst-charts__title">Объём вывоза по месяцам (кг)</h4>
        <div class="inst-charts__chart">
          <canvas ref="barChartRef" />
        </div>
      </div>
      <div class="inst-charts__card">
        <h4 class="inst-charts__title">Заявки по статусу</h4>
        <div class="inst-charts__chart inst-charts__chart--small">
          <canvas ref="pieChartRef" />
        </div>
      </div>
      <div class="inst-charts__card inst-charts__card--full">
        <h4 class="inst-charts__title">Совокупные доходы (руб.)</h4>
        <div class="inst-charts__chart">
          <canvas ref="lineChartRef" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import Chart from 'chart.js/auto'
import type { CollectionRequest } from '@/types'

const props = defineProps<{
  requests: CollectionRequest[]
}>()

const dateRange = ref('6m')
const barChartRef = ref<HTMLCanvasElement | null>(null)
const pieChartRef = ref<HTMLCanvasElement | null>(null)
const lineChartRef = ref<HTMLCanvasElement | null>(null)

let barChart: Chart | null = null
let pieChart: Chart | null = null
let lineChart: Chart | null = null

const dateRangeDates = computed(() => {
  const now = new Date()
  let start: Date
  if (dateRange.value === '6m') {
    start = new Date(now.getFullYear(), now.getMonth() - 6, 1)
  } else if (dateRange.value === 'year') {
    start = new Date(now.getFullYear(), 0, 1)
  } else {
    start = new Date(now.getFullYear() - 1, 0, 1)
    now.setFullYear(now.getFullYear() - 1)
  }
  return { start, end: dateRange.value === 'last_year' ? new Date(now.getFullYear(), 11, 31) : now }
})

const completedRequests = computed(() =>
  props.requests.filter((r) => r.status === 'completed')
)

const monthlyVolume = computed(() => {
  const { start, end } = dateRangeDates.value
  const months: Record<string, number> = {}
  const d = new Date(start.getFullYear(), start.getMonth(), 1)
  while (d <= end) {
    const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
    months[key] = 0
    d.setMonth(d.getMonth() + 1)
  }
  for (const r of completedRequests.value) {
    if (!r.completed_at) continue
    const dt = new Date(r.completed_at)
    const key = `${dt.getFullYear()}-${String(dt.getMonth() + 1).padStart(2, '0')}`
    if (key in months) {
      const kg = parseFloat(String(r.actual_amount || r.estimated_amount || r.paper_weight_kg || 0))
      months[key] += kg
    }
  }
  const labels = Object.keys(months).sort()
  const data = labels.map((k) => months[k])
  return { labels, data }
})

const statusData = computed(() => {
  const counts: Record<string, number> = { new: 0, accepted: 0, completed: 0 }
  for (const r of props.requests) {
    const s = r.status || 'new'
    counts[s] = (counts[s] || 0) + 1
  }
  return [
    { label: 'Новые', value: counts.new, color: '#f59e0b' },
    { label: 'Принятые', value: counts.accepted, color: '#0ea5e9' },
    { label: 'Завершённые', value: counts.completed, color: '#059669' },
  ].filter((x) => x.value > 0)
})

const cumulativeEarnings = computed(() => {
  const { start, end } = dateRangeDates.value
  const items = completedRequests.value
    .filter((r) => r.completed_at)
    .map((r) => ({
      date: new Date(r.completed_at!),
      value: parseFloat(String(r.actual_value || r.estimated_value || 0)),
    }))
  const labels: string[] = []
  const data: number[] = []
  const d = new Date(start.getFullYear(), start.getMonth(), 1)
  while (d <= end) {
    const monthEnd = new Date(d.getFullYear(), d.getMonth() + 1, 0, 23, 59, 59)
    let total = 0
    for (const r of items) {
      if (r.date <= monthEnd) total += r.value
    }
    labels.push(d.toLocaleDateString('ru-RU', { month: 'short', year: '2-digit' }))
    data.push(total)
    d.setMonth(d.getMonth() + 1)
  }
  return { labels, data }
})

function drawCharts() {
  const destroy = (c: Chart | null) => c?.destroy()

  if (barChartRef.value) {
    destroy(barChart)
    barChart = new Chart(barChartRef.value, {
      type: 'bar',
      data: {
        labels: monthlyVolume.value.labels.map((k) => {
          const [y, m] = k.split('-')
          return new Date(parseInt(y), parseInt(m) - 1).toLocaleDateString('ru-RU', { month: 'short', year: '2-digit' })
        }),
        datasets: [{
          label: 'Вывезено (кг)',
          data: monthlyVolume.value.data,
          backgroundColor: 'rgba(13, 148, 136, 0.6)',
          borderColor: '#0d9488',
          borderWidth: 1,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: { beginAtZero: true, ticks: { precision: 0 } },
        },
      },
    })
  }

  if (pieChartRef.value) {
    destroy(pieChart)
    pieChart = new Chart(pieChartRef.value, {
      type: 'doughnut',
      data: {
        labels: statusData.value.map((x) => x.label),
        datasets: [{
          data: statusData.value.map((x) => x.value),
          backgroundColor: statusData.value.map((x) => x.color),
          borderWidth: 0,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: 'bottom' } },
      },
    })
  }

  if (lineChartRef.value) {
    destroy(lineChart)
    lineChart = new Chart(lineChartRef.value, {
      type: 'line',
      data: {
        labels: cumulativeEarnings.value.labels,
        datasets: [{
          label: 'Доход (руб.)',
          data: cumulativeEarnings.value.data,
          borderColor: '#0d9488',
          backgroundColor: 'rgba(13, 148, 136, 0.1)',
          fill: true,
          tension: 0.3,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: { beginAtZero: true, ticks: { callback: (v) => v + ' ₽' } },
        },
      },
    })
  }
}

watch([dateRange, () => props.requests], () => drawCharts(), { deep: true })

onMounted(() => drawCharts())
onUnmounted(() => {
  barChart?.destroy()
  pieChart?.destroy()
  lineChart?.destroy()
})
</script>

<style scoped lang="scss">
.inst-charts {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.inst-charts__toolbar {
  display: flex;
  justify-content: flex-end;
}

.inst-charts__select {
  padding: 0.5rem 0.75rem;
  border-radius: var(--vuvoz-radius-sm);
  border: 2px solid var(--vuvoz-border);
  font-size: 0.9rem;
  background: #fff;
  &:focus { outline: none; border-color: var(--vuvoz-primary); }
}

.inst-charts__grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

@media (max-width: 900px) {
  .inst-charts__grid {
    grid-template-columns: 1fr;
  }
}

.inst-charts__card {
  background: var(--vuvoz-surface-elevated);
  border-radius: var(--vuvoz-radius-lg);
  border: 1px solid var(--vuvoz-border);
  padding: 1.5rem;
  box-shadow: var(--vuvoz-shadow-sm);

  &--full {
    grid-column: 1 / -1;
  }
}

.inst-charts__title {
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 1rem;
  color: var(--vuvoz-text);
}

.inst-charts__chart {
  height: 240px;
  position: relative;

  &--small {
    height: 200px;
    max-width: 280px;
    margin: 0 auto;
  }
}
</style>
