// src/modules/board/utils/due-date.util.ts
// Status deadline task: dipakai di card detail, card front (board), dan dashboard.

export type DueDateStatus = 'overdue' | 'soon' | 'normal' | 'none'

export function parseDueDate(due?: string | null): Date | null {
  if (!due || due === '-') return null
  const d = new Date(due)
  return Number.isNaN(d.getTime()) ? null : d
}

/** 'overdue' kalau sudah lewat, 'soon' kalau H-2, selain itu 'normal'/'none'. */
export function dueDateStatus(due?: string | null): DueDateStatus {
  const d = parseDueDate(due)
  if (!d) return 'none'
  const diffMs = d.getTime() - Date.now()
  const twoDaysMs = 2 * 24 * 60 * 60 * 1000
  if (diffMs < 0) return 'overdue'
  if (diffMs <= twoDaysMs) return 'soon'
  return 'normal'
}

export function dueDateBadgeClass(status: DueDateStatus): string {
  if (status === 'overdue') return 'bg-red-100 text-red-600 border border-red-200'
  if (status === 'soon') return 'bg-amber-100 text-amber-700 border border-amber-200'
  return 'bg-gray-100 text-gray-500 border border-gray-200'
}

/** ISO string → "YYYY-MM-DD" untuk value <input type="date">. */
export function dueDateInputValue(due?: string | null): string {
  const d = parseDueDate(due)
  if (!d) return ''
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}
