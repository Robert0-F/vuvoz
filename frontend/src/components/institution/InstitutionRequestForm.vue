<template>
  <div class="inst-request-form">
    <div class="inst-request-form__header">
      <h3 class="inst-request-form__title">Новый запрос на вывоз</h3>
      <p class="inst-request-form__sub">Укажите типы макулатуры и вес. Система покажет ориентировочную стоимость.</p>
    </div>

    <form class="inst-request-form__form" @submit.prevent="$emit('submit')">
      <div class="inst-request-form__step">
        <div class="inst-request-form__step-label">
          <span class="inst-request-form__step-num">1</span>
          Типы макулатуры и вес (кг) *
        </div>
        <p v-if="weightLimits" class="inst-request-form__hint">
          Суммарный вес: от {{ weightLimits.min_kg }} до {{ weightLimits.max_kg }} кг
        </p>
        <div v-if="errors.material_lines" class="inst-request-form__error">{{ errors.material_lines }}</div>
        <div
          v-for="(line, idx) in materialLines"
          :key="idx"
          class="inst-request-form__row"
        >
          <select v-model="line.material_type" class="inst-request-form__select">
            <option v-for="opt in materialTypeItems" :key="opt.value" :value="opt.value">{{ opt.title }}</option>
          </select>
          <input
            v-model="line.amount_kg"
            type="number"
            min="1"
            :max="weightLimits?.max_kg || 100000"
            step="0.01"
            placeholder="Вес (кг)"
            class="inst-request-form__input inst-request-form__input--narrow"
          />
          <button
            type="button"
            class="inst-request-form__remove"
            :disabled="materialLines.length <= 1"
            aria-label="Удалить"
            @click="$emit('remove-line', idx)"
          >
            <v-icon icon="mdi-close" size="20" />
          </button>
        </div>
        <button type="button" class="inst-request-form__add" @click="$emit('add-line')">
          <v-icon icon="mdi-plus" size="18" />
          Добавить тип макулатуры
        </button>
      </div>

      <div class="inst-request-form__step">
        <div class="inst-request-form__step-label">
          <span class="inst-request-form__step-num">2</span>
          Желаемая дата и комментарий
        </div>
        <div class="inst-request-form__row inst-request-form__row--wide">
          <input
            :value="desiredDate"
            type="date"
            class="inst-request-form__input"
            placeholder="Желаемая дата"
            @input="$emit('update:desiredDate', ($event.target as HTMLInputElement).value)"
          />
          <textarea
            :value="comment"
            class="inst-request-form__textarea"
            placeholder="Комментарий (необязательно)"
            rows="2"
            @input="$emit('update:comment', ($event.target as HTMLTextAreaElement).value)"
          />
        </div>
      </div>

      <div class="inst-request-form__footer">
        <div v-if="estimatedValuePreview != null" class="inst-request-form__preview">
          Примерная стоимость: <strong>{{ estimatedValuePreview }} руб.</strong>
        </div>
        <button type="submit" class="inst-request-form__submit" :disabled="submitting">
          {{ submitting ? 'Отправка…' : 'Отправить запрос' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  materialLines: { material_type: string; amount_kg: string }[]
  desiredDate: string
  comment: string
  weightLimits: { min_kg: string; max_kg: string } | null
  materialTypeItems: { title: string; value: string }[]
  errors: { material_lines?: string }
  estimatedValuePreview: string | null
  submitting: boolean
}>()

defineEmits<{
  submit: []
  'add-line': []
  'remove-line': [idx: number]
  'update:desiredDate': [value: string]
  'update:comment': [value: string]
}>()
</script>

<style scoped lang="scss">
.inst-request-form {
  background: var(--vuvoz-surface-elevated);
  border-radius: var(--vuvoz-radius-lg);
  border: 1px solid var(--vuvoz-border);
  box-shadow: var(--vuvoz-shadow-sm);
  overflow: hidden;
}

.inst-request-form__header {
  padding: 1.5rem 1.5rem 0;
}

.inst-request-form__title {
  font-size: 1.25rem;
  font-weight: 700;
  margin: 0 0 0.35rem;
  color: var(--vuvoz-text);
}

.inst-request-form__sub {
  font-size: 0.9rem;
  color: var(--vuvoz-text-secondary);
  margin: 0 0 1.5rem;
  line-height: 1.5;
}

.inst-request-form__form {
  padding: 0 1.5rem 1.5rem;
}

.inst-request-form__step {
  margin-bottom: 1.5rem;
}

.inst-request-form__step-label {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--vuvoz-text);
  margin-bottom: 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.inst-request-form__step-num {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--vuvoz-primary);
  color: #fff;
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.inst-request-form__hint {
  font-size: 0.8rem;
  color: var(--vuvoz-text-muted);
  margin: 0 0 0.5rem;
}

.inst-request-form__error {
  font-size: 0.85rem;
  color: #dc2626;
  margin-bottom: 0.75rem;
}

.inst-request-form__row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;

  &--wide {
    flex-direction: column;
    align-items: stretch;
  }
}

.inst-request-form__select,
.inst-request-form__input,
.inst-request-form__textarea {
  padding: 0.6rem 0.75rem;
  border-radius: var(--vuvoz-radius-sm);
  border: 2px solid var(--vuvoz-border);
  font-size: 1rem;
  transition: border-color 0.2s;

  &:focus {
    outline: none;
    border-color: var(--vuvoz-primary);
  }
}

.inst-request-form__select {
  min-width: 160px;
  background: #fff;
}

.inst-request-form__input {
  flex: 1;
  min-width: 100px;

  &--narrow {
    max-width: 120px;
  }
}

.inst-request-form__textarea {
  resize: vertical;
  min-height: 60px;
}

.inst-request-form__remove {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  color: var(--vuvoz-text-muted);
  cursor: pointer;
  border-radius: var(--vuvoz-radius-sm);
  &:hover:not(:disabled) {
    background: rgba(220, 38, 38, 0.08);
    color: #dc2626;
  }
  &:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }
}

.inst-request-form__add {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.5rem 0.75rem;
  border: 2px dashed var(--vuvoz-border);
  border-radius: var(--vuvoz-radius-sm);
  background: transparent;
  font-size: 0.9rem;
  color: var(--vuvoz-primary);
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;
  &:hover {
    border-color: var(--vuvoz-primary);
    background: rgba(13, 148, 136, 0.06);
  }
}

.inst-request-form__footer {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-top: 1.25rem;
  padding-top: 1.25rem;
  border-top: 1px solid var(--vuvoz-border);
}

.inst-request-form__preview {
  font-size: 1rem;
  color: var(--vuvoz-text-secondary);
}

.inst-request-form__submit {
  padding: 0.7rem 1.5rem;
  border-radius: var(--vuvoz-radius-sm);
  border: none;
  background: var(--vuvoz-primary);
  color: #fff;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.2s, transform 0.1s;
  &:hover:not(:disabled) {
    background: #0f766e;
    transform: translateY(-1px);
  }
  &:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }
}
</style>
