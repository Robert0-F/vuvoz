<template>
  <div class="home-page">
    <PublicSiteHeader
      home
      @scroll="scrollTo"
      @register="openRegistrationDialog"
      @login="goToLogin"
    />

    <main class="home-page__main">
      <HomeHero
        @scroll-to-calculator="scrollTo('calculator')"
        @scroll-to-process="scrollTo('how')"
        @open-registration="openRegistrationDialog"
      />
      <section id="calculator" ref="calculatorRef">
        <HomePickupCalculator />
      </section>
      <HomeTrustStrip />
      <section id="materials" ref="materialsRef">
        <HomeMaterialsShowcase @scroll-to-calculator="scrollTo('calculator')" />
      </section>
      <section id="for-whom" ref="forWhomRef">
        <HomeForWhom @scroll-to-contact="scrollTo('cta')" />
      </section>
      <section id="how" ref="howRef">
        <HomeHowItWorks />
      </section>
      <section id="benefits" ref="benefitsRef">
        <HomeBenefits />
      </section>
      <section id="products" ref="productsRef">
        <HomeProductsShowcase @login="goToLogin" />
      </section>
      <section id="testimonials" ref="testimonialsRef">
        <HomeTestimonials />
      </section>
      <section id="home-news" ref="newsRef">
        <HomeNews />
      </section>
      <section id="cta" ref="ctaRef">
        <HomeFinalCta
          @register="openRegistrationDialog"
          @scroll-to-calculator="scrollTo('calculator')"
        />
      </section>
    </main>

    <footer class="home-footer">
      <div class="home-footer__inner">
        <span class="home-footer__copy">© {{ new Date().getFullYear() }} Зелёный счёт. Вывоз и учёт вторичного сырья.</span>
        <div class="home-footer__links">
          <a href="#" @click.prevent="scrollTo('calculator')">Калькулятор</a>
          <RouterLink to="/products">Товары за баллы</RouterLink>
          <a href="#" @click.prevent="openRegistrationDialog">Регистрация</a>
          <a href="#" @click.prevent="goToLogin">Войти</a>
        </div>
      </div>
    </footer>

    <HomeRegistrationModal v-model="registrationDialog" @success="onRegistrationSuccess" />

    <Teleport to="body">
      <div v-if="registrationSuccess" class="home-snackbar home-snackbar--success">
        Заявка отправлена. Мы свяжемся с вами после рассмотрения.
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute, RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUserStore } from '@/stores/user'
import HomeHero from '@/components/home/HomeHero.vue'
import HomeMaterialsShowcase from '@/components/home/HomeMaterialsShowcase.vue'
import HomePickupCalculator from '@/components/home/HomePickupCalculator.vue'
import HomeTrustStrip from '@/components/home/HomeTrustStrip.vue'
import HomeRegistrationModal from '@/components/home/HomeRegistrationModal.vue'
import HomeForWhom from '@/components/home/HomeForWhom.vue'
import HomeHowItWorks from '@/components/home/HomeHowItWorks.vue'
import HomeBenefits from '@/components/home/HomeBenefits.vue'
import HomeProductsShowcase from '@/components/home/HomeProductsShowcase.vue'
import PublicSiteHeader from '@/components/PublicSiteHeader.vue'
import HomeTestimonials from '@/components/home/HomeTestimonials.vue'
import HomeNews from '@/components/home/HomeNews.vue'
import HomeFinalCta from '@/components/home/HomeFinalCta.vue'
const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const userStore = useUserStore()

const materialsRef = ref<HTMLElement | null>(null)
const calculatorRef = ref<HTMLElement | null>(null)
const forWhomRef = ref<HTMLElement | null>(null)
const howRef = ref<HTMLElement | null>(null)
const benefitsRef = ref<HTMLElement | null>(null)
const productsRef = ref<HTMLElement | null>(null)
const testimonialsRef = ref<HTMLElement | null>(null)
const newsRef = ref<HTMLElement | null>(null)
const ctaRef = ref<HTMLElement | null>(null)

function scrollTo(id: string) {
  const map: Record<string, typeof calculatorRef> = {
    materials: materialsRef,
    calculator: calculatorRef,
    'for-whom': forWhomRef,
    how: howRef,
    benefits: benefitsRef,
    products: productsRef,
    news: newsRef,
    cta: ctaRef,
  }
  const el = map[id]?.value
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

const registrationDialog = ref(false)
const registrationSuccess = ref(false)

function openRegistrationDialog() {
  registrationDialog.value = true
}

function onRegistrationSuccess() {
  registrationSuccess.value = true
  setTimeout(() => { registrationSuccess.value = false }, 4000)
}

onMounted(() => {
  const hash = route.hash?.replace('#', '')
  if (hash) setTimeout(() => scrollTo(hash), 300)
})

async function goToLogin() {
  if (authStore.isAuthenticated) {
    await userStore.fetchMe().catch(() => authStore.logout())
    const role = userStore.role
    if (role === 'admin') router.push({ name: 'AdminDashboard' })
    else if (role === 'company') router.push({ name: 'CompanyDashboard' })
    else if (role === 'institution') router.push({ name: 'InstitutionDashboard' })
    else if (role === 'support') router.push({ name: 'SupportDashboard' })
    else router.push({ name: 'Login' })
  } else {
    router.push({ name: 'Login' })
  }
}
</script>

<style scoped lang="scss">
.home-page__main {
  padding-top: 64px;
}

.home-footer {
  background: var(--vuvoz-text);
  color: rgba(255, 255, 255, 0.8);
  padding: 1.5rem;
}

.home-footer__inner {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.home-footer__copy {
  font-size: 0.9rem;
}

.home-footer__links {
  display: flex;
  gap: 1rem;
  a {
    color: rgba(255, 255, 255, 0.8);
    text-decoration: none;
    font-size: 0.9rem;
    &:hover { color: #fff; }
  }
}

.home-modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 1rem;
}

@media (max-width: 768px) {
  .home-modal-backdrop--mobile {
    padding: 0;
    align-items: flex-end;
  }
}

.home-modal {
  background: #fff;
  padding: 2rem;
  max-width: 440px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
}

@media (max-width: 768px) {
  .home-modal--mobile {
    max-width: none;
    max-height: 92vh;
    border-radius: var(--vuvoz-radius-lg) var(--vuvoz-radius-lg) 0 0;
    padding: 1.5rem 1rem 2rem;
  }
}

.home-modal__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}

.home-modal__title {
  margin: 0;
  font-size: 1.35rem;
}

.home-modal__close {
  width: 44px;
  height: 44px;
  min-width: 44px;
  min-height: 44px;
  border: none;
  background: var(--vuvoz-surface-muted);
  border-radius: 8px;
  font-size: 1.5rem;
  line-height: 1;
  cursor: pointer;
  color: var(--vuvoz-text);
  &:hover { background: var(--vuvoz-border); }
}

.home-modal__sub {
  margin: 0 0 1.5rem;
  font-size: 0.9rem;
}

.home-modal form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.home-modal__input {
  padding: 0.75rem 1rem;
  border-radius: 10px;
  border: 2px solid var(--vuvoz-border);
  font-size: 16px;
  min-height: 48px;
  &:focus {
    outline: none;
    border-color: var(--vuvoz-primary);
  }
}

.home-modal__textarea {
  resize: vertical;
  min-height: 80px;
}

.home-modal__error {
  color: #dc2626;
  font-size: 0.9rem;
  margin: 0;
}

.home-modal__actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.home-modal__btn {
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

.home-snackbar {
  position: fixed;
  bottom: 2rem;
  left: 50%;
  transform: translateX(-50%);
  padding: 1rem 1.5rem;
  border-radius: 12px;
  font-weight: 500;
  z-index: 10000;
  box-shadow: var(--vuvoz-shadow-xl);
  animation: snackbarIn 0.3s ease;

  &--success {
    background: #059669;
    color: #fff;
  }
}

@keyframes snackbarIn {
  from { opacity: 0; transform: translateX(-50%) translateY(10px); }
  to { opacity: 1; transform: translateX(-50%) translateY(0); }
}
</style>
