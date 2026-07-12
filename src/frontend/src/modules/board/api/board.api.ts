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

export async function addComment(taskId: string, content: string) {
  const res = await api.post(`/tasks/${taskId}/comments`, { content })
  return res.data?.data ?? res.data
}

export async function deleteComment(commentId: string) {
  await api.delete(`/tasks/comments/${commentId}`)
}

// ─── Attachments — pakai http (tanpa /api/v1) ─────────────────

export async function uploadAttachmentFile(taskId: string, file: File) {
  const formData = new FormData()
  formData.append('file', file)
  const res = await http.post(`/tasks/${taskId}/attachments/file`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return res.data?.data ?? res.data
}

export async function addAttachmentLink(taskId: string, title: string, url: string) {
  const res = await http.post(`/tasks/${taskId}/attachments/link`, { title, url })
  return res.data?.data ?? res.data
}

export async function deleteAttachment(attachId: string) {
  await http.delete(`/tasks/attachments/${attachId}`)
}