<template>
  <section ref="sectionRef" class="home-calc" :class="{ 'hp-visible': visible }">
    <div class="home-calc__inner">
      <h2 class="hp-section-title home-calc__title">Рассчитайте доход от сдачи макулатуры</h2>
      <p class="hp-subtitle home-calc__subtitle">Выберите тип организации и объём — покажем примерный доход и количество вывозов.</p>

      <div class="home-calc__card hp-card">
        <div class="home-calc__steps">
          <div class="home-calc__step">
            <span class="home-calc__step-label">Тип организации</span>
            <div class="home-calc__chips">
              <button
                v-for="opt in orgTypes"
                :key="opt.value"
                type="button"
                class="home-calc__chip"
                :class="{ 'home-calc__chip--active': form.orgType === opt.value }"
                @click="form.orgType = opt.value"
              >
                <span class="home-calc__chip-icon">{{ opt.icon }}</span>
                {{ opt.label }}
              </button>
            </div>
          </div>
          <div class="home-calc__step">
            <span class="home-calc__step-label">Объём в месяц (кг)</span>
            <div class="home-calc__slider-wrap">
              <input
                v-model.number="form.volumeKg"
                type="range"
                min="50"
                max="2000"
                step="50"
                class="home-calc__slider"
              />
              <span class="home-calc__volume-value">{{ form.volumeKg }} кг</span>
            </div>
          </div>
          <div class="home-calc__step">
            <span class="home-calc__step-label">Тип макулатуры</span>
            <select v-model="form.materialType" class="home-calc__select">
              <option v-for="m in materialOptions" :key="m.value" :value="m.value">{{ m.label }}</option>
            </select>
          </div>
        </div>

        <div class="home-calc__result">
          <div class="home-calc__result-label">Примерный доход в месяц</div>
          <div class="home-calc__result-value">{{ estimatedIncome }} ₽</div>
          <div class="home-calc__result-hint">≈ {{ estimatedPickups }} вывозов</div>
          <p class="home-calc__result-note">Расчёт ориентировочный. Точную стоимость уточнит менеджер после заявки.</p>
          <button type="button" class="home-calc__cta" @click="openLeadModal">
            Получить индивидуальное предложение
          </button>
        </div>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="leadModalOpen" class="home-calc__modal-backdrop" @click.self="leadModalOpen = false">
        <div class="home-calc__modal hp-card">
          <h3 class="home-calc__modal-title">Индивидуальное предложение</h3>
          <p class="hp-subtitle home-calc__modal-sub">Оставьте контакты — рассчитаем точную стоимость и свяжемся с вами.</p>
          <form class="home-calc__form" @submit.prevent="submitLead">
            <input
              v-model="leadForm.name"
              type="text"
              class="home-calc__input"
              placeholder="Имя *"
              required
            />
            <input
              v-model="leadForm.phone"
              type="tel"
              class="home-calc__input"
              placeholder="Телефон *"
              required
            />
            <input
              v-model="leadForm.company"
              type="text"
              class="home-calc__input"
              placeholder="Компания / организация"
            />
            <div class="home-calc__modal-actions">
              <button type="button" class="home-calc__btn home-calc__btn--secondary" @click="leadModalOpen = false">
                Отмена
              </button>
              <button type="submit" class="home-calc__btn home-calc__btn--primary" :disabled="leadSending">
                {{ leadSending ? 'Отправка…' : 'Отправить' }}
              </button>
            </div>
          </form>
          <p v-if="leadSuccess" class="home-calc__success">Спасибо! Мы свяжемся с вами в ближайшее время.</p>
          <p v-if="leadError" class="home-calc__error">Не удалось отправить. Попробуйте позже.</p>
        </div>
      </div>
    </Teleport>
  </section>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { api } from '@/api/axios'

const sectionRef = ref<HTMLElement | null>(null)
const visible = ref(false)

const orgTypes = [
  { value: 'office', label: 'Офис', icon: '🏢' },
  { value: 'school', label: 'Школа', icon: '🏫' },
  { value: 'retail', label: 'Торговля', icon: '🛒' },
  { value: 'warehouse', label: 'Склад', icon: '📦' },
]

const materialOptions = [
  { value: 'paper', label: 'Бумага' },
  { value: 'cardboard', label: 'Картон' },
  { value: 'newspapers', label: 'Газеты' },
  { value: 'mixed', label: 'Смешанная' },
]

// Fallback prices (руб/кг) when API requires auth
const defaultPrices: Record<string, number> = {
  paper: 5,
  cardboard: 3,
  newspapers: 4,
  mixed: 3.5,
  archive: 6,
}

const form = reactive({
  orgType: 'office',
  volumeKg: 200,
  materialType: 'paper',
})

const prices = ref<{ material_type: string; price_per_kg: string }[]>([])

onMounted(async () => {
  const obs = new IntersectionObserver(
    ([e]) => { if (e.isIntersecting) visible.value = true },
    { threshold: 0.15 }
  )
  if (sectionRef.value) obs.observe(sectionRef.value)
  try {
    const { data } = await api.get<{ material_type: string; price_per_kg: string }[]>('/prices/current/')
    prices.value = Array.isArray(data) ? data : []
  } catch {
    prices.value = []
  }
})

const pricePerKg = computed(() => {
  const p = prices.value.find((x) => x.material_type === form.materialType)
  if (p) return parseFloat(p.price_per_kg) || 0
  return defaultPrices[form.materialType] ?? 4
})

const estimatedIncome = computed(() => {
  const total = form.volumeKg * pricePerKg.value
  return Math.round(total).toLocaleString('ru-RU')
})

const estimatedPickups = computed(() => {
  const perTrip = 150
  return Math.max(1, Math.ceil(form.volumeKg / perTrip))
})

const leadModalOpen = ref(false)
const leadForm = reactive({ name: '', phone: '', company: '' })
const leadSending = ref(false)
const leadSuccess = ref(false)
const leadError = ref(false)

function openLeadModal() {
  leadSuccess.value = false
  leadError.value = false
  leadModalOpen.value = true
}

async function submitLead() {
  leadSending.value = true
  leadError.value = false
  try {
    await api.post('/registration-requests/', {
      first_name: leadForm.name.trim(),
      patronymic: '',
      institution_name: leadForm.company.trim() || 'Запрос с калькулятора',
      address: 'Запрос с калькулятора',
      phone: leadForm.phone.trim(),
    })
    leadSuccess.value = true
    leadForm.name = ''
    leadForm.phone = ''
    leadForm.company = ''
    setTimeout(() => {
      leadModalOpen.value = false
    }, 2000)
  } catch {
    leadError.value = true
  } finally {
    leadSending.value = false
  }
}
</script>

<style scoped lang="scss">
.home-calc {
  padding: clamp(3rem, 8vw, 5rem) 1.5rem;
  opacity: 0;
  transform: translateY(24px);
  transition: opacity 0.6s var(--vuvoz-ease), transform 0.6s var(--vuvoz-ease);

  &.hp-visible {
    opacity: 1;
    transform: translateY(0);
  }
}

.home-calc__inner {
  max-width: 900px;
  margin: 0 auto;
}

.home-calc__title {
  text-align: center;
  margin: 0 0 0.5rem;
}

.home-calc__subtitle {
  text-align: center;
  margin: 0 0 2.5rem;
}

.home-calc__card {
  background: var(--vuvoz-surface-elevated);
  padding: 2rem;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  align-items: start;
  border: 1px solid var(--vuvoz-border);
}

@media (max-width: 768px) {
  .home-calc__card {
    grid-template-columns: 1fr;
  }
}

.home-calc__step {
  margin-bottom: 1.5rem;
}

.home-calc__step-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--vuvoz-text);
  margin-bottom: 0.5rem;
}

.home-calc__chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.home-calc__chip {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.5rem 0.75rem;
  border-radius: 10px;
  border: 2px solid var(--vuvoz-border);
  background: #fff;
  font-size: 0.9rem;
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;

  &--active {
    border-color: var(--vuvoz-primary);
    background: rgba(13, 148, 136, 0.08);
    color: var(--vuvoz-primary);
  }
}

.home-calc__chip-icon {
  font-size: 1.1rem;
}

.home-calc__slider-wrap {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.home-calc__slider {
  flex: 1;
  height: 8px;
  border-radius: 4px;
  accent-color: var(--vuvoz-primary);
}

.home-calc__volume-value {
  font-weight: 600;
  min-width: 4rem;
}

.home-calc__select {
  width: 100%;
  padding: 0.6rem 0.75rem;
  border-radius: 10px;
  border: 2px solid var(--vuvoz-border);
  font-size: 1rem;
  background: #fff;
}

.home-calc__result {
  background: linear-gradient(135deg, rgba(13, 148, 136, 0.08) 0%, rgba(20, 184, 166, 0.06) 100%);
  padding: 1.5rem;
  border-radius: var(--vuvoz-radius);
  border: 1px solid rgba(13, 148, 136, 0.2);
}

.home-calc__result-label {
  font-size: 0.875rem;
  color: var(--vuvoz-text-secondary);
  margin-bottom: 0.25rem;
}

.home-calc__result-value {
  font-family: var(--hp-font-heading);
  font-size: 2rem;
  font-weight: 800;
  color: var(--vuvoz-primary);
  margin-bottom: 0.25rem;
}

.home-calc__result-hint {
  font-size: 0.875rem;
  color: var(--vuvoz-text-muted);
  margin-bottom: 0.5rem;
}

.home-calc__result-note {
  font-size: 0.75rem;
  color: var(--vuvoz-text-muted);
  margin: 0 0 1.25rem;
}

.home-calc__cta {
  width: 100%;
  padding: 0.875rem 1.25rem;
  border-radius: 10px;
  border: none;
  background: var(--vuvoz-primary);
  color: #fff;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.2s, transform 0.1s;
  &:hover {
    background: #0f766e;
    transform: translateY(-1px);
  }
}

.home-calc__modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 1rem;
}

.home-calc__modal {
  background: #fff;
  padding: 2rem;
  max-width: 420px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
}

.home-calc__modal-title {
  margin: 0 0 0.5rem;
  font-size: 1.35rem;
}

.home-calc__modal-sub {
  margin: 0 0 1.5rem;
  font-size: 0.9rem;
}

.home-calc__form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.home-calc__input {
  padding: 0.75rem 1rem;
  border-radius: 10px;
  border: 2px solid var(--vuvoz-border);
  font-size: 1rem;
  &:focus {
    outline: none;
    border-color: var(--vuvoz-primary);
  }
}

.home-calc__modal-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.home-calc__btn {
  flex: 1;
  padding: 0.75rem 1rem;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  &--primary {
    background: var(--vuvoz-primary);
    color: #fff;
  }
  &--secondary {
    background: var(--vuvoz-surface-muted);
    color: var(--vuvoz-text);
  }
}

.home-calc__success { color: var(--vuvoz-primary); margin-top: 1rem; font-weight: 500; }
.home-calc__error { color: #dc2626; margin-top: 1rem; font-size: 0.9rem; }
</style>
