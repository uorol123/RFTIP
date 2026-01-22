import { defineStore } from 'pinia'
import { ref, watch, onMounted } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const isDark = ref(false)

  function getStoredTheme(): boolean {
    if (typeof window === 'undefined') return false
    const stored = localStorage.getItem('rftip-theme')
    return stored === 'dark'
  }

  function applyTheme() {
    if (typeof window === 'undefined') return

    if (isDark.value) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }

  // Initialize theme on mount
  onMounted(() => {
    isDark.value = getStoredTheme()
    applyTheme()
  })

  // Watch for changes
  watch(isDark, (newValue) => {
    localStorage.setItem('rftip-theme', newValue ? 'dark' : 'light')
    applyTheme()
  })

  function toggleTheme() {
    isDark.value = !isDark.value
  }

  function setTheme(dark: boolean) {
    isDark.value = dark
  }

  return {
    isDark,
    toggleTheme,
    setTheme,
  }
})
