<template>
  <div class="home-page">
    <NavHeader />
    <div class="main-content">
      <HeroSection />
      <FeaturesSection />
    </div>
  </div>
</template>

<script setup lang="ts">
import NavHeader from '@/components/NavHeader.vue'
import HeroSection from '@/components/HeroSection.vue'
import FeaturesSection from '@/components/FeaturesSection.vue'
</script>

<style scoped>
.home-page {
  width: 100%;
  min-height: 100%;
  background: var(--bg-primary);
  display: flex;
  flex-direction: column;
  transition: background 0.3s ease;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}
</style>
