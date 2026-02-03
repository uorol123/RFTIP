/**
 * Notification Composable - Simplified Error/Success Notifications
 *
 * Provides an easy-to-use interface for showing notifications
 * with automatic error handling integration.
 */
import { useAppStore } from '@/stores/app'
import { handleError, isAuthError, formatErrorForDisplay } from '@/utils/errorHandler'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import logger from '@/utils/logger'

export function useNotification() {
  const appStore = useAppStore()
  const authStore = useAuthStore()
  const router = useRouter()

  /**
   * Show a success notification
   */
  const success = (message: string, duration?: number) => {
    return appStore.success(message, duration)
  }

  /**
   * Show an error notification
   */
  const error = (message: string, duration?: number) => {
    return appStore.error(message, duration)
  }

  /**
   * Show a warning notification
   */
  const warning = (message: string, duration?: number) => {
    return appStore.warning(message, duration)
  }

  /**
   * Show an info notification
   */
  const info = (message: string, duration?: number) => {
    return appStore.info(message, duration)
  }

  /**
   * Handle an error and show appropriate notification
   * Automatically handles auth errors by redirecting to login
   */
  const handleErrorNotification = (err: unknown, context?: Record<string, unknown>) => {
    const appError = handleError(err, context)
    const display = formatErrorForDisplay(appError)

    // Log the error
    logger.warn(`User notification: ${display.title} - ${display.message}`, {
      errorType: appError.type,
      errorCode: appError.code,
      context,
    })

    // Check if it's an auth error
    if (isAuthError(appError)) {
      // Auto logout and redirect
      authStore.logout()

      // Show notification
      error(display.message, 5000)

      // Redirect to login if not already there
      if (router.currentRoute.value.name !== 'Login') {
        router.push({
          name: 'Login',
          query: {
            redirect: router.currentRoute.value.fullPath !== '/' ? router.currentRoute.value.fullPath : undefined,
          },
        })
      }

      return
    }

    // Show error notification with action if available
    const fullMessage = display.action ? `${display.message}\n${display.action}` : display.message
    error(fullMessage, appError.type === 'network' ? 8000 : 5000)
  }

  /**
   * Show a notification from API operation result
   */
  const fromApiResult = <T>(result: { success: boolean; message?: string; data?: T; error?: unknown }) => {
    if (result.success) {
      if (result.message) {
        success(result.message)
      }
      return { success: true, data: result.data }
    } else {
      handleErrorNotification(result.error)
      return { success: false, error: result.error }
    }
  }

  /**
   * Wrap an async function with automatic error handling
   */
  const withErrorHandling = async <T>(
    fn: () => Promise<T>,
    options?: {
      successMessage?: string
      errorMessage?: string
      showSuccess?: boolean
      silent?: boolean
    }
  ): Promise<T | null> => {
    try {
      const result = await fn()

      if (options?.showSuccess && options?.successMessage) {
        success(options.successMessage)
      }

      return result
    } catch (err) {
      if (!options?.silent) {
        if (options?.errorMessage) {
          error(options.errorMessage)
        } else {
          handleErrorNotification(err)
        }
      }
      return null
    }
  }

  /**
   * Wrap an async function with loading state and error handling
   */
  const withLoading = async <T>(
    fn: () => Promise<T>,
    options?: {
      loadingMessage?: string
      successMessage?: string
      errorMessage?: string
      showSuccess?: boolean
      silent?: boolean
    }
  ): Promise<T | null> => {
    // Store original loading state
    // This would be better with a dedicated loading store
    const loadingMessage = options?.loadingMessage || '处理中...'

    try {
      info(loadingMessage, 0) // Show until explicitly removed

      const result = await fn()

      // Remove loading notification
      appStore.clearNotifications()

      if (options?.showSuccess && options?.successMessage) {
        success(options.successMessage)
      }

      return result
    } catch (err) {
      appStore.clearNotifications()

      if (!options?.silent) {
        if (options?.errorMessage) {
          error(options.errorMessage)
        } else {
          handleErrorNotification(err)
        }
      }
      return null
    }
  }

  /**
   * Clear all notifications
   */
  const clear = () => {
    appStore.clearNotifications()
  }

  return {
    success,
    error,
    warning,
    info,
    clear,
    handleErrorNotification,
    fromApiResult,
    withErrorHandling,
    withLoading,
  }
}

export default useNotification
