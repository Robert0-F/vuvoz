<template>
  <div class="products-page">
    <PublicSiteHeader @register="goRegister" @login="goLogin" />

    <main class="products-page__main">
      <h1 class="products-page__title">Каталог товаров за баллы</h1>
      <p class="products-page__lead">
        Организации накапливают зелёные баллы за сдачу вторсырья и могут обменять их на полезные товары.
        Для заказа войдите в личный кабинет учреждения.
      </p>

      <div v-if="loading" class="products-page__state">Загрузка каталога…</div>
      <template v-else>
        <div v-if="categories.length" class="products-page__tabs">
          <button
            type="button"
            class="products-page__tab"
            :class="{ 'products-page__tab--active': activeCategory === 'all' }"
            @click="activeCategory = 'all'"
          >
            Все
          </button>
          <button
            v-for="c in categories"
            :key="c.id"
            type="button"
            class="products-page__tab"
            :class="{ 'products-page__tab--active': activeCategory === c.slug }"
            @click="activeCategory = c.slug"
          >
            {{ c.name }}
          </button>
        </div>

        <div v-if="!filteredProducts.length" class="products-page__state">Товаров в этой категории пока нет.</div>
        <div v-else class="products-page__grid">
          <article v-for="p in filteredProducts" :key="p.id" class="products-page__card hp-card">
            <div class="products-page__visual">
              <img
                v-if="resolveMediaUrl(p.image_url)"
                :src="resolveMediaUrl(p.image_url)"
                :alt="p.name"
                class="products-page__img"
              />
              <div v-else class="products-page__placeholder">
                <v-icon icon="mdi-gift-outline" size="56" color="primary" />
              </div>
            </div>
            <div class="products-page__body">
              <p v-if="p.category_name" class="products-page__cat">{{ p.category_name }}</p>
              <h2 class="products-page__name">{{ p.name }}</h2>
              <p class="products-page__desc">{{ p.description || 'Описание скоро появится.' }}</p>
              <p class="products-page__price">
                <strong>{{ formatPoints(p.price_in_points) }}</strong> баллов
              </p>
            </div>
          </article>
        </div>

        <div class="products-page__cta">
          <p>Хотите заказать? Подключите организацию к платформе или войдите в кабинет.</p>
          <button type="button" class="products-page__cta-btn" @click="goLogin">Войти и заказать</button>
        </div>
      </template>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/api/axios'
import PublicSiteHeader from '@/components/PublicSiteHeader.vue'
import type { ProductCategory, PublicProduct } from '@/types'
import { resolveMediaUrl } from '@/utils/mediaUrl'

const router = useRouter()
const loading = ref(true)
const categories = ref<ProductCategory[]>([])
const products = ref<PublicProduct[]>([])
const activeCategory = ref('all')

const filteredProducts = computed(() => {
  if (activeCategory.value === 'all') return products.value
  return products.value.filter((p) => p.category_slug === activeCategory.value)
})

function formatPoints(v: string | number) {
  const n = typeof v === 'number' ? v : parseFloat(v)
  if (Number.isNaN(n)) return String(v)
  return n.toLocaleString('ru-RU', { maximumFractionDigits: 0 })
}

function goLogin() {
  router.push({ name: 'Login', query: { redirect: '/institution' } })
}

function goRegister() {
  router.push({ path: '/', hash: '#cta' })
}

onMounted(async () => {
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
.products-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #ecfdf5 0%, #fff 30%);
  padding-top: 72px;
}

.products-page__main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1.25rem 3rem;
}

.products-page__title {
  font-size: clamp(1.75rem, 4vw, 2.25rem);
  font-weight: 800;
  color: var(--vuvoz-text);
  margin-bottom: 0.5rem;
}

.products-page__lead {
  color: var(--vuvoz-text-muted, #64748b);
  max-width: 720px;
  margin-bottom: 1.5rem;
  line-height: 1.6;
}

.products-page__tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.products-page__tab {
  border: 1px solid var(--vuvoz-border);
  background: #fff;
  color: var(--vuvoz-text);
  border-radius: 999px;
  padding: 0.4rem 0.9rem;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  &--active {
    background: var(--vuvoz-primary);
    border-color: var(--vuvoz-primary);
    color: #fff;
  }
}

.products-page__state {
  text-align: center;
  padding: 3rem 1rem;
  color: var(--vuvoz-text-muted, #64748b);
}

.products-page__grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1.25rem;
}

.products-page__card {
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.products-page__visual {
  aspect-ratio: 4/3;
  background: #f8fafc;
  display: flex;
  align-items: center;
  justify-content: center;
}

.products-page__img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.products-page__placeholder {
  opacity: 0.7;
}

.products-page__body {
  padding: 1rem 1.1rem 1.25rem;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.products-page__cat {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--vuvoz-primary);
  margin-bottom: 0.25rem;
}

.products-page__name {
  font-size: 1.05rem;
  font-weight: 700;
  margin-bottom: 0.35rem;
}

.products-page__desc {
  font-size: 0.9rem;
  color: var(--vuvoz-text-muted, #64748b);
  line-height: 1.45;
  flex: 1;
  margin-bottom: 0.75rem;
}

.products-page__price {
  font-size: 1rem;
  color: var(--vuvoz-primary);
}

.products-page__cta {
  margin-top: 2.5rem;
  padding: 1.5rem;
  border-radius: 14px;
  background: rgba(13, 148, 136, 0.08);
  text-align: center;
  p { margin-bottom: 1rem; color: var(--vuvoz-text); }
}

.products-page__cta-btn {
  background: var(--vuvoz-primary);
  color: #fff;
  border: none;
  border-radius: 10px;
  padding: 0.65rem 1.25rem;
  font-weight: 600;
  cursor: pointer;
}
</style>
