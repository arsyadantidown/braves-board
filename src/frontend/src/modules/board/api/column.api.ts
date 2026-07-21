// src/services/columnService.ts
import http from '../../../app/api'

// Backend: require_permission() butuh board_id sebagai query param wajib
// (untuk permission check), TERPISAH dari board_id di body (kalau endpoint
// itu memang butuh board_id sebagai data, mis. ColumnCreate). Cek
// src/backend/app/api/column/views.py — setiap route yang tidak punya
// {board_id} di path mendeklarasikan board_id sebagai parameter biasa,
// yang di-resolve FastAPI sebagai query param.

export async function getColumns(boardId: string) {
    const res = await http.get('/columns', { params: { board_id: boardId } })
    return res.data?.data ?? res.data ?? []
}

// columnService.ts
export async function createColumn(boardId: string, title: string) {
    try {
        // board_id dibutuhkan DUA kali: query (permission check) + body (ColumnCreate.board_id)
        const res = await http.post('/columns', { title, board_id: boardId }, { params: { board_id: boardId } })
        return res.data?.data ?? res.data
    } catch (e: any) {
        console.log('create column error detail:', e.response?.data) // ← tambah ini
        throw e
    }
}

export async function updateColumn(columnId: string, boardId: string, payload: { title?: string }) {
    const res = await http.patch(`/columns/${columnId}`, payload, { params: { board_id: boardId } })
    return res.data?.data ?? res.data
}

export async function deleteColumn(columnId: string, boardId: string) {
    await http.delete(`/columns/${columnId}`, { params: { board_id: boardId } })
}

export async function reorderColumn(columnId: string, newPosition: number, boardId: string) {
    // new_position DAN board_id sama-sama query param — bukan Pydantic body model di backend.
    const res = await http.patch(`/columns/${columnId}/reorder`, null, {
        params: { new_position: newPosition, board_id: boardId },
    })
    return res.data?.data ?? res.data
}
