<template>
  <div class="w-56 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col h-full flex-shrink-0">
    <nav class="flex-1 py-4 px-3 flex flex-col gap-4">
      <!-- MENU -->
      <RouterLink v-for="menu in menus" :key="menu.path" :to="menu.path"
        class="flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors duration-150" :class="isActive(menu.path)
          ? 'bg-blue-600 text-white'
          : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-gray-800 dark:hover:text-white'
          ">
        <font-awesome-icon :icon="menu.icon" class="w-4 h-4"
          :class="isActive(menu.path) ? 'text-white' : 'text-gray-500 dark:text-gray-400'" />
        <span>{{ menu.name }}</span>
      </RouterLink>
    </nav>

    <!-- 🔥 LOGOUT BUTTON -->
    <div class="p-3 border-t dark:border-gray-700">
      <button @click="handleLogout"
        class="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-red-500 hover:bg-red-50 dark:hover:bg-red-500/10 transition">
        <font-awesome-icon icon="right-from-bracket" class="w-4 h-4" />
        Logout
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { library } from '@fortawesome/fontawesome-svg-core'
import {
  faTachometerAlt,
  faClipboardList,
  faClock,
  faChartBar,
  faProjectDiagram,
  faUsers,
  faRightFromBracket
} from '@fortawesome/free-solid-svg-icons'
import type { MenuItem } from '../../app/types/app.type'
import api from '../../app/api'

const router = useRouter()
const route = useRoute()

// Cocokkan juga sub-path (mis. /boards/:boardId) supaya menu "Boards" tetap
// aktif saat masuk ke board tertentu / buka detail card — sebelumnya cuma
// exact-match ke /boards jadi status aktif hilang begitu pindah ke board.
function isActive(path: string): boolean {
  return route.path === path || route.path.startsWith(`${path}/`)
}

library.add(
  faTachometerAlt,
  faClipboardList,
  faClock,
  faChartBar,
  faProjectDiagram,
  faUsers,
  faRightFromBracket
)

const menus: MenuItem[] = [
  { name: 'Dashboard', path: '/dashboard', icon: 'tachometer-alt' },
  { name: 'Boards', path: '/boards', icon: 'clipboard-list' },
  { name: 'Time Tracker', path: '/tracker', icon: 'clock' },
  { name: 'Reports', path: '/reports', icon: 'chart-bar' },
  { name: 'Projects', path: '/projects', icon: 'project-diagram' },
  { name: 'Team', path: '/team', icon: 'users' },
]

// 🔥 LOGOUT FUNCTION
async function handleLogout() {
  try {
    await api.post('/auth/logout')
  } catch (err) {
    console.error('Logout error:', err)
  }

  // langsung redirect
  window.location.href = '/'
}
// async function handleLogout() {
//   try {
//     await api.post('/auth/logout')
//   } catch (err) {
//     console.error('Logout error:', err)
//   } finally {
//     // hapus token & user
//     localStorage.removeItem('access_token')
//     localStorage.removeItem('user')

//     // redirect ke login
//     router.push('/')
//   }
// }
</script>