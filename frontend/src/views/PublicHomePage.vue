<template>
  <div>
    <v-app-bar color="primary" density="compact" elevation="2" class="px-4 py-2">
      <v-app-bar-title class="text-h6 font-weight-bold pl-2">
        Вывоз макулатуры
      </v-app-bar-title>
      <v-spacer />
      <v-btn variant="text" @click="scrollTo('home')">Главная</v-btn>
      <v-btn variant="text" @click="scrollTo('about')">О сервисе</v-btn>
      <v-btn variant="text" @click="scrollTo('news')">Новости</v-btn>
      <v-btn variant="text" @click="scrollTo('contact')">Контакты</v-btn>
      <v-btn color="secondary" variant="elevated" @click="goToLogin">
        Войти
      </v-btn>
    </v-app-bar>

    <v-main>
      <section ref="homeRef" class="py-12 pa-4">
        <v-container>
          <v-row align="center" justify="center">
            <v-col cols="12" md="8">
              <h1 class="text-h3 text-center mb-4">
                Сервис вывоза макулатуры
              </h1>
              <p class="text-h6 text-center text-medium-emphasis mb-8">
                Удобная система для организаций и компаний по приёму и вывозу макулатуры.
                Создавайте заявки, отслеживайте статусы и управляйте процессами в одном месте.
              </p>
            </v-col>
          </v-row>
        </v-container>
      </section>

      <section ref="aboutRef" class="py-12 bg-surface-variant pa-4">
        <v-container>
          <h2 class="text-h4 mb-6 text-center">О сервисе</h2>
          <v-row>
            <v-col cols="12" md="4">
              <v-card variant="tonal" class="pa-4 h-100">
                <v-icon size="48" color="primary" class="mb-3">mdi-recycle</v-icon>
                <h3 class="text-h6 mb-2">Экология</h3>
                <p class="text-body-2">
                  Вносите вклад в переработку бумаги и картона, сокращая объёмы отходов.
                </p>
              </v-card>
            </v-col>
            <v-col cols="12" md="4">
              <v-card variant="tonal" class="pa-4 h-100">
                <v-icon size="48" color="primary" class="mb-3">mdi-file-document-multiple</v-icon>
                <h3 class="text-h6 mb-2">Удобные заявки</h3>
                <p class="text-body-2">
                  Создавайте заявки на вывоз, указывайте типы макулатуры и ориентировочный вес.
                </p>
              </v-card>
            </v-col>
            <v-col cols="12" md="4">
              <v-card variant="tonal" class="pa-4 h-100">
                <v-icon size="48" color="primary" class="mb-3">mdi-chart-line</v-icon>
                <h3 class="text-h6 mb-2">Прозрачность</h3>
                <p class="text-body-2">
                  Отслеживайте статусы заявок и историю вывозов.
                </p>
              </v-card>
            </v-col>
          </v-row>
        </v-container>
      </section>

      <section ref="newsRef" class="py-12 pa-4">
        <v-container>
          <h2 class="text-h4 mb-6 text-center">Новости</h2>
          <v-row v-if="loadingNews">
            <v-col cols="12" class="text-center">
              <v-progress-circular indeterminate color="primary" size="48" />
            </v-col>
          </v-row>
          <v-row v-else-if="news.length === 0">
            <v-col cols="12" class="text-center text-medium-emphasis">
              Пока нет новостей.
            </v-col>
          </v-row>
          <v-row v-else>
            <v-col
              v-for="article in news"
              :key="article.id"
              cols="12"
              sm="6"
              md="4"
            >
              <v-card
                class="h-100 d-flex flex-column"
                variant="outlined"
                hover
                @click="goToNews(article.id)"
              >
                <v-img
                  v-if="article.image_url"
                  :src="article.image_url"
                  height="180"
                  cover
                  gradient="to bottom, rgba(0,0,0,0), rgba(0,0,0,0.3)"
                />
                <v-img
                  v-else
                  src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='200'%3E%3Crect fill='%23e0e0e0' width='400' height='200'/%3E%3Ctext fill='%239e9e9e' font-family='sans-serif' font-size='24' x='50%25' y='50%25' text-anchor='middle' dy='.3em'%3ENет изображения%3C/text%3E%3C/svg%3E"
                  height="180"
                  cover
                />
                <v-card-title class="text-subtitle-1 font-weight-bold">
                  {{ article.title }}
                </v-card-title>
                <v-card-text class="flex-grow-1 text-body-2 text-medium-emphasis">
                  {{ article.excerpt }}
                </v-card-text>
                <v-card-actions>
                  <span class="text-caption text-medium-emphasis">
                    {{ formatDate(article.created_at) }}
                  </span>
                  <v-spacer />
                  <v-btn variant="text" color="primary" size="small">
                    Читать далее
                  </v-btn>
                </v-card-actions>
              </v-card>
            </v-col>
          </v-row>
        </v-container>
      </section>

      <section ref="contactRef" class="py-12 bg-surface-variant pa-4">
        <v-container>
          <h2 class="text-h4 mb-6 text-center">Контакты</h2>
          <v-row justify="center">
            <v-col cols="12" md="6" class="text-center">
              <p class="text-body-1">
                По вопросам работы сервиса обращайтесь к администратору.
              </p>
              <v-btn color="primary" variant="elevated" @click="goToLogin">
                Войти в систему
              </v-btn>
            </v-col>
          </v-row>
        </v-container>
      </section>

      <v-footer class="mt-auto">
        <v-container>
          <div class="text-center text-body-2 text-medium-emphasis">
            © {{ new Date().getFullYear() }} Сервис вывоза макулатуры
          </div>
        </v-container>
      </v-footer>
    </v-main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
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
const authStore = useAuthStore()
const userStore = useUserStore()

const homeRef = ref<HTMLElement | null>(null)
const aboutRef = ref<HTMLElement | null>(null)
const newsRef = ref<HTMLElement | null>(null)
const contactRef = ref<HTMLElement | null>(null)

const news = ref<NewsArticle[]>([])
const loadingNews = ref(true)

function scrollTo(section: string) {
  const refs: Record<string, typeof homeRef> = {
    home: homeRef,
    about: aboutRef,
    news: newsRef,
    contact: contactRef,
  }
  const el = refs[section]?.value
  if (el) el.scrollIntoView({ behavior: 'smooth' })
}

function formatDate(s: string) {
  if (!s) return ''
  return new Date(s).toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
}

async function loadNews() {
  loadingNews.value = true
  try {
    const { data } = await api.get<NewsArticle[]>('/news/')
    news.value = Array.isArray(data) ? data : []
  } catch {
    news.value = []
  } finally {
    loadingNews.value = false
  }
}

const hasMore = ref(false)

function goToNews(id: number) {
  router.push({ name: 'NewsDetail', params: { id: String(id) } })
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
  loadNews()
})
</script>
