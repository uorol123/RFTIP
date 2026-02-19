import apiClient from './client'
import { apiCall } from './client'
import type {
  ApiResponse,
  User,
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  LoginLog,
  UploadAvatarResponse,
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

export async function updateProfile(data: {
  full_name?: string
  phone?: string
  avatar?: File
}): Promise<User> {
  const formData = new FormData()
  if (data.full_name !== undefined) formData.append('full_name', data.full_name)
  if (data.phone !== undefined) formData.append('phone', data.phone)
  if (data.avatar !== undefined) formData.append('avatar', data.avatar)

  return apiCall(() =>
    apiClient.put<User>('/auth/profile', formData)
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

// 上传临时头像（注册时使用）
export async function uploadTempAvatar(file: File): Promise<{ temp_token: string; message: string }> {
  const formData = new FormData()
  formData.append('avatar', file)

  return apiCall(() =>
    apiClient.post<{ temp_token: string; message: string }>('/auth/upload-temp-avatar', formData)
  )
}

// 上传头像（登录后使用）
export async function uploadAvatar(file: File): Promise<UploadAvatarResponse> {
  const formData = new FormData()
  formData.append('avatar', file)

  return apiCall(() =>
    apiClient.post<UploadAvatarResponse>('/auth/upload-avatar', formData)
  )
}

// 获取用户头像图片
export async function getUserAvatar(userId: number): Promise<Blob> {
  return apiCall(() =>
    apiClient.get<Blob>(`/auth/avatar/${userId}`, {
      responseType: 'blob',
    })
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
  uploadAvatar,
  getUserAvatar,
}
