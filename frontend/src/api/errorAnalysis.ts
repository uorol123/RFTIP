/**
 * 误差分析 API
 * 算法：基于梯度下降的迭代寻优算法
 * Base Path: /api/error-analysis
 */

import { apiCall } from './client'
import apiClient from './client'
import type {
  ErrorAnalysisConfig,
  ErrorAnalysisTask,
  TaskListResponse,
  ErrorAnalysisResult,
  TrackSegment,
  MatchGroup,
  ChartDataResponse,
  TaskDetailResponse,
} from '@/types/errorAnalysis'

// 导出类型以供 store 使用
export type {
  ErrorAnalysisConfig,
  ErrorAnalysisTask,
  TaskListResponse,
  ErrorAnalysisResult,
  TrackSegment,
  MatchGroup,
  ChartDataResponse,
  TaskDetailResponse,
}

// ========== 新版 API 请求/响应类型 ==========

/**
 * 雷达站信息
 */
export interface RadarStationInfo {
  id: number
  station_id: string
  latitude: number
  longitude: number
  altitude: number | null
  description: string | null
}

/**
 * 轨迹信息
 */
export interface TrackInfo {
  batch_id: string
  point_count: number
  start_time: string
  end_time: string
}

/**
 * 时间范围
 */
export interface TimeRange {
  start_time: string
  end_time: string
}

/**
 * 创建分析任务请求 (新版本)
 */
export interface CreateAnalysisRequest {
  radar_station_ids: number[]
  track_ids: string[]
  start_time?: string
  end_time?: string
  algorithm: string  // 算法名称
  config?: Partial<ErrorAnalysisConfig>
}

// ========== 旧版兼容类型 (保留用于迁移) ==========

export interface LegacyCreateAnalysisRequest {
  trajectory_file_id: number
  radar_station_file_id: number
  config?: Partial<ErrorAnalysisConfig>
}

export interface TaskListParams {
  skip?: number
  limit?: number
  status?: string
}

export interface MatchGroupParams {
  segment_id?: number
  skip?: number
  limit?: number
}

// ========== 1. 创建分析任务 (新版) ==========

/**
 * 创建误差分析任务
 * @param request - 分析请求参数
 * @returns 创建的任务信息
 */
export async function createAnalysis(request: CreateAnalysisRequest): Promise<ErrorAnalysisTask> {
  return apiCall(() =>
    apiClient.post<ErrorAnalysisTask>('/error-analysis/analyze', request)
  )
}

// ========== 2. 获取默认配置 ==========

/**
 * 获取默认配置
 * @returns 默认配置
 */
export async function getDefaultConfig(): Promise<ErrorAnalysisConfig> {
  return apiCall(() =>
    apiClient.get<ErrorAnalysisConfig>('/error-analysis/config')
  )
}

// ========== 3. 获取任务列表 ==========

/**
 * 获取任务列表
 * @param params - 查询参数
 * @returns 任务列表
 */
export async function getTaskList(params?: TaskListParams): Promise<TaskListResponse> {
  return apiCall(() =>
    apiClient.get<TaskListResponse>('/error-analysis/tasks', { params })
  )
}

// ========== 4. 获取任务详情 ==========

/**
 * 获取任务详情
 * @param taskId - 任务 ID (UUID字符串)
 * @returns 任务详情
 */
export async function getTaskDetail(taskId: string): Promise<ErrorAnalysisTask> {
  return apiCall(() =>
    apiClient.get<ErrorAnalysisTask>(`/error-analysis/tasks/${taskId}`)
  )
}

// ========== 5. 获取分析结果 ==========

/**
 * 获取分析结果
 * @param taskId - 任务 ID (UUID字符串)
 * @returns 分析结果
 */
export async function getAnalysisResult(taskId: string): Promise<ErrorAnalysisResult> {
  return apiCall(() =>
    apiClient.get<ErrorAnalysisResult>(`/error-analysis/tasks/${taskId}/results`)
  )
}

// ========== 6. 获取轨迹段列表 ==========

/**
 * 获取轨迹段列表
 * @param taskId - 任务 ID (UUID字符串)
 * @returns 轨迹段列表
 */
export async function getSegments(taskId: string): Promise<TrackSegment[]> {
  return apiCall(() =>
    apiClient.get<TrackSegment[]>(`/error-analysis/tasks/${taskId}/segments`)
  )
}

// ========== 7. 获取匹配组列表 ==========

/**
 * 获取匹配组列表
 * @param taskId - 任务 ID (UUID字符串)
 * @param params - 查询参数
 * @returns 匹配组列表
 */
export async function getMatchGroups(
  taskId: string,
  params?: MatchGroupParams
): Promise<MatchGroup[]> {
  return apiCall(() =>
    apiClient.get<MatchGroup[]>(`/error-analysis/tasks/${taskId}/matches`, { params })
  )
}

// ========== 8. 获取图表数据 ==========

/**
 * 获取图表数据
 * @param taskId - 任务 ID
 * @returns 图表数据
 */
export async function getChartData(taskId: string): Promise<ChartDataResponse> {
  return apiCall(() =>
    apiClient.get<ChartDataResponse>(`/error-analysis/tasks/${taskId}/chart`)
  )
}

// ========== 9. 数据查询 API (新版工作流) ==========

/**
 * 获取所有雷达站列表
 * @returns 雷达站列表
 */
export async function getRadarStations(): Promise<RadarStationInfo[]> {
  return apiCall(() =>
    apiClient.get<RadarStationInfo[]>('/error-analysis/radar-stations')
  )
}

/**
 * 获取某雷达站观测的所有轨迹
 * @param stationId - 雷达站ID
 * @returns 轨迹列表
 */
export async function getRadarStationTracks(stationId: number): Promise<TrackInfo[]> {
  return apiCall(() =>
    apiClient.get<TrackInfo[]>(`/error-analysis/radar-stations/${stationId}/tracks`)
  )
}

/**
 * 获取指定轨迹的时间范围
 * @param batchIds - 逗号分隔的轨迹批号列表
 * @returns 时间范围
 */
export async function getTracksTimeRange(batchIds: string): Promise<TimeRange> {
  return apiCall(() =>
    apiClient.get<TimeRange>('/error-analysis/tracks/time-range', { params: { batch_ids: batchIds } })
  )
}

/**
 * 获取多个雷达站共同观测到的轨迹
 * @param stationIds - 逗号分隔的雷达站ID列表
 * @returns 共同轨迹列表
 */
export async function getCommonTracks(stationIds: string): Promise<TrackInfo[]> {
  return apiCall(() =>
    apiClient.get<TrackInfo[]>('/error-analysis/common-tracks', { params: { station_ids: stationIds } })
  )
}

// ========== 10. 获取完整任务详情 ==========

/**
 * 获取完整任务详情
 * @param taskId - 任务 ID (UUID)
 * @param includeIntermediate - 是否包含中间步骤详细数据
 * @param includePoints - 是否包含插值点明细
 * @returns 完整任务详情
 */
export async function getTaskDetailFull(
  taskId: string,
  includeIntermediate = true,
  includePoints = false
): Promise<TaskDetailResponse> {
  return apiCall(() =>
    apiClient.get<TaskDetailResponse>(
      `/error-analysis/tasks/${taskId}/detail`,
      { params: { include_intermediate: includeIntermediate, include_points: includePoints } }
    )
  )
}

// ========== 导出 ==========

// 对象式导出（方便使用）
export const errorAnalysisApi = {
  createAnalysis,
  getDefaultConfig,
  getTaskList,
  getTaskDetail,
  getAnalysisResult,
  getSegments,
  getMatchGroups,
  getChartData,
  // 新版数据查询 API
  getRadarStations,
  getRadarStationTracks,
  getTracksTimeRange,
  getCommonTracks,
  // 任务详情
  getTaskDetailFull,
}
