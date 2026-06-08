<template>
  <section ref="sectionRef" class="home-for-whom" :class="{ 'hp-visible': visible }">
    <div class="home-for-whom__inner hp-container">
      <h2 class="hp-section-title home-for-whom__title">С кем работает «Зелёный счёт»</h2>
      <p class="hp-subtitle home-for-whom__subtitle">
        Учреждения сдают вторсырьё, компании вывозят, все видят прозрачный учёт веса и выплат.
      </p>

      <div class="home-for-whom__grid">
        <article
          v-for="(card, i) in cards"
          :key="card.title"
          class="home-for-whom__card hp-card hp-anim-in"
          :class="{ 'hp-visible': visible }"
          :style="{ transitionDelay: visible ? `${i * 0.08}s` : '0s' }"
        >
          <div class="home-for-whom__icon-wrap">
            <v-icon :icon="card.mdi" size="36" color="primary" />
          </div>
          <h3 class="home-for-whom__card-title">{{ card.title }}</h3>
          <p class="home-for-whom__card-text">{{ card.pain }}</p>
          <p class="home-for-whom__card-solution">{{ card.solution }}</p>
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
  {
    title: 'Учреждения',
    mdi: 'mdi-domain',
    pain: 'Школы, офисы, магазины — накапливается макулатура и картон.',
    solution: 'Регулярный вывоз, зелёные баллы, документы и личный кабинет.',
  },
  {
    title: 'Компании (вывоз)',
    mdi: 'mdi-truck',
    pain: 'Хотите вывозить вторсырьё и подключать организации.',
    solution: 'Заявки от учреждений, учёт вывозов и статистика по месяцам.',
  },
  {
    title: 'Торговля и склады',
    mdi: 'mdi-warehouse',
    pain: 'Большие объёмы упаковки, нужен стабильный график.',
    solution: 'Взвешивание на месте, прозрачный расчёт ₽/кг, закрывающие документы.',
  },
]

onMounted(() => {
  const obs = new IntersectionObserver(
    ([e]) => { if (e.isIntersecting) visible.value = true },
    { threshold: 0.1 },
  )
  if (sectionRef.value) obs.observe(sectionRef.value)
})

defineEmits<{ scrollToContact: [] }>()
</script>

<style scoped lang="scss">
.home-for-whom {
  padding: clamp(3rem, 8vw, 5rem) 0;
  background: var(--vuvoz-surface-muted);
  opacity: 0;
  transform: translateY(20px);
  transition: opacity 0.6s var(--vuvoz-ease), transform 0.6s var(--vuvoz-ease);

  &.hp-visible {
    opacity: 1;
    transform: translateY(0);
  }
}

.home-for-whom__title {
  text-align: center;
  margin: 0 0 0.5rem;
}

.home-for-whom__subtitle {
  text-align: center;
  margin: 0 0 2.5rem;
  max-width: 640px;
  margin-left: auto;
  margin-right: auto;
}

.home-for-whom__grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;

  @media (max-width: 900px) {
    grid-template-columns: 1fr;
  }
}

.home-for-whom__card {
  padding: 1.75rem;
  background: var(--vuvoz-surface-elevated);
}

.home-for-whom__icon-wrap {
  width: 3.5rem;
  height: 3.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 14px;
  background: rgba(13, 148, 136, 0.1);
  margin-bottom: 1rem;
}

.home-for-whom__card-title {
  margin: 0 0 0.5rem;
  font-size: 1.15rem;
}

.home-for-whom__card-text {
  font-size: 0.9rem;
  color: var(--vuvoz-text-secondary);
  margin: 0 0 0.5rem;
}

.home-for-whom__card-solution {
  font-size: 0.9rem;
  color: var(--vuvoz-primary);
  font-weight: 600;
  margin: 0;
}
</style>
