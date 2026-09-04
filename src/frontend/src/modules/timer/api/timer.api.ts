// src/modules/timer/api/timer.api.ts
// Semua API call yang berhubungan dengan Task Timer

import http from '../../../app/api'
import type { TimerLog } from '../utils/timer.format'

// Backend: require_permission() butuh board_id, tapi endpoint /tasks/*/timer/*
// tidak mendeklarasikannya di path — FastAPI resolve sebagai query param
// wajib. Semua call di bawah HARUS menyertakan board_id.

export async function startTimer(taskId: string, boardId: string, description?: string) {
  const trimmed = description?.trim()
  await http.post(`/tasks/${taskId}/timer/start`, trimmed ? { description: trimmed } : {}, {
    params: { board_id: boardId },
  })
}

export async function stopTimer(taskId: string, boardId: string) {
  await http.post(`/tasks/${taskId}/timer/stop`, {}, { params: { board_id: boardId } })
}

export async function pingTimer(taskId: string, boardId: string) {
  await http.post(`/tasks/${taskId}/timer/ping`, {}, { params: { board_id: boardId } })
}

export async function confirmTimer(taskId: string, boardId: string) {
  await http.post(`/tasks/${taskId}/timer/confirm`, {}, { params: { board_id: boardId } })
}

export async function getTimerLogs(taskId: string, boardId: string): Promise<TimerLog[]> {
  const res = await http.get(`/tasks/${taskId}/timer/logs`, { params: { board_id: boardId } })
  const data = res.data?.data ?? res.data ?? {}
  const logs = data.logs ?? []
  return Array.isArray(logs) ? logs : []
}

export interface TimeLogUpdatePayload {
  start_time?: string
  stop_time?: string
  activity_description?: string
}

// Edit satu time log. Backend: PATCH /tasks/{task_id}/timer/logs/{log_id}
// (semua field opsional). duration_seconds DIHITUNG ULANG oleh backend, dan
// HANYA saat stop_time ikut dikirim — karena itu pemanggil sebaiknya kirim
// start_time + stop_time bersamaan supaya durasi selalu konsisten.
export async function updateTimeLog(
  taskId: string,
  logId: string,
  boardId: string,
  payload: TimeLogUpdatePayload,
): Promise<TimerLog> {
  const res = await http.patch(`/tasks/${taskId}/timer/logs/${logId}`, payload, {
    params: { board_id: boardId },
  })
  return res.data?.data ?? res.data
}

// Hapus satu time log. Backend: DELETE /tasks/{task_id}/timer/logs/{log_id}.
export async function deleteTimeLog(taskId: string, logId: string, boardId: string): Promise<void> {
  await http.delete(`/tasks/${taskId}/timer/logs/${logId}`, { params: { board_id: boardId } })
}
