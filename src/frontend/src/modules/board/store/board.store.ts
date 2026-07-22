import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getBoards, createBoard as apiCreateBoard, getUsers as apiGetUsers } from '../api/board.api'
import { getColumns, createColumn as apiCreateColumn } from '../api/column.api'
import {
  getTasks,
  createTask as apiCreateTask,
  deleteTask as apiDeleteTask,
  updateTask as apiUpdateTask,
  moveTask as apiMoveTask,
} from '../api/task.api'
import { createSubtask as apiCreateSubtask, updateSubtask as apiUpdateSubtask, deleteSubtask as apiDeleteSubtask, completeSubtask as apiCompleteSubtask } from '../api/subtask.api'
import {
  getBoardMembers as apiGetBoardMembers,
  addBoardMember as apiAddBoardMember,
  updateBoardMemberRole as apiUpdateBoardMemberRole,
  removeBoardMember as apiRemoveBoardMember,
  type BoardMember,
  type BoardRole,
} from '../api/board-member.api'

export const useAppStore = defineStore('app', () => {
  // ─── Boards ───────────────────────────────────────────
  const boards = ref<any[]>([])
  const boardsLoaded = ref(false)

  async function fetchBoards(force = false) {
    if (boardsLoaded.value && !force) return
    const res = await getBoards()
    boards.value = Array.isArray(res) ? res : res.items ?? res.data ?? []
    boardsLoaded.value = true
  }

  async function addBoard(title: string) {
    const board = await apiCreateBoard(title)
    boards.value.push(board)
    return board
  }

  // ─── Users ────────────────────────────────────────────
  const users = ref<any[]>([])
  const usersLoaded = ref(false)

  async function fetchUsers(force = false) {
    if (usersLoaded.value && !force) return
    const res = await apiGetUsers()
    users.value = Array.isArray(res) ? res : res.items ?? res.data ?? []
    usersLoaded.value = true
  }

  // ─── Board Members ──────────────────────────────────────
  const boardMembers = ref<Record<string, BoardMember[]>>({})

  async function fetchBoardMembers(boardId: string, force = false) {
    if (boardMembers.value[boardId] && !force) return
    boardMembers.value[boardId] = await apiGetBoardMembers(boardId)
  }

  async function addBoardMemberToStore(boardId: string, userId: string, role: BoardRole = 'member') {
    const member = await apiAddBoardMember(boardId, userId, role)
    if (!boardMembers.value[boardId]) boardMembers.value[boardId] = []
    boardMembers.value[boardId].push(member)
    return member
  }

  async function updateBoardMemberRoleInStore(boardId: string, userId: string, role: BoardRole) {
    await apiUpdateBoardMemberRole(boardId, userId, role)
    const m = boardMembers.value[boardId]?.find(m => m.user_id === userId)
    if (m) m.role = role
  }

  async function removeBoardMemberFromStore(boardId: string, userId: string) {
    await apiRemoveBoardMember(boardId, userId)
    if (boardMembers.value[boardId]) {
      boardMembers.value[boardId] = boardMembers.value[boardId].filter(m => m.user_id !== userId)
    }
  }

  function getMyRole(boardId: string, userId?: string | null): BoardRole | null {
    if (!userId) return null
    return boardMembers.value[boardId]?.find(m => m.user_id === userId)?.role ?? null
  }

  // ─── Columns ──────────────────────────────────────────
  const columnsByBoard = ref<Record<string, any[]>>({})

  async function fetchColumns(boardId: string, force = false) {
    if (columnsByBoard.value[boardId] && !force) return
    try {
      const cols = await getColumns(boardId)
      columnsByBoard.value[boardId] = cols.map((col: any) => ({
        id: col.id,
        title: col.title,
        tasks: normalizeTaskList(col.tasks ?? []),
      }))
    } catch (e) {
      console.error('fetchColumns RAW error:', e)
      throw e
    }
  }

  async function addColumn(boardId: string, title: string) {
    const col = await apiCreateColumn(boardId, title)
    const newCol = { id: col.id, title: col.title, tasks: [] }
    if (!columnsByBoard.value[boardId]) columnsByBoard.value[boardId] = []
    columnsByBoard.value[boardId].push(newCol)
    return newCol
  }

  // ─── Tasks ────────────────────────────────────────────
  function normalizeTask(task: any, columnId?: string) {
    return {
      id: task.id,
      title: task.title,
      subtasks: (task.subtasks ?? []).map((s: any) => ({
        id: s.id,
        title: s.title,
        completed: s.is_completed ?? s.completed ?? false,
      })),
      assignee_ids: task.assignee_ids ?? [],
      labels: task.labels ?? [],
      activity: task.activity ?? [],
      attachments: task.attachments ?? [],
      time: task.time ?? '00:00:00',
      dueDate: task.due_date ?? task.dueDate ?? '-',
      label: task.label ?? null,
      labelClass: task.labelClass ?? null,
      description: task.description ?? '',
      status: task.status ?? 'To Do',
      column_id: task.column_id ?? columnId ?? null,
    }
  }

  function normalizeTaskList(tasks: any[], columnId?: string) {
    return tasks.map(t => normalizeTask(t, columnId))
  }

  function findColById(columnId: string) {
    for (const boardId in columnsByBoard.value) {
      const col = columnsByBoard.value[boardId].find((c: any) => c.id === columnId)
      if (col) return col
    }
    return null
  }

  function findTaskInStore(taskId: string): { col: any; idx: number } | null {
    for (const boardId in columnsByBoard.value) {
      for (const col of columnsByBoard.value[boardId]) {
        const idx = col.tasks.findIndex((t: any) => t.id === taskId)
        if (idx !== -1) return { col, idx }
      }
    }
    return null
  }

  // Backend: require_permission() butuh board_id via query param (bug pada
  // endpoint /tasks, /subtasks, /timer — lihat catatan di api/task.api.ts).
  // columnsByBoard sudah di-key by boardId, jadi resolve dari situ.
  function findBoardIdForColumn(columnId: string): string | null {
    for (const boardId in columnsByBoard.value) {
      if (columnsByBoard.value[boardId].some((c: any) => c.id === columnId)) return boardId
    }
    return null
  }

  function findBoardIdForTask(taskId: string): string | null {
    for (const boardId in columnsByBoard.value) {
      for (const col of columnsByBoard.value[boardId]) {
        if (col.tasks.some((t: any) => t.id === taskId)) return boardId
      }
    }
    return null
  }

  async function fetchTasks(columnId: string) {
    const boardId = findBoardIdForColumn(columnId)
    if (!boardId) return
    const tasks = await getTasks(columnId, boardId)
    const col = findColById(columnId)
    if (col) col.tasks = normalizeTaskList(tasks)
  }

  async function addTask(columnId: string, title: string) {
    const boardId = findBoardIdForColumn(columnId)
    if (!boardId) throw new Error('Board tidak ditemukan untuk column ini.')
    const task = await apiCreateTask(columnId, title, boardId)
    const normalized = {
      ...normalizeTask(task),
      column_id: task.column_id ?? columnId,
    }
    const col = findColById(columnId)
    if (col) col.tasks.push(normalized)
    return normalized
  }

  async function editTask(taskId: string, payload: object) {
    const boardId = findBoardIdForTask(taskId)
    if (!boardId) throw new Error('Board tidak ditemukan untuk task ini.')
    await apiUpdateTask(taskId, payload, boardId)
    const found = findTaskInStore(taskId)
    if (found) {
      found.col.tasks[found.idx] = { ...found.col.tasks[found.idx], ...payload }
    }
  }

  async function removeTask(taskId: string, columnId: string) {
    const boardId = findBoardIdForColumn(columnId)
    if (!boardId) throw new Error('Board tidak ditemukan untuk task ini.')
    await apiDeleteTask(taskId, boardId)
    const col = findColById(columnId)
    if (col) col.tasks = col.tasks.filter((t: any) => t.id !== taskId)
  }

  async function moveTaskToColumn(taskId: string, fromColumnId: string, toColumnId: string) {
    const boardId = findBoardIdForColumn(fromColumnId)
    if (!boardId) throw new Error('Board tidak ditemukan untuk task ini.')
    const toCol = findColById(toColumnId)
    // Backend mewajibkan position >= 1 — taruh di akhir column tujuan.
    const position = (toCol?.tasks?.length ?? 0) + 1

    await apiMoveTask(taskId, toColumnId, position, boardId)

    const fromCol = findColById(fromColumnId)
    if (fromCol && toCol) {
      const idx = fromCol.tasks.findIndex((t: any) => t.id === taskId)
      if (idx !== -1) {
        const [task] = fromCol.tasks.splice(idx, 1)
        task.column_id = toColumnId
        toCol.tasks.push(task)
      }
    }
  }

  async function addSubtask(taskId: string, title: string) {
    const boardId = findBoardIdForTask(taskId)
    if (!boardId) throw new Error('Board tidak ditemukan untuk task ini.')
    const res = await apiCreateSubtask(taskId, title, boardId)
    const newSubtask = {
      id: res.id ?? res,
      title,
      completed: false,
    }
    for (const bId in columnsByBoard.value) {
      for (const col of columnsByBoard.value[bId]) {
        const task = col.tasks.find((t: any) => t.id === taskId)
        if (task) {
          if (!task.subtasks) task.subtasks = []
          task.subtasks.push(newSubtask)
          break
        }
      }
    }
    return newSubtask
  }

  async function toggleSubtask(subtaskId: string, taskId: string, completed: boolean) {
    const boardId = findBoardIdForTask(taskId)
    if (!boardId) throw new Error('Board tidak ditemukan untuk task ini.')
    await apiCompleteSubtask(subtaskId, completed, boardId)
    for (const bId in columnsByBoard.value) {
      for (const col of columnsByBoard.value[bId]) {
        const task = col.tasks.find((t: any) => t.id === taskId)
        if (task) {
          const sub = task.subtasks?.find((s: any) => s.id === subtaskId)
          if (sub) sub.completed = completed
          break
        }
      }
    }
  }

  async function renameSubtask(subtaskId: string, taskId: string, title: string) {
    const boardId = findBoardIdForTask(taskId)
    if (!boardId) throw new Error('Board tidak ditemukan untuk task ini.')
    await apiUpdateSubtask(subtaskId, { title }, boardId)
    for (const bId in columnsByBoard.value) {
      for (const col of columnsByBoard.value[bId]) {
        const task = col.tasks.find((t: any) => t.id === taskId)
        if (task) {
          const sub = task.subtasks?.find((s: any) => s.id === subtaskId)
          if (sub) sub.title = title
          break
        }
      }
    }
  }

  async function removeSubtask(subtaskId: string, taskId: string) {
    const boardId = findBoardIdForTask(taskId)
    if (!boardId) throw new Error('Board tidak ditemukan untuk task ini.')
    await apiDeleteSubtask(subtaskId, boardId)
    for (const bId in columnsByBoard.value) {
      for (const col of columnsByBoard.value[bId]) {
        const task = col.tasks.find((t: any) => t.id === taskId)
        if (task) {
          task.subtasks = task.subtasks?.filter((s: any) => s.id !== subtaskId)
          break
        }
      }
    }
  }

  return {
    boards, boardsLoaded, fetchBoards, addBoard,
    users, usersLoaded, fetchUsers,
    boardMembers, fetchBoardMembers,
    addBoardMemberToStore, updateBoardMemberRoleInStore, removeBoardMemberFromStore, getMyRole,
    columnsByBoard, fetchColumns, addColumn,
    findBoardIdForColumn, findBoardIdForTask,
    fetchTasks, addTask, editTask, removeTask, moveTaskToColumn, addSubtask, toggleSubtask, renameSubtask, removeSubtask,
  }
}, {
  persist: {
    key: 'app-store',
    storage: localStorage,
    pick: ['boards', 'boardsLoaded', 'columnsByBoard'],
  }
})
