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
        label="Status"
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
      <template #item.status="{ item }">
        <v-chip :color="statusColor(item.status)" size="small">
          {{ formatStatus(item.status) }}
        </v-chip>
      </template>
      <template #item.paper_weight_kg="{ item }">
        {{ item.paper_weight_kg }} kg
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
          Update status
        </v-btn>
      </template>
    </v-data-table>
  </v-card>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { CollectionRequest, RequestStatus } from '@/types'

const props = withDefaults(
  defineProps<{
    requests: CollectionRequest[]
    loading?: boolean
    title?: string
    showStatusFilter?: boolean
    showActions?: boolean
    canUpdateStatus?: boolean
  }>(),
  {
    loading: false,
    title: 'Requests',
    showStatusFilter: false,
    showActions: false,
    canUpdateStatus: false,
  }
)

defineEmits<{
  'update-status': [request: CollectionRequest]
}>()

const statusFilter = ref<string>('all')

const statusOptions = [
  { title: 'All', value: 'all' },
  { title: 'New', value: 'new' },
  { title: 'Accepted', value: 'accepted' },
  { title: 'Completed', value: 'completed' },
]

const headers = computed(() => {
  const h = [
    { title: 'ID', key: 'id', sortable: true, width: '80' },
    { title: 'Institution', key: 'institution_name' },
    { title: 'Weight (kg)', key: 'paper_weight_kg' },
    { title: 'Desired date', key: 'desired_date' },
    { title: 'Status', key: 'status' },
    { title: 'Created', key: 'created_at' },
  ]
  if (props.showActions) {
    h.push({ title: '', key: 'actions', sortable: false, width: '120' })
  }
  return h
})

const filteredRequests = computed(() => {
  if (props.showStatusFilter && statusFilter.value !== 'all') {
    return props.requests.filter((r) => r.status === statusFilter.value)
  }
  return props.requests
})

function formatStatus(s: RequestStatus) {
  const map: Record<RequestStatus, string> = {
    new: 'New',
    accepted: 'Accepted',
    completed: 'Completed',
  }
  return map[s] || s
}

function formatDate(s: string) {
  if (!s) return '—'
  return new Date(s).toLocaleDateString()
}

function statusColor(s: RequestStatus) {
  const map: Record<RequestStatus, string> = {
    new: 'info',
    accepted: 'warning',
    completed: 'success',
  }
  return map[s] || 'default'
}
</script>
