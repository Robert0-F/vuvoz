<template>
  <v-row dense class="mb-4">
    <v-col v-for="kpi in items" :key="kpi.key" cols="6" sm="4" md="3">
      <v-card class="kpi-card rounded-lg" elevation="1">
        <v-card-text class="pa-3 d-flex align-center ga-3">
          <v-avatar v-if="kpi.icon" :color="kpi.color || 'primary'" variant="tonal" size="40">
            <v-icon :icon="kpi.icon" size="22" />
          </v-avatar>
          <div>
            <div class="text-caption text-medium-emphasis">{{ kpi.label }}</div>
            <div class="text-h6 font-weight-bold">{{ kpi.value }}</div>
            <div
              v-if="kpi.trend != null"
              class="text-caption"
              :class="kpi.trend >= 0 ? 'text-success' : 'text-error'"
            >
              {{ kpi.trend >= 0 ? '↑' : '↓' }} {{ Math.abs(kpi.trend) }}% к пред. периоду
            </div>
          </div>
        </v-card-text>
      </v-card>
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import type { KpiCard } from '@/composables/useAdminAnalytics'

defineProps<{ items: KpiCard[] }>()
</script>

<style scoped>
.kpi-card { transition: transform 0.2s, box-shadow 0.2s; }
.kpi-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
</style>
