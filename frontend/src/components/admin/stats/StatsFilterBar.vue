<template>
  <v-card class="rounded-lg mb-4" elevation="1">
    <v-card-text class="pa-4">
      <div class="d-flex flex-wrap align-center ga-3">
        <v-select
          :model-value="datePreset"
          :items="datePresetItems"
          label="Период"
          density="compact"
          variant="outlined"
          hide-details
          style="max-width: 160px"
          @update:model-value="$emit('update:datePreset', $event); $emit('applyPreset', $event)"
        />
        <v-text-field
          :model-value="filters.date_from"
          label="С"
          type="date"
          density="compact"
          variant="outlined"
          hide-details
          style="max-width: 145px"
          @update:model-value="updateFilter('date_from', $event)"
        />
        <v-text-field
          :model-value="filters.date_to"
          label="По"
          type="date"
          density="compact"
          variant="outlined"
          hide-details
          style="max-width: 145px"
          @update:model-value="updateFilter('date_to', $event)"
        />
        <v-select
          :model-value="filters.basis"
          :items="basisItems"
          label="Основа"
          density="compact"
          variant="outlined"
          hide-details
          style="max-width: 190px"
          @update:model-value="updateFilter('basis', $event)"
        />
        <v-btn color="primary" :loading="loading" @click="$emit('apply')">Применить</v-btn>
        <v-btn variant="text" @click="$emit('reset')">Сбросить</v-btn>
        <v-btn
          variant="tonal"
          size="small"
          :prepend-icon="expanded ? 'mdi-chevron-up' : 'mdi-filter-variant'"
          @click="$emit('update:expanded', !expanded)"
        >
          {{ expanded ? 'Скрыть фильтры' : 'Ещё фильтры' }}
        </v-btn>
      </div>

      <v-expand-transition>
        <div v-show="expanded" class="mt-4 pt-2 border-t">
          <div class="d-flex flex-wrap ga-3">
            <v-select
              :model-value="filters.company_id"
              :items="companyFilterItems"
              item-title="title"
              item-value="value"
              label="Компания"
              density="compact"
              variant="outlined"
              hide-details
              style="max-width: 240px"
              @update:model-value="updateFilter('company_id', $event); $emit('companyChange')"
            />
            <v-select
              :model-value="filters.institution_id"
              :items="institutionFilterItems"
              item-title="title"
              item-value="value"
              label="Организация"
              density="compact"
              variant="outlined"
              hide-details
              style="max-width: 260px"
              @update:model-value="updateFilter('institution_id', $event)"
            />
            <v-select
              :model-value="filters.material_type"
              :items="materialFilterItems"
              item-title="title"
              item-value="value"
              label="Материал"
              density="compact"
              variant="outlined"
              hide-details
              style="max-width: 220px"
              @update:model-value="updateFilter('material_type', $event)"
            />
            <v-text-field
              :model-value="filters.institution_type"
              label="Тип организации"
              density="compact"
              variant="outlined"
              hide-details
              clearable
              style="max-width: 180px"
              @update:model-value="updateFilter('institution_type', $event ?? '')"
            />
          </div>
        </div>
      </v-expand-transition>

      <div v-if="chips.length" class="d-flex flex-wrap ga-2 mt-3">
        <v-chip
          v-for="chip in chips"
          :key="chip.key"
          size="small"
          closable
          color="primary"
          variant="tonal"
          @click:close="$emit('removeChip', chip.key)"
        >
          {{ chip.label }}
        </v-chip>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import type { FilterOption } from '@/composables/useAdminAnalytics'

const props = defineProps<{
  loading: boolean
  datePreset: string
  expanded: boolean
  filters: {
    date_from: string
    date_to: string
    basis: string
    company_id: string
    institution_id: string
    institution_type: string
    material_type: string
  }
  datePresetItems: { title: string; value: string }[]
  basisItems: { title: string; value: string }[]
  companyFilterItems: FilterOption[]
  institutionFilterItems: FilterOption[]
  materialFilterItems: FilterOption[]
  chips: { key: string; label: string }[]
}>()

const emit = defineEmits<{
  apply: []
  reset: []
  applyPreset: [preset: string]
  companyChange: []
  removeChip: [key: string]
  'update:datePreset': [value: string]
  'update:expanded': [value: boolean]
  'update:filters': [filters: typeof props.filters]
}>()

function updateFilter(key: keyof typeof props.filters, value: string) {
  emit('update:filters', { ...props.filters, [key]: value })
}
</script>

<style scoped>
.border-t { border-top: 1px solid rgba(0,0,0,0.08); }
</style>
