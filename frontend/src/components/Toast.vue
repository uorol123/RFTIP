<template>
  <Teleport to="body">
    <TransitionGroup
      name="toast"
      tag="div"
      class="toast-container"
    >
      <div
        v-for="toast in toasts"
        :key="toast.id"
        :class="['toast', `toast-${toast.type}`]"
      >
        <div class="toast-icon">
          <svg v-if="toast.type === 'success'" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          <svg v-else-if="toast.type === 'error'" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
          <svg v-else-if="toast.type === 'warning'" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div class="toast-content">
          <div class="toast-message">{{ toast.message }}</div>
        </div>
        <button class="toast-close" @click="removeToast(toast.id)">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </TransitionGroup>
  </Teleport>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()
const { notifications: toasts } = storeToRefs(appStore)

const removeToast = (id: number) => {
  appStore.removeNotification(id)
}
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 1rem;
  right: 1rem;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  pointer-events: none;
}

.toast {
  pointer-events: auto;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  min-width: 300px;
  max-width: 450px;
  padding: 1rem;
  border-radius: 0.75rem;
  background: var(--bg-secondary);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  backdrop-filter: blur(12px);
  border: 1px solid var(--border-color, rgba(255, 255, 255, 0.1));
}

.toast-icon {
  flex-shrink: 0;
  width: 1.5rem;
  height: 1.5rem;
}

.toast-icon svg {
  width: 100%;
  height: 100%;
}

.toast-success .toast-icon {
  color: #10b981;
}

.toast-error .toast-icon {
  color: #ef4444;
}

.toast-warning .toast-icon {
  color: #f59e0b;
}

.toast-info .toast-icon {
  color: #3b82f6;
}

.toast-content {
  flex: 1;
  min-width: 0;
}

.toast-message {
  color: var(--text-primary);
  font-size: 0.875rem;
  line-height: 1.5;
  word-wrap: break-word;
}

.toast-close {
  flex-shrink: 0;
  width: 1.25rem;
  height: 1.25rem;
  padding: 0;
  border: none;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  transition: color 0.2s;
}

.toast-close:hover {
  color: var(--text-primary);
}

.toast-close svg {
  width: 100%;
  height: 100%;
}

/* Toast animations */
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

.toast-move {
  transition: transform 0.3s ease;
}

@media (max-width: 640px) {
  .toast-container {
    left: 1rem;
    right: 1rem;
  }

  .toast {
    min-width: 0;
    max-width: none;
  }
}
</style>
