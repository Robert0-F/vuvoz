<template>
  <div class="inst-stat-card" :class="{ 'inst-stat-card--elevated': elevated }">
    <div class="inst-stat-card__icon" :style="{ background: iconBg }">
      <v-icon :icon="icon" size="28" :color="iconColor" />
    </div>
    <div class="inst-stat-card__content">
      <div class="inst-stat-card__label">{{ title }}</div>
      <div class="inst-stat-card__value">{{ formattedValue }}</div>
      <div v-if="subtitle" class="inst-stat-card__subtitle">{{ subtitle }}</div>
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
    color?: 'primary' | 'success' | 'info' | 'warning'
    subtitle?: string
    elevated?: boolean
  }>(),
  { icon: 'mdi-chart-line', color: 'primary', elevated: true }
)

const colorMap = {
  primary: { bg: 'rgba(13, 148, 136, 0.12)', icon: '#0d9488' },
  success: { bg: 'rgba(5, 150, 105, 0.12)', icon: '#059669' },
  info: { bg: 'rgba(14, 165, 233, 0.12)', icon: '#0ea5e9' },
  warning: { bg: 'rgba(245, 158, 11, 0.12)', icon: '#f59e0b' },
}

const iconBg = computed(() => colorMap[props.color].bg)
const iconColor = computed(() => colorMap[props.color].icon)
const formattedValue = computed(() => {
  const v = props.value
  if (typeof v === 'number') return v.toLocaleString('ru-RU')
  return String(v)
})
</script>

<style scoped lang="scss">
.inst-stat-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem 1.5rem;
  background: var(--vuvoz-surface-elevated);
  border-radius: var(--vuvoz-radius-lg);
  border: 1px solid var(--vuvoz-border);
  transition: transform 0.2s var(--vuvoz-ease), box-shadow 0.2s var(--vuvoz-ease);

  &:hover {
    transform: translateY(-2px);
  }

  &--elevated {
    box-shadow: var(--vuvoz-shadow);
    &:hover {
      box-shadow: var(--vuvoz-shadow-lg);
    }
  }
}

.inst-stat-card__icon {
  width: 52px;
  height: 52px;
  border-radius: var(--vuvoz-radius);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.inst-stat-card__content {
  min-width: 0;
}

.inst-stat-card__label {
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--vuvoz-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 0.25rem;
}

.inst-stat-card__value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--vuvoz-text);
  letter-spacing: -0.02em;
}

.inst-stat-card__subtitle {
  font-size: 0.75rem;
  color: var(--vuvoz-text-muted);
  margin-top: 0.25rem;
}
</style>
