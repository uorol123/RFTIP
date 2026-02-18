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

// 函数式导出
export async function login(data: LoginRequest): Promise<LoginResponse> {
  return apiCall(() =>
    apiClient.post<LoginResponse>('/auth/login', data)
  )
}

export async function register(data: RegisterRequest): Promise<LoginResponse> {
  return apiCall(() =>
    apiClient.post<LoginResponse>('/auth/register', data)
  )
}

export async function logout(): Promise<void> {
  return apiCall(() =>
    apiClient.post<void>('/auth/logout')
  )
}

export async function getProfile(): Promise<User> {
  return apiCall(() =>
    apiClient.get<User>('/auth/profile')
  )
}

export async function updateProfile(data: Partial<User>): Promise<User> {
  return apiCall(() =>
    apiClient.put<User>('/auth/profile', data)
  )
}

export async function getLoginLogs(params?: { page?: number; page_size?: number }): Promise<ApiResponse<LoginLog[]>> {
  return apiCall(() =>
    apiClient.get<ApiResponse<LoginLog[]>>('/auth/login-logs', { params })
  )
}

export async function changePassword(data: { old_password: string; new_password: string }): Promise<void> {
  return apiCall(() =>
    apiClient.post<void>('/auth/change-password', data)
  )
}

// 发送验证码
export async function sendVerificationCode(email: string): Promise<{ message: string; email: string; expire_in: number }> {
  return apiCall(() =>
    apiClient.post<{ message: string; email: string; expire_in: number }>('/auth/send-verification-code', { email })
  )
}

// 对象式导出（保持向后兼容）
export const authApi = {
  login,
  register,
  logout,
  getProfile,
  updateProfile,
  getLoginLogs,
  changePassword,
  sendVerificationCode,
}
