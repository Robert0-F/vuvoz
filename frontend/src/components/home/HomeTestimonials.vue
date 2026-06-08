<template>
  <section ref="sectionRef" class="home-testimonials" :class="{ 'hp-visible': visible }">
    <div class="home-testimonials__inner">
      <h2 class="hp-section-title home-testimonials__title">Отзывы клиентов</h2>
      <p class="hp-subtitle home-testimonials__subtitle">Компании и организации о работе с «Зелёным счётом».</p>

      <div class="home-testimonials__carousel">
        <button type="button" class="home-testimonials__nav home-testimonials__nav--prev" aria-label="Назад" @click="prev">
          ‹
        </button>
        <div class="home-testimonials__track" ref="trackRef">
          <div
            v-for="(t, i) in testimonials"
            :key="i"
            class="home-testimonials__card hp-card"
            :class="{ 'home-testimonials__card--active': i === current }"
          >
            <div class="home-testimonials__stars">★★★★★</div>
            <blockquote class="home-testimonials__quote">«{{ t.quote }}»</blockquote>
            <div class="home-testimonials__author">
              <strong>{{ t.name }}</strong>, {{ t.position }}
            </div>
            <div class="home-testimonials__company">{{ t.company }}</div>
          </div>
        </div>
        <button type="button" class="home-testimonials__nav home-testimonials__nav--next" aria-label="Вперёд" @click="next">
          ›
        </button>
      </div>
      <div class="home-testimonials__dots">
        <button
          v-for="(_, i) in testimonials"
          :key="i"
          type="button"
          class="home-testimonials__dot"
          :class="{ 'home-testimonials__dot--active': i === current }"
          :aria-label="`Слайд ${i + 1}`"
          @click="current = i"
        />
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const sectionRef = ref<HTMLElement | null>(null)
const trackRef = ref<HTMLElement | null>(null)
const visible = ref(false)
const current = ref(0)

const testimonials = [
  {
    quote: 'Подключились за день. Вывоз по заявке — никаких лишних звонков. Баллы копим на канцтовары для школы.',
    name: 'Елена К.',
    position: 'директор школы',
    company: 'МБОУ СОШ № 42',
  },
  {
    quote: 'Раньше картон копился в углу. Теперь раз в две недели забирают, всё по акту. Удобно для отчётности.',
    name: 'Дмитрий В.',
    position: 'руководитель склада',
    company: 'Складской комплекс «Логист»',
  },
  {
    quote: 'Прозрачные цены и расчёт в личном кабинете. Рекомендую офисам с большим документооборотом.',
    name: 'Анна С.',
    position: 'офис-менеджер',
    company: 'ООО «Технопарк»',
  },
]

function prev() {
  current.value = (current.value - 1 + testimonials.length) % testimonials.length
}

function next() {
  current.value = (current.value + 1) % testimonials.length
}

onMounted(() => {
  const obs = new IntersectionObserver(
    ([e]) => { if (e.isIntersecting) visible.value = true },
    { threshold: 0.1 }
  )
  if (sectionRef.value) obs.observe(sectionRef.value)
})
</script>

<style scoped lang="scss">
.home-testimonials {
  padding: clamp(3rem, 8vw, 5rem) 1.5rem;
  opacity: 0;
  transform: translateY(20px);
  transition: opacity 0.6s var(--vuvoz-ease), transform 0.6s var(--vuvoz-ease);

  &.hp-visible {
    opacity: 1;
    transform: translateY(0);
  }
}

.home-testimonials__inner {
  max-width: 700px;
  margin: 0 auto;
}

.home-testimonials__title {
  text-align: center;
  margin: 0 0 0.5rem;
}

.home-testimonials__subtitle {
  text-align: center;
  margin: 0 0 2rem;
}

.home-testimonials__carousel {
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.home-testimonials__nav {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  border: 2px solid var(--vuvoz-border);
  background: #fff;
  font-size: 1.5rem;
  line-height: 1;
  cursor: pointer;
  color: var(--vuvoz-text);
  transition: border-color 0.2s, background 0.2s;
  &:hover {
    border-color: var(--vuvoz-primary);
    background: rgba(13, 148, 136, 0.06);
  }
}

.home-testimonials__track {
  flex: 1;
  min-width: 0;
  position: relative;
}

.home-testimonials__card {
  padding: 2rem;
  background: var(--vuvoz-surface-elevated);
  border: 1px solid var(--vuvoz-border);
  display: none;

  &--active {
    display: block;
    animation: fadeIn 0.3s ease;
  }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.home-testimonials__stars {
  color: #f59e0b;
  font-size: 1.1rem;
  letter-spacing: 0.1em;
  margin-bottom: 1rem;
}

.home-testimonials__quote {
  font-size: 1.1rem;
  line-height: 1.6;
  color: var(--vuvoz-text);
  margin: 0 0 1rem;
}

.home-testimonials__author {
  font-size: 0.95rem;
  margin-bottom: 0.25rem;
}

.home-testimonials__company {
  font-size: 0.875rem;
  color: var(--vuvoz-text-muted);
}

.home-testimonials__dots {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  margin-top: 1.5rem;
}

.home-testimonials__dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  border: none;
  background: var(--vuvoz-border);
  cursor: pointer;
  padding: 0;
  transition: background 0.2s;

  &--active {
    background: var(--vuvoz-primary);
    transform: scale(1.2);
  }
}
</style>
