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

export const tracksApi = {
  /**
   * Process tracks from a file
   */
  process: async (data: TrackProcessRequest): Promise<TrackProcessResponse> => {
    return apiCall(() =>
      apiClient.post<TrackProcessResponse>('/tracks/process', data)
    )
  },

  /**
   * Get raw (original) tracks
   */
  getRaw: async (params: {
    file_id: number
    track_id?: string
    limit?: number
    offset?: number
  }): Promise<Track[]> => {
    return apiCall(() =>
      apiClient.get<Track[]>('/tracks/raw', { params })
    )
  },

  /**
   * Get corrected tracks
   */
  getCorrected: async (params: {
    file_id: number
    track_id?: string
    limit?: number
    offset?: number
  }): Promise<Track[]> => {
    return apiCall(() =>
      apiClient.get<Track[]>('/tracks/corrected', { params })
    )
  },

  /**
   * Get track summary
   */
  getSummary: async (fileId: number): Promise<TrackSummary> => {
    return apiCall(() =>
      apiClient.get<TrackSummary>(`/tracks/summary?file_id=${fileId}`)
    )
  },

  /**
   * Get specific track details
   */
  getTrack: async (trackId: string, file_id: number): Promise<Track> => {
    return apiCall(() =>
      apiClient.get<Track>(`/tracks/${trackId}?file_id=${file_id}`)
    )
  },

  /**
   * Get track points
   */
  getPoints: async (params: {
    track_id: string
    file_id: number
    corrected?: boolean
    start_time?: string
    end_time?: string
  }): Promise<TrackPoint[]> => {
    return apiCall(() =>
      apiClient.get<TrackPoint[]>('/tracks/points', { params })
    )
  },

  /**
   * Get processing task status
   */
  getTaskStatus: async (taskId: string): Promise<{
    status: 'pending' | 'processing' | 'completed' | 'failed'
    progress: number
    result?: any
    error?: string
  }> => {
    return apiCall(() =>
      apiClient.get(`/tracks/tasks/${taskId}`)
    )
  },
}
