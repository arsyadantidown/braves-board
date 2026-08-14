import { ref } from 'vue'

// Dark mode global — mekanisme yang sama dengan LoginView sebelumnya:
// preferensi disimpan di localStorage key 'theme' ('true'/'false') dan
// diterapkan lewat class 'dark' (Tailwind darkMode: 'class'). Bedanya class
// dipasang di <html> (document.documentElement) supaya berlaku ke SELURUH
// aplikasi — termasuk konten yang di-Teleport ke <body> (modal card detail).

const STORAGE_KEY = 'theme'

// State singleton (dibagikan semua komponen yang memanggil useTheme()).
const isDark = ref<boolean>(false)

function apply(val: boolean) {
    const root = document.documentElement
    if (val) root.classList.add('dark')
    else root.classList.remove('dark')
}

/**
 * Baca preferensi tersimpan lalu terapkan. Dipanggil sekali sedini mungkin
 * (main.ts) supaya tema sudah benar sebelum halaman pertama render.
 */
export function initTheme() {
    isDark.value = localStorage.getItem(STORAGE_KEY) === 'true'
    apply(isDark.value)
}

export function useTheme() {
    function setDark(val: boolean) {
        isDark.value = val
        localStorage.setItem(STORAGE_KEY, String(val))
        apply(val)
    }

    function toggleTheme() {
        setDark(!isDark.value)
    }

    return { isDark, setDark, toggleTheme }
}
