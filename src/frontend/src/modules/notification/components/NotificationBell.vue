<template>
  <div class="relative">
    <button @click.stop="toggleOpen"
      class="w-8 h-8 flex items-center justify-center rounded-full border border-gray-300 hover:bg-gray-50 transition text-gray-600 relative">
      <font-awesome-icon icon="bell" class="text-sm" />
      <span v-if="unreadCount > 0"
        class="absolute -top-1 -right-1 min-w-[16px] h-4 px-1 rounded-full bg-red-500 text-white text-[10px] font-bold flex items-center justify-center leading-none">
        {{ unreadCount > 99 ? '99+' : unreadCount }}
      </span>
    </button>

    <div v-if="open" @click.stop
      class="absolute right-0 top-10 bg-white border border-gray-200 rounded-xl shadow-xl z-30 w-80 max-h-[28rem] flex flex-col overflow-hidden">
      <div class="flex items-center justify-between px-4 py-2.5 border-b border-gray-100 flex-shrink-0">
        <p class="text-sm font-semibold text-gray-800">Notifications</p>
        <button v-if="unreadCount > 0" @click="handleMarkAllRead"
          class="text-xs text-blue-500 hover:text-blue-600 transition">Mark all as read</button>
      </div>

      <div class="flex-1 overflow-y-auto">
        <p v-if="loading" class="text-xs text-gray-400 text-center py-6">Memuat…</p>
        <p v-else-if="!notifications.length" class="text-xs text-gray-400 text-center py-6">Belum ada notifikasi.</p>

        <div v-else v-for="n in notifications" :key="n.id"
          class="flex items-start gap-2.5 px-4 py-3 border-b border-gray-50 hover:bg-gray-50 transition cursor-pointer group"
          :class="!n.is_read ? 'bg-blue-50/40' : ''" @click="handleOpenNotification(n)">
          <div class="w-7 h-7 rounded-full flex items-center justify-center text-[11px] flex-shrink-0 mt-0.5"
            :class="typeStyle(n.type).badge">
            <font-awesome-icon :icon="typeStyle(n.type).icon" />
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-xs font-semibold text-gray-800">{{ n.title }}</p>
            <p class="text-xs text-gray-500 mt-0.5 leading-snug">{{ n.message }}</p>
            <p class="text-[10px] text-gray-400 mt-1">{{ timeAgo(n.created_at) }}</p>
          </div>
          <div class="flex flex-col items-end gap-1 flex-shrink-0">
            <span v-if="!n.is_read" class="w-2 h-2 rounded-full bg-blue-500 flex-shrink-0" title="Belum dibaca"></span>
            <button @click.stop="handleDelete(n.id)"
              class="opacity-0 group-hover:opacity-100 text-gray-300 hover:text-red-400 transition text-xs">✕</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { library } from '@fortawesome/fontawesome-svg-core'
import {
  faBell, faPlus, faPen, faArrowRight, faTrash, faCheckSquare, faComment, faPaperclip,
} from '@fortawesome/free-solid-svg-icons'
import { useNotificationStore } from '../store/notification.store'
import type { AppNotification } from '../api/notification.api'

library.add(faBell, faPlus, faPen, faArrowRight, faTrash, faCheckSquare, faComment, faPaperclip)

const router = useRouter()
const store = useNotificationStore()
const { notifications, unreadCount, loading } = storeToRefs(store)

const open = ref(false)

function toggleOpen() {
  const next = !open.value
  open.value = next
  if (next) store.fetchNotifications()
}

function closeOnOutsideClick() {
  open.value = false
}

onMounted(() => {
  store.startPolling()
  document.addEventListener('click', closeOnOutsideClick)
})

onUnmounted(() => {
  document.removeEventListener('click', closeOnOutsideClick)
})

function typeStyle(type: string): { icon: string; badge: string } {
  switch (type) {
    case 'task_created': return { icon: 'plus', badge: 'bg-emerald-100 text-emerald-600' }
    case 'task_updated': return { icon: 'pen', badge: 'bg-blue-100 text-blue-600' }
    case 'task_moved': return { icon: 'arrow-right', badge: 'bg-purple-100 text-purple-600' }
    case 'task_deleted': return { icon: 'trash', badge: 'bg-red-100 text-red-600' }
    case 'subtask_created': return { icon: 'check-square', badge: 'bg-emerald-100 text-emerald-600' }
    case 'subtask_updated': return { icon: 'check-square', badge: 'bg-blue-100 text-blue-600' }
    case 'subtask_completed': return { icon: 'check-square', badge: 'bg-emerald-100 text-emerald-600' }
    case 'comment_created': return { icon: 'comment', badge: 'bg-amber-100 text-amber-600' }
    case 'attachment_added': return { icon: 'paperclip', badge: 'bg-gray-100 text-gray-600' }
    default: return { icon: 'bell', badge: 'bg-gray-100 text-gray-600' }
  }
}

function timeAgo(iso: string): string {
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return '-'
  const diffSec = Math.max(0, Math.floor((Date.now() - d.getTime()) / 1000))
  if (diffSec < 60) return 'Baru saja'
  const diffMin = Math.floor(diffSec / 60)
  if (diffMin < 60) return `${diffMin} menit lalu`
  const diffHour = Math.floor(diffMin / 60)
  if (diffHour < 24) return `${diffHour} jam lalu`
  const diffDay = Math.floor(diffHour / 24)
  if (diffDay < 7) return `${diffDay} hari lalu`
  return d.toLocaleDateString('id-ID', { day: '2-digit', month: 'short', year: 'numeric' })
}

async function handleMarkAllRead() {
  try {
    await store.markAllAsRead()
  } catch { /* biarkan badge apa adanya kalau request gagal */ }
}

async function handleDelete(id: string) {
  try {
    await store.removeNotification(id)
  } catch { /* no-op — entry tetap tampil kalau delete gagal */ }
}

async function handleOpenNotification(n: AppNotification) {
  if (!n.is_read) {
    try { await store.markAsRead(n.id) } catch { /* navigasi tetap lanjut walau mark-read gagal */ }
  }
  open.value = false
  router.push({
    path: `/boards/${n.board_id}`,
    query: n.task_id ? { taskId: n.task_id } : {},
  })
}
</script>
