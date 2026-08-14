<template>
  <Teleport to="body">
    <div v-if="reminderOpen" class="fixed inset-0 z-[80] flex items-center justify-center"
      style="background: rgba(0,0,0,0.65)">
      <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl w-full max-w-sm mx-4 p-6">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-10 h-10 rounded-full bg-amber-100 dark:bg-amber-500/20 flex items-center justify-center flex-shrink-0">
            <font-awesome-icon icon="clock" class="text-amber-500 text-lg" />
          </div>
          <p class="text-sm font-semibold text-gray-800 dark:text-gray-100">Still working?</p>
        </div>

        <p class="text-sm text-gray-600 dark:text-gray-300 leading-relaxed mb-6">
          You have been working for {{ reminderHours }} hours. Are you still working on
          <span class="font-semibold text-gray-800 dark:text-gray-100">"{{ reminderTaskTitle }}"</span>?
        </p>

        <div class="flex gap-2 justify-end">
          <button @click="stopWorking" :disabled="stopping"
            class="text-sm text-red-600 dark:text-red-400 border border-red-200 dark:border-red-500/40 rounded-lg px-4 py-2 hover:bg-red-50 dark:hover:bg-red-500/10 transition disabled:opacity-50">
            {{ stopping ? 'Stopping...' : 'No, stop timer' }}
          </button>
          <button @click="keepWorking"
            class="text-sm text-white bg-blue-500 hover:bg-blue-600 rounded-lg px-4 py-2 transition">
            Yes, keep working
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { library } from '@fortawesome/fontawesome-svg-core'
import { faClock } from '@fortawesome/free-solid-svg-icons'
import { useTimerReminder } from '../composables/useTimerReminder'

library.add(faClock)

const { reminderOpen, reminderTaskTitle, reminderHours, stopping, keepWorking, stopWorking } = useTimerReminder()
</script>
