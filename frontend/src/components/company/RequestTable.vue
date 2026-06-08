<template>
  <v-card class="request-table-card" elevation="0" rounded="lg" border>
    <v-card-title class="d-flex flex-wrap align-center ga-2 py-3">
      <span>Все заявки</span>
      <v-chip v-if="props.institutionIdFilter != null" color="primary" variant="tonal" size="small" class="mr-2" closable @click:close="$emit('clear-institution-filter')">
        Фильтр по организации
      </v-chip>
      <v-spacer />
      <v-select
        v-model="statusFilter"
        :items="statusFilterItems"
        item-title="title"
        item-value="value"
        density="compact"
        hide-details
        label="Статус"
        variant="outlined"
        style="max-width: 160px"
      />
      <v-text-field
        v-model="search"
        placeholder="Поиск по организации..."
        density="compact"
        hide-details
        clearable
        variant="outlined"
        style="max-width: 220px"
        prepend-inner-icon="mdi-magnify"
      />
    </v-card-title>
    <v-divider />
    <div class="overflow-x-auto">
      <v-data-table
        :headers="headers"
        :items="filteredItems"
        :loading="loading"
        item-value="id"
        class="request-table"
        :mobile-breakpoint="600"
      >
        <template #item.request_number="{ item }">
          {{ item.request_number || item.id }}
        </template>
        <template #item.institution_name="{ item }">
          <a href="javascript:void(0)" class="request-table__link" @click="$emit('view-institution', item)">
            {{ item.institution_name }}
          </a>
        </template>
        <template #item.material_display="{ item }">
          {{ formatMaterial(item) }}
        </template>
        <template #item.estimated_amount="{ item }">
          {{ item.estimated_amount ?? item.paper_weight_kg ?? '—' }}
        </template>
        <template #item.actual_amount="{ item }">
          {{ item.actual_amount ?? '—' }}
        </template>
        <template #item.status="{ item }">
          <v-chip :color="statusColor(item.status)" size="small" variant="tonal">
            {{ statusLabel(item.status) }}
          </v-chip>
        </template>
        <template #item.created_at="{ item }">
          {{ formatDate(item.created_at) }}
        </template>
        <template #item.desired_date="{ item }">
          {{ item.desired_date ? formatDate(item.desired_date) : '—' }}
        </template>
        <template #item.actions="{ item }">
          <v-btn size="small" variant="text" @click="$emit('view-details', item)">
            Подробнее
          </v-btn>
          <v-btn
            v-if="item.status === 'new'"
            size="small"
            variant="text"
            color="primary"
            @click="$emit('accept', item)"
          >
            Принять
          </v-btn>
          <v-btn
            v-if="item.status === 'accepted'"
            size="small"
            variant="text"
            color="success"
            @click="$emit('complete', item)"
          >
            Завершить
          </v-btn>
        </template>
      </v-data-table>
    </div>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { CollectionRequest } from '@/types'

const props = withDefaults(
  defineProps<{ requests: CollectionRequest[]; loading?: boolean; institutionIdFilter?: number | null }>(),
  { loading: false, institutionIdFilter: null }
)

const emit = defineEmits<{
  'view-details': [r: CollectionRequest]
  'view-institution': [r: CollectionRequest]
  accept: [r: CollectionRequest]
  complete: [r: CollectionRequest]
  'clear-institution-filter': []
}>()

const statusFilter = ref('all')
const search = ref('')

const statusFilterItems = [
  { title: 'Все', value: 'all' },
  { title: 'Новые', value: 'new' },
  { title: 'Принятые', value: 'accepted' },
  { title: 'Ожидают подтверждения', value: 'pending_confirmation' },
  { title: 'Завершённые', value: 'completed' },
]

const headers = [
  { title: 'Номер', key: 'request_number', width: '130', sortable: true },
  { title: 'Организация', key: 'institution_name', sortable: true },
  { title: 'Материал', key: 'material_display', sortable: false },
  { title: 'Вес (кг)', key: 'estimated_amount', width: '100' },
  { title: 'Факт. вес', key: 'actual_amount', width: '100' },
  { title: 'Статус', key: 'status', width: '120' },
  { title: 'Создана', key: 'created_at', width: '110' },
  { title: 'Желаемая дата', key: 'desired_date', width: '120' },
  { title: 'Действия', key: 'actions', sortable: false, width: '180' },
]

const filteredItems = computed(() => {
  let list = props.requests
  if (props.institutionIdFilter != null) list = list.filter((r) => r.institution === props.institutionIdFilter)
  if (statusFilter.value !== 'all') list = list.filter((r) => r.status === statusFilter.value)
  const q = (search.value || '').trim().toLowerCase()
  if (q) list = list.filter((r) => (r.institution_name || '').toLowerCase().includes(q))
  return list
})

function formatMaterial(item: CollectionRequest) {
  const lines = item.material_lines
  const labels: Record<string, string> = {
    cardboard: 'Картон',
    paper: 'Макулатура',
    canisters: 'Канистры/флаконы',
    polyethylene: 'Полиэтилен/стрейч пленка',
    metal: 'Металл бытовой',
    glass: 'Стекло (бутылки)',
  }
  if (lines?.length) {
    return lines.map((l) => `${labels[l.material_type] || l.material_type} ${l.amount_kg} кг`).join(', ')
  }
  return item.material_type_display || item.material_type || '—'
}

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
  return new Date(s).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short', year: 'numeric' })
}
</script>

<style lang="scss" scoped>
.request-table__link {
  color: rgb(var(--v-theme-primary));
  text-decoration: none;
  &:hover { text-decoration: underline; }
}
</style>
