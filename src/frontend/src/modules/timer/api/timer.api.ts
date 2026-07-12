// src/services/timerService.ts
// Semua API call yang berhubungan dengan Task Timer

import http from '../../../app/api'

export async function startTimer(taskId: string) {
  await http.post(`/tasks/${taskId}/timer/start`)
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

export async function getTimerLogs(taskId: string) {
  const res = await http.get(`/tasks/${taskId}/timer/logs`)
  const data = res.data?.data ?? res.data ?? {}
  const logs = data.logs ?? []
  return Array.isArray(logs) ? logs : []
}