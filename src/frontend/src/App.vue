<template>
  <router-view />
  <!-- Reminder timer tiap 3 jam — global, tetap jalan lintas halaman selama tab terbuka -->
  <TimerReminderDialog />
</template>

<script setup lang="ts">
import TimerReminderDialog from './modules/timer/components/TimerReminderDialog.vue'
</script>
