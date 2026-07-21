<template>
  <AppLayout>
    <!-- ── Timer Bar (Clockify-style) ── -->
    <div class="bg-white rounded-2xl shadow-sm border border-gray-200 mb-6 px-5 py-4 flex items-center gap-4">
      <input
        v-model="manualTitle"
        type="text"
        placeholder="What are you working on?"
        class="flex-1 outline-none text-sm text-gray-700 placeholder-gray-400"
      />
      <div class="h-5 w-px bg-gray-200" />
      <button class="text-gray-400 hover:text-gray-600 transition" title="Add label">
        <font-awesome-icon icon="tag" />
      </button>
      <button class="text-gray-400 hover:text-gray-600 transition" title="Set date">
        <font-awesome-icon icon="calendar" />
      </button>
      <div class="h-5 w-px bg-gray-200" />
      <span
        class="text-sm font-mono font-bold min-w-[80px] text-right tabular-nums"
        :class="isRunning ? 'text-blue-600' : 'text-gray-500'"
      >{{ isRunning ? formatSec(elapsed) : '00:00:00' }}</span>
      <button
        @click="toggleTimer"
        :disabled="timerLoading"
        class="px-5 py-2 rounded-xl text-sm font-semibold transition disabled:opacity-50 min-w-[80px]"
        :class="isRunning ? 'bg-red-500 hover:bg-red-600 text-white' : 'bg-blue-600 hover:bg-blue-700 text-white'"
      >{{ timerLoading ? '...' : isRunning ? 'Stop' : 'Start' }}</button>
    </div>

    <!-- Active timer badge -->
    <div v-if="isRunning && activeTaskTitle" class="mb-5 flex items-center gap-2 text-xs text-green-600 font-medium">
      <span class="w-2 h-2 rounded-full bg-green-500 animate-pulse inline-block" />
      Tracking: <span class="font-semibold">{{ activeTaskTitle }}</span>
      <span class="text-gray-400 font-normal ml-1">— stop from Boards task card</span>
    </div>

    <!-- Week header -->
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-sm font-semibold text-gray-700">This week</h2>
      <div class="flex items-center gap-3 text-xs text-gray-500">
        <span>Total: <span class="font-bold text-gray-700">{{ weekTotal }}</span></span>
        <button v-if="activeTaskId" @click="fetchLogs(activeTaskId)" class="text-blue-500 hover:underline">Refresh</button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="logsLoading" class="flex items-center justify-center h-40 text-gray-400 gap-2 text-sm">
      <svg class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
      </svg>
      Loading...
    </div>

    <!-- Empty -->
    <div v-else-if="groups.length === 0" class="bg-gray-50 border border-dashed border-gray-300 rounded-2xl p-12 text-center">
      <font-awesome-icon icon="clock" class="text-3xl text-gray-300 mb-3 block mx-auto" />
      <p class="text-sm text-gray-500 font-medium">No time entries yet</p>
      <p class="text-xs text-gray-400 mt-1">Start a timer from Boards to track your work</p>
    </div>

    <!-- Log groups -->
    <div v-else class="space-y-4">
      <div v-for="(group, i) in groups" :key="i" class="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
        <!-- Group header -->
        <div class="flex items-center justify-between px-5 py-3 bg-gray-50 border-b border-gray-100">
          <span class="text-xs font-semibold text-gray-500 uppercase tracking-wide">{{ group.date }}</span>
          <div class="flex items-center gap-3">
            <span class="text-xs text-gray-400">Total</span>
            <span class="text-sm font-bold text-gray-700 font-mono">{{ group.total }}</span>
          </div>
        </div>
        <!-- Entries -->
        <div class="divide-y divide-gray-50">
          <div
            v-for="(item, j) in group.items"
            :key="j"
            class="flex items-center gap-4 px-5 py-3.5 hover:bg-gray-50 transition group"
          >
            <div class="flex-1 min-w-0">
              <p class="text-sm text-gray-800 font-medium truncate">{{ item.title }}</p>
              <div class="flex items-center gap-1.5 mt-0.5">
                <span class="w-2 h-2 rounded-full bg-orange-400 inline-block" />
                <span class="text-xs text-orange-500">{{ item.project }}</span>
              </div>
            </div>
            <div v-if="item.label" class="hidden sm:flex items-center gap-1 bg-gray-100 text-gray-500 text-xs px-2 py-1 rounded-lg">
              <font-awesome-icon icon="tag" class="text-xs" /> {{ item.label }}
            </div>
            <div class="flex items-center gap-1.5 text-xs text-gray-400 min-w-[130px] justify-center">
              <font-awesome-icon icon="calendar" class="text-gray-300" />
              <span>{{ item.timeRange }}</span>
            </div>
            <span class="text-sm font-mono font-semibold text-gray-700 min-w-[80px] text-right">{{ item.duration }}</span>
            <div class="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition">
              <button @click="resumeEntry(item)" class="text-gray-400 hover:text-blue-500 transition" title="Resume">
                <font-awesome-icon icon="play" />
              </button>
              <span class="text-gray-300 cursor-pointer hover:text-gray-500">⋮</span>
            </div>
          </div>
        </div>
      </div>
    </div>

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
import { faPlay, faStop, faTag, faCalendar, faClock } from '@fortawesome/free-solid-svg-icons'
import { startTimer, stopTimer, pingTimer as pingTimerApi, getTimerLogs } from '../../timer/api/timer.api'

library.add(faPlay, faStop, faTag, faCalendar, faClock)

const manualTitle  = ref('')
const timerLoading = ref(false)
const logsLoading  = ref(false)
const toast        = ref('')
const rawLogs      = ref<any[]>([])

const activeTaskId    = ref<string | null>(localStorage.getItem('active_timer_task_id'))
const activeTaskTitle = ref<string | null>(localStorage.getItem('active_timer_task_title'))
const activeBoardId   = ref<string | null>(localStorage.getItem('active_timer_board_id'))
const isRunning       = ref(!!activeTaskId.value)
const elapsed         = ref(0)

let tickTimer: ReturnType<typeof setInterval> | null = null
let pingInterval: ReturnType<typeof setInterval> | null = null

function startTick() {
  stopTick()
  tickTimer = setInterval(() => { elapsed.value++ }, 1000)
}
function stopTick() {
  if (tickTimer) { clearInterval(tickTimer); tickTimer = null }
}
function startPing(taskId: string) {
  stopPing()
  pingInterval = setInterval(async () => {
    if (!activeBoardId.value) return
    try { await pingTimerApi(taskId, activeBoardId.value) } catch {}
  }, 120000)
}
function stopPing() {
  if (pingInterval) { clearInterval(pingInterval); pingInterval = null }
}

function formatSec(s: number): string {
  const h = String(Math.floor(s / 3600)).padStart(2, '0')
  const m = String(Math.floor((s % 3600) / 60)).padStart(2, '0')
  const sec = String(s % 60).padStart(2, '0')
  return `${h}:${m}:${sec}`
}

async function toggleTimer() {
  if (isRunning.value) {
    if (!activeTaskId.value) return
    if (!activeBoardId.value) {
      showToast('Board timer tidak diketahui. Stop dari halaman Boards.')
      return
    }
    timerLoading.value = true
    try {
      await stopTimer(activeTaskId.value, activeBoardId.value)
      stopTick(); stopPing()
      showToast(`Stopped — ${formatSec(elapsed.value)}`)
      await fetchLogs(activeTaskId.value)
      isRunning.value = false
      elapsed.value   = 0
      localStorage.removeItem('active_timer_task_id')
      localStorage.removeItem('active_timer_task_title')
      localStorage.removeItem('active_timer_board_id')
      activeTaskId.value    = null
      activeTaskTitle.value = null
      activeBoardId.value   = null
    } catch (e: any) {
      showToast(e?.response?.data?.error?.message || 'Gagal menghentikan timer.')
    } finally {
      timerLoading.value = false
    }
  } else {
    showToast('Pilih task dari Boards untuk memulai timer.')
  }
}

function resumeEntry(item: any) {
  showToast(`Buka Boards → resume "${item.title}"`)
}

async function fetchLogs(taskId: string) {
  if (!activeBoardId.value) { rawLogs.value = []; return }
  logsLoading.value = true
  try {
    rawLogs.value = await getTimerLogs(taskId, activeBoardId.value)
  } catch {
    rawLogs.value = []
  } finally {
    logsLoading.value = false
  }
}

const groups = computed(() => {
  if (rawLogs.value.length === 0) return []
  const map: Record<string, any[]> = {}
  rawLogs.value.forEach((log: any) => {
    const startRaw  = log.started_at ?? log.start_time ?? log.created_at ?? ''
    const endRaw    = log.ended_at   ?? log.end_time   ?? ''
    const durSec    = Number(log.duration_seconds ?? log.duration_sec ?? log.duration ?? 0)
    const dateObj   = startRaw ? new Date(startRaw) : new Date()
    const dateKey   = dateObj.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })
    const timeRange = (startRaw && endRaw)
      ? `${fmtTime(startRaw)} – ${fmtTime(endRaw)}`
      : startRaw ? fmtTime(startRaw) : '-'
    if (!map[dateKey]) map[dateKey] = []
    map[dateKey].push({
      taskId:    activeTaskId.value,
      title:     activeTaskTitle.value ?? log.task_title ?? 'Task',
      project:   log.project ?? log.board_title ?? 'Braves Board',
      label:     log.label   ?? null,
      timeRange,
      duration:  formatSec(durSec),
      _sec:      durSec,
    })
  })
  return Object.entries(map).map(([date, items]) => ({
    date,
    total: formatSec(items.reduce((s: number, i: any) => s + i._sec, 0)),
    items,
  }))
})

const weekTotal = computed(() =>
  formatSec(groups.value.reduce((s, g) => s + g.items.reduce((ss: number, i: any) => ss + i._sec, 0), 0))
)

function fmtTime(iso: string): string {
  return new Date(iso).toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' })
}

let toastTimer: ReturnType<typeof setTimeout> | null = null
function showToast(msg: string) {
  toast.value = msg
  if (toastTimer) clearTimeout(toastTimer)
  toastTimer = setTimeout(() => { toast.value = '' }, 2500)
}

onMounted(() => {
  if (isRunning.value && activeTaskId.value) {
    startTick()
    startPing(activeTaskId.value)
    fetchLogs(activeTaskId.value)
  }
})

onUnmounted(() => { stopTick(); stopPing() })
</script>

<style scoped>
.toast-enter-active, .toast-leave-active { transition: all 0.25s ease; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateX(-50%) translateY(12px); }
</style>