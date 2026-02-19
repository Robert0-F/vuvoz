<template>
  <div class="login-page">
    <v-container fluid class="fill-height">
      <v-row align="center" justify="center">
        <v-col cols="12" sm="8" md="4">
          <AppFadeIn direction="up" :delay="0.05">
            <v-card class="login-card pa-6" elevation="0">
              <v-card-title class="text-h5 text-center mb-2 font-weight-bold">
                Компания по вывозу макулатуры
              </v-card-title>
              <v-card-subtitle class="text-center mb-4 text-medium-emphasis">
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
                  class="mb-2"
                />
                <v-text-field
                  v-model="password"
                  label="Пароль"
                  type="password"
                  variant="outlined"
                  :error-messages="errors.password"
                  density="comfortable"
                  prepend-inner-icon="mdi-lock"
                  class="mb-4"
                />
                <v-alert v-if="errorMessage" type="error" density="compact" class="mb-4" closable>
                  {{ errorMessage }}
                </v-alert>
                <v-btn
                  type="submit"
                  color="primary"
                  block
                  size="large"
                  class="vuvoz-transition"
                  :loading="loading"
                >
                  Войти
                </v-btn>
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
.login-card {
  border-radius: var(--vuvoz-radius-lg);
  box-shadow: var(--vuvoz-shadow-xl);
  border: 1px solid var(--vuvoz-border);
}
</style>
