// src/modules/board/api/board.api.ts
// Semua API call yang berhubungan dengan Boards

import api from '../../../app/api'

// Menggunakan centralized API client untuk semua endpoint
const http = api

// ─── Boards ───────────────────────────────────────────────────

export async function getBoards(limit = 100, offset = 0) {
  const res = await api.get('/boards', { params: { limit, offset } })
  return res.data?.data ?? res.data ?? {}
}

export async function createBoard(title: string) {
  const res = await api.post('/boards', { title })
  return res.data?.data ?? res.data
}

export async function getBoardDetail(boardId: string) {
  const res = await api.get(`/boards/${boardId}`)
  return res.data?.data ?? res.data
}

export async function updateBoard(boardId: string, title: string) {
  const res = await api.patch(`/boards/${boardId}`, { title })
  return res.data?.data ?? res.data
}

export async function deleteBoard(boardId: string) {
  await api.delete(`/boards/${boardId}`)
}

// ─── Users ───────────────────────────────────────────────────────

export async function getUsers() {
  const res = await api.get('/users')
  return res.data?.data ?? res.data ?? []
}

// ─── Comments ─────────────────────────────────────────────────
// Backend: require_permission() butuh board_id, tapi endpoint /tasks/*
// tidak mendeklarasikannya di path — FastAPI resolve sebagai query param
// wajib. Semua call di bawah HARUS menyertakan board_id.

export async function addComment(taskId: string, content: string, boardId: string) {
  const res = await api.post(`/tasks/${taskId}/comments`, { content }, { params: { board_id: boardId } })
  return res.data?.data ?? res.data
}

export async function deleteComment(commentId: string, boardId: string) {
  await api.delete(`/tasks/comments/${commentId}`, { params: { board_id: boardId } })
}

// ─── Attachments — pakai http (tanpa /api/v1) ─────────────────

export async function uploadAttachmentFile(taskId: string, file: File, boardId: string) {
  const formData = new FormData()
  formData.append('file', file)
  const res = await http.post(`/tasks/${taskId}/attachments/file`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    params: { board_id: boardId },
  })
  return res.data?.data ?? res.data
}

export async function addAttachmentLink(taskId: string, title: string, url: string, boardId: string) {
  const res = await http.post(`/tasks/${taskId}/attachments/link`, { title, url }, { params: { board_id: boardId } })
  return res.data?.data ?? res.data
}

export async function deleteAttachment(attachId: string, boardId: string) {
  await http.delete(`/tasks/attachments/${attachId}`, { params: { board_id: boardId } })
}