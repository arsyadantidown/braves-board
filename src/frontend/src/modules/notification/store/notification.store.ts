import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  getNotifications,
  getUnreadCount,
  markNotificationRead,
  markAllNotificationsRead,
  deleteNotification,
  type AppNotification,
} from '../api/notification.api'

const POLL_INTERVAL_MS = 30000

export const useNotificationStore = defineStore('notification', () => {
  const notifications = ref<AppNotification[]>([])
  const unreadCount = ref(0)
  const loading = ref(false)
  let pollInterval: ReturnType<typeof setInterval> | null = null

  async function fetchNotifications() {
    loading.value = true
    try {
      notifications.value = await getNotifications()
    } finally {
      loading.value = false
    }
  }

  async function refreshUnreadCount() {
    unreadCount.value = await getUnreadCount()
  }

  async function markAsRead(notificationId: string) {
    await markNotificationRead(notificationId)
    const n = notifications.value.find(x => x.id === notificationId)
    if (n && !n.is_read) {
      n.is_read = true
      unreadCount.value = Math.max(0, unreadCount.value - 1)
    }
  }

  async function markAllAsRead() {
    await markAllNotificationsRead()
    notifications.value.forEach(n => { n.is_read = true })
    unreadCount.value = 0
  }

  async function removeNotification(notificationId: string) {
    await deleteNotification(notificationId)
    const n = notifications.value.find(x => x.id === notificationId)
    notifications.value = notifications.value.filter(x => x.id !== notificationId)
    if (n && !n.is_read) unreadCount.value = Math.max(0, unreadCount.value - 1)
  }

  // Idempotent — AppLayout (dan bel notifikasi di dalamnya) di-mount ulang
  // tiap kali pindah halaman (tiap view bungkus <AppLayout> sendiri-sendiri,
  // bukan layout persisten via router-view), jadi startPolling() bisa
  // dipanggil berkali-kali. Guard di sini supaya interval tidak dobel.
  function startPolling() {
    if (pollInterval) return
    refreshUnreadCount().catch(() => { })
    pollInterval = setInterval(() => {
      refreshUnreadCount().catch(() => { })
    }, POLL_INTERVAL_MS)
  }

  function stopPolling() {
    if (pollInterval) { clearInterval(pollInterval); pollInterval = null }
  }

  return {
    notifications, unreadCount, loading,
    fetchNotifications, refreshUnreadCount,
    markAsRead, markAllAsRead, removeNotification,
    startPolling, stopPolling,
  }
})
