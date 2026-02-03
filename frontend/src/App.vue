<template>
  <div id="app" :class="{ 'is-dark': isDark }">
    <router-view />
    <Toast />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useThemeStore } from '@/stores/theme'
import { useAuthStore } from '@/stores/auth'
import Toast from '@/components/Toast.vue'

const themeStore = useThemeStore()
const authStore = useAuthStore()

const { isDark } = storeToRefs(themeStore)

// Initialize theme from storage
onMounted(() => {
  themeStore.setTheme(localStorage.getItem('theme') === 'dark')
  authStore.loadUserFromStorage()
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial,
    sans-serif;
}

#app {
  width: 100%;
  min-height: 100vh;
}

#app.is-dark {
  color-scheme: dark;
}
</style>
