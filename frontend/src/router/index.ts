import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUserStore } from '@/stores/user'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/LoginPage.vue'),
      meta: { guest: true },
    },
    {
      path: '/company',
      name: 'CompanyDashboard',
      component: () => import('@/views/CompanyDashboard.vue'),
      meta: { requiresAuth: true, role: 'company' },
    },
    {
      path: '/institution',
      name: 'InstitutionDashboard',
      component: () => import('@/views/InstitutionDashboard.vue'),
      meta: { requiresAuth: true, role: 'institution' },
    },
    {
      path: '/',
      redirect: () => '/login',
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/login',
    },
  ],
})

router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore()
  const userStore = useUserStore()

  if (to.meta.guest) {
    if (authStore.isAuthenticated) {
      await userStore.fetchMe().catch(() => authStore.logout())
      const role = userStore.role
      if (role === 'company') next({ name: 'CompanyDashboard' })
      else if (role === 'institution') next({ name: 'InstitutionDashboard' })
      else next()
    } else {
      next()
    }
    return
  }

  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      next({ name: 'Login', query: { redirect: to.fullPath } })
      return
    }
    if (!userStore.currentUser) {
      try {
        await userStore.fetchMe()
      } catch {
        authStore.logout()
        next({ name: 'Login' })
        return
      }
    }
    const requiredRole = to.meta.role as string | undefined
    if (requiredRole && userStore.role !== requiredRole) {
      if (userStore.role === 'company') next({ name: 'CompanyDashboard' })
      else if (userStore.role === 'institution') next({ name: 'InstitutionDashboard' })
      else next({ name: 'Login' })
      return
    }
  }

  next()
})

export default router
