import http from '../../../app/api'

export async function createSubtask(taskId: string, title: string) {
  const res = await http.post(`/tasks/${taskId}/subtasks`, { task_id: taskId, title })
  return res.data?.data ?? res.data
}

export async function updateSubtask(subtaskId: string, payload: { title?: string }) {
  const res = await http.patch(`/subtasks/${subtaskId}`, payload)
  return res.data?.data ?? res.data
}

export async function deleteSubtask(subtaskId: string) {
  await http.delete(`/subtasks/${subtaskId}`)
}

export async function completeSubtask(subtaskId: string, isCompleted: boolean) {
  const res = await http.patch(`/subtasks/${subtaskId}/complete`, { is_completed: isCompleted })
  return res.data?.data ?? res.data
}

export async function moveSubtask(subtaskId: string, position: number) {
  const res = await http.patch(`/subtasks/${subtaskId}/move`, { position })
  return res.data?.data ?? res.data
}