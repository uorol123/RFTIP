import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface Notification {
  id: number
  type: 'success' | 'error' | 'warning' | 'info'
  message: string
  duration?: number
}

export const useAppStore = defineStore('app', () => {
  // State
  const sidebarCollapsed = ref(false)
  const notifications = ref<Notification[]>([])
  let notificationId = 0

  // Actions
  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  function setSidebarCollapsed(collapsed: boolean) {
    sidebarCollapsed.value = collapsed
  }

  function addNotification(notification: Omit<Notification, 'id'>) {
    const id = ++notificationId
    notifications.value.push({ ...notification, id })

    const duration = notification.duration ?? 3000
    if (duration > 0) {
      setTimeout(() => {
        removeNotification(id)
      }, duration)
    }

    return id
  }

  function removeNotification(id: number) {
    const index = notifications.value.findIndex((n) => n.id === id)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }

  function clearNotifications() {
    notifications.value = []
  }

  // 便捷方法
  function success(message: string, duration?: number) {
    return addNotification({ type: 'success', message, duration })
  }

  function error(message: string, duration?: number) {
    return addNotification({ type: 'error', message, duration })
  }

  function warning(message: string, duration?: number) {
    return addNotification({ type: 'warning', message, duration })
  }

  function info(message: string, duration?: number) {
    return addNotification({ type: 'info', message, duration })
  }

  return {
    // State
    sidebarCollapsed,
    notifications,
    // Actions
    toggleSidebar,
    setSidebarCollapsed,
    addNotification,
    removeNotification,
    clearNotifications,
    success,
    error,
    warning,
    info,
  }
})
