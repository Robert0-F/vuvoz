import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import vuetify from './plugins/vuetify'
import { BRAND_LOGO_URL } from '@/constants/brandLogo'
import './styles/main.scss'

const favicon =
  document.querySelector<HTMLLinkElement>('link[rel="icon"]') ?? document.createElement('link')
favicon.rel = 'icon'
favicon.type = 'image/png'
favicon.href = BRAND_LOGO_URL
if (!favicon.parentElement) document.head.appendChild(favicon)

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(vuetify)
app.mount('#app')
