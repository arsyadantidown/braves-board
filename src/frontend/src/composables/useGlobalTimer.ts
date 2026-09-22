import { ref } from "vue";
import {
  pingTimer,
  confirmTimer,
  stopTimer,
} from "../modules/timer/api/timer.api";

const showConfirmModal = ref(false);
const activeTaskTitle = ref("");
const countdownSeconds = ref(300); // 5 menit hitung mundur (menit 175 -> 180)
const confirmLoading = ref(false);

let globalPingInterval: ReturnType<typeof setInterval> | null = null;
let globalCycleCheckInterval: ReturnType<typeof setInterval> | null = null;
let countdownInterval: ReturnType<typeof setInterval> | null = null;

export function useGlobalTimer() {
  // 1. Kirim Ping Heartbeat setiap 2 menit (120 detik)
  async function triggerPing() {
    const taskId = localStorage.getItem("active_timer_task_id");
    const boardId = localStorage.getItem("active_timer_board_id");
    if (!taskId || !boardId) return;

    try {
      await pingTimer(taskId, boardId);
    } catch {
      // Abaikan jika network drop sesaat
    }
  }

  // 2. Cek apakah sudah mencapai Menit ke-175 (10.500 detik) sejak mulai / konfirmasi terakhir
  function checkThreeHourCycle() {
    const taskId = localStorage.getItem("active_timer_task_id");
    const lastConfirmedStr =
      localStorage.getItem("active_timer_last_confirmed_at") ||
      localStorage.getItem("active_timer_started_at");

    if (!taskId || !lastConfirmedStr) {
      if (showConfirmModal.value) closeConfirmDialog();
      return;
    }

    const lastConfirmedMs = Number(lastConfirmedStr) || Date.now();
    const elapsedSeconds = Math.floor((Date.now() - lastConfirmedMs) / 1000);

    // Menit ke-175 = 10.500 detik
    if (elapsedSeconds >= 10500 && elapsedSeconds < 10800) {
      if (!showConfirmModal.value) {
        activeTaskTitle.value =
          localStorage.getItem("active_timer_task_title") || "Task";
        countdownSeconds.value = Math.max(0, 10800 - elapsedSeconds);
        showConfirmModal.value = true;
        startCountdown();
      }
    } else if (elapsedSeconds >= 10800) {
      // Menit ke-180 (3 jam) tanpa respon -> Auto-off otomatis
      handleAutoOff();
    }
  }

  function startCountdown() {
    if (countdownInterval) clearInterval(countdownInterval);
    countdownInterval = setInterval(() => {
      if (countdownSeconds.value > 0) {
        countdownSeconds.value--;
      } else {
        handleAutoOff();
      }
    }, 1000);
  }

  function closeConfirmDialog() {
    showConfirmModal.value = false;
    if (countdownInterval) {
      clearInterval(countdownInterval);
      countdownInterval = null;
    }
  }

  // 3. Aksi User: Klik "Ya, Lanjutkan Bekerja"
  async function handleConfirmActive() {
    const taskId = localStorage.getItem("active_timer_task_id");
    const boardId = localStorage.getItem("active_timer_board_id");
    if (!taskId || !boardId) return;

    confirmLoading.value = true;
    try {
      await confirmTimer(taskId, boardId);
      // Reset siklus 3 jam ke waktu sekarang
      localStorage.setItem(
        "active_timer_last_confirmed_at",
        String(Date.now()),
      );
      closeConfirmDialog();
    } catch (e) {
      console.error("Gagal mengonfirmasi timer:", e);
    } finally {
      confirmLoading.value = false;
    }
  }

  // 4. Aksi User: Klik "Hentikan Timer"
  async function handleStopFromModal() {
    const taskId = localStorage.getItem("active_timer_task_id");
    const boardId = localStorage.getItem("active_timer_board_id");
    if (taskId && boardId) {
      try {
        await stopTimer(taskId, boardId);
      } catch {}
    }
    clearTimerLocalStorage();
    closeConfirmDialog();
    window.location.reload(); // Reload ringan untuk sync UI
  }

  // 5. Auto-off pada menit ke-180 jika tidak ada respon
  function handleAutoOff() {
    clearTimerLocalStorage();
    closeConfirmDialog();
    alert(
      "⚠️ Timer otomatis dihentikan karena tidak ada konfirmasi aktif selama 3 jam.",
    );
    window.location.reload();
  }

  function clearTimerLocalStorage() {
    localStorage.removeItem("active_timer_task_id");
    localStorage.removeItem("active_timer_task_title");
    localStorage.removeItem("active_timer_board_id");
    localStorage.removeItem("active_timer_started_at");
    localStorage.removeItem("active_timer_last_confirmed_at");
  }

  function initGlobalHeartbeat() {
    if (!globalPingInterval) {
      // Ping setiap 2 menit (120.000 ms)
      globalPingInterval = setInterval(triggerPing, 120000);
    }
    if (!globalCycleCheckInterval) {
      // Periksa menit 175 setiap 5 detik
      globalCycleCheckInterval = setInterval(checkThreeHourCycle, 5000);
    }
  }

  return {
    showConfirmModal,
    activeTaskTitle,
    countdownSeconds,
    confirmLoading,
    handleConfirmActive,
    handleStopFromModal,
    initGlobalHeartbeat,
  };
}
