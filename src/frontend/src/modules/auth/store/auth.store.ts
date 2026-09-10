import axios from "axios";
import { computed, ref } from "vue";
import { defineStore } from "pinia";
import type { User } from "../api/auth.api";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";
const BASE_URL = `${API_BASE_URL}/api/v1`;

// Client khusus refresh: tidak memakai interceptor API utama,
// agar refresh 401 tidak memicu refresh berulang.
const refreshClient = axios.create({
  baseURL: BASE_URL,
  withCredentials: true,
});

export const useAuthStore = defineStore("auth", () => {
  // Jangan tambahkan `persist`: access token wajib hanya hidup di memory.
  const accessToken = ref<string | null>(null);
  const user = ref<User | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const initialized = ref(false);

  let refreshPromise: Promise<string | null> | null = null;

  const isAuthenticated = computed(() => accessToken.value !== null);

  function setAccessToken(token: string) {
    accessToken.value = token;
  }

  function setUser(value: User | null) {
    user.value = value;
  }

  function clearSession() {
    accessToken.value = null;
    user.value = null;
    error.value = null;
  }

  async function refreshAccessToken(): Promise<string | null> {
    if (!refreshPromise) {
      refreshPromise = refreshClient
        .post("/auth/refresh", {})
        .then(({ data }) => {
          const token: string | undefined =
            data?.data?.access_token ?? data?.access_token;

          if (!token) {
            throw new Error("Response refresh tidak mengandung access_token");
          }

          setAccessToken(token);
          return token;
        })
        .catch(() => {
          clearSession();
          return null;
        })
        .finally(() => {
          refreshPromise = null;
        });
    }

    return refreshPromise;
  }

  async function initialize(): Promise<boolean> {
    if (initialized.value) {
      return isAuthenticated.value;
    }

    initialized.value = true;
    await refreshAccessToken();
    return isAuthenticated.value;
  }

  return {
    accessToken,
    user,
    loading,
    error,
    initialized,
    isAuthenticated,
    setAccessToken,
    setUser,
    clearSession,
    refreshAccessToken,
    initialize,
  };
});
