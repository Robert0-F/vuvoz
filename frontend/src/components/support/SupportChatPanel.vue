<template>
  <div class="support-chat-panel">
    <div v-if="!supportAssigned && mode === 'institution'" class="support-chat-panel__alert">
      <v-icon icon="mdi-headset" size="28" color="warning" class="mb-2" />
      <p>Специалист техподдержки пока не назначен администратором.</p>
      <p class="text-caption">Когда поддержка будет подключена, вы сможете написать сюда.</p>
    </div>

    <template v-else>
      <header v-if="title" class="support-chat-panel__head">
        <div>
          <h3 class="support-chat-panel__title">{{ title }}</h3>
          <p v-if="subtitle" class="support-chat-panel__subtitle">{{ subtitle }}</p>
        </div>
        <v-btn
          v-if="showMarkRead"
          size="small"
          variant="tonal"
          @click="$emit('mark-read')"
        >
          Прочитано
        </v-btn>
      </header>

      <div v-if="loading && !messages.length" class="support-chat-panel__state">
        <v-progress-circular indeterminate color="primary" size="36" />
      </div>

      <v-alert v-if="error" type="error" variant="tonal" density="compact" class="mb-3">
        {{ error }}
      </v-alert>

      <div v-if="!loading || messages.length" ref="messagesRef" class="support-chat-panel__messages">
        <template v-for="group in messageGroups" :key="group.label">
          <div class="support-chat-panel__date">{{ group.label }}</div>
          <div
            v-for="msg in group.items"
            :key="msg.id"
            class="support-chat-panel__bubble"
            :class="{ 'support-chat-panel__bubble--mine': isMine(msg) }"
          >
            <p v-if="!isMine(msg)" class="support-chat-panel__author">
              {{ msg.sender_username }}
            </p>
            <p class="support-chat-panel__text">{{ msg.message }}</p>
            <p class="support-chat-panel__time">{{ formatTime(msg.created_at) }}</p>
          </div>
        </template>
        <p v-if="!messages.length" class="support-chat-panel__empty">
          Напишите первое сообщение — мы ответим в рабочее время.
        </p>
      </div>

      <form class="support-chat-panel__composer" @submit.prevent="submit">
        <v-textarea
          v-model="draft"
          variant="outlined"
          density="comfortable"
          rows="2"
          auto-grow
          maxlength="4000"
          hide-details
          :placeholder="placeholder"
          :disabled="sending || disabled"
          @keydown.enter.exact.prevent="submit"
        />
        <div class="support-chat-panel__composer-actions">
          <span class="support-chat-panel__hint">Enter — отправить, Shift+Enter — новая строка</span>
          <v-btn
            color="primary"
            :loading="sending"
            :disabled="disabled || !draft.trim()"
            type="submit"
          >
            Отправить
          </v-btn>
        </div>
      </form>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import type { SupportChatMessage } from '@/types'

const props = withDefaults(
  defineProps<{
    mode: 'institution' | 'support'
    messages: SupportChatMessage[]
    loading?: boolean
    sending?: boolean
    error?: string
    title?: string
    subtitle?: string
    supportAssigned?: boolean
    showMarkRead?: boolean
    disabled?: boolean
    currentUserId?: number | null
    placeholder?: string
  }>(),
  {
    loading: false,
    sending: false,
    error: '',
    supportAssigned: true,
    showMarkRead: true,
    disabled: false,
    placeholder: 'Введите сообщение...',
  },
)

const emit = defineEmits<{
  send: [text: string]
  'mark-read': []
}>()

const draft = ref('')
const messagesRef = ref<HTMLElement | null>(null)

function isMine(msg: SupportChatMessage) {
  if (typeof msg.is_mine === 'boolean') return msg.is_mine
  if (props.currentUserId) return msg.sender === props.currentUserId
  return false
}

function formatTime(iso: string) {
  return new Date(iso).toLocaleString('ru-RU', { dateStyle: 'short', timeStyle: 'short' })
}

function dateLabel(iso: string) {
  const d = new Date(iso)
  const today = new Date()
  const yesterday = new Date(today)
  yesterday.setDate(today.getDate() - 1)
  const sameDay = (a: Date, b: Date) =>
    a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth() && a.getDate() === b.getDate()
  if (sameDay(d, today)) return 'Сегодня'
  if (sameDay(d, yesterday)) return 'Вчера'
  return d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' })
}

const messageGroups = computed(() => {
  const groups: { label: string; items: SupportChatMessage[] }[] = []
  let currentLabel = ''
  for (const msg of props.messages) {
    const label = dateLabel(msg.created_at)
    if (label !== currentLabel) {
      groups.push({ label, items: [msg] })
      currentLabel = label
    } else {
      groups[groups.length - 1].items.push(msg)
    }
  }
  return groups
})

function scrollToBottom() {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}

function submit() {
  const text = draft.value.trim()
  if (!text || props.sending || props.disabled) return
  emit('send', text)
  draft.value = ''
}

watch(() => props.messages.length, scrollToBottom)
watch(() => props.loading, (v) => { if (!v) scrollToBottom() })

defineExpose({ scrollToBottom })
</script>

<style scoped lang="scss">
.support-chat-panel {
  display: flex;
  flex-direction: column;
  min-height: 420px;
}

.support-chat-panel__alert {
  text-align: center;
  padding: 2.5rem 1rem;
  color: var(--vuvoz-text-muted);
  background: var(--vuvoz-surface-muted);
  border-radius: var(--vuvoz-radius-lg);
  border: 1px dashed var(--vuvoz-border);
}

.support-chat-panel__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.75rem;
}

.support-chat-panel__title {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 700;
}

.support-chat-panel__subtitle {
  margin: 0.2rem 0 0;
  font-size: 0.85rem;
  color: var(--vuvoz-text-muted);
}

.support-chat-panel__state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
}

.support-chat-panel__messages {
  flex: 1;
  min-height: 280px;
  max-height: 52vh;
  overflow-y: auto;
  padding: 0.75rem;
  background: var(--vuvoz-surface-muted);
  border-radius: var(--vuvoz-radius-lg);
  border: 1px solid var(--vuvoz-border);
  margin-bottom: 0.75rem;
}

.support-chat-panel__date {
  text-align: center;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--vuvoz-text-muted);
  margin: 0.75rem 0 0.5rem;
}

.support-chat-panel__bubble {
  max-width: 82%;
  margin-bottom: 0.5rem;
  padding: 0.55rem 0.75rem;
  border-radius: 14px 14px 14px 4px;
  background: #fff;
  border: 1px solid var(--vuvoz-border);
  box-shadow: var(--vuvoz-shadow-sm);

  &--mine {
    margin-left: auto;
    border-radius: 14px 14px 4px 14px;
    background: rgba(13, 148, 136, 0.1);
    border-color: rgba(13, 148, 136, 0.25);
  }
}

.support-chat-panel__author {
  margin: 0 0 0.15rem;
  font-size: 0.72rem;
  font-weight: 600;
  color: var(--vuvoz-primary);
}

.support-chat-panel__text {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 0.92rem;
  line-height: 1.45;
}

.support-chat-panel__time {
  margin: 0.3rem 0 0;
  font-size: 0.7rem;
  color: var(--vuvoz-text-muted);
  text-align: right;
}

.support-chat-panel__empty {
  text-align: center;
  color: var(--vuvoz-text-muted);
  padding: 2rem 1rem;
  margin: 0;
}

.support-chat-panel__composer-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin-top: 0.5rem;
  flex-wrap: wrap;
}

.support-chat-panel__hint {
  font-size: 0.75rem;
  color: var(--vuvoz-text-muted);
}

@media (max-width: 600px) {
  .support-chat-panel__hint { display: none; }
  .support-chat-panel__messages { max-height: 45vh; }
}
</style>
