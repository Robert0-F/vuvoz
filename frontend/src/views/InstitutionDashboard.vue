<template>
  <div>
    <v-app-bar color="primary" density="compact">
      <v-app-bar-title>Организация</v-app-bar-title>
      <v-spacer />
      <v-menu location="bottom">
        <template #activator="{ props: menuProps }">
          <v-btn v-bind="menuProps" variant="text" icon="mdi-bell">
            <v-badge v-if="unreadCount > 0" :content="unreadCount" color="error" />
          </v-btn>
        </template>
        <v-list max-height="320" style="overflow-y: auto">
          <v-list-item
            v-for="n in notifications"
            :key="n.id"
            :title="n.title"
            :subtitle="n.message"
            :class="{ 'bg-grey-lighten-3': !n.read }"
            @click="markNotificationRead(n.id)"
          />
          <v-list-item v-if="!notifications.length" title="Нет уведомлений" />
          <v-list-item v-if="notifications.length" title="Прочитать все" @click="markAllNotificationsRead" />
        </v-list>
      </v-menu>
      <span class="mr-2">{{ userStore.user?.username }}</span>
      <v-btn variant="text" icon="mdi-logout" @click="logout" />
    </v-app-bar>

    <v-main class="pa-4">
      <v-container fluid>
        <!-- Institution info -->
        <v-card class="mb-6" variant="tonal">
          <v-card-title>Информация об организации</v-card-title>
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
              title="Мои заявки"
              :value="requests.length"
              icon="mdi-file-document-multiple"
              color="primary"
            />
          </v-col>
          <v-col cols="12" sm="6">
            <StatsCard
              title="Всего вывезено (кг)"
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
              <div class="mb-4">
                <div class="text-subtitle-2 mb-2">Типы макулатуры и вес (кг) *</div>
                <v-alert v-if="errors.material_lines" type="error" density="compact" class="mb-2">
                  {{ errors.material_lines }}
                </v-alert>
                <div
                  v-for="(line, idx) in materialLines"
                  :key="idx"
                  class="d-flex align-center mb-2"
                  style="gap: 8px"
                >
                  <v-select
                    v-model="line.material_type"
                    :items="materialTypeItems"
                    label="Тип"
                    variant="outlined"
                    density="compact"
                    hide-details
                    style="min-width: 160px"
                  />
                  <v-text-field
                    v-model="line.amount_kg"
                    label="Вес (кг)"
                    type="number"
                    min="1"
                    max="10000"
                    step="0.01"
                    variant="outlined"
                    density="compact"
                    hide-details
                    style="max-width: 120px"
                  />
                  <v-btn
                    icon="mdi-delete"
                    variant="text"
                    color="error"
                    size="small"
                    :disabled="materialLines.length <= 1"
                    @click="removeMaterialLine(idx)"
                  />
                </div>
                <v-btn
                  variant="tonal"
                  size="small"
                  prepend-icon="mdi-plus"
                  class="mt-2"
                  @click="addMaterialLine"
                >
                  Добавить тип макулатуры
                </v-btn>
              </div>
              <v-row>
                <v-col cols="12" sm="4" class="d-flex align-center">
                  <span v-if="estimatedValuePreview != null" class="text-body-1">
                    Примерная стоимость: <strong>{{ estimatedValuePreview }} руб.</strong>
                  </span>
                </v-col>
                <v-col cols="12" sm="3">
                  <v-text-field
                    v-model="form.desired_date"
                    label="Желаемая дата вывоза"
                    type="date"
                    variant="outlined"
                    density="comfortable"
                  />
                </v-col>
                <v-col cols="12" sm="3" class="d-flex align-center">
                  <v-btn type="submit" color="primary" :loading="submitting">
                    Отправить запрос
                  </v-btn>
                </v-col>
              </v-row>
              <v-row>
                <v-col cols="12">
                  <v-textarea
                    v-model="form.comment"
                    label="Комментарий (необязательно)"
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
          title="Мои заявки"
          :requests="requests"
          :loading="loadingRequests"
          hide-urgency
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
import type { CollectionRequest, CurrentPrice } from '@/types'

const router = useRouter()
const authStore = useAuthStore()
const userStore = useUserStore()

const requests = ref<CollectionRequest[]>([])
const loadingRequests = ref(false)
const submitting = ref(false)
const notifications = ref<{ id: number; title: string; message: string; read: boolean }[]>([])
const unreadCount = ref(0)
const formRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null)
const currentPrices = ref<CurrentPrice[]>([])

const materialTypeItems = [
  { title: 'Бумага', value: 'paper' },
  { title: 'Картон', value: 'cardboard' },
  { title: 'Газеты', value: 'newspapers' },
  { title: 'Смешанная', value: 'mixed' },
  { title: 'Архивная', value: 'archive' },
]

const materialLines = ref<{ material_type: string; amount_kg: string }[]>([
  { material_type: 'paper', amount_kg: '' },
])

const form = reactive({
  desired_date: '' as string,
  comment: '',
})

const errors = reactive<{ material_lines?: string }>({})

function addMaterialLine() {
  materialLines.value.push({ material_type: 'paper', amount_kg: '' })
}

function removeMaterialLine(idx: number) {
  if (materialLines.value.length > 1) {
    materialLines.value.splice(idx, 1)
  }
}

const estimatedValuePreview = computed(() => {
  let total = 0
  for (const line of materialLines.value) {
    const amount = parseFloat(line.amount_kg)
    if (isNaN(amount) || amount <= 0) continue
    const priceRow = currentPrices.value.find((p) => p.material_type === line.material_type)
    if (!priceRow) return null
    const price = parseFloat(priceRow.price_per_kg)
    if (isNaN(price)) return null
    total += amount * price
  }
  return total > 0 ? total.toFixed(2) : null
})

const totalWeight = computed(() => {
  return requests.value
    .reduce((sum, r) => sum + parseFloat(String(r.estimated_amount || r.paper_weight_kg || 0)), 0)
    .toFixed(1)
})

async function loadCurrentPrices() {
  try {
    const { data } = await api.get<CurrentPrice[]>('/prices/current/')
    currentPrices.value = data
  } catch {
    currentPrices.value = []
  }
}

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
  errors.material_lines = ''
  const lines = materialLines.value
    .map((l) => ({ material_type: l.material_type, amount_kg: parseFloat(l.amount_kg) }))
    .filter((l) => !isNaN(l.amount_kg) && l.amount_kg >= 1)
  if (lines.length === 0) {
    errors.material_lines = 'Укажите минимум один тип макулатуры и вес от 1 кг.'
    return
  }
  const totalKg = lines.reduce((s, l) => s + l.amount_kg, 0)
  if (totalKg > 10000) {
    errors.material_lines = 'Суммарный вес не более 10000 кг.'
    return
  }
  submitting.value = true
  try {
    await api.post('/collection-requests/', {
      material_lines: lines.map((l) => ({ material_type: l.material_type, amount_kg: String(l.amount_kg) })),
      desired_date: form.desired_date || null,
      comment: form.comment || '',
    })
    materialLines.value = [{ material_type: 'paper', amount_kg: '' }]
    form.desired_date = ''
    form.comment = ''
    await loadRequests()
  } catch (err: unknown) {
    const ax = err as { response?: { data?: Record<string, string | string[]> } }
    const data = ax.response?.data
    const msg = data?.material_lines ?? data?.non_field_errors
    if (msg) {
      errors.material_lines = Array.isArray(msg) ? msg.join(' ') : String(msg)
    } else {
      errors.material_lines = 'Не удалось отправить запрос.'
    }
  } finally {
    submitting.value = false
  }
}

async function loadNotifications() {
  try {
    const { data } = await api.get<{ id: number; title: string; message: string; read: boolean }[]>('/notifications/')
    notifications.value = data
    unreadCount.value = data.filter((n) => !n.read).length
  } catch {
    // ignore
  }
}

async function markNotificationRead(id: number) {
  try {
    await api.post(`/notifications/${id}/mark_read/`)
    const n = notifications.value.find((x) => x.id === id)
    if (n) n.read = true
    unreadCount.value = Math.max(0, unreadCount.value - 1)
  } catch {
    // ignore
  }
}

async function markAllNotificationsRead() {
  try {
    await api.post('/notifications/mark_all_read/')
    notifications.value.forEach((n) => (n.read = true))
    unreadCount.value = 0
  } catch {
    // ignore
  }
}

function logout() {
  authStore.logout()
  userStore.clearUser()
  router.push({ name: 'Login' })
}

onMounted(() => {
  loadCurrentPrices()
  loadRequests()
  loadNotifications()
})
</script>
