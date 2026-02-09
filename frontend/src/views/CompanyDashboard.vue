<template>
  <div>
    <v-app-bar color="primary" density="compact">
      <v-app-bar-title>Компания по вывозу</v-app-bar-title>
      <v-spacer />
      <v-menu location="bottom">
        <template #activator="{ props: menuProps }">
          <v-btn v-bind="menuProps" variant="text" icon="mdi-bell">
            <v-badge
              v-if="unreadCount > 0"
              :content="unreadCount"
              color="error"
            />
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
        <!-- Company info -->
        <v-card class="mb-6" variant="tonal">
          <v-card-title>Информация о компании</v-card-title>
          <v-card-text v-if="userStore.companyProfile">
            <v-row>
              <v-col cols="12" md="6">
                <div class="text-subtitle-2 text-medium-emphasis">Название компании</div>
                <div>{{ userStore.companyProfile.company_name }}</div>
              </v-col>
              <v-col cols="12" md="6">
                <div class="text-subtitle-2 text-medium-emphasis">Почта</div>
                <div>{{ userStore.companyProfile.contact_email }}</div>
              </v-col>
              <v-col cols="12" md="6">
                <div class="text-subtitle-2 text-medium-emphasis">Номер телефона</div>
                <div>{{ userStore.companyProfile.contact_phone }}</div>
              </v-col>
              <v-col cols="12">
                <div class="text-subtitle-2 text-medium-emphasis">Адрес</div>
                <div>{{ userStore.companyProfile.address }}</div>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>

        <!-- Stats -->
        <v-row class="mb-6">
          <v-col cols="12" sm="4">
            <StatsCard
              title="Всего запросов"
              :value="stats.totalRequests"
              icon="mdi-file-document-multiple"
              color="primary"
            />
          </v-col>
          <v-col cols="12" sm="4">
            <StatsCard
              title="Выполненых запросов"
              :value="stats.completed"
              icon="mdi-check-circle"
              color="success"
            />
          </v-col>
          <v-col cols="12" sm="4">
            <StatsCard
              title="Вывезено (кг)"
              :value="stats.totalWeight"
              icon="mdi-weight-kilogram"
              color="info"
            />
          </v-col>
        </v-row>

        <!-- My Institutions -->
        <v-card class="mb-6">
          <v-card-title class="d-flex align-center">
            Мои организации
            <v-spacer />
            <v-btn color="primary" prepend-icon="mdi-plus" @click="showCreateModal = true">
              Добавить организацию
            </v-btn>
          </v-card-title>
          <v-divider />
          <v-data-table
            :headers="institutionHeaders"
            :items="institutions"
            :loading="loadingInstitutions"
            item-value="id"
          >
            <template #item.contacts="{ item }">
              <div class="text-body-2">
                <div>{{ item.contact_person }}</div>
                <div class="text-medium-emphasis">{{ item.phone }}</div>
                <div class="text-medium-emphasis">{{ item.email }}</div>
              </div>
            </template>
            <template #item.actions="{ item }">
              <v-btn size="small" variant="text" @click="editInstitution(item)">Изменить</v-btn>
              <v-btn size="small" variant="text" color="error" @click="confirmDelete(item)">
                Удалить
              </v-btn>
            </template>
          </v-data-table>
        </v-card>

        <!-- Incoming requests -->
        <RequestTable
          title="Запросы на вывоз"
          :requests="requests"
          :loading="loadingRequests"
          show-status-filter
          show-actions
          can-update-status
          @update-status="openStatusDialog"
        />
      </v-container>
    </v-main>

    <CreateInstitutionModal v-model="showCreateModal" @created="loadInstitutions" />
    <EditInstitutionModal
      v-model="showEditModal"
      :institution="selectedInstitution"
      @saved="onEditSaved"
    />

    <v-dialog v-model="statusDialog" max-width="500" persistent>
      <v-card v-if="selectedRequest">
        <v-card-title>Изменение статуса заявки</v-card-title>
        <v-card-text>
          <v-select
            v-model="statusUpdate"
            :items="statusItems"
            label="Статус"
            variant="outlined"
            class="mb-3"
          />
          <template v-if="statusUpdate !== 'completed'">
            <v-text-field
              v-model="statusUpdateEstimatedDate"
              label="Предполагаемая дата вывоза"
              type="date"
              variant="outlined"
              density="comfortable"
              class="mb-3"
            />
            <v-textarea
              v-model="statusUpdateNotes"
              label="Внутренние заметки (не видны организации)"
              variant="outlined"
              rows="2"
            />
          </template>
          <template v-else>
            <v-text-field
              v-model="completeActualAmount"
              label="Фактическое количество (кг) *"
              type="number"
              min="1"
              step="0.01"
              variant="outlined"
              density="comfortable"
              :error-messages="completeErrors.actual_amount"
              class="mb-3"
            />
            <v-text-field
              v-model="completeActualDate"
              label="Дата фактического вывоза"
              type="date"
              variant="outlined"
              density="comfortable"
              class="mb-3"
            />
            <v-textarea
              v-model="completeInternalNotes"
              label="Внутренние заметки"
              variant="outlined"
              rows="2"
            />
            <p v-if="completeActualValue != null" class="text-body-2 mt-2">
              Расчётная стоимость: <strong>{{ completeActualValue }} руб.</strong>
            </p>
          </template>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="statusDialog = false">Отмена</v-btn>
          <v-btn color="primary" :loading="updatingStatus" @click="saveStatus">Сохранить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="deleteDialog" max-width="400" persistent>
      <v-card>
        <v-card-title>Удалить организацию?</v-card-title>
        <v-card-text>
          Будет удалена организация «{{ institutionToDelete?.institution_name }}». Действие нельзя отменить.
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="deleteDialog = false">Отмена</v-btn>
          <v-btn color="error" :loading="deleting" @click="doDelete">Удалить</v-btn>
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
import RequestTable from '@/components/RequestTable.vue'
import CreateInstitutionModal from '@/components/CreateInstitutionModal.vue'
import EditInstitutionModal from '@/components/EditInstitutionModal.vue'
import type { CollectionRequest, InstitutionProfile } from '@/types'

const router = useRouter()
const authStore = useAuthStore()
const userStore = useUserStore()

const institutions = ref<InstitutionProfile[]>([])
const requests = ref<CollectionRequest[]>([])
const loadingInstitutions = ref(false)
const loadingRequests = ref(false)
const showCreateModal = ref(false)
const statusDialog = ref(false)
const selectedRequest = ref<CollectionRequest | null>(null)
const statusUpdate = ref('')
const statusUpdateEstimatedDate = ref('')
const statusUpdateNotes = ref('')
const completeActualAmount = ref('')
const completeActualDate = ref('')
const completeInternalNotes = ref('')
const completeErrors = reactive<{ actual_amount?: string }>({})
const updatingStatus = ref(false)
const completeActualValue = ref<string | null>(null)
const notifications = ref<{ id: number; title: string; message: string; read: boolean }[]>([])
const unreadCount = ref(0)
const deleteDialog = ref(false)
const institutionToDelete = ref<InstitutionProfile | null>(null)
const deleting = ref(false)
const showEditModal = ref(false)
const selectedInstitution = ref<InstitutionProfile | null>(null)

const institutionHeaders = [
  { title: 'Название учреждения', key: 'institution_name' },
  { title: 'Тип', key: 'institution_type' },
  { title: 'Контакты', key: 'contacts', sortable: false },
  { title: 'Адрес', key: 'address' },
  { title: 'Действия', key: 'actions', sortable: false, width: '160' },
]

const statusItems = [
  { title: 'Новый', value: 'new' },
  { title: 'Принятый', value: 'accepted' },
  { title: 'Завершеный', value: 'completed' },
]

const stats = computed(() => {
  const total = requests.value.length
  const completed = requests.value.filter((r) => r.status === 'completed').length
  const totalWeight = requests.value.reduce(
    (sum, r) => sum + parseFloat(String(r.estimated_amount || r.paper_weight_kg || 0)),
    0
  )
  return { totalRequests: total, completed, totalWeight: totalWeight.toFixed(1) }
})

async function loadInstitutions() {
  loadingInstitutions.value = true
  try {
    const { data } = await api.get<InstitutionProfile[]>('/institutions/')
    institutions.value = data
  } finally {
    loadingInstitutions.value = false
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

function editInstitution(item: InstitutionProfile) {
  selectedInstitution.value = item
  showEditModal.value = true
}

function onEditSaved() {
  loadInstitutions()
  selectedInstitution.value = null
}

function confirmDelete(item: InstitutionProfile) {
  institutionToDelete.value = item
  deleteDialog.value = true
}

async function doDelete() {
  if (!institutionToDelete.value) return
  deleting.value = true
  try {
    await api.delete(`/institutions/${institutionToDelete.value.id}/`)
    await loadInstitutions()
    await loadRequests()
    deleteDialog.value = false
    institutionToDelete.value = null
  } finally {
    deleting.value = false
  }
}

function openStatusDialog(request: CollectionRequest) {
  selectedRequest.value = request
  statusUpdate.value = request.status
  statusUpdateEstimatedDate.value = request.estimated_collection_date || ''
  statusUpdateNotes.value = request.notes || ''
  completeActualAmount.value = request.actual_amount ?? ''
  completeActualDate.value = request.actual_collection_date ?? ''
  completeInternalNotes.value = request.internal_notes ?? ''
  completeErrors.actual_amount = ''
  completeActualValue.value = request.actual_value ?? null
  statusDialog.value = true
}

watch([() => selectedRequest.value?.id, () => statusUpdate.value, completeActualAmount], async () => {
  if (statusUpdate.value !== 'completed' || !selectedRequest.value) {
    completeActualValue.value = null
    return
  }
  const amount = parseFloat(completeActualAmount.value)
  if (isNaN(amount) || amount <= 0) {
    completeActualValue.value = null
    return
  }
  try {
    const { data } = await api.post<{ estimated_value: string }>('/collection-requests/calculate/', {
      material_type: selectedRequest.value.material_type || 'paper',
      amount_kg: completeActualAmount.value,
    })
    completeActualValue.value = data.estimated_value
  } catch {
    completeActualValue.value = null
  }
})

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

async function saveStatus() {
  if (!selectedRequest.value) return
  if (statusUpdate.value === 'completed') {
    completeErrors.actual_amount = ''
    const amount = parseFloat(completeActualAmount.value)
    if (isNaN(amount) || amount < 1) {
      completeErrors.actual_amount = 'Укажите фактическое количество (мин. 1 кг).'
      return
    }
    updatingStatus.value = true
    try {
      await api.post(`/collection-requests/${selectedRequest.value.id}/complete/`, {
        actual_amount: completeActualAmount.value,
        actual_collection_date: completeActualDate.value || null,
        internal_notes: completeInternalNotes.value || '',
      })
      await loadRequests()
      statusDialog.value = false
      selectedRequest.value = null
    } catch (err: unknown) {
      const ax = err as { response?: { data?: Record<string, string | string[]> } }
      const d = ax.response?.data
      if (d?.actual_amount) {
        completeErrors.actual_amount = Array.isArray(d.actual_amount) ? d.actual_amount.join(' ') : String(d.actual_amount)
      }
    } finally {
      updatingStatus.value = false
    }
    return
  }
  updatingStatus.value = true
  try {
    const payload: Record<string, unknown> = { status: statusUpdate.value }
    if (statusUpdateEstimatedDate.value) payload.estimated_collection_date = statusUpdateEstimatedDate.value
    else payload.estimated_collection_date = null
    payload.notes = statusUpdateNotes.value || ''
    await api.patch(`/collection-requests/${selectedRequest.value.id}/`, payload)
    await loadRequests()
    statusDialog.value = false
    selectedRequest.value = null
  } finally {
    updatingStatus.value = false
  }
}

function logout() {
  authStore.logout()
  userStore.clearUser()
  router.push({ name: 'Login' })
}

onMounted(() => {
  loadInstitutions()
  loadRequests()
  loadNotifications()
})
</script>
