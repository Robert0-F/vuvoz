/** Vuetify 3 v-file-input: single file → File, multiple → File[]. */
export function pickFirstFile(value: File | File[] | null | undefined): File | null {
  if (!value) return null
  if (value instanceof File) return value
  if (Array.isArray(value) && value.length > 0 && value[0] instanceof File) return value[0]
  return null
}
