import { ref, onMounted, onUnmounted } from 'vue'
import { stopTimer } from '../api/timer.api'

// Reminder client-side tiap 3 jam saat timer berjalan.
//
// Sumber kebenaran: localStorage yang di-set BoardsView saat timer start —
// 'active_timer_task_id', 'active_timer_task_title', 'active_timer_board_id',
// dan 'active_timer_started_at' (epoch ms). Karena composable ini dipasang di
// App.vue (root yang persist lintas route), interval-nya tetap jalan meski
// user pindah halaman selama tab terbuka. Hitungan murni dari selisih waktu,
// tidak bergantung pada stopwatch di halaman manapun.

const REMINDER_INTERVAL_HOURS = 3
const CHECK_EVERY_MS = 20_000 // cek tiap 20 detik

const LS_TASK_ID = 'active_timer_task_id'
const LS_TASK_TITLE = 'active_timer_task_title'
const LS_BOARD_ID = 'active_timer_board_id'
const LS_STARTED_AT = 'active_timer_started_at'

export function useTimerReminder() {
    const reminderOpen = ref(false)
    const reminderTaskTitle = ref('')
    const reminderHours = ref(REMINDER_INTERVAL_HOURS)
    const stopping = ref(false)

    // Milestone (kelipatan 3 jam) terakhir yang sudah ditampilkan dialognya,
    // di-scope ke started_at tertentu supaya reset otomatis saat timer baru.
    let notifiedForStartedAt = 0
    let lastNotifiedMilestone = 0
    let intervalId: ReturnType<typeof setInterval> | null = null

    function readActive() {
        const taskId = localStorage.getItem(LS_TASK_ID)
        if (!taskId) return null
        const boardId = localStorage.getItem(LS_BOARD_ID)
        const title = localStorage.getItem(LS_TASK_TITLE) || 'task ini'
        let startedAt = Number(localStorage.getItem(LS_STARTED_AT))
        // Timer yang sudah jalan sebelum fitur ini ada (atau data hilang):
        // pakai 'now' sebagai baseline supaya reminder tetap berfungsi ke depan.
        if (!startedAt || Number.isNaN(startedAt)) {
            startedAt = Date.now()
            localStorage.setItem(LS_STARTED_AT, String(startedAt))
        }
        return { taskId, boardId, title, startedAt }
    }

    function check() {
        // Dialog sedang terbuka — jangan tumpuk pengecekan.
        if (reminderOpen.value) return

        const active = readActive()
        if (!active) {
            // Tidak ada timer berjalan — reset state milestone.
            notifiedForStartedAt = 0
            lastNotifiedMilestone = 0
            return
        }

        // Timer baru (started_at berubah) → reset hitungan milestone.
        if (active.startedAt !== notifiedForStartedAt) {
            notifiedForStartedAt = active.startedAt
            lastNotifiedMilestone = 0
        }

        const elapsedHours = (Date.now() - active.startedAt) / 3_600_000
        const milestone = Math.floor(elapsedHours / REMINDER_INTERVAL_HOURS)

        if (milestone >= 1 && milestone > lastNotifiedMilestone) {
            lastNotifiedMilestone = milestone
            reminderTaskTitle.value = active.title
            reminderHours.value = milestone * REMINDER_INTERVAL_HOURS
            reminderOpen.value = true
        }
    }

    // Yes → lanjut kerja; dialog ditutup, reminder berikutnya 3 jam lagi
    // (lastNotifiedMilestone sudah maju ke milestone saat ini).
    function keepWorking() {
        reminderOpen.value = false
    }

    // No → hentikan timer via endpoint stop yang sudah ada, bersihkan state.
    async function stopWorking() {
        const active = readActive()
        if (!active || !active.boardId) {
            clearActiveTimer()
            reminderOpen.value = false
            return
        }
        stopping.value = true
        try {
            await stopTimer(active.taskId, active.boardId)
        } catch {
            // Diamkan — kalaupun gagal, tetap tutup dialog agar tidak menghalangi.
        } finally {
            stopping.value = false
            clearActiveTimer()
            reminderOpen.value = false
            notifiedForStartedAt = 0
            lastNotifiedMilestone = 0
        }
    }

    function clearActiveTimer() {
        localStorage.removeItem(LS_TASK_ID)
        localStorage.removeItem(LS_TASK_TITLE)
        localStorage.removeItem(LS_BOARD_ID)
        localStorage.removeItem(LS_STARTED_AT)
    }

    function onVisible() {
        if (document.visibilityState === 'visible') check()
    }

    onMounted(() => {
        check()
        intervalId = setInterval(check, CHECK_EVERY_MS)
        document.addEventListener('visibilitychange', onVisible)
    })

    onUnmounted(() => {
        if (intervalId) clearInterval(intervalId)
        document.removeEventListener('visibilitychange', onVisible)
    })

    return { reminderOpen, reminderTaskTitle, reminderHours, stopping, keepWorking, stopWorking }
}
