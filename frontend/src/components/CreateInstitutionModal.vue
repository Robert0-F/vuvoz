<template>
  <v-dialog v-model="isOpen" max-width="600" persistent @click:outside="close">
    <v-card>
      <v-card-title>Create new institution</v-card-title>
      <v-divider />
      <v-card-text>
        <v-form ref="formRef">
          <v-text-field
            v-model="form.username"
            label="Username (for institution login)"
            variant="outlined"
            density="comfortable"
            :error-messages="errors.username"
            class="mb-2"
          />
          <v-text-field
            v-model="form.password"
            label="Password"
            type="password"
            variant="outlined"
            density="comfortable"
            :error-messages="errors.password"
            class="mb-2"
          />
          <v-text-field
            v-model="form.institution_name"
            label="Institution name"
            variant="outlined"
            density="comfortable"
            :error-messages="errors.institution_name"
            class="mb-2"
          />
          <v-text-field
            v-model="form.institution_type"
            label="Institution type"
            variant="outlined"
            density="comfortable"
            :error-messages="errors.institution_type"
            class="mb-2"
          />
          <v-textarea
            v-model="form.address"
            label="Address"
            variant="outlined"
            density="comfortable"
            rows="2"
            :error-messages="errors.address"
            class="mb-2"
          />
          <v-text-field
            v-model="form.contact_person"
            label="Contact person"
            variant="outlined"
            density="comfortable"
            :error-messages="errors.contact_person"
            class="mb-2"
          />
          <v-text-field
            v-model="form.phone"
            label="Phone"
            variant="outlined"
            density="comfortable"
            :error-messages="errors.phone"
            class="mb-2"
          />
          <v-text-field
            v-model="form.email"
            label="Email"
            type="email"
            variant="outlined"
            density="comfortable"
            :error-messages="errors.email"
          />
        </v-form>
      </v-card-text>
      <v-divider />
      <v-card-actions>
        <v-spacer />
        <v-btn variant="text" @click="close">Cancel</v-btn>
        <v-btn color="primary" :loading="loading" @click="submit">Create</v-btn>
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
  username: '',
  password: '',
  institution_name: '',
  address: '',
  contact_person: '',
  phone: '',
  email: '',
  institution_type: '',
})

const errors = reactive<Record<string, string>>({})
const loading = ref(false)
const formRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null)

watch(isOpen, (open) => {
  if (!open) {
    Object.keys(form).forEach((k) => ((form as Record<string, string>)[k] = ''))
    Object.keys(errors).forEach((k) => (errors[k] = ''))
  }
})

function close() {
  isOpen.value = false
}

function validate(): boolean {
  const required: (keyof CreateInstitutionPayload)[] = [
    'username',
    'password',
    'institution_name',
    'address',
    'contact_person',
    'phone',
    'email',
    'institution_type',
  ]
  let valid = true
  required.forEach((key) => {
    if (!String((form as Record<string, string>)[key] || '').trim()) {
      errors[key] = 'This field is required'
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
    await api.post('/institutions/', form)
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
      errors.institution_name = 'Failed to create institution.'
    }
  } finally {
    loading.value = false
  }
}
</script>
