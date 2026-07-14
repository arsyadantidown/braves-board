// src/modules/timer/utils/timer.format.ts
// Formatting untuk tampilan timer & time log.

export interface TimerLog {
  id: string
  start_time: string | null
  stop_time: string | null
  duration_seconds: number | null
  activity_description: string | null
  stop_reason: string | null
  created_at: string | null
}

/** Detik → "HH:MM:SS" (untuk stopwatch berjalan). */
export function formatTimer(seconds: number): string {
  const safe = Math.max(0, Math.floor(seconds || 0))
  const h = String(Math.floor(safe / 3600)).padStart(2, '0')
  const m = String(Math.floor((safe % 3600) / 60)).padStart(2, '0')
  const s = String(safe % 60).padStart(2, '0')
  return `${h}:${m}:${s}`
}

/**
 * ISO string → "13:00" (jam lokal).
 * Disusun manual, bukan toLocaleTimeString('id-ID') — locale id-ID memakai
 * titik sebagai pemisah ("13.00"), sedangkan format yang diminta pakai titik dua.
 */
export function formatClock(iso: string | null): string {
  if (!iso) return '-'
  const date = new Date(iso)
  if (Number.isNaN(date.getTime())) return '-'
  const h = String(date.getHours()).padStart(2, '0')
  const m = String(date.getMinutes()).padStart(2, '0')
  return `${h}:${m}`
}

/** ISO string → "14 Jul 2026". */
export function formatLogDate(iso: string | null): string {
  if (!iso) return '-'
  const date = new Date(iso)
  if (Number.isNaN(date.getTime())) return '-'
  return date.toLocaleDateString('id-ID', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  })
}

/**
 * Detik → durasi natural: "3 jam", "1 jam 30 menit", "45 menit", "30 detik".
 * Menit disembunyikan kalau pas di jam bulat, sesuai contoh "13:00 → 16:00, 3 jam".
 */
export function formatDuration(seconds: number | null): string {
  const total = Math.max(0, Math.floor(seconds ?? 0))
  if (total < 60) return `${total} detik`

  const hours = Math.floor(total / 3600)
  const minutes = Math.floor((total % 3600) / 60)

  if (hours === 0) return `${minutes} menit`
  if (minutes === 0) return `${hours} jam`
  return `${hours} jam ${minutes} menit`
}

/**
 * Satu log → "13:00 → 16:00, 3 jam".
 * Log yang timernya masih jalan (belum ada stop_time) → "13:00 → berjalan".
 */
export function formatTimerLog(log: TimerLog): string {
  const start = formatClock(log.start_time)

  if (!log.stop_time) {
    return `${start} → berjalan`
  }

  return `${start} → ${formatClock(log.stop_time)}, ${formatDuration(log.duration_seconds)}`
}

/** Total durasi semua log dalam detik. */
export function totalDurationSeconds(logs: TimerLog[]): number {
  return logs.reduce((sum, log) => sum + Math.max(0, log.duration_seconds ?? 0), 0)
}

/**
 * stop_reason → label singkat. "manual" (dihentikan user) tidak butuh label,
 * sisanya (auto-stop oleh backend) ditandai supaya kelihatan bukan aksi sengaja.
 */
export function formatStopReason(reason: string | null): string | null {
  switch (reason) {
    case null:
    case 'manual':
      return null
    case 'normal_close':
      return 'Tab ditutup'
    case 'no_response':
      return 'Tidak ada respons'
    case 'unexpected_close':
      return 'Auto-stop (idle)'
    default:
      return reason
  }
}
