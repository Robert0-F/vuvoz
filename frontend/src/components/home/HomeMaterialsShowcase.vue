<template>
  <section ref="sectionRef" class="home-materials" :class="{ 'hp-visible': visible }">
    <div class="home-materials__inner hp-container">
      <div class="home-materials__head">
        <h2 class="hp-section-title home-materials__title">Скупка вторичного сырья</h2>
        <p class="hp-subtitle home-materials__subtitle">
          Актуальные цены за килограмм. Вывозим макулатуру, картон, пластик, стекло и другие фракции.
        </p>
      </div>

      <div v-if="loading" class="home-materials__state">Загрузка цен…</div>
      <div v-else-if="!featured.length" class="home-materials__state">Цены скоро появятся.</div>
      <div v-else class="home-materials__grid">
        <article
          v-for="(m, i) in featured"
          :key="m.id"
          class="home-materials__card hp-card"
          :style="{ '--delay': `${i * 0.08}s` }"
        >
          <div class="home-materials__visual">
            <img
              v-if="resolveMediaUrl(m.image_url)"
              :src="resolveMediaUrl(m.image_url)"
              :alt="m.name"
              class="home-materials__photo"
            />
            <img
              v-else-if="resolveMediaUrl(m.icon_url)"
              :src="resolveMediaUrl(m.icon_url)"
              :alt="m.name"
              class="home-materials__icon-img"
            />
            <div v-else class="home-materials__icon-wrap">
              <v-icon :icon="materialMdiIcon(m.code, m.icon)" size="40" color="primary" />
            </div>
          </div>
          <h3 class="home-materials__name">{{ m.name }}</h3>
          <p class="home-materials__desc">{{ m.short_description || 'Регулярный вывоз и честный вес' }}</p>
          <p class="home-materials__price">
            <span class="home-materials__price-value">{{ formatPrice(m.price_per_kg) }}</span>
            <span class="home-materials__price-unit">₽ / кг</span>
          </p>
        </article>
      </div>

      <div class="home-materials__actions">
        <RouterLink to="/materials" class="home-materials__more">Посмотреть всё сырьё</RouterLink>
        <button type="button" class="home-materials__calc" @click="$emit('scroll-to-calculator')">
          Рассчитать вывоз
        </button>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { api } from '@/api/axios'
import type { PublicMaterial } from '@/types'
import { resolveMediaUrl } from '@/utils/mediaUrl'
import { materialMdiIcon } from '@/utils/materialIcon'

defineEmits<{ 'scroll-to-calculator': [] }>()

const sectionRef = ref<HTMLElement | null>(null)
const visible = ref(false)
const materials = ref<PublicMaterial[]>([])
const loading = ref(true)

const featured = computed(() => materials.value.slice(0, 4))

function formatPrice(v: string) {
  const n = parseFloat(v)
  if (Number.isNaN(n)) return v
  return n.toLocaleString('ru-RU', { minimumFractionDigits: 0, maximumFractionDigits: 2 })
}

onMounted(async () => {
  const obs = new IntersectionObserver(
    ([e]) => { if (e?.isIntersecting) visible.value = true },
    { threshold: 0.12 },
  )
  if (sectionRef.value) obs.observe(sectionRef.value)
  try {
    const { data } = await api.get<PublicMaterial[]>('/public/materials/')
    materials.value = Array.isArray(data) ? data : []
  } catch {
    materials.value = []
  } finally {
    loading.value = false
  }
})
</script>

<style scoped lang="scss">
.home-materials {
  padding: clamp(3rem, 7vw, 4.5rem) 1.5rem;
  background: linear-gradient(180deg, #f8fafc 0%, #fff 100%);
  opacity: 0;
  transform: translateY(20px);
  transition: opacity 0.55s var(--vuvoz-ease), transform 0.55s var(--vuvoz-ease);

  &.hp-visible {
    opacity: 1;
    transform: translateY(0);
  }
}

.home-materials__inner {
  max-width: 1200px;
  margin: 0 auto;
}

.home-materials__head {
  text-align: center;
  margin-bottom: 2rem;
}

.home-materials__title {
  margin: 0 0 0.5rem;
}

.home-materials__subtitle {
  margin: 0 auto;
  max-width: 640px;
}

.home-materials__state {
  text-align: center;
  color: var(--vuvoz-text-muted);
  padding: 2rem;
}

.home-materials__grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.25rem;
}

@media (max-width: 1024px) {
  .home-materials__grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 520px) {
  .home-materials__grid {
    grid-template-columns: 1fr;
  }
}

.home-materials__card {
  padding: 1.25rem;
  border: 1px solid var(--vuvoz-border);
  display: flex;
  flex-direction: column;
  transition: transform 0.25s var(--vuvoz-ease), box-shadow 0.25s var(--vuvoz-ease);

  &:hover {
    transform: translateY(-4px);
    box-shadow: var(--vuvoz-shadow-lg);
  }
}

.home-materials__visual {
  height: 140px;
  border-radius: 12px;
  background: linear-gradient(145deg, rgba(13, 148, 136, 0.12), rgba(16, 185, 129, 0.06));
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1rem;
  overflow: hidden;
}

.home-materials__photo {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.home-materials__icon-img {
  width: 72px;
  height: 72px;
  object-fit: contain;
}

.home-materials__icon-wrap {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--vuvoz-shadow-sm);
}

.home-materials__name {
  margin: 0 0 0.35rem;
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--vuvoz-text);
}

.home-materials__desc {
  margin: 0 0 1rem;
  font-size: 0.85rem;
  color: var(--vuvoz-text-muted);
  line-height: 1.4;
  flex: 1;
}

.home-materials__price {
  margin: 0;
  display: flex;
  align-items: baseline;
  gap: 0.35rem;
}

.home-materials__price-value {
  font-size: 1.5rem;
  font-weight: 800;
  color: #059669;
}

.home-materials__price-unit {
  font-size: 0.9rem;
  color: var(--vuvoz-text-muted);
}

.home-materials__actions {
  margin-top: 2rem;
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 1rem;
}

.home-materials__more {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 48px;
  padding: 0 1.5rem;
  border-radius: 12px;
  border: 2px solid var(--vuvoz-primary);
  color: var(--vuvoz-primary);
  font-weight: 600;
  text-decoration: none;
  transition: background 0.2s, color 0.2s;

  &:hover {
    background: rgba(13, 148, 136, 0.08);
  }
}

.home-materials__calc {
  min-height: 48px;
  padding: 0 1.75rem;
  border: none;
  border-radius: 12px;
  background: var(--vuvoz-primary);
  color: #fff;
  font-weight: 600;
  cursor: pointer;
  transition: filter 0.2s, transform 0.2s;

  &:hover {
    filter: brightness(1.05);
    transform: translateY(-1px);
  }
}
</style>
