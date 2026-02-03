/**
 * Error Handler Utility - Centralized Error Handling
 *
 * Provides consistent error handling across the application.
 * Handles different error types and provides user-friendly messages.
 */

import type { AxiosError } from 'axios'
import logger from './logger'
import type { ApiError } from '@/api/types'

export enum ErrorType {
  NETWORK = 'network',
  SERVER = 'server',
  VALIDATION = 'validation',
  AUTHENTICATION = 'authentication',
  AUTHORIZATION = 'authorization',
  NOT_FOUND = 'not_found',
  CONFLICT = 'conflict',
  RATE_LIMIT = 'rate_limit',
  UNKNOWN = 'unknown',
}

export interface AppError {
  type: ErrorType
  code: string | number
  message: string
  detail?: string
  originalError?: unknown
  context?: Record<string, unknown>
}

/**
 * Get user-friendly error message from API error
 */
function getErrorMessage(error: ApiError): string {
  // Error message mapping
  const messageMap: Record<string, string> = {
    // Authentication errors
    AUTHENTICATION_FAILED: '登录失败，请检查用户名和密码',
    TOKEN_EXPIRED: '登录已过期，请重新登录',
    INVALID_TOKEN: '登录信息无效，请重新登录',

    // Authorization errors
    PERMISSION_DENIED: '您没有权限执行此操作',

    // Validation errors
    VALIDATION_ERROR: '输入数据有误，请检查后重试',

    // Not found errors
    NOT_FOUND: '请求的资源不存在',
    USER_NOT_FOUND: '用户不存在',
    FILE_NOT_FOUND: '文件不存在',

    // Conflict errors
    CONFLICT: '数据冲突，请刷新后重试',
    DUPLICATE_USER: '用户名已存在',

    // Server errors
    INTERNAL_SERVER_ERROR: '服务器错误，请稍后重试',
    DATABASE_ERROR: '数据库错误，请稍后重试',

    // Network errors
    NETWORK_ERROR: '网络连接失败，请检查网络设置',

    // File errors
    FILE_PROCESSING_FAILED: '文件处理失败',
    INVALID_FILE_TYPE: '不支持的文件类型',
    FILE_SIZE_LIMIT_EXCEEDED: '文件大小超出限制',

    // Rate limiting
    RATE_LIMIT_EXCEEDED: '请求过于频繁，请稍后再试',
  }

  // Try to find a mapped message by error code
  if (error.code && typeof error.code === 'string') {
    const mappedMessage = messageMap[error.code]
    if (mappedMessage) {
      return mappedMessage
    }
  }

  // Return the server's message if available
  if (error.message) {
    return error.message
  }

  // Fallback message
  return '操作失败，请稍后重试'
}

/**
 * Get error type from HTTP status code or error code
 */
function getErrorType(error: ApiError): ErrorType {
  const code = error.code

  // Network error (no response)
  if (code === 0) {
    return ErrorType.NETWORK
  }

  // By status code
  if (typeof code === 'number') {
    if (code === 401) return ErrorType.AUTHENTICATION
    if (code === 403) return ErrorType.AUTHORIZATION
    if (code === 404) return ErrorType.NOT_FOUND
    if (code === 409) return ErrorType.CONFLICT
    if (code === 422) return ErrorType.VALIDATION
    if (code === 429) return ErrorType.RATE_LIMIT
    if (code >= 500) return ErrorType.SERVER
    if (code >= 400) return ErrorType.VALIDATION
  }

  // By error code string
  if (typeof code === 'string') {
    if (code.includes('AUTH') || code.includes('TOKEN')) return ErrorType.AUTHENTICATION
    if (code.includes('PERMISSION')) return ErrorType.AUTHORIZATION
    if (code.includes('NOT_FOUND')) return ErrorType.NOT_FOUND
    if (code.includes('CONFLICT') || code.includes('DUPLICATE')) return ErrorType.CONFLICT
    if (code.includes('VALIDATION') || code.includes('INVALID')) return ErrorType.VALIDATION
    if (code.includes('RATE_LIMIT')) return ErrorType.RATE_LIMIT
    if (code.includes('SERVER') || code.includes('DATABASE')) return ErrorType.SERVER
    if (code.includes('NETWORK')) return ErrorType.NETWORK
  }

  return ErrorType.UNKNOWN
}

/**
 * Handle Axios errors and convert to AppError
 */
export function handleAxiosError(error: AxiosError<ApiError>): AppError {
  const apiError = error.response?.data

  // If we have a structured API error
  if (apiError) {
    const appError: AppError = {
      type: getErrorType(apiError),
      code: apiError.code,
      message: getErrorMessage(apiError),
      detail: apiError.detail,
      originalError: error,
    }

    // Log the error
    if (appError.type === ErrorType.SERVER || appError.type === ErrorType.UNKNOWN) {
      logger.error(`API Error: ${appError.message}`, error instanceof Error ? error : new Error(String(error)), {
        url: error.config?.url,
        method: error.config?.method?.toUpperCase(),
        status: error.response?.status,
        code: appError.code,
      })
    } else {
      logger.warn(`API Error: ${appError.message}`, {
        url: error.config?.url,
        method: error.config?.method?.toUpperCase(),
        status: error.response?.status,
        code: appError.code,
      })
    }

    return appError
  }

  // Network error or timeout
  if (!error.response) {
    const appError: AppError = {
      type: ErrorType.NETWORK,
      code: 0,
      message: '网络连接失败，请检查网络设置',
      detail: error.message,
      originalError: error,
    }

    logger.warn('Network Error', {
      url: error.config?.url,
      message: error.message,
    })

    return appError
  }

  // Unknown error structure
  const appError: AppError = {
    type: ErrorType.UNKNOWN,
    code: error.response.status,
    message: `请求失败 (${error.response.status})`,
    detail: error.message,
    originalError: error,
  }

  logger.error(`Unknown API Error`, error instanceof Error ? error : new Error(String(error)), {
    url: error.config?.url,
    status: error.response.status,
  })

  return appError
}

/**
 * Handle generic JavaScript errors
 */
export function handleGenericError(error: unknown): AppError {
  if (error instanceof Error) {
    return {
      type: ErrorType.UNKNOWN,
      code: 'RUNTIME_ERROR',
      message: error.message || '发生未知错误',
      detail: error.stack,
      originalError: error,
    }
  }

  return {
    type: ErrorType.UNKNOWN,
    code: 'UNKNOWN_ERROR',
    message: '发生未知错误',
    detail: String(error),
    originalError: error,
  }
}

/**
 * Main error handler function
 */
export function handleError(error: unknown, context?: Record<string, unknown>): AppError {
  // Add context to logger
  if (context) {
    logger.debug('Error context', context)
  }

  // Axios error
  if (error && typeof error === 'object' && 'isAxiosError' in error) {
    return handleAxiosError(error as AxiosError<ApiError>)
  }

  // Generic error
  return handleGenericError(error)
}

/**
 * Check if error is retryable
 */
export function isRetryableError(error: AppError): boolean {
  return (
    error.type === ErrorType.NETWORK ||
    error.type === ErrorType.SERVER ||
    error.code === 429 || // Rate limit
    error.code === 503 // Service unavailable
  )
}

/**
 * Check if error should trigger logout
 */
export function isAuthError(error: AppError): boolean {
  return (
    error.type === ErrorType.AUTHENTICATION ||
    error.code === 'TOKEN_EXPIRED' ||
    error.code === 'INVALID_TOKEN' ||
    error.code === 401
  )
}

/**
 * Get suggested action for error
 */
export function getSuggestedAction(error: AppError): string | null {
  const actionMap: Record<ErrorType, string | null> = {
    [ErrorType.NETWORK]: '请检查您的网络连接',
    [ErrorType.SERVER]: '请稍后重试，如果问题持续存在请联系技术支持',
    [ErrorType.VALIDATION]: '请检查您的输入信息',
    [ErrorType.AUTHENTICATION]: '请重新登录',
    [ErrorType.AUTHORIZATION]: '您没有权限执行此操作',
    [ErrorType.NOT_FOUND]: '请确认资源是否存在',
    [ErrorType.CONFLICT]: '请刷新页面后重试',
    [ErrorType.RATE_LIMIT]: '请稍后再试',
    [ErrorType.UNKNOWN]: '请稍后重试',
  }

  return actionMap[error.type] || null
}

/**
 * Format error for user display
 */
export function formatErrorForDisplay(error: AppError): {
  title: string
  message: string
  action?: string
} {
  const titleMap: Record<ErrorType, string> = {
    [ErrorType.NETWORK]: '网络错误',
    [ErrorType.SERVER]: '服务器错误',
    [ErrorType.VALIDATION]: '输入错误',
    [ErrorType.AUTHENTICATION]: '认证失败',
    [ErrorType.AUTHORIZATION]: '权限不足',
    [ErrorType.NOT_FOUND]: '未找到',
    [ErrorType.CONFLICT]: '数据冲突',
    [ErrorType.RATE_LIMIT]: '请求过于频繁',
    [ErrorType.UNKNOWN]: '错误',
  }

  return {
    title: titleMap[error.type] || '错误',
    message: error.message,
    action: getSuggestedAction(error) || undefined,
  }
}

/**
 * Create a toast notification config from an error
 */
export function errorToToastConfig(error: AppError) {
  const display = formatErrorForDisplay(error)

  return {
    title: display.title,
    description: display.message,
    status: 'error' as const,
    duration: error.type === ErrorType.NETWORK ? 8000 : 5000,
    isClosable: true,
  }
}

export default {
  handleError,
  handleAxiosError,
  handleGenericError,
  isRetryableError,
  isAuthError,
  getSuggestedAction,
  formatErrorForDisplay,
  errorToToastConfig,
}
