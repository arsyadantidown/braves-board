<template>
  <AppLayout>
    <div class="mb-8">
      <h1 class="text-2xl font-bold text-gray-800 dark:text-gray-100">Dashboard</h1>
      <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">Welcome back, {{ currentUser?.full_name ?? currentUser?.email ?? '...' }}</p>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
      <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5">
        <p class="text-xs text-gray-400 dark:text-gray-500 mb-1">Total Boards</p>
        <p class="text-2xl font-bold text-gray-800 dark:text-gray-100">{{ boards.length }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5">
        <p class="text-xs text-gray-400 dark:text-gray-500 mb-1">My Tasks</p>
        <p class="text-2xl font-bold text-gray-800 dark:text-gray-100">{{ myTasks.length }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5">
        <p class="text-xs text-gray-400 dark:text-gray-500 mb-1">Completed</p>
        <p class="text-2xl font-bold text-emerald-500">{{ completedCount }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5">
        <p class="text-xs text-gray-400 dark:text-gray-500 mb-1">This Week</p>
        <p class="text-2xl font-bold text-blue-500">
          {{ weeklyTimeLoading ? '…' : formatTimer(weeklySeconds) }}
        </p>
      </div>
    </div>

    <!-- Quick actions -->
    <section class="mb-8">
      <h2 class="text-sm font-semibold text-gray-700 dark:text-gray-200 mb-4">Quick Actions</h2>
      <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
        <router-link to="/boards"
          class="group flex items-center gap-3 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5 transition-all duration-200 ease-out hover:-translate-y-0.5 hover:shadow-md hover:border-blue-400 dark:hover:border-blue-500 active:translate-y-0 active:scale-[0.98] active:shadow-sm focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-400/60">
          <div class="w-10 h-10 rounded-lg bg-blue-50 dark:bg-blue-500/15 flex items-center justify-center flex-shrink-0 transition-transform duration-200 group-hover:scale-110">
            <svg class="w-5 h-5 text-blue-500 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2" />
            </svg>
          </div>
          <div class="min-w-0">
            <p class="text-sm font-semibold text-gray-800 dark:text-gray-100 truncate">Boards</p>
            <p class="text-xs text-gray-400 dark:text-gray-500 truncate">Manage your boards</p>
          </div>
        </router-link>

        <router-link to="/tracker"
          class="group flex items-center gap-3 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5 transition-all duration-200 ease-out hover:-translate-y-0.5 hover:shadow-md hover:border-emerald-400 dark:hover:border-emerald-500 active:translate-y-0 active:scale-[0.98] active:shadow-sm focus:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400/60">
          <div class="w-10 h-10 rounded-lg bg-emerald-50 dark:bg-emerald-500/15 flex items-center justify-center flex-shrink-0 transition-transform duration-200 group-hover:scale-110">
            <svg class="w-5 h-5 text-emerald-500 dark:text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div class="min-w-0">
            <p class="text-sm font-semibold text-gray-800 dark:text-gray-100 truncate">Time Tracker</p>
            <p class="text-xs text-gray-400 dark:text-gray-500 truncate">Track your time</p>
          </div>
        </router-link>

        <router-link to="/reports"
          class="group flex items-center gap-3 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5 transition-all duration-200 ease-out hover:-translate-y-0.5 hover:shadow-md hover:border-purple-400 dark:hover:border-purple-500 active:translate-y-0 active:scale-[0.98] active:shadow-sm focus:outline-none focus-visible:ring-2 focus-visible:ring-purple-400/60">
          <div class="w-10 h-10 rounded-lg bg-purple-50 dark:bg-purple-500/15 flex items-center justify-center flex-shrink-0 transition-transform duration-200 group-hover:scale-110">
            <svg class="w-5 h-5 text-purple-500 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <div class="min-w-0">
            <p class="text-sm font-semibold text-gray-800 dark:text-gray-100 truncate">Reports</p>
            <p class="text-xs text-gray-400 dark:text-gray-500 truncate">View your reports</p>
          </div>
        </router-link>
      </div>
    </section>

    <!-- My Tasks -->
    <section class="mb-8">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-sm font-semibold text-gray-700 dark:text-gray-200">My Tasks</h2>
        <span class="text-xs text-gray-400 dark:text-gray-500">Card yang meng-assign Anda</span>
      </div>

      <div v-if="tasksLoading" class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-8 text-center text-sm text-gray-400 dark:text-gray-500">
        Memuat task…
      </div>
      <div v-else-if="!myTasks.length"
        class="bg-white dark:bg-gray-800 rounded-xl border border-dashed border-gray-300 dark:border-gray-600 p-8 text-center text-sm text-gray-400 dark:text-gray-500">
        Belum ada task yang di-assign ke Anda.
      </div>
      <div v-else class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 divide-y divide-gray-100 dark:divide-gray-700 overflow-hidden">
        <router-link v-for="t in myTasks" :key="t.id" :to="`/boards/${t.boardId}`"
          class="flex items-center gap-4 px-5 py-3.5 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition">
          <div class="flex-1 min-w-0">
            <p class="text-sm text-gray-800 dark:text-gray-100 font-medium truncate">{{ t.title }}</p>
            <div class="flex items-center gap-2 mt-1 flex-wrap">
              <span class="text-[11px] text-gray-400 dark:text-gray-500">{{ t.boardTitle }} • {{ t.columnTitle }}</span>
              <span v-if="t.dueDate && t.dueDate !== '-' && dueDateStatus(t.dueDate) !== 'normal'"
                class="text-[10px] font-semibold px-1.5 py-0.5 rounded-full"
                :class="dueDateBadgeClass(dueDateStatus(t.dueDate))">
                {{ dueDateStatus(t.dueDate) === 'overdue' ? 'Overdue' : 'Due Soon' }}
              </span>
            </div>
          </div>

          <!-- Progress dari subtask selesai -->
          <div class="w-32 flex-shrink-0" v-if="t.subtaskTotal > 0">
            <div class="flex items-center justify-between mb-1">
              <span class="text-[10px] text-gray-400 dark:text-gray-500">{{ t.subtaskDone }}/{{ t.subtaskTotal }}</span>
              <span class="text-[10px] font-semibold text-gray-500 dark:text-gray-400">{{ t.progress }}%</span>
            </div>
            <div class="bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
              <div class="h-1.5 rounded-full transition-all"
                :class="t.progress === 100 ? 'bg-emerald-500' : 'bg-blue-500'"
                :style="{ width: t.progress + '%' }"></div>
            </div>
          </div>
          <span v-else class="w-32 flex-shrink-0 text-[10px] text-gray-300 dark:text-gray-600 text-right">No subtasks</span>
        </router-link>
      </div>
    </section>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import AppLayout from '../../../components/common/AppLayout.vue'
import { useAppStore } from '../../board/store/board.store'
import { storeToRefs } from 'pinia'
import { useAuth } from '../../../composables/useAuth'
import { dueDateStatus, dueDateBadgeClass } from '../../board/utils/due-date.util'
import { getTimerLogs } from '../../timer/api/timer.api'
import { formatTimer } from '../../timer/utils/timer.format'

interface MyTask {
  id: string
  boardId: string
  boardTitle: string
  columnTitle: string
  title: string
  dueDate: string
  subtaskDone: number
  subtaskTotal: number
  progress: number
}

const { user: currentUser, fetchCurrentUser } = useAuth()
const store = useAppStore()
const { boards, columnsByBoard } = storeToRefs(store)

const tasksLoading = ref(false)
const weeklyTimeLoading = ref(false)
const weeklySeconds = ref(0)

// ─── My Tasks: backend tidak punya endpoint "tasks saya" atau filter by
// assignee — jadi di-derive di frontend dari semua board/column/task yang
// sudah termuat di store, difilter assignee_ids.includes(currentUser.id).
const myTasks = computed<MyTask[]>(() => {
  const myId = currentUser.value?.id
  if (!myId) return []

  const result: MyTask[] = []
  for (const board of boards.value) {
    const cols = columnsByBoard.value[board.id] ?? []
    for (const col of cols) {
      for (const t of col.tasks ?? []) {
        if (!t.assignee_ids?.includes(myId)) continue
        const subtaskTotal = t.subtasks?.length ?? 0
        const subtaskDone = t.subtasks?.filter((s: any) => s.completed).length ?? 0
        result.push({
          id: t.id,
          boardId: board.id,
          boardTitle: board.title,
          columnTitle: col.title,
          title: t.title,
          dueDate: t.dueDate,
          subtaskDone,
          subtaskTotal,
          progress: subtaskTotal > 0 ? Math.round((subtaskDone / subtaskTotal) * 100) : 0,
        })
      }
    }
  }

  // Urutkan: overdue dulu, lalu due soon, baru sisanya.
  const rank = { overdue: 0, soon: 1, normal: 2, none: 3 }
  return result.sort((a, b) => rank[dueDateStatus(a.dueDate)] - rank[dueDateStatus(b.dueDate)])
})

const completedCount = computed(() =>
  myTasks.value.filter(t => t.subtaskTotal > 0 && t.progress === 100).length
)

async function loadMyTasks() {
  tasksLoading.value = true
  try {
    await store.fetchBoards()
    await Promise.all(boards.value.map((b: any) => store.fetchColumns(b.id).catch(() => { })))
  } finally {
    tasksLoading.value = false
  }
}

// ─── Total waktu minggu ini: backend tidak punya endpoint agregat time log,
// hanya per-task (GET /tasks/{id}/timer/logs). Approximasi: jumlahkan durasi
// log dalam 7 hari terakhir dari task yang di-assign ke user ini — bukan
// waktu yang murni ditrack oleh user (TimeLog tidak punya field user_id),
// tapi ini pendekatan terbaik yang bisa didapat dari API yang tersedia.
async function loadWeeklyTime() {
  if (!myTasks.value.length) { weeklySeconds.value = 0; return }
  weeklyTimeLoading.value = true
  const sevenDaysAgo = Date.now() - 7 * 24 * 60 * 60 * 1000
  try {
    const logSets = await Promise.all(
      myTasks.value.map(t => getTimerLogs(t.id, t.boardId).catch(() => []))
    )
    let total = 0
    for (const logs of logSets) {
      for (const log of logs) {
        if (!log.start_time) continue
        const started = new Date(log.start_time).getTime()
        if (Number.isNaN(started) || started < sevenDaysAgo) continue
        total += log.duration_seconds ?? 0
      }
    }
    weeklySeconds.value = total
  } finally {
    weeklyTimeLoading.value = false
  }
}

onMounted(async () => {
  if (!currentUser.value) await fetchCurrentUser()
  await loadMyTasks()
  await loadWeeklyTime()
})
</script>
