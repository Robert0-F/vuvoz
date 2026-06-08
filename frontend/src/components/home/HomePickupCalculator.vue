<template>
  <section ref="sectionRef" class="home-pickup" :class="{ 'hp-visible': visible }">
    <div class="home-pickup__inner hp-container">
      <h2 class="hp-section-title home-pickup__title">Заявка на вывоз без регистрации</h2>
      <p class="hp-subtitle home-pickup__subtitle">
        Добавьте виды сырья и вес — сумма пересчитывается сразу. Оформите заявку, менеджер свяжется с вами.
      </p>

      <div v-if="loading" class="home-pickup__state">Загрузка…</div>
      <div v-else-if="!materials.length" class="home-pickup__state">Калькулятор временно недоступен.</div>
      <div v-else class="home-pickup__card hp-card">
        <div class="home-pickup__form-col">
          <div
            v-for="(row, rowIndex) in lines"
            :key="row.id"
            class="home-pickup__line"
          >
            <div class="home-pickup__line-head">
              <span class="home-pickup__label">Вид сырья {{ lines.length > 1 ? rowIndex + 1 : '' }}</span>
              <button
                v-if="lines.length > 1"
                type="button"
                class="home-pickup__remove"
                aria-label="Удалить"
                @click="removeLine(row.id)"
              >
                ×
              </button>
            </div>
            <div class="home-pickup__materials">
              <button
                v-for="m in materials"
                :key="m.id"
                type="button"
                class="home-pickup__mat"
                :class="{ 'home-pickup__mat--active': row.materialId === m.id }"
                @click="row.materialId = m.id"
              >
                <img
                  v-if="resolveMediaUrl(m.icon_url)"
                  :src="resolveMediaUrl(m.icon_url)"
                  :alt="m.name"
                  class="home-pickup__mat-icon"
                />
                <v-icon v-else :icon="materialMdiIcon(m.code, m.icon)" size="22" />
                <span>{{ m.name }}</span>
              </button>
            </div>
            <div class="home-pickup__weight-row">
              <input
                v-model.number="row.weightKg"
                type="range"
                :min="minKg"
                :max="maxKg"
                :step="weightStep"
                class="home-pickup__slider"
                @input="clampRowWeight(row)"
              />
              <div class="home-pickup__weight-input-wrap">
                <input
                  v-model.number="row.weightKg"
                  type="number"
                  :min="minKg"
                  :max="maxKg"
                  :step="weightStep"
                  class="home-pickup__weight-input"
                  @change="clampRowWeight(row)"
                />
                <span class="home-pickup__weight-unit">кг</span>
              </div>
            </div>
            <p v-if="rowMaterial(row)" class="home-pickup__line-meta">
              {{ formatPrice(rowMaterial(row)!.price_per_kg) }} ₽/кг
            </p>
          </div>

          <button
            v-if="lines.length < materials.length"
            type="button"
            class="home-pickup__add"
            @click="addLine"
          >
            + Добавить другой вид сырья
          </button>
          <p class="home-pickup__hint">Вес каждой позиции: от {{ minKg }} до {{ maxKg }} кг</p>
        </div>

        <div class="home-pickup__result-col">
          <div class="home-pickup__result" :class="{ 'home-pickup__result--empty': !hasValidLines }">
            <span class="home-pickup__result-label">Примерная выплата</span>
            <div class="home-pickup__result-value">{{ payoutFormatted }} ₽</div>
            <ul v-if="lineBreakdown.length" class="home-pickup__breakdown">
              <li v-for="item in lineBreakdown" :key="item.key">
                {{ item.name }} · {{ item.weight }} кг × {{ item.price }} ₽/кг = {{ item.subtotal }} ₽
              </li>
            </ul>
            <p v-else class="home-pickup__result-note">Укажите вес хотя бы для одной позиции</p>
            <p v-if="hasValidLines" class="home-pickup__result-note">Точная сумма после взвешивания на месте.</p>
            <button
              type="button"
              class="home-pickup__btn-order"
              :disabled="!hasValidLines"
              @click="openOrderModal"
            >
              Оформить заявку на вывоз
            </button>
          </div>
        </div>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="orderModalOpen" class="home-pickup__backdrop" @click.self="orderModalOpen = false">
        <div class="home-pickup__modal">
          <h3 class="home-pickup__modal-title">Заявка на вывоз</h3>
          <p class="hp-subtitle home-pickup__modal-sub">
            Ориентир {{ payoutFormatted }} ₽ · {{ lineBreakdown.length }} {{ lineBreakdown.length === 1 ? 'позиция' : 'позиции' }}
          </p>
          <ul class="home-pickup__modal-lines">
            <li v-for="item in lineBreakdown" :key="item.key">{{ item.name }} — {{ item.weight }} кг</li>
          </ul>
          <form class="home-pickup__form" @submit.prevent="submitOrder">
            <input v-model="orderForm.contact_name" type="text" class="home-pickup__input" placeholder="Имя или организация" />
            <input v-model="orderForm.phone" type="tel" class="home-pickup__input" placeholder="Телефон *" required />
            <textarea
              v-model="orderForm.address"
              class="home-pickup__input home-pickup__textarea"
              placeholder="Адрес вывоза *"
              rows="2"
              required
            />
            <label class="home-pickup__date-label">
              Желаемая дата вывоза *
              <input v-model="orderForm.preferred_date" type="date" class="home-pickup__input" :min="minDate" required />
            </label>
            <div class="home-pickup__modal-actions">
              <button type="button" class="home-pickup__btn-secondary" @click="orderModalOpen = false">Отмена</button>
              <button type="submit" class="home-pickup__btn-primary" :disabled="orderSending || !hasValidLines">
                {{ orderSending ? 'Отправка…' : 'Отправить заявку' }}
              </button>
            </div>
          </form>
          <p v-if="orderSuccess" class="home-pickup__success">Заявка принята. Мы свяжемся с вами в ближайшее время.</p>
          <p v-if="orderError" class="home-pickup__error">{{ orderError }}</p>
        </div>
      </div>
    </Teleport>
  </section>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { api } from '@/api/axios'
import type { PublicMaterial } from '@/types'
import { materialMdiIcon } from '@/utils/materialIcon'
import { resolveMediaUrl } from '@/utils/mediaUrl'
import { formatApiError } from '@/utils/apiError'

interface PickupLine {
  id: number
  materialId: number | null
  weightKg: number
}

let lineIdSeq = 1

const sectionRef = ref<HTMLElement | null>(null)
const visible = ref(false)
const loading = ref(true)
const materials = ref<PublicMaterial[]>([])
const minKg = ref(50)
const maxKg = ref(2000)
const weightStep = 10
const lines = ref<PickupLine[]>([])

const orderModalOpen = ref(false)
const orderSending = ref(false)
const orderSuccess = ref(false)
const orderError = ref('')
const orderForm = reactive({
  contact_name: '',
  phone: '',
  address: '',
  preferred_date: '',
})

function rowMaterial(row: PickupLine): PublicMaterial | undefined {
  return materials.value.find((m) => m.id === row.materialId)
}

function formatPrice(v: string | number) {
  const n = typeof v === 'string' ? parseFloat(v) : v
  return (n || 0).toLocaleString('ru-RU', { maximumFractionDigits: 2 })
}

function clampRowWeight(row: PickupLine) {
  if (Number.isNaN(row.weightKg)) row.weightKg = minKg.value
  row.weightKg = Math.min(maxKg.value, Math.max(minKg.value, Math.round(row.weightKg)))
}

function addLine() {
  const used = new Set(lines.value.map((l) => l.materialId))
  const next = materials.value.find((m) => !used.has(m.id))
  if (!next) return
  lines.value.push({
    id: lineIdSeq++,
    materialId: next.id,
    weightKg: Math.min(200, maxKg.value),
  })
}

function removeLine(id: number) {
  if (lines.value.length <= 1) return
  lines.value = lines.value.filter((l) => l.id !== id)
}

const lineBreakdown = computed(() => {
  const out: { key: string; name: string; weight: number; price: string; subtotal: string }[] = []
  for (const row of lines.value) {
    const m = rowMaterial(row)
    if (!m || row.weightKg < minKg.value) continue
    const price = parseFloat(m.price_per_kg) || 0
    const subtotal = Math.round(row.weightKg * price)
    out.push({
      key: `${row.id}-${m.id}`,
      name: m.name,
      weight: row.weightKg,
      price: formatPrice(price),
      subtotal: subtotal.toLocaleString('ru-RU'),
    })
  }
  return out
})

const totalPayout = computed(() => {
  let sum = 0
  for (const row of lines.value) {
    const m = rowMaterial(row)
    if (!m || row.weightKg < minKg.value) continue
    sum += row.weightKg * (parseFloat(m.price_per_kg) || 0)
  }
  return sum
})

const payoutFormatted = computed(() => Math.round(totalPayout.value).toLocaleString('ru-RU'))

const hasValidLines = computed(() => lineBreakdown.value.length > 0)

const minDate = computed(() => {
  const d = new Date()
  d.setDate(d.getDate() + 1)
  return d.toISOString().slice(0, 10)
})

function openOrderModal() {
  if (!hasValidLines.value) return
  orderSuccess.value = false
  orderError.value = ''
  if (!orderForm.preferred_date) orderForm.preferred_date = minDate.value
  orderModalOpen.value = true
}

async function submitOrder() {
  if (!hasValidLines.value) return
  orderSending.value = true
  orderError.value = ''
  const items = lines.value
    .filter((row) => row.materialId && row.weightKg >= minKg.value)
    .map((row) => ({
      material_id: row.materialId!,
      weight_kg: row.weightKg,
    }))
  try {
    await api.post('/public/pickup-requests/', {
      items,
      phone: orderForm.phone.trim(),
      address: orderForm.address.trim(),
      preferred_date: orderForm.preferred_date,
      contact_name: orderForm.contact_name.trim(),
    })
    orderSuccess.value = true
    orderForm.contact_name = ''
    orderForm.phone = ''
    orderForm.address = ''
    orderForm.preferred_date = ''
    setTimeout(() => {
      orderModalOpen.value = false
    }, 2000)
  } catch (err) {
    orderError.value = formatApiError(err)
  } finally {
    orderSending.value = false
  }
}

onMounted(async () => {
  const obs = new IntersectionObserver(
    ([e]) => { if (e?.isIntersecting) visible.value = true },
    { threshold: 0.1 },
  )
  if (sectionRef.value) obs.observe(sectionRef.value)

  try {
    const [matRes, limRes] = await Promise.all([
      api.get<PublicMaterial[]>('/public/materials/'),
      api.get<{ min_kg: string; max_kg: string }>('/public/weight-limits/'),
    ])
    materials.value = Array.isArray(matRes.data) ? matRes.data : []
    const min = parseFloat(limRes.data?.min_kg ?? '50')
    const max = parseFloat(limRes.data?.max_kg ?? '2000')
    if (!Number.isNaN(min)) minKg.value = min
    if (!Number.isNaN(max)) maxKg.value = max
    if (materials.value.length) {
      lines.value = [
        {
          id: lineIdSeq++,
          materialId: materials.value[0].id,
          weightKg: Math.min(Math.max(200, minKg.value), maxKg.value),
        },
      ]
    }
  } catch {
    materials.value = []
  } finally {
    loading.value = false
  }
})
</script>

<style scoped lang="scss">
.home-pickup {
  padding: clamp(3rem, 8vw, 5rem) 0;
  background: #fff;
  opacity: 0;
  transform: translateY(24px);
  transition: opacity 0.6s var(--vuvoz-ease), transform 0.6s var(--vuvoz-ease);

  &.hp-visible {
    opacity: 1;
    transform: translateY(0);
  }
}

.home-pickup__inner {
  width: 100%;
}

.home-pickup__title {
  text-align: center;
  margin: 0 0 0.5rem;
}

.home-pickup__subtitle {
  text-align: center;
  margin: 0 0 2rem;
}

.home-pickup__state {
  text-align: center;
  color: var(--vuvoz-text-muted);
  padding: 2rem;
}

.home-pickup__card {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  padding: 2rem;
  background: var(--vuvoz-surface-elevated);
  align-items: start;

  @media (max-width: 900px) {
    grid-template-columns: 1fr;
  }
}

.home-pickup__line {
  padding-bottom: 1.25rem;
  margin-bottom: 1.25rem;
  border-bottom: 1px solid var(--vuvoz-border);

  &:last-of-type {
    border-bottom: none;
    margin-bottom: 0;
  }
}

.home-pickup__line-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.home-pickup__label {
  font-weight: 600;
  font-size: 0.9rem;
}

.home-pickup__remove {
  border: none;
  background: transparent;
  font-size: 1.5rem;
  line-height: 1;
  cursor: pointer;
  color: var(--vuvoz-text-muted);
}

.home-pickup__materials {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.home-pickup__mat {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.45rem 0.75rem;
  border-radius: 10px;
  border: 2px solid var(--vuvoz-border);
  background: #fff;
  cursor: pointer;
  font-size: 0.85rem;

  &--active {
    border-color: var(--vuvoz-primary);
    background: rgba(13, 148, 136, 0.08);
    color: var(--vuvoz-primary);
  }
}

.home-pickup__mat-icon {
  width: 22px;
  height: 22px;
  object-fit: contain;
  flex-shrink: 0;
}

.home-pickup__weight-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 1rem;
}

.home-pickup__slider {
  flex: 1;
  min-width: 140px;
  accent-color: var(--vuvoz-primary);
}

.home-pickup__weight-input-wrap {
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.home-pickup__weight-input {
  width: 5rem;
  padding: 0.5rem 0.6rem;
  border-radius: 8px;
  border: 2px solid var(--vuvoz-border);
  font-size: 1rem;
  text-align: right;
}

.home-pickup__weight-unit {
  font-size: 0.9rem;
  color: var(--vuvoz-text-muted);
}

.home-pickup__line-meta {
  font-size: 0.8rem;
  color: var(--vuvoz-text-muted);
  margin: 0.35rem 0 0;
}

.home-pickup__add {
  width: 100%;
  padding: 0.75rem;
  border: 2px dashed var(--vuvoz-primary);
  border-radius: 12px;
  background: rgba(13, 148, 136, 0.04);
  color: var(--vuvoz-primary);
  font-weight: 600;
  cursor: pointer;
  margin-top: 0.5rem;
}

.home-pickup__hint {
  font-size: 0.85rem;
  color: var(--vuvoz-text-muted);
  margin: 0.75rem 0 0;
}

.home-pickup__result {
  background: linear-gradient(135deg, #f0fdfa 0%, #ecfdf5 100%);
  border-radius: var(--vuvoz-radius-lg);
  padding: 1.75rem;
  border: 1px solid rgba(13, 148, 136, 0.2);
  min-height: 220px;

  &--empty .home-pickup__result-value {
    opacity: 0.45;
  }
}

.home-pickup__result-label {
  font-size: 0.9rem;
  color: var(--vuvoz-text-muted);
}

.home-pickup__result-value {
  font-size: clamp(2rem, 5vw, 2.75rem);
  font-weight: 800;
  color: #059669;
  margin: 0.35rem 0 0.75rem;
  font-family: var(--hp-font-heading);
}

.home-pickup__breakdown {
  list-style: none;
  padding: 0;
  margin: 0 0 1rem;
  font-size: 0.85rem;
  color: var(--vuvoz-text-secondary);
  line-height: 1.5;
}

.home-pickup__result-note {
  font-size: 0.85rem;
  color: var(--vuvoz-text-muted);
  margin: 0.25rem 0;
}

.home-pickup__btn-order {
  margin-top: 1.25rem;
  width: 100%;
  min-height: 48px;
  border: none;
  border-radius: 12px;
  background: #059669;
  color: #fff;
  font-weight: 600;
  cursor: pointer;

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.home-pickup__backdrop {
  position: fixed;
  inset: 0;
  z-index: 2000;
  background: rgba(15, 23, 42, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.home-pickup__modal {
  width: 100%;
  max-width: 440px;
  padding: 1.75rem;
  border: 1px solid var(--vuvoz-border);
  border-radius: var(--vuvoz-radius-lg);
  background: #fff;
  box-shadow: var(--vuvoz-shadow-xl);
}

.home-pickup__modal-title {
  margin: 0 0 0.35rem;
  font-size: 1.25rem;
}

.home-pickup__modal-sub {
  margin: 0 0 0.75rem;
}

.home-pickup__modal-lines {
  margin: 0 0 1rem;
  padding-left: 1.1rem;
  font-size: 0.9rem;
  color: var(--vuvoz-text-secondary);
}

.home-pickup__form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.home-pickup__input {
  width: 100%;
  padding: 0.75rem 1rem;
  border-radius: 10px;
  border: 2px solid var(--vuvoz-border);
  font-size: 16px;
  background: #fff;
}

.home-pickup__textarea {
  resize: vertical;
  min-height: 72px;
}

.home-pickup__date-label {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  font-size: 0.85rem;
  font-weight: 600;
}

.home-pickup__modal-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.home-pickup__btn-secondary,
.home-pickup__btn-primary {
  flex: 1;
  min-height: 44px;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
}

.home-pickup__btn-secondary {
  border: 2px solid var(--vuvoz-border);
  background: #fff;
}

.home-pickup__btn-primary {
  border: none;
  background: var(--vuvoz-primary);
  color: #fff;

  &:disabled {
    opacity: 0.6;
  }
}

.home-pickup__success {
  color: #059669;
  margin-top: 1rem;
  font-weight: 600;
}

.home-pickup__error {
  color: #dc2626;
  margin-top: 0.75rem;
}
</style>
