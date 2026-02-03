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

export const filesApi = {
  /**
   * Upload a file (CSV/Excel)
   */
  upload: async (file: File, isPublic: boolean = false): Promise<FileUploadResponse> => {
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
  },

  /**
   * Get list of files
   */
  list: async (params?: PaginationParams & {
    status?: string
    is_public?: boolean
    search?: string
  }): Promise<PaginatedResponse<DataFile>> => {
    return apiCall(() =>
      apiClient.get<PaginatedResponse<DataFile>>('/files/', { params })
    )
  },

  /**
   * Get file details
   */
  get: async (fileId: number): Promise<DataFile> => {
    return apiCall(() =>
      apiClient.get<DataFile>(`/files/${fileId}`)
    )
  },

  /**
   * Delete a file
   */
  delete: async (fileId: number): Promise<void> => {
    return apiCall(() =>
      apiClient.delete<void>(`/files/${fileId}`)
    )
  },

  /**
   * Process a file
   */
  process: async (fileId: number, options?: FileProcessRequest): Promise<{ task_id: string }> => {
    return apiCall(() =>
      apiClient.post<{ task_id: string }>(`/files/${fileId}/process`, options)
    )
  },

  /**
   * Update file visibility
   */
  updateVisibility: async (fileId: number, isPublic: boolean): Promise<DataFile> => {
    return apiCall(() =>
      apiClient.put<DataFile>(`/files/${fileId}`, { is_public: isPublic })
    )
  },

  /**
   * Get file processing status
   */
  getStatus: async (fileId: number): Promise<{ status: string; progress: number }> => {
    return apiCall(() =>
      apiClient.get<{ status: string; progress: number }>(`/files/${fileId}/status`)
    )
  },
}
