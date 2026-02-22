<template>
  <div class="inst-notifications" :class="{ 'inst-notifications--collapsed': collapsed }">
    <button
      type="button"
      class="inst-notifications__toggle"
      :aria-expanded="!collapsed"
      aria-label="Уведомления"
      @click="collapsed = !collapsed"
    >
      <v-icon icon="mdi-bell-outline" size="24" />
      <span v-if="unreadCount > 0" class="inst-notifications__badge">{{ unreadCount }}</span>
    </button>
    <div v-show="!collapsed" class="inst-notifications__panel">
      <div class="inst-notifications__header">
        <h4 class="inst-notifications__title">Уведомления</h4>
        <button
          v-if="items.length"
          type="button"
          class="inst-notifications__read-all"
          @click="$emit('mark-all-read')"
        >
          Прочитать все
        </button>
      </div>
      <div class="inst-notifications__list">
        <div
          v-for="n in items"
          :key="n.id"
          class="inst-notifications__item"
          :class="{ 'inst-notifications__item--unread': !n.read }"
          @click="$emit('mark-read', n.id)"
        >
          <div class="inst-notifications__item-title">{{ n.title }}</div>
          <div class="inst-notifications__item-message">{{ n.message }}</div>
        </div>
        <div v-if="!items.length" class="inst-notifications__empty">
          Нет уведомлений
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

defineProps<{
  items: { id: number; title: string; message: string; read: boolean }[]
  unreadCount: number
}>()

defineEmits<{
  'mark-read': [id: number]
  'mark-all-read': []
}>()

const collapsed = ref(true)
</script>

<style scoped lang="scss">
.inst-notifications {
  position: relative;
}

.inst-notifications__toggle {
  position: relative;
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  border-radius: var(--vuvoz-radius-sm);
  color: var(--vuvoz-text);
  cursor: pointer;
  transition: background 0.2s;
  &:hover {
    background: rgba(13, 148, 136, 0.08);
  }
}

.inst-notifications__badge {
  position: absolute;
  top: 4px;
  right: 4px;
  min-width: 18px;
  height: 18px;
  padding: 0 4px;
  border-radius: 9999px;
  background: #dc2626;
  color: #fff;
  font-size: 0.7rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.inst-notifications__panel {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 0.5rem;
  width: 320px;
  max-height: 400px;
  background: var(--vuvoz-surface-elevated);
  border-radius: var(--vuvoz-radius-lg);
  border: 1px solid var(--vuvoz-border);
  box-shadow: var(--vuvoz-shadow-xl);
  overflow: hidden;
  z-index: 100;
}

.inst-notifications__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--vuvoz-border);
}

.inst-notifications__title {
  font-size: 1rem;
  font-weight: 600;
  margin: 0;
  color: var(--vuvoz-text);
}

.inst-notifications__read-all {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--vuvoz-primary);
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  &:hover { text-decoration: underline; }
}

.inst-notifications__list {
  max-height: 320px;
  overflow-y: auto;
}

.inst-notifications__item {
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--vuvoz-border);
  cursor: pointer;
  transition: background 0.2s;
  &:last-child { border-bottom: none; }
  &:hover {
    background: var(--vuvoz-surface-muted);
  }
  &--unread {
    background: rgba(13, 148, 136, 0.04);
  }
}

.inst-notifications__item-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--vuvoz-text);
  margin-bottom: 0.25rem;
}

.inst-notifications__item-message {
  font-size: 0.85rem;
  color: var(--vuvoz-text-secondary);
  line-height: 1.4;
}

.inst-notifications__empty {
  padding: 2rem;
  text-align: center;
  font-size: 0.9rem;
  color: var(--vuvoz-text-muted);
}
</style>
