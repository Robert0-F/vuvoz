<template>
  <section ref="sectionRef" class="home-final-cta" :class="{ 'hp-visible': visible }">
    <div class="home-final-cta__bg" />
    <div class="home-final-cta__content">
      <h2 class="home-final-cta__title">Готовы начать зарабатывать на отходах?</h2>
      <p class="home-final-cta__sub">Присоединяйтесь к организациям, которые уже ведут учёт на «Зелёном счёте».</p>
      <div class="home-final-cta__buttons">
        <button type="button" class="home-final-cta__btn home-final-cta__btn--primary" @click="$emit('register')">
          Зарегистрировать организацию
        </button>
        <button type="button" class="home-final-cta__btn home-final-cta__btn--secondary" @click="$emit('scrollToCalculator')">
          Посмотреть тарифы
        </button>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const sectionRef = ref<HTMLElement | null>(null)
const visible = ref(false)

onMounted(() => {
  const obs = new IntersectionObserver(
    ([e]) => { if (e.isIntersecting) visible.value = true },
    { threshold: 0.2 }
  )
  if (sectionRef.value) obs.observe(sectionRef.value)
})

defineEmits<{
  register: []
  scrollToCalculator: []
}>()
</script>

<style scoped lang="scss">
.home-final-cta {
  position: relative;
  padding: clamp(4rem, 10vw, 6rem) 1.5rem;
  overflow: hidden;
  opacity: 0;
  transform: translateY(20px);
  transition: opacity 0.6s var(--vuvoz-ease), transform 0.6s var(--vuvoz-ease);

  &.hp-visible {
    opacity: 1;
    transform: translateY(0);
  }
}

.home-final-cta__bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #0f766e 0%, #0d9488 50%, #14b8a6 100%);
  &::after {
    content: '';
    position: absolute;
    inset: 0;
    background-image: radial-gradient(circle at 20% 50%, rgba(255,255,255,0.08) 0%, transparent 50%);
  }
}

.home-final-cta__content {
  position: relative;
  z-index: 1;
  max-width: 640px;
  margin: 0 auto;
  text-align: center;
}

.home-final-cta__title {
  font-family: var(--hp-font-heading);
  font-size: clamp(1.75rem, 4vw, 2.5rem);
  font-weight: 800;
  color: #fff;
  margin: 0 0 1rem;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.home-final-cta__sub {
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.9);
  margin: 0 0 2rem;
}

.home-final-cta__buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  justify-content: center;
}

.home-final-cta__btn {
  font-family: var(--hp-font-heading);
  font-weight: 600;
  font-size: 1rem;
  padding: 0.875rem 1.75rem;
  border-radius: 12px;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  border: none;

  &--primary {
    background: #fff;
    color: #0d9488;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.15);
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
    }
  }

  &--secondary {
    background: rgba(255, 255, 255, 0.15);
    color: #fff;
    border: 2px solid rgba(255, 255, 255, 0.6);
    &:hover {
      background: rgba(255, 255, 255, 0.25);
      transform: translateY(-2px);
    }
  }
}
</style>
