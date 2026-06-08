<template>
  <div v-if="data">
    <v-alert
      v-if="entityProfile"
      type="info"
      variant="tonal"
      density="compact"
      class="mb-4"
    >
      <strong>Профиль среза:</strong>
      <span v-if="data.filters?.company_name"> {{ data.filters.company_name }}</span>
      <span v-if="data.filters?.institution_name"> · {{ data.filters.institution_name }}</span>
      · {{ data.kpis.total_requests_period }} заявок · {{ formatKg(data.kpis.total_weight_kg_period ?? 0) }} ·
      {{ data.kpis.completion_rate_period }}% завершено
    </v-alert>

    <StatsKpiRow :items="kpiItems" />

    <v-row>
      <v-col cols="12" md="6">
        <v-card class="rounded-lg" elevation="1">
          <v-card-title>Топ компаний по объёму</v-card-title>
          <v-card-subtitle class="pb-0">Клик по столбцу — фильтр по компании</v-card-subtitle>
          <v-card-text>
            <div class="chart-wrap" style="height: 320px">
              <canvas ref="chartCompanies"></canvas>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="6">
        <v-card class="rounded-lg" elevation="1">
          <v-card-title>Топ организаций</v-card-title>
          <v-card-subtitle class="pb-0">Клик — фильтр по организации</v-card-subtitle>
          <v-card-text>
            <div class="chart-wrap" style="height: 320px">
              <canvas ref="chartInstitutions"></canvas>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="6">
        <v-card class="rounded-lg" elevation="1">
          <v-card-title>По типам учреждений</v-card-title>
          <v-card-text>
            <div class="chart-wrap" style="height: 260px">
              <canvas ref="chartTypes"></canvas>
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
                <tr><th>Компания</th><th class="text-right">Организаций</th></tr>
              </thead>
              <tbody>
                <tr
                  v-for="c in data.institutions_per_company"
                  :key="c.company_id"
                  class="clickable-row"
                  @click="$emit('drillCompany', c.company_id)"
                >
                  <td>{{ c.company_name }}</td>
                  <td class="text-right">{{ c.institution_count }}</td>
                </tr>
                <tr v-if="!data.institutions_per_company.length">
                  <td colspan="2" class="text-center text-medium-emphasis">Нет данных</td>
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
import { CHART_COLORS, disposeCharts, scheduleChartDraw } from './chartTheme'
import type { AnalyticsData } from '@/composables/useAdminAnalytics'
import { formatKg } from '@/composables/useAdminAnalytics'

const props = defineProps<{ data: AnalyticsData }>()
const emit = defineEmits<{ drillCompany: [id: number]; drillInstitution: [id: number] }>()

const chartCompanies = ref<HTMLCanvasElement | null>(null)
const chartInstitutions = ref<HTMLCanvasElement | null>(null)
const chartTypes = ref<HTMLCanvasElement | null>(null)
let charts: Chart[] = []

const entityProfile = computed(() => props.data.kpis.is_entity_filtered || props.data.filters?.company_name)

const kpiItems = computed(() => {
  const k = props.data.kpis
  return [
    { key: 'companies', label: 'Компаний в срезе', value: k.total_companies ?? 0, icon: 'mdi-domain', color: 'primary' },
    { key: 'inst', label: 'Организаций в срезе', value: k.total_institutions ?? 0, icon: 'mdi-school', color: 'teal' },
    { key: 'top', label: 'Лидер (кг)', value: props.data.top_companies[0] ? formatKg(props.data.top_companies[0].total_kg) : '—', icon: 'mdi-trophy', color: 'warning' },
    { key: 'rate', label: '% завершения', value: `${k.completion_rate_period ?? 0}%`, icon: 'mdi-percent', color: 'success' },
  ]
})

function makeDrillHandler(
  canvas: HTMLCanvasElement,
  chart: Chart,
  items: { id: number }[],
  event: 'drillCompany' | 'drillInstitution',
) {
  canvas.onclick = (evt) => {
    const pts = chart.getElementsAtEventForMode(evt, 'nearest', { intersect: true }, true)
    if (!pts.length) return
    const idx = pts[0].index
    const id = items[idx]?.id
    if (id) emit(event, id)
  }
}

function drawCharts() {
  charts = disposeCharts(charts)
  const d = props.data

  if (chartCompanies.value && d.top_companies.length) {
    const top = d.top_companies.slice(0, 12)
    const chart = new Chart(chartCompanies.value, {
      type: 'bar',
      data: {
        labels: top.map((c) => c.company_name.slice(0, 16)),
        datasets: [{ label: 'кг', data: top.map((c) => c.total_kg), backgroundColor: '#0d9488' }],
      },
      options: { indexAxis: 'y', responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } },
    })
    charts.push(chart)
    makeDrillHandler(chartCompanies.value, chart, top.map((c) => ({ id: c.company_id })), 'drillCompany')
  }

  if (chartInstitutions.value && d.top_organizations.length) {
    const top = d.top_organizations.slice(0, 12)
    const chart = new Chart(chartInstitutions.value, {
      type: 'bar',
      data: {
        labels: top.map((o) => o.institution_name.slice(0, 14)),
        datasets: [{ label: 'кг', data: top.map((o) => o.total_kg), backgroundColor: '#059669' }],
      },
      options: { indexAxis: 'y', responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } },
    })
    charts.push(chart)
    makeDrillHandler(chartInstitutions.value, chart, top.map((o) => ({ id: o.institution_id })), 'drillInstitution')
  }

  if (chartTypes.value && d.institution_type_breakdown.length) {
    charts.push(new Chart(chartTypes.value, {
      type: 'pie',
      data: {
        labels: d.institution_type_breakdown.map((i) => i.institution_type),
        datasets: [{ data: d.institution_type_breakdown.map((i) => i.total_kg), backgroundColor: CHART_COLORS }],
      },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'right' } } },
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
.clickable-row { cursor: pointer; }
.clickable-row:hover { background: rgba(0,0,0,0.04); }
</style>
