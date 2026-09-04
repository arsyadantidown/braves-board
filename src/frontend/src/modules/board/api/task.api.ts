import http from '../../../app/api'

// Backend: require_permission() butuh board_id, tapi endpoint /tasks/* tidak
// mendeklarasikannya di path — FastAPI resolve sebagai query param wajib.
// Semua call di bawah HARUS menyertakan board_id, atau backend balas 422
// "board_id: Field required".

// assigneeId opsional → backend GET /tasks mendukung filter ?assignee_id=...
// (commit backend "add task filter by assignee": Task.assignee_ids.any(id)).
// Hanya dikirim kalau ada, supaya perilaku default (semua task) tidak berubah.
export async function getTasks(columnId: string, boardId: string, assigneeId?: string) {
  const params: Record<string, string> = { column_id: columnId, board_id: boardId }
  if (assigneeId) params.assignee_id = assigneeId
  const res = await http.get('/tasks', { params })
  return res.data?.data ?? res.data ?? []
}

export async function getTaskDetail(taskId: string, boardId: string) {
  const res = await http.get(`/tasks/${taskId}`, { params: { board_id: boardId } })
  return res.data?.data ?? res.data
}

export async function createTask(columnId: string, title: string, boardId: string) {
  const res = await http.post('/tasks', { column_id: columnId, title }, { params: { board_id: boardId } })
  return res.data?.data ?? res.data
}

export async function updateTask(taskId: string, payload: object, boardId: string) {
  const res = await http.patch(`/tasks/${taskId}`, payload, { params: { board_id: boardId } })
  return res.data?.data ?? res.data
}

export async function deleteTask(taskId: string, boardId: string) {
  await http.delete(`/tasks/${taskId}`, { params: { board_id: boardId } })
}

// Set status "complete" pada level task. Endpoint ini BELUM ADA di backend
// (is_completed masih read-only) — lihat BACKEND_REQUESTS.md poin 1. Ditulis
// sesuai kontrak yang direkomendasikan (mirror PATCH /subtasks/{id}/complete)
// supaya begitu backend menyediakannya, langsung berfungsi tanpa ubah UI.
export async function setTaskComplete(taskId: string, isCompleted: boolean, boardId: string) {
  const res = await http.patch(`/tasks/${taskId}/complete`, { is_completed: isCompleted }, { params: { board_id: boardId } })
  return res.data?.data ?? res.data
}

export async function archiveTask(taskId: string, boardId: string) {
  const res = await http.patch(`/tasks/${taskId}/archive`, null, { params: { board_id: boardId } })
  return res.data?.data ?? res.data
}

export async function unarchiveTask(taskId: string, boardId: string) {
  const res = await http.patch(`/tasks/${taskId}/unarchive`, null, { params: { board_id: boardId } })
  return res.data?.data ?? res.data
}

export async function moveTask(taskId: string, columnId: string, position: number, boardId: string) {
  const res = await http.patch(`/tasks/${taskId}/move`, {
    column_id: columnId,
    position,
  }, { params: { board_id: boardId } })
  return res.data?.data ?? res.data
}

export async function reorderTask(taskId: string, position: number, boardId: string) {
  const res = await http.patch(`/tasks/${taskId}/reorder`, { position }, { params: { board_id: boardId } })
  return res.data?.data ?? res.data
}
