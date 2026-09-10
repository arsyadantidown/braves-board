import { storeToRefs } from "pinia";
import {
  getCurrentUser,
  logout as apiLogout,
} from "../modules/auth/api/auth.api";
import { useAuthStore } from "../modules/auth/store/auth.store";

export function useAuth() {
  const authStore = useAuthStore();
  const { user, loading, error, accessToken, isAuthenticated } =
    storeToRefs(authStore);

  async function fetchCurrentUser() {
    loading.value = true;
    error.value = null;

    try {
      const currentUser = await getCurrentUser();
      authStore.setUser(currentUser);
      return currentUser;
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : "Gagal memuat profil";

      authStore.setUser(null);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function signOut() {
    loading.value = true;

    try {
      await apiLogout();
    } finally {
      authStore.clearSession();
      loading.value = false;
    }
  }

  return {
    user,
    loading,
    error,
    accessToken,
    isAuthenticated,
    fetchCurrentUser,
    signOut,
  };
}
