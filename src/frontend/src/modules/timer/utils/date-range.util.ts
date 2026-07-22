// src/modules/timer/utils/date-range.util.ts
// Preset rentang tanggal untuk filter Time Tracker (Clockify-style).

export type DateRangePreset = 'today' | 'week' | 'month' | 'custom'

function startOfDay(d: Date): Date {
  const r = new Date(d)
  r.setHours(0, 0, 0, 0)
  return r
}

function endOfDay(d: Date): Date {
  const r = new Date(d)
  r.setHours(23, 59, 59, 999)
  return r
}

/** Awal minggu (Senin) untuk tanggal tertentu. */
function startOfWeek(d: Date): Date {
  const r = startOfDay(d)
  const day = r.getDay() // 0 = Minggu
  const diff = day === 0 ? 6 : day - 1 // jarak ke Senin
  r.setDate(r.getDate() - diff)
  return r
}

function startOfMonth(d: Date): Date {
  const r = startOfDay(d)
  r.setDate(1)
  return r
}

export interface DateRange {
  start: Date
  end: Date
}

export function resolveDateRange(preset: DateRangePreset, customStart?: string, customEnd?: string): DateRange {
  const now = new Date()

  if (preset === 'today') {
    return { start: startOfDay(now), end: endOfDay(now) }
  }
  if (preset === 'week') {
    return { start: startOfWeek(now), end: endOfDay(now) }
  }
  if (preset === 'month') {
    return { start: startOfMonth(now), end: endOfDay(now) }
  }

  // custom
  const start = customStart ? startOfDay(new Date(customStart)) : startOfDay(now)
  const end = customEnd ? endOfDay(new Date(customEnd)) : endOfDay(now)
  return { start, end }
}

export function isWithinRange(iso: string | null, range: DateRange): boolean {
  if (!iso) return false
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return false
  return d >= range.start && d <= range.end
}

/** Key pengelompokan per hari, mis. "2026-07-21". */
export function dayKey(iso: string | null): string {
  if (!iso) return 'unknown'
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return 'unknown'
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

/** "2026-07-21" → "Senin, 21 Jul 2026". */
export function formatDayHeading(key: string): string {
  if (key === 'unknown') return 'Tanggal tidak diketahui'
  const d = new Date(`${key}T00:00:00`)
  if (Number.isNaN(d.getTime())) return key
  return d.toLocaleDateString('id-ID', { weekday: 'long', day: '2-digit', month: 'short', year: 'numeric' })
}
