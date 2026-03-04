<template>
  <v-card class="institution-card" elevation="0" rounded="lg" border @click="$emit('click')">
    <div class="institution-card__body">
      <div class="institution-card__icon">
        <v-icon icon="mdi-domain" size="28" />
      </div>
      <div class="institution-card__main">
        <div class="institution-card__name">{{ institution.institution_name }}</div>
        <div class="institution-card__meta">
          <span class="institution-card__type">{{ institution.institution_type }}</span>
          <span v-if="institution.contact_person" class="institution-card__contact">
            {{ institution.contact_person }}
          </span>
        </div>
        <div v-if="requestCount !== undefined" class="institution-card__stats">
          Заявок: {{ requestCount }}
          <span v-if="formattedLastRequest" class="institution-card__last">
            · Последняя: {{ formattedLastRequest }}
          </span>
        </div>
      </div>
      <v-icon icon="mdi-chevron-right" class="institution-card__chevron" />
    </div>
  </v-card>
</template>

<script setup lang="ts">
import type { InstitutionProfile } from '@/types'
import { computed } from 'vue'

const props = defineProps<{
  institution: InstitutionProfile
  requestCount?: number
  lastRequestDate?: string
}>()

defineEmits<{ click: [] }>()

const formattedLastRequest = computed(() => {
  const d = props.lastRequestDate
  if (!d) return ''
  return new Date(d).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short', year: 'numeric' })
})
</script>

<style lang="scss" scoped>
.institution-card {
  cursor: pointer;
  transition: box-shadow 0.2s ease, transform 0.2s ease;
  &:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    transform: translateY(-1px);
  }
}
.institution-card__body {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px;
}
.institution-card__icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: rgba(13, 148, 136, 0.1);
  color: rgb(var(--v-theme-primary));
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.institution-card__main { flex: 1; min-width: 0; }
.institution-card__name { font-weight: 600; font-size: 1rem; margin-bottom: 4px; }
.institution-card__meta { font-size: 0.875rem; color: #64748b; }
.institution-card__stats { font-size: 0.8rem; margin-top: 6px; color: #64748b; }
.institution-card__chevron { color: #94a3b8; flex-shrink: 0; }
</style>
