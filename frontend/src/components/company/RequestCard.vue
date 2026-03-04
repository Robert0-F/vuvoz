<template>
  <v-card
    class="request-card"
    elevation="1"
    rounded="lg"
    @click="$emit('click')"
  >
    <div class="request-card__inner">
      <div class="request-card__top">
        <h3 class="request-card__institution" @click.stop="$emit('view-institution', request)">
          {{ request.institution_name }}
        </h3>
        <v-chip
          :color="statusColor"
          size="small"
          variant="tonal"
          class="request-card__badge"
        >
          {{ statusLabel }}
        </v-chip>
      </div>

      <div class="request-card__row">
        <v-icon icon="mdi-recycle" size="18" class="request-card__icon" />
        <span class="request-card__material">{{ materialDisplay }}</span>
      </div>
      <div class="request-card__row request-card__row--meta">
        <span class="request-card__weight">{{ estimatedWeight }} кг</span>
        <span v-if="request.desired_date" class="request-card__date">
          {{ formatDate(request.desired_date) }}
        </span>
      </div>
      <div class="request-card__time">{{ timeAgo }}</div>

      <div class="request-card__actions">
        <template v-if="request.status === 'new'">
          <v-btn
            color="primary"
            variant="tonal"
            size="small"
            block
            prepend-icon="mdi-check"
            class="request-card__btn"
            @click.stop="$emit('accept', request)"
          >
            Принять
          </v-btn>
          <v-btn
            variant="text"
            size="small"
            block
            class="request-card__btn"
            @click.stop="$emit('view-details', request)"
          >
            Подробнее
          </v-btn>
        </template>
        <template v-else-if="request.status === 'accepted'">
          <v-btn
            color="success"
            variant="tonal"
            size="small"
            block
            prepend-icon="mdi-check-circle"
            class="request-card__btn"
            @click.stop="$emit('complete', request)"
          >
            Завершить
          </v-btn>
          <v-btn
            variant="text"
            size="small"
            block
            class="request-card__btn"
            @click.stop="$emit('view-details', request)"
          >
            Подробнее
          </v-btn>
        </template>
        <template v-else>
          <v-btn
            variant="text"
            size="small"
            block
            class="request-card__btn"
            @click.stop="$emit('view-details', request)"
          >
            Подробнее
          </v-btn>
        </template>
      </div>
    </div>
  </v-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { CollectionRequest } from '@/types'

const props = defineProps<{ request: CollectionRequest }>()

defineEmits<{
  accept: [r: CollectionRequest]
  complete: [r: CollectionRequest]
  'view-details': [r: CollectionRequest]
  'view-institution': [r: CollectionRequest]
  click: []
}>()

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
  const lines = r.material_lines
  if (lines?.length) {
    return lines
      .map((l) => `${materialLabels[l.material_type] || l.material_type} ${l.amount_kg} кг`)
      .join(', ')
  }
  return r.material_type_display || r.material_type || '—'
})

const estimatedWeight = computed(() => {
  const r = props.request
  if (r.material_lines?.length) {
    return r.material_lines.reduce((s, l) => s + parseFloat(String(l.amount_kg || 0)), 0).toFixed(1)
  }
  return r.estimated_amount ?? r.paper_weight_kg ?? '—'
})

const statusLabel = computed(() => {
  const m: Record<string, string> = { new: 'Новый', accepted: 'Принят', completed: 'Завершён', cancelled: 'Отменён' }
  return m[props.request.status] || props.request.status
})

const statusColor = computed(() => {
  const m: Record<string, string> = { new: 'warning', accepted: 'info', completed: 'success', cancelled: 'grey' }
  return m[props.request.status] || 'grey'
})

const timeAgo = computed(() => {
  const d = new Date(props.request.created_at)
  const now = Date.now()
  const diff = Math.floor((now - d.getTime()) / 1000)
  if (diff < 60) return 'только что'
  if (diff < 3600) return `${Math.floor(diff / 60)} мин. назад`
  if (diff < 86400) return `${Math.floor(diff / 3600)} ч. назад`
  if (diff < 604800) return `${Math.floor(diff / 86400)} дн. назад`
  return d.toLocaleDateString('ru-RU')
})

function formatDate(s: string) {
  if (!s) return '—'
  return new Date(s).toLocaleDateString('ru-RU')
}
</script>

<style lang="scss" scoped>
.request-card {
  height: 100%;
  min-height: 220px;
  display: flex;
  flex-direction: column;
  transition: box-shadow 0.2s ease, transform 0.2s ease;
  cursor: pointer;
  border: 1px solid rgba(0, 0, 0, 0.06);

  &:hover {
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
    transform: translateY(-2px);
  }
}

.request-card__inner {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 16px;
}

.request-card__top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 12px;
  min-height: 2.5em;
}

.request-card__institution {
  font-size: 1rem;
  font-weight: 600;
  line-height: 1.3;
  margin: 0;
  color: rgb(var(--v-theme-on-surface));
  cursor: pointer;
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;

  &:hover {
    text-decoration: underline;
    color: rgb(var(--v-theme-primary));
  }
}

.request-card__badge {
  flex-shrink: 0;
}

.request-card__row {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.875rem;
  color: var(--vuvoz-text-secondary, #475569);
  margin-bottom: 4px;

  &--meta {
    gap: 12px;
    flex-wrap: wrap;
  }
}

.request-card__icon {
  color: rgb(var(--v-theme-primary));
  opacity: 0.9;
  flex-shrink: 0;
}

.request-card__material {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.request-card__date {
  font-size: 0.8125rem;
  color: var(--vuvoz-text-muted, #64748b);
}

.request-card__time {
  font-size: 0.75rem;
  color: var(--vuvoz-text-muted, #64748b);
  margin-top: 4px;
  margin-bottom: 12px;
}

.request-card__actions {
  margin-top: auto;
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding-top: 12px;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
}

.request-card__btn {
  text-transform: none;
}
</style>
