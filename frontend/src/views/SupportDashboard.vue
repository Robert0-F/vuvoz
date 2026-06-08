<template>
  <div class="support-dashboard">
    <header class="support-dashboard__header">
      <div class="support-dashboard__header-inner">
        <div class="support-dashboard__brand">
          <AppHeaderLogo :height-px="34" href="/" />
          <span class="support-dashboard__brand-caption">Техподдержка</span>
        </div>
        <button type="button" class="support-dashboard__logout" @click="logout">Выйти</button>
      </div>
    </header>

    <main class="support-dashboard__main">
      <aside
        class="support-dashboard__institutions"
        :class="{ 'support-dashboard__institutions--hidden': mobileChatOpen }"
      >
        <h2 class="support-dashboard__title">Учреждения</h2>
        <v-text-field
          v-model="search"
          density="compact"
          variant="outlined"
          hide-details
          placeholder="Поиск..."
          prepend-inner-icon="mdi-magnify"
          class="mb-3"
        />
        <div v-if="loadingInstitutions" class="support-dashboard__state">Загрузка...</div>
        <div v-else-if="!filteredInstitutions.length" class="support-dashboard__state">
          {{ search ? 'Ничего не найдено' : 'Нет закреплённых учреждений.' }}
        </div>
        <button
          v-for="inst in filteredInstitutions"
          :key="inst.id"
          type="button"
          class="support-dashboard__inst-btn"
          :class="{ 'support-dashboard__inst-btn--active': selectedInstitutionId === inst.id }"
          @click="selectInstitution(inst.id)"
        >
          <span class="support-dashboard__inst-row">
            <span class="support-dashboard__inst-name">{{ inst.institution_name }}</span>
            <v-chip v-if="inst.unread_count" size="x-small" color="error" variant="flat">
              {{ inst.unread_count }}
            </v-chip>
          </span>
          <span v-if="inst.last_message_preview" class="support-dashboard__inst-preview">
            {{ inst.last_message_preview }}
          </span>
          <span class="support-dashboard__inst-meta">{{ inst.contact_person }} · {{ inst.phone }}</span>
        </button>
      </aside>

      <section
        class="support-dashboard__chat"
        :class="{ 'support-dashboard__chat--full': mobileChatOpen }"
      >
        <button
          v-if="mobileChatOpen && selectedInstitutionId"
          type="button"
          class="support-dashboard__back d-md-none"
          @click="mobileChatOpen = false"
        >
          ← К списку
        </button>

        <template v-if="selectedInstitutionId">
          <SupportChatPanel
            mode="support"
            :messages="messages"
            :loading="loadingMessages"
            :sending="sending"
            :error="chatError"
            :title="selectedInstitutionName"
            :subtitle="selectedInstitutionMeta"
            :current-user-id="userStore.user?.id ?? null"
            @send="sendMessage"
            @mark-read="markAsRead"
          />
        </template>
        <div v-else class="support-dashboard__state support-dashboard__state--center">
          Выберите учреждение, чтобы открыть чат.
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/api/axios'
import { useAuthStore } from '@/stores/auth'
import { useUserStore } from '@/stores/user'
import type { SupportAssignedInstitution, SupportChatMessage } from '@/types'
import AppHeaderLogo from '@/components/AppHeaderLogo.vue'
import SupportChatPanel from '@/components/support/SupportChatPanel.vue'

const router = useRouter()
const authStore = useAuthStore()
const userStore = useUserStore()

const institutions = ref<SupportAssignedInstitution[]>([])
const loadingInstitutions = ref(false)
const selectedInstitutionId = ref<number | null>(null)
const messages = ref<SupportChatMessage[]>([])
const loadingMessages = ref(false)
const sending = ref(false)
const chatError = ref('')
const search = ref('')
const pollTimer = ref<number | null>(null)
const mobileChatOpen = ref(false)

const filteredInstitutions = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return institutions.value
  return institutions.value.filter(
    (i) =>
      i.institution_name.toLowerCase().includes(q) ||
      i.contact_person.toLowerCase().includes(q),
  )
})

const selectedInstitution = computed(() =>
  institutions.value.find((x) => x.id === selectedInstitutionId.value),
)

const selectedInstitutionName = computed(() => selectedInstitution.value?.institution_name || 'Чат')

const selectedInstitutionMeta = computed(() => {
  const i = selectedInstitution.value
  if (!i) return ''
  return `${i.contact_person} · ${i.phone}`
})

async function loadInstitutions() {
  loadingInstitutions.value = true
  try {
    const { data } = await api.get<SupportAssignedInstitution[]>('/support/institutions/')
    institutions.value = data
    if (!selectedInstitutionId.value && data.length) {
      selectedInstitutionId.value = data[0].id
      await loadMessages()
    }
  } finally {
    loadingInstitutions.value = false
  }
}

async function loadMessages() {
  if (!selectedInstitutionId.value) return
  loadingMessages.value = true
  chatError.value = ''
  try {
    const { data } = await api.get<SupportChatMessage[]>(
      `/support/chats/${selectedInstitutionId.value}/`,
    )
    messages.value = data
  } catch {
    chatError.value = 'Не удалось загрузить сообщения'
    messages.value = []
  } finally {
    loadingMessages.value = false
  }
}

async function sendMessage(text: string) {
  if (!selectedInstitutionId.value) return
  sending.value = true
  try {
    await api.post(`/support/chats/${selectedInstitutionId.value}/`, { message: text })
    await Promise.all([loadMessages(), loadInstitutions()])
  } catch {
    chatError.value = 'Не удалось отправить сообщение'
  } finally {
    sending.value = false
  }
}

async function markAsRead() {
  if (!selectedInstitutionId.value) return
  await api.post(`/support/chats/${selectedInstitutionId.value}/read/`)
  await Promise.all([loadMessages(), loadInstitutions()])
}

async function selectInstitution(id: number) {
  selectedInstitutionId.value = id
  mobileChatOpen.value = true
  await loadMessages()
}

function startPolling() {
  stopPolling()
  pollTimer.value = window.setInterval(() => {
    if (selectedInstitutionId.value) loadMessages().catch(() => undefined)
    loadInstitutions().catch(() => undefined)
  }, 7000)
}

function stopPolling() {
  if (pollTimer.value) {
    clearInterval(pollTimer.value)
    pollTimer.value = null
  }
}

function logout() {
  authStore.logout()
  userStore.clearUser()
  router.push({ name: 'Login' })
}

onMounted(async () => {
  await loadInstitutions()
  startPolling()
})

onBeforeUnmount(stopPolling)
</script>

<style scoped lang="scss">
.support-dashboard { min-height: 100vh; background: var(--vuvoz-surface); }
.support-dashboard__header { background: var(--vuvoz-surface-elevated); border-bottom: 1px solid var(--vuvoz-border); }
.support-dashboard__header-inner {
  max-width: 1280px;
  margin: 0 auto;
  padding: 1rem 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.support-dashboard__brand {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}
.support-dashboard__brand-caption {
  font-weight: 700;
  font-size: 0.95rem;
  color: var(--vuvoz-text-muted);
}
.support-dashboard__logout {
  border: 1px solid var(--vuvoz-border);
  background: #fff;
  border-radius: 8px;
  padding: 0.5rem 0.8rem;
  cursor: pointer;
}
.support-dashboard__main {
  max-width: 1280px;
  margin: 0 auto;
  padding: 1.25rem 1.5rem;
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 1rem;
  min-height: calc(100vh - 72px);
}
.support-dashboard__institutions,
.support-dashboard__chat {
  background: var(--vuvoz-surface-elevated);
  border: 1px solid var(--vuvoz-border);
  border-radius: 12px;
  padding: 1rem;
}
.support-dashboard__title { margin: 0 0 0.75rem; font-size: 1rem; font-weight: 700; }
.support-dashboard__state {
  color: var(--vuvoz-text-muted);
  font-size: 0.9rem;
  &--center {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 300px;
  }
}
.support-dashboard__inst-btn {
  width: 100%;
  text-align: left;
  border: 1px solid var(--vuvoz-border);
  background: #fff;
  border-radius: 10px;
  padding: 0.65rem 0.75rem;
  margin-bottom: 0.5rem;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
  &:hover { border-color: var(--vuvoz-primary); }
  &--active {
    border-color: var(--vuvoz-primary);
    background: rgba(13, 148, 136, 0.06);
  }
}
.support-dashboard__inst-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}
.support-dashboard__inst-name { font-weight: 600; font-size: 0.92rem; }
.support-dashboard__inst-preview {
  display: block;
  font-size: 0.8rem;
  color: var(--vuvoz-text);
  margin-top: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.support-dashboard__inst-meta {
  display: block;
  color: var(--vuvoz-text-muted);
  font-size: 0.78rem;
  margin-top: 0.2rem;
}
.support-dashboard__back {
  border: none;
  background: transparent;
  color: var(--vuvoz-primary);
  font-weight: 600;
  margin-bottom: 0.5rem;
  cursor: pointer;
}
@media (max-width: 960px) {
  .support-dashboard__main { grid-template-columns: 1fr; }
  .support-dashboard__institutions--hidden { display: none; }
  .support-dashboard__chat--full { grid-column: 1; }
}
</style>
