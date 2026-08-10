// src/modules/notification/api/notification.api.ts
// Semua API call yang berhubungan dengan Notifications

import http from '../../../app/api'

export interface AppNotification {
  id: string
  user_id: string
  board_id: string
  task_id: string | null
  type: string
  title: string
  message: string
  is_read: boolean
  created_at: string
}

export async function getNotifications(limit = 20, offset = 0): Promise<AppNotification[]> {
  const res = await http.get('/notifications', { params: { limit, offset } })
  const data = res.data?.data ?? res.data ?? {}
  const list = data.notifications ?? []
  return Array.isArray(list) ? list : []
}

export async function getUnreadCount(): Promise<number> {
  const res = await http.get('/notifications/unread-count')
  const data = res.data?.data ?? res.data ?? {}
  return data.count ?? 0
}

export async function markNotificationRead(notificationId: string): Promise<AppNotification> {
  const res = await http.patch(`/notifications/${notificationId}/read`)
  return res.data?.data ?? res.data
}

export async function markAllNotificationsRead(): Promise<void> {
  await http.patch('/notifications/read-all')
}

export async function deleteNotification(notificationId: string): Promise<void> {
  await http.delete(`/notifications/${notificationId}`)
}
