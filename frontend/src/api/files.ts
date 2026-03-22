/**
 * 文件管理模块 API
 * Base Path: /api/files
 *
 * API 规范参考: express.md Section 2
 */

import { apiCall } from './client'
import apiClient from './client'
import type {
  FileUploadResponse,
  BatchUploadResponse,
  ShareFileRequest,
  ShareFileResponse,
  FileListResponse,
  FileListParams,
  FileStatusResponse,
  FileDetailResponse,
  FileCategory,
  WsMessage,
} from './types'

// ========== 2.1 上传数据文件（单个） ==========

/**
 * 上传单个数据文件
 * @param file - 要上传的文件（CSV 或 Excel）
 * @param category - 文件分类，默认为 'trajectory'
 * @returns 上传响应，包含 file_id, filename, status 等信息
 */
export async function uploadFile(
  file: File,
  category: FileCategory = 'trajectory'
): Promise<FileUploadResponse> {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('category', category)

  return apiCall(() =>
    apiClient.post<FileUploadResponse>('/files/upload', formData)
  )
}

// ========== 2.2 批量上传数据文件 ==========

/**
 * 批量上传数据文件
 * @param files - 要上传的文件数组（最多 10 个）
 * @param category - 文件分类，默认为 'trajectory'
 * @returns 批量上传响应，包含 task_id 和所有文件的状态
 */
export async function uploadFilesBatch(
  files: File[],
  category: FileCategory = 'trajectory'
): Promise<BatchUploadResponse> {
  const formData = new FormData()
  files.forEach((file) => {
    formData.append('files', file)
  })
  formData.append('category', category)

  return apiCall(() =>
    apiClient.post<BatchUploadResponse>('/files/upload-batch', formData)
  )
}

// ========== 2.3 生成文件分享链接 ==========

/**
 * 生成文件分享链接
 * @param fileId - 文件ID
 * @param options - 分享选项（过期时间、密码、最大下载次数）
 * @returns 分享链接信息，包含 share_token, share_url, qr_code
 */
export async function shareFile(
  fileId: number,
  options: ShareFileRequest = {}
): Promise<ShareFileResponse> {
  return apiCall(() =>
    apiClient.post<ShareFileResponse>(`/files/${fileId}/share`, options)
  )
}

// ========== 2.4 访问分享文件 ==========

/**
 * 访问分享的文件（下载）
 * @param shareToken - 分享令牌
 * @param password - 访问密码（如果需要）
 * @returns 文件内容（Blob）
 */
export async function getSharedFile(
  shareToken: string,
  password?: string
): Promise<Blob> {
  const headers: Record<string, string> = {}
  if (password) {
    headers['X-Share-Password'] = password
  }

  return apiCall(() =>
    apiClient.get<Blob>(`/files/share/${shareToken}`, {
      headers,
      responseType: 'blob',
    })
  )
}

// ========== 2.5 获取文件列表 ==========

/**
 * 获取文件列表
 * @param params - 查询参数（分页、筛选、搜索）
 * @returns 文件列表响应，包含 total 和 files 数组
 */
export async function getFileList(params?: FileListParams): Promise<FileListResponse> {
  return apiCall(() =>
    apiClient.get<FileListResponse>('/files/', { params })
  )
}

// ========== 2.6 获取文件处理状态（实时） ==========

/**
 * 获取文件处理状态（实时进度）
 * @param fileId - 文件ID
 * @returns 文件处理状态，包含 progress, stage, message 等
 */
export async function getFileStatus(fileId: number): Promise<FileStatusResponse> {
  return apiCall(() =>
    apiClient.get<FileStatusResponse>(`/files/${fileId}/status`)
  )
}

// ========== 2.7 获取文件详情 ==========

/**
 * 获取文件详情
 * @param fileId - 文件ID
 * @returns 文件详细信息，包含分享信息等
 */
export async function getFileDetail(fileId: number): Promise<FileDetailResponse> {
  return apiCall(() =>
    apiClient.get<FileDetailResponse>(`/files/${fileId}`)
  )
}

// ========== 2.8 删除文件 ==========

/**
 * 删除文件
 * @param fileId - 文件ID
 */
export async function deleteFile(fileId: number): Promise<void> {
  return apiCall(() =>
    apiClient.delete<void>(`/files/${fileId}`)
  )
}

// ========== 2.9 取消分享链接 ==========

/**
 * 取消文件分享链接
 * @param fileId - 文件ID
 */
export async function cancelShare(fileId: number): Promise<void> {
  return apiCall(() =>
    apiClient.delete<void>(`/files/${fileId}/share`)
  )
}

// ========== 2.10 文件处理 WebSocket ==========

/**
 * 创建文件处理进度 WebSocket 连接
 * @param fileId - 文件ID
 * @param token - JWT access token
 * @param callbacks - 回调函数
 * @returns WebSocket 实例
 *
 * @example
 * const ws = createFileProgressWebSocket(fileId, token, {
 *   onProgress: (data) => console.log('Progress:', data.progress),
 *   onCompleted: (data) => console.log('Completed!'),
 *   onError: (error) => console.error('Error:', error),
 * })
 *
 * // 关闭连接
 * ws.close()
 */
export function createFileProgressWebSocket(
  fileId: number,
  token: string,
  callbacks: FileProgressCallbacks
): WebSocket {
  const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const wsHost = import.meta.env.VITE_WS_BASE_URL
    ? import.meta.env.VITE_WS_BASE_URL.replace(/^https?:\/\//, '').replace(/^ws:\/\//, '')
    : window.location.host
  const wsUrl = `${wsProtocol}//${wsHost}/api/ws/files/${fileId}?token=${token}`
  const ws = new WebSocket(wsUrl)

  // 跟踪连接是否被手动关闭
  let manuallyClosed = false

  ws.onopen = () => {
    console.log(`[WS] Connected to file ${fileId}`)
    // 发送心跳
    const heartbeatInterval = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'ping' }))
      } else {
        clearInterval(heartbeatInterval)
      }
    }, 30000) // 每30秒发送一次心跳
  }

  ws.onmessage = (event) => {
    try {
      const message: WsMessage = JSON.parse(event.data)

      switch (message.type) {
        case 'progress':
          callbacks.onProgress?.(message.data as FileStatusResponse)
          break
        case 'completed':
          callbacks.onCompleted?.(message.data as FileStatusResponse)
          break
        case 'error':
          callbacks.onError?.(message.data.message || '处理失败')
          break
      }
    } catch (error) {
      console.error('Failed to parse WebSocket message:', error)
      callbacks.onError?.('消息解析失败')
    }
  }

  ws.onerror = (error) => {
    console.error('WebSocket error:', error)
    // 不再自动触发错误回调，让 onclose 处理
    // 只有在异常错误（非正常关闭）时才报错
  }

  ws.onclose = (event) => {
    console.log(`[WS] Closed for file ${fileId}, code: ${event.code}, wasClean: ${event.wasClean}`)
    // 清理心跳定时器
    clearInterval(heartbeatInterval)

    // 只有在非正常关闭且未手动关闭时才触发错误回调
    if (!event.wasClean && !manuallyClosed) {
      callbacks.onError?.('WebSocket 连接中断')
    }

    callbacks.onClose?.()
  }

  // 添加手动关闭方法
  const originalClose = ws.close.bind(ws)
  ws.close = () => {
    manuallyClosed = true
    originalClose()
  }

  return ws
}

// ========== 导出 ==========

// 函数式导出
export {
  deleteFile as delete, // 别名导出，避免与关键字冲突
}

// 对象式导出（方便使用）
export const filesApi = {
  uploadFile,
  uploadFilesBatch,
  shareFile,
  getSharedFile,
  getFileList,
  getFileStatus,
  getFileDetail,
  deleteFile,
  cancelShare,
  createFileProgressWebSocket,
}
