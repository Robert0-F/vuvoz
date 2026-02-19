<template>
  <v-dialog v-model="isOpen" max-width="600" persistent transition="dialog-transition" @click:outside="close">
    <v-card class="rounded-xl">
      <v-card-title>Создание организации</v-card-title>
      <v-divider />
      <v-card-text>
        <v-form ref="formRef">
          <v-text-field
            v-model="form.email"
            label="Почта (для входа в систему)"
            type="email"
            variant="outlined"
            density="comfortable"
            :error-messages="errors.email"
            class="mb-2"
          />
          <v-text-field
            v-model="form.password"
            label="Пароль (необязательно — будет сгенерирован)"
            type="password"
            variant="outlined"
            density="comfortable"
            :error-messages="errors.password"
            class="mb-2"
          />
          <v-text-field
            v-model="form.institution_name"
            label="Название учреждения"
            variant="outlined"
            density="comfortable"
            :error-messages="errors.institution_name"
            class="mb-2"
          />
          <v-text-field
            v-model="form.institution_type"
            label="Тип организации"
            variant="outlined"
            density="comfortable"
            :error-messages="errors.institution_type"
            class="mb-2"
          />
          <v-textarea
            v-model="form.address"
            label="Адрес"
            variant="outlined"
            density="comfortable"
            rows="2"
            :error-messages="errors.address"
            class="mb-2"
          />
          <v-text-field
            v-model="form.contact_person"
            label="Контактное лицо"
            variant="outlined"
            density="comfortable"
            :error-messages="errors.contact_person"
            class="mb-2"
          />
          <v-text-field
            v-model="form.phone"
            label="Номер телефона *"
            variant="outlined"
            density="comfortable"
            :error-messages="errors.phone"
            hint="Формат: +7 XXX XXX XX XX"
            persistent-hint
          />
        </v-form>
      </v-card-text>
      <v-divider />
      <v-card-actions>
        <v-spacer />
        <v-btn variant="text" @click="close">Отмена</v-btn>
        <v-btn color="primary" :loading="loading" @click="submit">Создать</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { api } from '@/api/axios'
import type { CreateInstitutionPayload } from '@/types'

const isOpen = defineModel<boolean>({ default: false })

const emit = defineEmits<{
  created: []
}>()

const form = reactive<CreateInstitutionPayload>({
  email: '',
  password: '',
  institution_name: '',
  address: '',
  contact_person: '',
  phone: '',
  institution_type: '',
})

const errors = reactive<Record<string, string>>({})
const loading = ref(false)
const formRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null)

watch(isOpen, (open) => {
  if (!open) {
    form.email = ''
    form.password = ''
    form.institution_name = ''
    form.address = ''
    form.contact_person = ''
    form.phone = ''
    form.institution_type = ''
    Object.keys(errors).forEach((k) => (errors[k] = ''))
  }
})

function close() {
  isOpen.value = false
}

function validate(): boolean {
  const required: (keyof CreateInstitutionPayload)[] = [
    'email',
    'institution_name',
    'address',
    'contact_person',
    'phone',
    'institution_type',
  ]
  let valid = true
  required.forEach((key) => {
    const val = form[key]
    if (key === 'password') return
    if (!String(val ?? '').trim()) {
      errors[key] = 'Обязательное поле'
      valid = false
    } else {
      errors[key] = ''
    }
  })
  return valid
}

async function submit() {
  if (!validate()) return
  loading.value = true
  Object.keys(errors).forEach((k) => (errors[k] = ''))
  try {
    const payload: Record<string, string> = {
      email: form.email.trim(),
      institution_name: form.institution_name.trim(),
      address: form.address.trim(),
      contact_person: form.contact_person.trim(),
      phone: form.phone.trim(),
      institution_type: form.institution_type.trim(),
    }
    if (form.password?.trim()) {
      payload.password = form.password
    }
    await api.post('/institutions/', payload)
    emit('created')
    close()
  } catch (err: unknown) {
    const ax = err as { response?: { data?: Record<string, string[]> } }
    const data = ax.response?.data
    if (data && typeof data === 'object') {
      Object.entries(data).forEach(([key, messages]) => {
        errors[key] = Array.isArray(messages) ? messages.join(' ') : String(messages)
      })
    } else {
      errors.institution_name = 'Не удалось создать организацию.'
    }
  } finally {
    loading.value = false
  }
}
</script>
