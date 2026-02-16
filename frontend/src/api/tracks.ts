import apiClient from './client'
import { apiCall } from './client'
import type {
  Track,
  TrackPoint,
  TrackSummary,
  TrackProcessRequest,
  TrackProcessResponse,
  PaginationParams,
} from './types'

// 函数式导出
export async function process(data: TrackProcessRequest): Promise<TrackProcessResponse> {
  return apiCall(() =>
    apiClient.post<TrackProcessResponse>('/tracks/process', data)
  )
}

export async function getRaw(params: {
  file_id: number
  track_id?: string
  limit?: number
  offset?: number
}): Promise<Track[]> {
  return apiCall(() =>
    apiClient.get<Track[]>('/tracks/raw', { params })
  )
}

export async function getCorrected(params: {
  file_id: number
  track_id?: string
  limit?: number
  offset?: number
}): Promise<Track[]> {
  return apiCall(() =>
    apiClient.get<Track[]>('/tracks/corrected', { params })
  )
}

export async function getSummary(fileId: number): Promise<TrackSummary> {
  return apiCall(() =>
    apiClient.get<TrackSummary>(`/tracks/summary?file_id=${fileId}`)
  )
}

export async function getTrack(trackId: string, file_id: number): Promise<Track> {
  return apiCall(() =>
    apiClient.get<Track>(`/tracks/${trackId}?file_id=${file_id}`)
  )
}

export async function getPoints(params: {
  track_id: string
  file_id: number
  corrected?: boolean
  start_time?: string
  end_time?: string
}): Promise<TrackPoint[]> {
  return apiCall(() =>
    apiClient.get<TrackPoint[]>('/tracks/points', { params })
  )
}

export async function getTaskStatus(taskId: string): Promise<{
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress: number
  result?: any
  error?: string
}> {
  return apiCall(() =>
    apiClient.get(`/tracks/tasks/${taskId}`)
  )
}

// 对象式导出（保持向后兼容）
export const tracksApi = {
  process,
  getRaw,
  getCorrected,
  getSummary,
  getTrack,
  getPoints,
  getTaskStatus,
}
