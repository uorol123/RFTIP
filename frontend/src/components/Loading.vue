<template>
  <div :class="['loading-overlay', { fullscreen }]" v-if="show">
    <div class="loading-content">
      <div class="spinner"></div>
      <p v-if="message" class="loading-message">{{ message }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  show?: boolean
  message?: string
  fullscreen?: boolean
}

withDefaults(defineProps<Props>(), {
  show: true,
  message: '',
  fullscreen: true,
})
</script>

<style scoped>
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(15, 23, 42, 0.5);
  backdrop-filter: blur(4px);
  z-index: 1000;
}

.loading-overlay.fullscreen {
  position: fixed;
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 2rem;
  border-radius: 1rem;
  background: var(--bg-secondary);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

.spinner {
  width: 3rem;
  height: 3rem;
  border: 3px solid var(--bg-tertiary);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-message {
  margin: 0;
  color: var(--text-primary);
  font-size: 0.875rem;
  font-weight: 500;
}

@media (prefers-reduced-motion: reduce) {
  .spinner {
    animation-duration: 2s;
  }
}
</style>
