import http from '../../../app/api'

// Backend: require_permission() butuh board_id, tapi endpoint /tasks/* tidak
// mendeklarasikannya di path — FastAPI resolve sebagai query param wajib.
// Semua call di bawah HARUS menyertakan board_id, atau backend balas 422
// "board_id: Field required".

export async function getTasks(columnId: string, boardId: string) {
  const res = await http.get('/tasks', { params: { column_id: columnId, board_id: boardId } })
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
