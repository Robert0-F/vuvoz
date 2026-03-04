<template>
  <div class="date-range-picker">
    <v-select
      v-model="preset"
      :items="presetItems"
      item-title="title"
      item-value="value"
      label="Период"
      density="compact"
      hide-details
      variant="outlined"
      class="date-range-picker__select"
      @update:model-value="onPresetChange"
    />
    <template v-if="preset === 'custom'">
      <v-text-field
        v-model="startDate"
        type="date"
        label="С"
        density="compact"
        hide-details
        variant="outlined"
        class="date-range-picker__input"
        @update:model-value="$emit('update:startDate', startDate)"
      />
      <v-text-field
        v-model="endDate"
        type="date"
        label="По"
        density="compact"
        hide-details
        variant="outlined"
        class="date-range-picker__input"
        @update:model-value="$emit('update:endDate', endDate)"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

const presetItems = [
  { title: 'Последние 30 дней', value: '30' },
  { title: 'Текущий год', value: 'year' },
  { title: 'Свой период', value: 'custom' },
]

const preset = ref('30')
const startDate = ref('')
const endDate = ref('')

const range = computed(() => {
  const end = new Date()
  const to = end.toISOString().slice(0, 10)
  let from: string
  if (preset.value === 'year') {
    from = `${end.getFullYear()}-01-01`
  } else if (preset.value === 'custom') {
    from = startDate.value
    return { startDate: from, endDate: endDate.value }
  } else {
    const d = new Date(end)
    d.setDate(d.getDate() - 30)
    from = d.toISOString().slice(0, 10)
  }
  return { startDate: from, endDate: to }
})

function onPresetChange() {
  if (preset.value === 'custom') {
    const end = new Date()
    endDate.value = end.toISOString().slice(0, 10)
    const d = new Date(end)
    d.setDate(d.getDate() - 30)
    startDate.value = d.toISOString().slice(0, 10)
  }
  emit('change', range.value)
}

const emit = defineEmits<{
  change: [payload: { startDate: string; endDate: string }]
  'update:startDate': [v: string]
  'update:endDate': [v: string]
}>()

watch(range, (r) => {
  if (preset.value !== 'custom') {
    emit('change', r)
  }
}, { immediate: true })

defineExpose({ range, preset, startDate, endDate })
</script>

<style lang="scss" scoped>
.date-range-picker {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;

  &__select {
    max-width: 200px;
  }

  &__input {
    max-width: 150px;
  }
}
</style>
