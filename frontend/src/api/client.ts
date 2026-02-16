import axios, { AxiosError } from 'axios'
import type { InternalAxiosRequestConfig, AxiosResponse } from 'axios'
import { useAuthStore } from '@/stores/auth'
import type { ApiError } from './types'
import logger from '@/utils/logger'
import { handleError, isAuthError } from '@/utils/errorHandler'

// Create axios instance
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request ID counter for tracking
let requestIdCounter = 0

// Request interceptor - Add auth token and logging
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers = config.headers || {}
      config.headers.Authorization = `Bearer ${authStore.token}`
    }

    // Add request ID for tracking
    const requestId = ++requestIdCounter
    config.headers['X-Request-ID'] = `req_${requestId}`
    config.metadata = { requestId, startTime: Date.now() }

    // Log the request
    logger.apiRequest(
      config.method?.toUpperCase() || 'UNKNOWN',
      config.url || 'unknown',
      {
        requestId: `req_${requestId}`,
        headers: config.headers,
        params: config.params,
        hasData: !!config.data,
      }
    )

    return config
  },
  (error) => {
    logger.error('Request interceptor error', error instanceof Error ? error : new Error(String(error)))
    return Promise.reject(error)
  }
)

// Response interceptor - Handle errors, token refresh, and logging
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    // Log successful response
    const duration = Date.now() - (response.config.metadata?.startTime || 0)
    const requestId = response.config.headers['X-Request-ID']

    logger.apiResponse(
      response.config.method?.toUpperCase() || 'UNKNOWN',
      response.config.url || 'unknown',
      response.status,
      duration
    )

    // Log slow responses
    if (duration > 2000) {
      logger.warn(`Slow API response: ${response.config.url} (${duration}ms)`, {
        requestId,
        url: response.config.url,
        duration,
      })
    }

    return response
  },
  async (error: AxiosError<ApiError>) => {
    const authStore = useAuthStore()
    const requestId = error.config?.headers['X-Request-ID']
    const duration = Date.now() - (error.config?.metadata?.startTime || Date.now())

    // Log the error response
    logger.apiResponse(
      error.config?.method?.toUpperCase() || 'UNKNOWN',
      error.config?.url || 'unknown',
      error.response?.status || 0,
      duration
    )

    // Handle 401 Unauthorized - Token expired
    if (error.response?.status === 401) {
      logger.warn('Authentication failed - clearing auth state', {
        requestId,
        url: error.config?.url,
      })

      // Clear auth state
      authStore.logout()

      // Redirect to login if not already there
      if (window.location.pathname !== '/login') {
        const returnUrl = window.location.pathname !== '/' ? window.location.pathname : undefined
        window.location.href = `/login${returnUrl ? `?redirect=${encodeURIComponent(returnUrl)}` : ''}`
      }
    }

    // Handle 403 Forbidden
    if (error.response?.status === 403) {
      logger.warn('Authorization failed - permission denied', {
        requestId,
        url: error.config?.url,
      })

      return Promise.reject({
        code: 'PERMISSION_DENIED',
        message: '您没有权限执行此操作',
        detail: error.response.data?.detail,
        status: 403,
      })
    }

    // Handle 404 Not Found
    if (error.response?.status === 404) {
      logger.warn('Resource not found', {
        requestId,
        url: error.config?.url,
      })

      return Promise.reject({
        code: 'NOT_FOUND',
        message: '请求的资源不存在',
        detail: error.response.data?.detail,
        status: 404,
      })
    }

    // Handle 409 Conflict
    if (error.response?.status === 409) {
      return Promise.reject({
        code: error.response.data?.code || 'CONFLICT',
        message: error.response.data?.message || '数据冲突，请刷新后重试',
        detail: error.response.data?.detail,
        status: 409,
      })
    }

    // Handle 422 Validation Error
    if (error.response?.status === 422) {
      logger.warn('Validation error', {
        requestId,
        url: error.config?.url,
        errors: error.response.data,
      })

      return Promise.reject({
        code: 'VALIDATION_ERROR',
        message: error.response.data?.message || '输入数据有误，请检查后重试',
        errors: error.response.data?.errors,
        detail: error.response.data?.detail,
        status: 422,
      })
    }

    // Handle 429 Rate Limit
    if (error.response?.status === 429) {
      const retryAfter = error.response.headers['retry-after']
      logger.warn('Rate limit exceeded', {
        requestId,
        url: error.config?.url,
        retryAfter,
      })

      return Promise.reject({
        code: 'RATE_LIMIT_EXCEEDED',
        message: retryAfter
          ? `请求过于频繁，请 ${retryAfter} 秒后重试`
          : '请求过于频繁，请稍后再试',
        detail: error.response.data?.detail,
        status: 429,
      })
    }

    // Handle 500+ Server Errors
    if (error.response?.status && error.response.status >= 500) {
      logger.error('Server error', error instanceof Error ? error : new Error(String(error)), {
        requestId,
        url: error.config?.url,
        status: error.response.status,
      })

      return Promise.reject({
        code: 'INTERNAL_SERVER_ERROR',
        message: '服务器错误，请稍后重试',
        detail: error.response.data?.detail,
        status: error.response.status,
      })
    }

    // Network error (no response)
    if (!error.response) {
      logger.warn('Network error', {
        requestId,
        url: error.config?.url,
        message: error.message,
      })

      return Promise.reject({
        code: 0,
        message: '网络连接失败，请检查网络设置',
        detail: error.message,
        status: 0,
      })
    }

    // Return error from server with structured format
    const serverError = error.response.data
    return Promise.reject({
      code: serverError?.code || error.response.status,
      message: serverError?.message || error.message || '请求失败',
      detail: serverError?.detail,
      errors: serverError?.errors,
      status: error.response.status,
    })
  }
)

// Wrapper for API calls with consistent error handling
export const apiCall = async <T>(
  apiFunction: () => Promise<AxiosResponse<T>>
): Promise<T> => {
  try {
    const response = await apiFunction()
    return response.data
  } catch (error) {
    // Convert to AppError and re-throw
    throw error
  }
}

// Wrapper for API calls with automatic error notification
export const apiCallWithNotify = async <T>(
  apiFunction: () => Promise<AxiosResponse<T>>,
  options?: {
    successMessage?: string
    errorMessage?: string
  }
): Promise<T> => {
  try {
    const response = await apiFunction()

    // Show success message if provided
    if (options?.successMessage) {
      // Dynamically import to avoid circular dependencies
      const { useAppStore } = await import('@/stores/app')
      const appStore = useAppStore()
      appStore.success(options.successMessage)
    }

    return response.data
  } catch (error) {
    // Show error notification
    const appError = handleError(error)

    if (options?.errorMessage) {
      const { useAppStore } = await import('@/stores/app')
      const appStore = useAppStore()
      appStore.error(options.errorMessage)
    } else {
      const { useAppStore } = await import('@/stores/app')
      const appStore = useAppStore()

      // Handle auth errors silently (they're handled by the interceptor)
      if (!isAuthError(appError)) {
        const { formatErrorForDisplay } = await import('@/utils/errorHandler')
        const display = formatErrorForDisplay(appError)
        appStore.error(display.message)
      }
    }

    throw error
  }
}

// Export API call utilities
export default apiClient
