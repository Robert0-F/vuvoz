<template>
  <section ref="sectionRef" class="home-for-whom" :class="{ 'hp-visible': visible }">
    <div class="home-for-whom__inner">
      <h2 class="hp-section-title home-for-whom__title">Для кого Vuvoz</h2>
      <p class="hp-subtitle home-for-whom__subtitle">Организации любого типа получают вывоз макулатуры по заявке и бонусы за сданное сырьё.</p>

      <div class="home-for-whom__grid">
        <article
          v-for="(card, i) in cards"
          :key="card.title"
          class="home-for-whom__card hp-card hp-anim-in"
          :class="{ 'hp-visible': visible }"
          :style="{ transitionDelay: visible ? `${i * 0.08}s` : '0s' }"
        >
          <div class="home-for-whom__icon">{{ card.icon }}</div>
          <h3 class="home-for-whom__card-title">{{ card.title }}</h3>
          <p class="home-for-whom__card-text">{{ card.pain }}</p>
          <p class="home-for-whom__card-solution">{{ card.solution }}</p>
          <a href="#" class="home-for-whom__link" @click.prevent="$emit('scrollToContact')">Подробнее</a>
        </article>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const sectionRef = ref<HTMLElement | null>(null)
const visible = ref(false)

const cards = [
  { title: 'Офисы', icon: '🏢', pain: 'Скопление бумаги и архива.', solution: 'Настроим регулярный вывоз и расчёт стоимости под ваш объём.' },
  { title: 'Школы и детские сады', icon: '🏫', pain: 'Нужен раздельный сбор и экопросвещение.', solution: 'Подключим к программе и начислим баллы за макулатуру.' },
  { title: 'Торговые центры', icon: '🛒', pain: 'Много картона от упаковки.', solution: 'Вывоз по графику, взвешивание и документы для отчётности.' },
  { title: 'Склады', icon: '📦', pain: 'Крупные объёмы картона и бумаги.', solution: 'Гибкие лимиты и расчёт под ваши тоннажи.' },
]

onMounted(() => {
  const obs = new IntersectionObserver(
    ([e]) => { if (e.isIntersecting) visible.value = true },
    { threshold: 0.1 }
  )
  if (sectionRef.value) obs.observe(sectionRef.value)
})

defineEmits<{ scrollToContact: [] }>()
</script>

<style scoped lang="scss">
.home-for-whom {
  padding: clamp(3rem, 8vw, 5rem) 1.5rem;
  background: var(--vuvoz-surface-muted);
  opacity: 0;
  transform: translateY(20px);
  transition: opacity 0.6s var(--vuvoz-ease), transform 0.6s var(--vuvoz-ease);

  &.hp-visible {
    opacity: 1;
    transform: translateY(0);
  }
}

.home-for-whom__inner {
  max-width: 1200px;
  margin: 0 auto;
}

.home-for-whom__title {
  text-align: center;
  margin: 0 0 0.5rem;
}

.home-for-whom__subtitle {
  text-align: center;
  margin: 0 0 2.5rem;
  max-width: 560px;
  margin-left: auto;
  margin-right: auto;
}

.home-for-whom__grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1.5rem;
}

.home-for-whom__card {
  background: var(--vuvoz-surface-elevated);
  padding: 1.75rem;
  border: 1px solid var(--vuvoz-border);
}

.home-for-whom__icon {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.home-for-whom__card-title {
  font-size: 1.2rem;
  margin: 0 0 0.5rem;
}

.home-for-whom__card-text {
  font-size: 0.9rem;
  color: var(--vuvoz-text-secondary);
  margin: 0 0 0.5rem;
}

.home-for-whom__card-solution {
  font-size: 0.95rem;
  color: var(--vuvoz-text);
  margin: 0 0 1rem;
  line-height: 1.5;
}

.home-for-whom__link {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--vuvoz-primary);
  text-decoration: none;
  &:hover { text-decoration: underline; }
}
</style>
