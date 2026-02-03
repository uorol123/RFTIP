<template>
  <Teleport to="body">
    <Transition name="dialog">
      <div v-if="show" class="dialog-overlay" @click="onOverlayClick">
        <div class="dialog-content" @click.stop>
          <div class="dialog-header">
            <h3 class="dialog-title">{{ title }}</h3>
          </div>
          <div class="dialog-body">
            <p class="dialog-message">{{ message }}</p>
          </div>
          <div class="dialog-footer">
            <button
              type="button"
              class="dialog-btn dialog-btn-cancel"
              @click="onCancel"
            >
              {{ cancelText }}
            </button>
            <button
              type="button"
              :class="['dialog-btn', 'dialog-btn-confirm', `dialog-btn-${type}`]"
              @click="onConfirm"
            >
              {{ confirmText }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { watch } from 'vue'

interface Props {
  show?: boolean
  title?: string
  message?: string
  confirmText?: string
  cancelText?: string
  type?: 'danger' | 'warning' | 'info' | 'success'
  closeOnOverlay?: boolean
}

interface Emits {
  (e: 'confirm'): void
  (e: 'cancel'): void
}

const props = withDefaults(defineProps<Props>(), {
  show: false,
  title: 'Confirm',
  message: 'Are you sure?',
  confirmText: 'Confirm',
  cancelText: 'Cancel',
  type: 'info',
  closeOnOverlay: true,
})

const emit = defineEmits<Emits>()

const onConfirm = () => {
  emit('confirm')
}

const onCancel = () => {
  emit('cancel')
}

const onOverlayClick = () => {
  if (props.closeOnOverlay) {
    emit('cancel')
  }
}

// Handle escape key
watch(() => props.show, (show) => {
  if (show) {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        emit('cancel')
      }
    }
    document.addEventListener('keydown', handleEscape)
    return () => document.removeEventListener('keydown', handleEscape)
  }
})
</script>

<style scoped>
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  z-index: 9999;
  padding: 1rem;
}

.dialog-content {
  width: 100%;
  max-width: 450px;
  border-radius: 1rem;
  background: var(--bg-secondary);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  overflow: hidden;
}

.dialog-header {
  padding: 1.5rem 1.5rem 1rem;
}

.dialog-title {
  margin: 0;
  color: var(--text-primary);
  font-size: 1.25rem;
  font-weight: 600;
}

.dialog-body {
  padding: 0 1.5rem 1.5rem;
}

.dialog-message {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.9375rem;
  line-height: 1.6;
}

.dialog-footer {
  display: flex;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--border-color, rgba(255, 255, 255, 0.1));
  justify-content: flex-end;
}

.dialog-btn {
  padding: 0.625rem 1.25rem;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.dialog-btn-cancel {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.dialog-btn-cancel:hover {
  background: var(--bg-primary);
}

.dialog-btn-confirm {
  color: white;
}

.dialog-btn-danger {
  background: #ef4444;
}

.dialog-btn-danger:hover {
  background: #dc2626;
}

.dialog-btn-warning {
  background: #f59e0b;
}

.dialog-btn-warning:hover {
  background: #d97706;
}

.dialog-btn-info {
  background: #3b82f6;
}

.dialog-btn-info:hover {
  background: #2563eb;
}

.dialog-btn-success {
  background: #10b981;
}

.dialog-btn-success:hover {
  background: #059669;
}

/* Dialog animations */
.dialog-enter-active,
.dialog-leave-active {
  transition: opacity 0.3s ease;
}

.dialog-enter-active .dialog-content,
.dialog-leave-active .dialog-content {
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.dialog-enter-from,
.dialog-leave-to {
  opacity: 0;
}

.dialog-enter-from .dialog-content,
.dialog-leave-to .dialog-content {
  transform: scale(0.95);
  opacity: 0;
}

@media (max-width: 640px) {
  .dialog-content {
    max-width: 100%;
  }

  .dialog-footer {
    flex-direction: column;
  }

  .dialog-btn {
    width: 100%;
  }
}
</style>
