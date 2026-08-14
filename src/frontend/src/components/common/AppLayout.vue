<template>
  <div class="flex flex-col h-screen bg-gray-100 dark:bg-gray-900">
    <!-- TOP HEADER -->
    <div class="h-14 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between px-6 flex-shrink-0 relative">
      <div class="flex items-center gap-2 text-lg font-semibold">
        <img src="../../assets/Grid.png" alt="logo" class="w-5" />
        <span class="text-gray-800 dark:text-gray-100">Braves</span>
        <span class="text-blue-600">Board</span>
      </div>

      <div class="flex items-center gap-3">
        <button @click="toggleTheme" :title="isDark ? 'Switch to light mode' : 'Switch to dark mode'"
          class="w-8 h-8 flex items-center justify-center rounded-full border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 transition text-gray-600 dark:text-gray-300">
          <font-awesome-icon :icon="isDark ? 'sun' : 'moon'" class="text-sm" />
        </button>
        <button class="w-8 h-8 flex items-center justify-center rounded-full border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 transition text-gray-600 dark:text-gray-300">
          <font-awesome-icon icon="question" class="text-sm" />
        </button>
        <NotificationBell />
        <button class="w-8 h-8 flex items-center justify-center rounded-full border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 transition text-gray-600 dark:text-gray-300">
          <font-awesome-icon icon="user" class="text-sm" />
        </button>
      </div>


    </div>

    <div class="flex flex-1 overflow-hidden">
      <AppSidebar />
      <main class="flex-1 overflow-auto p-6 bg-gray-100 dark:bg-gray-900">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { library } from '@fortawesome/fontawesome-svg-core'
import { faQuestion, faUser, faMoon, faSun } from '@fortawesome/free-solid-svg-icons'
import AppSidebar from './AppSidebar.vue'
import NotificationBell from '../../modules/notification/components/NotificationBell.vue'
import { useTheme } from '../../composables/useTheme'

const { isDark, toggleTheme } = useTheme()

library.add(faQuestion, faUser, faMoon, faSun)
</script>