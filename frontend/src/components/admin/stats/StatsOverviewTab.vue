<template>
  <div v-if="data">
    <StatsKpiRow :items="kpiItems" />

    <v-row>
      <v-col cols="12" md="8">
        <v-card class="rounded-lg" elevation="1">
          <v-card-title>Динамика: объём и заявки</v-card-title>
          <v-card-subtitle class="pb-0">Килограммы и количество заявок за выбранный период</v-card-subtitle>
          <v-card-text>
            <div class="chart-wrap" style="height: 300px">
              <canvas ref="chartCombined"></canvas>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="4">
        <v-card class="rounded-lg mb-4" elevation="1">
          <v-card-title>Завершённость</v-card-title>
          <v-card-text>
            <div class="chart-wrap" style="height: 180px">
              <canvas ref="chartCompletion"></canvas>
            </div>
            <p class="text-center text-body-2 mt-2">
              {{ completion.completed }} из {{ completion.total }}
              <strong>({{ completion.percent }}%)</strong>
            </p>
          </v-card-text>
        </v-card>
        <v-card class="rounded-lg" elevation="1" variant="tonal" color="grey">
          <v-card-text class="text-caption text-medium-emphasis">
            В системе: {{ data.kpis.total_companies_global ?? data.kpis.total_companies }} компаний,
            {{ data.kpis.total_institutions_global ?? data.kpis.total_institutions }} организаций
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12">
        <v-card class="rounded-lg" elevation="1">
          <v-card-title>Топ-3 материала</v-card-title>
          <v-card-text>
            <v-row v-if="topMaterials.length">
              <v-col v-for="(m, i) in topMaterials" :key="m.material_type" cols="12" sm="4">
                <div class="material-rank pa-3 rounded-lg" :style="{ borderLeft: `4px solid ${CHART_COLORS[i]}` }">
                  <div class="text-caption text-medium-emphasis">#{{ i + 1 }}</div>
                  <div class="text-subtitle-1 font-weight-bold">{{ m.material_type_display }}</div>
                  <div class="text-body-2">{{ formatKg(m.total_kg) }} · {{ m.request_count }} заявок</div>
                </div>
              </v-col>
            </v-row>
            <p v-else class="text-medium-emphasis text-center py-4">Нет данных за период</p>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { Chart } from 'chart.js'
import './chartTheme'
import StatsKpiRow from './StatsKpiRow.vue'
import { CHART_COLORS, disposeCharts, scheduleChartDraw } from './chartTheme'
import type { AnalyticsData } from '@/composables/useAdminAnalytics'
import { formatKg } from '@/composables/useAdminAnalytics'

const props = defineProps<{
  data: AnalyticsData
  completion: { total: number; completed: number; percent: number }
}>()

const chartCombined = ref<HTMLCanvasElement | null>(null)
const chartCompletion = ref<HTMLCanvasElement | null>(null)
let charts: Chart[] = []

const topMaterials = computed(() => props.data.materials.slice(0, 3))

const kpiItems = computed(() => {
  const k = props.data.kpis
  const filtered = k.is_entity_filtered
  return [
    {
      key: 'requests',
      label: 'Заявок за период',
      value: k.total_requests_period ?? 0,
      icon: 'mdi-clipboard-list-outline',
      color: 'primary',
    },
    {
      key: 'weight',
      label: 'Собрано за период',
      value: formatKg(k.total_weight_kg_period ?? 0),
      trend: k.weight_trend_percent as number | null,
      icon: 'mdi-weight-kilogram',
      color: 'teal',
    },
    {
      key: 'completion',
      label: '% завершения',
      value: `${k.completion_rate_period ?? 0}%`,
      icon: 'mdi-check-circle-outline',
      color: 'success',
    },
    {
      key: 'avg',
      label: filtered ? 'Ср. вес заявки' : 'Ср. вес заявки (кг)',
      value: k.avg_weight_per_request ?? 0,
      icon: 'mdi-scale-balance',
      color: 'info',
    },
  ]
})

function drawCharts() {
  charts = disposeCharts(charts)
  const d = props.data

  if (chartCombined.value && (d.weight_over_time.length || d.requests_over_time.length)) {
    const labels = d.weight_over_time.length
      ? d.weight_over_time.map((w) => w.period_label)
      : d.requests_over_time.map((r) => r.period_label)
    charts.push(new Chart(chartCombined.value, {
      type: 'line',
      data: {
        labels,
        datasets: [
          {
            label: 'кг',
            data: d.weight_over_time.map((w) => w.total_kg),
            borderColor: '#0d9488',
            backgroundColor: 'rgba(13,148,136,0.1)',
            fill: true,
            tension: 0.3,
            yAxisID: 'y',
          },
          {
            label: 'Заявок',
            data: d.requests_over_time.map((r) => r.count),
            borderColor: '#059669',
            backgroundColor: 'rgba(5,150,105,0.06)',
            fill: true,
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
          y: { position: 'left', title: { display: true, text: 'кг' } },
          y1: { position: 'right', grid: { drawOnChartArea: false }, title: { display: true, text: 'Заявок' } },
        },
      },
    }))
  }

  if (chartCompletion.value && props.completion.total) {
    const { completed, total } = props.completion
    charts.push(new Chart(chartCompletion.value, {
      type: 'doughnut',
      data: {
        labels: ['Завершено', 'Остальные'],
        datasets: [{ data: [completed, total - completed], backgroundColor: ['#059669', '#e5e7eb'] }],
      },
      options: { responsive: true, maintainAspectRatio: false, cutout: '68%', plugins: { legend: { display: false } } },
    }))
  }

  charts.forEach((c) => c.resize())
}

function scheduleDraw() {
  nextTick(() => scheduleChartDraw(drawCharts))
}

watch(() => [props.data, props.completion] as const, scheduleDraw, { deep: true })
onMounted(scheduleDraw)
onBeforeUnmount(() => { charts = disposeCharts(charts) })
defineExpose({ drawCharts })
</script>

<style scoped>
.chart-wrap { position: relative; width: 100%; }
.material-rank { background: rgba(0,0,0,0.03); }
</style>
