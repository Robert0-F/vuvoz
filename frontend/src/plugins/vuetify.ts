import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { aliases, mdi } from 'vuetify/iconsets/mdi'
import '@mdi/font/css/materialdesignicons.css'

export default createVuetify({
  components,
  directives,
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: {
      mdi,
    },
  },
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        dark: false,
        colors: {
          primary: '#0d9488',
          'primary-darken-1': '#0f766e',
          'primary-lighten-1': '#14b8a6',
          secondary: '#0f766e',
          'secondary-darken-1': '#115e59',
          accent: '#f59e0b',
          surface: '#f8fafc',
          'surface-bright': '#ffffff',
          'surface-variant': '#f0fdfa',
          'on-surface': '#0f172a',
          'on-surface-variant': '#334155',
          error: '#dc2626',
          info: '#0ea5e9',
          success: '#059669',
          warning: '#f59e0b',
        },
        variables: {
          'border-opacity': 0.12,
          'shadow-key-umbra-opacity': 0.08,
          'shadow-key-penumbra-opacity': 0.06,
        },
      },
    },
  },
  defaults: {
    VCard: {
      elevation: 0,
      rounded: 'lg',
    },
    VBtn: {
      rounded: 'lg',
    },
  },
})
