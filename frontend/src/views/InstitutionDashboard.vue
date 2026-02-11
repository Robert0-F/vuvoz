<template>
  <div>
    <v-app-bar color="primary" density="compact" class="px-4 py-2">
      <v-app-bar-title class="pl-2">Организация</v-app-bar-title>
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

    <v-main class="pa-50">
      <v-container fluid class="pa-0 pa-sm-4">
        <!-- Institution info -->
        <v-card class="mb-6 rounded-lg" variant="tonal" elevation="1">
          <v-card-title class="d-flex align-center">
            Информация об организации
            <v-spacer />
            <v-btn variant="tonal" size="small" @click="showEditProfile = true">
              Изменить контактные данные
            </v-btn>
          </v-card-title>
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
                <div class="text-subtitle-2 text-medium-emphasis">Почта / Телефон</div>
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
            <StatsCard title="Мои заявки" :value="requests.length" icon="mdi-file-document-multiple" color="primary" />
          </v-col>
          <v-col cols="12" sm="6">
            <StatsCard title="Всего вывезено (кг)" :value="totalWeight" icon="mdi-weight-kilogram" color="info" />
          </v-col>
        </v-row>

        <!-- New request form -->
        <v-card class="mb-6 rounded-lg" elevation="1">
          <v-card-title>Новый запрос на вывоз</v-card-title>
          <v-divider />
          <v-card-text>
            <v-form @submit.prevent="submitRequest" ref="formRef">
              <div class="mb-4">
                <div class="text-subtitle-2 mb-2">Типы макулатуры и вес (кг) *</div>
                <p v-if="weightLimits" class="text-caption text-medium-emphasis mb-2">
                  Суммарный вес: от {{ weightLimits.min_kg }} до {{ weightLimits.max_kg }} кг
                </p>
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
                    :max="weightLimits ? weightLimits.max_kg : 100000"
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
                <v-btn variant="tonal" size="small" prepend-icon="mdi-plus" class="mt-2" @click="addMaterialLine">
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
                  <v-text-field v-model="form.desired_date" label="Желаемая дата вывоза" type="date" variant="outlined" density="comfortable" />
                </v-col>
                <v-col cols="12" sm="3" class="d-flex align-center">
                  <v-btn type="submit" color="primary" :loading="submitting">Отправить запрос</v-btn>
                </v-col>
              </v-row>
              <v-row>
                <v-col cols="12">
                  <v-textarea v-model="form.comment" label="Комментарий (необязательно)" variant="outlined" density="comfortable" rows="2" />
                </v-col>
              </v-row>
            </v-form>
          </v-card-text>
        </v-card>

        <!-- Request tabs -->
        <v-tabs v-model="requestTab" class="mb-2">
          <v-tab value="active">Текущие заявки</v-tab>
          <v-tab value="completed">Завершённые заявки</v-tab>
        </v-tabs>
        <v-window v-model="requestTab">
          <v-window-item value="active">
            <v-card class="rounded-lg" elevation="1">
              <v-card-title>Текущие заявки</v-card-title>
              <v-divider />
              <v-data-table
                :headers="activeRequestHeaders"
                :items="activeRequests"
                :loading="loadingRequests"
                item-value="id"
                class="elevation-0"
              >
                <template #item.request_number="{ item }">{{ item.request_number || item.id }}</template>
                <template #item.institution_name>{{ userStore.institutionProfile?.institution_name ?? '—' }}</template>
                <template #item.phone>{{ userStore.institutionProfile?.phone ?? '—' }}</template>
                <template #item.info>{{ userStore.institutionProfile ? [userStore.institutionProfile.address, userStore.institutionProfile.contact_person].filter(Boolean).join(' · ') : '—' }}</template>
                <template #item.material_display="{ item }">{{ formatMaterialLines(item) }}</template>
                <template #item.estimated_value="{ item }">{{ item.estimated_value != null ? `${item.estimated_value} руб.` : '—' }}</template>
                <template #item.actual_value="{ item }">{{ item.actual_value != null ? `${item.actual_value} руб.` : '—' }}</template>
                <template #item.desired_date="{ item }">{{ item.desired_date ? formatDate(item.desired_date) : '—' }}</template>
                <template #item.status="{ item }">
                  <v-chip :color="statusColor(item.status)" size="small">{{ statusLabel(item.status) }}</v-chip>
                </template>
                <template #item.created_at="{ item }">{{ formatDate(item.created_at) }}</template>
              </v-data-table>
            </v-card>
          </v-window-item>
          <v-window-item value="completed">
            <v-card class="rounded-lg" elevation="1">
              <v-card-title>Завершённые заявки</v-card-title>
              <v-divider />
              <v-data-table
                :headers="completedRequestHeaders"
                :items="completedRequests"
                :loading="loadingRequests"
                item-value="id"
                class="elevation-0"
              >
                <template #item.request_number="{ item }">{{ item.request_number || item.id }}</template>
                <template #item.institution_name>{{ userStore.institutionProfile?.institution_name ?? '—' }}</template>
                <template #item.phone>{{ userStore.institutionProfile?.phone ?? '—' }}</template>
                <template #item.info>{{ userStore.institutionProfile ? [userStore.institutionProfile.address, userStore.institutionProfile.contact_person].filter(Boolean).join(' · ') : '—' }}</template>
                <template #item.material_display="{ item }">{{ formatMaterialLines(item) }}</template>
                <template #item.actual_amount="{ item }">{{ item.actual_amount ?? '—' }}</template>
                <template #item.actual_value="{ item }">{{ item.actual_value != null ? `${item.actual_value} руб.` : '—' }}</template>
                <template #item.created_at="{ item }">{{ formatDate(item.created_at) }}</template>
              </v-data-table>
            </v-card>
          </v-window-item>
        </v-window>
      </v-container>
    </v-main>

    <!-- Edit profile (phone, contact person) -->
    <v-dialog v-model="showEditProfile" max-width="480" persistent>
      <v-card>
        <v-card-title>Изменить контактные данные</v-card-title>
        <v-card-text>
          <v-text-field
            v-model="profileEdit.contact_person"
            label="Контактное лицо *"
            variant="outlined"
            class="mb-2"
            :error-messages="profileEditErrors.contact_person"
          />
          <v-text-field
            v-model="profileEdit.phone"
            label="Телефон *"
            variant="outlined"
            hint="Формат: 7 XXX XXX XX XX или +7 XXX XXX XX XX"
            persistent-hint
            :error-messages="profileEditErrors.phone"
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="showEditProfile = false">Отмена</v-btn>
          <v-btn color="primary" :loading="savingProfile" @click="saveProfile">Сохранить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/api/axios'
import { useAuthStore } from '@/stores/auth'
import { useUserStore } from '@/stores/user'
import StatsCard from '@/components/StatsCard.vue'
import type { CollectionRequest, CurrentPrice, InstitutionProfile } from '@/types'

const router = useRouter()
const authStore = useAuthStore()
const userStore = useUserStore()

const requestTab = ref('active')
const requests = ref<CollectionRequest[]>([])
const loadingRequests = ref(false)
const submitting = ref(false)
const notifications = ref<{ id: number; title: string; message: string; read: boolean }[]>([])
const unreadCount = ref(0)
const formRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null)
const currentPrices = ref<CurrentPrice[]>([])
const weightLimits = ref<{ min_kg: string; max_kg: string } | null>(null)
const showEditProfile = ref(false)
const profileEdit = reactive({ contact_person: '', phone: '' })
const profileEditErrors = reactive<Record<string, string>>({})
const savingProfile = ref(false)

const materialTypeItems = [
  { title: 'Бумага', value: 'paper' },
  { title: 'Картон', value: 'cardboard' },
  { title: 'Газеты', value: 'newspapers' },
  { title: 'Смешанная', value: 'mixed' },
  { title: 'Архивная', value: 'archive' },
]

const materialLines = ref<{ material_type: string; amount_kg: string }[]>([{ material_type: 'paper', amount_kg: '' }])

const form = reactive({
  desired_date: '' as string,
  comment: '',
})

const errors = reactive<{ material_lines?: string }>({})

const activeRequests = computed(() => requests.value.filter((r) => r.status !== 'completed'))
const completedRequests = computed(() => requests.value.filter((r) => r.status === 'completed'))

const activeRequestHeaders = [
  { title: 'Номер', key: 'request_number', width: '120' },
  { title: 'Организация', key: 'institution_name' },
  { title: 'Телефон', key: 'phone' },
  { title: 'Информация', key: 'info', sortable: false },
  { title: 'Типы макулатуры', key: 'material_display', sortable: false },
  { title: 'Вес (кг)', key: 'estimated_amount' },
  { title: 'Ориент. стоимость', key: 'estimated_value', width: '120' },
  { title: 'Факт. стоимость', key: 'actual_value', width: '120' },
  { title: 'Желаемая дата', key: 'desired_date' },
  { title: 'Статус', key: 'status' },
  { title: 'Дата создания', key: 'created_at' },
]

const completedRequestHeaders = [
  { title: 'Номер', key: 'request_number', width: '120' },
  { title: 'Организация', key: 'institution_name' },
  { title: 'Телефон', key: 'phone' },
  { title: 'Информация', key: 'info', sortable: false },
  { title: 'Типы макулатуры', key: 'material_display', sortable: false },
  { title: 'Факт. вес (кг)', key: 'actual_amount' },
  { title: 'Факт. стоимость', key: 'actual_value', width: '120' },
  { title: 'Дата создания', key: 'created_at' },
]

const materialTypeLabels: Record<string, string> = {
  paper: 'Бумага',
  cardboard: 'Картон',
  newspapers: 'Газеты',
  mixed: 'Смешанная',
  archive: 'Архивная',
}

function formatMaterialLines(item: CollectionRequest): string {
  const lines = item.material_lines
  if (lines && Array.isArray(lines) && lines.length > 0) {
    return lines.map((l) => `${materialTypeLabels[l.material_type] || l.material_type} ${l.amount_kg} кг`).join(', ')
  }
  const mt = item.material_type_display || item.material_type
  const amt = item.estimated_amount ?? item.paper_weight_kg
  return mt && amt != null ? `${mt} ${amt} кг` : '—'
}

function formatDate(s: string) {
  if (!s) return '—'
  return new Date(s).toLocaleDateString('ru-RU')
}

function statusLabel(s: string) {
  const m: Record<string, string> = { new: 'Новый', accepted: 'Принят', completed: 'Завершён' }
  return m[s] || s
}

function statusColor(s: string) {
  const m: Record<string, string> = { new: 'warning', accepted: 'info', completed: 'success' }
  return m[s] || 'default'
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
    .filter((r) => r.status === 'completed')
    .reduce((sum, r) => sum + parseFloat(String(r.actual_amount || r.estimated_amount || r.paper_weight_kg || 0)), 0)
    .toFixed(1)
})

function addMaterialLine() {
  materialLines.value.push({ material_type: 'paper', amount_kg: '' })
}

function removeMaterialLine(idx: number) {
  if (materialLines.value.length > 1) materialLines.value.splice(idx, 1)
}

async function loadWeightLimits() {
  try {
    const { data } = await api.get<{ min_kg: string; max_kg: string }>('/weight-limits/')
    weightLimits.value = data
  } catch {
    weightLimits.value = { min_kg: '100', max_kg: '100000' }
  }
}

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
  const minKg = weightLimits.value ? parseFloat(weightLimits.value.min_kg) : 100
  const maxKg = weightLimits.value ? parseFloat(weightLimits.value.max_kg) : 100000
  if (totalKg < minKg) {
    errors.material_lines = `Суммарный вес не менее ${minKg} кг.`
    return
  }
  if (totalKg > maxKg) {
    errors.material_lines = `Суммарный вес не более ${maxKg} кг.`
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

watch(showEditProfile, (open) => {
  if (open && userStore.institutionProfile) {
    profileEdit.contact_person = userStore.institutionProfile.contact_person ?? ''
    profileEdit.phone = userStore.institutionProfile.phone ?? ''
    profileEditErrors.contact_person = ''
    profileEditErrors.phone = ''
  }
})

async function saveProfile() {
  const profile = userStore.institutionProfile as (InstitutionProfile & { id: number }) | null
  if (!profile?.id) return
  profileEditErrors.contact_person = ''
  profileEditErrors.phone = ''
  if (!profileEdit.contact_person?.trim()) {
    profileEditErrors.contact_person = 'Обязательное поле'
    return
  }
  if (!profileEdit.phone?.trim()) {
    profileEditErrors.phone = 'Обязательное поле'
    return
  }
  savingProfile.value = true
  try {
    await api.patch(`/institutions/${profile.id}/`, {
      contact_person: profileEdit.contact_person.trim(),
      phone: profileEdit.phone.trim(),
    })
    await userStore.fetchMe()
    showEditProfile.value = false
  } catch (err: unknown) {
    const ax = err as { response?: { data?: Record<string, string[]> } }
    const d = ax.response?.data
    if (d) {
      if (d.contact_person) profileEditErrors.contact_person = Array.isArray(d.contact_person) ? d.contact_person.join(' ') : d.contact_person
      if (d.phone) profileEditErrors.phone = Array.isArray(d.phone) ? d.phone.join(' ') : d.phone
    }
  } finally {
    savingProfile.value = false
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
  loadWeightLimits()
  loadCurrentPrices()
  loadRequests()
  loadNotifications()
})
</script>
