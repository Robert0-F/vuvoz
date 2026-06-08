<template>
  <div class="admin-stats-dashboard">
    <StatsFilterBar
      :loading="loading"
      :date-preset="datePreset"
      :expanded="filtersExpanded"
      :filters="filters"
      :date-preset-items="datePresetItems"
      :basis-items="basisItems"
      :company-filter-items="companyFilterItems"
      :institution-filter-items="institutionFilterItems"
      :material-filter-items="materialFilterItems"
      :chips="activeFilterChips"
      @update:date-preset="datePreset = $event"
      @update:expanded="filtersExpanded = $event"
      @update:filters="Object.assign(filters, $event)"
      @apply-preset="applyDatePreset"
      @apply="loadAnalytics"
      @reset="resetFilters"
      @company-change="onCompanyFilterChange"
      @remove-chip="removeFilterChip"
    />

    <v-alert
      v-if="data && activeFilterChips.length"
      type="info"
      variant="tonal"
      density="compact"
      class="mb-4"
    >
      Срез: {{ formatPeriodLabel(data.period) }}
    </v-alert>

    <v-alert v-if="error" type="error" class="mb-4">{{ error }}</v-alert>

    <v-progress-linear v-if="loading && !data" indeterminate color="primary" class="mb-4" />

    <template v-if="data">
      <v-progress-linear v-if="loading" indeterminate color="primary" class="mb-4" />

      <v-tabs v-model="sectionTab" class="dashboard-tabs mb-4" color="primary">
        <v-tab value="summary">Сводка</v-tab>
        <v-tab value="requests">Заявки</v-tab>
        <v-tab value="materials">Сырьё</v-tab>
        <v-tab value="partners">Партнёры</v-tab>
        <v-tab value="site_bonus">Сайт и бонусы</v-tab>
      </v-tabs>

      <v-window v-model="sectionTab">
        <v-window-item value="summary">
          <StatsOverviewTab
            ref="tabSummary"
            :data="data"
            :completion="completionSummary"
          />
        </v-window-item>
        <v-window-item value="requests">
          <StatsRequestsTab ref="tabRequests" :data="data" />
        </v-window-item>
        <v-window-item value="materials">
          <StatsMaterialsTab ref="tabMaterials" :data="data" />
        </v-window-item>
        <v-window-item value="partners">
          <StatsPartnersTab
            ref="tabPartners"
            :data="data"
            @drill-company="drillDownCompany"
            @drill-institution="drillDownInstitution"
          />
        </v-window-item>
        <v-window-item value="site_bonus">
          <StatsSiteBonusTab ref="tabSiteBonus" :data="data" />
        </v-window-item>
      </v-window>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, nextTick } from 'vue'
import { useAdminAnalytics, formatPeriodLabel } from '@/composables/useAdminAnalytics'
import StatsFilterBar from './stats/StatsFilterBar.vue'
import StatsOverviewTab from './stats/StatsOverviewTab.vue'
import StatsRequestsTab from './stats/StatsRequestsTab.vue'
import StatsMaterialsTab from './stats/StatsMaterialsTab.vue'
import StatsPartnersTab from './stats/StatsPartnersTab.vue'
import StatsSiteBonusTab from './stats/StatsSiteBonusTab.vue'
import { scheduleChartDraw } from './stats/chartTheme'
import './stats/chartTheme'

const {
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
} = useAdminAnalytics()

interface TabExpose { drawCharts?: () => void }
const tabSummary = ref<TabExpose | null>(null)
const tabRequests = ref<TabExpose | null>(null)
const tabMaterials = ref<TabExpose | null>(null)
const tabPartners = ref<TabExpose | null>(null)
const tabSiteBonus = ref<TabExpose | null>(null)

const tabRefs: Record<string, typeof tabSummary> = {
  summary: tabSummary,
  requests: tabRequests,
  materials: tabMaterials,
  partners: tabPartners,
  site_bonus: tabSiteBonus,
}

function drawActiveTab() {
  nextTick(() => {
    const draw = tabRefs[sectionTab.value]?.value?.drawCharts
    if (draw) scheduleChartDraw(draw)
  })
}

watch(sectionTab, drawActiveTab)
watch(data, () => {
  if (!loading.value) drawActiveTab()
})
watch(loading, (isLoading) => {
  if (!isLoading) drawActiveTab()
})

onMounted(() => {
  init()
})

defineExpose({ loadAnalytics })
</script>

<style scoped>
.admin-stats-dashboard { padding: 0 4px; }
.dashboard-tabs :deep(.v-tab) { text-transform: none; font-weight: 500; }
@media (max-width: 600px) {
  .admin-stats-dashboard { padding: 0; }
}
</style>
