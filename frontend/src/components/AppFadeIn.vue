<template>
  <div :class="wrapperClass" :style="wrapperStyle">
    <slot />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    delay?: number
    duration?: 'fast' | 'normal' | 'slow'
    direction?: 'up' | 'down' | 'none'
  }>(),
  { delay: 0, duration: 'normal', direction: 'up' }
)

const durationMap = { fast: 0.2, normal: 0.35, slow: 0.5 }
const wrapperClass = computed(() => {
  const dir = props.direction === 'up' ? 'vuvoz-fade-in-up' : props.direction === 'down' ? 'vuvoz-fade-in-down' : 'vuvoz-fade-in'
  return [dir]
})

const wrapperStyle = computed(() => ({
  animationDelay: `${props.delay}s`,
  animationDuration: `${durationMap[props.duration]}s`,
  animationFillMode: 'backwards',
}))
</script>
