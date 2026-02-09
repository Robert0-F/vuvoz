<template>
  <div>
    <v-app-bar color="primary" density="compact">
      <v-app-bar-title>Панель администратора</v-app-bar-title>
      <v-spacer />
      <span class="mr-2">{{ userStore.user?.username }}</span>
      <v-btn variant="text" icon="mdi-logout" @click="logout" />
    </v-app-bar>

    <v-main class="pa-4">
      <v-container fluid>
        <v-tabs v-model="activeTab" class="mb-4">
          <v-tab value="prices">Цены на макулатуру</v-tab>
          <v-tab value="news">Новости</v-tab>
          <v-tab value="companies">Компании</v-tab>
          <v-tab value="institutions">Организации</v-tab>
          <v-tab value="requests">Заявки</v-tab>
        </v-tabs>

        <v-window v-model="activeTab">
          <!-- Prices -->
          <v-window-item value="prices">
            <v-card>
              <v-card-title class="d-flex align-center">
                Справочник цен (руб/кг)
                <v-spacer />
                <v-btn color="primary" prepend-icon="mdi-plus" @click="openPriceDialog()">
                  Добавить цену
                </v-btn>
              </v-card-title>
              <v-divider />
              <v-data-table
                :headers="priceHeaders"
                :items="prices"
                :loading="loadingPrices"
                item-value="id"
              >
                <template #item.material_type_display="{ item }">
                  {{ item.material_type_display || item.material_type }}
                </template>
                <template #item.price_per_kg="{ item }">
                  {{ item.price_per_kg }} руб/кг
                </template>
                <template #item.valid_to="{ item }">
                  {{ item.valid_to || '—' }}
                </template>
                <template #item.is_active="{ item }">
                  <v-chip :color="item.is_active ? 'success' : 'default'" size="small">
                    {{ item.is_active ? 'Да' : 'Нет' }}
                  </v-chip>
                </template>
                <template #item.actions="{ item }">
                  <v-btn size="small" variant="text" @click="openPriceDialog(item)">Изменить</v-btn>
                  <v-btn size="small" variant="text" color="error" @click="confirmDeletePrice(item)">Удалить</v-btn>
                </template>
              </v-data-table>
            </v-card>

            <v-dialog v-model="priceDialog" max-width="500" persistent>
              <v-card>
                <v-card-title>{{ editingPrice ? 'Редактировать цену' : 'Новая цена' }}</v-card-title>
                <v-card-text>
                  <v-select
                    v-model="priceForm.material_type"
                    :items="materialTypeItems"
                    label="Тип макулатуры"
                    variant="outlined"
                    class="mb-3"
                  />
                  <v-text-field
                    v-model="priceForm.price_per_kg"
                    label="Цена за кг (руб)"
                    type="number"
                    min="0"
                    step="0.01"
                    variant="outlined"
                    class="mb-3"
                  />
                  <v-text-field
                    v-model="priceForm.valid_from"
                    label="Действует с (дата)"
                    type="date"
                    variant="outlined"
                    class="mb-3"
                  />
                  <v-text-field
                    v-model="priceForm.valid_to"
                    label="Действует по (дата, необяз.)"
                    type="date"
                    variant="outlined"
                    class="mb-3"
                  />
                  <v-checkbox v-model="priceForm.is_active" label="Активна" />
                </v-card-text>
                <v-card-actions>
                  <v-spacer />
                  <v-btn variant="text" @click="priceDialog = false">Отмена</v-btn>
                  <v-btn color="primary" :loading="savingPrice" @click="savePrice">Сохранить</v-btn>
                </v-card-actions>
              </v-card>
            </v-dialog>

            <v-dialog v-model="deletePriceDialog" max-width="400" persistent>
              <v-card>
                <v-card-title>Удалить запись о цене?</v-card-title>
                <v-card-actions>
                  <v-spacer />
                  <v-btn variant="text" @click="deletePriceDialog = false">Отмена</v-btn>
                  <v-btn color="error" :loading="deletingPrice" @click="doDeletePrice">Удалить</v-btn>
                </v-card-actions>
              </v-card>
            </v-dialog>
          </v-window-item>

          <!-- News -->
          <v-window-item value="news">
            <v-card>
              <v-card-title class="d-flex align-center">
                Новости
                <v-spacer />
                <v-btn color="primary" prepend-icon="mdi-plus" @click="openNewsDialog()">
                  Добавить новость
                </v-btn>
              </v-card-title>
              <v-divider />
              <v-data-table
                :headers="newsHeaders"
                :items="newsArticles"
                :loading="loadingNews"
                item-value="id"
              >
                <template #item.is_published="{ item }">
                  <v-switch
                    :model-value="item.is_published"
                    hide-details
                    density="compact"
                    color="success"
                    @update:model-value="toggleNewsPublish(item)"
                  />
                </template>
                <template #item.created_at="{ item }">
                  {{ formatNewsDate(item.created_at) }}
                </template>
                <template #item.actions="{ item }">
                  <v-btn size="small" variant="text" @click="openNewsDialog(item)">Изменить</v-btn>
                  <v-btn size="small" variant="text" color="error" @click="confirmDeleteNews(item)">Удалить</v-btn>
                </template>
              </v-data-table>
            </v-card>

            <v-dialog v-model="newsDialog" max-width="640" persistent scrollable>
              <v-card>
                <v-card-title>{{ editingNews ? 'Редактировать новость' : 'Новая новость' }}</v-card-title>
                <v-card-text style="max-height: 70vh" class="overflow-y-auto">
                  <v-text-field
                    v-model="newsForm.title"
                    label="Заголовок *"
                    variant="outlined"
                    class="mb-3"
                  />
                  <v-textarea
                    v-model="newsForm.content"
                    label="Содержание *"
                    variant="outlined"
                    rows="6"
                    class="mb-3"
                  />
                  <v-file-input
                    v-model="newsForm.imageFile"
                    label="Изображение (необяз.)"
                    accept="image/*"
                    prepend-icon=""
                    prepend-inner-icon="mdi-camera"
                    variant="outlined"
                    class="mb-3"
                    @update:model-value="onNewsImageChange"
                  />
                  <v-img
                    v-if="newsForm.imagePreview"
                    :src="newsForm.imagePreview"
                    max-height="200"
                    cover
                    class="rounded mb-3"
                  />
                  <v-checkbox v-model="newsForm.is_published" label="Опубликовано" />
                </v-card-text>
                <v-card-actions>
                  <v-spacer />
                  <v-btn variant="text" @click="newsDialog = false">Отмена</v-btn>
                  <v-btn color="primary" :loading="savingNews" @click="saveNews">Сохранить</v-btn>
                </v-card-actions>
              </v-card>
            </v-dialog>

            <v-dialog v-model="deleteNewsDialog" max-width="400" persistent>
              <v-card>
                <v-card-title>Удалить новость?</v-card-title>
                <v-card-text>
                  Будет удалена новость «{{ newsToDelete?.title }}». Действие нельзя отменить.
                </v-card-text>
                <v-card-actions>
                  <v-spacer />
                  <v-btn variant="text" @click="deleteNewsDialog = false">Отмена</v-btn>
                  <v-btn color="error" :loading="deletingNews" @click="doDeleteNews">Удалить</v-btn>
                </v-card-actions>
              </v-card>
            </v-dialog>
          </v-window-item>

          <!-- Companies -->
          <v-window-item value="companies">
            <v-card>
              <v-card-title class="d-flex align-center">
                Все компании
                <v-spacer />
                <v-btn color="primary" prepend-icon="mdi-plus" @click="openCompanyDialog()">
                  Добавить компанию
                </v-btn>
              </v-card-title>
              <v-divider />
              <v-data-table
                :headers="companyHeaders"
                :items="companies"
                :loading="loadingCompanies"
                item-value="id"
              >
                <template #item.contact_phone="{ item }">
                  {{ item.contact_phone }} / {{ item.contact_email }}
                </template>
                <template #item.actions="{ item }">
                  <v-btn size="small" variant="text" @click="openCompanyDialog(item)">Изменить</v-btn>
                  <v-btn size="small" variant="text" color="error" @click="confirmDeleteCompany(item)">Удалить</v-btn>
                </template>
              </v-data-table>
            </v-card>

            <v-dialog v-model="companyDialog" max-width="600" persistent scrollable>
              <v-card>
                <v-card-title>{{ editingCompany ? 'Редактировать компанию' : 'Новая компания' }}</v-card-title>
                <v-card-text style="max-height: 70vh" class="overflow-y-auto">
                  <v-text-field
                    v-model="companyForm.company_name"
                    label="Название компании *"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="companyForm.contact_email"
                    label="Почта *"
                    type="email"
                    variant="outlined"
                    class="mb-2"
                    :disabled="!!editingCompany"
                  />
                  <v-text-field
                    v-if="!editingCompany"
                    v-model="companyForm.password"
                    label="Пароль (необяз. — сгенерируется)"
                    type="password"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="companyForm.contact_phone"
                    label="Телефон *"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-textarea
                    v-model="companyForm.address"
                    label="Адрес *"
                    variant="outlined"
                    rows="2"
                    class="mb-2"
                  />
                  <v-textarea
                    v-model="companyForm.legal_address"
                    label="Юридический адрес (необяз.)"
                    variant="outlined"
                    rows="2"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="companyForm.inn"
                    label="ИНН (необяз.)"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="companyForm.kpp"
                    label="КПП (необяз.)"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="companyForm.ogrn"
                    label="ОГРН (необяз.)"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="companyForm.bank_account"
                    label="Расчётный счёт (необяз.)"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="companyForm.bank_name"
                    label="Название банка (необяз.)"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="companyForm.bik"
                    label="БИК (необяз.)"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="companyForm.corr_account"
                    label="Корр. счёт (необяз.)"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="companyForm.website"
                    label="Сайт (необяз.)"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-textarea
                    v-model="companyForm.description"
                    label="Описание (необяз.)"
                    variant="outlined"
                    rows="2"
                  />
                </v-card-text>
                <v-card-actions>
                  <v-spacer />
                  <v-btn variant="text" @click="companyDialog = false">Отмена</v-btn>
                  <v-btn color="primary" :loading="savingCompany" @click="saveCompany">Сохранить</v-btn>
                </v-card-actions>
              </v-card>
            </v-dialog>

            <v-dialog v-model="deleteCompanyDialog" max-width="400" persistent>
              <v-card>
                <v-card-title>Удалить компанию?</v-card-title>
                <v-card-text>
                  Будет удалена компания «{{ companyToDelete?.company_name }}» и все связанные организации. Действие нельзя отменить.
                </v-card-text>
                <v-card-actions>
                  <v-spacer />
                  <v-btn variant="text" @click="deleteCompanyDialog = false">Отмена</v-btn>
                  <v-btn color="error" :loading="deletingCompany" @click="doDeleteCompany">Удалить</v-btn>
                </v-card-actions>
              </v-card>
            </v-dialog>
          </v-window-item>

          <!-- Institutions -->
          <v-window-item value="institutions">
            <v-card>
              <v-card-title class="d-flex align-center">
                Все организации
                <v-spacer />
                <v-btn color="primary" prepend-icon="mdi-plus" @click="openInstitutionDialog()">
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
                  {{ item.contact_person }} / {{ item.phone }}
                </template>
                <template #item.actions="{ item }">
                  <v-btn size="small" variant="text" @click="openInstitutionDialog(item)">Изменить</v-btn>
                  <v-btn size="small" variant="text" color="error" @click="confirmDeleteInstitution(item)">Удалить</v-btn>
                </template>
              </v-data-table>
            </v-card>

            <v-dialog v-model="institutionDialog" max-width="600" persistent scrollable>
              <v-card>
                <v-card-title>{{ editingInstitution ? 'Редактировать организацию' : 'Новая организация' }}</v-card-title>
                <v-card-text style="max-height: 70vh" class="overflow-y-auto">
                  <v-select
                    v-model="institutionForm.parent_company"
                    :items="companies"
                    item-title="company_name"
                    item-value="id"
                    label="Компания (заявки идут только в эту компанию) *"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="institutionForm.email"
                    label="Почта / Логин (для входа) *"
                    type="email"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="institutionForm.password"
                    :label="editingInstitution ? 'Новый пароль (оставьте пустым, чтобы не менять)' : 'Пароль (необяз. — сгенерируется)'"
                    type="password"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="institutionForm.institution_name"
                    label="Название учреждения *"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="institutionForm.institution_type"
                    label="Тип организации *"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-textarea
                    v-model="institutionForm.address"
                    label="Адрес *"
                    variant="outlined"
                    rows="2"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="institutionForm.contact_person"
                    label="Контактное лицо *"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="institutionForm.phone"
                    label="Телефон *"
                    variant="outlined"
                    hint="Формат: +7 XXX XXX XX XX"
                    persistent-hint
                    class="mb-2"
                  />
                  <v-textarea
                    v-model="institutionForm.legal_address"
                    label="Юридический адрес (необяз.)"
                    variant="outlined"
                    rows="2"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="institutionForm.inn"
                    label="ИНН (необяз.)"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="institutionForm.kpp"
                    label="КПП (необяз.)"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="institutionForm.contact_person_on_site"
                    label="Контакт на площадке (необяз.)"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="institutionForm.phone_on_site"
                    label="Телефон на площадке (необяз.)"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="institutionForm.preferred_days"
                    label="Предпочтительные дни (необяз.)"
                    variant="outlined"
                    placeholder="пн, ср, пт"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="institutionForm.preferred_hours"
                    label="Предпочтительные часы (необяз.)"
                    variant="outlined"
                    placeholder="09:00-18:00"
                    class="mb-2"
                  />
                  <v-textarea
                    v-model="institutionForm.access_details"
                    label="Детали доступа (необяз.)"
                    variant="outlined"
                    rows="2"
                    class="mb-2"
                  />
                  <v-textarea
                    v-model="institutionForm.container_location"
                    label="Расположение контейнера (необяз.)"
                    variant="outlined"
                    rows="2"
                  />
                </v-card-text>
                <v-card-actions>
                  <v-spacer />
                  <v-btn variant="text" @click="institutionDialog = false">Отмена</v-btn>
                  <v-btn color="primary" :loading="savingInstitution" @click="saveInstitution">Сохранить</v-btn>
                </v-card-actions>
              </v-card>
            </v-dialog>

            <v-dialog v-model="deleteInstitutionDialog" max-width="400" persistent>
              <v-card>
                <v-card-title>Удалить организацию?</v-card-title>
                <v-card-text>
                  Будет удалена организация «{{ institutionToDelete?.institution_name }}». Действие нельзя отменить.
                </v-card-text>
                <v-card-actions>
                  <v-spacer />
                  <v-btn variant="text" @click="deleteInstitutionDialog = false">Отмена</v-btn>
                  <v-btn color="error" :loading="deletingInstitution" @click="doDeleteInstitution">Удалить</v-btn>
                </v-card-actions>
              </v-card>
            </v-dialog>
          </v-window-item>

          <!-- Requests -->
          <v-window-item value="requests">
            <v-card>
              <v-card-title class="d-flex align-center">
                Все заявки
                <v-spacer />
                <v-select
                  v-model="requestStatusFilter"
                  :items="requestStatusOptions"
                  density="compact"
                  hide-details
                  label="Статус"
                  variant="outlined"
                  style="max-width: 160px"
                />
              </v-card-title>
              <v-divider />
              <v-data-table
                :headers="requestHeaders"
                :items="filteredAdminRequests"
                :loading="loadingRequests"
                item-value="id"
              >
                <template #item.request_number="{ item }">
                  {{ item.request_number || item.id }}
                </template>
                <template #item.status="{ item }">
                  <v-chip :color="requestStatusColor(item.status)" size="small">
                    {{ requestStatusLabel(item.status) }}
                  </v-chip>
                </template>
                <template #item.estimated_value="{ item }">
                  {{ item.estimated_value != null ? `${item.estimated_value} руб.` : '—' }}
                </template>
                <template #item.actual_value="{ item }">
                  {{ item.actual_value != null ? `${item.actual_value} руб.` : '—' }}
                </template>
              </v-data-table>
            </v-card>
          </v-window-item>
        </v-window>
      </v-container>
    </v-main>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/api/axios'
import { useAuthStore } from '@/stores/auth'
import { useUserStore } from '@/stores/user'
import type { CompanyProfile, InstitutionProfile, CollectionRequest, NewsArticle, PriceList } from '@/types'

const router = useRouter()
const authStore = useAuthStore()
const userStore = useUserStore()

const activeTab = ref('prices')
const prices = ref<PriceList[]>([])
const companies = ref<CompanyProfile[]>([])
const institutions = ref<InstitutionProfile[]>([])
const adminRequests = ref<CollectionRequest[]>([])
const loadingPrices = ref(false)
const loadingCompanies = ref(false)
const loadingInstitutions = ref(false)
const loadingRequests = ref(false)
const priceDialog = ref(false)
const editingPrice = ref<PriceList | null>(null)
const savingPrice = ref(false)
const priceForm = reactive({
  material_type: 'paper',
  price_per_kg: '',
  valid_from: '',
  valid_to: '' as string,
  is_active: true,
})
const deletePriceDialog = ref(false)
const priceToDelete = ref<PriceList | null>(null)
const deletingPrice = ref(false)
const requestStatusFilter = ref('all')

const newsArticles = ref<NewsArticle[]>([])
const loadingNews = ref(false)
const newsDialog = ref(false)
const editingNews = ref<NewsArticle | null>(null)
const savingNews = ref(false)
const newsForm = reactive({
  title: '',
  content: '',
  imageFile: null as File[] | null,
  imagePreview: '' as string,
  is_published: true,
})
const deleteNewsDialog = ref(false)
const newsToDelete = ref<NewsArticle | null>(null)
const deletingNews = ref(false)

const newsHeaders = [
  { title: 'Заголовок', key: 'title' },
  { title: 'Дата', key: 'created_at', width: '140' },
  { title: 'Опубликовано', key: 'is_published', width: '120' },
  { title: 'Автор', key: 'author_username', width: '120' },
  { title: 'Действия', key: 'actions', sortable: false, width: '180' },
]

const companyDialog = ref(false)
const editingCompany = ref<CompanyProfile | null>(null)
const savingCompany = ref(false)
const companyForm = reactive({
  company_name: '',
  contact_email: '',
  password: '',
  contact_phone: '',
  address: '',
  legal_address: '',
  inn: '',
  kpp: '',
  ogrn: '',
  bank_account: '',
  bank_name: '',
  bik: '',
  corr_account: '',
  website: '',
  description: '',
})
const deleteCompanyDialog = ref(false)
const companyToDelete = ref<CompanyProfile | null>(null)
const deletingCompany = ref(false)

const institutionDialog = ref(false)
const editingInstitution = ref<InstitutionProfile | null>(null)
const savingInstitution = ref(false)
const institutionForm = reactive({
  parent_company: null as number | null,
  email: '',
  password: '',
  institution_name: '',
  institution_type: '',
  address: '',
  contact_person: '',
  phone: '',
  legal_address: '',
  inn: '',
  kpp: '',
  contact_person_on_site: '',
  phone_on_site: '',
  preferred_days: '',
  preferred_hours: '',
  access_details: '',
  container_location: '',
})
const deleteInstitutionDialog = ref(false)
const institutionToDelete = ref<InstitutionProfile | null>(null)
const deletingInstitution = ref(false)

const materialTypeItems = [
  { title: 'Бумага', value: 'paper' },
  { title: 'Картон', value: 'cardboard' },
  { title: 'Газеты', value: 'newspapers' },
  { title: 'Смешанная', value: 'mixed' },
  { title: 'Архивная', value: 'archive' },
]

const priceHeaders = [
  { title: 'Тип макулатуры', key: 'material_type_display' },
  { title: 'Цена', key: 'price_per_kg' },
  { title: 'Действует с', key: 'valid_from' },
  { title: 'Действует по', key: 'valid_to' },
  { title: 'Активна', key: 'is_active' },
  { title: 'Действия', key: 'actions', sortable: false, width: '180' },
]

const companyHeaders = [
  { title: 'Название', key: 'company_name' },
  { title: 'Контакты', key: 'contact_phone' },
  { title: 'Адрес', key: 'address' },
  { title: 'Действия', key: 'actions', sortable: false, width: '180' },
]

const institutionHeaders = [
  { title: 'Название', key: 'institution_name' },
  { title: 'Компания', key: 'parent_company_name' },
  { title: 'Тип', key: 'institution_type' },
  { title: 'Контакты', key: 'contacts' },
  { title: 'Адрес', key: 'address' },
  { title: 'Действия', key: 'actions', sortable: false, width: '180' },
]

const requestHeaders = [
  { title: 'Номер', key: 'request_number', width: '140' },
  { title: 'Организация', key: 'institution_name' },
  { title: 'Компания', key: 'receiving_company_name' },
  { title: 'Тип макулатуры', key: 'material_type_display' },
  { title: 'Вес (кг)', key: 'estimated_amount' },
  { title: 'Ориент. стоимость', key: 'estimated_value' },
  { title: 'Факт. стоимость', key: 'actual_value' },
  { title: 'Статус', key: 'status' },
  { title: 'Дата создания', key: 'created_at' },
]

const requestStatusOptions = [
  { title: 'Все', value: 'all' },
  { title: 'Новые', value: 'new' },
  { title: 'Принятые', value: 'accepted' },
  { title: 'Завершённые', value: 'completed' },
]

const filteredAdminRequests = computed(() => {
  if (requestStatusFilter.value === 'all') return adminRequests.value
  return adminRequests.value.filter((r) => r.status === requestStatusFilter.value)
})

function requestStatusLabel(s: string) {
  const m: Record<string, string> = { new: 'Новый', accepted: 'Принят', completed: 'Завершён' }
  return m[s] || s
}

function requestStatusColor(s: string) {
  const m: Record<string, string> = { new: 'warning', accepted: 'info', completed: 'success' }
  return m[s] || 'default'
}

async function loadPrices() {
  loadingPrices.value = true
  try {
    const { data } = await api.get<PriceList[]>('/prices/')
    prices.value = data
  } finally {
    loadingPrices.value = false
  }
}

async function loadCompanies() {
  loadingCompanies.value = true
  try {
    const { data } = await api.get<CompanyProfile[]>('/company-profiles/')
    companies.value = data
  } finally {
    loadingCompanies.value = false
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
    adminRequests.value = data
  } finally {
    loadingRequests.value = false
  }
}

async function loadNews() {
  loadingNews.value = true
  try {
    const { data } = await api.get<NewsArticle[]>('/news/')
    newsArticles.value = Array.isArray(data) ? data : []
  } finally {
    loadingNews.value = false
  }
}

function formatNewsDate(s: string) {
  if (!s) return '—'
  return new Date(s).toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

function openNewsDialog(item?: NewsArticle) {
  editingNews.value = item ?? null
  if (item) {
    newsForm.title = item.title
    newsForm.content = item.content
    newsForm.is_published = item.is_published
    newsForm.imageFile = null
    newsForm.imagePreview = item.image_url || ''
  } else {
    newsForm.title = ''
    newsForm.content = ''
    newsForm.is_published = true
    newsForm.imageFile = null
    newsForm.imagePreview = ''
  }
  newsDialog.value = true
}

function onNewsImageChange(files: File[] | File | null) {
  const arr = Array.isArray(files) ? files : files ? [files] : []
  if (arr.length > 0) {
    newsForm.imagePreview = URL.createObjectURL(arr[0])
  } else {
    newsForm.imagePreview = ''
  }
}

async function saveNews() {
  savingNews.value = true
  try {
    const formData = new FormData()
    formData.append('title', newsForm.title)
    formData.append('content', newsForm.content)
    formData.append('is_published', String(newsForm.is_published))
    if (newsForm.imageFile && newsForm.imageFile.length > 0) {
      formData.append('image', newsForm.imageFile[0])
    }
    if (editingNews.value) {
      await api.patch(`/news/${editingNews.value.id}/`, formData)
    } else {
      await api.post('/news/', formData)
    }
    newsDialog.value = false
    await loadNews()
  } finally {
    savingNews.value = false
  }
}

function confirmDeleteNews(item: NewsArticle) {
  newsToDelete.value = item
  deleteNewsDialog.value = true
}

async function doDeleteNews() {
  if (!newsToDelete.value) return
  deletingNews.value = true
  try {
    await api.delete(`/news/${newsToDelete.value.id}/`)
    deleteNewsDialog.value = false
    newsToDelete.value = null
    await loadNews()
  } finally {
    deletingNews.value = false
  }
}

async function toggleNewsPublish(item: NewsArticle) {
  try {
    await api.patch(`/news/${item.id}/`, { is_published: !item.is_published })
    await loadNews()
  } catch {
    // ignore
  }
}

function openPriceDialog(item?: PriceList) {
  editingPrice.value = item ?? null
  if (item) {
    priceForm.material_type = item.material_type
    priceForm.price_per_kg = String(item.price_per_kg)
    priceForm.valid_from = item.valid_from
    priceForm.valid_to = item.valid_to || ''
    priceForm.is_active = item.is_active
  } else {
    priceForm.material_type = 'paper'
    priceForm.price_per_kg = ''
    priceForm.valid_from = new Date().toISOString().slice(0, 10)
    priceForm.valid_to = ''
    priceForm.is_active = true
  }
  priceDialog.value = true
}

async function savePrice() {
  savingPrice.value = true
  try {
    const payload = {
      material_type: priceForm.material_type,
      price_per_kg: priceForm.price_per_kg,
      valid_from: priceForm.valid_from,
      valid_to: priceForm.valid_to || null,
      is_active: priceForm.is_active,
    }
    if (editingPrice.value) {
      await api.patch(`/prices/${editingPrice.value.id}/`, payload)
    } else {
      await api.post('/prices/', payload)
    }
    priceDialog.value = false
    await loadPrices()
  } finally {
    savingPrice.value = false
  }
}

function confirmDeletePrice(item: PriceList) {
  priceToDelete.value = item
  deletePriceDialog.value = true
}

async function doDeletePrice() {
  if (!priceToDelete.value) return
  deletingPrice.value = true
  try {
    await api.delete(`/prices/${priceToDelete.value.id}/`)
    deletePriceDialog.value = false
    priceToDelete.value = null
    await loadPrices()
  } finally {
    deletingPrice.value = false
  }
}

function openCompanyDialog(item?: CompanyProfile) {
  editingCompany.value = item ?? null
  if (item) {
    companyForm.company_name = item.company_name
    companyForm.contact_email = item.contact_email
    companyForm.contact_phone = item.contact_phone
    companyForm.address = item.address ?? ''
    companyForm.legal_address = item.legal_address ?? ''
    companyForm.inn = item.inn ?? ''
    companyForm.kpp = item.kpp ?? ''
    companyForm.ogrn = item.ogrn ?? ''
    companyForm.bank_account = item.bank_account ?? ''
    companyForm.bank_name = item.bank_name ?? ''
    companyForm.bik = item.bik ?? ''
    companyForm.corr_account = item.corr_account ?? ''
    companyForm.website = item.website ?? ''
    companyForm.description = item.description ?? ''
  } else {
    companyForm.company_name = ''
    companyForm.contact_email = ''
    companyForm.password = ''
    companyForm.contact_phone = ''
    companyForm.address = ''
    companyForm.legal_address = ''
    companyForm.inn = ''
    companyForm.kpp = ''
    companyForm.ogrn = ''
    companyForm.bank_account = ''
    companyForm.bank_name = ''
    companyForm.bik = ''
    companyForm.corr_account = ''
    companyForm.website = ''
    companyForm.description = ''
  }
  companyDialog.value = true
}

async function saveCompany() {
  savingCompany.value = true
  try {
    const payload: Record<string, string> = {
      company_name: companyForm.company_name,
      contact_phone: companyForm.contact_phone,
      address: companyForm.address,
      contact_email: companyForm.contact_email,
      legal_address: companyForm.legal_address || '',
      inn: companyForm.inn || '',
      kpp: companyForm.kpp || '',
      ogrn: companyForm.ogrn || '',
      bank_account: companyForm.bank_account || '',
      bank_name: companyForm.bank_name || '',
      bik: companyForm.bik || '',
      corr_account: companyForm.corr_account || '',
      website: companyForm.website || '',
      description: companyForm.description || '',
    }
    if (editingCompany.value) {
      await api.patch(`/company-profiles/${editingCompany.value.id}/`, payload)
    } else {
      await api.post('/company-profiles/', {
        ...payload,
        email: companyForm.contact_email,
        password: companyForm.password || undefined,
      })
    }
    companyDialog.value = false
    await loadCompanies()
  } finally {
    savingCompany.value = false
  }
}

function confirmDeleteCompany(item: CompanyProfile) {
  companyToDelete.value = item
  deleteCompanyDialog.value = true
}

async function doDeleteCompany() {
  if (!companyToDelete.value) return
  deletingCompany.value = true
  try {
    await api.delete(`/company-profiles/${companyToDelete.value.id}/`)
    deleteCompanyDialog.value = false
    companyToDelete.value = null
    await loadCompanies()
    await loadInstitutions()
  } finally {
    deletingCompany.value = false
  }
}

async function openInstitutionDialog(item?: InstitutionProfile) {
  editingInstitution.value = item ?? null
  if (item) {
    institutionForm.parent_company = item.parent_company
    institutionForm.email = item.email
    institutionForm.password = ''
    institutionForm.institution_name = item.institution_name
    institutionForm.institution_type = item.institution_type
    institutionForm.address = item.address ?? ''
    institutionForm.contact_person = item.contact_person
    institutionForm.phone = item.phone
    institutionForm.legal_address = item.legal_address ?? ''
    institutionForm.inn = item.inn ?? ''
    institutionForm.kpp = item.kpp ?? ''
    institutionForm.contact_person_on_site = item.contact_person_on_site ?? ''
    institutionForm.phone_on_site = item.phone_on_site ?? ''
    institutionForm.preferred_days = item.preferred_days ?? ''
    institutionForm.preferred_hours = item.preferred_hours ?? ''
    institutionForm.access_details = item.access_details ?? ''
    institutionForm.container_location = item.container_location ?? ''
  } else {
    if (companies.value.length === 0) await loadCompanies()
    institutionForm.parent_company = companies.value.length ? companies.value[0].id : null
    institutionForm.email = ''
    institutionForm.password = ''
    institutionForm.institution_name = ''
    institutionForm.institution_type = ''
    institutionForm.address = ''
    institutionForm.contact_person = ''
    institutionForm.phone = ''
    institutionForm.legal_address = ''
    institutionForm.inn = ''
    institutionForm.kpp = ''
    institutionForm.contact_person_on_site = ''
    institutionForm.phone_on_site = ''
    institutionForm.preferred_days = ''
    institutionForm.preferred_hours = ''
    institutionForm.access_details = ''
    institutionForm.container_location = ''
  }
  institutionDialog.value = true
}

async function saveInstitution() {
  savingInstitution.value = true
  try {
    const payload: Record<string, unknown> = {
      institution_name: institutionForm.institution_name,
      institution_type: institutionForm.institution_type,
      address: institutionForm.address,
      contact_person: institutionForm.contact_person,
      phone: institutionForm.phone,
      email: institutionForm.email,
      legal_address: institutionForm.legal_address || '',
      inn: institutionForm.inn || '',
      kpp: institutionForm.kpp || '',
      contact_person_on_site: institutionForm.contact_person_on_site || '',
      phone_on_site: institutionForm.phone_on_site || '',
      preferred_days: institutionForm.preferred_days || '',
      preferred_hours: institutionForm.preferred_hours || '',
      access_details: institutionForm.access_details || '',
      container_location: institutionForm.container_location || '',
    }
    if (editingInstitution.value) {
      payload.parent_company = institutionForm.parent_company
      if (institutionForm.password) payload.password = institutionForm.password
      await api.patch(`/institutions/${editingInstitution.value.id}/`, payload)
    } else {
      if (institutionForm.parent_company == null) return
      await api.post('/institutions/', {
        ...payload,
        parent_company: institutionForm.parent_company,
        password: institutionForm.password || undefined,
      })
    }
    institutionDialog.value = false
    await loadInstitutions()
  } finally {
    savingInstitution.value = false
  }
}

function confirmDeleteInstitution(item: InstitutionProfile) {
  institutionToDelete.value = item
  deleteInstitutionDialog.value = true
}

async function doDeleteInstitution() {
  if (!institutionToDelete.value) return
  deletingInstitution.value = true
  try {
    await api.delete(`/institutions/${institutionToDelete.value.id}/`)
    deleteInstitutionDialog.value = false
    institutionToDelete.value = null
    await loadInstitutions()
  } finally {
    deletingInstitution.value = false
  }
}

function logout() {
  authStore.logout()
  userStore.clearUser()
  router.push({ name: 'Login' })
}

watch(activeTab, (tab) => {
  if (tab === 'prices') loadPrices()
  if (tab === 'news') loadNews()
  if (tab === 'companies') loadCompanies()
  if (tab === 'institutions') loadInstitutions()
  if (tab === 'requests') loadRequests()
})

onMounted(() => {
  loadPrices()
})
</script>
