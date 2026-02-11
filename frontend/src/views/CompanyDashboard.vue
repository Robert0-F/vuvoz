<template>
  <div>
    <v-app-bar color="primary" density="compact" class="px-4 py-2">
      <v-app-bar-title class="pl-2">Компания по вывозу</v-app-bar-title>
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
        <v-tabs v-model="companyTab" class="mb-4">
          <v-tab value="overview">Обзор</v-tab>
          <v-tab value="stats">Статистика</v-tab>
          <v-tab value="institutions">Организации</v-tab>
          <v-tab value="requests">Заявки</v-tab>
          <v-tab value="completed">Завершённые</v-tab>
        </v-tabs>

        <v-window v-model="companyTab">
          <!-- Overview -->
          <v-window-item value="overview">
            <v-card class="mb-4 rounded-lg" variant="tonal" elevation="1">
              <v-card-title>Информация о компании</v-card-title>
              <v-card-text v-if="userStore.companyProfile">
                <v-row>
                  <v-col cols="12" md="6">
                    <div class="text-subtitle-2 text-medium-emphasis">Название</div>
                    <div>{{ userStore.companyProfile.company_name }}</div>
                  </v-col>
                  <v-col cols="12" md="6">
                    <div class="text-subtitle-2 text-medium-emphasis">Почта</div>
                    <div>{{ userStore.companyProfile.contact_email }}</div>
                  </v-col>
                  <v-col cols="12" md="6">
                    <div class="text-subtitle-2 text-medium-emphasis">Телефон</div>
                    <div>{{ userStore.companyProfile.contact_phone }}</div>
                  </v-col>
                  <v-col cols="12">
                    <div class="text-subtitle-2 text-medium-emphasis">Адрес</div>
                    <div>{{ userStore.companyProfile.address }}</div>
                  </v-col>
                </v-row>
              </v-card-text>
            </v-card>
            <v-row class="mb-4">
              <v-col cols="12" sm="4">
                <StatsCard title="Всего заявок" :value="statsOverview.totalRequests" icon="mdi-file-document-multiple" color="primary" />
              </v-col>
              <v-col cols="12" sm="4">
                <StatsCard title="Завершено" :value="statsOverview.completed" icon="mdi-check-circle" color="success" />
              </v-col>
              <v-col cols="12" sm="4">
                <StatsCard title="Вывезено (кг)" :value="statsOverview.totalWeight" icon="mdi-weight-kilogram" color="info" />
              </v-col>
            </v-row>
            <v-card class="rounded-lg" elevation="1">
              <v-card-title class="d-flex align-center">
                Мои организации
                <v-spacer />
                <v-btn color="primary" prepend-icon="mdi-plus" @click="showCreateModal = true">Добавить</v-btn>
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
                  <v-btn size="small" variant="text" @click="openInstitutionCard(item)">Просмотр</v-btn>
                  <v-btn size="small" variant="text" @click="editInstitution(item)">Изменить</v-btn>
                  <v-btn size="small" variant="text" color="error" @click="confirmDelete(item)">Удалить</v-btn>
                </template>
              </v-data-table>
            </v-card>
          </v-window-item>

          <!-- Statistics -->
          <v-window-item value="stats">
            <v-card class="rounded-lg" elevation="1">
              <v-card-title class="d-flex align-center flex-wrap ga-2">
                Статистика по заявкам
                <v-select
                  v-model="statsPeriod"
                  :items="statsPeriodItems"
                  density="compact"
                  hide-details
                  label="Период"
                  variant="outlined"
                  style="max-width: 180px"
                />
                <v-text-field
                  v-if="statsPeriod === 'custom'"
                  v-model="statsStartDate"
                  type="date"
                  density="compact"
                  hide-details
                  label="С"
                  variant="outlined"
                  style="max-width: 150px"
                />
                <v-text-field
                  v-if="statsPeriod === 'custom'"
                  v-model="statsEndDate"
                  type="date"
                  density="compact"
                  hide-details
                  label="По"
                  variant="outlined"
                  style="max-width: 150px"
                />
                <v-btn color="primary" @click="loadStats">Обновить</v-btn>
              </v-card-title>
              <v-divider />
              <v-card-text>
                <v-row v-if="companyStats">
                  <v-col cols="12" sm="6" md="3">
                    <StatsCard title="Заявок за период" :value="companyStats.total_requests" icon="mdi-file-document-multiple" color="primary" />
                  </v-col>
                  <v-col cols="12" sm="6" md="3">
                    <StatsCard title="Завершено" :value="companyStats.requests_by_status?.completed ?? 0" icon="mdi-check-circle" color="success" />
                  </v-col>
                  <v-col cols="12" sm="6" md="3">
                    <StatsCard title="Вывезено (кг)" :value="String(companyStats.total_weight_kg ?? 0)" icon="mdi-weight-kilogram" color="info" />
                  </v-col>
                  <v-col cols="12" sm="6" md="3">
                    <StatsCard title="Организаций" :value="companyStats.total_institutions" icon="mdi-domain" color="secondary" />
                  </v-col>
                  <v-col v-if="companyStats.avg_processing_time_hours != null" cols="12" md="6">
                    <v-card variant="tonal" class="pa-3">
                      <div class="text-caption text-medium-emphasis">Среднее время обработки (заявка → завершение)</div>
                      <div class="text-h6">{{ companyStats.avg_processing_time_hours.toFixed(1) }} ч</div>
                    </v-card>
                  </v-col>
                  <v-col v-if="companyStats.monthly_comparison" cols="12" md="6">
                    <v-card variant="tonal" class="pa-3">
                      <div class="text-caption text-medium-emphasis">Текущий / прошлый месяц (заявки)</div>
                      <div class="text-body-2">{{ companyStats.monthly_comparison.current_month_requests }} / {{ companyStats.monthly_comparison.previous_month_requests }}</div>
                      <div class="text-caption mt-1">Вывезено (кг): {{ companyStats.monthly_comparison.current_month_weight_kg }} / {{ companyStats.monthly_comparison.previous_month_weight_kg }}</div>
                    </v-card>
                  </v-col>
                </v-row>
                <p v-else class="text-medium-emphasis">Выберите период и нажмите «Обновить».</p>
              </v-card-text>
            </v-card>
          </v-window-item>

          <!-- Institutions -->
          <v-window-item value="institutions">
            <v-card class="rounded-lg" elevation="1">
              <v-card-title class="d-flex align-center">
                Организации
                <v-spacer />
                <v-btn color="primary" prepend-icon="mdi-plus" @click="showCreateModal = true">Добавить</v-btn>
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
                    <div class="text-medium-emphasis">{{ item.phone }} / {{ item.email }}</div>
                  </div>
                </template>
                <template #item.actions="{ item }">
                  <v-btn size="small" variant="text" @click="openInstitutionCard(item)">Просмотр</v-btn>
                  <v-btn size="small" variant="text" @click="editInstitution(item)">Изменить</v-btn>
                  <v-btn size="small" variant="text" color="error" @click="confirmDelete(item)">Удалить</v-btn>
                </template>
              </v-data-table>
            </v-card>
          </v-window-item>

          <!-- Active requests (new + accepted) -->
          <v-window-item value="requests">
            <v-card class="rounded-lg" elevation="1">
              <v-card-title>Текущие заявки</v-card-title>
              <v-divider />
              <v-data-table
                :headers="activeRequestHeaders"
                :items="activeRequests"
                :loading="loadingRequests"
                item-value="id"
              >
                <template #item.request_number="{ item }">{{ item.request_number || item.id }}</template>
                <template #item.material_display="{ item }">{{ formatMaterialLines(item) }}</template>
                <template #item.estimated_value="{ item }">{{ item.estimated_value != null ? `${item.estimated_value} руб.` : '—' }}</template>
                <template #item.desired_date="{ item }">{{ item.desired_date ? formatDate(item.desired_date) : '—' }}</template>
                <template #item.status="{ item }">
                  <v-chip :color="statusColor(item.status)" size="small">{{ statusLabel(item.status) }}</v-chip>
                </template>
                <template #item.created_at="{ item }">{{ formatDate(item.created_at) }}</template>
                <template #item.actions="{ item }">
                  <v-btn size="small" variant="text" @click="openRequestCard(item)">Просмотр</v-btn>
                  <v-btn size="small" variant="text" color="primary" @click="openStatusDialog(item)">Изменить статус</v-btn>
                </template>
              </v-data-table>
            </v-card>
          </v-window-item>

          <!-- Completed requests -->
          <v-window-item value="completed">
            <v-card class="rounded-lg" elevation="1">
              <v-card-title>Завершённые заявки</v-card-title>
              <v-divider />
              <v-data-table
                :headers="completedRequestHeaders"
                :items="completedRequests"
                :loading="loadingRequests"
                item-value="id"
              >
                <template #item.request_number="{ item }">{{ item.request_number || item.id }}</template>
                <template #item.material_display="{ item }">{{ formatMaterialLines(item) }}</template>
                <template #item.actual_amount="{ item }">{{ item.actual_amount ?? '—' }}</template>
                <template #item.actual_collection_date="{ item }">{{ item.actual_collection_date ? formatDate(item.actual_collection_date) : '—' }}</template>
                <template #item.actual_value="{ item }">{{ item.actual_value != null ? `${item.actual_value} руб.` : '—' }}</template>
                <template #item.created_at="{ item }">{{ formatDate(item.created_at) }}</template>
                <template #item.actions="{ item }">
                  <v-btn size="small" variant="text" @click="openRequestCard(item)">Просмотр</v-btn>
                </template>
              </v-data-table>
            </v-card>
          </v-window-item>
        </v-window>
      </v-container>
    </v-main>

    <CreateInstitutionModal v-model="showCreateModal" @created="loadInstitutions" />
    <EditInstitutionModal
      v-model="showEditModal"
      :institution="selectedInstitution"
      company-edit-only
      @saved="onEditSaved"
    />

    <!-- Institution card (full info) -->
    <v-dialog v-model="institutionCardDialog" max-width="640" persistent>
      <v-card v-if="institutionCard">
        <v-card-title class="d-flex align-center">
          {{ institutionCard.institution_name }}
          <v-spacer />
          <v-btn icon variant="text" @click="institutionCardDialog = false">×</v-btn>
        </v-card-title>
        <v-divider />
        <v-card-text class="text-body-2">
          <p><strong>Тип:</strong> {{ institutionCard.institution_type }}</p>
          <p><strong>Почта / Логин:</strong> {{ institutionCard.email }}</p>
          <p><strong>Контактное лицо:</strong> {{ institutionCard.contact_person }}</p>
          <p><strong>Телефон:</strong> {{ institutionCard.phone }}</p>
          <p><strong>Адрес:</strong> {{ institutionCard.address || '—' }}</p>
          <p><strong>Юр. адрес:</strong> {{ institutionCard.legal_address || '—' }}</p>
          <p><strong>ИНН / КПП:</strong> {{ institutionCard.inn || '—' }} / {{ institutionCard.kpp || '—' }}</p>
          <p><strong>Контакт на площадке:</strong> {{ institutionCard.contact_person_on_site || '—' }}</p>
          <p><strong>Телефон на площадке:</strong> {{ institutionCard.phone_on_site || '—' }}</p>
          <p><strong>Предпочтительные дни/часы:</strong> {{ institutionCard.preferred_days || '—' }} / {{ institutionCard.preferred_hours || '—' }}</p>
          <p v-if="institutionCard.access_details"><strong>Детали доступа:</strong><br />{{ institutionCard.access_details }}</p>
          <p v-if="institutionCard.container_location"><strong>Расположение контейнера:</strong><br />{{ institutionCard.container_location }}</p>
          <p v-if="institutionCard.company_notes"><strong>Заметка компании:</strong><br />{{ institutionCard.company_notes }}</p>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn color="primary" @click="institutionCardDialog = false; editInstitution(institutionCard)">Изменить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Request card (full info) -->
    <v-dialog v-model="requestCardDialog" max-width="640" persistent>
      <v-card v-if="requestCard">
        <v-card-title class="d-flex align-center">
          Заявка {{ requestCard.request_number || requestCard.id }}
          <v-spacer />
          <v-btn icon variant="text" @click="requestCardDialog = false">×</v-btn>
        </v-card-title>
        <v-divider />
        <v-card-text class="text-body-2">
          <p><strong>Организация:</strong> {{ requestCard.institution_name }}</p>
          <p><strong>Статус:</strong> {{ statusLabel(requestCard.status) }}</p>
          <p><strong>Типы макулатуры:</strong> {{ formatMaterialLines(requestCard) }}</p>
          <p><strong>Ориент. вес (кг):</strong> {{ requestCard.estimated_amount ?? requestCard.paper_weight_kg ?? '—' }}</p>
          <p><strong>Факт. вес (кг):</strong> {{ requestCard.actual_amount ?? '—' }}</p>
          <p><strong>Ориент. стоимость:</strong> {{ requestCard.estimated_value != null ? `${requestCard.estimated_value} руб.` : '—' }}</p>
          <p><strong>Факт. стоимость:</strong> {{ requestCard.actual_value != null ? `${requestCard.actual_value} руб.` : '—' }}</p>
          <p><strong>Желаемая дата:</strong> {{ requestCard.desired_date ? formatDate(requestCard.desired_date) : '—' }}</p>
          <p><strong>Предполаг. дата вывоза:</strong> {{ requestCard.estimated_collection_date ? formatDate(requestCard.estimated_collection_date) : '—' }}</p>
          <p><strong>Факт. дата вывоза:</strong> {{ requestCard.actual_collection_date ? formatDate(requestCard.actual_collection_date) : '—' }}</p>
          <p><strong>Комментарий:</strong> {{ requestCard.comment || '—' }}</p>
          <p><strong>Дата создания:</strong> {{ requestCard.created_at }}</p>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn v-if="requestCard.status !== 'completed'" color="primary" @click="requestCardDialog = false; openStatusDialog(requestCard)">Изменить статус</v-btn>
          <v-btn @click="requestCardDialog = false">Закрыть</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="statusDialog" max-width="500" persistent>
      <v-card v-if="selectedRequest">
        <v-card-title>Изменение статуса заявки</v-card-title>
        <v-card-text>
          <v-select v-model="statusUpdate" :items="statusItems" label="Статус" variant="outlined" class="mb-3" />
          <template v-if="statusUpdate !== 'completed'">
            <v-text-field v-model="statusUpdateEstimatedDate" label="Предполагаемая дата вывоза" type="date" variant="outlined" density="comfortable" class="mb-3" />
            <v-textarea v-model="statusUpdateNotes" label="Внутренние заметки (не видны организации)" variant="outlined" rows="2" />
          </template>
          <template v-else>
            <v-text-field v-model="completeActualAmount" label="Фактическое количество (кг) *" type="number" min="1" step="0.01" variant="outlined" density="comfortable" :error-messages="completeErrors.actual_amount" class="mb-3" />
            <v-text-field v-model="completeActualDate" label="Дата фактического вывоза" type="date" variant="outlined" density="comfortable" class="mb-3" />
            <v-textarea v-model="completeInternalNotes" label="Внутренние заметки" variant="outlined" rows="2" />
            <p v-if="completeActualValue != null" class="text-body-2 mt-2">Расчётная стоимость: <strong>{{ completeActualValue }} руб.</strong></p>
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
        <v-card-text>Будет удалена организация «{{ institutionToDelete?.institution_name }}». Действие нельзя отменить.</v-card-text>
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
import CreateInstitutionModal from '@/components/CreateInstitutionModal.vue'
import EditInstitutionModal from '@/components/EditInstitutionModal.vue'
import type { CollectionRequest, InstitutionProfile } from '@/types'

const router = useRouter()
const authStore = useAuthStore()
const userStore = useUserStore()

const companyTab = ref('overview')
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
const institutionCardDialog = ref(false)
const institutionCard = ref<InstitutionProfile | null>(null)
const requestCardDialog = ref(false)
const requestCard = ref<CollectionRequest | null>(null)

const statsPeriod = ref('month')
const statsPeriodItems = [
  { title: 'День (сегодня)', value: 'day' },
  { title: 'Неделя', value: 'week' },
  { title: 'Месяц', value: 'month' },
  { title: 'Произвольный период', value: 'custom' },
]
const statsStartDate = ref('')
const statsEndDate = ref('')
const companyStats = ref<{
  total_requests?: number
  total_weight_kg?: number
  total_institutions?: number
  requests_by_status?: { new?: number; accepted?: number; completed?: number }
  avg_processing_time_hours?: number
  monthly_comparison?: { current_month_requests?: number; previous_month_requests?: number; current_month_weight_kg?: number; previous_month_weight_kg?: number }
} | null>(null)

const institutionHeaders = [
  { title: 'Название', key: 'institution_name' },
  { title: 'Тип', key: 'institution_type' },
  { title: 'Контакты', key: 'contacts', sortable: false },
  { title: 'Адрес', key: 'address' },
  { title: 'Действия', key: 'actions', sortable: false, width: '220' },
]

const activeRequestHeaders = [
  { title: 'Номер', key: 'request_number', width: '130' },
  { title: 'Организация', key: 'institution_name' },
  { title: 'Типы макулатуры', key: 'material_display', sortable: false },
  { title: 'Вес (кг)', key: 'estimated_amount' },
  { title: 'Ориент. стоимость', key: 'estimated_value', width: '130' },
  { title: 'Желаемая дата', key: 'desired_date' },
  { title: 'Статус', key: 'status' },
  { title: 'Создана', key: 'created_at' },
  { title: 'Действия', key: 'actions', sortable: false, width: '220' },
]

const completedRequestHeaders = [
  { title: 'Номер', key: 'request_number', width: '130' },
  { title: 'Организация', key: 'institution_name' },
  { title: 'Типы макулатуры', key: 'material_display', sortable: false },
  { title: 'Факт. вес (кг)', key: 'actual_amount' },
  { title: 'Дата вывоза', key: 'actual_collection_date' },
  { title: 'Факт. стоимость', key: 'actual_value', width: '130' },
  { title: 'Создана', key: 'created_at' },
  { title: 'Действия', key: 'actions', sortable: false, width: '100' },
]

const statusItems = [
  { title: 'Новый', value: 'new' },
  { title: 'Принятый', value: 'accepted' },
  { title: 'Завершённый', value: 'completed' },
]

const activeRequests = computed(() => requests.value.filter((r) => r.status !== 'completed'))
const completedRequests = computed(() => requests.value.filter((r) => r.status === 'completed'))

const statsOverview = computed(() => {
  const total = requests.value.length
  const completed = requests.value.filter((r) => r.status === 'completed').length
  const totalWeight = requests.value
    .filter((r) => r.status === 'completed')
    .reduce((sum, r) => sum + parseFloat(String(r.actual_amount || r.estimated_amount || r.paper_weight_kg || 0)), 0)
  return { totalRequests: total, completed, totalWeight: totalWeight.toFixed(1) }
})

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

function getStatsDateRange(): { start_date: string; end_date: string } {
  const now = new Date()
  const today = now.toISOString().slice(0, 10)
  if (statsPeriod.value === 'day') {
    return { start_date: today, end_date: today }
  }
  if (statsPeriod.value === 'week') {
    const d = new Date(now)
    d.setDate(d.getDate() - 7)
    return { start_date: d.toISOString().slice(0, 10), end_date: today }
  }
  if (statsPeriod.value === 'month') {
    const d = new Date(now)
    d.setMonth(d.getMonth() - 1)
    return { start_date: d.toISOString().slice(0, 10), end_date: today }
  }
  return { start_date: statsStartDate.value || today, end_date: statsEndDate.value || today }
}

async function loadStats() {
  const { start_date, end_date } = getStatsDateRange()
  try {
    const { data } = await api.get('/stats/company/', { params: { start_date, end_date } })
    companyStats.value = data
  } catch {
    companyStats.value = null
  }
}

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

function openInstitutionCard(item: InstitutionProfile) {
  institutionCard.value = item
  institutionCardDialog.value = true
}

function openRequestCard(item: CollectionRequest) {
  requestCard.value = item
  requestCardDialog.value = true
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

watch(companyTab, (tab) => {
  if (tab === 'stats') loadStats()
  if (tab === 'institutions') loadInstitutions()
  if (tab === 'requests' || tab === 'completed') loadRequests()
})

onMounted(() => {
  loadInstitutions()
  loadRequests()
  loadNotifications()
})
</script>
