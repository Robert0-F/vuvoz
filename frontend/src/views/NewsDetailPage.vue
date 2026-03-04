<template>
  <div class="news-detail-page">
    <v-app-bar color="primary" density="compact" elevation="0" class="px-4 py-2">
      <v-btn variant="text" icon="mdi-arrow-left" @click="goBack" />
      <v-app-bar-title class="pl-2">Новости</v-app-bar-title>
      <v-spacer />
      <v-btn variant="elevated" color="secondary" class="vuvoz-transition" @click="goToLogin">
        Войти
      </v-btn>
    </v-app-bar>

    <v-main class="bg-surface-variant">
      <v-container v-if="loading" class="py-12">
        <v-row justify="center">
          <v-col cols="12" class="text-center">
            <v-progress-circular indeterminate color="primary" size="48" />
          </v-col>
        </v-row>
      </v-container>
      <v-container v-else-if="article" class="py-8">
        <AppFadeIn direction="up">
          <v-btn variant="text" prepend-icon="mdi-arrow-left" class="mb-4" @click="goBack">
            К списку новостей
          </v-btn>
          <v-card variant="flat" class="news-article-card pa-4 pa-md-8" elevation="1">
            <h1 class="vuvoz-section-title text-h4 mb-4">{{ article.title }}</h1>
            <div class="text-caption text-medium-emphasis mb-4">
              {{ formatDate(article.created_at) }}
              <span v-if="article.author_username"> · {{ article.author_username }}</span>
            </div>
            <v-img
              v-if="article.image_url"
              :src="article.image_url"
              max-height="400"
              cover
              class="rounded-lg mb-6"
            />
            <div class="text-body-1 article-content">{{ article.content }}</div>
          </v-card>
        </AppFadeIn>
      </v-container>
      <v-container v-else class="py-12">
        <v-alert type="warning" class="rounded-lg">
          Статья не найдена.
        </v-alert>
        <v-btn class="mt-4" @click="goBack">На главную</v-btn>
      </v-container>
    </v-main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import AppFadeIn from '@/components/AppFadeIn.vue'
import { useRouter, useRoute } from 'vue-router'
import { api } from '@/api/axios'
import { useAuthStore } from '@/stores/auth'
import { useUserStore } from '@/stores/user'

interface NewsArticle {
  id: number
  title: string
  content: string
  excerpt: string
  image_url: string | null
  created_at: string
  is_published: boolean
  author_username: string
}

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const userStore = useUserStore()

const article = ref<NewsArticle | null>(null)
const loading = ref(true)

const articleId = computed(() => route.params.id)

function formatDate(s: string) {
  if (!s) return ''
  return new Date(s).toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
}

async function loadArticle() {
  loading.value = true
  try {
    const { data } = await api.get<NewsArticle>(`/news/${articleId.value}/`)
    article.value = data
  } catch {
    article.value = null
  } finally {
    loading.value = false
  }
}

function goBack() {
  router.push({ name: 'Home' })
}

async function goToLogin() {
  if (authStore.isAuthenticated) {
    await userStore.fetchMe().catch(() => authStore.logout())
    const role = userStore.role
    if (role === 'admin') router.push({ name: 'AdminDashboard' })
    else if (role === 'company') router.push({ name: 'CompanyDashboard' })
    else if (role === 'institution') router.push({ name: 'InstitutionDashboard' })
    else router.push({ name: 'Login' })
  } else {
    router.push({ name: 'Login' })
  }
}

onMounted(() => {
  loadArticle()
})
</script>

<style scoped>
.news-article-card {
  border-radius: var(--vuvoz-radius-lg);
  box-shadow: var(--vuvoz-shadow);
}
.article-content {
  white-space: pre-wrap;
  line-height: 1.6;
}
@media (max-width: 600px) {
  .news-detail-page .v-container { padding-left: 1rem; padding-right: 1rem; }
  .news-article-card :deep(.v-img) { max-height: 240px; }
}
</style>
