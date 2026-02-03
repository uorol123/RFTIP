import axios, { AxiosError, InternalAxiosRequestConfig, AxiosResponse } from 'axios'
import { useAuthStore } from '@/stores/auth'
import type { ApiError } from './types'

// Create axios instance
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor - Add auth token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers = config.headers || {}
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor - Handle errors and token refresh
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  async (error: AxiosError<ApiError>) => {
    const authStore = useAuthStore()

    // Handle 401 Unauthorized - Token expired
    if (error.response?.status === 401) {
      // Clear auth state and redirect to login
      authStore.logout()
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }

    // Handle 403 Forbidden
    if (error.response?.status === 403) {
      return Promise.reject({
        code: 403,
        message: 'You do not have permission to perform this action',
      })
    }

    // Handle 404 Not Found
    if (error.response?.status === 404) {
      return Promise.reject({
        code: 404,
        message: 'The requested resource was not found',
      })
    }

    // Handle 500 Server Error
    if (error.response?.status === 500) {
      return Promise.reject({
        code: 500,
        message: 'Server error. Please try again later',
      })
    }

    // Return default error for network errors
    if (!error.response) {
      return Promise.reject({
        code: 0,
        message: 'Network error. Please check your connection',
      })
    }

    // Return error from server
    return Promise.reject(error.response.data || {
      code: error.response.status,
      message: error.message || 'An error occurred',
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
    throw error
  }
}

export default apiClient
