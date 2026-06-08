/**
 * Resolve media URL for <img src> on the current site origin.
 * API may return relative `/media/...` or absolute URLs with a backend host (e.g. 127.0.0.1:8000).
 */
export function resolveMediaUrl(url: string | null | undefined): string {
  if (!url) return ''
  const trimmed = url.trim()
  if (!trimmed) return ''

  if (trimmed.startsWith('http://') || trimmed.startsWith('https://')) {
    try {
      const { pathname, search } = new URL(trimmed)
      if (pathname.startsWith('/media/')) {
        return `${window.location.origin}${pathname}${search}`
      }
    } catch {
      /* fall through */
    }
    return trimmed
  }

  const path = trimmed.startsWith('/') ? trimmed : `/media/${trimmed.replace(/^\//, '')}`
  return `${window.location.origin}${path}`
}
