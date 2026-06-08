import {
  ArcElement,
  BarController,
  BarElement,
  CategoryScale,
  Chart,
  DoughnutController,
  Filler,
  Legend,
  LinearScale,
  LineController,
  LineElement,
  PieController,
  PointElement,
  Tooltip,
} from 'chart.js'

Chart.register(
  ArcElement,
  BarController,
  BarElement,
  CategoryScale,
  DoughnutController,
  Filler,
  Legend,
  LinearScale,
  LineController,
  LineElement,
  PieController,
  PointElement,
  Tooltip,
)

export const CHART_COLORS = [
  '#0d9488', '#059669', '#0ea5e9', '#8b5cf6', '#f59e0b', '#ef4444', '#6366f1', '#14b8a6',
]

export const STATUS_COLORS = {
  new: '#f59e0b',
  accepted: '#0ea5e9',
  completed: '#059669',
  cancelled: '#6b7280',
}

export const SLA_COLORS = ['#059669', '#84cc16', '#f59e0b', '#ef4444']

export function disposeCharts(instances: Chart[]) {
  instances.forEach((c) => c.destroy())
  return [] as Chart[]
}

let drawTimer: ReturnType<typeof setTimeout> | null = null

/** Отложенная отрисовка после mount/layout вкладки v-window (с дебаунсом). */
export function scheduleChartDraw(drawFn: () => void, delayMs = 100) {
  if (drawTimer) clearTimeout(drawTimer)
  drawTimer = setTimeout(() => {
    drawTimer = null
    drawFn()
  }, delayMs)
}

/** Безопасное создание графика: уничтожает предыдущий экземпляр на том же canvas. */
export function createChart(canvas: HTMLCanvasElement, config: ConstructorParameters<typeof Chart>[1]) {
  const existing = Chart.getChart(canvas)
  if (existing) existing.destroy()
  return new Chart(canvas, config)
}
