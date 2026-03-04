<template>
  <div class="login-page">
    <v-container fluid class="login-page__container fill-height">
      <v-row align="center" justify="center">
        <v-col cols="12" sm="10" md="6" lg="4" class="login-page__col">
          <AppFadeIn direction="up" :delay="0.05">
            <v-card class="login-card" elevation="0">
              <v-card-title class="login-card__title">
                Компания по вывозу макулатуры
              </v-card-title>
              <v-card-subtitle class="login-card__subtitle text-center mb-4 text-medium-emphasis">
                Вход в систему
              </v-card-subtitle>

              <v-form @submit.prevent="onSubmit" ref="formRef">
                <v-text-field
                  v-model="username"
                  label="Логин"
                  type="text"
                  variant="outlined"
                  :error-messages="errors.username"
                  density="comfortable"
                  prepend-inner-icon="mdi-account"
                  class="mb-2 login-field"
                  autocomplete="username"
                />
                <v-text-field
                  v-model="password"
                  label="Пароль"
                  :type="showPassword ? 'text' : 'password'"
                  variant="outlined"
                  :error-messages="errors.password"
                  density="comfortable"
                  prepend-inner-icon="mdi-lock"
                  :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
                  class="mb-2 login-field"
                  autocomplete="current-password"
                  @click:append-inner="showPassword = !showPassword"
                />
                <button
                  type="button"
                  class="login-card__show-pwd"
                  @click="showPassword = !showPassword"
                >
                  {{ showPassword ? 'Скрыть пароль' : 'Показать пароль' }}
                </button>
                <v-alert v-if="errorMessage" type="error" density="compact" class="mb-4" closable>
                  {{ errorMessage }}
                </v-alert>
                <v-btn
                  type="submit"
                  color="primary"
                  block
                  size="x-large"
                  class="vuvoz-transition login-btn"
                  :loading="loading"
                >
                  Войти
                </v-btn>
                <div class="login-card__home mt-3 text-center">
                  <RouterLink to="/" class="login-card__home-link">
                    <v-icon icon="mdi-home-outline" size="20" class="mr-1" />
                    На главную
                  </RouterLink>
                </div>
              </v-form>
            </v-card>
          </AppFadeIn>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import AppFadeIn from '@/components/AppFadeIn.vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const userStore = useUserStore()

const username = ref('')
const password = ref('')
const showPassword = ref(false)
const loading = ref(false)
const errorMessage = ref('')
const errors = reactive<{ username?: string; password?: string }>({})
const formRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null)

async function onSubmit() {
  errorMessage.value = ''
  errors.username = ''
  errors.password = ''
  if (!username.value.trim()) {
    errors.username = 'Username is required'
    return
  }
  if (!password.value) {
    errors.password = 'Password is required'
    return
  }
  loading.value = true
  try {
    await authStore.login(username.value, password.value)
    await userStore.fetchMe()
    const redirect = (route.query.redirect as string) || undefined
    if (userStore.role === 'admin') {
      router.push(redirect || { name: 'AdminDashboard' })
    } else if (userStore.role === 'company') {
      router.push(redirect || { name: 'CompanyDashboard' })
    } else if (userStore.role === 'institution') {
      router.push(redirect || { name: 'InstitutionDashboard' })
    } else {
      router.push(redirect || { name: 'Login' })
    }
  } catch (err: unknown) {
    const ax = err as { response?: { data?: { detail?: string }; status?: number } }
    if (ax.response?.status === 401) {
      errorMessage.value = 'Invalid username or password.'
    } else {
      errorMessage.value = ax.response?.data?.detail || 'Login failed. Please try again.'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
.login-page {
  background: var(--vuvoz-gradient-soft);
  min-height: 100vh;
}

.login-page__container {
  padding: 1rem;
}
@media (max-width: 600px) {
  .login-page__container {
    padding: 0.5rem 0.75rem;
  }
  .login-page__col {
    max-width: 100%;
    flex: 0 0 100%;
    padding-left: 0.25rem;
    padding-right: 0.25rem;
  }
}

.login-card {
  border-radius: var(--vuvoz-radius-lg);
  box-shadow: var(--vuvoz-shadow-xl);
  border: 1px solid var(--vuvoz-border);
  padding: 1.5rem;
}
@media (min-width: 600px) {
  .login-card {
    padding: 2rem;
  }
}
@media (max-width: 599px) {
  .login-card {
    padding: 1rem 1.25rem;
    width: 100%;
    box-sizing: border-box;
  }
}

.login-card__title {
  font-size: 1.35rem;
  font-weight: 700;
  text-align: center;
  margin-bottom: 0.5rem;
  word-wrap: break-word;
  line-height: 1.3;
}
@media (max-width: 599px) {
  .login-card__title {
    font-size: 1.15rem;
    line-height: 1.35;
  }
}

.login-card__subtitle {
  font-size: 0.95rem;
}

.login-card__show-pwd {
  display: block;
  width: 100%;
  margin-bottom: 1rem;
  padding: 0.5rem 0;
  border: none;
  background: none;
  font-size: 0.875rem;
  color: var(--vuvoz-primary);
  cursor: pointer;
  min-height: 44px;
  -webkit-tap-highlight-color: transparent;
}
@media (min-width: 600px) {
  .login-card__show-pwd {
    display: none;
  }
}

.login-card__home-link {
  display: inline-flex;
  align-items: center;
  font-size: 0.9rem;
  color: var(--vuvoz-text-muted);
  text-decoration: none;
  padding: 0.5rem 0.75rem;
  border-radius: var(--vuvoz-radius-sm);
  min-height: 44px;
  -webkit-tap-highlight-color: transparent;
  &:hover {
    color: var(--vuvoz-primary);
    background: rgba(13, 148, 136, 0.06);
  }
}

@media (max-width: 600px) {
  .login-field :deep(.v-field__input) {
    font-size: 16px !important;
    min-height: 48px;
  }
  .login-field :deep(.v-field) {
    --v-field-input-padding-top: 14px;
    --v-field-input-padding-bottom: 14px;
  }
  .login-btn {
    min-height: 48px !important;
  }
}
</style>
