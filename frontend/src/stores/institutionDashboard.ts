import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/api/axios'
import type { CollectionRequest, PointsHistoryItem } from '@/types'

export const useInstitutionDashboardStore = defineStore('institutionDashboard', () => {
  const requests = ref<CollectionRequest[]>([])
  const loadingRequests = ref(false)
  const pointsData = ref<{ balance: string; history: PointsHistoryItem[] }>({ balance: '0', history: [] })
  const loadingPoints = ref(false)
  const stats = ref<{
    total_requests: number
    requests_by_status: Record<string, number>
    total_weight_all_time: number | string
    total_weight_this_month: number | string
  } | null>(null)
  const loadingStats = ref(false)

  const totalWeight = computed(() => {
    return requests.value
      .filter((r) => r.status === 'completed')
      .reduce((sum, r) => sum + parseFloat(String(r.actual_amount || r.estimated_amount || r.paper_weight_kg || 0)), 0)
  })

  const activeRequests = computed(() => requests.value.filter((r) => r.status !== 'completed'))
  const completedRequests = computed(() => requests.value.filter((r) => r.status === 'completed'))

  async function fetchRequests() {
    loadingRequests.value = true
    try {
      const { data } = await api.get<CollectionRequest[]>('/collection-requests/')
      requests.value = data
    } finally {
      loadingRequests.value = false
    }
  }

  async function fetchPoints() {
    loadingPoints.value = true
    try {
      const { data } = await api.get<{ balance: string; history: PointsHistoryItem[] }>('/me/points/')
      pointsData.value = { balance: data.balance, history: data.history || [] }
    } catch {
      pointsData.value = { balance: '0', history: [] }
    } finally {
      loadingPoints.value = false
    }
  }

  async function fetchStats(params?: { start_date?: string; end_date?: string }) {
    loadingStats.value = true
    try {
      const { data } = await api.get<typeof stats.value>('/stats/institution/', { params })
      stats.value = data
    } catch {
      stats.value = null
    } finally {
      loadingStats.value = false
    }
  }

  return {
    requests,
    loadingRequests,
    pointsData,
    loadingPoints,
    stats,
    loadingStats,
    totalWeight,
    activeRequests,
    completedRequests,
    fetchRequests,
    fetchPoints,
    fetchStats,
  }
})
