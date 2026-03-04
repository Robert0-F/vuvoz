<template>
  <div class="inst-request-grid">
    <!-- New / Active / Completed tabs -->
    <div class="inst-request-grid__tabs">
      <button
        type="button"
        class="inst-request-grid__tab"
        :class="{ 'inst-request-grid__tab--active': ordersTab === 'new' }"
        @click="ordersTab = 'new'"
      >
        Новые
      </button>
      <button
        type="button"
        class="inst-request-grid__tab"
        :class="{ 'inst-request-grid__tab--active': ordersTab === 'accepted' }"
        @click="ordersTab = 'accepted'"
      >
        В работе
      </button>
      <button
        type="button"
        class="inst-request-grid__tab"
        :class="{ 'inst-request-grid__tab--active': ordersTab === 'completed' }"
        @click="ordersTab = 'completed'"
      >
        Завершённые
      </button>
    </div>

    <div class="inst-request-grid__toolbar">
      <div class="inst-request-grid__filters">
        <input
          v-model="dateFrom"
          type="date"
          class="inst-request-grid__date"
          placeholder="С"
        />
        <input
          v-model="dateTo"
          type="date"
          class="inst-request-grid__date"
          placeholder="По"
        />
      </div>
      <div class="inst-request-grid__sort">
        <select v-model="sortBy" class="inst-request-grid__select inst-request-grid__select--sort">
          <option value="created_at">По дате создания</option>
          <option value="status">По статусу</option>
          <option value="estimated_value">По сумме</option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="inst-request-grid__loading">
      <v-progress-circular indeterminate color="primary" size="40" />
    </div>

    <div v-else-if="!filtered.length" class="inst-request-grid__empty">
      Нет заявок по выбранным фильтрам.
    </div>

    <div v-else class="inst-request-grid__cards">
      <article
        v-for="item in paginatedItems"
        :key="item.id"
        class="inst-request-card"
        @click="openQuickView(item)"
      >
        <div class="inst-request-card__top">
          <span class="inst-request-card__num">{{ item.request_number || item.id }}</span>
          <span class="inst-request-card__status" :class="`inst-request-card__status--${item.status}`">
            {{ statusLabel(item.status) }}
          </span>
        </div>
        <div class="inst-request-card__body">
          <div class="inst-request-card__row">
            <span class="inst-request-card__label">Макулатура</span>
            <span class="inst-request-card__value">{{ formatMaterialLines(item) }}</span>
          </div>
          <div class="inst-request-card__row">
            <span class="inst-request-card__label">Сумма</span>
            <span class="inst-request-card__value">{{ item.actual_value ?? item.estimated_value ?? '—' }} руб.</span>
          </div>
          <div class="inst-request-card__row">
            <span class="inst-request-card__label">Дата создания</span>
            <span class="inst-request-card__value">{{ formatDate(item.created_at) }}</span>
          </div>
          <!-- Executor info for accepted/completed -->
          <div v-if="item.status === 'accepted' || item.status === 'completed'" class="inst-request-card__executor">
            <div class="inst-request-card__executor-title">Принято компанией: {{ item.receiving_company_name || '—' }}</div>
            <div v-if="item.receiving_company_phone" class="inst-request-card__executor-line">
              <v-icon icon="mdi-phone-outline" size="16" class="inst-request-card__executor-icon" />
              <a :href="`tel:${item.receiving_company_phone}`" class="inst-request-card__executor-link">{{ item.receiving_company_phone }}</a>
            </div>
            <div v-if="item.receiving_company_email" class="inst-request-card__executor-line">
              <v-icon icon="mdi-email-outline" size="16" class="inst-request-card__executor-icon" />
              <a :href="`mailto:${item.receiving_company_email}`" class="inst-request-card__executor-link">{{ item.receiving_company_email }}</a>
            </div>
            <div class="inst-request-card__executor-line">
              <v-icon icon="mdi-calendar" size="16" class="inst-request-card__executor-icon" />
              <span>Планируемая дата вывоза: {{ plannedDateLabel(item) }}</span>
            </div>
          </div>
        </div>
        <div class="inst-request-card__footer">
          <button
            v-if="canCancel(item)"
            type="button"
            class="inst-request-card__cancel"
            @click.stop="cancelRequest(item)"
          >
            Отменить
          </button>
          <span class="inst-request-card__action">
            Подробнее
            <v-icon icon="mdi-chevron-right" size="20" />
          </span>
        </div>
      </article>
    </div>

    <div v-if="totalPages > 1" class="inst-request-grid__pagination">
      <button
        type="button"
        class="inst-request-grid__page"
        :disabled="currentPage <= 1"
        @click="currentPage--"
      >
        ‹
      </button>
      <span class="inst-request-grid__page-info">{{ currentPage }} / {{ totalPages }}</span>
      <button
        type="button"
        class="inst-request-grid__page"
        :disabled="currentPage >= totalPages"
        @click="currentPage++"
      >
        ›
      </button>
    </div>

    <!-- Cancel confirmation modal -->
    <Teleport to="body">
      <div v-if="confirmCancelItem" class="inst-quick-view" @click.self="closeCancelConfirm">
        <div class="inst-quick-view__panel">
          <div class="inst-quick-view__header">
            <h3>Подтверждение отмены</h3>
            <button type="button" class="inst-quick-view__close" aria-label="Закрыть" @click="closeCancelConfirm">
              <v-icon icon="mdi-close" size="24" />
            </button>
          </div>
          <div class="inst-quick-view__body">
            <p>Вы уверены, что хотите отменить заявку {{ confirmCancelItem.request_number || confirmCancelItem.id }}?</p>
            <div class="inst-quick-view__actions inst-quick-view__actions--row">
              <button type="button" class="inst-quick-view__cancel inst-quick-view__cancel--secondary" @click="closeCancelConfirm">
                Нет
              </button>
              <button
                type="button"
                class="inst-quick-view__cancel"
                :disabled="cancellingId === confirmCancelItem.id"
                @click="confirmCancel"
              >
                {{ cancellingId === confirmCancelItem.id ? 'Отмена…' : 'Да, отменить' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Quick view modal -->
    <Teleport to="body">
      <div v-if="quickViewItem" class="inst-quick-view" @click.self="quickViewItem = null">
        <div class="inst-quick-view__panel">
          <div class="inst-quick-view__header">
            <h3>Заявка {{ quickViewItem.request_number || quickViewItem.id }}</h3>
            <button type="button" class="inst-quick-view__close" aria-label="Закрыть" @click="quickViewItem = null">
              <v-icon icon="mdi-close" size="24" />
            </button>
          </div>
          <div class="inst-quick-view__body">
            <div class="inst-quick-view__row">
              <span class="inst-quick-view__label">Статус</span>
              <span class="inst-quick-view__status" :class="`inst-quick-view__status--${quickViewItem.status}`">
                {{ statusLabel(quickViewItem.status) }}
              </span>
            </div>
            <div class="inst-quick-view__row">
              <span class="inst-quick-view__label">Типы макулатуры и вес</span>
              <span>{{ formatMaterialLines(quickViewItem) }}</span>
            </div>
            <div class="inst-quick-view__row">
              <span class="inst-quick-view__label">Ориент. стоимость</span>
              <span>{{ quickViewItem.estimated_value ?? '—' }} руб.</span>
            </div>
            <div class="inst-quick-view__row">
              <span class="inst-quick-view__label">Факт. стоимость</span>
              <span>{{ quickViewItem.actual_value ?? '—' }} руб.</span>
            </div>
            <div class="inst-quick-view__row">
              <span class="inst-quick-view__label">Желаемая дата</span>
              <span>{{ quickViewItem.desired_date ? formatDate(quickViewItem.desired_date) : '—' }}</span>
            </div>
            <div class="inst-quick-view__row">
              <span class="inst-quick-view__label">Дата создания</span>
              <span>{{ formatDate(quickViewItem.created_at) }}</span>
            </div>
            <div v-if="quickViewItem.completed_at" class="inst-quick-view__row">
              <span class="inst-quick-view__label">Дата завершения</span>
              <span>{{ formatDate(quickViewItem.completed_at) }}</span>
            </div>
            <div v-if="quickViewItem.comment" class="inst-quick-view__row">
              <span class="inst-quick-view__label">Комментарий</span>
              <span>{{ quickViewItem.comment }}</span>
            </div>
            <!-- Executor info for accepted/completed -->
            <div v-if="(quickViewItem.status === 'accepted' || quickViewItem.status === 'completed') && quickViewItem.receiving_company_name" class="inst-quick-view__executor">
              <h4 class="inst-quick-view__executor-title">Информация об исполнителе</h4>
              <div class="inst-quick-view__executor-row">
                <span class="inst-quick-view__label">Компания</span>
                <span>{{ quickViewItem.receiving_company_name }}</span>
              </div>
              <div v-if="quickViewItem.receiving_company_phone" class="inst-quick-view__executor-row">
                <v-icon icon="mdi-phone-outline" size="18" class="inst-quick-view__executor-icon" />
                <a :href="`tel:${quickViewItem.receiving_company_phone}`" class="inst-quick-view__executor-link">{{ quickViewItem.receiving_company_phone }}</a>
              </div>
              <div v-if="quickViewItem.receiving_company_email" class="inst-quick-view__executor-row">
                <v-icon icon="mdi-email-outline" size="18" class="inst-quick-view__executor-icon" />
                <a :href="`mailto:${quickViewItem.receiving_company_email}`" class="inst-quick-view__executor-link">{{ quickViewItem.receiving_company_email }}</a>
              </div>
              <div class="inst-quick-view__executor-row">
                <v-icon icon="mdi-calendar" size="18" class="inst-quick-view__executor-icon" />
                <span>Планируемая дата: {{ quickViewItem.estimated_collection_date ? formatDate(quickViewItem.estimated_collection_date) : (quickViewItem.desired_date ? formatDate(quickViewItem.desired_date) : '—') }}</span>
              </div>
              <div v-if="quickViewItem.actual_collection_date" class="inst-quick-view__executor-row">
                <v-icon icon="mdi-calendar-check" size="18" class="inst-quick-view__executor-icon" />
                <span>Фактическая дата вывоза: {{ formatDate(quickViewItem.actual_collection_date) }}</span>
              </div>
            </div>
            <div v-if="canCancel(quickViewItem)" class="inst-quick-view__actions">
              <button
                type="button"
                class="inst-quick-view__cancel"
                @click="cancelRequest(quickViewItem)"
              >
                Отменить заявку
              </button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { api } from '@/api/axios'
import type { CollectionRequest } from '@/types'

const props = defineProps<{
  items: CollectionRequest[]
  loading?: boolean
  institutionName?: string
}>()

const emit = defineEmits<{ (e: 'cancelled'): void }>()

const ordersTab = ref<'new' | 'accepted' | 'completed'>('new')
const dateFrom = ref('')
const dateTo = ref('')
const sortBy = ref('created_at')
const currentPage = ref(1)
const pageSize = 12
const quickViewItem = ref<CollectionRequest | null>(null)

const materialTypeLabels: Record<string, string> = {
  cardboard: 'Картон',
  paper: 'Макулатура',
  canisters: 'Канистры/флаконы',
  polyethylene: 'Полиэтилен/стрейч пленка',
  metal: 'Металл бытовой',
  glass: 'Стекло (бутылки)',
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
  return new Date(s).toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' })
}

function statusLabel(s: string) {
  const m: Record<string, string> = { new: 'Новый', accepted: 'Принят', completed: 'Завершён', cancelled: 'Отменён' }
  return m[s] || s
}

function plannedDateLabel(item: CollectionRequest): string {
  const d = item.actual_collection_date || item.estimated_collection_date || item.desired_date
  return d ? formatDate(d) : 'не указана'
}

function canCancel(item: CollectionRequest) {
  return item.status === 'new' || item.status === 'accepted'
}

function openQuickView(item: CollectionRequest) {
  quickViewItem.value = item
}

const filtered = computed(() => {
  let list = [...props.items]
  if (ordersTab.value === 'new') {
    list = list.filter((r) => r.status === 'new')
  } else if (ordersTab.value === 'accepted') {
    list = list.filter((r) => r.status === 'accepted')
  } else {
    list = list.filter((r) => r.status === 'completed' || r.status === 'cancelled')
  }
  if (dateFrom.value) {
    const from = new Date(dateFrom.value)
    list = list.filter((r) => new Date(r.created_at) >= from)
  }
  if (dateTo.value) {
    const to = new Date(dateTo.value)
    to.setHours(23, 59, 59, 999)
    list = list.filter((r) => new Date(r.created_at) <= to)
  }
  list.sort((a, b) => {
    if (sortBy.value === 'created_at') return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    if (sortBy.value === 'status') return (a.status || '').localeCompare(b.status || '')
    const av = parseFloat(String(a.estimated_value || a.actual_value || 0))
    const bv = parseFloat(String(b.estimated_value || b.actual_value || 0))
    return bv - av
  })
  return list
})

const totalPages = computed(() => Math.max(1, Math.ceil(filtered.value.length / pageSize)))

const paginatedItems = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filtered.value.slice(start, start + pageSize)
})

watch([ordersTab, dateFrom, dateTo, sortBy], () => {
  currentPage.value = 1
})

const cancellingId = ref<number | null>(null)
const confirmCancelItem = ref<CollectionRequest | null>(null)

async function cancelRequest(item: CollectionRequest) {
  confirmCancelItem.value = item
}

async function confirmCancel() {
  const item = confirmCancelItem.value
  if (!item) return
  cancellingId.value = item.id
  try {
    await api.post(`/collection-requests/${item.id}/cancel/`)
    confirmCancelItem.value = null
    emit('cancelled')
  } catch {
    // Error handling: could add toast
  } finally {
    cancellingId.value = null
  }
}

function closeCancelConfirm() {
  if (!cancellingId.value) {
    confirmCancelItem.value = null
  }
}

</script>

<style scoped lang="scss">
.inst-request-grid__toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.25rem;
}

.inst-request-grid__filters,
.inst-request-grid__sort {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.inst-request-grid__select,
.inst-request-grid__date {
  padding: 0.5rem 0.75rem;
  border-radius: var(--vuvoz-radius-sm);
  border: 2px solid var(--vuvoz-border);
  font-size: 0.9rem;
  background: #fff;
  &:focus { outline: none; border-color: var(--vuvoz-primary); }
}

.inst-request-grid__date {
  min-width: 140px;
}

.inst-request-grid__loading,
.inst-request-grid__empty {
  text-align: center;
  padding: 3rem 2rem;
  color: var(--vuvoz-text-muted);
}

.inst-request-grid__cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
}

@media (max-width: 640px) {
  .inst-request-grid__cards {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }
  .inst-request-grid__toolbar {
    flex-direction: column;
    align-items: stretch;
  }
  .inst-request-grid__tabs {
    flex-wrap: wrap;
  }
  .inst-request-card__body {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }
  .inst-request-card__executor {
    padding: 0.6rem;
  }
  .inst-request-card__executor-line {
    flex-wrap: wrap;
  }
}

.inst-request-card {
  background: var(--vuvoz-surface-elevated);
  border-radius: var(--vuvoz-radius-lg);
  border: 1px solid var(--vuvoz-border);
  padding: 1.25rem;
  cursor: pointer;
  transition: transform 0.2s var(--vuvoz-ease), box-shadow 0.2s var(--vuvoz-ease);
  &:hover {
    transform: translateY(-2px);
    box-shadow: var(--vuvoz-shadow-lg);
  }
}

.inst-request-card__top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.inst-request-card__num {
  font-weight: 700;
  font-size: 1rem;
  color: var(--vuvoz-text);
}

.inst-request-card__status {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 9999px;
  &--new { background: rgba(245, 158, 11, 0.15); color: #b45309; }
  &--accepted { background: rgba(14, 165, 233, 0.15); color: #0ea5e9; }
  &--completed { background: rgba(5, 150, 105, 0.15); color: #059669; }
  &--cancelled { background: rgba(107, 114, 128, 0.15); color: #6b7280; }
}

.inst-request-card__body {
  margin-bottom: 1rem;
}

.inst-request-card__row {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  margin-bottom: 0.35rem;
  font-size: 0.9rem;
}

.inst-request-card__label {
  color: var(--vuvoz-text-muted);
}

.inst-request-card__value {
  color: var(--vuvoz-text);
  text-align: right;
}

.inst-request-card__executor {
  margin-top: 1rem;
  padding: 0.75rem;
  background: rgba(13, 148, 136, 0.06);
  border-radius: var(--vuvoz-radius-sm);
  border: 1px solid rgba(13, 148, 136, 0.2);
}

.inst-request-card__executor-title {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--vuvoz-text-muted);
  margin: 0 0 0.5rem 0;
}

.inst-request-card__executor-line {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.85rem;
  margin-bottom: 0.25rem;
  &:last-child { margin-bottom: 0; }
}

.inst-request-card__executor-icon {
  flex-shrink: 0;
  color: var(--vuvoz-primary);
}

.inst-request-card__executor-link {
  color: var(--vuvoz-primary);
  text-decoration: none;
  word-break: break-all;
  &:hover { text-decoration: underline; }
}

.inst-request-card__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--vuvoz-border);
  font-size: 0.85rem;
  font-weight: 600;
}

.inst-request-card__cancel {
  padding: 0.35rem 0.75rem;
  border: 1px solid var(--vuvoz-border);
  border-radius: var(--vuvoz-radius-sm);
  background: transparent;
  color: var(--vuvoz-text-muted);
  font-size: 0.8rem;
  cursor: pointer;
  &:hover { border-color: #dc2626; color: #dc2626; }
}

.inst-request-card__action {
  margin-left: auto;
  color: var(--vuvoz-primary);
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.inst-request-grid__pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-top: 1.5rem;
}

.inst-request-grid__page {
  width: 40px;
  height: 40px;
  border-radius: var(--vuvoz-radius-sm);
  border: 2px solid var(--vuvoz-border);
  background: #fff;
  font-size: 1.25rem;
  cursor: pointer;
  &:hover:not(:disabled) {
    border-color: var(--vuvoz-primary);
    background: rgba(13, 148, 136, 0.06);
  }
  &:disabled { opacity: 0.4; cursor: not-allowed; }
}

.inst-request-grid__page-info {
  font-size: 0.9rem;
  color: var(--vuvoz-text-muted);
}

.inst-quick-view {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 1rem;
}

@media (max-width: 640px) {
  .inst-quick-view {
    padding: 0.5rem;
    align-items: flex-end;
  }
  .inst-quick-view__panel {
    max-height: 85vh;
    border-radius: var(--vuvoz-radius-lg) var(--vuvoz-radius-lg) 0 0;
  }
}

.inst-quick-view__panel {
  background: #fff;
  border-radius: var(--vuvoz-radius-lg);
  box-shadow: var(--vuvoz-shadow-xl);
  max-width: 480px;
  width: 100%;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.inst-quick-view__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--vuvoz-border);
}

.inst-quick-view__header h3 {
  margin: 0;
  font-size: 1.2rem;
}

.inst-quick-view__close {
  width: 40px;
  height: 40px;
  border: none;
  background: transparent;
  cursor: pointer;
  color: var(--vuvoz-text-muted);
  &:hover { color: var(--vuvoz-text); }
}

.inst-quick-view__body {
  padding: 1.5rem;
  overflow-y: auto;
}

.inst-quick-view__row {
  margin-bottom: 1rem;
  font-size: 0.95rem;
}

.inst-quick-view__label {
  display: block;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--vuvoz-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.03em;
  margin-bottom: 0.25rem;
}

.inst-quick-view__status {
  font-weight: 600;
  &--new { color: #b45309; }
  &--accepted { color: #0ea5e9; }
  &--completed { color: #059669; }
  &--cancelled { color: #6b7280; }
}

.inst-quick-view__executor {
  margin-top: 1.25rem;
  padding: 1rem;
  background: rgba(13, 148, 136, 0.06);
  border-radius: var(--vuvoz-radius-sm);
  border: 1px solid rgba(13, 148, 136, 0.2);
}

.inst-quick-view__executor-title {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--vuvoz-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.03em;
  margin: 0 0 0.75rem 0;
}

.inst-quick-view__executor-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  font-size: 0.95rem;
  &:last-child { margin-bottom: 0; }
}

.inst-quick-view__executor-icon {
  flex-shrink: 0;
  color: var(--vuvoz-primary);
}

.inst-quick-view__executor-link {
  color: var(--vuvoz-primary);
  text-decoration: none;
  word-break: break-all;
  &:hover { text-decoration: underline; }
}

.inst-request-grid__tabs {
  display: flex;
  gap: 0.25rem;
  margin-bottom: 1rem;
}

.inst-request-grid__tab {
  padding: 0.5rem 1rem;
  border: 2px solid var(--vuvoz-border);
  border-radius: var(--vuvoz-radius-sm);
  background: #fff;
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--vuvoz-text-muted);
  cursor: pointer;
  transition: border-color 0.2s, color 0.2s, background 0.2s;
  &:hover { border-color: var(--vuvoz-primary); color: var(--vuvoz-primary); }
  &--active {
    border-color: var(--vuvoz-primary);
    color: var(--vuvoz-primary);
    background: rgba(13, 148, 136, 0.06);
  }
}

.inst-quick-view__actions {
  margin-top: 1rem;
  display: flex;
  gap: 0.75rem;
  &--row { flex-direction: row; }
}

.inst-quick-view__cancel {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: var(--vuvoz-radius-sm);
  background: rgba(220, 38, 38, 0.1);
  color: #dc2626;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  &:hover:not(:disabled) { background: rgba(220, 38, 38, 0.2); }
  &:disabled { opacity: 0.7; cursor: not-allowed; }
  &--secondary {
    background: var(--vuvoz-surface-muted);
    color: var(--vuvoz-text);
    &:hover { background: var(--vuvoz-border); }
  }
}
</style>
