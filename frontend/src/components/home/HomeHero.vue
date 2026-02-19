<template>
  <section ref="sectionRef" class="home-hero" :class="{ 'hp-visible': visible }">
    <div class="home-hero__bg">
      <div class="home-hero__gradient" />
      <div class="home-hero__grid" aria-hidden="true" />
    </div>
    <div class="home-hero__content">
      <h1 class="home-hero__title hp-headline">
        Превратите макулатуру в ресурс для бизнеса
      </h1>
      <p class="home-hero__subtitle hp-subtitle">
        Автоматизация вывоза, прозрачные расчёты и бонусы за сданное сырьё. Удобный личный кабинет и вывоз по заявке.
      </p>
      <div class="home-hero__cta">
        <button type="button" class="home-hero__btn home-hero__btn--primary" @click="$emit('scrollToCalculator')">
          Рассчитать стоимость
        </button>
        <button type="button" class="home-hero__btn home-hero__btn--secondary" @click="$emit('scrollToProcess')">
          Как это работает
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
  scrollToCalculator: []
  scrollToProcess: []
}>()
</script>

<style scoped lang="scss">
.home-hero {
  min-height: 90vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  padding: clamp(2rem, 6vw, 4rem) 1.5rem;
  opacity: 0;
  transform: translateY(24px);
  transition: opacity 0.8s cubic-bezier(0.4, 0, 0.2, 1), transform 0.8s cubic-bezier(0.4, 0, 0.2, 1);

  &.hp-visible {
    opacity: 1;
    transform: translateY(0);
  }
}

.home-hero__bg {
  position: absolute;
  inset: 0;
  z-index: 0;
}

.home-hero__gradient {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #0f766e 0%, #0d9488 40%, #14b8a6 100%);
}

.home-hero__grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255,255,255,0.06) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.06) 1px, transparent 1px);
  background-size: 60px 60px;
}

.home-hero__content {
  position: relative;
  z-index: 1;
  max-width: 800px;
  margin: 0 auto;
  text-align: center;
}

.home-hero__title {
  font-size: clamp(2.25rem, 5vw, 3.5rem);
  color: #fff;
  margin: 0 0 1.25rem;
  text-shadow: 0 2px 20px rgba(0, 0, 0, 0.15);
}

.home-hero__subtitle {
  font-size: clamp(1rem, 2vw, 1.25rem);
  color: rgba(255, 255, 255, 0.92);
  line-height: 1.6;
  margin: 0 0 2.5rem;
  max-width: 560px;
  margin-left: auto;
  margin-right: auto;
}

.home-hero__cta {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  justify-content: center;
}

.home-hero__btn {
  font-family: var(--hp-font-heading);
  font-weight: 600;
  font-size: 1rem;
  padding: 0.875rem 1.75rem;
  border-radius: 12px;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  border: none;

  &:hover {
    transform: translateY(-2px);
  }

  &--primary {
    background: #fff;
    color: #0d9488;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.15);
    &:hover {
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
    }
  }

  &--secondary {
    background: rgba(255, 255, 255, 0.15);
    color: #fff;
    border: 2px solid rgba(255, 255, 255, 0.6);
    &:hover {
      background: rgba(255, 255, 255, 0.25);
    }
  }
}
</style>
