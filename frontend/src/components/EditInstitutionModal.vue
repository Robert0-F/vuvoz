<template>
  <v-dialog v-model="isOpen" max-width="600" persistent @click:outside="close">
    <v-card>
      <v-card-title>{{ companyEditOnly ? 'Дополнительная информация (адрес, контакты, заметка)' : 'Редактирование организации' }}</v-card-title>
      <v-divider />
      <v-card-text>
        <v-form ref="formRef">
          <template v-if="companyEditOnly">
            <p class="text-body-2 text-medium-emphasis mb-2">{{ form.institution_name }} ({{ form.institution_type }})</p>
            <v-textarea
              v-model="form.address"
              label="Адрес *"
              variant="outlined"
              density="comfortable"
              rows="2"
              :error-messages="errors.address"
              class="mb-2"
            />
            <v-text-field
              v-model="form.contact_person"
              label="Контактное лицо *"
              variant="outlined"
              density="comfortable"
              :error-messages="errors.contact_person"
              class="mb-2"
            />
            <v-text-field
              v-model="form.phone"
              label="Номер телефона *"
              hint="Формат: 7 XXX XXX XX XX или +7 XXX XXX XX XX"
              persistent-hint
              variant="outlined"
              density="comfortable"
              :error-messages="errors.phone"
              class="mb-2"
            />
            <v-text-field
              v-model="form.email"
              label="Почта (логин для входа) *"
              type="email"
              variant="outlined"
              density="comfortable"
              :error-messages="errors.email"
              class="mb-2"
            />
            <v-textarea
              v-model="form.company_notes"
              label="Заметка компании (новый комментарий)"
              variant="outlined"
              rows="2"
              placeholder="Дополнительная заметка об организации"
              :error-messages="errors.company_notes"
            />
          </template>
          <template v-else>
            <v-text-field v-model="form.institution_name" label="Название учреждения" variant="outlined" density="comfortable" :error-messages="errors.institution_name" class="mb-2" />
            <v-text-field v-model="form.institution_type" label="Тип организации" variant="outlined" density="comfortable" :error-messages="errors.institution_type" class="mb-2" />
            <v-textarea v-model="form.address" label="Адрес" variant="outlined" density="comfortable" rows="2" :error-messages="errors.address" class="mb-2" />
            <v-text-field v-model="form.contact_person" label="Контактное лицо" variant="outlined" density="comfortable" :error-messages="errors.contact_person" class="mb-2" />
            <v-text-field v-model="form.phone" label="Номер телефона *" hint="Формат: +7 XXX XXX XX XX" persistent-hint variant="outlined" density="comfortable" :error-messages="errors.phone" class="mb-2" />
            <v-text-field v-model="form.email" label="Почта (для входа)" type="email" variant="outlined" density="comfortable" :error-messages="errors.email" />
          </template>
        </v-form>
      </v-card-text>
      <v-divider />
      <v-card-actions>
        <v-spacer />
        <v-btn variant="text" @click="close">Отмена</v-btn>
        <v-btn color="primary" :loading="loading" @click="submit">Сохранить</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { api } from '@/api/axios'
import type { InstitutionProfile } from '@/types'

const isOpen = defineModel<boolean>({ default: false })

const props = withDefaults(
  defineProps<{
    institution: InstitutionProfile | null
    companyEditOnly?: boolean
  }>(),
  { companyEditOnly: false }
)

const emit = defineEmits<{
  saved: []
}>()

const form = reactive({
  institution_name: '',
  institution_type: '',
  address: '',
  contact_person: '',
  phone: '',
  email: '',
  company_notes: '',
})

const errors = reactive<Record<string, string>>({})
const loading = ref(false)
const formRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null)

function assignForm(inst: InstitutionProfile | null) {
  if (!inst) return
  form.institution_name = inst.institution_name ?? ''
  form.institution_type = inst.institution_type ?? ''
  form.address = inst.address ?? ''
  form.contact_person = inst.contact_person ?? ''
  form.phone = inst.phone ?? ''
  form.email = inst.email ?? ''
  form.company_notes = (inst as InstitutionProfile & { company_notes?: string }).company_notes ?? ''
  Object.keys(errors).forEach((k) => (errors[k] = ''))
}

watch(
  () => props.institution,
  (inst) => assignForm(inst ?? null),
  { immediate: true }
)

watch(isOpen, (open) => {
  if (open && props.institution) assignForm(props.institution)
})

function close() {
  isOpen.value = false
}

function validate(): boolean {
  const required = props.companyEditOnly
    ? (['address', 'contact_person', 'phone', 'email'] as const)
    : (['institution_name', 'institution_type', 'address', 'contact_person', 'phone', 'email'] as const)
  let valid = true
  required.forEach((key) => {
    if (!String(form[key] ?? '').trim()) {
      errors[key] = 'Обязательное поле'
      valid = false
    } else {
      errors[key] = ''
    }
  })
  return valid
}

async function submit() {
  if (!props.institution) return
  if (!validate()) return
  loading.value = true
  Object.keys(errors).forEach((k) => (errors[k] = ''))
  try {
    if (props.companyEditOnly) {
      await api.patch(`/institutions/${props.institution.id}/`, {
        address: form.address.trim(),
        contact_person: form.contact_person.trim(),
        phone: form.phone.trim(),
        email: form.email.trim(),
        company_notes: form.company_notes?.trim() ?? '',
      })
    } else {
      await api.patch(`/institutions/${props.institution.id}/`, {
        institution_name: form.institution_name.trim(),
        institution_type: form.institution_type.trim(),
        address: form.address.trim(),
        contact_person: form.contact_person.trim(),
        phone: form.phone.trim(),
        email: form.email.trim(),
      })
    }
    emit('saved')
    close()
  } catch (err: unknown) {
    const ax = err as { response?: { data?: Record<string, string[]> } }
    const data = ax.response?.data
    if (data && typeof data === 'object') {
      Object.entries(data).forEach(([key, messages]) => {
        errors[key] = Array.isArray(messages) ? messages.join(' ') : String(messages)
      })
    } else {
      errors.address = 'Не удалось сохранить.'
    }
  } finally {
    loading.value = false
  }
}
</script>
