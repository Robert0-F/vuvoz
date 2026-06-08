<template>

  <div v-if="data">

    <StatsKpiRow :items="kpiItems" />



    <v-row>

      <v-col cols="12" md="5">

        <v-card class="rounded-lg" elevation="1">

          <v-card-title>Воронка заявок</v-card-title>

          <v-card-subtitle class="pb-0">Распределение по статусам за период</v-card-subtitle>

          <v-card-text>

            <div class="chart-wrap" style="height: 260px">

              <canvas ref="chartFunnel"></canvas>

            </div>

          </v-card-text>

        </v-card>

      </v-col>

      <v-col cols="12" md="4">

        <v-card class="rounded-lg" elevation="1">

          <v-card-title>Срочность</v-card-title>

          <v-card-text>

            <div class="chart-wrap" style="height: 260px">
              <canvas ref="chartUrgency"></canvas>
            </div>
            <p v-if="!insights.urgency_breakdown.length" class="text-medium-emphasis text-center py-2">Нет данных о срочности</p>

          </v-card-text>

        </v-card>

      </v-col>

      <v-col cols="12" md="3">

        <v-card class="rounded-lg h-100" elevation="1" color="warning" variant="tonal">

          <v-card-title class="text-subtitle-1">Очередь сейчас</v-card-title>

          <v-card-text>

            <div class="text-h4 font-weight-bold">{{ insights.backlog.new }}</div>

            <div class="text-body-2 mb-3">новых заявок</div>

            <div class="text-h4 font-weight-bold">{{ insights.backlog.accepted }}</div>

            <div class="text-body-2">в работе</div>

            <v-divider class="my-3" />

            <div class="text-caption">Всего в очереди: {{ insights.backlog.total }}</div>

          </v-card-text>

        </v-card>

      </v-col>



      <v-col cols="12" md="6">

        <v-card class="rounded-lg" elevation="1">

          <v-card-title>Время до завершения</v-card-title>

          <v-card-subtitle class="pb-0">От создания до завершения заявки</v-card-subtitle>

          <v-card-text>

            <div class="chart-wrap" style="height: 240px">

              <canvas ref="chartSla"></canvas>

            </div>

            <p v-if="data.avg_completion_hours != null" class="text-body-2 mt-2 text-center">

              Среднее: <strong>{{ data.avg_completion_hours }} ч</strong>

            </p>

          </v-card-text>

        </v-card>

      </v-col>

      <v-col cols="12" md="6">

        <v-card class="rounded-lg" elevation="1">

          <v-card-title>Статусы по периодам</v-card-title>

          <v-card-text>

            <div class="chart-wrap" style="height: 240px">
              <canvas ref="chartStatusTime"></canvas>
            </div>
            <p v-if="!insights.status_over_time.length" class="text-medium-emphasis text-center py-2">Нет данных за период</p>

          </v-card-text>

        </v-card>

      </v-col>



      <v-col cols="12" md="6">

        <v-card class="rounded-lg" elevation="1">

          <v-card-title>Динамика заявок</v-card-title>

          <v-card-text>

            <div class="chart-wrap" style="height: 220px">
              <canvas ref="chartRequestsLine"></canvas>
            </div>
            <p v-if="!data.requests_over_time.length" class="text-medium-emphasis text-center py-2">Нет данных за период</p>

          </v-card-text>

        </v-card>

      </v-col>

      <v-col cols="12" md="6">

        <v-card class="rounded-lg" elevation="1">

          <v-card-title>% завершения по компаниям</v-card-title>

          <v-card-text>

            <v-table density="compact">

              <thead>

                <tr>

                  <th>Компания</th>

                  <th class="text-right">Всего</th>

                  <th class="text-right">%</th>

                </tr>

              </thead>

              <tbody>

                <tr v-for="r in data.completion_rate_by_company.slice(0, 8)" :key="r.company_id">

                  <td>{{ r.company_name }}</td>

                  <td class="text-right">{{ r.total }}</td>

                  <td class="text-right">

                    <v-chip size="x-small" :color="rateColor(r.completion_rate_percent)">

                      {{ r.completion_rate_percent }}%

                    </v-chip>

                  </td>

                </tr>

                <tr v-if="!data.completion_rate_by_company.length">

                  <td colspan="3" class="text-center text-medium-emphasis">Нет данных</td>

                </tr>

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

import { CHART_COLORS, SLA_COLORS, STATUS_COLORS, createChart, disposeCharts, scheduleChartDraw } from './chartTheme'

import type { AnalyticsData } from '@/composables/useAdminAnalytics'



const props = defineProps<{ data: AnalyticsData }>()



const DEFAULT_BUCKETS = [

  { bucket: 'under_24h', label: '< 24 ч', count: 0 },

  { bucket: '1_3d', label: '1–3 дн', count: 0 },

  { bucket: '3_7d', label: '3–7 дн', count: 0 },

  { bucket: 'over_7d', label: '> 7 дн', count: 0 },

]



const chartFunnel = ref<HTMLCanvasElement | null>(null)

const chartUrgency = ref<HTMLCanvasElement | null>(null)

const chartSla = ref<HTMLCanvasElement | null>(null)

const chartStatusTime = ref<HTMLCanvasElement | null>(null)

const chartRequestsLine = ref<HTMLCanvasElement | null>(null)

let charts: Chart[] = []



const insights = computed(() => {

  const ri = props.data.requests_insights

  return {

    funnel: ri?.funnel ?? [],

    backlog: ri?.backlog ?? { new: 0, accepted: 0, total: 0 },

    urgency_breakdown: ri?.urgency_breakdown ?? [],

    completion_time_buckets: ri?.completion_time_buckets ?? DEFAULT_BUCKETS,

    estimated_vs_actual: ri?.estimated_vs_actual ?? {

      request_count: 0,

      total_estimated_kg: 0,

      total_actual_kg: 0,

      avg_estimated_kg: 0,

      avg_actual_kg: 0,

      deviation_percent: 0,

    },

    status_over_time: ri?.status_over_time ?? [],

  }

})



const kpiItems = computed(() => {

  const eva = insights.value.estimated_vs_actual

  return [

    { key: 'backlog', label: 'В очереди', value: insights.value.backlog.total, icon: 'mdi-clock-outline', color: 'warning' },

    { key: 'completed', label: '% завершения', value: `${props.data.kpis.completion_rate_period ?? 0}%`, icon: 'mdi-check', color: 'success' },

    { key: 'sla', label: 'Ср. время (ч)', value: props.data.avg_completion_hours ?? '—', icon: 'mdi-timer-outline', color: 'info' },

    { key: 'deviation', label: 'Отклонение веса', value: eva.request_count ? `${eva.deviation_percent}%` : '—', icon: 'mdi-scale-unbalanced', color: 'secondary' },

  ]

})



function rateColor(p: number) {

  if (p >= 80) return 'success'

  if (p >= 50) return 'warning'

  return 'error'

}



function pushChart(canvas: HTMLCanvasElement | null, config: ConstructorParameters<typeof Chart>[1]) {
  if (!canvas) return
  try {
    charts.push(createChart(canvas, config))
  } catch (e) {
    console.error('Chart render error:', e)
  }
}

function drawCharts() {
  charts = disposeCharts(charts)
  const ins = insights.value

  if (chartFunnel.value && ins.funnel.length) {
    pushChart(chartFunnel.value, {

        type: 'bar',

        data: {

          labels: ins.funnel.map((f) => f.label),

          datasets: [{

            label: 'Заявок',

            data: ins.funnel.map((f) => f.count),

            backgroundColor: [STATUS_COLORS.new, STATUS_COLORS.accepted, STATUS_COLORS.completed, STATUS_COLORS.cancelled],

          }],

        },

        options: {

          indexAxis: 'y',

          responsive: true,

          maintainAspectRatio: false,

          plugins: {

            legend: { display: false },

            tooltip: {

              callbacks: {

                afterLabel: (ctx) => `${ins.funnel[ctx.dataIndex]?.percent ?? 0}%`,

              },

            },

          },

        },
    })
  }

  if (chartUrgency.value && ins.urgency_breakdown.length) {
    pushChart(chartUrgency.value, {

        type: 'doughnut',

        data: {

          labels: ins.urgency_breakdown.map((u) => u.urgency_display),

          datasets: [{

            data: ins.urgency_breakdown.map((u) => u.count),

            backgroundColor: CHART_COLORS.slice(0, ins.urgency_breakdown.length),

          }],

        },

        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } } },
    })
  }

  if (chartSla.value) {
    const buckets = ins.completion_time_buckets
    pushChart(chartSla.value, {

        type: 'bar',

        data: {

          labels: buckets.map((b) => b.label),

          datasets: [{ label: 'Заявок', data: buckets.map((b) => b.count), backgroundColor: SLA_COLORS }],

        },

        options: {

          responsive: true,

          maintainAspectRatio: false,

          plugins: { legend: { display: false } },

          scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } },
        },
    })
  }

  if (chartStatusTime.value && ins.status_over_time.length) {
    pushChart(chartStatusTime.value, {

        type: 'bar',

        data: {

          labels: ins.status_over_time.map((s) => s.period_label),

          datasets: [

            { label: 'Новые', data: ins.status_over_time.map((s) => s.new), backgroundColor: STATUS_COLORS.new, stack: 's' },

            { label: 'Принятые', data: ins.status_over_time.map((s) => s.accepted), backgroundColor: STATUS_COLORS.accepted, stack: 's' },

            { label: 'Завершённые', data: ins.status_over_time.map((s) => s.completed), backgroundColor: STATUS_COLORS.completed, stack: 's' },

            { label: 'Отменённые', data: ins.status_over_time.map((s) => s.cancelled), backgroundColor: STATUS_COLORS.cancelled, stack: 's' },

          ],

        },

        options: {

          responsive: true,

          maintainAspectRatio: false,

          plugins: { legend: { position: 'top' } },

          scales: { x: { stacked: true }, y: { stacked: true, beginAtZero: true } },
        },
    })
  }

  if (chartRequestsLine.value && props.data.requests_over_time.length) {
    pushChart(chartRequestsLine.value, {

        type: 'line',

        data: {

          labels: props.data.requests_over_time.map((r) => r.period_label),

          datasets: [{

            label: 'Заявок',

            data: props.data.requests_over_time.map((r) => r.count),

            borderColor: '#059669',

            fill: true,

            backgroundColor: 'rgba(5,150,105,0.1)',

            tension: 0.3,

          }],

        },

        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } },
    })
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


