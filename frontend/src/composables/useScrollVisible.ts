import { onMounted, onUnmounted, ref, type Ref } from 'vue'

export function useScrollVisible(threshold = 0.1): Ref<boolean> {
  const el: Ref<HTMLElement | null> = ref(null)
  const visible = ref(false)

  let observer: IntersectionObserver | null = null

  onMounted(() => {
    observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) visible.value = true
      },
      { threshold, rootMargin: '0px 0px -40px 0px' }
    )
    if (el.value) observer.observe(el.value)
  })

  onUnmounted(() => {
    if (observer && el.value) observer.unobserve(el.value)
  })

  return { el, visible }
}
