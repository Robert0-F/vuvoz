<template>
  <section ref="sectionRef" class="home-how" :class="{ 'hp-visible': visible }">
    <div class="home-how__inner">
      <h2 class="hp-section-title home-how__title">Как это работает</h2>
      <p class="hp-subtitle home-how__subtitle">Четыре шага от заявки до оплаты и документов.</p>

      <div class="home-how__timeline">
        <div
          v-for="(step, i) in steps"
          :key="step.title"
          class="home-how__step hp-anim-in"
          :class="{ 'hp-visible': visible }"
          :style="{ transitionDelay: visible ? `${i * 0.12}s` : '0s' }"
        >
          <div class="home-how__num">{{ i + 1 }}</div>
          <div class="home-how__content">
            <h3 class="home-how__step-title">{{ step.title }}</h3>
            <p class="home-how__step-text">{{ step.text }}</p>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const sectionRef = ref<HTMLElement | null>(null)
const visible = ref(false)

const steps = [
  { title: 'Заявка', text: 'Оставьте заявку через сайт, личный кабинет или Telegram-бот — укажите тип и объём макулатуры.' },
  { title: 'Расчёт', text: 'Мгновенный расчёт стоимости по актуальным тарифам. Прозрачно и без скрытых платежей.' },
  { title: 'Вывоз', text: 'Водитель приезжает в удобное время, взвешивает и забирает сырьё. Фотофиксация при необходимости.' },
  { title: 'Оплата и документы', text: 'Средства зачисляются, выдаём документы для отчётности и начисляем зелёные баллы.' },
]

onMounted(() => {
  const obs = new IntersectionObserver(
    ([e]) => { if (e.isIntersecting) visible.value = true },
    { threshold: 0.1 }
  )
  if (sectionRef.value) obs.observe(sectionRef.value)
})
</script>

<style scoped lang="scss">
.home-how {
  padding: clamp(3rem, 8vw, 5rem) 1.5rem;
  opacity: 0;
  transform: translateY(20px);
  transition: opacity 0.6s var(--vuvoz-ease), transform 0.6s var(--vuvoz-ease);

  &.hp-visible {
    opacity: 1;
    transform: translateY(0);
  }
}

.home-how__inner {
  max-width: 900px;
  margin: 0 auto;
}

.home-how__title {
  text-align: center;
  margin: 0 0 0.5rem;
}

.home-how__subtitle {
  text-align: center;
  margin: 0 0 2.5rem;
}

.home-how__timeline {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.5rem;
}

@media (max-width: 768px) {
  .home-how__timeline {
    grid-template-columns: 1fr;
  }
}

.home-how__step {
  text-align: center;
  padding: 1.5rem 1rem;
  background: var(--vuvoz-surface-elevated);
  border-radius: var(--vuvoz-radius-lg);
  border: 1px solid var(--vuvoz-border);
  box-shadow: var(--vuvoz-shadow-sm);
}

.home-how__num {
  width: 48px;
  height: 48px;
  margin: 0 auto 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--vuvoz-primary) 0%, #14b8a6 100%);
  color: #fff;
  font-family: var(--hp-font-heading);
  font-weight: 800;
  font-size: 1.25rem;
}

.home-how__step-title {
  font-size: 1.1rem;
  margin: 0 0 0.5rem;
}

.home-how__step-text {
  font-size: 0.9rem;
  color: var(--vuvoz-text-secondary);
  line-height: 1.5;
  margin: 0;
}
</style>
