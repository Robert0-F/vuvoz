<template>
  <v-card>
    <v-card-title class="d-flex align-center">
      <span>{{ title }}</span>
      <v-spacer />
      <v-select
        v-if="showStatusFilter"
        v-model="statusFilter"
        :items="statusOptions"
        density="compact"
        hide-details
        label="Статус"
        variant="outlined"
        class="shrink ml-2"
        style="max-width: 160px"
      />
    </v-card-title>
    <v-divider />
    <v-data-table
      :headers="headers"
      :items="filteredRequests"
      :loading="loading"
      item-value="id"
      class="elevation-0"
    >
      <template #item.request_number="{ item }">
        {{ item.request_number || item.id }}
      </template>
      <template #item.urgency="{ item }">
        {{ formatUrgency(item.urgency) }}
      </template>
      <template #item.status="{ item }">
        <v-chip :color="statusColor(item.status)" size="small">
          {{ formatStatus(item.status) }}
        </v-chip>
      </template>
      <template #item.paper_weight_kg="{ item }">
        {{ item.estimated_amount ?? item.paper_weight_kg }} kg
      </template>
      <template #item.estimated_value="{ item }">
        {{ item.estimated_value != null ? `${item.estimated_value} руб.` : '—' }}
      </template>
      <template #item.actual_value="{ item }">
        {{ item.actual_value != null ? `${item.actual_value} руб.` : '—' }}
      </template>
      <template #item.desired_date="{ item }">
        {{ item.desired_date ? formatDate(item.desired_date) : '—' }}
      </template>
      <template #item.created_at="{ item }">
        {{ formatDate(item.created_at) }}
      </template>
      <template #item.actions="{ item }" v-if="showActions">
        <v-btn
          v-if="canUpdateStatus"
          size="small"
          variant="text"
          color="primary"
          @click="$emit('update-status', item)"
        >
          Изменить статус
        </v-btn>
      </template>
    </v-data-table>
  </v-card>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { CollectionRequest, RequestStatus, Urgency } from '@/types'

const props = withDefaults(
  defineProps<{
    requests: CollectionRequest[]
    loading?: boolean
    title?: string
    showStatusFilter?: boolean
    showActions?: boolean
    canUpdateStatus?: boolean
    hideUrgency?: boolean
  }>(),
  {
    loading: false,
    title: 'Requests',
    showStatusFilter: false,
    showActions: false,
    canUpdateStatus: false,
    hideUrgency: false,
  }
)

defineEmits<{
  'update-status': [request: CollectionRequest]
}>()

const statusFilter = ref<string>('all')

const statusOptions = [
  { title: 'Все', value: 'all' },
  { title: 'Новые', value: 'new' },
  { title: 'Принятые', value: 'accepted' },
  { title: 'Завершеные', value: 'completed' },
]

const headers = computed(() => {
  const h = [
    { title: 'Номер', key: 'request_number', sortable: true, width: '140' },
    { title: 'Организация', key: 'institution_name' },
    { title: 'Тип макулатуры', key: 'material_type_display', width: '120' },
    ...(props.hideUrgency ? [] : [{ title: 'Срочность', key: 'urgency', sortable: true, width: '100' }]),
    { title: 'Вес (кг)', key: 'paper_weight_kg' },
    { title: 'Ориент. стоимость', key: 'estimated_value', width: '120' },
    { title: 'Факт. стоимость', key: 'actual_value', width: '120' },
    { title: 'Желаемая дата', key: 'desired_date' },
    { title: 'Статус', key: 'status' },
    { title: 'Дата создания', key: 'created_at' },
  ]
  if (props.showActions) {
    h.push({ title: 'Действия', key: 'actions', sortable: false, width: '140' })
  }
  return h
})

const filteredRequests = computed(() => {
  if (props.showStatusFilter && statusFilter.value !== 'all') {
    return props.requests.filter((r) => r.status === statusFilter.value)
  }
  return props.requests
})

function formatUrgency(u?: Urgency) {
  const map: Record<string, string> = { low: 'Низкая', medium: 'Средняя', high: 'Высокая' }
  return u ? map[u] || u : '—'
}

function formatStatus(s: RequestStatus) {
  const map: Record<RequestStatus, string> = {
    new: 'Новый',
    accepted: 'Принят',
    completed: 'Завершён',
  }
  return map[s] || s
}

function formatDate(s: string) {
  if (!s) return '—'
  return new Date(s).toLocaleDateString()
}

function statusColor(s: RequestStatus) {
  const map: Record<RequestStatus, string> = {
    new: 'warning',
    accepted: 'info',
    completed: 'success',
  }
  return map[s] || 'default'
}
</script>
