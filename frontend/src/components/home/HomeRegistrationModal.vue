<template>
  <Teleport to="body">
    <div v-if="modelValue" class="home-reg__backdrop" @click.self="close">
      <div class="home-reg__modal">
        <div class="home-reg__head">
          <h2 class="home-reg__title">Регистрация на «Зелёный счёт»</h2>
          <button type="button" class="home-reg__close" aria-label="Закрыть" @click="close">×</button>
        </div>

        <div class="home-reg__type-tabs">
          <button
            type="button"
            class="home-reg__type-tab"
            :class="{ 'home-reg__type-tab--active': regType === 'institution' }"
            @click="regType = 'institution'"
          >
            Учреждение
          </button>
          <button
            type="button"
            class="home-reg__type-tab"
            :class="{ 'home-reg__type-tab--active': regType === 'company' }"
            @click="regType = 'company'"
          >
            Компания (вывоз)
          </button>
        </div>

        <div class="home-reg__benefits">
          <h3 class="home-reg__benefits-title">Что вы получаете</h3>
          <ul v-if="regType === 'institution'" class="home-reg__benefits-list">
            <li>Регулярный вывоз вторсырья по вашему графику</li>
            <li>Прозрачное взвешивание и учёт на «зелёном счёте»</li>
            <li>Зелёные баллы за сдачу — тратьте в каталоге наград</li>
            <li>Документы для отчётности и личный кабинет</li>
            <li>Уведомления о статусе заявок</li>
          </ul>
          <ul v-else class="home-reg__benefits-list">
            <li>Заявки от организаций на вывоз вторсырья</li>
            <li>Учёт вывозов, веса и выплат в одной системе</li>
            <li>Привязка учреждений к вашей компании</li>
            <li>Статистика по месяцам и материалам</li>
            <li>Поддержка администратора платформы при подключении</li>
          </ul>
        </div>

        <form v-if="regType === 'institution'" class="home-reg__form" @submit.prevent="submitInstitution">
          <input v-model="instForm.first_name" type="text" class="home-reg__input" placeholder="Имя *" required />
          <input v-model="instForm.patronymic" type="text" class="home-reg__input" placeholder="Отчество" />
          <input v-model="instForm.institution_name" type="text" class="home-reg__input" placeholder="Название учреждения *" required />
          <textarea v-model="instForm.address" class="home-reg__input home-reg__textarea" placeholder="Адрес *" rows="2" required />
          <input v-model="instForm.phone" type="tel" class="home-reg__input" placeholder="Телефон *" required />
          <input v-model="instForm.email" type="email" class="home-reg__input" placeholder="Email *" required />
          <label class="home-reg__consent">
            <input v-model="consent" type="checkbox" required />
            <span>Согласен на обработку персональных данных</span>
          </label>
          <p v-if="error" class="home-reg__error">Не удалось отправить. Попробуйте позже.</p>
          <div class="home-reg__actions">
            <button type="button" class="home-reg__btn home-reg__btn--secondary" @click="close">Отмена</button>
            <button type="submit" class="home-reg__btn home-reg__btn--primary" :disabled="sending">
              {{ sending ? 'Отправка…' : 'Отправить заявку' }}
            </button>
          </div>
        </form>

        <form v-else class="home-reg__form" @submit.prevent="submitCompany">
          <input v-model="coForm.company_name" type="text" class="home-reg__input" placeholder="Название компании *" required />
          <input v-model="coForm.contact_name" type="text" class="home-reg__input" placeholder="Контактное лицо *" required />
          <input v-model="coForm.phone" type="tel" class="home-reg__input" placeholder="Телефон *" required />
          <input v-model="coForm.email" type="email" class="home-reg__input" placeholder="Email" />
          <textarea v-model="coForm.address" class="home-reg__input home-reg__textarea" placeholder="Регион / адрес базы" rows="2" />
          <textarea v-model="coForm.comment" class="home-reg__input home-reg__textarea" placeholder="Парк техники, лицензии (опционально)" rows="2" />
          <label class="home-reg__consent">
            <input v-model="consent" type="checkbox" required />
            <span>Согласен на обработку персональных данных</span>
          </label>
          <p v-if="error" class="home-reg__error">Не удалось отправить. Попробуйте позже.</p>
          <div class="home-reg__actions">
            <button type="button" class="home-reg__btn home-reg__btn--secondary" @click="close">Отмена</button>
            <button type="submit" class="home-reg__btn home-reg__btn--primary" :disabled="sending">
              {{ sending ? 'Отправка…' : 'Отправить заявку' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { api } from '@/api/axios'

const props = defineProps<{ modelValue: boolean }>()
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  success: []
}>()

const regType = ref<'institution' | 'company'>('institution')
const sending = ref(false)
const error = ref(false)
const consent = ref(false)

const instForm = reactive({
  first_name: '',
  patronymic: '',
  institution_name: '',
  address: '',
  phone: '',
  email: '',
})

const coForm = reactive({
  company_name: '',
  contact_name: '',
  phone: '',
  email: '',
  address: '',
  comment: '',
})

function resetForms() {
  instForm.first_name = ''
  instForm.patronymic = ''
  instForm.institution_name = ''
  instForm.address = ''
  instForm.phone = ''
  instForm.email = ''
  coForm.company_name = ''
  coForm.contact_name = ''
  coForm.phone = ''
  coForm.email = ''
  coForm.address = ''
  coForm.comment = ''
  consent.value = false
  error.value = false
}

function close() {
  emit('update:modelValue', false)
}

watch(() => props.modelValue, (open) => {
  if (open) resetForms()
})

async function submitInstitution() {
  sending.value = true
  error.value = false
  try {
    await api.post('/registration-requests/', {
      first_name: instForm.first_name.trim(),
      patronymic: instForm.patronymic.trim(),
      institution_name: instForm.institution_name.trim(),
      address: instForm.address.trim(),
      phone: instForm.phone.trim(),
      email: instForm.email.trim(),
    })
    emit('success')
    close()
  } catch {
    error.value = true
  } finally {
    sending.value = false
  }
}

async function submitCompany() {
  sending.value = true
  error.value = false
  try {
    await api.post('/company-registration-requests/', {
      company_name: coForm.company_name.trim(),
      contact_name: coForm.contact_name.trim(),
      phone: coForm.phone.trim(),
      email: coForm.email.trim(),
      address: coForm.address.trim(),
      comment: coForm.comment.trim(),
    })
    emit('success')
    close()
  } catch {
    error.value = true
  } finally {
    sending.value = false
  }
}
</script>

<style scoped lang="scss">
.home-reg__backdrop {
  position: fixed;
  inset: 0;
  z-index: 2000;
  background: rgba(15, 23, 42, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.home-reg__modal {
  width: 100%;
  max-width: 520px;
  max-height: 90vh;
  overflow-y: auto;
  padding: 1.75rem;
  background: #fff;
  border-radius: var(--vuvoz-radius-lg);
  border: 1px solid var(--vuvoz-border);
  box-shadow: var(--vuvoz-shadow-xl);
}

.home-reg__head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.home-reg__title {
  margin: 0;
  font-size: 1.35rem;
  font-family: var(--hp-font-heading);
}

.home-reg__close {
  border: none;
  background: transparent;
  font-size: 1.75rem;
  line-height: 1;
  cursor: pointer;
  color: var(--vuvoz-text-muted);
}

.home-reg__type-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.home-reg__type-tab {
  flex: 1;
  padding: 0.65rem;
  border-radius: 10px;
  border: 2px solid var(--vuvoz-border);
  background: #fff;
  font-weight: 600;
  cursor: pointer;

  &--active {
    border-color: var(--vuvoz-primary);
    background: rgba(13, 148, 136, 0.08);
    color: var(--vuvoz-primary);
  }
}

.home-reg__benefits {
  background: #f0fdfa;
  border-radius: 12px;
  padding: 1rem 1.15rem;
  margin-bottom: 1.25rem;
  border: 1px solid rgba(13, 148, 136, 0.15);
}

.home-reg__benefits-title {
  margin: 0 0 0.5rem;
  font-size: 0.95rem;
}

.home-reg__benefits-list {
  margin: 0;
  padding-left: 1.1rem;
  font-size: 0.88rem;
  color: var(--vuvoz-text-secondary);
  line-height: 1.5;
}

.home-reg__form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.home-reg__input {
  width: 100%;
  padding: 0.75rem 1rem;
  border-radius: 10px;
  border: 2px solid var(--vuvoz-border);
  font-size: 16px;
  background: #fff;
}

.home-reg__textarea {
  resize: vertical;
  min-height: 64px;
}

.home-reg__consent {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  font-size: 0.85rem;
  color: var(--vuvoz-text-secondary);
  cursor: pointer;
}

.home-reg__actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 0.25rem;
}

.home-reg__btn {
  flex: 1;
  min-height: 44px;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
}

.home-reg__btn--secondary {
  border: 2px solid var(--vuvoz-border);
  background: #fff;
}

.home-reg__btn--primary {
  border: none;
  background: var(--vuvoz-primary);
  color: #fff;

  &:disabled {
    opacity: 0.6;
  }
}

.home-reg__error {
  color: #dc2626;
  font-size: 0.9rem;
  margin: 0;
}
</style>
