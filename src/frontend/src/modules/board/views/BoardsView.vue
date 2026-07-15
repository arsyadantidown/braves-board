<template>
  <Layout>
    <div class="flex gap-3 overflow-x-auto pb-4 px-1">

      <!-- Column loop -->
      <VueDraggable v-model="columnsByBoard[boardId]" :animation="150" ghost-class="opacity-40"
        chosen-class="shadow-lg" handle=".column-drag-handle" class="flex gap-3" @end="onColumnDragEnd">
        <div v-for="board in columnsByBoard[boardId]" :key="board.id"
          class="min-w-[260px] max-w-[260px] flex flex-col rounded-xl border border-gray-200 bg-gray-50"
          style="max-height: calc(100vh - 120px)">

          <!-- Column Header -->
          <div class="column-drag-handle flex items-center justify-between px-3 py-2.5 border-b border-gray-200 cursor-grab active:cursor-grabbing">
            <div class="flex items-center gap-2">
              <span class="text-sm font-medium text-gray-700">{{ board.title }}</span>
              <span class="text-xs text-gray-400 bg-white border border-gray-200 rounded-full px-2 py-0.5 leading-none">
                {{ board.tasks?.length ?? 0 }}
              </span>
            </div>
            <span class="text-gray-400 text-base cursor-pointer hover:text-gray-600 leading-none select-none">···</span>
          </div>

        <!-- Task Cards -->
        <!-- Task Cards -->
        <div class="flex-1 overflow-y-auto px-2.5 py-2">
          <div v-if="!board.tasks?.length" class="text-xs text-gray-400 text-center py-8">No tasks</div>

          <VueDraggable v-model="board.tasks" group="tasks" :data-column-id="board.id" :animation="150"
            ghost-class="opacity-40" chosen-class="shadow-lg" class="flex flex-col gap-2 min-h-[40px]"
            @end="onTaskDragEnd">
            <div v-for="task in (board.tasks as Task[])" :key="task.id" :data-id="task.id"
              class="bg-white rounded-lg border border-gray-200 p-3 cursor-grab active:cursor-grabbing hover:border-blue-400 hover:shadow-md transition-all group"
              @click="openModal(task)">

              <div v-if="task.label" class="mb-2">
                <span class="inline-block text-[11px] font-medium px-2.5 py-0.5 rounded-full"
                  :class="task.labelClass ?? 'bg-green-100 text-green-700'">{{ task.label }}</span>
              </div>

              <p class="text-sm text-gray-800 leading-snug mb-2 font-normal">{{ task.title }}</p>

              <div class="flex flex-wrap gap-1.5 mb-2">
                <span v-if="task.dueDate && task.dueDate !== '-'"
                  class="flex items-center gap-1 text-[11px] px-2 py-0.5 rounded bg-gray-100 text-gray-500">
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  {{ task.dueDate }}
                </span>
                <span v-if="task.subtasks?.length" class="flex items-center gap-1 text-[11px] px-2 py-0.5 rounded"
                  :class="task.subtasks.filter(s => s.completed).length === task.subtasks.length ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'">
                  ✓ {{ task.subtasks.filter(s => s.completed).length }}/{{ task.subtasks.length }}
                </span>
                <span v-if="task.attachments?.length"
                  class="flex items-center gap-1 text-[11px] px-2 py-0.5 rounded bg-gray-100 text-gray-500">
                  📎 {{ task.attachments.length }}
                </span>
              </div>

              <div class="flex items-center justify-between mt-1">
                <div class="flex items-center gap-1 text-[11px] tabular-nums"
                  :class="activeTimerTaskId === task.id ? 'text-emerald-600 font-medium' : 'text-gray-400'">
                  <span class="w-1.5 h-1.5 rounded-full"
                    :class="activeTimerTaskId === task.id ? 'bg-emerald-500 animate-pulse' : 'bg-gray-300'"></span>
                  {{ task.time || '00:00:00' }}
                  <button class="ml-1 text-[10px] px-1.5 py-0.5 rounded border transition"
                    :class="activeTimerTaskId === task.id ? 'border-red-200 text-red-500 bg-red-50 hover:bg-red-100' : 'border-gray-200 text-gray-400 hover:bg-gray-100'"
                    @click.stop="handleTimerToggle(task)">
                    {{ activeTimerTaskId === task.id ? '⏹' : '▶' }}
                  </button>
                </div>
                <div class="flex">
                  <div v-for="(m, mi) in resolveMembers(task.assignee_ids).slice(0, 3)" :key="mi"
                    class="w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold text-white border-2 border-white"
                    :class="m.color" :style="(mi as number) > 0 ? 'margin-left: -6px' : ''"
                    :title="m.name">{{ m.initial }}</div>
                </div>
              </div>
            </div>
          </VueDraggable>
        </div>

        <!-- Add Card button -->
        <div class="mx-2.5 mb-2.5 mt-1">
          <div v-if="addingTaskColumnId === board.id">
            <input v-model="newTaskTitle" @keyup.enter="handleCreateTask(board.id)"
              @keyup.esc="addingTaskColumnId = null; newTaskTitle = ''" placeholder="Task title..." autofocus
              class="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 outline-none focus:border-blue-400 transition mb-2 bg-white" />
            <div class="flex gap-2">
              <button @click="handleCreateTask(board.id)" :disabled="taskCreating || !newTaskTitle.trim()"
                class="flex-1 bg-blue-500 text-white text-xs py-1.5 rounded-lg hover:bg-blue-600 disabled:opacity-50 transition">
                {{ taskCreating ? 'Adding...' : 'Add' }}
              </button>
              <button @click="addingTaskColumnId = null; newTaskTitle = ''"
                class="text-xs text-gray-400 px-2 hover:text-gray-600">✕</button>
            </div>
          </div>
          <button v-else @click="addingTaskColumnId = board.id"
            class="w-full text-left text-xs text-gray-400 border border-dashed border-gray-200 rounded-lg py-2 px-3 hover:bg-white hover:text-gray-600 hover:border-gray-300 transition">
            + Add card
          </button>
        </div>

        </div> <!-- tutup v-for -->
      </VueDraggable>

      <!-- Add Column -->
      <div class="min-w-[240px] flex-shrink-0 pt-0.5">
        <div v-if="!showNewBoard">
          <button @click="showNewBoard = true"
            class="w-full text-sm text-gray-400 border border-dashed border-gray-300 rounded-xl py-3 hover:border-blue-400 hover:text-blue-500 transition">
            + Add column
          </button>
        </div>
        <div v-else class="bg-gray-50 rounded-xl border border-gray-200 p-3">
          <input v-model="newBoardTitle" @keyup.enter="handleCreateBoard"
            @keyup.esc="showNewBoard = false; newBoardTitle = ''" placeholder="Column title..." autofocus
            class="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 outline-none focus:border-blue-400 transition mb-2 bg-white" />
          <div class="flex gap-2">
            <button @click="handleCreateBoard" :disabled="boardCreating || !newBoardTitle.trim()"
              class="flex-1 bg-blue-500 text-white text-xs py-1.5 rounded-lg hover:bg-blue-600 disabled:opacity-50 transition">
              {{ boardCreating ? 'Creating...' : 'Add column' }}
            </button>
            <button @click="showNewBoard = false; newBoardTitle = ''"
              class="text-xs text-gray-400 px-2 hover:text-gray-600">✕</button>
          </div>
        </div>
      </div>

    </div>
  </Layout>

  <!-- Modal — DI LUAR Layout -->
  <Teleport to="body">
    <div v-if="selectedTask" class="fixed inset-0 z-50 flex items-center justify-center"
      style="background: rgba(0,0,0,0.65)" @click.self="closeModal">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-4xl mx-4 flex flex-col overflow-hidden"
        style="max-height: 90vh" @click="closeAllDropdowns">

        <!-- Top Bar -->
        <div class="flex items-center justify-between px-5 py-3 border-b border-gray-100 flex-shrink-0">
          <div class="flex items-center gap-2">
            <div class="relative">
              <button @click.stop="closeAllDropdowns(); statusOpen = !statusOpen"
                class="flex items-center gap-1.5 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 px-3 py-1.5 rounded-lg transition">
                {{ selectedTask.status }}
                <svg class="w-3 h-3" viewBox="0 0 10 6" fill="currentColor">
                  <path d="M0 0l5 6 5-6z" />
                </svg>
              </button>
              <div v-if="statusOpen"
                class="absolute left-0 top-10 bg-white border border-gray-200 rounded-xl shadow-xl z-20 py-1 min-w-[140px]">
                <button v-for="s in statuses" :key="s" @click.stop="selectedTask.status = s; statusOpen = false"
                  class="w-full text-left px-4 py-2 text-sm hover:bg-gray-50 transition"
                  :class="selectedTask.status === s ? 'text-blue-600 font-semibold' : 'text-gray-700'">{{ s }}</button>
              </div>
            </div>
            <button @click="handleSaveTask"
              class="text-xs bg-blue-500 text-white px-3 py-1.5 rounded-lg hover:bg-blue-600 transition">Save</button>
            <div class="relative">
              <button @click.stop="closeAllDropdowns(); moveOpen = !moveOpen"
                class="text-xs border border-gray-300 px-3 py-1.5 rounded-lg hover:bg-gray-50 transition text-gray-600">
                Move to...
              </button>
              <div v-if="moveOpen"
                class="absolute left-0 top-9 bg-white border border-gray-200 rounded-xl shadow-xl z-20 w-48 py-1">
                <button v-for="col in allColumns" :key="col.id" @click.stop="handleMoveTask(col.id); moveOpen = false"
                  class="w-full text-left px-4 py-2 text-sm hover:bg-gray-50 transition"
                  :class="col.id === selectedTask?.column_id ? 'text-blue-600 font-semibold' : 'text-gray-700'">
                  {{ col.title }}
                </button>
              </div>
            </div>
            <button @click="handleDeleteTask"
              class="text-xs border border-red-200 text-red-500 px-3 py-1.5 rounded-lg hover:bg-red-50 transition">Delete</button>
          </div>
          <div class="flex items-center gap-1">
            <button
              class="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-gray-100 text-gray-500 transition">
              <font-awesome-icon icon="image" />
            </button>
            <button class="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-gray-100 transition"
              :class="selectedTask._watching ? 'text-blue-500' : 'text-gray-500'" @click.stop="toggleWatch">
              <font-awesome-icon icon="eye" />
            </button>
            <div class="relative">
              <button @click.stop="closeAllDropdowns(); ellipsisOpen = !ellipsisOpen"
                class="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-gray-100 text-gray-500 transition">
                <font-awesome-icon icon="ellipsis-h" />
              </button>
              <div v-if="ellipsisOpen"
                class="absolute right-0 top-10 bg-white border border-gray-200 rounded-xl shadow-xl z-20 w-52 py-1.5 overflow-hidden">
                <template v-for="item in ellipsisMenuItems" :key="item.action">
                  <div v-if="item.action === 'share'" class="border-t border-gray-100 my-1"></div>
                  <button @click.stop="handleEllipsisAction(item.action)"
                    class="w-full flex items-center gap-3 px-4 py-2 text-sm transition"
                    :class="item.danger ? 'text-red-500 hover:bg-red-50' : 'text-gray-700 hover:bg-gray-50'">
                    {{ item.label }}
                  </button>
                </template>
              </div>
            </div>
            <button @click.stop="closeModal"
              class="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-gray-100 text-gray-400 transition ml-1">
              <font-awesome-icon icon="times" />
            </button>
          </div>
        </div>

        <!-- Body -->
        <div class="flex flex-1 overflow-hidden">
          <!-- LEFT -->
          <div class="flex-1 overflow-y-auto px-6 py-5">
            <div class="flex items-start gap-3 mb-5">
              <h2 contenteditable="true"
                @blur="(e: FocusEvent) => { if (selectedTask && e.target) selectedTask.title = (e.target as HTMLElement).innerText }"
                class="text-xl font-bold text-gray-900 outline-none border-b-2 border-transparent focus:border-blue-400 flex-1 leading-tight">
                {{ selectedTask.title }}</h2>
            </div>

            <div class="flex flex-wrap gap-2 mb-6">
              <div class="relative">
                <button @click.stop="closeAllDropdowns(); addMenuOpen = !addMenuOpen"
                  class="flex items-center gap-1.5 text-xs border border-gray-300 rounded-lg px-3 py-1.5 hover:bg-gray-50 text-gray-600 transition font-medium">
                  <font-awesome-icon icon="plus" /> Add
                </button>
                <div v-if="addMenuOpen"
                  class="absolute left-0 top-9 bg-white border border-gray-200 rounded-xl shadow-xl z-20 w-64 overflow-hidden">
                  <div class="flex items-center justify-between px-4 py-2.5 border-b border-gray-100">
                    <span class="text-xs font-semibold text-gray-500">Add to card</span>
                    <button @click.stop="addMenuOpen = false" class="text-gray-400 hover:text-gray-600">✕</button>
                  </div>
                  <div class="py-1">
                    <button v-for="item in addMenuItems" :key="item.action" @click.stop="handleAddAction(item.action)"
                      class="w-full flex items-center gap-3 px-4 py-2.5 hover:bg-gray-50 transition text-left">
                      <div
                        class="w-8 h-8 rounded-lg bg-gray-100 flex items-center justify-center flex-shrink-0 text-gray-600 text-xs">
                        +</div>
                      <div>
                        <p class="text-sm font-medium text-gray-800">{{ item.label }}</p>
                        <p class="text-xs text-gray-400 mt-0.5">{{ item.desc }}</p>
                      </div>
                    </button>
                  </div>
                </div>
              </div>
              <button @click.stop="closeAllDropdowns(); addingSubtask = !addingSubtask"
                class="flex items-center gap-1.5 text-xs border border-gray-300 rounded-lg px-3 py-1.5 hover:bg-gray-50 text-gray-600 transition">
                <font-awesome-icon icon="check-square" /> Subtask
              </button>
              <button @click.stop="showAttachPanel = !showAttachPanel"
                class="flex items-center gap-1.5 text-xs border border-gray-300 rounded-lg px-3 py-1.5 hover:bg-gray-50 text-gray-600 transition"
                :class="showAttachPanel ? 'bg-gray-100 border-gray-400' : ''">
                <font-awesome-icon icon="paperclip" /> Attachment
              </button>
            </div>

            <div class="mb-6">
              <p class="text-xs text-gray-500 font-medium mb-2">Due date</p>
              <button
                class="flex items-center gap-2 text-sm text-gray-700 bg-gray-100 hover:bg-gray-200 px-3 py-1.5 rounded-lg transition">
                {{ selectedTask.dueDate }}
                <svg class="w-3 h-3" viewBox="0 0 10 6" fill="currentColor">
                  <path d="M0 0l5 6 5-6z" />
                </svg>
              </button>
            </div>

            <div class="mb-6">
              <div class="flex items-center gap-2 mb-2">
                <font-awesome-icon icon="align-left" class="text-gray-500 text-sm" />
                <p class="text-sm font-semibold text-gray-700">Description</p>
              </div>
              <textarea v-model="selectedTask.description" placeholder="Add a more detailed description..." rows="3"
                class="w-full text-sm text-gray-600 border border-gray-200 rounded-lg px-3 py-2.5 outline-none focus:border-blue-400 resize-none transition placeholder-gray-400"></textarea>
            </div>

            <div class="mb-6 p-3 bg-gray-50 border border-gray-200 rounded-xl">
              <div class="flex items-center justify-between gap-3">
                <div class="flex items-center gap-2 flex-shrink-0">
                  <font-awesome-icon icon="clock" class="text-gray-500 text-sm" />
                  <p class="text-sm font-semibold text-gray-700">Time Tracker</p>
                </div>
                <input v-if="activeTimerTaskId !== selectedTask.id" v-model="timerDescription" type="text"
                  placeholder="Sedang mengerjakan apa? (opsional)"
                  class="flex-1 min-w-0 text-xs text-gray-600 border border-gray-200 rounded-lg px-2.5 py-1.5 outline-none focus:border-blue-400 transition placeholder-gray-400" />
                <div class="flex items-center gap-2 flex-shrink-0">
                  <span class="text-sm font-mono font-semibold"
                    :class="activeTimerTaskId === selectedTask.id ? 'text-green-600' : 'text-gray-500'">
                    {{ activeTimerTaskId === selectedTask.id ? formatTimer(timerSeconds[selectedTask.id] || 0) :
                      (selectedTask.time || '00:00:00') }}
                  </span>
                  <button @click.stop="handleTimerToggle(selectedTask)"
                    class="flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-lg transition"
                    :class="activeTimerTaskId === selectedTask.id ? 'bg-red-100 text-red-600 hover:bg-red-200 border border-red-200' : 'bg-green-100 text-green-700 hover:bg-green-200 border border-green-200'">
                    <font-awesome-icon :icon="activeTimerTaskId === selectedTask.id ? 'stop' : 'play'" />
                    {{ activeTimerTaskId === selectedTask.id ? 'Stop' : 'Start' }}
                  </button>
                  <button v-if="activeTimerTaskId === selectedTask.id" @click.stop="handleConfirmTimer(selectedTask.id)"
                    class="text-xs text-blue-600 border border-blue-200 bg-blue-50 hover:bg-blue-100 px-3 py-1.5 rounded-lg transition">
                    Confirm
                  </button>
                </div>
              </div>

              <!-- Riwayat time log: "13:00 → 16:00, 3 jam" -->
              <div class="mt-3 pt-3 border-t border-gray-200">
                <div class="flex items-center justify-between mb-2">
                  <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide">Time Logs</p>
                  <span v-if="timerLogs.length" class="text-xs text-gray-500">
                    Total {{ formatDuration(totalDurationSeconds(timerLogs)) }}
                  </span>
                </div>

                <p v-if="timerLogsLoading" class="text-xs text-gray-400">Memuat…</p>
                <p v-else-if="timerLogsError" class="text-xs text-red-500">{{ timerLogsError }}</p>
                <p v-else-if="!timerLogs.length" class="text-xs text-gray-400">Belum ada time log.</p>

                <ul v-else class="space-y-1.5 max-h-40 overflow-y-auto">
                  <li v-for="log in timerLogs" :key="log.id"
                    class="py-1 border-b border-gray-100 last:border-0">
                    <div class="flex items-baseline justify-between gap-3 text-xs">
                      <span class="text-gray-400 flex-shrink-0 w-20">{{ formatLogDate(log.start_time) }}</span>
                      <span class="text-gray-700 tabular-nums flex-1">{{ formatTimerLog(log) }}</span>
                      <span v-if="formatStopReason(log.stop_reason)"
                        class="flex-shrink-0 text-[10px] font-medium text-amber-600 bg-amber-50 border border-amber-200 rounded-full px-1.5 py-0.5">
                        {{ formatStopReason(log.stop_reason) }}
                      </span>
                    </div>
                    <p v-if="log.activity_description" class="text-xs text-gray-400 mt-0.5 pl-20 truncate">
                      {{ log.activity_description }}
                    </p>
                  </li>
                </ul>
              </div>
            </div>

            <!-- Subtasks -->
            <div class="mb-6">
              <div class="flex items-center justify-between mb-3">
                <div class="flex items-center gap-2">
                  <font-awesome-icon icon="check-square" class="text-gray-500 text-sm" />
                  <p class="text-sm font-semibold text-gray-700">Subtasks</p>
                  <span class="text-xs text-gray-400 bg-gray-100 rounded-full px-2 py-0.5">
                    {{selectedTask.subtasks?.filter(s => s.completed).length ?? 0}}/{{ selectedTask.subtasks?.length
                      ?? 0 }}
                  </span>
                </div>
                <button @click="addingSubtask = !addingSubtask"
                  class="text-xs text-blue-500 hover:text-blue-600 transition">
                  + Add
                </button>
              </div>

              <!-- Progress bar -->
              <div v-if="selectedTask.subtasks?.length" class="mb-3">
                <div class="flex-1 bg-gray-200 rounded-full h-1.5">
                  <div class="bg-blue-500 h-1.5 rounded-full transition-all"
                    :style="{ width: ((selectedTask.subtasks.filter(s => s.completed).length / selectedTask.subtasks.length) * 100) + '%' }">
                  </div>
                </div>
              </div>

              <!-- Subtask list -->
              <div class="space-y-1.5">
                <div v-for="sub in (selectedTask.subtasks ?? [])" :key="sub.id"
                  class="flex items-center gap-2 group px-2 py-1.5 rounded-lg hover:bg-gray-50 transition">
                  <input type="checkbox" :checked="sub.completed" @change="handleToggleSubtask(sub.id, !sub.completed)"
                    class="w-4 h-4 rounded accent-blue-600 cursor-pointer flex-shrink-0" />
                  <span contenteditable="true"
                    @blur="(e: FocusEvent) => handleRenameSubtask(sub.id, sub.title, (e.target as HTMLElement).innerText)"
                    class="text-sm flex-1 outline-none border-b border-transparent focus:border-blue-400 transition"
                    :class="sub.completed ? 'line-through text-gray-400' : 'text-gray-700'">
                    {{ sub.title }}
                  </span>
                  <button @click="handleDeleteSubtask(sub.id)"
                    class="opacity-0 group-hover:opacity-100 text-gray-300 hover:text-red-400 transition text-xs px-1">✕</button>
                </div>
              </div>

              <!-- Add subtask input -->
              <div v-if="addingSubtask" class="mt-2 flex gap-2">
                <input v-model="newSubtaskTitle" @keyup.enter="handleAddSubtask"
                  @keyup.esc="addingSubtask = false; newSubtaskTitle = ''" placeholder="Subtask title..." autofocus
                  class="flex-1 text-sm border border-gray-200 rounded-lg px-3 py-1.5 outline-none focus:border-blue-400 transition" />
                <button @click="handleAddSubtask" :disabled="subtaskCreating || !newSubtaskTitle.trim()"
                  class="bg-blue-500 text-white text-xs px-3 py-1.5 rounded-lg hover:bg-blue-600 disabled:opacity-50 transition">
                  {{ subtaskCreating ? '...' : 'Add' }}
                </button>
                <button @click="addingSubtask = false; newSubtaskTitle = ''"
                  class="text-xs text-gray-400 px-2 hover:text-gray-600">✕</button>
              </div>
            </div>

            <!-- Attachments -->
            <div v-if="(selectedTask.attachments?.length ?? 0) > 0" class="mb-6">
              <div class="flex items-center gap-2 mb-2">
                <font-awesome-icon icon="paperclip" class="text-gray-400 text-xs" />
                <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide">Attachments</p>
              </div>
              <div class="space-y-2">
                <div v-for="(att, i) in selectedTask.attachments" :key="i"
                  class="flex items-center justify-between gap-2 bg-gray-50 border border-gray-100 rounded-lg px-3 py-2 group hover:border-gray-300 transition">
                  <div class="flex items-center gap-3 min-w-0">
                    <img v-if="att.url && att.type === 'image'" :src="att.url"
                      class="w-12 h-12 rounded object-cover flex-shrink-0 border border-gray-200" />
                    <div v-else
                      class="w-12 h-12 rounded bg-gray-100 border border-gray-200 flex items-center justify-center flex-shrink-0">
                      <font-awesome-icon icon="paperclip" class="text-gray-400" />
                    </div>
                    <div class="min-w-0">
                      <a v-if="att.url" :href="att.url" target="_blank"
                        class="text-xs font-medium text-blue-600 hover:underline block truncate max-w-[200px]">{{
                          att.title ??
                          att.url }}</a>
                      <p v-else class="text-xs font-medium text-gray-700 truncate">{{ att.title ?? '-' }}</p>
                      <p class="text-xs text-gray-400 mt-0.5">{{ att.type === 'image' ? 'Image' : att.type === 'link' ?
                        'Link' :
                        'File' }}</p>
                    </div>
                  </div>
                  <button @click="handleDeleteAttachment(att.id, i)"
                    class="opacity-0 group-hover:opacity-100 text-gray-300 hover:text-red-400 transition text-xs flex-shrink-0 px-1"
                    title="Delete">✕</button>
                </div>
              </div>
            </div>

            <!-- Members -->
            <div class="mb-6">
              <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Members</p>
              <div class="flex items-center gap-2 flex-wrap">
                <div v-for="m in assignedMembers" :key="m.id" class="relative group/member">
                  <div class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-white"
                    :class="m.color" :title="m.name">{{ m.initial }}</div>
                  <button @click.stop="handleToggleMember(m.id)"
                    class="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-white border border-gray-300 text-gray-400 hover:text-red-500 hover:border-red-300 opacity-0 group-hover/member:opacity-100 transition text-[9px] flex items-center justify-center leading-none"
                    title="Remove">✕</button>
                </div>
                <div class="relative">
                  <button @click.stop="closeAllDropdowns(); memberMenuOpen = !memberMenuOpen"
                    class="w-8 h-8 rounded-full border-2 border-dashed border-gray-300 flex items-center justify-center text-gray-400 hover:border-blue-400 text-sm">+</button>
                  <div v-if="memberMenuOpen"
                    class="absolute left-0 top-9 bg-white border border-gray-200 rounded-xl shadow-xl z-20 w-56 py-1 max-h-64 overflow-y-auto">
                    <button v-for="u in users" :key="u.id" @click.stop="handleToggleMember(u.id)"
                      class="w-full flex items-center gap-2.5 px-3 py-2 text-sm hover:bg-gray-50 transition text-left">
                      <div class="w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold text-white flex-shrink-0"
                        :class="memberColor(u.id)">{{ (u.full_name || u.email || '?').charAt(0).toUpperCase() }}</div>
                      <span class="flex-1 truncate text-gray-700">{{ u.full_name || u.email }}</span>
                      <font-awesome-icon v-if="(selectedTask?.assignee_ids ?? []).includes(u.id)" icon="check"
                        class="text-blue-500 text-xs" />
                    </button>
                    <p v-if="!users.length" class="px-3 py-2 text-xs text-gray-400">Tidak ada user.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- RIGHT: Comments -->
          <div class="w-72 border-l border-gray-100 flex flex-col flex-shrink-0">
            <div class="flex items-center justify-between px-4 py-3 border-b border-gray-100">
              <div class="flex items-center gap-2 text-sm font-semibold text-gray-700">
                <font-awesome-icon icon="comment-alt" class="text-gray-400" />
                Comments and activity
              </div>
              <button @click="showActivity = !showActivity"
                class="text-xs text-gray-500 border border-gray-200 rounded-lg px-2 py-1 hover:bg-gray-50 transition">
                {{ showActivity ? 'Hide' : 'Show' }}
              </button>
            </div>
            <div class="px-4 py-3 border-b border-gray-100">
              <input v-model="newComment" @keyup.enter="handleAddComment" :disabled="commentLoading"
                placeholder="Write a comment..."
                class="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 outline-none focus:border-blue-400 transition placeholder-gray-400 disabled:opacity-50" />
              <button @click="handleAddComment" :disabled="commentLoading || !newComment.trim()"
                class="mt-2 w-full bg-blue-500 hover:bg-blue-600 disabled:opacity-40 disabled:cursor-not-allowed text-white text-xs font-medium py-1.5 rounded-lg transition">
                {{ commentLoading ? 'Sending...' : 'Send' }}
              </button>
            </div>
            <div class="flex-1 overflow-y-auto px-4 py-3 space-y-4">
              <div v-for="(act, i) in selectedTask.activity" :key="i" class="flex gap-2.5 group">
                <div
                  class="w-7 h-7 rounded-full flex-shrink-0 flex items-center justify-center text-xs font-bold text-white mt-0.5"
                  :class="act.color || 'bg-blue-500'">{{ act.initial }}</div>
                <div class="flex-1 min-w-0">
                  <div class="flex items-baseline gap-1 flex-wrap justify-between">
                    <div class="flex items-baseline gap-1">
                      <span class="text-xs font-semibold text-gray-800">{{ act.author }}</span>
                      <span class="text-xs text-gray-500">{{ act.action }}</span>
                    </div>
                    <button v-if="act.comment && act.id" @click="handleDeleteComment(act.id, i)"
                      class="opacity-0 group-hover:opacity-100 text-gray-300 hover:text-red-400 transition text-xs"
                      title="Delete">✕</button>
                  </div>
                  <p class="text-xs text-blue-500 mt-0.5">{{ act.date }}</p>
                  <div v-if="act.comment" class="mt-1.5 bg-gray-50 border border-gray-200 rounded-lg px-3 py-2">
                    <p class="text-xs font-medium text-blue-600">{{ act.comment.title }}</p>
                    <p class="text-xs text-gray-600 mt-0.5">{{ act.comment.body }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Attachment Panel -->
        <div v-if="showAttachPanel" class="border-t border-gray-100 px-6 py-4 bg-gray-50 flex-shrink-0">
          <div class="flex items-center justify-between mb-3">
            <p class="text-sm font-semibold text-gray-700">Add Attachment</p>
            <button @click="showAttachPanel = false; showAttachLink = false"
              class="text-gray-400 hover:text-gray-600 text-xs">✕
              Close</button>
          </div>
          <div class="flex gap-2 flex-wrap">
            <label
              class="cursor-pointer flex items-center gap-2 border border-gray-300 rounded-lg px-3 py-2 text-xs text-gray-600 hover:bg-white transition">
              <font-awesome-icon icon="paperclip" />
              {{ attachFileLoading ? 'Uploading...' : 'Upload File' }}
              <input type="file" class="hidden" @change="handleUploadFile" :disabled="attachFileLoading" />
            </label>
            <button @click="showAttachLink = !showAttachLink"
              class="flex items-center gap-2 border border-gray-300 rounded-lg px-3 py-2 text-xs text-gray-600 hover:bg-white transition">
              🔗 Add Link
            </button>
          </div>
          <div v-if="showAttachLink" class="mt-3 flex flex-col gap-2">
            <input v-model="attachLinkTitle" placeholder="Title"
              class="text-sm border border-gray-200 rounded-lg px-3 py-1.5 outline-none focus:border-blue-400 transition" />
            <input v-model="attachLinkUrl" placeholder="https://..."
              class="text-sm border border-gray-200 rounded-lg px-3 py-1.5 outline-none focus:border-blue-400 transition" />
            <button @click="handleAddLink"
              :disabled="attachLinkLoading || !attachLinkTitle.trim() || !attachLinkUrl.trim()"
              class="bg-blue-500 text-white text-xs py-1.5 rounded-lg hover:bg-blue-600 disabled:opacity-40 transition">
              {{ attachLinkLoading ? 'Adding...' : 'Add Link' }}
            </button>
          </div>
        </div>

      </div>
    </div>
  </Teleport>

  <!-- Toast -->
  <Teleport to="body">
    <Transition name="toast">
      <div v-if="toast"
        class="fixed bottom-6 left-1/2 -translate-x-1/2 z-[60] bg-gray-900 text-white text-sm px-5 py-2.5 rounded-xl shadow-lg pointer-events-none">
        {{ toast }}
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { VueDraggable } from 'vue-draggable-plus'
import { moveTask as apiMoveTask } from '../api/task.api'
import { reorderColumn as apiReorderColumn } from '../api/column.api'
import { useRoute, useRouter } from 'vue-router'
import { ref, computed, onMounted, onUnmounted } from 'vue'
import Layout from '../../../components/common/AppLayout.vue'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { library } from '@fortawesome/fontawesome-svg-core'
import {
  faClock, faPlay, faStop, faPlus, faTag, faCheckSquare, faPaperclip,
  faAlignLeft, faEye, faImage, faEllipsisH, faTimes, faCommentAlt, faCheck,
} from '@fortawesome/free-solid-svg-icons'
import {
  addComment as apiAddComment,
  deleteComment as apiDeleteComment,
  uploadAttachmentFile as apiUploadFile,
  addAttachmentLink as apiAddLink,
  deleteAttachment as apiDeleteAttachment,
} from '../api/board.api'
import {
  startTimer as apiStartTimer,
  stopTimer as apiStopTimer,
  pingTimer as apiPingTimer,
  confirmTimer as apiConfirmTimer,
  getTimerLogs as apiGetTimerLogs,
} from '../../timer/api/timer.api'
import {
  formatTimer,
  formatDuration,
  formatLogDate,
  formatTimerLog,
  formatStopReason,
  totalDurationSeconds,
} from '../../timer/utils/timer.format'
import type { TimerLog } from '../../timer/utils/timer.format'
import { useAppStore } from '../store/board.store'
import { storeToRefs } from 'pinia'

// ─── Types ────────────────────────────────────────────────────
interface ActivityItem {
  author: string
  initial: string
  color: string
  action: string
  date: string
  comment?: { title: string; body: string }
  id?: string
}

interface Subtask {
  id: string
  title: string
  completed: boolean
}
interface Task {
  id: string
  column_id: string
  title: string
  description?: string
  status?: string
  subtasks?: Subtask[]
  assignee_ids?: string[]
  activity: ActivityItem[]
  attachments?: { id: string | null; title: string; type: string; url: string | null }[]
  time?: string
  dueDate?: string
  label?: string
  labelClass?: string
  _watching?: boolean
}

library.add(faClock, faPlay, faStop, faPlus, faTag, faCheckSquare, faPaperclip, faAlignLeft, faEye, faImage, faEllipsisH, faTimes, faCommentAlt, faCheck)

const route = useRoute()
const router = useRouter()
const boardId = route.params.boardId as string
const store = useAppStore()
const { columnsByBoard, users } = storeToRefs(store)
const boards = computed(() => columnsByBoard.value[boardId] ?? [])
const moveOpen = ref(false)

// ─── Task State ───────────────────────────────────────────────
const newTaskTitle = ref('')
const addingTaskColumnId = ref<string | null>(null)
const taskCreating = ref(false)

// ─── UI State ─────────────────────────────────────────────────
const selectedTask = ref<Task | null>(null)
const statusOpen = ref(false)
const ellipsisOpen = ref(false)
const addMenuOpen = ref(false)
const memberMenuOpen = ref(false)
const newComment = ref('')
const commentLoading = ref(false)
const showAttachPanel = ref(false)
const showAttachLink = ref(false)
const attachLinkTitle = ref('')
const attachLinkUrl = ref('')
const attachLinkLoading = ref(false)
const attachFileLoading = ref(false)
const showActivity = ref(true)
const toast = ref('')
const showNewBoard = ref(false)
const newBoardTitle = ref('')
const boardCreating = ref(false)

//subtask state
const newSubtaskTitle = ref('')
const addingSubtask = ref(false)
const subtaskCreating = ref(false)

// ─── Timer State ──────────────────────────────────────────────
const activeTimerTaskId = ref<string | null>(null)
const timerSeconds = ref<Record<string, number>>({})
const timerLogs = ref<TimerLog[]>([])
const timerLogsLoading = ref(false)
const timerLogsError = ref('')
const timerDescription = ref('')
let tickInterval: ReturnType<typeof setInterval> | null = null
let pingInterval: ReturnType<typeof setInterval> | null = null
let toastTimer: ReturnType<typeof setTimeout> | null = null
let originalTaskSnapshot: { title: string; description: string } | null = null

// ─── Helpers ──────────────────────────────────────────────────
const memberPalette = ['bg-blue-500', 'bg-emerald-500', 'bg-amber-500', 'bg-pink-500', 'bg-purple-500', 'bg-cyan-600', 'bg-rose-500', 'bg-indigo-500']

function memberColor(id: string): string {
  let hash = 0
  for (let i = 0; i < id.length; i++) hash = (hash * 31 + id.charCodeAt(i)) >>> 0
  return memberPalette[hash % memberPalette.length]
}

function resolveMembers(ids?: string[]) {
  if (!ids?.length) return []
  return ids
    .map(id => users.value.find((u: any) => u.id === id))
    .filter((u: any): u is any => !!u)
    .map((u: any) => ({
      id: u.id as string,
      name: (u.full_name ?? u.email ?? 'Unknown') as string,
      initial: ((u.full_name ?? u.email ?? '?') as string).charAt(0).toUpperCase(),
      color: memberColor(u.id),
    }))
}

const assignedMembers = computed(() => resolveMembers(selectedTask.value?.assignee_ids))
function findTaskById(id: string): Task | null {
  for (const board of boards.value) {
    const t = (board.tasks ?? []).find((t: Task) => t.id === id)
    if (t) return t
  }
  return null
}

function showToast(msg: string) {
  toast.value = msg
  if (toastTimer) clearTimeout(toastTimer)
  toastTimer = setTimeout(() => { toast.value = '' }, 2500)
}

// ─── Timer ────────────────────────────────────────────────────
function startTick(taskId: string) {
  if (tickInterval) clearInterval(tickInterval)
  tickInterval = setInterval(() => {
    timerSeconds.value[taskId] = (timerSeconds.value[taskId] || 0) + 1
    const task = findTaskById(taskId)
    if (task) task.time = formatTimer(timerSeconds.value[taskId])
  }, 1000)
}

function stopTick() {
  if (tickInterval) { clearInterval(tickInterval); tickInterval = null }
}

function startPing(taskId: string) {
  if (pingInterval) clearInterval(pingInterval)
  pingInterval = setInterval(async () => {
    try { await apiPingTimer(taskId) } catch { }
  }, 120000)
}

function stopPing() {
  if (pingInterval) { clearInterval(pingInterval); pingInterval = null }
}
async function onTaskDragEnd(event: any) {
  const taskId = event.item?.dataset?.id
  const toColumnId = event.to?.dataset?.columnId
  const fromColumnId = event.from?.dataset?.columnId
  const newIndex = event.newIndex ?? 0

  console.log('drag end:', { taskId, fromColumnId, toColumnId, newIndex })

  if (!taskId || !toColumnId || fromColumnId === toColumnId) return

  try {
    await apiMoveTask(taskId, toColumnId, newIndex + 1)
    showToast('Task moved!')
  } catch (e: any) {
    showToast(e?.response?.data?.error?.message || 'Gagal memindahkan task.')
    // JANGAN fetch ulang — biarkan vue-draggable handle UI
  }
}

async function onColumnDragEnd(event: any) {
  const columnId = columnsByBoard.value[boardId]?.[event.newIndex]?.id
  if (!columnId) return

  try {
    await apiReorderColumn(columnId, event.newIndex + 1)
  } catch (e: any) {
    showToast(e?.response?.data?.error?.message || 'Gagal mengubah urutan column.')
    // JANGAN fetch ulang — biarkan vue-draggable handle UI
  }
}

async function handleAddSubtask() {
  if (!newSubtaskTitle.value.trim() || !selectedTask.value) return
  const title = newSubtaskTitle.value.trim()
  subtaskCreating.value = true
  try {
    await store.addSubtask(selectedTask.value.id, title)
    newSubtaskTitle.value = ''
    addingSubtask.value = false
    logActivity(`menambahkan checklist "${title}"`)
    showToast('Subtask added.')
  } catch (e: any) {
    showToast(e?.response?.data?.error?.message || 'Gagal menambah subtask.')
  } finally {
    subtaskCreating.value = false
  }
}

async function handleToggleSubtask(subtaskId: string, completed: boolean) {
  if (!selectedTask.value) return
  const sub = selectedTask.value.subtasks?.find(s => s.id === subtaskId)
  try {
    await store.toggleSubtask(subtaskId, selectedTask.value.id, completed)
    if (sub) {
      logActivity(completed
        ? `menyelesaikan checklist "${sub.title}"`
        : `membuka kembali checklist "${sub.title}"`)
    }
  } catch (e: any) {
    showToast(e?.response?.data?.error?.message || 'Gagal update subtask.')
  }
}

async function handleRenameSubtask(subtaskId: string, oldTitle: string, newTitle: string) {
  if (!selectedTask.value) return
  const trimmed = newTitle.trim()
  if (!trimmed || trimmed === oldTitle) {
    const sub = selectedTask.value.subtasks?.find(s => s.id === subtaskId)
    if (sub) sub.title = oldTitle
    return
  }
  try {
    await store.renameSubtask(subtaskId, selectedTask.value.id, trimmed)
  } catch (e: any) {
    const sub = selectedTask.value.subtasks?.find(s => s.id === subtaskId)
    if (sub) sub.title = oldTitle
    showToast(e?.response?.data?.error?.message || 'Gagal mengubah nama subtask.')
  }
}

async function handleDeleteSubtask(subtaskId: string) {
  if (!selectedTask.value) return
  try {
    await store.removeSubtask(subtaskId, selectedTask.value.id)
    showToast('Subtask deleted.')
  } catch (e: any) {
    showToast(e?.response?.data?.error?.message || 'Gagal menghapus subtask.')
  }
}

async function handleTimerToggle(task: Task) {
  if (!task.id) { showToast('Task ID belum tersedia.'); return }
  if (activeTimerTaskId.value && activeTimerTaskId.value !== task.id) {
    await doStopTimer(activeTimerTaskId.value)
  }
  if (activeTimerTaskId.value === task.id) {
    await doStopTimer(task.id)
  } else {
    try {
      await apiStartTimer(task.id, timerDescription.value)
      activeTimerTaskId.value = task.id
      if (!timerSeconds.value[task.id]) timerSeconds.value[task.id] = 0
      localStorage.setItem('active_timer_task_id', task.id)
      localStorage.setItem('active_timer_task_title', task.title ?? '')
      timerDescription.value = ''
      startTick(task.id)
      startPing(task.id)
      showToast('Timer started ▶')
    } catch (e: any) {
      showToast(e?.response?.data?.error?.message || 'Gagal memulai timer.')
    }
  }
}

async function doStopTimer(taskId: string) {
  try {
    await apiStopTimer(taskId)
    stopTick()
    stopPing()
    const elapsed = timerSeconds.value[taskId] || 0
    activeTimerTaskId.value = null
    localStorage.removeItem('active_timer_task_id')
    localStorage.removeItem('active_timer_task_title')
    showToast(`Timer stopped ⏹ — ${formatTimer(elapsed)}`)

    // Log baru baru tercatat di backend setelah stop — tarik ulang biar langsung tampil.
    if (selectedTask.value?.id === taskId) {
      await loadTimerLogs(taskId)
    }
  } catch (e: any) {
    showToast(e?.response?.data?.error?.message || 'Gagal menghentikan timer.')
  }
}

async function handleConfirmTimer(taskId: string) {
  try {
    await apiConfirmTimer(taskId)
    showToast('Timer confirmed ✓')
  } catch (e: any) {
    showToast(e?.response?.data?.error?.message || 'Gagal konfirmasi timer.')
  }
}

async function loadTimerLogs(taskId: string) {
  if (!taskId) return
  timerLogsLoading.value = true
  timerLogsError.value = ''
  try {
    timerLogs.value = await apiGetTimerLogs(taskId)
  } catch (e: any) {
    timerLogs.value = []
    timerLogsError.value = e?.response?.data?.error?.message || 'Gagal memuat time log.'
  } finally {
    timerLogsLoading.value = false
  }
}

// ─── Task ─────────────────────────────────────────────────────
async function handleCreateTask(columnId: string) {
  if (!newTaskTitle.value.trim() || taskCreating.value) return
  taskCreating.value = true
  try {
    await store.addTask(columnId, newTaskTitle.value.trim())
    newTaskTitle.value = ''
    addingTaskColumnId.value = null
    showToast('Task created!')
  } catch (e: any) {
    showToast(e?.response?.data?.error?.message || 'Gagal membuat task.')
  } finally {
    taskCreating.value = false
  }
}

// ─── Column ───────────────────────────────────────────────────
async function initBoards() {
  if (!boardId) { showToast('Board ID tidak ditemukan.'); return }
  try {
    await store.fetchColumns(boardId)
  } catch (e: any) {
    console.error('fetchColumns error:', e?.response?.status, e?.response?.data)
    showToast('Akses ditolak atau Board tidak ditemukan.')
    router.replace('/boards')
  }
}

async function handleCreateBoard() {
  if (!newBoardTitle.value.trim() || boardCreating.value) return
  boardCreating.value = true
  try {
    const col = await store.addColumn(boardId, newBoardTitle.value.trim())
    newBoardTitle.value = ''
    showNewBoard.value = false
    showToast(`Column "${col.title}" created!`)
  } catch (e: any) {
    showToast(e?.response?.data?.error?.message || 'Gagal membuat column.')
  } finally {
    boardCreating.value = false
  }
}

onMounted(() => { initBoards(); store.fetchUsers() })
onUnmounted(() => { stopTick(); stopPing() })
// ─── Task Actions ─────────────────────────────────────
async function handleDeleteTask() {
  if (!selectedTask.value) return
  const columnId = selectedTask.value.column_id
  try {
    await store.removeTask(selectedTask.value.id, columnId)
    closeModal()
    showToast('Task deleted.')
  } catch (e: any) {
    showToast(e?.response?.data?.error?.message || 'Gagal menghapus task.')
  }
}

async function handleSaveTask() {
  if (!selectedTask.value) return
  const prev = originalTaskSnapshot
  const nextTitle = selectedTask.value.title
  const nextDescription = selectedTask.value.description ?? ''
  try {
    await store.editTask(selectedTask.value.id, {
      title: nextTitle,
      description: nextDescription,
      status: selectedTask.value.status,
    })
    if (prev) {
      if (prev.title !== nextTitle) logActivity(`mengubah judul card menjadi "${nextTitle}"`)
      if (prev.description !== nextDescription) logActivity('mengubah deskripsi card')
    }
    originalTaskSnapshot = { title: nextTitle, description: nextDescription }
    showToast('Task saved.')
  } catch (e: any) {
    showToast(e?.response?.data?.error?.message || 'Gagal menyimpan task.')
  }
}

// columns list untuk move task dropdown
const allColumns = computed(() => {
  return columnsByBoard.value[boardId] ?? []
})

async function handleMoveTask(toColumnId: string) {
  if (!selectedTask.value) return
  const task = selectedTask.value
  const fromColumnId = task.column_id
  if (fromColumnId === toColumnId) return
  const toColumn = allColumns.value.find((c: any) => c.id === toColumnId)
  try {
    await store.moveTaskToColumn(task.id, fromColumnId, toColumnId)
    if (toColumn) logActivityOn(task, `memindahkan card ke "${toColumn.title}"`)
    closeModal()
    showToast('Task moved.')
  } catch (e: any) {
    showToast(e?.response?.data?.error?.message || 'Gagal memindahkan task.')
  }
}

async function handleToggleMember(userId: string) {
  if (!selectedTask.value) return
  const current = selectedTask.value.assignee_ids ?? []
  const isAssigned = current.includes(userId)
  const next = isAssigned ? current.filter(id => id !== userId) : [...current, userId]
  const user = users.value.find((u: any) => u.id === userId)
  try {
    await store.editTask(selectedTask.value.id, { assignee_ids: next })
    selectedTask.value.assignee_ids = next
    if (user) {
      logActivity(isAssigned
        ? `menghapus ${user.full_name} dari card ini`
        : `menambahkan ${user.full_name} ke card ini`)
    }
  } catch (e: any) {
    showToast(e?.response?.data?.error?.message || 'Gagal mengubah member.')
  }
}

// ─── Dropdowns ────────────────────────────────────────────────
function closeAllDropdowns() {
  statusOpen.value = false
  ellipsisOpen.value = false
  addMenuOpen.value = false
  moveOpen.value = false
  memberMenuOpen.value = false
}

const ellipsisMenuItems = [
  { label: 'Leave', action: 'leave', danger: false },
  { label: 'Move', action: 'move', danger: false },
  { label: 'Copy', action: 'copy', danger: false },
  { label: 'Mirror', action: 'mirror', danger: false },
  { label: 'Make template', action: 'template', danger: false },
  { label: 'Watch', action: 'watch', danger: false },
  { label: 'Share', action: 'share', danger: false },
  { label: 'Archive', action: 'archive', danger: true },
]

function handleEllipsisAction(action: string) {
  ellipsisOpen.value = false
  if (action === 'watch') { toggleWatch(); return }
  if (action === 'share') { navigator.clipboard?.writeText(window.location.href).catch(() => { }); showToast('Link copied!'); return }
  if (action === 'archive') { logActivity('archived this card'); showToast('Card archived.'); return }
  if (action === 'leave') { logActivity('left this card'); showToast('You left this card.'); return }
  showToast('Coming soon.')
}

function toggleWatch() {
  if (!selectedTask.value) return
  selectedTask.value._watching = !selectedTask.value._watching
  logActivity(selectedTask.value._watching ? 'is watching this card' : 'stopped watching this card')
  showToast(selectedTask.value._watching ? 'Watching this card.' : 'Stopped watching.')
}

const addMenuItems = [
  { label: 'Labels', action: 'labels', desc: 'Organize, categorize, and prioritize' },
  { label: 'Dates', action: 'dates', desc: 'Start date, due date, reminder' },
  { label: 'Subtask', action: 'checklist', desc: 'Add subtask' },
  { label: 'Members', action: 'members', desc: 'Assign members' },
  { label: 'Attachments', action: 'attachments', desc: 'Add links, pages, work items, etc' },
]

function handleAddAction(action: string) {
  addMenuOpen.value = false
  if (action === 'checklist') { addingSubtask.value = true; return }
  if (action === 'members') { memberMenuOpen.value = true; return }
  showToast(`${action} — coming soon.`)
}

const statuses = ['To Do', 'Doing', 'In Review', 'Done']

// ─── Modal ────────────────────────────────────────────────────
function openModal(task: Task) {
  selectedTask.value = task
  closeAllDropdowns()
  addingSubtask.value = false
  showAttachPanel.value = false
  originalTaskSnapshot = { title: task.title, description: task.description ?? '' }

  timerLogs.value = []
  timerLogsError.value = ''
  timerDescription.value = ''
  loadTimerLogs(task.id)
}

function closeModal() {
  selectedTask.value = null
  originalTaskSnapshot = null
  timerLogs.value = []
  timerLogsError.value = ''
  timerDescription.value = ''
  closeAllDropdowns()
}

// ─── Comments ─────────────────────────────────────────────────
async function handleAddComment() {
  const content = newComment.value.trim()
  if (!content || !selectedTask.value || commentLoading.value) return
  if (!selectedTask.value.id) { showToast('Task ID belum tersedia.'); return }
  commentLoading.value = true
  try {
    await apiAddComment(selectedTask.value.id, content)
    selectedTask.value.activity.unshift({
      author: 'You', initial: 'Y', color: 'bg-blue-500', action: '',
      date: new Date().toLocaleString('id-ID', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' }),
      comment: { title: 'Comment', body: content },
    })
    newComment.value = ''
  } catch (e: any) {
    showToast(e?.response?.data?.error?.message || 'Gagal mengirim komentar.')
  } finally {
    commentLoading.value = false
  }
}

async function handleDeleteComment(commentId: string, index: number) {
  if (!commentId) return
  try {
    await apiDeleteComment(commentId)
    selectedTask.value?.activity.splice(index, 1)
    showToast('Comment deleted.')
  } catch (e: any) {
    showToast(e?.response?.data?.error?.message || 'Gagal menghapus komentar.')
  }
}

// ─── Attachments ──────────────────────────────────────────────
async function handleUploadFile(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file || !selectedTask.value?.id) return
  attachFileLoading.value = true
  try {
    const att = await apiUploadFile(selectedTask.value.id, file)
    if (!selectedTask.value.attachments) selectedTask.value.attachments = []
    selectedTask.value.attachments.push({
      id: att.id ?? null,
      title: att.file_name ?? file.name,
      type: att.type ?? 'image',
      url: att.file_url ?? null,
    })
    logActivity(`attached file "${file.name}"`)
    showToast(`File "${file.name}" uploaded!`)
  } catch (e: any) {
    showToast(e?.response?.data?.error?.message || 'Gagal upload file.')
  } finally {
    attachFileLoading.value = false
    input.value = ''
  }
}

async function handleAddLink() {
  const title = attachLinkTitle.value.trim()
  const url = attachLinkUrl.value.trim()
  if (!title || !url || !selectedTask.value?.id || attachLinkLoading.value) return
  attachLinkLoading.value = true
  try {
    await apiAddLink(selectedTask.value.id, title, url)
    if (!selectedTask.value.attachments) selectedTask.value.attachments = []
    selectedTask.value.attachments.push({ id: null, title, type: 'link', url })
    logActivity(`attached link "${title}"`)
    showToast(`Link "${title}" added!`)
    attachLinkTitle.value = ''
    attachLinkUrl.value = ''
    showAttachLink.value = false
  } catch (e: any) {
    showToast(e?.response?.data?.error?.message || 'Gagal menambah link.')
  } finally {
    attachLinkLoading.value = false
  }
}

async function handleDeleteAttachment(attachId: string | null, index: number) {
  if (!attachId) return
  try {
    const att = selectedTask.value?.attachments?.[index]
    await apiDeleteAttachment(attachId)
    selectedTask.value?.attachments?.splice(index, 1)
    logActivity(`deleted attachment "${att?.title ?? 'file'}"`)
    showToast('Attachment deleted.')
  } catch (e: any) {
    showToast(e?.response?.data?.error?.message || 'Gagal menghapus attachment.')
  }
}

// ─── Activity ─────────────────────────────────────────────────
function logActivity(action: string) {
  if (!selectedTask.value) return
  logActivityOn(selectedTask.value, action)
}

function logActivityOn(task: Task, action: string) {
  task.activity.unshift({
    author: 'You', initial: 'Y', color: 'bg-blue-500', action,
    date: new Date().toLocaleString('id-ID', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' }),
  })
}
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