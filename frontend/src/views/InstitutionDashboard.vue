<template>
  <div>
    <v-app-bar color="primary" density="compact">
      <v-app-bar-title>Орагнизация</v-app-bar-title>
      <v-spacer />
      <span class="mr-2">{{ userStore.user?.username }}</span>
      <v-btn variant="text" icon="mdi-logout" @click="logout" />
    </v-app-bar>

    <v-main class="pa-4">
      <v-container fluid>
        <!-- Institution info -->
        <v-card class="mb-6" variant="tonal">
          <v-card-title>Institution information</v-card-title>
          <v-card-text v-if="userStore.institutionProfile">
            <v-row>
              <v-col cols="12" md="6">
                <div class="text-subtitle-2 text-medium-emphasis">Название организации</div>
                <div>{{ userStore.institutionProfile.institution_name }}</div>
              </v-col>
              <v-col cols="12" md="6">
                <div class="text-subtitle-2 text-medium-emphasis">Тип</div>
                <div>{{ userStore.institutionProfile.institution_type }}</div>
              </v-col>
              <v-col cols="12" md="6">
                <div class="text-subtitle-2 text-medium-emphasis">Контактное лицо</div>
                <div>{{ userStore.institutionProfile.contact_person }}</div>
              </v-col>
              <v-col cols="12" md="6">
                <div class="text-subtitle-2 text-medium-emphasis">Почта / Номер</div>
                <div>{{ userStore.institutionProfile.email }} / {{ userStore.institutionProfile.phone }}</div>
              </v-col>
              <v-col cols="12">
                <div class="text-subtitle-2 text-medium-emphasis">Адрес</div>
                <div>{{ userStore.institutionProfile.address }}</div>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>

        <!-- Stats -->
        <v-row class="mb-6">
          <v-col cols="12" sm="6">
            <StatsCard
              title="My total requests"
              :value="requests.length"
              icon="mdi-file-document-multiple"
              color="primary"
            />
          </v-col>
          <v-col cols="12" sm="6">
            <StatsCard
              title="Total weight (kg)"
              :value="totalWeight"
              icon="mdi-weight-kilogram"
              color="info"
            />
          </v-col>
        </v-row>

        <!-- New request form -->
        <v-card class="mb-6">
          <v-card-title>Новый запрос на вывоз</v-card-title>
          <v-divider />
          <v-card-text>
            <v-form @submit.prevent="submitRequest" ref="formRef">
              <v-row>
                <v-col cols="12" sm="4">
                  <v-text-field
                    v-model="form.paper_weight_kg"
                    label="Вес бумаги (кг)"
                    type="number"
                    min="0"
                    step="0.01"
                    variant="outlined"
                    density="comfortable"
                    :error-messages="errors.paper_weight_kg"
                  />
                </v-col>
                <v-col cols="12" sm="4">
                  <v-text-field
                    v-model="form.desired_date"
                    label="Дата вывоза"
                    type="date"
                    variant="outlined"
                    density="comfortable"
                  />
                </v-col>
                <v-col cols="12" sm="4" class="d-flex align-center">
                  <v-btn type="submit" color="primary" :loading="submitting">
                    Подтвердите заявку
                  </v-btn>
                </v-col>
              </v-row>
              <v-row>
                <v-col cols="12">
                  <v-textarea
                    v-model="form.comment"
                    label="Comment (optional)"
                    variant="outlined"
                    density="comfortable"
                    rows="2"
                  />
                </v-col>
              </v-row>
            </v-form>
          </v-card-text>
        </v-card>

        <!-- Request history -->
        <RequestTable
          title="My requests"
          :requests="requests"
          :loading="loadingRequests"
        />
      </v-container>
    </v-main>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/api/axios'
import { useAuthStore } from '@/stores/auth'
import { useUserStore } from '@/stores/user'
import StatsCard from '@/components/StatsCard.vue'
import RequestTable from '@/components/RequestTable.vue'
import type { CollectionRequest } from '@/types'

const router = useRouter()
const authStore = useAuthStore()
const userStore = useUserStore()

const requests = ref<CollectionRequest[]>([])
const loadingRequests = ref(false)
const submitting = ref(false)
const formRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null)

const form = reactive({
  paper_weight_kg: '' as string,
  desired_date: '' as string,
  comment: '',
})

const errors = reactive<{ paper_weight_kg?: string }>({})

const totalWeight = computed(() => {
  return requests.value
    .reduce((sum, r) => sum + parseFloat(String(r.paper_weight_kg)), 0)
    .toFixed(1)
})

async function loadRequests() {
  loadingRequests.value = true
  try {
    const { data } = await api.get<CollectionRequest[]>('/collection-requests/')
    requests.value = data
  } finally {
    loadingRequests.value = false
  }
}

async function submitRequest() {
  errors.paper_weight_kg = ''
  const weight = parseFloat(form.paper_weight_kg)
  if (isNaN(weight) || weight <= 0) {
    errors.paper_weight_kg = 'Enter a valid weight (kg).'
    return
  }
  submitting.value = true
  try {
    await api.post('/collection-requests/', {
      paper_weight_kg: form.paper_weight_kg,
      desired_date: form.desired_date || null,
      comment: form.comment || '',
    })
    form.paper_weight_kg = ''
    form.desired_date = ''
    form.comment = ''
    await loadRequests()
  } catch (err: unknown) {
    const ax = err as { response?: { data?: Record<string, string[]> } }
    const data = ax.response?.data
    if (data?.paper_weight_kg) {
      errors.paper_weight_kg = Array.isArray(data.paper_weight_kg)
        ? data.paper_weight_kg.join(' ')
        : String(data.paper_weight_kg)
    } else {
      errors.paper_weight_kg = 'Failed to submit request.'
    }
  } finally {
    submitting.value = false
  }
}

function logout() {
  authStore.logout()
  userStore.clearUser()
  router.push({ name: 'Login' })
}

onMounted(() => {
  loadRequests()
})
</script>
