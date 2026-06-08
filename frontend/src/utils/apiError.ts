/** Turn DRF/axios error payload into a short user-facing Russian message. */
export function formatApiError(error: unknown, fallback = 'Не удалось отправить. Попробуйте позже.'): string {
  const response = (error as { response?: { status?: number; data?: unknown } })?.response
  if (!response) return fallback

  if (response.status === 429) {
    return 'Слишком много попыток. Подождите немного и попробуйте снова.'
  }
  if (response.status === 403) {
    return 'Доступ запрещён. Обновите страницу и попробуйте снова.'
  }

  const body = response.data
  if (typeof body === 'string' && body.trim()) return body.trim()

  if (body && typeof body === 'object') {
    const record = body as Record<string, unknown>
    if (typeof record.detail === 'string' && record.detail.trim()) {
      return record.detail.trim()
    }
    const messages: string[] = []
    for (const value of Object.values(record)) {
      if (Array.isArray(value)) {
        for (const item of value) {
          if (typeof item === 'string' && item.trim()) messages.push(item.trim())
        }
      } else if (typeof value === 'string' && value.trim()) {
        messages.push(value.trim())
      }
    }
    if (messages.length) return messages.join(' ')
  }

  return fallback
}
