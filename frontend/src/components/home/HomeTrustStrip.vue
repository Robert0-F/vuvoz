<template>
  <section class="home-trust hp-container">
    <div class="home-trust__grid">
      <div v-for="item in items" :key="item.title" class="home-trust__item">
        <v-icon :icon="item.icon" size="32" color="primary" class="mb-2" />
        <strong class="home-trust__title">{{ item.title }}</strong>
        <span class="home-trust__text">{{ item.text }}</span>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
const items = [
  { icon: 'mdi-scale-balance', title: 'Честный вес', text: 'Взвешивание с фотофиксацией — без споров' },
  { icon: 'mdi-file-document-check', title: 'Документы', text: 'Акты и справки для отчётности' },
  { icon: 'mdi-leaf', title: 'Зелёный счёт', text: 'Баллы и прозрачный учёт выплат' },
  { icon: 'mdi-truck-fast', title: 'Вывоз по графику', text: 'Подстроимся под ваши сроки' },
]
</script>

<style scoped lang="scss">
.home-trust {
  padding: 2rem 0 0;
}

.home-trust__grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;

  @media (max-width: 900px) {
    grid-template-columns: repeat(2, 1fr);
  }
  @media (max-width: 480px) {
    grid-template-columns: 1fr;
  }
}

.home-trust__item {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 1.25rem;
  background: var(--vuvoz-surface-elevated);
  border-radius: var(--vuvoz-radius-lg);
  border: 1px solid var(--vuvoz-border);
}

.home-trust__title {
  font-size: 0.95rem;
  margin-bottom: 0.25rem;
}

.home-trust__text {
  font-size: 0.85rem;
  color: var(--vuvoz-text-secondary);
  line-height: 1.4;
}
</style>
