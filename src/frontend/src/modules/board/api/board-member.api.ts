// src/modules/board/api/board-member.api.ts
// Semua API call yang berhubungan dengan Board Members (role: owner/admin/member)

import http from '../../../app/api'

export type BoardRole = 'owner' | 'admin' | 'member'

export interface BoardMember {
  id: string
  board_id: string
  user_id: string
  role: BoardRole
  created_at: string
  updated_at: string
}

export async function getBoardMembers(boardId: string): Promise<BoardMember[]> {
  const res = await http.get(`/boards/${boardId}/members`)
  return res.data?.data ?? res.data ?? []
}

export async function addBoardMember(boardId: string, userId: string, role: BoardRole = 'member'): Promise<BoardMember> {
  const res = await http.post(`/boards/${boardId}/members`, { user_id: userId, role })
  return res.data?.data ?? res.data
}

export async function updateBoardMemberRole(boardId: string, userId: string, role: BoardRole): Promise<BoardMember> {
  const res = await http.patch(`/boards/${boardId}/members/${userId}`, { role })
  return res.data?.data ?? res.data
}

export async function removeBoardMember(boardId: string, userId: string): Promise<void> {
  await http.delete(`/boards/${boardId}/members/${userId}`)
}
