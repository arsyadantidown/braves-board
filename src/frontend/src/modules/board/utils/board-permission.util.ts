// src/modules/board/utils/board-permission.util.ts
// Cermin dari src/backend/app/core/permission.py — HARUS disinkronkan manual
// kalau backend menambah/mengubah permission key, karena tidak ada endpoint
// yang mengekspos tabel ini ke frontend.

import type { BoardRole } from '../api/board-member.api'

export type Permission =
  | 'board.view' | 'board.update' | 'board.delete'
  | 'member.view' | 'member.invite' | 'member.remove' | 'member.change_role'
  | 'column.view' | 'column.create' | 'column.rename' | 'column.move' | 'column.delete'
  | 'task.view' | 'task.create' | 'task.update' | 'task.archive' | 'task.delete'

const PERMISSIONS: Record<Permission, BoardRole[]> = {
  'board.view': ['owner', 'admin', 'member'],
  'board.update': ['owner', 'admin'],
  'board.delete': ['owner'],

  'member.view': ['owner', 'admin', 'member'],
  'member.invite': ['owner', 'admin'],
  'member.remove': ['owner', 'admin'],
  'member.change_role': ['owner'],

  'column.view': ['owner', 'admin', 'member'],
  'column.create': ['owner', 'admin'],
  'column.rename': ['owner', 'admin'],
  'column.move': ['owner', 'admin'],
  'column.delete': ['owner', 'admin'],

  'task.view': ['owner', 'admin', 'member'],
  'task.create': ['owner', 'admin', 'member'],
  'task.update': ['owner', 'admin', 'member'],
  'task.archive': ['owner', 'admin', 'member'],
  'task.delete': ['owner', 'admin'],
}

export function hasPermission(role: BoardRole | null | undefined, permission: Permission): boolean {
  if (!role) return false
  return PERMISSIONS[permission].includes(role)
}

/** Pesan default kalau request gagal karena 403 dari backend (lihat app/core/dependencies.py). */
export function permissionErrorMessage(detail?: string): string {
  if (detail === 'Not a board member') return 'Anda bukan member board ini.'
  if (detail === 'Permission denied') return 'Anda tidak punya izin untuk melakukan aksi ini.'
  return 'Akses ditolak.'
}
