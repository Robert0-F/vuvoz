import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/api/axios'
import type { TokenResponse } from '@/types'

const ACCESS_KEY = 'access_token'
const REFRESH_KEY = 'refresh_token'

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref<string | null>(localStorage.getItem(ACCESS_KEY))
  const refreshToken = ref<string | null>(localStorage.getItem(REFRESH_KEY))

  const isAuthenticated = computed(() => !!accessToken.value)

  function setTokens(data: TokenResponse) {
    accessToken.value = data.access
    refreshToken.value = data.refresh
    localStorage.setItem(ACCESS_KEY, data.access)
    localStorage.setItem(REFRESH_KEY, data.refresh)
  }

  function clearTokens() {
    accessToken.value = null
    refreshToken.value = null
    localStorage.removeItem(ACCESS_KEY)
    localStorage.removeItem(REFRESH_KEY)
  }

  async function login(username: string, password: string) {
    const { data } = await api.post<TokenResponse>('/token/', { username, password })
    setTokens(data)
    return data
  }

  function logout() {
    clearTokens()
  }

  return {
    accessToken,
    refreshToken,
    isAuthenticated,
    login,
    logout,
    setTokens,
    clearTokens,
  }
})
