<template>
  <div class="inst-dashboard">
    <header class="inst-dashboard__header">
      <div class="inst-dashboard__header-inner">
        <div class="inst-dashboard__brand">Vuvoz</div>
        <nav class="inst-dashboard__nav">
          <button
            type="button"
            class="inst-dashboard__tab"
            :class="{ 'inst-dashboard__tab--active': mainTab === 'requests' }"
            @click="mainTab = 'requests'"
          >
            Заявки
          </button>
          <button
            type="button"
            class="inst-dashboard__tab"
            :class="{ 'inst-dashboard__tab--active': mainTab === 'stats' }"
            @click="mainTab = 'stats'"
          >
            Статистика
          </button>
          <button
            type="button"
            class="inst-dashboard__tab"
            :class="{ 'inst-dashboard__tab--active': mainTab === 'points' }"
            @click="mainTab = 'points'"
          >
            Баллы
          </button>
        </nav>
        <div class="inst-dashboard__actions">
          <InstitutionNotifications
            :items="notifications"
            :unread-count="unreadCount"
            @mark-read="markNotificationRead"
            @mark-all-read="markAllNotificationsRead"
          />
          <div class="inst-dashboard__profile" ref="profileRef">
            <button
              type="button"
              class="inst-dashboard__profile-btn"
              @click="profileMenuOpen = !profileMenuOpen"
            >
              <span class="inst-dashboard__avatar">{{ avatarText }}</span>
              <span class="inst-dashboard__username">{{ userStore.user?.username }}</span>
              <v-icon icon="mdi-chevron-down" size="20" :class="{ 'inst-dashboard__chevron--open': profileMenuOpen }" />
            </button>
            <div v-show="profileMenuOpen" class="inst-dashboard__profile-menu">
              <button type="button" @click="showEditProfile = true; profileMenuOpen = false">
                Изменить контакты
              </button>
              <button type="button" @click="logout">
                Выйти
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>

    <main class="inst-dashboard__main">
      <div class="inst-dashboard__container">
        <!-- Summary cards (visible on requests tab) -->
        <section v-if="mainTab === 'requests'" class="inst-dashboard__summary">
          <InstitutionStatCard
            title="Мои заявки"
            :value="requests.length"
            icon="mdi-file-document-multiple"
            color="primary"
          />
          <InstitutionStatCard
            title="Вывезено (кг)"
            :value="totalWeightDisplay"
            icon="mdi-weight-kilogram"
            color="info"
          />
          <InstitutionStatCard
            title="Зелёные баллы"
            :value="pointsBalance"
            icon="mdi-leaf"
            color="success"
            subtitle="На балансе"
          />
        </section>

        <!-- Requests tab -->
        <template v-if="mainTab === 'requests'">
          <!-- Compact org info -->
          <div class="inst-dashboard__org-card">
            <div class="inst-dashboard__org-info">
              <h3 class="inst-dashboard__org-name">{{ userStore.institutionProfile?.institution_name }}</h3>
              <p class="inst-dashboard__org-detail">{{ userStore.institutionProfile?.institution_type }} · {{ userStore.institutionProfile?.address }}</p>
            </div>
            <button type="button" class="inst-dashboard__org-edit" @click="showEditProfile = true">
              Редактировать контакты
            </button>
          </div>

          <!-- Collecting company info -->
          <div v-if="userStore.institutionProfile?.parent_company_name" class="inst-dashboard__company-card">
            <h4 class="inst-dashboard__company-title">Компания вывоза</h4>
            <p class="inst-dashboard__company-name">{{ userStore.institutionProfile?.parent_company_name }}</p>
            <p v-if="userStore.institutionProfile?.parent_company_contact_phone" class="inst-dashboard__company-contact">
              Тел.: {{ userStore.institutionProfile.parent_company_contact_phone }}
            </p>
            <p v-if="userStore.institutionProfile?.parent_company_contact_email" class="inst-dashboard__company-contact">
              Email: {{ userStore.institutionProfile.parent_company_contact_email }}
            </p>
          </div>

          <!-- New request form -->
          <InstitutionRequestForm
            :material-lines="materialLines"
            :desired-date="form.desired_date"
            :comment="form.comment"
            :weight-limits="weightLimits"
            :material-type-items="materialTypeItems"
            :errors="errors"
            :estimated-value-preview="estimatedValuePreview"
            :submitting="submitting"
            @submit="submitRequest"
            @add-line="addMaterialLine"
            @remove-line="removeMaterialLine"
            @update:desired-date="form.desired_date = $event"
            @update:comment="form.comment = $event"
          />

          <!-- Request grid with New/Completed tabs -->
          <div class="inst-dashboard__section">
            <h3 class="inst-dashboard__section-title">Заявки</h3>
            <InstitutionRequestGrid
              :items="requests"
              :loading="dashboardStore.loadingRequests"
              :institution-name="userStore.institutionProfile?.institution_name"
              @cancelled="dashboardStore.fetchRequests()"
            />
          </div>
        </template>

        <!-- Stats tab -->
        <template v-if="mainTab === 'stats'">
          <InstitutionCharts :requests="requests" />
        </template>

        <!-- Points tab -->
        <template v-if="mainTab === 'points'">
          <div class="inst-dashboard__points-summary">
            <InstitutionStatCard
              title="Баланс зелёных баллов"
              :value="pointsBalance"
              icon="mdi-leaf"
              color="success"
              subtitle="Баллы начисляются за завершённые заявки"
            />
            <button type="button" class="inst-dashboard__points-history" @click="pointsHistoryModal = true">
              История баллов
            </button>
          </div>

          <div class="inst-dashboard__section">
            <h3 class="inst-dashboard__section-title">Каталог товаров</h3>
            <div v-if="loadingProducts" class="inst-dashboard__loading">
              <v-progress-circular indeterminate color="primary" size="40" />
            </div>
            <div v-else-if="!products.length" class="inst-dashboard__empty">Товаров пока нет.</div>
            <div v-else class="inst-dashboard__products">
              <article
                v-for="p in products"
                :key="p.id"
                class="inst-product-card"
                @click="addToOrder(p)"
              >
                <div class="inst-product-card__img">
                  <img v-if="productImageSrc(p)" :src="productImageSrc(p)" :alt="p.name" />
                  <v-icon v-else icon="mdi-image-outline" size="48" color="grey" />
                </div>
                <div class="inst-product-card__body">
                  <h4 class="inst-product-card__name">{{ p.name }}</h4>
                  <p class="inst-product-card__desc">{{ p.description || '—' }}</p>
                  <div class="inst-product-card__footer">
                    <span class="inst-product-card__price">{{ p.price_in_points }} баллов</span>
                    <v-btn size="small" color="primary">В заказ</v-btn>
                  </div>
                </div>
              </article>
            </div>
            <div v-if="orderItems.length" class="inst-dashboard__cart">
              <span>В корзине: {{ orderItems.map(i => i.name + ' × ' + i.quantity).join(', ') }} · {{ orderTotal }} баллов</span>
              <div>
                <v-btn variant="text" size="small" @click="orderItems = []">Очистить</v-btn>
                <v-btn color="primary" size="small" @click="openOrderDialog">Оформить заказ</v-btn>
              </div>
            </div>
          </div>
        </template>
      </div>
    </main>

    <!-- Modals -->
    <Teleport to="body">
      <div v-if="showEditProfile" class="inst-modal-backdrop" @click.self="showEditProfile = false">
        <div class="inst-modal hp-card inst-modal--wide">
          <h3 class="inst-modal__title">Изменить данные учреждения</h3>
          <v-text-field v-model="profileEdit.institution_name" label="Название учреждения *" variant="outlined" class="mb-3" :error-messages="profileEditErrors.institution_name" />
          <v-text-field v-model="profileEdit.contact_person" label="Контактное лицо *" variant="outlined" class="mb-3" :error-messages="profileEditErrors.contact_person" />
          <v-text-field v-model="profileEdit.email" label="Email (логин) *" variant="outlined" type="email" class="mb-3" :error-messages="profileEditErrors.email" />
          <v-text-field v-model="profileEdit.phone" label="Телефон *" variant="outlined" hint="7 XXX XXX XX XX или +7 XXX XXX XX XX" persistent-hint class="mb-3" :error-messages="profileEditErrors.phone" />
          <v-text-field v-model="profileEdit.password" label="Новый пароль" variant="outlined" type="password" hint="Оставьте пустым, чтобы не менять" persistent-hint class="mb-3" :error-messages="profileEditErrors.password" />
          <div class="inst-modal__actions">
            <v-btn variant="text" @click="showEditProfile = false">Отмена</v-btn>
            <v-btn color="primary" :loading="savingProfile" @click="saveProfile">Сохранить</v-btn>
          </div>
        </div>
      </div>

      <div v-if="pointsHistoryModal" class="inst-modal-backdrop" @click.self="pointsHistoryModal = false">
        <div class="inst-modal hp-card">
          <div class="inst-modal__header">
            <h3 class="inst-modal__title">История баллов</h3>
            <button type="button" class="inst-modal__close" @click="pointsHistoryModal = false">×</button>
          </div>
          <div class="inst-modal__body">
            <table v-if="pointsHistory.length" class="inst-history-table">
              <thead>
                <tr><th>Сумма</th><th>Дата</th><th>Заявка / Заказ</th></tr>
              </thead>
              <tbody>
                <tr v-for="(h, i) in pointsHistory" :key="i">
                  <td :class="h.type === 'expense' ? 'text-error' : 'text-success'">{{ h.type === 'expense' ? h.amount : '+' + h.amount }}</td>
                  <td>{{ formatPointsDate(h.date) }}</td>
                  <td>{{ h.reference }}</td>
                </tr>
              </tbody>
            </table>
            <p v-else class="inst-modal__empty">Нет записей.</p>
          </div>
        </div>
      </div>

      <div v-if="orderDialog" class="inst-modal-backdrop" @click.self="orderDialog = false">
        <div class="inst-modal hp-card">
          <h3 class="inst-modal__title">Оформление заказа</h3>
          <p class="inst-modal__sub">В заказе: {{ orderItems.map(i => i.name + ' × ' + i.quantity).join(', ') }}. Итого: {{ orderTotal }} баллов.</p>
          <v-alert v-if="orderError" type="error" density="compact" class="mb-3">{{ orderError }}</v-alert>
          <v-text-field v-model="orderForm.recipient_name" label="ФИО получателя *" variant="outlined" class="mb-2" />
          <v-text-field v-model="orderForm.recipient_phone" label="Телефон *" variant="outlined" class="mb-2" />
          <v-textarea v-model="orderForm.address" label="Адрес доставки *" variant="outlined" rows="3" />
          <div class="inst-modal__actions">
            <v-btn variant="text" @click="orderDialog = false">Отмена</v-btn>
            <v-btn color="primary" :loading="submittingOrder" @click="submitOrder">Подтвердить</v-btn>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/api/axios'
import { useAuthStore } from '@/stores/auth'
import { useUserStore } from '@/stores/user'
import { useInstitutionDashboardStore } from '@/stores/institutionDashboard'
import InstitutionStatCard from '@/components/institution/InstitutionStatCard.vue'
import InstitutionRequestForm from '@/components/institution/InstitutionRequestForm.vue'
import InstitutionRequestGrid from '@/components/institution/InstitutionRequestGrid.vue'
import InstitutionCharts from '@/components/institution/InstitutionCharts.vue'
import InstitutionNotifications from '@/components/institution/InstitutionNotifications.vue'
import type { CollectionRequest, CurrentPrice, InstitutionProfile, Product as ProductType, PointsHistoryItem } from '@/types'

const router = useRouter()
const authStore = useAuthStore()
const userStore = useUserStore()
const dashboardStore = useInstitutionDashboardStore()

const mainTab = ref('requests')
const profileRef = ref<HTMLElement | null>(null)
const profileMenuOpen = ref(false)
const showEditProfile = ref(false)
const profileEdit = reactive({ institution_name: '', contact_person: '', email: '', phone: '', password: '' })
const profileEditErrors = reactive<Record<string, string>>({})
const savingProfile = ref(false)
const pointsHistoryModal = ref(false)
const orderDialog = ref(false)
const orderForm = reactive({ recipient_name: '', recipient_phone: '', address: '' })
const orderError = ref('')
const submittingOrder = ref(false)
const notifications = ref<{ id: number; title: string; message: string; read: boolean }[]>([])
const unreadCount = ref(0)
const products = ref<ProductType[]>([])
const loadingProducts = ref(false)
const orderItems = ref<{ product_id: number; name: string; quantity: number; price: string }[]>([])
const formRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null)
const currentPrices = ref<CurrentPrice[]>([])
const weightLimits = ref<{ min_kg: string; max_kg: string } | null>(null)
const submitting = ref(false)

const materialTypeItems = [
  { title: 'Бумага', value: 'paper' },
  { title: 'Картон', value: 'cardboard' },
  { title: 'Газеты', value: 'newspapers' },
  { title: 'Смешанная', value: 'mixed' },
  { title: 'Архивная', value: 'archive' },
]

const materialLines = ref<{ material_type: string; amount_kg: string }[]>([{ material_type: 'paper', amount_kg: '' }])
const form = reactive({ desired_date: '', comment: '' })
const errors = reactive<{ material_lines?: string }>({})

const requests = computed(() => dashboardStore.requests)
const pointsBalance = computed(() => {
  const b = userStore.institutionProfile?.bonus_balance
  if (b !== undefined && b !== null) return String(b)
  return dashboardStore.pointsData.balance || '0'
})
const pointsHistory = computed(() => dashboardStore.pointsData.history)
const totalWeightDisplay = computed(() => dashboardStore.totalWeight.toFixed(1))

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

const orderTotal = computed(() =>
  orderItems.value.reduce((sum, i) => sum + parseFloat(i.price) * i.quantity, 0).toFixed(2)
)

const avatarText = computed(() => {
  const name = userStore.institutionProfile?.institution_name || userStore.user?.username || ''
  const parts = name.split(/\s+/)
  if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase()
  return (name[0] || 'О').toUpperCase()
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
    await dashboardStore.fetchRequests()
  } catch (err: unknown) {
    const ax = err as { response?: { data?: Record<string, string | string[]> } }
    const data = ax.response?.data
    const msg = data?.material_lines ?? data?.non_field_errors
    errors.material_lines = msg ? (Array.isArray(msg) ? msg.join(' ') : String(msg)) : 'Не удалось отправить запрос.'
  } finally {
    submitting.value = false
  }
}

function productImageSrc(p: { image_url?: string | null; image?: string }): string {
  const u = p.image_url || (p.image ? `/media/${(p.image as string).replace(/^\//, '')}` : '')
  if (!u) return ''
  if (u.startsWith('http')) return u
  return window.location.origin + (u.startsWith('/') ? u : '/' + u)
}

function formatPointsDate(iso: string | null) {
  if (!iso) return '—'
  return new Date(iso).toLocaleString('ru-RU', { dateStyle: 'short', timeStyle: 'short' })
}

function addToOrder(p: ProductType) {
  const existing = orderItems.value.find((i) => i.product_id === p.id)
  if (existing) existing.quantity += 1
  else orderItems.value.push({ product_id: p.id, name: p.name, quantity: 1, price: p.price_in_points })
}

function openOrderDialog() {
  if (!orderItems.value.length) return
  orderForm.recipient_name = userStore.institutionProfile?.contact_person ?? ''
  orderForm.recipient_phone = userStore.institutionProfile?.phone ?? ''
  orderForm.address = userStore.institutionProfile?.address ?? ''
  orderError.value = ''
  orderDialog.value = true
}

async function submitOrder() {
  orderError.value = ''
  if (!orderForm.recipient_name?.trim()) { orderError.value = 'Укажите ФИО получателя'; return }
  if (!orderForm.recipient_phone?.trim()) { orderError.value = 'Укажите телефон'; return }
  if (!orderForm.address?.trim()) { orderError.value = 'Укажите адрес доставки'; return }
  submittingOrder.value = true
  try {
    await api.post('/points-orders/', {
      recipient_name: orderForm.recipient_name.trim(),
      recipient_phone: orderForm.recipient_phone.trim(),
      address: orderForm.address.trim(),
      items: orderItems.value.map((i) => ({ product_id: i.product_id, quantity: i.quantity })),
    })
    orderDialog.value = false
    orderItems.value = []
    await userStore.fetchMe()
    await dashboardStore.fetchPoints()
  } catch (err: unknown) {
    const ax = err as { response?: { data?: { detail?: string } } }
    orderError.value = ax.response?.data?.detail ?? 'Ошибка при оформлении заказа'
  } finally {
    submittingOrder.value = false
  }
}

watch(showEditProfile, (open) => {
  if (open && userStore.institutionProfile) {
    profileEdit.institution_name = userStore.institutionProfile.institution_name ?? ''
    profileEdit.contact_person = userStore.institutionProfile.contact_person ?? ''
    profileEdit.email = userStore.user?.username ?? userStore.institutionProfile.email ?? ''
    profileEdit.phone = userStore.institutionProfile.phone ?? ''
    profileEdit.password = ''
    profileEditErrors.institution_name = ''
    profileEditErrors.contact_person = ''
    profileEditErrors.email = ''
    profileEditErrors.phone = ''
    profileEditErrors.password = ''
  }
})

async function saveProfile() {
  const profile = userStore.institutionProfile as (InstitutionProfile & { id: number }) | null
  if (!profile?.id) return
  profileEditErrors.institution_name = ''
  profileEditErrors.contact_person = ''
  profileEditErrors.email = ''
  profileEditErrors.phone = ''
  profileEditErrors.password = ''
  if (!profileEdit.institution_name?.trim()) { profileEditErrors.institution_name = 'Обязательное поле'; return }
  if (!profileEdit.contact_person?.trim()) { profileEditErrors.contact_person = 'Обязательное поле'; return }
  if (!profileEdit.email?.trim()) { profileEditErrors.email = 'Обязательное поле'; return }
  if (!profileEdit.phone?.trim()) { profileEditErrors.phone = 'Обязательное поле'; return }
  savingProfile.value = true
  try {
    const payload: Record<string, string> = {
      institution_name: profileEdit.institution_name.trim(),
      contact_person: profileEdit.contact_person.trim(),
      email: profileEdit.email.trim(),
      phone: profileEdit.phone.trim(),
    }
    if (profileEdit.password?.trim()) payload.password = profileEdit.password.trim()
    await api.patch(`/institutions/${profile.id}/`, payload)
    await userStore.fetchMe()
    showEditProfile.value = false
  } catch (err: unknown) {
    const ax = err as { response?: { data?: Record<string, string | string[]> } }
    const d = ax.response?.data
    if (d) {
      const setErr = (key: string) => { profileEditErrors[key] = Array.isArray(d![key]) ? (d![key] as string[]).join(' ') : String(d![key]) }
      if (d.institution_name) setErr('institution_name')
      if (d.contact_person) setErr('contact_person')
      if (d.email) setErr('email')
      if (d.phone) setErr('phone')
      if (d.password) setErr('password')
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
  } catch {}
}

async function markNotificationRead(id: number) {
  try {
    await api.post(`/notifications/${id}/mark_read/`)
    const n = notifications.value.find((x) => x.id === id)
    if (n) n.read = true
    unreadCount.value = Math.max(0, unreadCount.value - 1)
  } catch {}
}

async function markAllNotificationsRead() {
  try {
    await api.post('/notifications/mark_all_read/')
    notifications.value.forEach((n) => (n.read = true))
    unreadCount.value = 0
  } catch {}
}

function logout() {
  authStore.logout()
  userStore.clearUser()
  router.push({ name: 'Login' })
}

function handleClickOutside(e: MouseEvent) {
  if (profileMenuOpen.value && profileRef.value && !profileRef.value.contains(e.target as Node)) {
    profileMenuOpen.value = false
  }
}

async function loadProducts() {
  loadingProducts.value = true
  try {
    const { data } = await api.get<ProductType[]>('/products/')
    products.value = data
  } catch {
    products.value = []
  } finally {
    loadingProducts.value = false
  }
}

onMounted(() => {
  loadWeightLimits()
  loadCurrentPrices()
  dashboardStore.fetchRequests()
  loadNotifications()
  document.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})

watch(mainTab, (tab) => {
  if (tab === 'points') {
    dashboardStore.fetchPoints()
    loadProducts()
  }
  if (tab === 'stats') {
    dashboardStore.fetchStats()
  }
})
</script>

<style scoped lang="scss">
.inst-dashboard {
  min-height: 100vh;
  background: var(--vuvoz-surface);
}

.inst-dashboard__header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: var(--vuvoz-surface-elevated);
  border-bottom: 1px solid var(--vuvoz-border);
  box-shadow: var(--vuvoz-shadow-sm);
}

.inst-dashboard__header-inner {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0.75rem 1.5rem;
  display: flex;
  align-items: center;
  gap: 2rem;
}

.inst-dashboard__brand {
  font-weight: 800;
  font-size: 1.25rem;
  color: var(--vuvoz-primary);
  letter-spacing: -0.02em;
}

.inst-dashboard__nav {
  display: flex;
  gap: 0.25rem;
}

.inst-dashboard__tab {
  padding: 0.5rem 1rem;
  border: none;
  background: transparent;
  font-size: 0.95rem;
  font-weight: 500;
  color: var(--vuvoz-text-muted);
  border-radius: var(--vuvoz-radius-sm);
  cursor: pointer;
  transition: color 0.2s, background 0.2s;
  &:hover {
    color: var(--vuvoz-text);
    background: var(--vuvoz-surface-muted);
  }
  &--active {
    color: var(--vuvoz-primary);
    background: rgba(13, 148, 136, 0.08);
  }
}

.inst-dashboard__actions {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.inst-dashboard__profile {
  position: relative;
}

.inst-dashboard__profile-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.35rem 0.75rem;
  border: 2px solid var(--vuvoz-border);
  border-radius: var(--vuvoz-radius);
  background: #fff;
  cursor: pointer;
  font-size: 0.9rem;
  color: var(--vuvoz-text);
  transition: border-color 0.2s;
  &:hover {
    border-color: var(--vuvoz-primary);
  }
}

.inst-dashboard__avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--vuvoz-primary);
  color: #fff;
  font-weight: 700;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.inst-dashboard__chevron--open {
  transform: rotate(180deg);
}

.inst-dashboard__profile-menu {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 0.35rem;
  min-width: 180px;
  padding: 0.5rem;
  background: #fff;
  border-radius: var(--vuvoz-radius);
  border: 1px solid var(--vuvoz-border);
  box-shadow: var(--vuvoz-shadow-lg);
  z-index: 100;
  button {
    display: block;
    width: 100%;
    padding: 0.5rem 0.75rem;
    border: none;
    background: none;
    font-size: 0.9rem;
    text-align: left;
    cursor: pointer;
    border-radius: var(--vuvoz-radius-sm);
    color: var(--vuvoz-text);
    &:hover { background: var(--vuvoz-surface-muted); }
  }
}

.inst-dashboard__main {
  padding: 1.5rem;
}

.inst-dashboard__container {
  max-width: 1200px;
  margin: 0 auto;
}

.inst-dashboard__summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.inst-dashboard__org-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
  padding: 1rem 1.25rem;
  background: var(--vuvoz-surface-elevated);
  border-radius: var(--vuvoz-radius-lg);
  border: 1px solid var(--vuvoz-border);
  margin-bottom: 1.5rem;
}

.inst-dashboard__org-name {
  font-size: 1.1rem;
  font-weight: 700;
  margin: 0 0 0.25rem;
  color: var(--vuvoz-text);
}

.inst-dashboard__org-detail {
  font-size: 0.9rem;
  color: var(--vuvoz-text-muted);
  margin: 0;
}

.inst-dashboard__org-edit {
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--vuvoz-primary);
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.35rem 0;
  &:hover { text-decoration: underline; }
}

.inst-dashboard__company-card {
  padding: 1rem 1.25rem;
  background: var(--vuvoz-surface-muted);
  border-radius: var(--vuvoz-radius-lg);
  border: 1px solid var(--vuvoz-border);
  margin-bottom: 1.5rem;
}

.inst-dashboard__company-title {
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  color: var(--vuvoz-text-muted);
  margin: 0 0 0.5rem;
}

.inst-dashboard__company-name {
  font-size: 1rem;
  font-weight: 600;
  color: var(--vuvoz-text);
  margin: 0 0 0.25rem;
}

.inst-dashboard__company-contact {
  font-size: 0.9rem;
  color: var(--vuvoz-text-muted);
  margin: 0 0 0.15rem;
}

.inst-dashboard__section {
  margin-top: 2rem;
}

.inst-dashboard__section-title {
  font-size: 1.15rem;
  font-weight: 700;
  margin: 0 0 1rem;
  color: var(--vuvoz-text);
}

.inst-dashboard__points-summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.inst-dashboard__points-history {
  padding: 0.5rem 1rem;
  border: 2px solid var(--vuvoz-primary);
  border-radius: var(--vuvoz-radius-sm);
  background: transparent;
  color: var(--vuvoz-primary);
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  &:hover { background: rgba(13, 148, 136, 0.06); }
}

.inst-dashboard__products {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1.25rem;
}

.inst-product-card {
  background: var(--vuvoz-surface-elevated);
  border-radius: var(--vuvoz-radius-lg);
  border: 1px solid var(--vuvoz-border);
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s var(--vuvoz-ease), box-shadow 0.2s var(--vuvoz-ease);
  &:hover {
    transform: translateY(-4px);
    box-shadow: var(--vuvoz-shadow-lg);
  }
}

.inst-product-card__img {
  aspect-ratio: 16/10;
  background: var(--vuvoz-surface-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
}

.inst-product-card__body {
  padding: 1rem;
}

.inst-product-card__name {
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 0.35rem;
  color: var(--vuvoz-text);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.inst-product-card__desc {
  font-size: 0.85rem;
  color: var(--vuvoz-text-muted);
  margin: 0 0 1rem;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.inst-product-card__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.inst-product-card__price {
  font-weight: 700;
  color: #059669;
  font-size: 1rem;
}

.inst-dashboard__loading,
.inst-dashboard__empty {
  text-align: center;
  padding: 3rem;
  color: var(--vuvoz-text-muted);
}

.inst-dashboard__cart {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
  margin-top: 1.5rem;
  padding: 1rem 1.25rem;
  background: var(--vuvoz-surface-muted);
  border-radius: var(--vuvoz-radius);
  font-size: 0.95rem;
}

.inst-modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 1rem;
}

.inst-modal {
  background: #fff;
  padding: 1.5rem;
  max-width: 440px;
  &--wide { max-width: 480px; }
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  border-radius: var(--vuvoz-radius-lg);
  box-shadow: var(--vuvoz-shadow-xl);
}

.inst-modal__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.inst-modal__title {
  margin: 0;
  font-size: 1.25rem;
}

.inst-modal__close {
  width: 36px;
  height: 36px;
  border: none;
  background: var(--vuvoz-surface-muted);
  border-radius: var(--vuvoz-radius-sm);
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--vuvoz-text);
}

.inst-modal__sub {
  margin: 0 0 1rem;
  font-size: 0.95rem;
  color: var(--vuvoz-text-secondary);
}

.inst-modal__body {
  margin-bottom: 1rem;
}

.inst-modal__empty {
  margin: 0;
  color: var(--vuvoz-text-muted);
  font-size: 0.9rem;
}

.inst-modal__actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1rem;
}

.inst-history-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
  th, td {
    padding: 0.5rem 0.75rem;
    text-align: left;
    border-bottom: 1px solid var(--vuvoz-border);
  }
  th {
    font-weight: 600;
    color: var(--vuvoz-text-muted);
  }
}
</style>
