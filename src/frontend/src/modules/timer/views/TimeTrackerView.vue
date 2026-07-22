<template>
  <AppLayout>
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-800">Time Tracker</h1>
      <p class="text-sm text-gray-500 mt-1">Riwayat waktu kerja dari card yang melibatkan Anda.</p>
    </div>

    <!-- Active timer bar -->
    <div v-if="activeTaskId" class="bg-white rounded-2xl shadow-sm border border-emerald-200 mb-6 px-5 py-4 flex items-center gap-4">
      <span class="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse flex-shrink-0" />
      <div class="flex-1 min-w-0">
        <p class="text-sm font-medium text-gray-800 truncate">{{ activeTaskTitle || 'Task' }}</p>
        <p class="text-xs text-gray-400">{{ activeBoardTitle }}</p>
      </div>
      <span class="text-lg font-mono font-bold text-emerald-600 tabular-nums">{{ formatTimer(elapsed) }}</span>
      <button @click="handleStopActiveTimer" :disabled="stopLoading"
        class="px-4 py-2 rounded-xl text-sm font-semibold bg-red-500 hover:bg-red-600 text-white transition disabled:opacity-50">
        {{ stopLoading ? '...' : 'Stop' }}
      </button>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-2xl border border-gray-200 shadow-sm mb-6 p-4 flex flex-wrap items-end gap-3">
      <div class="min-w-[160px]">
        <label class="block text-[11px] text-gray-400 mb-1">Board</label>
        <select v-model="filterBoardId"
          class="w-full text-sm border border-gray-200 rounded-lg px-2.5 py-1.5 outline-none focus:border-blue-400 transition bg-white">
          <option value="">Semua board</option>
          <option v-for="b in boards" :key="b.id" :value="b.id">{{ b.title }}</option>
        </select>
      </div>

      <div class="min-w-[140px]">
        <label class="block text-[11px] text-gray-400 mb-1">Rentang tanggal</label>
        <select v-model="datePreset"
          class="w-full text-sm border border-gray-200 rounded-lg px-2.5 py-1.5 outline-none focus:border-blue-400 transition bg-white">
          <option value="today">Hari ini</option>
          <option value="week">Minggu ini</option>
          <option value="month">Bulan ini</option>
          <option value="custom">Custom</option>
        </select>
      </div>

      <template v-if="datePreset === 'custom'">
        <div>
          <label class="block text-[11px] text-gray-400 mb-1">Dari</label>
          <input type="date" v-model="customStart"
            class="text-sm border border-gray-200 rounded-lg px-2.5 py-1.5 outline-none focus:border-blue-400 transition" />
        </div>
        <div>
          <label class="block text-[11px] text-gray-400 mb-1">Sampai</label>
          <input type="date" v-model="customEnd"
            class="text-sm border border-gray-200 rounded-lg px-2.5 py-1.5 outline-none focus:border-blue-400 transition" />
        </div>
      </template>

      <div v-if="availableTags.length" class="min-w-[140px]">
        <label class="block text-[11px] text-gray-400 mb-1">Tag</label>
        <select v-model="filterTag"
          class="w-full text-sm border border-gray-200 rounded-lg px-2.5 py-1.5 outline-none focus:border-blue-400 transition bg-white">
          <option value="">Semua tag</option>
          <option v-for="tag in availableTags" :key="tag" :value="tag">{{ tag }}</option>
        </select>
      </div>

      <div class="flex-1 min-w-[180px]">
        <label class="block text-[11px] text-gray-400 mb-1">Cari task</label>
        <input v-model="searchQuery" type="text" placeholder="Nama task..."
          class="w-full text-sm border border-gray-200 rounded-lg px-2.5 py-1.5 outline-none focus:border-blue-400 transition placeholder-gray-400" />
      </div>

      <div class="ml-auto text-right">
        <p class="text-[11px] text-gray-400 mb-1">Total</p>
        <p class="text-lg font-bold text-gray-800 font-mono tabular-nums">{{ formatTimer(filteredTotalSeconds) }}</p>
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
    <div v-else-if="!dayGroups.length" class="bg-gray-50 border border-dashed border-gray-300 rounded-2xl p-12 text-center">
      <font-awesome-icon icon="clock" class="text-3xl text-gray-300 mb-3 block mx-auto" />
      <p class="text-sm text-gray-500 font-medium">Belum ada time entry</p>
      <p class="text-xs text-gray-400 mt-1">Mulai timer dari card di Boards untuk mulai tracking.</p>
    </div>

    <!-- Log groups -->
    <div v-else class="space-y-4">
      <div v-for="group in dayGroups" :key="group.key" class="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
        <div class="flex items-center justify-between px-5 py-3 bg-gray-50 border-b border-gray-100">
          <span class="text-xs font-semibold text-gray-500 uppercase tracking-wide">{{ group.heading }}</span>
          <div class="flex items-center gap-3">
            <span class="text-xs text-gray-400">Total</span>
            <span class="text-sm font-bold text-gray-700 font-mono">{{ formatTimer(group.totalSeconds) }}</span>
          </div>
        </div>
        <div class="divide-y divide-gray-50">
          <div v-for="entry in group.entries" :key="entry.id"
            class="flex items-center gap-4 px-5 py-3.5 hover:bg-gray-50 transition">
            <div class="flex-1 min-w-0">
              <router-link :to="`/boards/${entry.boardId}`" class="text-sm text-gray-800 font-medium truncate block hover:text-blue-600 transition">
                {{ entry.taskTitle }}
              </router-link>
              <div class="flex items-center gap-1.5 mt-0.5 flex-wrap">
                <span class="text-xs text-orange-500">{{ entry.boardTitle }} • {{ entry.columnTitle }}</span>
                <span v-if="entry.activityDescription" class="text-xs text-gray-400 truncate">— {{ entry.activityDescription }}</span>
                <span v-if="formatStopReason(entry.stopReason)"
                  class="text-[10px] font-medium text-amber-600 bg-amber-50 border border-amber-200 rounded-full px-1.5 py-0.5">
                  {{ formatStopReason(entry.stopReason) }}
                </span>
              </div>
            </div>
            <div class="flex items-center gap-1.5 text-xs text-gray-400 min-w-[120px] justify-center flex-shrink-0">
              <font-awesome-icon icon="calendar" class="text-gray-300" />
              <span>{{ entry.stopTime ? `${formatClock(entry.startTime)} – ${formatClock(entry.stopTime)}` : `${formatClock(entry.startTime)} – berjalan` }}</span>
            </div>
            <span class="text-sm font-mono font-semibold text-gray-700 min-w-[70px] text-right flex-shrink-0">
              {{ entry.durationSeconds != null ? formatTimer(entry.durationSeconds) : '—' }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Gap notice: backend belum expose endpoint update/delete time log -->
    <p class="text-xs text-gray-400 mt-6 text-center">
      Riwayat waktu di halaman ini read-only — backend belum menyediakan endpoint untuk mengubah atau menghapus entry yang sudah tercatat.
    </p>

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
import { faTag, faCalendar, faClock } from '@fortawesome/free-solid-svg-icons'
import { stopTimer, getTimerLogs } from '../api/timer.api'
import { formatTimer, formatClock, formatStopReason } from '../utils/timer.format'
import { resolveDateRange, isWithinRange, dayKey, formatDayHeading, type DateRangePreset } from '../utils/date-range.util'
import { useAppStore } from '../../board/store/board.store'
import { storeToRefs } from 'pinia'
import { useAuth } from '../../../composables/useAuth'

library.add(faTag, faCalendar, faClock)

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
const datePreset = ref<DateRangePreset>('week')
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
