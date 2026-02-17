<template>
  <div class="homepage">
    <v-app-bar color="primary" density="compact" elevation="0" class="px-4 py-2">
      <v-app-bar-title class="text-h6 font-weight-bold pl-2">
        Вывоз макулатуры
      </v-app-bar-title>
      <v-spacer />
      <v-btn variant="text" @click="scrollTo('home')">Главная</v-btn>
      <v-btn variant="text" @click="scrollTo('who')">С кем работаем</v-btn>
      <v-btn variant="text" @click="scrollTo('how')">Как работаем</v-btn>
      <v-btn variant="text" @click="scrollTo('news')">Новости</v-btn>
      <v-btn variant="text" @click="scrollTo('contact')">Контакты</v-btn>
      <v-btn
        variant="outlined"
        color="primary"
        class="mr-2"
        @click="openRegistrationDialog"
      >
        Регистрация
      </v-btn>
      <v-btn color="secondary" variant="elevated" @click="goToLogin">
        Войти
      </v-btn>
    </v-app-bar>

    <v-main>
      <!-- Hero -->
      <section ref="homeRef" class="hero py-16 pa-4">
        <v-container>
          <v-row align="center" justify="center">
            <v-col cols="12" md="10" class="text-center">
              <h1 class="hero-title text-h3 text-md-h2 font-weight-bold mb-4">
                Помогаем организациям эффективно управлять отходами
              </h1>
              <p class="hero-subtitle text-h6 text-md-h5 text-medium-emphasis mb-8">
                Вывоз и переработка макулатуры. Удобные заявки, прозрачный учёт и зелёные баллы для учреждений.
              </p>
              <div class="d-flex flex-wrap justify-center gap-3">
                <v-btn
                  size="large"
                  color="primary"
                  variant="elevated"
                  @click="goToLogin"
                >
                  Войти в личный кабинет
                </v-btn>
                <v-btn
                  size="large"
                  variant="outlined"
                  color="primary"
                  @click="openRegistrationDialog"
                >
                  Зарегистрировать учреждение
                </v-btn>
              </div>
            </v-col>
          </v-row>
        </v-container>
      </section>

      <!-- С кем мы работаем -->
      <section ref="whoRef" class="py-12 bg-surface-variant pa-4">
        <v-container>
          <h2 class="text-h4 text-md-h3 font-weight-bold mb-8 text-center">
            С кем мы работаем
          </h2>
          <v-row>
            <v-col v-for="card in whoWeWorkWith" :key="card.title" cols="12" sm="6" md="3">
              <v-card variant="flat" class="pa-4 h-100 rounded-lg" elevation="1">
                <v-icon size="40" color="primary" class="mb-3">{{ card.icon }}</v-icon>
                <h3 class="text-h6 font-weight-medium mb-2">{{ card.title }}</h3>
                <p class="text-body-2 text-medium-emphasis">{{ card.text }}</p>
              </v-card>
            </v-col>
          </v-row>
        </v-container>
      </section>

      <!-- Как мы работаем -->
      <section ref="howRef" class="py-12 pa-4">
        <v-container>
          <h2 class="text-h4 text-md-h3 font-weight-bold mb-8 text-center">
            Как мы работаем
          </h2>
          <v-row align="stretch">
            <v-col
              v-for="(step, i) in howWeWork"
              :key="step.title"
              cols="12"
              md="3"
            >
              <v-card variant="outlined" class="pa-4 h-100 d-flex flex-column rounded-lg">
                <span class="step-num text-h4 font-weight-bold text-primary mb-3">{{ i + 1 }}</span>
                <h3 class="text-h6 font-weight-medium mb-2">{{ step.title }}</h3>
                <p class="text-body-2 text-medium-emphasis flex-grow-1">{{ step.text }}</p>
              </v-card>
            </v-col>
          </v-row>
        </v-container>
      </section>

      <!-- Новости -->
      <section ref="newsRef" class="py-12 bg-surface-variant pa-4">
        <v-container>
          <h2 class="text-h4 text-md-h3 font-weight-bold mb-8 text-center">
            Новости
          </h2>
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
                class="h-100 d-flex flex-column rounded-lg"
                variant="flat"
                elevation="1"
                hover
                @click="goToNews(article.id)"
              >
                <v-img
                  v-if="article.image_url"
                  :src="article.image_url"
                  height="180"
                  cover
                  class="rounded-t-lg"
                  gradient="to bottom, rgba(0,0,0,0), rgba(0,0,0,0.2)"
                />
                <v-img
                  v-else
                  src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='200'%3E%3Crect fill='%23e8f5e9' width='400' height='200'/%3E%3Ctext fill='%23666' font-family='sans-serif' font-size='18' x='50%25' y='50%25' text-anchor='middle' dy='.3em'%3ENет изображения%3C/text%3E%3C/svg%3E"
                  height="180"
                  cover
                  class="rounded-t-lg"
                />
                <v-card-title class="text-subtitle-1 font-weight-bold pt-3">
                  {{ article.title }}
                </v-card-title>
                <v-card-text class="flex-grow-1 text-body-2 text-medium-emphasis">
                  {{ article.excerpt }}
                </v-card-text>
                <v-card-actions class="pt-0">
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

      <!-- Контакты и CTA -->
      <section ref="contactRef" class="py-12 pa-4">
        <v-container>
          <h2 class="text-h4 text-md-h3 font-weight-bold mb-6 text-center">
            Хотите подключить учреждение?
          </h2>
          <v-row justify="center">
            <v-col cols="12" md="8" class="text-center">
              <p class="text-body-1 text-medium-emphasis mb-6">
                Оставьте заявку на регистрацию — администратор свяжется с вами и подключит организацию к сервису вывоза макулатуры.
              </p>
              <v-btn
                size="large"
                color="primary"
                variant="elevated"
                @click="openRegistrationDialog"
              >
                Зарегистрировать учреждение
              </v-btn>
              <p class="text-body-2 text-medium-emphasis mt-6">
                Уже есть доступ? <v-btn variant="text" color="primary" size="small" @click="goToLogin">Войти</v-btn>
              </p>
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

    <!-- Регистрация учреждения -->
    <v-dialog v-model="registrationDialog" max-width="500" persistent>
      <v-card class="rounded-lg">
        <v-card-title class="d-flex align-center">
          Заявка на регистрацию учреждения
          <v-spacer />
          <v-btn icon variant="text" @click="registrationDialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        <v-card-text>
          <p class="text-body-2 text-medium-emphasis mb-4">
            Заполните форму. После рассмотрения заявки администратор свяжется с вами.
          </p>
          <v-form ref="registrationFormRef" @submit.prevent="submitRegistration">
            <v-text-field
              v-model="registrationForm.first_name"
              label="Имя *"
              variant="outlined"
              density="comfortable"
              class="mb-3"
              :rules="[v => !!v || 'Обязательное поле']"
            />
            <v-text-field
              v-model="registrationForm.patronymic"
              label="Отчество"
              variant="outlined"
              density="comfortable"
              class="mb-3"
            />
            <v-text-field
              v-model="registrationForm.institution_name"
              label="Название учреждения *"
              variant="outlined"
              density="comfortable"
              class="mb-3"
              :rules="[v => !!v || 'Обязательное поле']"
            />
            <v-textarea
              v-model="registrationForm.address"
              label="Адрес *"
              variant="outlined"
              density="comfortable"
              rows="2"
              class="mb-3"
              :rules="[v => !!v || 'Обязательное поле']"
            />
            <v-text-field
              v-model="registrationForm.phone"
              label="Телефон *"
              variant="outlined"
              density="comfortable"
              type="tel"
              placeholder="+7 (999) 123-45-67"
              :rules="[v => !!v || 'Обязательное поле']"
            />
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="registrationDialog = false">Отмена</v-btn>
          <v-btn
            color="primary"
            variant="elevated"
            :loading="registrationSending"
            @click="submitRegistration"
          >
            Отправить заявку
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Успех после регистрации -->
    <v-snackbar v-model="registrationSuccess" color="success" :timeout="4000">
      Заявка отправлена. Мы свяжемся с вами после рассмотрения.
    </v-snackbar>
    <v-snackbar v-model="registrationError" color="error" :timeout="5000">
      Не удалось отправить заявку. Попробуйте позже.
    </v-snackbar>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import type { VForm } from 'vuetify/components'
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

const whoWeWorkWith = [
  { title: 'Школы и детские сады', icon: 'mdi-school', text: 'Учебные заведения подключаются к раздельному сбору и получают баллы за макулатуру.' },
  { title: 'Офисы и бизнес-центры', icon: 'mdi-office-building', text: 'Удобный вывоз бумаги и картона по заявкам с личного кабинета.' },
  { title: 'Магазины и склады', icon: 'mdi-store', text: 'Регулярный вывоз упаковки и макулатуры по согласованному графику.' },
  { title: 'Учреждения', icon: 'mdi-domain', text: 'Любые организации могут оставить заявку на регистрацию и вывоз.' },
]

const howWeWork = [
  { title: 'Оставьте заявку', text: 'Зарегистрируйте учреждение на сайте или войдите в личный кабинет и создайте заявку на вывоз.' },
  { title: 'Укажите объём', text: 'Выберите типы макулатуры и ориентировочный вес. Система проверит лимиты.' },
  { title: 'Дождитесь вывоза', text: 'Компания-сборщик примет заявку и организует вывоз в удобное время.' },
  { title: 'Получайте баллы', text: 'За сданную макулатуру начисляются зелёные баллы — ими можно оплатить товары каталога.' },
]

const router = useRouter()
const authStore = useAuthStore()
const userStore = useUserStore()

const homeRef = ref<HTMLElement | null>(null)
const whoRef = ref<HTMLElement | null>(null)
const howRef = ref<HTMLElement | null>(null)
const newsRef = ref<HTMLElement | null>(null)
const contactRef = ref<HTMLElement | null>(null)

const news = ref<NewsArticle[]>([])
const loadingNews = ref(true)
const registrationDialog = ref(false)
const registrationSending = ref(false)
const registrationSuccess = ref(false)
const registrationError = ref(false)
const registrationFormRef = ref<VForm | null>(null)
const registrationForm = reactive({
  first_name: '',
  patronymic: '',
  institution_name: '',
  address: '',
  phone: '',
})

function scrollTo(section: string) {
  const refs: Record<string, typeof homeRef> = {
    home: homeRef,
    who: whoRef,
    how: howRef,
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

function openRegistrationDialog() {
  registrationForm.first_name = ''
  registrationForm.patronymic = ''
  registrationForm.institution_name = ''
  registrationForm.address = ''
  registrationForm.phone = ''
  registrationDialog.value = true
}

async function submitRegistration() {
  const valid = await registrationFormRef.value?.validate()
  if (!valid?.valid) return
  registrationSending.value = true
  registrationError.value = false
  try {
    await api.post('/registration-requests/', {
      first_name: registrationForm.first_name.trim(),
      patronymic: registrationForm.patronymic.trim(),
      institution_name: registrationForm.institution_name.trim(),
      address: registrationForm.address.trim(),
      phone: registrationForm.phone.trim(),
    })
    registrationSuccess.value = true
    registrationDialog.value = false
  } catch {
    registrationError.value = true
  } finally {
    registrationSending.value = false
  }
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

<style scoped>
.hero-title {
  line-height: 1.2;
}
.hero-subtitle {
  line-height: 1.4;
}
.step-num {
  line-height: 1;
}
</style>
