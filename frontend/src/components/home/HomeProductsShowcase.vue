<template>
  <section ref="sectionRef" class="home-products" :class="{ 'hp-visible': visible }">
    <div class="home-products__inner hp-container">
      <div class="home-products__head">
        <h2 class="hp-section-title home-products__title">Товары за зелёные баллы</h2>
        <p class="hp-subtitle home-products__subtitle">
          Накапливайте баллы за сдачу вторсырья и обменивайте их на канцелярию, эко-товары и сувениры.
        </p>
      </div>

      <div v-if="loading" class="home-products__state">Загрузка каталога…</div>
      <div v-else-if="!products.length" class="home-products__state">Каталог скоро появится.</div>
      <template v-else>
        <div v-if="categories.length" class="home-products__tabs">
          <button
            type="button"
            class="home-products__tab"
            :class="{ 'home-products__tab--active': activeCategory === 'all' }"
            @click="activeCategory = 'all'"
          >
            Все
          </button>
          <button
            v-for="c in categories"
            :key="c.id"
            type="button"
            class="home-products__tab"
            :class="{ 'home-products__tab--active': activeCategory === c.slug }"
            @click="activeCategory = c.slug"
          >
            {{ c.name }}
          </button>
        </div>

        <div class="home-products__grid">
          <article
            v-for="(p, i) in featured"
            :key="p.id"
            class="home-products__card hp-card"
            :style="{ '--delay': `${i * 0.08}s` }"
          >
            <div class="home-products__visual">
              <img
                v-if="resolveMediaUrl(p.image_url)"
                :src="resolveMediaUrl(p.image_url)"
                :alt="p.name"
                class="home-products__photo"
              />
              <div v-else class="home-products__icon-wrap">
                <v-icon icon="mdi-gift-outline" size="40" color="primary" />
              </div>
            </div>
            <p v-if="p.category_name" class="home-products__cat">{{ p.category_name }}</p>
            <h3 class="home-products__name">{{ p.name }}</h3>
            <p class="home-products__desc">{{ p.description || 'Товар из каталога наград' }}</p>
            <p class="home-products__price">
              <span class="home-products__price-value">{{ formatPoints(p.price_in_points) }}</span>
              <span class="home-products__price-unit">баллов</span>
            </p>
          </article>
        </div>
      </template>

      <div class="home-products__actions">
        <RouterLink to="/products" class="home-products__more">Весь каталог товаров</RouterLink>
        <button type="button" class="home-products__login" @click="$emit('login')">Войти и заказать</button>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { api } from '@/api/axios'
import type { ProductCategory, PublicProduct } from '@/types'
import { resolveMediaUrl } from '@/utils/mediaUrl'

defineEmits<{ login: [] }>()

const sectionRef = ref<HTMLElement | null>(null)
const visible = ref(false)
const loading = ref(true)
const categories = ref<ProductCategory[]>([])
const products = ref<PublicProduct[]>([])
const activeCategory = ref('all')

const filtered = computed(() => {
  if (activeCategory.value === 'all') return products.value
  return products.value.filter((p) => p.category_slug === activeCategory.value)
})

const featured = computed(() => filtered.value.slice(0, 4))

function formatPoints(v: string | number) {
  const n = typeof v === 'number' ? v : parseFloat(v)
  if (Number.isNaN(n)) return String(v)
  return n.toLocaleString('ru-RU', { maximumFractionDigits: 0 })
}

onMounted(async () => {
  const obs = new IntersectionObserver(
    ([e]) => { if (e?.isIntersecting) visible.value = true },
    { threshold: 0.12 },
  )
  if (sectionRef.value) obs.observe(sectionRef.value)
  try {
    const [catRes, prodRes] = await Promise.all([
      api.get<ProductCategory[]>('/public/products/categories/'),
      api.get<PublicProduct[]>('/public/products/'),
    ])
    categories.value = Array.isArray(catRes.data) ? catRes.data : []
    products.value = Array.isArray(prodRes.data) ? prodRes.data : []
  } catch {
    categories.value = []
    products.value = []
  } finally {
    loading.value = false
  }
})
</script>

<style scoped lang="scss">
.home-products {
  padding: clamp(3rem, 7vw, 4.5rem) 1.5rem;
  background: linear-gradient(180deg, #fff 0%, #ecfdf5 100%);
  opacity: 0;
  transform: translateY(16px);
  transition: opacity 0.6s ease, transform 0.6s ease;
  &.hp-visible { opacity: 1; transform: none; }
}

.home-products__head { text-align: center; margin-bottom: 1.75rem; }
.home-products__title { margin-bottom: 0.5rem; }
.home-products__subtitle { max-width: 640px; margin: 0 auto; }

.home-products__tabs {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.home-products__tab {
  border: 1px solid var(--vuvoz-border);
  background: #fff;
  border-radius: 999px;
  padding: 0.35rem 0.85rem;
  font-weight: 600;
  font-size: 0.85rem;
  cursor: pointer;
  &--active {
    background: var(--vuvoz-primary);
    border-color: var(--vuvoz-primary);
    color: #fff;
  }
}

.home-products__state {
  text-align: center;
  padding: 2rem;
  color: var(--vuvoz-text-muted, #64748b);
}

.home-products__grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 1.25rem;
  margin-bottom: 1.75rem;
}

.home-products__card {
  padding: 1rem;
  animation: home-products-in 0.5s ease backwards;
  animation-delay: var(--delay, 0s);
}

@keyframes home-products-in {
  from { opacity: 0; transform: translateY(10px); }
}

.home-products__visual {
  aspect-ratio: 4/3;
  border-radius: 10px;
  overflow: hidden;
  background: #f8fafc;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.75rem;
}

.home-products__photo { width: 100%; height: 100%; object-fit: cover; }
.home-products__cat {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--vuvoz-primary);
  margin-bottom: 0.2rem;
}
.home-products__name { font-size: 1rem; font-weight: 700; margin-bottom: 0.35rem; }
.home-products__desc {
  font-size: 0.88rem;
  color: var(--vuvoz-text-muted, #64748b);
  line-height: 1.4;
  margin-bottom: 0.5rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.home-products__price-value { font-size: 1.15rem; font-weight: 800; color: var(--vuvoz-primary); }
.home-products__price-unit { font-size: 0.85rem; color: var(--vuvoz-text-muted, #64748b); margin-left: 0.25rem; }

.home-products__actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 1rem;
}

.home-products__more {
  color: var(--vuvoz-primary);
  font-weight: 700;
  text-decoration: none;
  &:hover { text-decoration: underline; }
}

.home-products__login {
  background: var(--vuvoz-primary);
  color: #fff;
  border: none;
  border-radius: 10px;
  padding: 0.55rem 1.1rem;
  font-weight: 600;
  cursor: pointer;
}
</style>
