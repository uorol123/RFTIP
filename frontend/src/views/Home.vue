<template>
  <div class="home-page">
    <ThreeRadar />
  </div>
</template>

<script setup lang="ts">
import ThreeRadar from '@/components/ThreeRadar.vue'
</script>

<style scoped>
.home-page {
  width: 100%;
  min-height: 100vh;
  background: var(--bg-primary);
}
</style>
