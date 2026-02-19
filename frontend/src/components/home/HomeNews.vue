<template>
  <section ref="sectionRef" class="home-news" :class="{ 'hp-visible': visible }">
    <div class="home-news__inner">
      <h2 class="hp-section-title home-news__title">Новости</h2>
      <p class="hp-subtitle home-news__subtitle">Актуальные события и обновления сервиса.</p>

      <div v-if="loading" class="home-news__loading">Загрузка…</div>
      <div v-else-if="articles.length === 0" class="home-news__empty">Пока нет новостей.</div>
      <div v-else class="home-news__grid">
        <article
          v-for="article in articles"
          :key="article.id"
          class="home-news__card hp-card hp-anim-in"
          :class="{ 'hp-visible': visible }"
          @click="goToNews(article.id)"
        >
          <div class="home-news__img-wrap">
            <img
              v-if="article.image_url"
              :src="article.image_url"
              :alt="article.title"
              class="home-news__img"
            />
            <div v-else class="home-news__img home-news__img--placeholder" />
          </div>
          <div class="home-news__body">
            <h3 class="home-news__card-title">{{ article.title }}</h3>
            <p class="home-news__excerpt">{{ article.excerpt }}</p>
            <time class="home-news__date">{{ formatDate(article.created_at) }}</time>
          </div>
        </article>
      </div>
      <div class="home-news__more">
        <button type="button" class="home-news__btn" @click="goToAllNews">Все новости</button>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/api/axios'

interface Article {
  id: number
  title: string
  excerpt: string
  image_url: string | null
  created_at: string
}

const router = useRouter()
const sectionRef = ref<HTMLElement | null>(null)
const visible = ref(false)
const loading = ref(true)
const articles = ref<Article[]>([])

onMounted(async () => {
  const obs = new IntersectionObserver(
    ([e]) => { if (e.isIntersecting) visible.value = true },
    { threshold: 0.1 }
  )
  if (sectionRef.value) obs.observe(sectionRef.value)
  try {
    const { data } = await api.get<Article[]>('/news/')
    articles.value = (Array.isArray(data) ? data : []).slice(0, 3)
  } catch {
    articles.value = []
  } finally {
    loading.value = false
  }
})

function formatDate(s: string) {
  if (!s) return ''
  return new Date(s).toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' })
}

function goToNews(id: number) {
  router.push({ name: 'NewsDetail', params: { id: String(id) } })
}

function goToAllNews() {
  const el = document.getElementById('home-news')
  el?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}
</script>

<style scoped lang="scss">
.home-news {
  padding: clamp(3rem, 8vw, 5rem) 1.5rem;
  background: var(--vuvoz-surface-muted);
  opacity: 0;
  transform: translateY(20px);
  transition: opacity 0.6s var(--vuvoz-ease), transform 0.6s var(--vuvoz-ease);

  &.hp-visible {
    opacity: 1;
    transform: translateY(0);
  }
}

.home-news__inner {
  max-width: 1100px;
  margin: 0 auto;
}

.home-news__title {
  text-align: center;
  margin: 0 0 0.5rem;
}

.home-news__subtitle {
  text-align: center;
  margin: 0 0 2.5rem;
}

.home-news__loading,
.home-news__empty {
  text-align: center;
  color: var(--vuvoz-text-muted);
  padding: 2rem;
}

.home-news__grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}

@media (max-width: 900px) {
  .home-news__grid {
    grid-template-columns: 1fr;
  }
}

.home-news__card {
  background: var(--vuvoz-surface-elevated);
  border: 1px solid var(--vuvoz-border);
  overflow: hidden;
  cursor: pointer;
}

.home-news__img-wrap {
  aspect-ratio: 16/10;
  overflow: hidden;
}

.home-news__img {
  width: 100%;
  height: 100%;
  object-fit: cover;

  &--placeholder {
    background: linear-gradient(135deg, var(--vuvoz-surface-muted) 0%, var(--vuvoz-border) 100%);
  }
}

.home-news__body {
  padding: 1.25rem;
}

.home-news__card-title {
  font-size: 1.05rem;
  margin: 0 0 0.5rem;
  line-height: 1.3;
}

.home-news__excerpt {
  font-size: 0.9rem;
  color: var(--vuvoz-text-secondary);
  line-height: 1.5;
  margin: 0 0 0.75rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.home-news__date {
  font-size: 0.8rem;
  color: var(--vuvoz-text-muted);
}

.home-news__more {
  text-align: center;
  margin-top: 2rem;
}

.home-news__btn {
  padding: 0.75rem 1.5rem;
  border-radius: 10px;
  border: 2px solid var(--vuvoz-primary);
  background: transparent;
  color: var(--vuvoz-primary);
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
  &:hover {
    background: var(--vuvoz-primary);
    color: #fff;
  }
}
</style>
