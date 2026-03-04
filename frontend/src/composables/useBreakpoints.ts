import { computed } from 'vue'
import { useDisplay } from 'vuetify'

/** Vuetify breakpoints: xs < 600, sm 600-960, md 960-1280, lg 1280-1920, xl 1920+ */
export function useBreakpoints() {
  const display = useDisplay()

  const isMobile = computed(() => display.smAndDown.value)
  const isTablet = computed(() => display.md.value)
  const isDesktop = computed(() => display.lgAndUp.value)
  const isXs = computed(() => display.xs.value)
  const isSm = computed(() => display.sm.value)

  /** Use for fullscreen modals on small screens */
  const fullscreenModal = computed(() => display.smAndDown.value)

  return {
    ...display,
    isMobile,
    isTablet,
    isDesktop,
    isXs,
    isSm,
    fullscreenModal,
  }
}
