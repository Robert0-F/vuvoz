<template>
  <section ref="sectionRef" class="home-hero" :class="{ 'hp-visible': visible }">
    <div class="home-hero__bg">
      <div class="home-hero__gradient" />
      <div class="home-hero__mesh" aria-hidden="true" />
      <div class="home-hero__grid" aria-hidden="true" />
      <div class="home-hero__glow home-hero__glow--one" aria-hidden="true" />
      <div class="home-hero__glow home-hero__glow--two" aria-hidden="true" />
    </div>

    <div class="home-hero__inner hp-container">
      <div class="home-hero__content">
        <p class="home-hero__eyebrow hp-anim-in" :class="{ 'hp-visible': visible }">Платформа учёта вторсырья</p>
        <h1 class="home-hero__title hp-headline hp-anim-in" :class="{ 'hp-visible': visible }">
          Вывоз вторсырья с прозрачным
          <span class="home-hero__title-accent">«Зелёным счётом»</span>
        </h1>
        <p class="home-hero__subtitle hp-subtitle hp-anim-in" :class="{ 'hp-visible': visible }">
          Считайте вес и выплату в реальном времени, оформляйте заявку без регистрации и ведите учёт в личном кабинете.
        </p>

        <div class="home-hero__cta hp-anim-in" :class="{ 'hp-visible': visible }">
          <button type="button" class="home-hero__btn home-hero__btn--primary" @click="$emit('scrollToCalculator')">
            Рассчитать вывоз
          </button>
          <button type="button" class="home-hero__btn home-hero__btn--ghost" @click="$emit('openRegistration')">
            Подключиться
          </button>
        </div>

        <div class="home-hero__trust hp-anim-in" :class="{ 'hp-visible': visible }">
          <div class="home-hero__trust-item">Честное взвешивание</div>
          <div class="home-hero__trust-item">Документы для отчётности</div>
          <div class="home-hero__trust-item">Зелёные баллы</div>
        </div>
      </div>

      <div class="home-hero__visual hp-anim-in" :class="{ 'hp-visible': visible }" aria-label="Зелёный счёт">
        <div class="home-hero__logo-stage">
          <div class="home-hero__logo-halo" aria-hidden="true" />
          <div class="home-hero__logo-card">
            <img
              class="home-hero__logo-img"
              :src="heroLogoUrl"
              alt="Зелёный счёт"
              width="360"
              height="360"
              decoding="async"
              fetchpriority="high"
            />
          </div>
        </div>

        <div class="home-hero__float home-hero__float--one">
          <v-icon icon="mdi-scale-balance" size="22" color="#0d9488" />
          <span>₽/кг прозрачно</span>
        </div>
        <div class="home-hero__float home-hero__float--two">
          <v-icon icon="mdi-truck-fast" size="22" color="#0d9488" />
          <span>Вывоз по графику</span>
        </div>
        <div class="home-hero__float home-hero__float--three">
          <v-icon icon="mdi-file-document-check" size="22" color="#0d9488" />
          <span>Документы</span>
        </div>
      </div>
    </div>

    <p class="home-hero__disclaimer hp-container">
      Данные на странице носят информационный характер и уточняются менеджером при подготовке предложения.
    </p>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { HERO_LOGO_URL } from '@/constants/brandLogo'

const heroLogoUrl = HERO_LOGO_URL

const sectionRef = ref<HTMLElement | null>(null)
const visible = ref(false)

onMounted(() => {
  const obs = new IntersectionObserver(
    ([e]) => { if (e.isIntersecting) visible.value = true },
    { threshold: 0.15 },
  )
  if (sectionRef.value) obs.observe(sectionRef.value)
})

defineEmits<{
  scrollToCalculator: []
  scrollToProcess: []
  openRegistration: []
}>()
</script>

<style scoped lang="scss">
.home-hero {
  min-height: min(92vh, 900px);
  display: flex;
  flex-direction: column;
  justify-content: center;
  position: relative;
  overflow: hidden;
  padding: clamp(5rem, 8vw, 6.5rem) 0 clamp(1.5rem, 3vw, 2rem);
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
  background:
    radial-gradient(circle at 12% 18%, rgba(94, 234, 212, 0.42) 0%, transparent 45%),
    radial-gradient(circle at 88% 78%, rgba(45, 212, 191, 0.32) 0%, transparent 42%),
    linear-gradient(128deg, #064e47 0%, #0d9488 42%, #0f766e 72%, #0a5c55 100%);
}

.home-hero__mesh {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 70% 30%, rgba(255, 255, 255, 0.12) 0%, transparent 35%),
    radial-gradient(circle at 25% 75%, rgba(153, 246, 228, 0.15) 0%, transparent 40%);
  animation: heroMeshBreathe 8s ease-in-out infinite;
}

.home-hero__grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.05) 1px, transparent 1px);
  background-size: 56px 56px;
  mask-image: linear-gradient(180deg, rgba(0, 0, 0, 0.5) 0%, transparent 90%);
}

.home-hero__glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(12px);
  pointer-events: none;
}

.home-hero__glow--one {
  width: 280px;
  height: 280px;
  top: 10%;
  left: 5%;
  background: rgba(255, 255, 255, 0.12);
}

.home-hero__glow--two {
  width: 360px;
  height: 360px;
  right: 4%;
  bottom: 8%;
  background: rgba(167, 243, 208, 0.14);
}

.home-hero__inner {
  position: relative;
  z-index: 1;
  width: 100%;
  display: grid;
  grid-template-columns: 1.05fr 0.95fr;
  align-items: center;
  gap: clamp(1.5rem, 4vw, 3rem);
}

.home-hero__content {
  max-width: 580px;
}

.home-hero__eyebrow {
  margin: 0 0 1rem;
  color: rgba(167, 243, 208, 0.95);
  font-size: 0.78rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  font-weight: 700;
  transition-delay: 0.05s;
}

.home-hero__title {
  font-size: clamp(2rem, 4.2vw, 3.35rem);
  color: #fff;
  margin: 0 0 1rem;
  line-height: 1.12;
  text-shadow: 0 8px 32px rgba(0, 0, 0, 0.22);
  transition-delay: 0.12s;
}

.home-hero__title-accent {
  display: inline;
  background: linear-gradient(90deg, #ecfdf5 0%, #99f6e4 50%, #5eead4 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.home-hero__subtitle {
  font-size: clamp(1rem, 1.75vw, 1.15rem);
  color: rgba(255, 255, 255, 0.92);
  line-height: 1.65;
  margin: 0 0 1.75rem;
  transition-delay: 0.2s;
}

.home-hero__cta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 1.35rem;
  transition-delay: 0.28s;
}

.home-hero__btn {
  font-family: var(--hp-font-heading);
  font-weight: 600;
  font-size: 1rem;
  padding: 0.9rem 1.65rem;
  min-height: 48px;
  border-radius: 12px;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s;
  border: 2px solid transparent;

  &:hover {
    transform: translateY(-2px);
  }

  &--primary {
    background: #fff;
    color: #0d9488;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.18);
    &:hover {
      box-shadow: 0 10px 28px rgba(0, 0, 0, 0.24);
    }
  }

  &--ghost {
    background: rgba(255, 255, 255, 0.1);
    color: #fff;
    border-color: rgba(255, 255, 255, 0.45);
    backdrop-filter: blur(6px);
    &:hover {
      background: rgba(255, 255, 255, 0.2);
    }
  }
}

.home-hero__trust {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  transition-delay: 0.36s;
}

.home-hero__trust-item {
  color: #ecfdf5;
  background: rgba(6, 78, 71, 0.45);
  border: 1px solid rgba(167, 243, 208, 0.35);
  border-radius: 999px;
  padding: 0.45rem 0.85rem;
  font-size: 0.78rem;
  font-weight: 500;
}

.home-hero__visual {
  position: relative;
  min-height: 400px;
  padding: 1.5rem 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition-delay: 0.22s;
}

.home-hero__logo-stage {
  position: relative;
  z-index: 1;
  width: min(300px, 68vw);
  aspect-ratio: 1;
  display: grid;
  place-items: center;
}

.home-hero__logo-halo {
  position: absolute;
  inset: 6%;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.28) 0%, rgba(167, 243, 208, 0.12) 45%, transparent 72%);
  filter: blur(2px);
  animation: heroHaloBreathe 6s ease-in-out infinite;
}

.home-hero__logo-card {
  position: relative;
  width: 100%;
  aspect-ratio: 1;
  padding: clamp(0.75rem, 1.8vw, 1.1rem);
  border-radius: 24px;
  background: #fff;
  box-shadow:
    0 24px 56px rgba(0, 0, 0, 0.24),
    0 8px 24px rgba(6, 78, 71, 0.16),
    0 0 0 1px rgba(255, 255, 255, 0.65);
  transform: rotate(-2deg);
  transition: transform 0.35s ease, box-shadow 0.35s ease;

  &:hover {
    transform: rotate(0deg) translateY(-4px);
    box-shadow:
      0 32px 72px rgba(0, 0, 0, 0.28),
      0 12px 32px rgba(6, 78, 71, 0.2),
      0 0 0 1px rgba(255, 255, 255, 0.75);
  }
}

.home-hero__logo-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  display: block;
  border-radius: 12px;
}

.home-hero__float {
  position: absolute;
  z-index: 2;
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.55rem 0.85rem;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid rgba(255, 255, 255, 0.6);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.18);
  font-size: 0.82rem;
  font-weight: 600;
  color: #134e4a;
  backdrop-filter: blur(8px);
  animation: heroFloat 4.5s ease-in-out infinite;
  white-space: nowrap;
}

.home-hero__float--one {
  top: 2%;
  left: 0;
  animation-delay: 0s;
}

.home-hero__float--two {
  right: 0;
  top: 38%;
  animation-delay: 1.2s;
}

.home-hero__float--three {
  bottom: 2%;
  left: 0;
  animation-delay: 2.4s;
}

.home-hero__disclaimer {
  position: relative;
  z-index: 1;
  width: 100%;
  margin: 1.25rem auto 0;
  color: rgba(255, 255, 255, 0.72);
  font-size: 0.72rem;
  line-height: 1.45;
}

.home-hero .hp-anim-in {
  opacity: 0;
  transform: translateY(16px);
  transition: opacity 0.65s cubic-bezier(0.4, 0, 0.2, 1), transform 0.65s cubic-bezier(0.4, 0, 0.2, 1);

  &.hp-visible {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes heroHaloBreathe {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.82; transform: scale(1.04); }
}

@keyframes heroMeshBreathe {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.75; }
}

@keyframes heroFloat {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

@media (prefers-reduced-motion: reduce) {
  .home-hero__logo-halo,
  .home-hero__mesh,
  .home-hero__float {
    animation: none !important;
  }
}

@media (max-width: 1024px) {
  .home-hero__inner {
    grid-template-columns: 1fr;
    text-align: center;
  }

  .home-hero__content {
    max-width: 100%;
    order: 2;
  }

  .home-hero__visual {
    order: 1;
    min-height: 340px;
    padding: 1.25rem 0;
  }

  .home-hero__subtitle {
    margin-left: auto;
    margin-right: auto;
  }

  .home-hero__cta {
    justify-content: center;
  }

  .home-hero__trust {
    justify-content: center;
  }

  .home-hero__float--two {
    right: 0;
  }
}

@media (max-width: 768px) {
  .home-hero {
    min-height: auto;
    padding-top: 5rem;
  }

  .home-hero__logo-stage {
    width: min(260px, 72vw);
  }

  .home-hero__float {
    font-size: 0.75rem;
    padding: 0.45rem 0.65rem;
  }

  .home-hero__float--one {
    left: 0;
    top: 0;
  }

  .home-hero__float--three {
    left: 0;
    bottom: 0;
  }

  .home-hero__cta {
    flex-direction: column;
  }

  .home-hero__btn {
    width: 100%;
  }
}
</style>
