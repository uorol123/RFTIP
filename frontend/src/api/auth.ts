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
  const formData = new FormData()
  formData.append('username', data.username)
  formData.append('password', data.password)

  return apiCall(() =>
    apiClient.post<LoginResponse>('/auth/login', formData)
  )
}

export async function register(data: RegisterRequest): Promise<User> {
  return apiCall(() =>
    apiClient.post<User>('/auth/register', data)
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

// 上传临时头像
export async function uploadTempAvatar(file: File): Promise<{ temp_token: string; message: string }> {
  const formData = new FormData()
  formData.append('avatar', file)

  return apiCall(() =>
    apiClient.post<{ temp_token: string; message: string }>('/auth/upload-temp-avatar', formData)
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
  update: updateProfile,
  getLoginLogs,
  changePassword,
  sendVerificationCode,
  uploadTempAvatar,
}
