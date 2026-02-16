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

// 函数式导出
export async function create(data: CreateZoneRequest): Promise<NoFlyZone> {
  return apiCall(() =>
    apiClient.post<NoFlyZone>('/zones/', data)
  )
}

export async function list(params?: PaginationParams & {
  is_active?: boolean
  zone_type?: 'circle' | 'polygon'
}): Promise<PaginatedResponse<NoFlyZone>> {
  return apiCall(() =>
    apiClient.get<PaginatedResponse<NoFlyZone>>('/zones/', { params })
  )
}

export async function get(zoneId: number): Promise<NoFlyZone> {
  return apiCall(() =>
    apiClient.get<NoFlyZone>(`/zones/${zoneId}`)
  )
}

export async function update(zoneId: number, data: Partial<CreateZoneRequest>): Promise<NoFlyZone> {
  return apiCall(() =>
    apiClient.put<NoFlyZone>(`/zones/${zoneId}`, data)
  )
}

export async function deleteZone(zoneId: number): Promise<void> {
  return apiCall(() =>
    apiClient.delete<void>(`/zones/${zoneId}`)
  )
}

// 直接导出 delete 函数（与视图文件中的使用一致）
export { deleteZone as delete }

export async function detectIntrusions(params?: {
  file_id?: number
  track_id?: string
  start_time?: string
  end_time?: string
}): Promise<IntrusionDetection> {
  return apiCall(() =>
    apiClient.post<IntrusionDetection>('/zones/detect-intrusions', params)
  )
}

export async function getIntrusions(params?: PaginationParams & {
  zone_id?: number
  track_id?: string
  start_time?: string
  end_time?: string
}): Promise<PaginatedResponse<Intrusion>> {
  return apiCall(() =>
    apiClient.get<PaginatedResponse<Intrusion>>('/zones/intrusions/list', { params })
  )
}

export async function toggleActive(zoneId: number, isActive: boolean): Promise<NoFlyZone> {
  return apiCall(() =>
    apiClient.patch<NoFlyZone>(`/zones/${zoneId}/toggle`, { is_active: isActive })
  )
}

// 对象式导出（保持向后兼容）
export const zonesApi = {
  create,
  list,
  get,
  update,
  delete: deleteZone, // 避免与关键字冲突
  detectIntrusions,
  getIntrusions,
  toggleActive,
}
