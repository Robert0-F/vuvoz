<template>
  <div class="stats-widget" :class="{ 'stats-widget--pulse': pulse }">
    <div class="stats-widget__icon-wrap">
      <v-icon :icon="icon" size="28" />
    </div>
    <div class="stats-widget__content">
      <div class="stats-widget__label">{{ title }}</div>
      <div class="stats-widget__value">{{ formattedValue }}</div>
      <div v-if="trendLabel" class="stats-widget__trend" :class="trendClass">
        <v-icon :icon="trendIcon" size="14" />
        <span>{{ trendLabel }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    title: string
    value: string | number
    icon?: string
    pulse?: boolean
    trend?: number
    trendLabel?: string
  }>(),
  { icon: 'mdi-chart-box', pulse: false }
)

const formattedValue = computed(() => {
  if (typeof props.value === 'number') return props.value.toLocaleString('ru-RU')
  return props.value
})

const trendClass = computed(() => {
  if (props.trend === undefined) return ''
  if (props.trend > 0) return 'stats-widget__trend--up'
  if (props.trend < 0) return 'stats-widget__trend--down'
  return ''
})

const trendIcon = computed(() => {
  if (props.trend === undefined) return 'mdi-minus'
  if (props.trend > 0) return 'mdi-trending-up'
  if (props.trend < 0) return 'mdi-trending-down'
  return 'mdi-minus'
})
</script>

<style lang="scss" scoped>
.stats-widget {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 18px;
  border-radius: 16px;
  background: #fff;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
  transition: box-shadow 0.25s ease, transform 0.2s ease;
  border: 1px solid #e2e8f0;
}
.stats-widget:hover {
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.08);
}
.stats-widget--pulse .stats-widget__icon-wrap {
  animation: pulse 2s ease-in-out infinite;
}
.stats-widget__icon-wrap {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(13, 148, 136, 0.12);
  color: rgb(var(--v-theme-primary));
}
.stats-widget__label { font-size: 0.75rem; color: #64748b; margin-bottom: 4px; }
.stats-widget__value { font-size: 1.35rem; font-weight: 700; color: #0f172a; }
.stats-widget__trend { font-size: 0.7rem; margin-top: 4px; display: inline-flex; align-items: center; gap: 2px; }
.stats-widget__trend--up { color: #059669; }
.stats-widget__trend--down { color: #dc2626; }
@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.85; transform: scale(1.02); }
}
</style>
