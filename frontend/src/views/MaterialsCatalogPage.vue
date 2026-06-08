<template>
  <div class="materials-page">
    <PublicSiteHeader @register="goHomeCta" @login="goLogin" />

    <main class="materials-page__main">
      <h1 class="materials-page__title">Вторичное сырьё и цены</h1>
      <p class="materials-page__lead">
        Мы вывозим и принимаем перечисленные фракции. Цена указана за килограмм при сдаче на переработку.
      </p>

      <div v-if="loading" class="materials-page__state">Загрузка…</div>
      <div v-else-if="!materials.length" class="materials-page__state">Список материалов пока пуст.</div>
      <div v-else class="materials-page__grid">
        <article v-for="m in materials" :key="m.id" class="materials-page__card hp-card">
          <div class="materials-page__visual">
            <img
              v-if="resolveMediaUrl(m.image_url)"
              :src="resolveMediaUrl(m.image_url)"
              :alt="m.name"
              class="materials-page__img"
            />
            <img
              v-else-if="resolveMediaUrl(m.icon_url)"
              :src="resolveMediaUrl(m.icon_url)"
              :alt="m.name"
              class="materials-page__icon-img"
            />
            <div v-else class="materials-page__icon">
              <v-icon :icon="materialMdiIcon(m.code, m.icon)" size="56" color="primary" />
            </div>
          </div>
          <div class="materials-page__body">
            <h2 class="materials-page__name">{{ m.name }}</h2>
            <p class="materials-page__desc">{{ m.short_description || 'Вывоз по заявке, взвешивание на месте.' }}</p>
            <p class="materials-page__price">
              <strong>{{ formatPrice(m.price_per_kg) }}</strong> ₽ / кг
            </p>
          </div>
        </article>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/api/axios'
import PublicSiteHeader from '@/components/PublicSiteHeader.vue'
import type { PublicMaterial } from '@/types'
import { resolveMediaUrl } from '@/utils/mediaUrl'
import { materialMdiIcon } from '@/utils/materialIcon'

const router = useRouter()
const materials = ref<PublicMaterial[]>([])
const loading = ref(true)

function goHomeCta() {
  router.push({ path: '/', hash: '#cta' })
}

function goLogin() {
  router.push({ name: 'Login' })
}

function formatPrice(v: string) {
  const n = parseFloat(v)
  if (Number.isNaN(n)) return v
  return n.toLocaleString('ru-RU', { maximumFractionDigits: 2 })
}

onMounted(async () => {
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
.materials-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #f0fdfa 0%, #fff 35%);
  padding-top: 64px;
}

.materials-page__main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2.5rem 1.25rem 4rem;
}

.materials-page__title {
  margin: 0 0 0.5rem;
  font-size: clamp(1.75rem, 4vw, 2.25rem);
  font-weight: 800;
  color: var(--vuvoz-text);
}

.materials-page__lead {
  margin: 0 0 2rem;
  color: var(--vuvoz-text-muted);
  max-width: 640px;
}

.materials-page__state {
  text-align: center;
  padding: 3rem;
  color: var(--vuvoz-text-muted);
}

.materials-page__grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}

.materials-page__card {
  overflow: hidden;
  border: 1px solid var(--vuvoz-border);
  display: flex;
  flex-direction: column;
  transition: box-shadow 0.25s, transform 0.25s;

  &:hover {
    transform: translateY(-4px);
    box-shadow: var(--vuvoz-shadow-lg);
  }
}

.materials-page__visual {
  height: 180px;
  background: linear-gradient(145deg, rgba(13, 148, 136, 0.15), rgba(255, 255, 255, 0.5));
  display: flex;
  align-items: center;
  justify-content: center;
}

.materials-page__img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.materials-page__icon-img {
  width: 96px;
  height: 96px;
  object-fit: contain;
}

.materials-page__body {
  padding: 1.25rem;
}

.materials-page__name {
  margin: 0 0 0.5rem;
  font-size: 1.15rem;
}

.materials-page__desc {
  margin: 0 0 1rem;
  font-size: 0.9rem;
  color: var(--vuvoz-text-muted);
  line-height: 1.45;
}

.materials-page__price {
  margin: 0;
  font-size: 1.1rem;
  color: #059669;

  strong {
    font-size: 1.35rem;
  }
}
</style>
