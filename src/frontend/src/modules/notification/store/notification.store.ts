import { defineStore } from "pinia";
import { ref } from "vue";
import {
  getNotifications,
  getUnreadCount,
  markNotificationRead,
  markAllNotificationsRead,
  deleteNotification,
  type AppNotification,
} from "../api/notification.api";

// Polling interval cerdas: 12 detik (hanya 5 request per menit)
const POLL_INTERVAL_MS = 12000;

export const useNotificationStore = defineStore("notification", () => {
  const notifications = ref<AppNotification[]>([]);
  const unreadCount = ref(0);
  const loading = ref(false);
  const isDropdownOpen = ref(false);

  let pollInterval: ReturnType<typeof setInterval> | null = null;
  let isListenerAttached = false;

  async function fetchNotifications(silent = false) {
    if (!silent) loading.value = true;
    try {
      notifications.value = await getNotifications();
    } finally {
      if (!silent) loading.value = false;
    }
  }

  async function refreshUnreadCount() {
    try {
      unreadCount.value = await getUnreadCount();
    } catch {
      // Abaikan error jaringan sementara
    }
  }

  async function markAsRead(notificationId: string) {
    await markNotificationRead(notificationId);
    const n = notifications.value.find((x) => x.id === notificationId);
    if (n && !n.is_read) {
      n.is_read = true;
      unreadCount.value = Math.max(0, unreadCount.value - 1);
    }
  }

  async function markAllAsRead() {
    await markAllNotificationsRead();
    notifications.value.forEach((n) => {
      n.is_read = true;
    });
    unreadCount.value = 0;
  }

  async function removeNotification(notificationId: string) {
    await deleteNotification(notificationId);
    const n = notifications.value.find((x) => x.id === notificationId);
    notifications.value = notifications.value.filter(
      (x) => x.id !== notificationId,
    );
    if (n && !n.is_read) unreadCount.value = Math.max(0, unreadCount.value - 1);
  }

  function handleVisibilityOrFocus() {
    if (
      typeof document !== "undefined" &&
      document.visibilityState === "visible"
    ) {
      refreshUnreadCount();
      if (isDropdownOpen.value) {
        fetchNotifications(true);
      }
    }
  }

  function startPolling() {
    // 1. Fetch awal langsung saat app/komponen mount
    refreshUnreadCount();

    // 2. Jalankan interval hanya jika belum berjalan
    if (!pollInterval) {
      pollInterval = setInterval(() => {
        // Hanya tembak polling jika tab browser sedang dibuka/dilihat user
        if (
          typeof document !== "undefined" &&
          document.visibilityState === "visible"
        ) {
          refreshUnreadCount();
          if (isDropdownOpen.value) {
            fetchNotifications(true);
          }
        }
      }, POLL_INTERVAL_MS);
    }

    // 3. Pasang listener focus/tab switch (hanya 1x)
    if (!isListenerAttached && typeof window !== "undefined") {
      window.addEventListener("focus", handleVisibilityOrFocus);
      document.addEventListener("visibilitychange", handleVisibilityOrFocus);
      isListenerAttached = true;
    }
  }

  function stopPolling() {
    if (pollInterval) {
      clearInterval(pollInterval);
      pollInterval = null;
    }
  }

  return {
    notifications,
    unreadCount,
    loading,
    isDropdownOpen,
    fetchNotifications,
    refreshUnreadCount,
    markAsRead,
    markAllAsRead,
    removeNotification,
    startPolling,
    stopPolling,
  };
});
