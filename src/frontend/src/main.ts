import { createApp } from 'vue'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import App from './App.vue'
import router from "./app/router";
import './index.css'
import { initTheme } from './composables/useTheme'

// Terapkan preferensi dark mode sedini mungkin (sebelum mount) supaya tidak
// ada flash tema terang saat halaman pertama kali dibuka.
initTheme()

const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)

const app = createApp(App)
app.use(pinia)
app.use(router)
app.mount('#app')
