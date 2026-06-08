<template>
  <section ref="sectionRef" class="home-benefits" :class="{ 'hp-visible': visible }">
    <div class="home-benefits__inner hp-container">
      <h2 class="hp-section-title home-benefits__title">Почему «Зелёный счёт»</h2>
      <p class="hp-subtitle home-benefits__subtitle">Прозрачность, удобство и выгода для каждой организации.</p>

      <div class="home-benefits__grid">
        <div
          v-for="(item, i) in benefits"
          :key="item.title"
          class="home-benefits__item hp-anim-in"
          :class="{ 'hp-visible': visible }"
          :style="{ transitionDelay: visible ? `${i * 0.08}s` : '0s' }"
          @mouseenter="hovered = i"
          @mouseleave="hovered = -1"
        >
          <div class="home-benefits__icon-wrap" :class="{ 'home-benefits__icon-wrap--hover': hovered === i }">
            <span class="home-benefits__icon">{{ item.icon }}</span>
          </div>
          <h3 class="home-benefits__item-title">{{ item.title }}</h3>
          <p class="home-benefits__item-desc">{{ item.desc }}</p>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const sectionRef = ref<HTMLElement | null>(null)
const visible = ref(false)
const hovered = ref(-1)

const benefits = [
  { icon: '⚖️', title: 'Прозрачное взвешивание с фотофиксацией', desc: 'Фиксируем вес и состояние сырья — никаких споров.' },
  { icon: '💰', title: 'Мгновенные бонусы на счёт', desc: 'Зелёные баллы за сданную макулатуру можно тратить в каталоге.' },
  { icon: '📱', title: 'Личный кабинет и Telegram-бот', desc: 'Заявки, история вывозов и уведомления в одном месте.' },
  { icon: '📄', title: 'Документы для отчётности', desc: 'Акт приёма-передачи и справки для бухгалтерии.' },
  { icon: '📅', title: 'Вывоз по вашим срокам', desc: 'Укажите желаемую дату — подстроимся под вас.' },
  { icon: '🔄', title: 'Один контракт на всё', desc: 'Разные типы макулатуры — один сервис и один расчёт.' },
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
.home-benefits {
  padding: clamp(3rem, 8vw, 5rem) 1.5rem;
  background: linear-gradient(180deg, #f0fdfa 0%, #fff 50%, var(--vuvoz-surface-muted) 100%);
  opacity: 0;
  transform: translateY(20px);
  transition: opacity 0.6s var(--vuvoz-ease), transform 0.6s var(--vuvoz-ease);

  &.hp-visible {
    opacity: 1;
    transform: translateY(0);
  }
}

.home-benefits__inner {
  max-width: 1100px;
  margin: 0 auto;
}

.home-benefits__title {
  text-align: center;
  margin: 0 0 0.5rem;
}

.home-benefits__subtitle {
  text-align: center;
  margin: 0 0 2.5rem;
}

.home-benefits__grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}

@media (max-width: 900px) {
  .home-benefits__grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 500px) {
  .home-benefits__grid {
    grid-template-columns: 1fr;
  }
}

.home-benefits__item {
  background: var(--vuvoz-surface-elevated);
  padding: 1.75rem;
  border-radius: var(--vuvoz-radius-lg);
  border: 1px solid var(--vuvoz-border);
  transition: transform 0.25s var(--vuvoz-ease), box-shadow 0.25s var(--vuvoz-ease), border-color 0.25s;

  &:hover {
    transform: translateY(-6px);
    box-shadow: var(--vuvoz-shadow-lg);
    border-color: rgba(var(--v-theme-primary), 0.25);
  }
}

.home-benefits__icon-wrap {
  width: 3.25rem;
  height: 3.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 14px;
  background: linear-gradient(135deg, rgba(var(--v-theme-primary), 0.12), rgba(var(--v-theme-primary), 0.04));
  margin-bottom: 1rem;
  transition: transform 0.25s var(--vuvoz-ease);

  &--hover {
    transform: scale(1.08);
  }
}

.home-benefits__icon {
  font-size: 1.75rem;
  line-height: 1;
}

.home-benefits__item-title {
  font-size: 1.05rem;
  margin: 0 0 0.5rem;
}

.home-benefits__item-desc {
  font-size: 0.9rem;
  color: var(--vuvoz-text-secondary);
  line-height: 1.5;
  margin: 0;
}
</style>
