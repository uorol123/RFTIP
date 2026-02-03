import apiClient from './client'
import { apiCall } from './client'
import type {
  ApiResponse,
  User,
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  LoginLog,
} from './types'

export const authApi = {
  /**
   * User login
   */
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    return apiCall(() =>
      apiClient.post<LoginResponse>('/auth/login', data)
    )
  },

  /**
   * User registration
   */
  register: async (data: RegisterRequest): Promise<LoginResponse> => {
    return apiCall(() =>
      apiClient.post<LoginResponse>('/auth/register', data)
    )
  },

  /**
   * User logout
   */
  logout: async (): Promise<void> => {
    return apiCall(() =>
      apiClient.post<void>('/auth/logout')
    )
  },

  /**
   * Get current user profile
   */
  getProfile: async (): Promise<User> => {
    return apiCall(() =>
      apiClient.get<User>('/auth/profile')
    )
  },

  /**
   * Update user profile
   */
  updateProfile: async (data: Partial<User>): Promise<User> => {
    return apiCall(() =>
      apiClient.put<User>('/auth/profile', data)
    )
  },

  /**
   * Get login logs
   */
  getLoginLogs: async (params?: { page?: number; page_size?: number }): Promise<ApiResponse<LoginLog[]>> => {
    return apiCall(() =>
      apiClient.get<ApiResponse<LoginLog[]>>('/auth/login-logs', { params })
    )
  },

  /**
   * Change password
   */
  changePassword: async (data: { old_password: string; new_password: string }): Promise<void> => {
    return apiCall(() =>
      apiClient.post<void>('/auth/change-password', data)
    )
  },
}
