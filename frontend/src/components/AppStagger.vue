<template>
  <div class="app-stagger" :style="{ '--stagger-step': staggerStep + 's' }">
    <slot />
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    staggerStep?: number
  }>(),
  { staggerStep: 0.06 }
)
</script>

<style scoped>
.app-stagger > * {
  animation: vuvoz-fade-in-up 0.4s cubic-bezier(0.4, 0, 0.2, 1) backwards;
}
.app-stagger > *:nth-child(1) { animation-delay: calc(var(--stagger-step) * 1); }
.app-stagger > *:nth-child(2) { animation-delay: calc(var(--stagger-step) * 2); }
.app-stagger > *:nth-child(3) { animation-delay: calc(var(--stagger-step) * 3); }
.app-stagger > *:nth-child(4) { animation-delay: calc(var(--stagger-step) * 4); }
.app-stagger > *:nth-child(5) { animation-delay: calc(var(--stagger-step) * 5); }
.app-stagger > *:nth-child(6) { animation-delay: calc(var(--stagger-step) * 6); }
.app-stagger > *:nth-child(7) { animation-delay: calc(var(--stagger-step) * 7); }
.app-stagger > *:nth-child(8) { animation-delay: calc(var(--stagger-step) * 8); }
</style>
