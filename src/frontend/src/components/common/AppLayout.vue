<template>
  <div class="flex flex-col h-screen bg-gray-100 dark:bg-gray-900">
    <!-- TOP HEADER -->
    <div
      class="h-14 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between px-6 flex-shrink-0 relative"
    >
      <div class="flex items-center gap-2 text-lg font-semibold">
        <img src="../../assets/Grid.png" alt="logo" class="w-5" />
        <span class="text-gray-800 dark:text-gray-100">Braves</span>
        <span class="text-blue-600">Board</span>
      </div>

      <div class="flex items-center gap-3">
        <button
          @click="toggleTheme"
          :title="isDark ? 'Switch to light mode' : 'Switch to dark mode'"
          class="w-8 h-8 flex items-center justify-center rounded-full border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 transition text-gray-600 dark:text-gray-300"
        >
          <font-awesome-icon :icon="isDark ? 'sun' : 'moon'" class="text-sm" />
        </button>
        <button
          class="w-8 h-8 flex items-center justify-center rounded-full border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 transition text-gray-600 dark:text-gray-300"
        >
          <font-awesome-icon icon="question" class="text-sm" />
        </button>
        <NotificationBell />
        <div class="relative">
          <div class="flex items-center gap-1">
            <button
              @click="showProfile = !showProfile"
              class="w-8 h-8 flex items-center justify-center rounded-full overflow-hidden border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 transition"
            >
              <!-- Tampilkan foto HANYA jika ada URL dan TIDAK error -->
              <img
                v-if="user?.picture_url && !imgError"
                :src="user.picture_url"
                :alt="user.full_name"
                @error="imgError = true"
                class="h-8 w-8 rounded-full object-cover"
              />
              <!-- Fallback: Jika tidak ada foto ATAU gambar broken, tampilkan Inisial -->
              <div
                v-else
                class="w-full h-full bg-blue-600 text-white font-bold text-xs flex items-center justify-center"
              >
                {{
                  user?.full_name ? user.full_name.charAt(0).toUpperCase() : "U"
                }}
              </div>
            </button>

            <font-awesome-icon
              v-if="!showProfile"
              icon="chevron-down"
              class="text-[10px] text-gray-400 dark:text-gray-500"
            />
            <font-awesome-icon
              v-else
              icon="chevron-up"
              class="text-[10px] text-gray-400 dark:text-gray-500"
            />
          </div>

          <!-- Profile Dropdown -->
          <div
            v-if="showProfile"
            class="absolute right-0 top-11 z-50 w-72 overflow-hidden rounded-xl border border-gray-200 bg-white shadow-xl dark:border-gray-700 dark:bg-gray-800"
          >
            <!-- Profile Header -->
            <div
              class="flex items-center gap-3 border-b border-gray-200 p-4 dark:border-gray-700"
            >
              <!-- Tampilkan foto HANYA jika ada URL dan TIDAK error -->
              <img
                v-if="user?.picture_url && !imgError"
                :src="user.picture_url"
                :alt="user.full_name"
                @error="imgError = true"
                class="h-12 w-12 rounded-full object-cover ring-2 ring-gray-100 dark:ring-gray-700"
              />
              <!-- Fallback: Jika tidak ada foto ATAU gambar broken, tampilkan Inisial -->
              <div
                v-else
                class="h-12 w-12 rounded-full bg-blue-600 text-white font-bold text-lg flex items-center justify-center ring-2 ring-gray-100 dark:ring-gray-700 flex-shrink-0"
              >
                {{
                  user?.full_name ? user.full_name.charAt(0).toUpperCase() : "U"
                }}
              </div>

              <div class="min-w-0">
                <p
                  class="truncate text-sm font-semibold text-gray-900 dark:text-white"
                >
                  {{ user?.full_name }}
                </p>

                <p class="truncate text-xs text-gray-500 dark:text-gray-400">
                  {{ user?.email }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="flex flex-1 overflow-hidden">
      <AppSidebar />
      <main class="flex-1 overflow-auto p-6 bg-gray-100 dark:bg-gray-900">
        <slot />
      </main>
    </div>
  </div>
  <!-- MODAL CONFIRM ACTIVE (MENIT KE-175) -->
  <Teleport to="body">
    <div
      v-if="showConfirmModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm px-4"
    >
      <div
        class="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-md w-full p-6 border border-gray-100 dark:border-gray-700 animate-in fade-in zoom-in duration-200"
      >
        <div class="flex items-center gap-3 mb-4 text-amber-500">
          <span class="text-2xl">⏳</span>
          <h3 class="text-base font-bold text-gray-800 dark:text-gray-100">
            Konfirmasi Aktivitas Kerja
          </h3>
        </div>

        <p class="text-sm text-gray-600 dark:text-gray-300 mb-2">
          Anda telah bekerja selama
          <strong class="text-blue-600">2 jam 55 menit</strong> pada task:
        </p>

        <div
          class="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-xl mb-4 border border-gray-200 dark:border-gray-600 text-sm font-semibold text-gray-800 dark:text-gray-100 truncate"
        >
          {{ activeTaskTitle }}
        </div>

        <p
          class="text-xs text-amber-600 dark:text-amber-400 mb-6 flex items-center gap-1.5"
        >
          <span>⚠️</span> Timer tetap berjalan. Otomatis berhenti dalam
          <strong
            >{{ Math.floor(countdownSeconds / 60) }}m
            {{ countdownSeconds % 60 }}s</strong
          >
          jika tidak dikonfirmasi.
        </p>

        <div class="flex items-center justify-end gap-3">
          <button
            @click="handleStopFromModal"
            class="px-4 py-2 text-xs font-semibold text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-xl transition"
          >
            Hentikan Timer
          </button>
          <button
            @click="handleConfirmActive"
            :disabled="confirmLoading"
            class="px-5 py-2 text-xs font-bold bg-blue-600 hover:bg-blue-700 text-white rounded-xl shadow-md transition disabled:opacity-50"
          >
            {{ confirmLoading ? "Menyimpan..." : "Ya, Lanjutkan Bekerja" }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { useGlobalTimer } from "../../composables/useGlobalTimer";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { library } from "@fortawesome/fontawesome-svg-core";
import {
  faQuestion,
  faUser,
  faMoon,
  faSun,
  faChevronDown,
  faChevronUp,
} from "@fortawesome/free-solid-svg-icons";
import AppSidebar from "./AppSidebar.vue";
import NotificationBell from "../../modules/notification/components/NotificationBell.vue";
import { useTheme } from "../../composables/useTheme";
import { onMounted, ref } from "vue";
import { useAuth } from "../../composables/useAuth";

const { isDark, toggleTheme } = useTheme();

library.add(faQuestion, faUser, faMoon, faSun, faChevronDown, faChevronUp);

const { user, fetchCurrentUser } = useAuth();
const showProfile = ref(false);
const imgError = ref(false);

const {
  showConfirmModal,
  activeTaskTitle,
  countdownSeconds,
  confirmLoading,
  handleConfirmActive,
  handleStopFromModal,
  initGlobalHeartbeat,
} = useGlobalTimer();

onMounted(() => {
  if (!user.value) {
    fetchCurrentUser();
  }
  initGlobalHeartbeat();
});
</script>
