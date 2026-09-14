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
              class="w-8 h-8 flex items-center justify-center rounded-full border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 transition"
            >
              <img
                v-if="user?.picture_url"
                :src="user.picture_url"
                :alt="user.full_name"
                class="h-8 w-8 rounded-full object-cover"
              />
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
              <img
                v-if="user?.picture_url"
                :src="user.picture_url"
                :alt="user.full_name"
                class="h-12 w-12 rounded-full object-cover ring-2 ring-gray-100 dark:ring-gray-700"
              />

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
</template>

<script setup lang="ts">
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

onMounted(() => {
  if (!user.value) {
    fetchCurrentUser();
  }
});
</script>
