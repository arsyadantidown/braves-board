// src/modules/timer/api/timer.api.ts
// Semua API call yang berhubungan dengan Task Timer

import http from '../../../app/api'
import type { TimerLog } from '../utils/timer.format'

export async function startTimer(taskId: string, description?: string) {
  const trimmed = description?.trim()
  await http.post(`/tasks/${taskId}/timer/start`, trimmed ? { description: trimmed } : {})
}

export async function stopTimer(taskId: string) {
  await http.post(`/tasks/${taskId}/timer/stop`)
}

export async function pingTimer(taskId: string) {
  await http.post(`/tasks/${taskId}/timer/ping`)
}

export async function confirmTimer(taskId: string) {
  await http.post(`/tasks/${taskId}/timer/confirm`)
}

export async function getTimerLogs(taskId: string): Promise<TimerLog[]> {
  const res = await http.get(`/tasks/${taskId}/timer/logs`)
  const data = res.data?.data ?? res.data ?? {}
  const logs = data.logs ?? []
  return Array.isArray(logs) ? logs : []
}
