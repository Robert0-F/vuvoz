<template>
  <div>
    <v-app-bar color="primary" density="compact">
      <v-app-bar-title>Waste Paper Collection — Company</v-app-bar-title>
      <v-spacer />
      <span class="mr-2">{{ userStore.user?.username }}</span>
      <v-btn variant="text" icon="mdi-logout" @click="logout" />
    </v-app-bar>

    <v-main class="pa-4">
      <v-container fluid>
        <!-- Company info -->
        <v-card class="mb-6" variant="tonal">
          <v-card-title>Company information</v-card-title>
          <v-card-text v-if="userStore.companyProfile">
            <v-row>
              <v-col cols="12" md="6">
                <div class="text-subtitle-2 text-medium-emphasis">Company name</div>
                <div>{{ userStore.companyProfile.company_name }}</div>
              </v-col>
              <v-col cols="12" md="6">
                <div class="text-subtitle-2 text-medium-emphasis">Contact email</div>
                <div>{{ userStore.companyProfile.contact_email }}</div>
              </v-col>
              <v-col cols="12" md="6">
                <div class="text-subtitle-2 text-medium-emphasis">Phone</div>
                <div>{{ userStore.companyProfile.contact_phone }}</div>
              </v-col>
              <v-col cols="12">
                <div class="text-subtitle-2 text-medium-emphasis">Address</div>
                <div>{{ userStore.companyProfile.address }}</div>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>

        <!-- Stats -->
        <v-row class="mb-6">
          <v-col cols="12" sm="4">
            <StatsCard
              title="Total requests"
              :value="stats.totalRequests"
              icon="mdi-file-document-multiple"
              color="primary"
            />
          </v-col>
          <v-col cols="12" sm="4">
            <StatsCard
              title="Completed"
              :value="stats.completed"
              icon="mdi-check-circle"
              color="success"
            />
          </v-col>
          <v-col cols="12" sm="4">
            <StatsCard
              title="Total weight (kg)"
              :value="stats.totalWeight"
              icon="mdi-weight-kilogram"
              color="info"
            />
          </v-col>
        </v-row>

        <!-- My Institutions -->
        <v-card class="mb-6">
          <v-card-title class="d-flex align-center">
            My institutions
            <v-spacer />
            <v-btn color="primary" prepend-icon="mdi-plus" @click="showCreateModal = true">
              Add institution
            </v-btn>
          </v-card-title>
          <v-divider />
          <v-data-table
            :headers="institutionHeaders"
            :items="institutions"
            :loading="loadingInstitutions"
            item-value="id"
          >
            <template #item.actions="{ item }">
              <v-btn size="small" variant="text" @click="editInstitution(item)">Edit</v-btn>
              <v-btn size="small" variant="text" color="error" @click="confirmDelete(item)">
                Delete
              </v-btn>
            </template>
          </v-data-table>
        </v-card>

        <!-- Incoming requests -->
        <RequestTable
          title="Incoming requests"
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

    <v-dialog v-model="statusDialog" max-width="400" persistent>
      <v-card v-if="selectedRequest">
        <v-card-title>Update status</v-card-title>
        <v-card-text>
          <v-select
            v-model="statusUpdate"
            :items="statusItems"
            label="Status"
            variant="outlined"
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="statusDialog = false">Cancel</v-btn>
          <v-btn color="primary" :loading="updatingStatus" @click="saveStatus">Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="deleteDialog" max-width="400" persistent>
      <v-card>
        <v-card-title>Delete institution?</v-card-title>
        <v-card-text>
          This will delete "{{ institutionToDelete?.institution_name }}". This action cannot be undone.
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="deleteDialog = false">Cancel</v-btn>
          <v-btn color="error" :loading="deleting" @click="doDelete">Delete</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/api/axios'
import { useAuthStore } from '@/stores/auth'
import { useUserStore } from '@/stores/user'
import StatsCard from '@/components/StatsCard.vue'
import RequestTable from '@/components/RequestTable.vue'
import CreateInstitutionModal from '@/components/CreateInstitutionModal.vue'
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
const updatingStatus = ref(false)
const deleteDialog = ref(false)
const institutionToDelete = ref<InstitutionProfile | null>(null)
const deleting = ref(false)

const institutionHeaders = [
  { title: 'ID', key: 'id', width: '80' },
  { title: 'Name', key: 'institution_name' },
  { title: 'Type', key: 'institution_type' },
  { title: 'Contact', key: 'contact_person' },
  { title: 'Email', key: 'email' },
  { title: 'Actions', key: 'actions', sortable: false, width: '160' },
]

const statusItems = [
  { title: 'New', value: 'new' },
  { title: 'Accepted', value: 'accepted' },
  { title: 'Completed', value: 'completed' },
]

const stats = computed(() => {
  const total = requests.value.length
  const completed = requests.value.filter((r) => r.status === 'completed').length
  const totalWeight = requests.value.reduce(
    (sum, r) => sum + parseFloat(String(r.paper_weight_kg)),
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
  // Could open edit modal or navigate; for simplicity we skip inline edit
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
  statusDialog.value = true
}

async function saveStatus() {
  if (!selectedRequest.value) return
  updatingStatus.value = true
  try {
    await api.patch(`/collection-requests/${selectedRequest.value.id}/`, {
      status: statusUpdate.value,
    })
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
})
</script>
