<template>
  <component
    :is="href ? 'a' : 'span'"
    :href="href ?? undefined"
    class="app-header-logo"
    :class="{ 'app-header-logo--link': !!href }"
    :aria-label="href ? 'На главную' : undefined"
    @click="onClick"
  >
    <img
      class="app-header-logo__img"
      :src="BRAND_LOGO_URL"
      :alt="alt"
      :width="widthAttr"
      :height="heightPx"
      loading="eager"
      decoding="async"
    />
  </component>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { BRAND_LOGO_ASPECT, BRAND_LOGO_HEIGHT, BRAND_LOGO_URL, BRAND_LOGO_WIDTH } from '@/constants/brandLogo'

const props = withDefaults(
  defineProps<{
    /** Display height in px; width follows 1000:180 aspect ratio */
    heightPx?: number
    href?: string | null
    alt?: string
    /** Use router.push instead of full page navigation when href is set */
    useRouter?: boolean
  }>(),
  {
    heightPx: 36,
    href: '/',
    alt: 'Зелёный счёт',
    useRouter: true,
  },
)

const router = useRouter()

const widthAttr = computed(() => Math.round(props.heightPx * BRAND_LOGO_ASPECT))
const cssHeight = computed(() => `${props.heightPx}px`)

const onClick = (e: MouseEvent) => {
  if (!props.href || !props.useRouter) return
  if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return
  e.preventDefault()
  router.push(props.href)
}

</script>

<style scoped lang="scss">
.app-header-logo {
  display: inline-flex;
  align-items: center;
  flex-shrink: 0;
  line-height: 0;
  text-decoration: none;
}

.app-header-logo--link {
  cursor: pointer;
}

.app-header-logo__img {
  height: v-bind(cssHeight);
  width: auto;
  max-width: 100%;
  object-fit: contain;
  display: block;
}
</style>
