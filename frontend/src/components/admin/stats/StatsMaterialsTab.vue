<template>
  <div v-if="data">
    <StatsKpiRow :items="kpiItems" />

    <v-row>
      <v-col cols="12" md="5">
        <v-card class="rounded-lg" elevation="1">
          <v-card-title>Доля материалов</v-card-title>
          <v-card-text>
            <div class="chart-wrap" style="height: 300px">
              <canvas ref="chartPie"></canvas>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="7">
        <v-card class="rounded-lg" elevation="1">
          <v-card-title>Топ материалов по весу</v-card-title>
          <v-card-text>
            <div class="chart-wrap" style="height: 300px">
              <canvas ref="chartBar"></canvas>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12">
        <v-card class="rounded-lg" elevation="1">
          <v-card-title>Динамика объёма (кг)</v-card-title>
          <v-card-text>
            <div class="chart-wrap" style="height: 260px">
              <canvas ref="chartWeight"></canvas>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="6">
        <v-card class="rounded-lg" elevation="1">
          <v-card-title>План vs факт (завершённые)</v-card-title>
          <v-card-text>
            <div v-if="eva.request_count" class="text-body-1">
              <p><strong>Заявок:</strong> {{ eva.request_count }}</p>
              <p><strong>Оценка:</strong> {{ formatKg(eva.total_estimated_kg) }}</p>
              <p><strong>Факт:</strong> {{ formatKg(eva.total_actual_kg) }}</p>
              <p :class="eva.deviation_percent >= 0 ? 'text-success' : 'text-error'">
                Отклонение: {{ eva.deviation_percent >= 0 ? '+' : '' }}{{ eva.deviation_percent }}%
              </p>
            </div>
            <p v-else class="text-medium-emphasis">Нет завершённых заявок с фактическим весом</p>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="6">
        <v-card class="rounded-lg" elevation="1">
          <v-card-title>Таблица материалов</v-card-title>
          <v-card-text>
            <v-table density="compact">
              <thead>
                <tr><th>Материал</th><th class="text-right">кг</th><th class="text-right">Заявок</th></tr>
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { Chart } from 'chart.js'
import './chartTheme'
import StatsKpiRow from './StatsKpiRow.vue'
import { CHART_COLORS, disposeCharts, scheduleChartDraw } from './chartTheme'
import type { AnalyticsData } from '@/composables/useAdminAnalytics'
import { formatKg, formatNum } from '@/composables/useAdminAnalytics'

const props = defineProps<{ data: AnalyticsData }>()

const chartPie = ref<HTMLCanvasElement | null>(null)
const chartBar = ref<HTMLCanvasElement | null>(null)
const chartWeight = ref<HTMLCanvasElement | null>(null)
let charts: Chart[] = []

const eva = computed(() => props.data.requests_insights?.estimated_vs_actual ?? {
  request_count: 0,
  total_estimated_kg: 0,
  total_actual_kg: 0,
  avg_estimated_kg: 0,
  avg_actual_kg: 0,
  deviation_percent: 0,
})

const kpiItems = computed(() => {
  const k = props.data.kpis
  const matCount = props.data.materials.length
  return [
    { key: 'weight', label: 'Собрано кг', value: formatKg(k.total_weight_kg_period ?? 0), icon: 'mdi-weight', color: 'teal' },
    { key: 'types', label: 'Типов материалов', value: matCount, icon: 'mdi-recycle', color: 'primary' },
    { key: 'est', label: 'Ориент. стоимость', value: formatNum(k.total_estimated_value ?? 0), icon: 'mdi-currency-rub', color: 'info' },
    { key: 'act', label: 'Факт. стоимость', value: formatNum(k.total_actual_value ?? 0), icon: 'mdi-cash-check', color: 'success' },
  ]
})

function drawCharts() {
  charts = disposeCharts(charts)
  const d = props.data

  if (chartPie.value && d.materials.length) {
    charts.push(new Chart(chartPie.value, {
      type: 'doughnut',
      data: {
        labels: d.materials.map((m) => m.material_type_display),
        datasets: [{ data: d.materials.map((m) => m.total_kg), backgroundColor: CHART_COLORS.slice(0, d.materials.length) }],
      },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'right' } } },
    }))
  }

  if (chartBar.value && d.materials.length) {
    const top = d.materials.slice(0, 10)
    charts.push(new Chart(chartBar.value, {
      type: 'bar',
      data: {
        labels: top.map((m) => m.material_type_display),
        datasets: [{ label: 'кг', data: top.map((m) => m.total_kg), backgroundColor: CHART_COLORS.slice(0, top.length) }],
      },
      options: { indexAxis: 'y', responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } },
    }))
  }

  if (chartWeight.value && d.weight_over_time.length) {
    charts.push(new Chart(chartWeight.value, {
      type: 'line',
      data: {
        labels: d.weight_over_time.map((w) => w.period_label),
        datasets: [{ label: 'кг', data: d.weight_over_time.map((w) => w.total_kg), borderColor: '#0d9488', fill: true, tension: 0.3 }],
      },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } },
    }))
  }

  charts.forEach((c) => c.resize())
}

function scheduleDraw() {
  nextTick(() => scheduleChartDraw(drawCharts))
}

watch(() => props.data, scheduleDraw, { deep: true })
onMounted(scheduleDraw)
onBeforeUnmount(() => { charts = disposeCharts(charts) })
defineExpose({ drawCharts })
</script>

<style scoped>
.chart-wrap { position: relative; width: 100%; }
</style>
