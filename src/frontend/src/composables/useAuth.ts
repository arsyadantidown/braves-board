import { ref, computed } from 'vue'
import type { User } from '../modules/auth/api/auth.api'
import { getCurrentUser, logout as apiLogout } from '../modules/auth/api/auth.api'

// State global (singleton pattern tanpa Pinia)
const user = ref<User | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)

// Coba load user dari localStorage saat pertama kali
const savedUser = localStorage.getItem('user')
if (savedUser) {
  try {
    user.value = JSON.parse(savedUser)
  } catch {
    localStorage.removeItem('user')
  }
}

export function useAuth() {
  const isAuthenticated = computed(() => {
    return !!localStorage.getItem('access_token') && user.value !== null
  })

  async function fetchCurrentUser() {
    loading.value = true
    error.value = null
    try {
      user.value = await getCurrentUser()
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Gagal memuat profil'
      user.value = null
    } finally {
      loading.value = false
    }
  }

  async function signOut() {
    loading.value = true
    try {
      await apiLogout()
    } finally {
      user.value = null
      loading.value = false
    }
  }

  return {
    user,
    loading,
    error,
    isAuthenticated,
    fetchCurrentUser,
    signOut,
  }
}
