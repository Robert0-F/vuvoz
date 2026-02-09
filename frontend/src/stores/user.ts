import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/api/axios'
import type {
  CurrentUserResponse,
  CompanyProfile,
  InstitutionProfile,
  UserRole,
} from '@/types'

export const useUserStore = defineStore('user', () => {
  const currentUser = ref<CurrentUserResponse | null>(null)

  const user = computed(() => currentUser.value)
  const role = computed(() => currentUser.value?.role ?? null)
  const isAdmin = computed(() => currentUser.value?.role === 'admin')
  const isCompany = computed(() => currentUser.value?.role === 'company')
  const isInstitution = computed(() => currentUser.value?.role === 'institution')
  const profile = computed(() => currentUser.value?.profile ?? null)
  const companyProfile = computed(
    () => (currentUser.value?.role === 'company' ? (currentUser.value.profile as CompanyProfile) : null)
  )
  const institutionProfile = computed(
    () =>
      currentUser.value?.role === 'institution'
        ? (currentUser.value.profile as InstitutionProfile)
        : null
  )

  async function fetchMe() {
    const { data } = await api.get<CurrentUserResponse>('/me/')
    currentUser.value = data
    return data
  }

  function clearUser() {
    currentUser.value = null
  }

  return {
    currentUser,
    user,
    role,
    isAdmin,
    isCompany,
    isInstitution,
    profile,
    companyProfile,
    institutionProfile,
    fetchMe,
    clearUser,
  }
})
