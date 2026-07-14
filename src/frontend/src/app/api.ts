// src/app/api.ts
import axios, { AxiosError, AxiosHeaders } from 'axios'
import type { InternalAxiosRequestConfig } from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? ''
const BASE_URL = `${API_BASE_URL}/api/v1`

const NON_IDEMPOTENT_METHODS = ['post', 'put', 'patch', 'delete']
const REFRESH_PATH = '/auth/refresh'

type RetriableRequest = InternalAxiosRequestConfig & { _retry?: boolean }

const api = axios.create({
  baseURL: BASE_URL,
  // Refresh token dikirim lewat httpOnly cookie dari backend.
  withCredentials: true,
})

// Auto inject token & nonce
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')

  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }

  if (config.method && NON_IDEMPOTENT_METHODS.includes(config.method.toLowerCase())) {
    config.headers['X-Request-Nonce'] = crypto.randomUUID()
  }

  return config
})

// ─── Single-flight refresh ──────────────────────────────────────
// Saat banyak request 401 bersamaan, hanya SATU POST /auth/refresh yang
// terbang; sisanya menunggu promise yang sama. Tanpa ini, tiap request
// menembak /auth/refresh sendiri dan kena rate limiter (20 req/60s).
let refreshPromise: Promise<string> | null = null

function refreshAccessToken(): Promise<string> {
  if (!refreshPromise) {
    // axios polos, bukan `api`, supaya 401 dari refresh tidak memicu
    // response interceptor ini lagi (infinite loop).
    refreshPromise = axios
      .post(
        `${BASE_URL}${REFRESH_PATH}`,
        {},
        {
          withCredentials: true,
          headers: { 'X-Request-Nonce': crypto.randomUUID() },
        },
      )
      .then(({ data }) => {
        const token: string | undefined = data?.data?.access_token ?? data?.access_token
        if (!token) {
          throw new Error('Response /auth/refresh tidak mengandung access_token')
        }
        localStorage.setItem('access_token', token)
        return token
      })
      .finally(() => {
        // Dilepas setelah settle — penunggu yang sudah pegang referensi
        // tetap menerima hasil yang sama.
        refreshPromise = null
      })
  }

  return refreshPromise
}

function handleAuthFailure() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('user')

  if (window.location.pathname !== '/') {
    window.location.href = '/'
  }
}

// Response interceptor: auto-refresh saat 401
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as RetriableRequest | undefined

    if (error.response?.status !== 401 || !originalRequest) {
      return Promise.reject(error)
    }

    // Refresh-nya sendiri yang 401 → refresh token mati, tidak ada gunanya retry.
    if (originalRequest.url?.includes(REFRESH_PATH)) {
      handleAuthFailure()
      return Promise.reject(error)
    }

    // Sudah pernah di-retry dengan token baru dan tetap 401 → berhenti.
    // Flag ini WAJIB dipasang di setiap request, bukan cuma yang pertama,
    // supaya tidak ada request yang memicu gelombang refresh kedua.
    if (originalRequest._retry) {
      handleAuthFailure()
      return Promise.reject(error)
    }

    originalRequest._retry = true

    try {
      const token = await refreshAccessToken()
      originalRequest.headers = AxiosHeaders.from(originalRequest.headers)
      originalRequest.headers.set('Authorization', `Bearer ${token}`)
      return await api(originalRequest)
    } catch (refreshError) {
      handleAuthFailure()
      return Promise.reject(refreshError)
    }
  },
)

export default api
