<template>
  <Layout>
    <div class="p-6">
      <div class="flex items-center justify-between mb-6">
        <div>
          <h1 class="text-xl font-bold text-gray-800">My Boards</h1>
          <p class="text-sm text-gray-400 mt-0.5">{{ boards.length }} board{{ boards.length === 1 ? '' : 's' }}</p>
        </div>
        <button @click="showCreate = true"
          class="flex items-center gap-2 bg-blue-500 text-white text-sm font-medium px-4 py-2 rounded-lg hover:bg-blue-600 transition shadow-sm">
          <font-awesome-icon icon="plus" /> New Board
        </button>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        <div v-for="i in 4" :key="i" class="rounded-xl bg-gray-100 animate-pulse aspect-[4/3]"></div>
      </div>

      <!-- Empty -->
      <div v-else-if="boards.length === 0"
        class="border border-dashed border-gray-300 rounded-2xl p-16 text-center">
        <font-awesome-icon icon="clipboard-list" class="text-3xl text-gray-300 mb-3 block mx-auto" />
        <p class="text-sm text-gray-500 font-medium">Belum ada board</p>
        <p class="text-xs text-gray-400 mt-1">Buat board pertama Anda untuk mulai mengatur task.</p>
      </div>

      <!-- Board Grid -->
      <div v-else class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        <div v-for="board in boards" :key="board.id" @click="router.push(`/boards/${board.id}`)"
          class="group rounded-xl border border-gray-200 bg-white overflow-hidden cursor-pointer hover:shadow-lg hover:-translate-y-0.5 transition-all duration-150 aspect-[4/3] flex flex-col">
          <div class="h-2/3 flex items-center justify-center relative flex-shrink-0"
            :class="boardGradient(board.id)">
            <span class="text-3xl font-bold text-white/90 select-none">{{ (board.title || '?').charAt(0).toUpperCase() }}</span>

            <div class="absolute top-2 right-2" @click.stop>
              <button @click.stop="toggleMenu(board.id)"
                class="w-7 h-7 rounded-lg flex items-center justify-center bg-black/20 hover:bg-black/30 text-white opacity-0 group-hover:opacity-100 transition"
                :class="openMenuId === board.id ? 'opacity-100' : ''">
                <font-awesome-icon icon="ellipsis-h" class="text-xs" />
              </button>
              <div v-if="openMenuId === board.id"
                class="absolute right-0 top-8 bg-white border border-gray-200 rounded-xl shadow-xl z-20 w-40 py-1 overflow-hidden text-left">
                <button @click.stop="startRename(board)"
                  class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition">Rename</button>
                <button @click.stop="startDelete(board)"
                  class="w-full text-left px-4 py-2 text-sm text-red-500 hover:bg-red-50 transition">Delete</button>
              </div>
            </div>
          </div>
          <div class="flex-1 px-3.5 py-2.5 flex flex-col justify-center min-w-0">
            <h3 class="font-semibold text-sm text-gray-800 truncate">{{ board.title }}</h3>
            <p class="text-xs text-gray-400 mt-0.5">{{ formatCreatedAt(board.created_at) }}</p>
          </div>
        </div>
      </div>

      <!-- Create Board Modal -->
      <div v-if="showCreate" class="fixed inset-0 z-50 flex items-center justify-center"
        style="background: rgba(0,0,0,0.5)" @click.self="showCreate = false">
        <div class="bg-white rounded-2xl shadow-2xl p-6 w-full max-w-sm mx-4">
          <h2 class="text-base font-bold text-gray-800 mb-4">Create Board</h2>
          <input v-model="newTitle" @keyup.enter="handleCreate" placeholder="Board title..." autofocus
            class="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 outline-none focus:border-blue-400 transition mb-3" />
          <div class="flex gap-2">
            <button @click="handleCreate" :disabled="creating || !newTitle.trim()"
              class="flex-1 bg-blue-500 text-white text-sm py-2 rounded-lg hover:bg-blue-600 disabled:opacity-50 transition">
              {{ creating ? 'Creating...' : 'Create' }}
            </button>
            <button @click="showCreate = false; newTitle = ''" class="text-sm text-gray-400 px-3 hover:text-gray-600">
              Cancel
            </button>
          </div>
        </div>
      </div>

      <!-- Rename Board Modal -->
      <div v-if="renamingBoard" class="fixed inset-0 z-50 flex items-center justify-center"
        style="background: rgba(0,0,0,0.5)" @click.self="renamingBoard = null">
        <div class="bg-white rounded-2xl shadow-2xl p-6 w-full max-w-sm mx-4">
          <h2 class="text-base font-bold text-gray-800 mb-4">Rename Board</h2>
          <input v-model="renameTitle" @keyup.enter="handleRenameSubmit" @keyup.esc="renamingBoard = null" autofocus
            class="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 outline-none focus:border-blue-400 transition mb-3" />
          <div class="flex gap-2">
            <button @click="handleRenameSubmit" :disabled="renaming || !renameTitle.trim()"
              class="flex-1 bg-blue-500 text-white text-sm py-2 rounded-lg hover:bg-blue-600 disabled:opacity-50 transition">
              {{ renaming ? 'Saving...' : 'Save' }}
            </button>
            <button @click="renamingBoard = null" class="text-sm text-gray-400 px-3 hover:text-gray-600">
              Cancel
            </button>
          </div>
        </div>
      </div>

      <!-- Delete Board Confirmation -->
      <div v-if="deletingBoard" class="fixed inset-0 z-50 flex items-center justify-center"
        style="background: rgba(0,0,0,0.65)" @click.self="deletingBoard = null">
        <div class="bg-white rounded-2xl shadow-2xl w-full max-w-sm mx-4 p-5">
          <p class="text-sm font-semibold text-gray-800 mb-2">Hapus board ini?</p>
          <p class="text-xs text-gray-500 leading-relaxed mb-5">
            Board "{{ deletingBoard.title }}" beserta seluruh column dan card di dalamnya akan tidak bisa diakses lagi.
            Tindakan ini tidak bisa dibatalkan.
          </p>
          <div class="flex gap-2 justify-end">
            <button @click="deletingBoard = null"
              class="text-xs text-gray-600 border border-gray-300 rounded-lg px-4 py-2 hover:bg-gray-50 transition">
              Batal
            </button>
            <button @click="handleDeleteSubmit"
              class="text-xs text-white bg-red-500 hover:bg-red-600 rounded-lg px-4 py-2 transition">
              Ya, hapus
            </button>
          </div>
        </div>
      </div>

      <!-- Toast -->
      <Teleport to="body">
        <Transition name="toast">
          <div v-if="toast"
            class="fixed bottom-6 left-1/2 -translate-x-1/2 z-[60] bg-gray-900 text-white text-sm px-5 py-2.5 rounded-xl shadow-lg pointer-events-none">
            {{ toast }}
          </div>
        </Transition>
      </Teleport>
    </div>
  </Layout>
</template>
<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import Layout from '../../../components/common/AppLayout.vue'
import { useAppStore } from '../../board/store/board.store'
import { storeToRefs } from 'pinia'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { library } from '@fortawesome/fontawesome-svg-core'
import { faPlus, faEllipsisH, faClipboardList } from '@fortawesome/free-solid-svg-icons'

library.add(faPlus, faEllipsisH, faClipboardList)

const router = useRouter()
const store = useAppStore()
const { boards } = storeToRefs(store)

const loading = ref(false)
const creating = ref(false)
const showCreate = ref(false)
const newTitle = ref('')
const toast = ref('')
let toastTimer: ReturnType<typeof setTimeout> | null = null

function showToast(msg: string) {
  toast.value = msg
  if (toastTimer) clearTimeout(toastTimer)
  toastTimer = setTimeout(() => { toast.value = '' }, 2500)
}

// ─── Board card menu (⋮) ────────────────────────────────────────
// Tidak ada opsi ubah warna/cover board — board_model.py cuma punya
// id/user_id/title/created_at/updated_at/deleted_at, tidak ada field warna
// atau cover sama sekali. Gradient di kartu di bawah murni dekoratif
// (hash dari board id), bukan fitur yang bisa dipilih/disimpan user.
const openMenuId = ref<string | null>(null)

function toggleMenu(boardId: string) {
  openMenuId.value = openMenuId.value === boardId ? null : boardId
}

function closeMenu() {
  openMenuId.value = null
}

onMounted(() => document.addEventListener('click', closeMenu))
onUnmounted(() => document.removeEventListener('click', closeMenu))

const gradients = [
  'bg-gradient-to-br from-blue-500 to-blue-600',
  'bg-gradient-to-br from-emerald-500 to-emerald-600',
  'bg-gradient-to-br from-purple-500 to-purple-600',
  'bg-gradient-to-br from-amber-500 to-amber-600',
  'bg-gradient-to-br from-rose-500 to-rose-600',
  'bg-gradient-to-br from-cyan-500 to-cyan-600',
  'bg-gradient-to-br from-indigo-500 to-indigo-600',
]

function boardGradient(id: string): string {
  let hash = 0
  for (let i = 0; i < id.length; i++) hash = (hash * 31 + id.charCodeAt(i)) >>> 0
  return gradients[hash % gradients.length]
}

function formatCreatedAt(iso: string): string {
  if (!iso) return ''
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return ''
  return `Dibuat ${d.toLocaleDateString('id-ID', { day: '2-digit', month: 'short', year: 'numeric' })}`
}

async function fetchBoards() {
  loading.value = true
  try {
    await store.fetchBoards()  // ← tidak fetch ulang kalau sudah ada
  } catch {
    showToast('Gagal memuat boards.')
  } finally {
    loading.value = false
  }
}

async function handleCreate() {
  if (!newTitle.value.trim() || creating.value) return
  creating.value = true
  try {
    const board = await store.addBoard(newTitle.value.trim())
    newTitle.value = ''
    showCreate.value = false
    showToast(`Board "${board.title}" created!`)
  } catch {
    showToast('Gagal membuat board.')
  } finally {
    creating.value = false
  }
}

// ─── Rename ───────────────────────────────────────────────────
const renamingBoard = ref<any | null>(null)
const renameTitle = ref('')
const renaming = ref(false)

function startRename(board: any) {
  openMenuId.value = null
  renamingBoard.value = board
  renameTitle.value = board.title
}

async function handleRenameSubmit() {
  if (!renamingBoard.value || !renameTitle.value.trim() || renaming.value) return
  renaming.value = true
  try {
    await store.renameBoard(renamingBoard.value.id, renameTitle.value.trim())
    showToast('Board renamed.')
    renamingBoard.value = null
  } catch (e: any) {
    showToast(e?.response?.data?.error?.message || 'Gagal mengubah nama board.')
  } finally {
    renaming.value = false
  }
}

// ─── Delete ───────────────────────────────────────────────────
const deletingBoard = ref<any | null>(null)

function startDelete(board: any) {
  openMenuId.value = null
  deletingBoard.value = board
}

async function handleDeleteSubmit() {
  if (!deletingBoard.value) return
  const board = deletingBoard.value
  deletingBoard.value = null
  try {
    await store.removeBoard(board.id)
    showToast('Board deleted.')
  } catch (e: any) {
    showToast(e?.response?.data?.error?.message || 'Gagal menghapus board.')
  }
}

onMounted(fetchBoards)
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.25s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(12px);
}
</style>
