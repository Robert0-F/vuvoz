<template>
  <div class="home-page">
    <header class="home-nav">
      <div class="home-nav__inner">
        <a href="/" class="home-nav__logo">Vuvoz</a>
        <button
          type="button"
          class="home-nav__burger"
          aria-label="Меню"
          :aria-expanded="mobileMenuOpen"
          @click="mobileMenuOpen = !mobileMenuOpen"
        >
          <span /><span /><span />
        </button>
        <nav class="home-nav__links" :class="{ 'home-nav__links--open': mobileMenuOpen }">
          <a href="#" @click.prevent="scrollTo('calculator'); mobileMenuOpen = false">Калькулятор</a>
          <a href="#" @click.prevent="scrollTo('for-whom'); mobileMenuOpen = false">Для кого</a>
          <a href="#" @click.prevent="scrollTo('how'); mobileMenuOpen = false">Как работает</a>
          <a href="#" @click.prevent="scrollTo('benefits'); mobileMenuOpen = false">Преимущества</a>
          <a href="#" @click.prevent="scrollTo('news'); mobileMenuOpen = false">Новости</a>
          <a href="#" @click.prevent="scrollTo('cta'); mobileMenuOpen = false">Контакты</a>
        </nav>
        <div class="home-nav__actions">
          <button type="button" class="home-nav__btn home-nav__btn--outline" @click="openRegistrationDialog">
            Регистрация
          </button>
          <button type="button" class="home-nav__btn home-nav__btn--primary" @click="goToLogin">
            Войти
          </button>
        </div>
      </div>
    </header>

    <main>
      <HomeHero
        @scroll-to-calculator="scrollTo('calculator')"
        @scroll-to-process="scrollTo('how')"
      />
      <section id="calculator" ref="calculatorRef">
        <HomeCalculator />
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
        <span class="home-footer__copy">© {{ new Date().getFullYear() }} Vuvoz. Вывоз макулатуры и переработка.</span>
        <div class="home-footer__links">
          <a href="#" @click.prevent="scrollTo('calculator')">Калькулятор</a>
          <a href="#" @click.prevent="openRegistrationDialog">Регистрация</a>
          <a href="#" @click.prevent="goToLogin">Войти</a>
        </div>
      </div>
    </footer>

    <!-- Registration modal -->
    <Teleport to="body">
      <div v-if="registrationDialog" class="home-modal-backdrop" @click.self="registrationDialog = false">
        <div class="home-modal hp-card">
          <div class="home-modal__head">
            <h2 class="home-modal__title">Заявка на регистрацию учреждения</h2>
            <button type="button" class="home-modal__close" aria-label="Закрыть" @click="registrationDialog = false">×</button>
          </div>
          <p class="hp-subtitle home-modal__sub">Заполните форму — администратор свяжется с вами и подключит организацию.</p>
          <form @submit.prevent="submitRegistration">
            <input
              v-model="registrationForm.first_name"
              type="text"
              class="home-modal__input"
              placeholder="Имя *"
              required
            />
            <input
              v-model="registrationForm.patronymic"
              type="text"
              class="home-modal__input"
              placeholder="Отчество"
            />
            <input
              v-model="registrationForm.institution_name"
              type="text"
              class="home-modal__input"
              placeholder="Название учреждения *"
              required
            />
            <textarea
              v-model="registrationForm.address"
              class="home-modal__input home-modal__textarea"
              placeholder="Адрес *"
              rows="2"
              required
            />
            <input
              v-model="registrationForm.phone"
              type="tel"
              class="home-modal__input"
              placeholder="Телефон *"
              required
            />
            <p v-if="registrationError" class="home-modal__error">Не удалось отправить. Попробуйте позже.</p>
            <div class="home-modal__actions">
              <button type="button" class="home-modal__btn home-modal__btn--secondary" @click="registrationDialog = false">
                Отмена
              </button>
              <button type="submit" class="home-modal__btn home-modal__btn--primary" :disabled="registrationSending">
                {{ registrationSending ? 'Отправка…' : 'Отправить заявку' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <Teleport to="body">
      <div v-if="registrationSuccess" class="home-snackbar home-snackbar--success">
        Заявка отправлена. Мы свяжемся с вами после рассмотрения.
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/api/axios'
import { useAuthStore } from '@/stores/auth'
import { useUserStore } from '@/stores/user'
import HomeHero from '@/components/home/HomeHero.vue'
import HomeCalculator from '@/components/home/HomeCalculator.vue'
import HomeForWhom from '@/components/home/HomeForWhom.vue'
import HomeHowItWorks from '@/components/home/HomeHowItWorks.vue'
import HomeBenefits from '@/components/home/HomeBenefits.vue'
import HomeTestimonials from '@/components/home/HomeTestimonials.vue'
import HomeNews from '@/components/home/HomeNews.vue'
import HomeFinalCta from '@/components/home/HomeFinalCta.vue'

const router = useRouter()
const authStore = useAuthStore()
const userStore = useUserStore()

const calculatorRef = ref<HTMLElement | null>(null)
const forWhomRef = ref<HTMLElement | null>(null)
const howRef = ref<HTMLElement | null>(null)
const benefitsRef = ref<HTMLElement | null>(null)
const testimonialsRef = ref<HTMLElement | null>(null)
const newsRef = ref<HTMLElement | null>(null)
const ctaRef = ref<HTMLElement | null>(null)

function scrollTo(id: string) {
  const map: Record<string, typeof calculatorRef> = {
    calculator: calculatorRef,
    'for-whom': forWhomRef,
    how: howRef,
    benefits: benefitsRef,
    news: newsRef,
    cta: ctaRef,
  }
  const el = map[id]?.value
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

const mobileMenuOpen = ref(false)
const registrationDialog = ref(false)
const registrationSending = ref(false)
const registrationSuccess = ref(false)
const registrationError = ref(false)
const registrationForm = reactive({
  first_name: '',
  patronymic: '',
  institution_name: '',
  address: '',
  phone: '',
})

function openRegistrationDialog() {
  registrationForm.first_name = ''
  registrationForm.patronymic = ''
  registrationForm.institution_name = ''
  registrationForm.address = ''
  registrationForm.phone = ''
  registrationError.value = false
  registrationDialog.value = true
}

async function submitRegistration() {
  registrationSending.value = true
  registrationError.value = false
  try {
    await api.post('/registration-requests/', {
      first_name: registrationForm.first_name.trim(),
      patronymic: registrationForm.patronymic.trim(),
      institution_name: registrationForm.institution_name.trim(),
      address: registrationForm.address.trim(),
      phone: registrationForm.phone.trim(),
    })
    registrationSuccess.value = true
    registrationDialog.value = false
    setTimeout(() => { registrationSuccess.value = false }, 4000)
  } catch {
    registrationError.value = true
  } finally {
    registrationSending.value = false
  }
}

async function goToLogin() {
  if (authStore.isAuthenticated) {
    await userStore.fetchMe().catch(() => authStore.logout())
    const role = userStore.role
    if (role === 'admin') router.push({ name: 'AdminDashboard' })
    else if (role === 'company') router.push({ name: 'CompanyDashboard' })
    else if (role === 'institution') router.push({ name: 'InstitutionDashboard' })
    else router.push({ name: 'Login' })
  } else {
    router.push({ name: 'Login' })
  }
}
</script>

<style scoped lang="scss">
.home-nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--vuvoz-border);
}

.home-nav__inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0.75rem 1.5rem;
  display: flex;
  align-items: center;
  gap: 2rem;
}

.home-nav__logo {
  font-family: var(--hp-font-heading);
  font-weight: 800;
  font-size: 1.35rem;
  color: var(--vuvoz-primary);
  text-decoration: none;
  letter-spacing: -0.02em;
}

.home-nav__burger {
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

.home-nav__links {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem 1.5rem;
  a {
    font-size: 0.9rem;
    font-weight: 500;
    color: var(--vuvoz-text);
    text-decoration: none;
    padding: 0.35rem 0.5rem;
    border-radius: 8px;
    &:hover { color: var(--vuvoz-primary); background: rgba(13, 148, 136, 0.06); }
  }
}

.home-nav__actions {
  margin-left: auto;
  display: flex;
  gap: 0.5rem;
}

.home-nav__btn {
  font-family: var(--hp-font-heading);
  font-weight: 600;
  font-size: 0.9rem;
  padding: 0.5rem 1rem;
  border-radius: 10px;
  cursor: pointer;
  border: 2px solid transparent;
  transition: background 0.2s, color 0.2s;

  &--outline {
    border-color: var(--vuvoz-primary);
    background: transparent;
    color: var(--vuvoz-primary);
    &:hover { background: rgba(13, 148, 136, 0.08); }
  }

  &--primary {
    background: var(--vuvoz-primary);
    color: #fff;
    &:hover { background: #0f766e; }
  }
}

@media (max-width: 768px) {
  .home-nav__burger { display: flex; }
  .home-nav__links {
    display: none;
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: #fff;
    border-bottom: 1px solid var(--vuvoz-border);
    flex-direction: column;
    padding: 1rem;
    &--open {
      display: flex;
    }
  }
  .home-nav__actions .home-nav__btn--outline { display: none; }
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

.home-modal {
  background: #fff;
  padding: 2rem;
  max-width: 440px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
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
  width: 36px;
  height: 36px;
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
  font-size: 1rem;
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
