import { createApp } from "vue";
import { createPinia } from "pinia";
import piniaPluginPersistedstate from "pinia-plugin-persistedstate";
import App from "./App.vue";
import router from "./app/router";
import "./index.css";
import { initTheme } from "./composables/useTheme";
import { useAuthStore } from "./modules/auth/store/auth.store";
// Terapkan preferensi dark mode sedini mungkin (sebelum mount) supaya tidak
// ada flash tema terang saat halaman pertama kali dibuka.
initTheme();

const pinia = createPinia();
pinia.use(piniaPluginPersistedstate);

async function bootstrap() {
  const app = createApp(App);

  app.use(pinia);

  // Bersihkan token lama dari implementasi sebelumnya.
  // Setelah migrasi tidak ada lagi kode yang menulis key ini.
  localStorage.removeItem("access_token");
  localStorage.removeItem("user");

  // Kalau refresh cookie valid, token baru masuk ke Pinia memory.
  // Kalau tidak valid/tidak ada, aplikasi tetap lanjut sebagai guest.
  await useAuthStore(pinia).initialize();

  app.use(router);
  await router.isReady();

  app.mount("#app");
}

void bootstrap();
