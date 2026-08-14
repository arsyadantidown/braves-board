<template>
  <div>
    <div class="min-h-screen flex items-center justify-center bg-gray-100 dark:bg-gray-900 transition duration-300">
      <button
        @click="toggleTheme"
        class="absolute top-5 right-5 px-4 py-2 rounded bg-black text-white dark:bg-white dark:text-black"
      >
        {{ isDark ? 'Light' : 'Dark' }}
      </button>

      <div class="bg-white dark:bg-gray-800 text-white dark:text-white p-8 rounded-xl">
        <div class="flex items-center justify-center gap-3 mb-6">
          <div class="p-5 text-lg font-semibold text-gray-700 dark:text-gray-200 border-b border-gray-200 flex items-center gap-1">
            <img src="../../../assets/Grid.png" alt="" class="w-5" />
            Braves <span class="text-blue-600">Board</span>
          </div>
        </div>

        <!-- Error message -->
        <p v-if="errorMsg" class="text-red-500 text-xs text-center mb-3 px-1">{{ errorMsg }}</p>

        <!-- Sign in with Google -->
        <button
          @click="handleGoogleLogin"
          :disabled="isLoading"
          class="flex items-center justify-center gap-3 w-full border border-gray-300 py-2.5 px-4 rounded-lg hover:bg-gray-50 transition text-gray-700 dark:text-gray-200 dark:hover:bg-gray-700 font-medium text-sm disabled:opacity-60 disabled:cursor-not-allowed"
        >
          <img src="../../../assets/google.png" alt="google" class="w-5 h-5" />
          <span v-if="isLoading">Menghubungkan...</span>
          <span v-else>Sign in with Google</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { getGoogleLoginUrl } from '../api/auth.api'
import { useTheme } from '../../../composables/useTheme'

const { isDark, toggleTheme } = useTheme()
const isLoading = ref(false)
const errorMsg = ref<string | null>(null)

async function handleGoogleLogin() {
  isLoading.value = true
  errorMsg.value = null
  try {
    const url = await getGoogleLoginUrl()
    window.location.href = url
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : ''
    if (msg.includes('Network Error') || msg.includes('ECONNREFUSED')) {
      errorMsg.value = 'Server tidak dapat dijangkau. Pastikan backend sudah berjalan.'
    } else if (msg.includes('401') || msg.includes('Unauthorized')) {
      errorMsg.value = 'Endpoint login tidak dikenali server. Hubungi developer backend.'
    } else {
      errorMsg.value = msg || 'Gagal menghubungi server. Coba lagi.'
    }
    isLoading.value = false
  }
}
</script>