import apiClient from './client'
import { apiCall } from './client'
import type {
  NoFlyZone,
  CreateZoneRequest,
  Intrusion,
  IntrusionDetection,
  PaginatedResponse,
  PaginationParams,
} from './types'

export const zonesApi = {
  /**
   * Create a new no-fly zone
   */
  create: async (data: CreateZoneRequest): Promise<NoFlyZone> => {
    return apiCall(() =>
      apiClient.post<NoFlyZone>('/zones/', data)
    )
  },

  /**
   * Get list of no-fly zones
   */
  list: async (params?: PaginationParams & {
    is_active?: boolean
    zone_type?: 'circle' | 'polygon'
  }): Promise<PaginatedResponse<NoFlyZone>> => {
    return apiCall(() =>
      apiClient.get<PaginatedResponse<NoFlyZone>>('/zones/', { params })
    )
  },

  /**
   * Get zone details
   */
  get: async (zoneId: number): Promise<NoFlyZone> => {
    return apiCall(() =>
      apiClient.get<NoFlyZone>(`/zones/${zoneId}`)
    )
  },

  /**
   * Update a zone
   */
  update: async (zoneId: number, data: Partial<CreateZoneRequest>): Promise<NoFlyZone> => {
    return apiCall(() =>
      apiClient.put<NoFlyZone>(`/zones/${zoneId}`, data)
    )
  },

  /**
   * Delete a zone
   */
  delete: async (zoneId: number): Promise<void> => {
    return apiCall(() =>
      apiClient.delete<void>(`/zones/${zoneId}`)
    )
  },

  /**
   * Detect intrusions
   */
  detectIntrusions: async (params?: {
    file_id?: number
    track_id?: string
    start_time?: string
    end_time?: string
  }): Promise<IntrusionDetection> => {
    return apiCall(() =>
      apiClient.post<IntrusionDetection>('/zones/detect-intrusions', params)
    )
  },

  /**
   * Get intrusion records
   */
  getIntrusions: async (params?: PaginationParams & {
    zone_id?: number
    track_id?: string
    start_time?: string
    end_time?: string
  }): Promise<PaginatedResponse<Intrusion>> => {
    return apiCall(() =>
      apiClient.get<PaginatedResponse<Intrusion>>('/zones/intrusions/list', { params })
    )
  },

  /**
   * Toggle zone active status
   */
  toggleActive: async (zoneId: number, isActive: boolean): Promise<NoFlyZone> => {
    return apiCall(() =>
      apiClient.patch<NoFlyZone>(`/zones/${zoneId}/toggle`, { is_active: isActive })
    )
  },
}
