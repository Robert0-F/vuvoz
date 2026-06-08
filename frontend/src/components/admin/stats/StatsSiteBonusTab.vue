<template>
  <div v-if="data">
    <h3 class="text-h6 mb-3">Заявки с сайта (без регистрации)</h3>
    <StatsKpiRow :items="pickupKpis" />

    <v-row class="mb-6">
      <v-col cols="12" md="5">
        <v-card class="rounded-lg" elevation="1">
          <v-card-title>По статусам</v-card-title>
          <v-card-text>
            <div class="chart-wrap" style="height: 240px">
              <canvas ref="chartPickupStatus"></canvas>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="7">
        <v-card class="rounded-lg" elevation="1">
          <v-card-title>Динамика заявок с сайта</v-card-title>
          <v-card-text>
            <div class="chart-wrap" style="height: 240px">
              <canvas ref="chartPickupTime"></canvas>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12">
        <v-card class="rounded-lg" elevation="1">
          <v-card-title>Материалы в заявках с сайта</v-card-title>
          <v-card-text>
            <v-table v-if="pickup.materials.length" density="compact">
              <thead>
                <tr><th>Материал</th><th class="text-right">кг</th><th class="text-right">Заявок</th></tr>
              </thead>
              <tbody>
                <tr v-for="m in pickup.materials" :key="m.material_type">
                  <td>{{ m.material_type_display }}</td>
                  <td class="text-right">{{ formatKg(m.total_kg) }}</td>
                  <td class="text-right">{{ m.request_count }}</td>
                </tr>
              </tbody>
            </v-table>
            <p v-else class="text-medium-emphasis text-center py-4">Нет заявок с сайта за период</p>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <h3 class="text-h6 mb-3">Бонусы и каталог</h3>
    <StatsKpiRow :items="bonusKpis" />

    <v-row>
      <v-col cols="12" md="6">
        <v-card class="rounded-lg" elevation="1">
          <v-card-title>Начисление баллов</v-card-title>
          <v-card-text>
            <div class="chart-wrap" style="height: 240px">
              <canvas ref="chartBonus"></canvas>
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
                <tr><th>Организация</th><th class="text-right">Баллов</th></tr>
              </thead>
              <tbody>
                <tr v-for="t in data.top_point_institutions" :key="t.institution_id">
                  <td>{{ t.institution_name }}</td>
                  <td class="text-right">{{ t.total_points }}</td>
                </tr>
                <tr v-if="!data.top_point_institutions.length">
                  <td colspan="2" class="text-center text-medium-emphasis">Нет данных</td>
                </tr>
              </tbody>
            </v-table>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12">
        <v-card class="rounded-lg" elevation="1">
          <v-card-title>Популярные товары</v-card-title>
          <v-card-text>
            <v-table density="compact">
              <thead>
                <tr><th>Товар</th><th class="text-right">Заказов</th><th class="text-right">Штук</th></tr>
              </thead>
              <tbody>
                <tr v-for="p in data.popular_products" :key="p.product_id">
                  <td>{{ p.product_name }}</td>
                  <td class="text-right">{{ p.order_count }}</td>
                  <td class="text-right">{{ p.total_quantity }}</td>
                </tr>
                <tr v-if="!data.popular_products.length">
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
import { CHART_COLORS, disposeCharts, scheduleChartDraw } from './chartTheme'
import type { AnalyticsData } from '@/composables/useAdminAnalytics'
import { formatKg, formatNum } from '@/composables/useAdminAnalytics'

const props = defineProps<{ data: AnalyticsData }>()

const chartPickupStatus = ref<HTMLCanvasElement | null>(null)
const chartPickupTime = ref<HTMLCanvasElement | null>(null)
const chartBonus = ref<HTMLCanvasElement | null>(null)
let charts: Chart[] = []

const pickup = computed(() => props.data.public_pickup ?? {
  kpis: { total_period: 0, new: 0, done: 0, total_kg: 0, total_payout: 0 },
  by_status: [],
  materials: [],
  over_time: [],
})

const pickupKpis = computed(() => {
  const k = pickup.value.kpis
  return [
    { key: 'total', label: 'Заявок с сайта', value: k.total_period, icon: 'mdi-web', color: 'primary' },
    { key: 'new', label: 'Новых', value: k.new, icon: 'mdi-new-box', color: 'warning' },
    { key: 'kg', label: 'кг в заявках', value: formatKg(k.total_kg), icon: 'mdi-weight', color: 'teal' },
    { key: 'payout', label: 'Ориент. выплата', value: formatNum(k.total_payout), icon: 'mdi-cash', color: 'success' },
  ]
})

const bonusKpis = computed(() => {
  const totalPoints = props.data.bonus_over_time.reduce((s, b) => s + b.total_points, 0)
  return [
    { key: 'points', label: 'Баллов (всего на графике)', value: formatNum(totalPoints), icon: 'mdi-star', color: 'purple' },
    { key: 'orgs', label: 'Организаций в топе', value: props.data.top_point_institutions.length, icon: 'mdi-school', color: 'info' },
    { key: 'products', label: 'Популярных товаров', value: props.data.popular_products.length, icon: 'mdi-gift', color: 'secondary' },
  ]
})

function drawCharts() {
  charts = disposeCharts(charts)
  const pp = pickup.value

  if (chartPickupStatus.value && pp.by_status.length) {
    charts.push(new Chart(chartPickupStatus.value, {
      type: 'doughnut',
      data: {
        labels: pp.by_status.map((s) => s.status_display),
        datasets: [{ data: pp.by_status.map((s) => s.count), backgroundColor: CHART_COLORS }],
      },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } } },
    }))
  }

  if (chartPickupTime.value && pp.over_time.length) {
    charts.push(new Chart(chartPickupTime.value, {
      type: 'line',
      data: {
        labels: pp.over_time.map((o) => o.period_label),
        datasets: [{ label: 'Заявок', data: pp.over_time.map((o) => o.count), borderColor: '#0ea5e9', fill: true, tension: 0.3 }],
      },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } },
    }))
  }

  if (chartBonus.value && props.data.bonus_over_time.length) {
    charts.push(new Chart(chartBonus.value, {
      type: 'line',
      data: {
        labels: props.data.bonus_over_time.map((b) => b.period_label),
        datasets: [{ label: 'Баллов', data: props.data.bonus_over_time.map((b) => b.total_points), borderColor: '#8b5cf6', fill: true, tension: 0.3 }],
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
