<template>
  <v-dialog :model-value="modelValue" :max-width="fullscreen ? undefined : 640" :fullscreen="fullscreen" persistent scrollable class="request-detail-modal" @update:model-value="$emit('update:modelValue', $event)">
    <v-card v-if="request">
      <v-card-title class="d-flex align-center py-3">
        Заявка {{ request.request_number || request.id }}
        <v-spacer />
        <v-chip :color="statusColor(request.status)" size="small" variant="tonal">
          {{ statusLabel(request.status) }}
        </v-chip>
        <v-btn icon variant="text" @click="$emit('update:modelValue', false)">
          <v-icon icon="mdi-close" />
        </v-btn>
      </v-card-title>
      <v-divider />
      <v-card-text class="text-body-2 pt-3">
        <div class="request-detail__section">
          <div class="request-detail__row">
            <span class="request-detail__label">Организация</span>
            <a href="javascript:void(0)" class="request-detail__link" @click="$emit('view-institution', request)">
              {{ request.institution_name }}
            </a>
          </div>
          <div class="request-detail__row">
            <span class="request-detail__label">Материал / вес</span>
            <span>{{ materialDisplay }}</span>
          </div>
          <div class="request-detail__row">
            <span class="request-detail__label">Ориент. стоимость</span>
            <span>{{ request.estimated_value != null ? `${request.estimated_value} руб.` : '—' }}</span>
          </div>
          <div class="request-detail__row">
            <span class="request-detail__label">Желаемая дата</span>
            <span>{{ request.desired_date ? formatDate(request.desired_date) : '—' }}</span>
          </div>
          <div class="request-detail__row">
            <span class="request-detail__label">Создана</span>
            <span>{{ formatDateTime(request.created_at) }}</span>
          </div>
          <template v-if="request.status === 'accepted'">
            <div class="request-detail__row">
              <span class="request-detail__label">Дата вывоза</span>
              <span>{{ request.actual_collection_date ? formatDate(request.actual_collection_date) : 'не назначена' }}</span>
            </div>
            <div class="request-detail__dates-edit mt-3">
              <div class="text-caption text-medium-emphasis mb-2">Назначить или изменить дату вывоза</div>
              <v-text-field
                v-model="editActualDate"
                label="Дата вывоза"
                type="date"
                variant="outlined"
                density="compact"
                hide-details
                class="mb-2"
              />
              <v-btn size="small" color="primary" :loading="savingDates" @click="saveDates">
                Сохранить дату
              </v-btn>
            </div>
          </template>
          <template v-if="request.status === 'pending_confirmation'">
            <div class="request-detail__row">
              <span class="request-detail__label">Факт. вес (кг)</span>
              <span>{{ request.actual_amount ?? '—' }}</span>
            </div>
            <div class="request-detail__row">
              <span class="request-detail__label">Факт. стоимость</span>
              <span>{{ request.actual_value != null ? `${request.actual_value} руб.` : '—' }}</span>
            </div>
            <div class="request-detail__row text-medium-emphasis">
              <span>Ожидает подтверждения учреждением</span>
            </div>
          </template>
          <template v-if="request.status === 'completed'">
            <div class="request-detail__row">
              <span class="request-detail__label">Факт. вес (кг)</span>
              <span>{{ request.actual_amount ?? '—' }}</span>
            </div>
            <div class="request-detail__row">
              <span class="request-detail__label">Факт. стоимость</span>
              <span>{{ request.actual_value != null ? `${request.actual_value} руб.` : '—' }}</span>
            </div>
            <div class="request-detail__row">
              <span class="request-detail__label">Дата вывоза</span>
              <span>{{ request.actual_collection_date ? formatDate(request.actual_collection_date) : '—' }}</span>
            </div>
          </template>
          <div v-if="request.comment" class="request-detail__row">
            <span class="request-detail__label">Комментарий</span>
            <span>{{ request.comment }}</span>
          </div>
        </div>
        <div class="request-detail__timeline mt-4">
          <div class="text-caption text-medium-emphasis mb-2">Статусы</div>
          <div class="request-detail__timeline-item">
            <v-icon icon="mdi-circle-small" size="20" color="success" />
            <span>Создана — {{ formatDateTime(request.created_at) }}</span>
          </div>
          <div v-if="request.status !== 'new'" class="request-detail__timeline-item">
            <v-icon icon="mdi-circle-small" size="20" color="info" />
            <span>Принята</span>
          </div>
          <div v-if="request.status === 'pending_confirmation'" class="request-detail__timeline-item">
            <v-icon icon="mdi-circle-small" size="20" color="warning" />
            <span>Ожидает подтверждения учреждения</span>
          </div>
          <div v-if="request.status === 'completed'" class="request-detail__timeline-item">
            <v-icon icon="mdi-circle-small" size="20" color="success" />
            <span>Завершена — {{ request.completed_at ? formatDateTime(request.completed_at) : '—' }}</span>
          </div>
        </div>
      </v-card-text>
      <v-divider />
      <v-card-actions class="py-3">
        <v-spacer />
        <v-btn v-if="request.status === 'new'" color="primary" @click="$emit('accept', request)">
          Принять заявку
        </v-btn>
        <v-btn v-if="request.status === 'accepted'" color="success" @click="$emit('complete', request)">
          Завершить
        </v-btn>
        <v-btn variant="text" @click="$emit('update:modelValue', false)">Закрыть</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { api } from '@/api/axios'
import type { CollectionRequest } from '@/types'

const props = defineProps<{ modelValue: boolean; request: CollectionRequest | null; fullscreen?: boolean }>()

const emit = defineEmits<{
  'update:modelValue': [v: boolean]
  accept: [r: CollectionRequest]
  complete: [r: CollectionRequest]
  'view-institution': [r: CollectionRequest]
  saved: []
}>()

const request = computed(() => props.request)

const editActualDate = ref('')
const savingDates = ref(false)

watch(() => props.request, (r) => {
  if (r) {
    editActualDate.value = r.actual_collection_date?.slice(0, 10) ?? ''
  }
}, { immediate: true })

async function saveDates() {
  if (!props.request) return
  savingDates.value = true
  try {
    await api.patch(`/collection-requests/${props.request.id}/`, {
      actual_collection_date: editActualDate.value || null,
    })
    emit('saved')
  } finally {
    savingDates.value = false
  }
}

const materialLabels: Record<string, string> = {
  cardboard: 'Картон',
  paper: 'Макулатура',
  canisters: 'Канистры/флаконы',
  polyethylene: 'Полиэтилен/стрейч пленка',
  metal: 'Металл бытовой',
  glass: 'Стекло (бутылки)',
}

const materialDisplay = computed(() => {
  const r = props.request
  if (!r) return '—'
  const lines = r.material_lines
  if (lines?.length) {
    return lines
      .map((l) => `${materialLabels[l.material_type] || l.material_type} ${l.amount_kg} кг`)
      .join(', ')
  }
  return r.material_type_display || r.material_type || '—'
})

function statusLabel(s: string) {
  const m: Record<string, string> = {
    new: 'Новый',
    accepted: 'Принят',
    pending_confirmation: 'Ожидает подтверждения',
    completed: 'Завершён',
    cancelled: 'Отменён',
  }
  return m[s] || s
}

function statusColor(s: string) {
  const m: Record<string, string> = {
    new: 'warning',
    accepted: 'info',
    pending_confirmation: 'warning',
    completed: 'success',
    cancelled: 'grey',
  }
  return m[s] || 'grey'
}

function formatDate(s: string) {
  if (!s) return '—'
  return new Date(s).toLocaleDateString('ru-RU')
}

function formatDateTime(s: string) {
  if (!s) return '—'
  return new Date(s).toLocaleString('ru-RU', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}
</script>

<style lang="scss" scoped>
.request-detail__section { display: flex; flex-direction: column; gap: 10px; }
.request-detail__row { display: flex; flex-wrap: wrap; gap: 8px; }
.request-detail__label { font-weight: 600; min-width: 140px; color: var(--vuvoz-text-muted, #64748b); }
.request-detail__link { color: rgb(var(--v-theme-primary)); text-decoration: none; }
.request-detail__link:hover { text-decoration: underline; }
.request-detail__timeline-item { display: flex; align-items: center; gap: 6px; margin-bottom: 4px; }
</style>
