<template>
  <AppLayout>
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-800 dark:text-gray-100">Time Tracker</h1>
      <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">Riwayat waktu kerja dari card yang melibatkan Anda.</p>
    </div>

    <!-- Active timer bar -->
    <div v-if="activeTaskId" class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-emerald-200 dark:border-emerald-700 mb-6 px-5 py-4 flex items-center gap-4">
      <span class="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse flex-shrink-0" />
      <div class="flex-1 min-w-0">
        <p class="text-sm font-medium text-gray-800 dark:text-gray-100 truncate">{{ activeTaskTitle || 'Task' }}</p>
        <p class="text-xs text-gray-400 dark:text-gray-500">{{ activeBoardTitle }}</p>
      </div>
      <span class="text-lg font-mono font-bold text-emerald-600 tabular-nums">{{ formatTimer(elapsed) }}</span>
      <button @click="handleStopActiveTimer" :disabled="stopLoading"
        class="px-4 py-2 rounded-xl text-sm font-semibold bg-red-500 hover:bg-red-600 text-white transition disabled:opacity-50">
        {{ stopLoading ? '...' : 'Stop' }}
      </button>
    </div>

    <!-- Filters -->
    <div class="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm mb-6 p-4 flex flex-wrap items-end gap-3">
      <div class="min-w-[160px]">
        <label class="block text-[11px] text-gray-400 dark:text-gray-500 mb-1">Board</label>
        <select v-model="filterBoardId"
          class="w-full text-sm border border-gray-200 dark:border-gray-600 rounded-lg px-2.5 py-1.5 outline-none focus:border-blue-400 transition bg-white dark:bg-gray-700 dark:text-gray-100">
          <option value="">Semua board</option>
          <option v-for="b in boards" :key="b.id" :value="b.id">{{ b.title }}</option>
        </select>
      </div>

      <div class="min-w-[140px]">
        <label class="block text-[11px] text-gray-400 dark:text-gray-500 mb-1">Rentang tanggal</label>
        <select v-model="datePreset"
          class="w-full text-sm border border-gray-200 dark:border-gray-600 rounded-lg px-2.5 py-1.5 outline-none focus:border-blue-400 transition bg-white dark:bg-gray-700 dark:text-gray-100">
          <option value="all">Semua waktu</option>
          <option value="today">Hari ini</option>
          <option value="week">Minggu ini</option>
          <option value="month">Bulan ini</option>
          <option value="custom">Custom</option>
        </select>
      </div>

      <template v-if="datePreset === 'custom'">
        <div>
          <label class="block text-[11px] text-gray-400 dark:text-gray-500 mb-1">Dari</label>
          <input type="date" v-model="customStart"
            class="text-sm border border-gray-200 dark:border-gray-600 rounded-lg px-2.5 py-1.5 outline-none focus:border-blue-400 transition bg-white dark:bg-gray-700 dark:text-gray-100" />
        </div>
        <div>
          <label class="block text-[11px] text-gray-400 dark:text-gray-500 mb-1">Sampai</label>
          <input type="date" v-model="customEnd"
            class="text-sm border border-gray-200 dark:border-gray-600 rounded-lg px-2.5 py-1.5 outline-none focus:border-blue-400 transition bg-white dark:bg-gray-700 dark:text-gray-100" />
        </div>
      </template>

      <div v-if="availableTags.length" class="min-w-[140px]">
        <label class="block text-[11px] text-gray-400 dark:text-gray-500 mb-1">Tag</label>
        <select v-model="filterTag"
          class="w-full text-sm border border-gray-200 dark:border-gray-600 rounded-lg px-2.5 py-1.5 outline-none focus:border-blue-400 transition bg-white dark:bg-gray-700 dark:text-gray-100">
          <option value="">Semua tag</option>
          <option v-for="tag in availableTags" :key="tag" :value="tag">{{ tag }}</option>
        </select>
      </div>

      <div class="flex-1 min-w-[180px]">
        <label class="block text-[11px] text-gray-400 dark:text-gray-500 mb-1">Cari task</label>
        <input v-model="searchQuery" type="text" placeholder="Nama task..."
          class="w-full text-sm border border-gray-200 dark:border-gray-600 rounded-lg px-2.5 py-1.5 outline-none focus:border-blue-400 transition placeholder-gray-400 bg-white dark:bg-gray-700 dark:text-gray-100" />
      </div>

      <div class="ml-auto text-right">
        <p class="text-[11px] text-gray-400 dark:text-gray-500 mb-1">Total</p>
        <p class="text-lg font-bold text-gray-800 dark:text-gray-100 font-mono tabular-nums">{{ formatTimer(filteredTotalSeconds) }}</p>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center h-40 text-gray-400 gap-2 text-sm">
      <svg class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
      </svg>
      Loading...
    </div>

    <!-- Empty -->
    <div v-else-if="!dayGroups.length" class="bg-gray-50 dark:bg-gray-800 border border-dashed border-gray-300 dark:border-gray-600 rounded-2xl p-12 text-center">
      <font-awesome-icon icon="clock" class="text-3xl text-gray-300 mb-3 block mx-auto" />
      <p class="text-sm text-gray-500 dark:text-gray-400 font-medium">Belum ada time entry</p>
      <p class="text-xs text-gray-400 dark:text-gray-500 mt-1">Mulai timer dari card di Boards untuk mulai tracking.</p>
    </div>

    <!-- Log groups -->
    <div v-else class="space-y-4">
      <div v-for="group in dayGroups" :key="group.key" class="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm overflow-hidden">
        <div class="flex items-center justify-between px-5 py-3 bg-gray-50 dark:bg-gray-700/40 border-b border-gray-100 dark:border-gray-700">
          <span class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">{{ group.heading }}</span>
          <div class="flex items-center gap-3">
            <span class="text-xs text-gray-400 dark:text-gray-500">Total</span>
            <span class="text-sm font-bold text-gray-700 dark:text-gray-200 font-mono">{{ formatTimer(group.totalSeconds) }}</span>
          </div>
        </div>
        <div class="divide-y divide-gray-50 dark:divide-gray-700/60">
          <div v-for="entry in group.entries" :key="entry.id"
            class="group flex items-center gap-4 px-5 py-3.5 hover:bg-gray-50 dark:hover:bg-gray-700/40 transition">
            <div class="flex-1 min-w-0">
              <router-link :to="`/boards/${entry.boardId}`" class="text-sm text-gray-800 dark:text-gray-100 font-medium truncate block hover:text-blue-600 transition">
                {{ entry.taskTitle }}
              </router-link>
              <div class="flex items-center gap-1.5 mt-0.5 flex-wrap">
                <span class="text-xs text-orange-500">{{ entry.boardTitle }} • {{ entry.columnTitle }}</span>
                <span v-if="entry.activityDescription" class="text-xs text-gray-400 dark:text-gray-500 truncate">— {{ entry.activityDescription }}</span>
                <span v-if="formatStopReason(entry.stopReason)"
                  class="text-[10px] font-medium text-amber-600 bg-amber-50 border border-amber-200 rounded-full px-1.5 py-0.5">
                  {{ formatStopReason(entry.stopReason) }}
                </span>
              </div>
            </div>
            <div class="flex items-center gap-1.5 text-xs text-gray-400 dark:text-gray-500 min-w-[120px] justify-center flex-shrink-0">
              <font-awesome-icon icon="calendar" class="text-gray-300" />
              <span>{{ entry.stopTime ? `${formatClock(entry.startTime)} – ${formatClock(entry.stopTime)}` : `${formatClock(entry.startTime)} – berjalan` }}</span>
            </div>
            <span class="text-sm font-mono font-semibold text-gray-700 dark:text-gray-200 min-w-[70px] text-right flex-shrink-0">
              {{ entry.durationSeconds != null ? formatTimer(entry.durationSeconds) : '—' }}
            </span>
            <div class="flex items-center gap-1 flex-shrink-0 w-[60px] justify-end">
              <template v-if="entry.stopTime">
                <button @click="openEditEntry(entry)" title="Edit entry"
                  class="opacity-0 group-hover:opacity-100 focus:opacity-100 w-7 h-7 flex items-center justify-center rounded-lg text-gray-400 hover:text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-500/20 transition">
                  <font-awesome-icon icon="pen" class="text-xs" />
                </button>
                <button @click="openDeleteEntry(entry)" title="Hapus entry"
                  class="opacity-0 group-hover:opacity-100 focus:opacity-100 w-7 h-7 flex items-center justify-center rounded-lg text-gray-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-500/20 transition">
                  <font-awesome-icon icon="trash" class="text-xs" />
                </button>
              </template>
              <span v-else class="text-[10px] text-emerald-500 font-medium">berjalan</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Catatan: entry manual (tanpa start/stop realtime) belum tersedia —
         backend belum expose endpoint POST untuk membuat time log manual. -->
    <p class="text-xs text-gray-400 dark:text-gray-500 mt-6 text-center">
      Arahkan kursor ke sebuah entry untuk mengubah atau menghapusnya.
    </p>

    <!-- Edit time log -->
    <Teleport to="body">
      <div v-if="editingEntry" class="fixed inset-0 z-50 flex items-center justify-center p-4"
        @click.self="closeEditEntry">
        <div class="absolute inset-0 bg-black/40" @click="closeEditEntry" />
        <div class="relative bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700 w-full max-w-md p-5">
          <h2 class="text-base font-bold text-gray-800 dark:text-gray-100 mb-1">Edit time entry</h2>
          <p class="text-xs text-gray-400 dark:text-gray-500 mb-4 truncate">{{ editingEntry.taskTitle }}</p>

          <label class="block text-[11px] text-gray-400 dark:text-gray-500 mb-1">Waktu mulai</label>
          <input type="datetime-local" v-model="editStart"
            class="w-full text-sm border border-gray-200 dark:border-gray-600 rounded-lg px-2.5 py-1.5 mb-3 outline-none focus:border-blue-400 transition bg-white dark:bg-gray-700 dark:text-gray-100" />

          <label class="block text-[11px] text-gray-400 dark:text-gray-500 mb-1">Waktu selesai</label>
          <input type="datetime-local" v-model="editStop"
            class="w-full text-sm border border-gray-200 dark:border-gray-600 rounded-lg px-2.5 py-1.5 mb-3 outline-none focus:border-blue-400 transition bg-white dark:bg-gray-700 dark:text-gray-100" />

          <label class="block text-[11px] text-gray-400 dark:text-gray-500 mb-1">Deskripsi aktivitas</label>
          <input type="text" v-model="editDescription" placeholder="Opsional…"
            class="w-full text-sm border border-gray-200 dark:border-gray-600 rounded-lg px-2.5 py-1.5 outline-none focus:border-blue-400 transition placeholder-gray-400 bg-white dark:bg-gray-700 dark:text-gray-100" />

          <p class="text-[11px] text-gray-400 dark:text-gray-500 mt-2">Durasi dihitung ulang otomatis oleh server.</p>
          <p v-if="editError" class="text-xs text-red-500 mt-2">{{ editError }}</p>

          <div class="flex justify-end gap-2 mt-5">
            <button @click="closeEditEntry"
              class="text-sm px-3 py-1.5 rounded-lg text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 transition">Batal</button>
            <button @click="saveEditEntry" :disabled="editSaving"
              class="text-sm px-4 py-1.5 rounded-lg font-semibold bg-blue-500 hover:bg-blue-600 text-white transition disabled:opacity-50">
              {{ editSaving ? 'Menyimpan…' : 'Simpan' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Konfirmasi hapus time log -->
    <Teleport to="body">
      <div v-if="deletingEntry" class="fixed inset-0 z-50 flex items-center justify-center p-4"
        @click.self="closeDeleteEntry">
        <div class="absolute inset-0 bg-black/40" @click="closeDeleteEntry" />
        <div class="relative bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700 w-full max-w-sm p-5">
          <h2 class="text-base font-bold text-gray-800 dark:text-gray-100 mb-1">Hapus time entry?</h2>
          <p class="text-sm text-gray-500 dark:text-gray-400 mb-4">
            Entry <span class="font-medium text-gray-700 dark:text-gray-200">{{ deletingEntry.taskTitle }}</span>
            akan dihapus permanen. Aksi ini tidak bisa dibatalkan.
          </p>
          <div class="flex justify-end gap-2">
            <button @click="closeDeleteEntry"
              class="text-sm px-3 py-1.5 rounded-lg text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 transition">Batal</button>
            <button @click="confirmDeleteEntry" :disabled="deleteLoading"
              class="text-sm px-4 py-1.5 rounded-lg font-semibold bg-red-500 hover:bg-red-600 text-white transition disabled:opacity-50">
              {{ deleteLoading ? 'Menghapus…' : 'Hapus' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <Teleport to="body">
      <Transition name="toast">
        <div v-if="toast" class="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 bg-gray-900 text-white text-sm px-5 py-2.5 rounded-xl shadow-lg pointer-events-none">
          {{ toast }}
        </div>
      </Transition>
    </Teleport>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import AppLayout from '../../../components/common/AppLayout.vue'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { library } from '@fortawesome/fontawesome-svg-core'
import { faTag, faCalendar, faClock, faPen, faTrash } from '@fortawesome/free-solid-svg-icons'
import { stopTimer, getTimerLogs, updateTimeLog, deleteTimeLog } from '../api/timer.api'
import { formatTimer, formatClock, formatStopReason } from '../utils/timer.format'
import { resolveDateRange, isWithinRange, dayKey, formatDayHeading, type DateRangePreset } from '../utils/date-range.util'
import { useAppStore } from '../../board/store/board.store'
import { storeToRefs } from 'pinia'
import { useAuth } from '../../../composables/useAuth'

library.add(faTag, faCalendar, faClock, faPen, faTrash)

interface TimeEntry {
  id: string
  taskId: string
  taskTitle: string
  boardId: string
  boardTitle: string
  columnTitle: string
  labels: string[]
  startTime: string | null
  stopTime: string | null
  durationSeconds: number | null
  activityDescription: string | null
  stopReason: string | null
}

const { user: currentUser, fetchCurrentUser } = useAuth()
const store = useAppStore()
const { boards, columnsByBoard } = storeToRefs(store)

const loading = ref(false)
const stopLoading = ref(false)
const toast = ref('')
let toastTimer: ReturnType<typeof setTimeout> | null = null

function showToast(msg: string) {
  toast.value = msg
  if (toastTimer) clearTimeout(toastTimer)
  toastTimer = setTimeout(() => { toast.value = '' }, 2500)
}

// ─── Filters ────────────────────────────────────────────────────
const filterBoardId = ref('')
// Default 'all' — sebelumnya default 'week' diam-diam menyembunyikan
// riwayat lebih lama dari 7 hari (ini penyebab laporan "riwayat Juli tidak
// muncul": datanya ada, cuma ke-filter default).
const datePreset = ref<DateRangePreset>('all')
const customStart = ref('')
const customEnd = ref('')
const filterTag = ref('')
const searchQuery = ref('')

// ─── Active timer (bisa sudah dimulai dari BoardsView) ──────────
const activeTaskId = ref<string | null>(localStorage.getItem('active_timer_task_id'))
const activeTaskTitle = ref<string | null>(localStorage.getItem('active_timer_task_title'))
const activeBoardId = ref<string | null>(localStorage.getItem('active_timer_board_id'))
const elapsed = ref(0)
let tickInterval: ReturnType<typeof setInterval> | null = null

const activeBoardTitle = computed(() => {
  return boards.value.find((b: any) => b.id === activeBoardId.value)?.title ?? '-'
})

function startTick(fromSeconds: number) {
  elapsed.value = fromSeconds
  if (tickInterval) clearInterval(tickInterval)
  tickInterval = setInterval(() => { elapsed.value++ }, 1000)
}

function stopTick() {
  if (tickInterval) { clearInterval(tickInterval); tickInterval = null }
}

async function handleStopActiveTimer() {
  if (!activeTaskId.value || !activeBoardId.value) return
  stopLoading.value = true
  try {
    await stopTimer(activeTaskId.value, activeBoardId.value)
    stopTick()
    showToast(`Timer stopped — ${formatTimer(elapsed.value)}`)
    localStorage.removeItem('active_timer_task_id')
    localStorage.removeItem('active_timer_task_title')
    localStorage.removeItem('active_timer_board_id')
    localStorage.removeItem('active_timer_started_at')
    activeTaskId.value = null
    activeTaskTitle.value = null
    activeBoardId.value = null
    elapsed.value = 0
    await loadEntries()
  } catch (e: any) {
    showToast(e?.response?.data?.error?.message || 'Gagal menghentikan timer.')
  } finally {
    stopLoading.value = false
  }
}

// ─── Edit / Hapus time log (ala Clockify) ──────────────────────
// Semua perubahan lewat backend (PATCH/DELETE /tasks/{id}/timer/logs/{logId})
// lalu loadEntries() menarik ulang dari server → tidak ada state palsu, total
// & daftar konsisten setelah refresh. Backend menghitung ulang durasi (dan
// hanya saat stop_time dikirim), jadi kita selalu kirim start+stop bersamaan.
// Hanya entry yang SUDAH selesai (punya stopTime) yang bisa diedit/dihapus —
// entry yang masih berjalan dihentikan dulu lewat tombol Stop.
const editingEntry = ref<TimeEntry | null>(null)
const editStart = ref('')
const editStop = ref('')
const editDescription = ref('')
const editError = ref('')
const editSaving = ref(false)

const deletingEntry = ref<TimeEntry | null>(null)
const deleteLoading = ref(false)

// ISO → nilai <input type="datetime-local"> (waktu lokal, tanpa detik).
function isoToLocalInput(iso: string | null): string {
  if (!iso) return ''
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return ''
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`
}

function openEditEntry(entry: TimeEntry) {
  editingEntry.value = entry
  editStart.value = isoToLocalInput(entry.startTime)
  editStop.value = isoToLocalInput(entry.stopTime)
  editDescription.value = entry.activityDescription ?? ''
  editError.value = ''
}

function closeEditEntry() {
  editingEntry.value = null
  editError.value = ''
}

async function saveEditEntry() {
  if (!editingEntry.value || editSaving.value) return
  if (!editStart.value || !editStop.value) {
    editError.value = 'Waktu mulai dan selesai wajib diisi.'
    return
  }
  const startMs = new Date(editStart.value).getTime()
  const stopMs = new Date(editStop.value).getTime()
  if (Number.isNaN(startMs) || Number.isNaN(stopMs)) {
    editError.value = 'Format waktu tidak valid.'
    return
  }
  if (stopMs <= startMs) {
    editError.value = 'Waktu selesai harus setelah waktu mulai.'
    return
  }
  editSaving.value = true
  try {
    const entry = editingEntry.value
    await updateTimeLog(entry.taskId, entry.id, entry.boardId, {
      start_time: new Date(editStart.value).toISOString(),
      stop_time: new Date(editStop.value).toISOString(),
      activity_description: editDescription.value.trim(),
    })
    closeEditEntry()
    showToast('Time entry diperbarui.')
    await loadEntries()
  } catch (e: any) {
    editError.value = e?.response?.data?.error?.message || 'Gagal memperbarui entry.'
  } finally {
    editSaving.value = false
  }
}

function openDeleteEntry(entry: TimeEntry) {
  deletingEntry.value = entry
}

function closeDeleteEntry() {
  deletingEntry.value = null
}

async function confirmDeleteEntry() {
  if (!deletingEntry.value || deleteLoading.value) return
  deleteLoading.value = true
  try {
    const entry = deletingEntry.value
    await deleteTimeLog(entry.taskId, entry.id, entry.boardId)
    closeDeleteEntry()
    showToast('Time entry dihapus.')
    await loadEntries()
  } catch (e: any) {
    showToast(e?.response?.data?.error?.message || 'Gagal menghapus entry.')
  } finally {
    deleteLoading.value = false
  }
}

// ─── Data: semua time entry dari task yang melibatkan user login ──
// Backend tidak punya endpoint "time log saya" ataupun user_id di TimeLog
// sendiri — jadi didekati dari task yang assignee_ids-nya termasuk user ini,
// lalu tarik time log per task (GET /tasks/{id}/timer/logs). Entry di
// dalamnya TIDAK benar-benar terikat ke user tertentu (siapapun yang start
// timer di task itu akan tercampur), ini pendekatan terbaik yang bisa
// didapat dari API yang tersedia saat ini.
const allEntries = ref<TimeEntry[]>([])

async function loadEntries() {
  const myId = currentUser.value?.id
  if (!myId) { allEntries.value = []; return }

  loading.value = true
  try {
    await store.fetchBoards()
    await Promise.all(boards.value.map((b: any) => store.fetchColumns(b.id).catch(() => { })))

    const involvedTasks: { taskId: string; taskTitle: string; boardId: string; boardTitle: string; columnTitle: string; labels: string[] }[] = []
    for (const board of boards.value) {
      const cols = columnsByBoard.value[board.id] ?? []
      for (const col of cols) {
        for (const t of col.tasks ?? []) {
          if (!t.assignee_ids?.includes(myId)) continue
          involvedTasks.push({
            taskId: t.id,
            taskTitle: t.title,
            boardId: board.id,
            boardTitle: board.title,
            columnTitle: col.title,
            labels: t.labels ?? [],
          })
        }
      }
    }

    const logSets = await Promise.all(
      involvedTasks.map(t => getTimerLogs(t.taskId, t.boardId).catch(() => []))
    )

    const entries: TimeEntry[] = []
    logSets.forEach((logs, i) => {
      const t = involvedTasks[i]
      for (const log of logs) {
        entries.push({
          id: log.id,
          taskId: t.taskId,
          taskTitle: t.taskTitle,
          boardId: t.boardId,
          boardTitle: t.boardTitle,
          columnTitle: t.columnTitle,
          labels: t.labels,
          startTime: log.start_time,
          stopTime: log.stop_time,
          durationSeconds: log.duration_seconds,
          activityDescription: log.activity_description,
          stopReason: log.stop_reason,
        })
      }
    })

    allEntries.value = entries
  } finally {
    loading.value = false
  }
}

const availableTags = computed(() => {
  const set = new Set<string>()
  for (const e of allEntries.value) {
    for (const label of e.labels) set.add(label)
  }
  return Array.from(set).sort()
})

const filteredEntries = computed(() => {
  const range = resolveDateRange(datePreset.value, customStart.value, customEnd.value)
  const q = searchQuery.value.trim().toLowerCase()

  return allEntries.value
    .filter(e => isWithinRange(e.startTime, range))
    .filter(e => !filterBoardId.value || e.boardId === filterBoardId.value)
    .filter(e => !filterTag.value || e.labels.includes(filterTag.value))
    .filter(e => !q || e.taskTitle.toLowerCase().includes(q))
    .sort((a, b) => new Date(b.startTime ?? 0).getTime() - new Date(a.startTime ?? 0).getTime())
})

const filteredTotalSeconds = computed(() =>
  filteredEntries.value.reduce((sum, e) => sum + Math.max(0, e.durationSeconds ?? 0), 0)
)

const dayGroups = computed(() => {
  const map = new Map<string, TimeEntry[]>()
  for (const e of filteredEntries.value) {
    const key = dayKey(e.startTime)
    if (!map.has(key)) map.set(key, [])
    map.get(key)!.push(e)
  }
  return Array.from(map.entries())
    .sort((a, b) => b[0].localeCompare(a[0]))
    .map(([key, entries]) => ({
      key,
      heading: formatDayHeading(key),
      entries,
      totalSeconds: entries.reduce((sum, e) => sum + Math.max(0, e.durationSeconds ?? 0), 0),
    }))
})

onMounted(async () => {
  if (!currentUser.value) await fetchCurrentUser()

  if (activeTaskId.value && activeBoardId.value) {
    try {
      const logs = await getTimerLogs(activeTaskId.value, activeBoardId.value)
      const running = logs.find(l => !l.stop_time)
      const startedAt = running?.start_time ? new Date(running.start_time).getTime() : Date.now()
      startTick(Math.max(0, Math.floor((Date.now() - startedAt) / 1000)))
    } catch {
      startTick(0)
    }
  }

  await loadEntries()
})

onUnmounted(() => { stopTick() })
</script>

<style scoped>
.toast-enter-active, .toast-leave-active { transition: all 0.25s ease; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateX(-50%) translateY(12px); }
</style>
