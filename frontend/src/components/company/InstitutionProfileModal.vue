<template>
  <v-dialog :model-value="modelValue" :max-width="fullscreen ? undefined : 560" :fullscreen="fullscreen" persistent scrollable @update:model-value="$emit('update:modelValue', $event)">
    <v-card v-if="institution">
      <v-card-title class="d-flex align-center py-3">
        {{ institution.institution_name }}
        <v-spacer />
        <v-btn icon variant="text" @click="$emit('update:modelValue', false)">
          <v-icon icon="mdi-close" />
        </v-btn>
      </v-card-title>
      <v-divider />
      <v-card-text class="text-body-2 pt-3">
        <p><strong>Тип:</strong> {{ institution.institution_type }}</p>
        <p><strong>Контактное лицо:</strong> {{ institution.contact_person || '—' }}</p>
        <p><strong>Телефон:</strong> {{ institution.phone || '—' }}</p>
        <p><strong>Почта:</strong> {{ institution.email || '—' }}</p>
        <p><strong>Адрес:</strong> {{ institution.address || '—' }}</p>
        <p><strong>Юр. адрес:</strong> {{ institution.legal_address || '—' }}</p>
        <p><strong>ИНН / КПП:</strong> {{ institution.inn || '—' }} / {{ institution.kpp || '—' }}</p>
        <p v-if="institution.contact_person_on_site"><strong>Контакт на площадке:</strong> {{ institution.contact_person_on_site }}</p>
        <p v-if="institution.phone_on_site"><strong>Телефон на площадке:</strong> {{ institution.phone_on_site }}</p>
        <p v-if="institution.preferred_days || institution.preferred_hours">
          <strong>Предпочтительные дни/часы:</strong> {{ institution.preferred_days || '—' }} / {{ institution.preferred_hours || '—' }}
        </p>
        <p v-if="institution.access_details"><strong>Детали доступа:</strong><br />{{ institution.access_details }}</p>
        <p v-if="institution.container_location"><strong>Расположение контейнера:</strong><br />{{ institution.container_location }}</p>
        <p v-if="institution.company_notes"><strong>Заметка компании:</strong><br />{{ institution.company_notes }}</p>
      </v-card-text>
      <v-divider />
      <v-card-actions class="py-3">
        <v-spacer />
        <v-btn color="primary" variant="tonal" @click="$emit('view-requests', institution)">
          Все заявки организации
        </v-btn>
        <v-btn variant="text" @click="$emit('update:modelValue', false)">Закрыть</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import type { InstitutionProfile } from '@/types'

defineProps<{ modelValue: boolean; institution: InstitutionProfile | null; fullscreen?: boolean }>()

defineEmits<{
  'update:modelValue': [v: boolean]
  'view-requests': [inst: InstitutionProfile]
}>()
</script>
