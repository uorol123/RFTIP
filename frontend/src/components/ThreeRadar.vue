<template>
  <component :is="currentComponent" />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useThemeStore } from '@/stores/theme'
import TrajectoryDark from './TrajectoryDark.vue'
import TrajectoryLight from './TrajectoryLight.vue'

const themeStore = useThemeStore()

const currentComponent = computed(() => {
  return themeStore.isDark ? TrajectoryDark : TrajectoryLight
})
</script>
