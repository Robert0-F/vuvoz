<template>
  <header class="public-header">
    <div class="public-header__inner hp-container">
      <AppHeaderLogo class="public-header__logo" :height-px="44" href="/" alt="Зелёный счёт — на главную" />

      <nav class="public-header__links" :class="{ 'public-header__links--open': mobileOpen }">
        <a href="#" @click.prevent="go('calculator')">Заявка на вывоз</a>

        <div
          class="public-header__dropdown"
          @mouseenter="catalogOpen = true"
          @mouseleave="catalogOpen = false"
        >
          <button type="button" class="public-header__drop-btn" @click="catalogOpen = !catalogOpen">
            Каталог
            <v-icon icon="mdi-chevron-down" size="18" />
          </button>
          <div v-show="catalogOpen" class="public-header__drop-menu">
            <RouterLink to="/materials" @click="closeMenus">Сырьё и цены</RouterLink>
            <RouterLink to="/products" @click="closeMenus">Товары за баллы</RouterLink>
          </div>
        </div>

        <div
          class="public-header__dropdown"
          @mouseenter="aboutOpen = true"
          @mouseleave="aboutOpen = false"
        >
          <button type="button" class="public-header__drop-btn" @click="aboutOpen = !aboutOpen">
            О платформе
            <v-icon icon="mdi-chevron-down" size="18" />
          </button>
          <div v-show="aboutOpen" class="public-header__drop-menu">
            <a href="#" @click.prevent="go('for-whom')">Для кого</a>
            <a href="#" @click.prevent="go('how')">Как работает</a>
            <a href="#" @click.prevent="go('benefits')">Преимущества</a>
          </div>
        </div>

        <a href="#" @click.prevent="go('news')">Новости</a>
        <a href="#" @click.prevent="go('cta')">Контакты</a>
      </nav>

      <div class="public-header__actions">
        <button type="button" class="public-header__btn public-header__btn--outline" @click="$emit('register')">
          Регистрация
        </button>
        <button type="button" class="public-header__btn public-header__btn--primary" @click="$emit('login')">
          Войти
        </button>
      </div>

      <button
        type="button"
        class="public-header__burger"
        aria-label="Меню"
        :aria-expanded="mobileOpen"
        @click="mobileOpen = !mobileOpen"
      >
        <span /><span /><span />
      </button>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import AppHeaderLogo from '@/components/AppHeaderLogo.vue'

const props = defineProps<{ home?: boolean }>()
const emit = defineEmits<{
  register: []
  login: []
  scroll: [id: string]
}>()

const router = useRouter()
const mobileOpen = ref(false)
const catalogOpen = ref(false)
const aboutOpen = ref(false)

function closeMenus() {
  mobileOpen.value = false
  catalogOpen.value = false
  aboutOpen.value = false
}

function go(id: string) {
  closeMenus()
  if (props.home) {
    emit('scroll', id)
  } else {
    router.push({ path: '/', hash: `#${id}` })
  }
}
</script>

<style scoped lang="scss">
.public-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--vuvoz-border);
}

.public-header__inner {
  padding-top: 0.5rem;
  padding-bottom: 0.5rem;
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  column-gap: 0.75rem;
}

.public-header__logo {
  grid-column: 1;
  justify-self: start;
  max-width: min(280px, 36vw);
}

.public-header__links {
  grid-column: 2;
  justify-self: center;
  display: flex;
  flex-wrap: nowrap;
  align-items: center;
  gap: 0.15rem 0.5rem;
  white-space: nowrap;

  > a {
    font-size: 0.88rem;
    font-weight: 500;
    color: var(--vuvoz-text);
    text-decoration: none;
    padding: 0.35rem 0.45rem;
    border-radius: 8px;
    &:hover { color: var(--vuvoz-primary); background: rgba(13, 148, 136, 0.06); }
  }
}

.public-header__dropdown {
  position: relative;
}

.public-header__drop-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.15rem;
  font-size: 0.88rem;
  font-weight: 500;
  color: var(--vuvoz-text);
  background: transparent;
  border: none;
  padding: 0.35rem 0.45rem;
  border-radius: 8px;
  cursor: pointer;
  &:hover { color: var(--vuvoz-primary); background: rgba(13, 148, 136, 0.06); }
}

.public-header__drop-menu {
  position: absolute;
  top: 100%;
  left: 0;
  min-width: 190px;
  background: #fff;
  border: 1px solid var(--vuvoz-border);
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  padding: 0.35rem;
  z-index: 10;

  a {
    display: block;
    padding: 0.5rem 0.65rem;
    font-size: 0.88rem;
    font-weight: 500;
    color: var(--vuvoz-text);
    text-decoration: none;
    border-radius: 8px;
    &:hover { color: var(--vuvoz-primary); background: rgba(13, 148, 136, 0.06); }
  }
}

.public-header__actions {
  grid-column: 3;
  justify-self: end;
  display: flex;
  gap: 0.5rem;
}

.public-header__btn {
  font-size: 0.88rem;
  font-weight: 600;
  padding: 0.45rem 0.9rem;
  border-radius: 10px;
  cursor: pointer;
  border: 1px solid transparent;
  &--outline {
    background: #fff;
    border-color: var(--vuvoz-border);
    color: var(--vuvoz-text);
  }
  &--primary {
    background: var(--vuvoz-primary);
    color: #fff;
  }
}

.public-header__burger {
  display: none;
  flex-direction: column;
  justify-content: center;
  gap: 5px;
  width: 40px;
  height: 40px;
  padding: 0;
  border: none;
  background: transparent;
  cursor: pointer;
  span {
    display: block;
    width: 22px;
    height: 2px;
    background: var(--vuvoz-text);
    border-radius: 1px;
  }
}

@media (max-width: 960px) {
  .public-header__inner { grid-template-columns: max-content auto auto; }
  .public-header__burger { display: flex; justify-self: end; }
  .public-header__links {
    display: none;
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: #fff;
    border-bottom: 1px solid var(--vuvoz-border);
    flex-direction: column;
    align-items: stretch;
    padding: 1rem;
    white-space: normal;
    &--open { display: flex; }
  }
  .public-header__dropdown { width: 100%; }
  .public-header__drop-menu {
    position: static;
    box-shadow: none;
    border: none;
    padding-left: 0.5rem;
  }
  .public-header__actions { display: none; }
}
</style>
