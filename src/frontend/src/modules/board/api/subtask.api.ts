import http from '../../../app/api'

// Backend: require_permission() butuh board_id, tapi endpoint /subtasks/*
// tidak mendeklarasikannya di path — FastAPI resolve sebagai query param
// wajib. Semua call di bawah HARUS menyertakan board_id.

export async function createSubtask(taskId: string, title: string, boardId: string) {
  const res = await http.post(`/tasks/${taskId}/subtasks`, { task_id: taskId, title }, { params: { board_id: boardId } })
  return res.data?.data ?? res.data
}

export async function updateSubtask(subtaskId: string, payload: { title?: string }, boardId: string) {
  const res = await http.patch(`/subtasks/${subtaskId}`, payload, { params: { board_id: boardId } })
  return res.data?.data ?? res.data
}

export async function deleteSubtask(subtaskId: string, boardId: string) {
  await http.delete(`/subtasks/${subtaskId}`, { params: { board_id: boardId } })
}

export async function completeSubtask(subtaskId: string, isCompleted: boolean, boardId: string) {
  const res = await http.patch(`/subtasks/${subtaskId}/complete`, { is_completed: isCompleted }, { params: { board_id: boardId } })
  return res.data?.data ?? res.data
}

export async function moveSubtask(subtaskId: string, position: number, boardId: string) {
  const res = await http.patch(`/subtasks/${subtaskId}/move`, { position }, { params: { board_id: boardId } })
  return res.data?.data ?? res.data
}
