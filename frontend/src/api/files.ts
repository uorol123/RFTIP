import apiClient from './client'
import { apiCall } from './client'
import type {
  ApiResponse,
  DataFile,
  PaginatedResponse,
  PaginationParams,
  FileUploadResponse,
  FileProcessRequest,
} from './types'

// 函数式导出
export async function upload(file: File, isPublic: boolean = false): Promise<FileUploadResponse> {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('is_public', isPublic.toString())

  return apiCall(() =>
    apiClient.post<FileUploadResponse>('/files/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  )
}

export async function list(params?: PaginationParams & {
  status?: string
  is_public?: boolean
  search?: string
}): Promise<PaginatedResponse<DataFile>> {
  return apiCall(() =>
    apiClient.get<PaginatedResponse<DataFile>>('/files/', { params })
  )
}

export async function get(fileId: number): Promise<DataFile> {
  return apiCall(() =>
    apiClient.get<DataFile>(`/files/${fileId}`)
  )
}

export async function deleteFile(fileId: number): Promise<void> {
  return apiCall(() =>
    apiClient.delete<void>(`/files/${fileId}`)
  )
}

// 直接导出 delete 函数（与视图文件中的使用一致）
export { deleteFile as delete }

export async function process(fileId: number, options?: FileProcessRequest): Promise<{ task_id: string }> {
  return apiCall(() =>
    apiClient.post<{ task_id: string }>(`/files/${fileId}/process`, options)
  )
}

export async function updateVisibility(fileId: number, isPublic: boolean): Promise<DataFile> {
  return apiCall(() =>
    apiClient.put<DataFile>(`/files/${fileId}`, { is_public: isPublic })
  )
}

export async function getStatus(fileId: number): Promise<{ status: string; progress: number }> {
  return apiCall(() =>
    apiClient.get<{ status: string; progress: number }>(`/files/${fileId}/status`)
  )
}

// 对象式导出（保持向后兼容）
export const filesApi = {
  upload,
  list,
  get,
  delete: deleteFile, // 避免与关键字冲突
  process,
  updateVisibility,
  getStatus,
}
