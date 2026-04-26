/**
 * 误差分析类型定义
 * 算法：基于梯度下降的迭代寻优算法
 *
 * 与后端 API 模型对应 - 新版工作流
 */

// ========== 代价函数权重 ==========

/**
 * 代价函数权重配置
 */
export interface CostWeights {
  variance: number
  azimuth: number
  range: number
  elevation: number
}

// ========== 配置类型 ==========

/**
 * 误差分析配置 (基于梯度下降的迭代寻优算法参数)
 */
export interface ErrorAnalysisConfig {
  // 网格与时间参数
  grid_resolution: number  // 网格分辨率（度），默认 0.2
  time_window: number  // 时间窗口长度（秒），默认 60
  match_distance_threshold: number  // 匹配距离阈值（度），默认 0.12
  min_track_points: number  // 最小航迹点数，默认 10

  // 优化参数
  optimization_steps: number[]  // 方位角优化步长序列，默认 [0.1, 0.01]
  range_optimization_steps: number[]  // 距离优化步长序列，默认 [1000, 800, 500, 300, 200, 100, 50, 20, 10]

  // 代价函数权重
  cost_weights: CostWeights

  // 最大匹配组数
  max_match_groups: number  // 默认 15000
}

/**
 * 默认配置 (与原项目参数一致)
 */
export const DEFAULT_ERROR_ANALYSIS_CONFIG: ErrorAnalysisConfig = {
  grid_resolution: 0.2,
  time_window: 60,
  match_distance_threshold: 0.12,
  min_track_points: 10,
  optimization_steps: [0.1, 0.01],
  range_optimization_steps: [1000, 800, 500, 300, 200, 100, 50, 20, 10],
  cost_weights: {
    variance: 100.0,
    azimuth: 0.15,
    range: 6e-7,
    elevation: 0.1,
  },
  max_match_groups: 15000,
}

/**
 * 预设配置方案
 */
export type PresetProfile = 'standard' | 'high_precision' | 'fast' | 'coarse'

export const PRESET_PROFILES: Record<PresetProfile, ErrorAnalysisConfig> = {
  /**
   * 标准配置 - 平衡精度与速度
   * 与原项目默认参数一致
   */
  standard: {
    grid_resolution: 0.2,
    time_window: 60,
    match_distance_threshold: 0.12,
    min_track_points: 10,
    optimization_steps: [0.1, 0.01],
    range_optimization_steps: [1000, 800, 500, 300, 200, 100, 50, 20, 10],
    cost_weights: {
      variance: 100.0,
      azimuth: 0.15,
      range: 6e-7,
      elevation: 0.1,
    },
    max_match_groups: 15000,
  },
  /**
   * 高精度配置 - 适用于需要精细误差分析的场景
   * 更小的网格、更严格的时间窗口、更多优化迭代
   */
  high_precision: {
    grid_resolution: 0.1,
    time_window: 30,
    match_distance_threshold: 0.08,
    min_track_points: 15,
    optimization_steps: [0.05, 0.01, 0.005],
    range_optimization_steps: [500, 300, 200, 100, 50, 20, 10, 5],
    cost_weights: {
      variance: 150.0,
      azimuth: 0.2,
      range: 8e-7,
      elevation: 0.15,
    },
    max_match_groups: 20000,
  },
  /**
   * 快速分析配置 - 适用于大数据量的初步筛选
   * 更大的网格、更宽松的阈值
   */
  fast: {
    grid_resolution: 0.5,
    time_window: 120,
    match_distance_threshold: 0.25,
    min_track_points: 5,
    optimization_steps: [0.2, 0.05],
    range_optimization_steps: [2000, 1000, 500, 200, 100],
    cost_weights: {
      variance: 80.0,
      azimuth: 0.1,
      range: 5e-7,
      elevation: 0.08,
    },
    max_match_groups: 10000,
  },
  /**
   * 粗粒度配置 - 适用于低分辨率数据或大范围分析
   */
  coarse: {
    grid_resolution: 1.0,
    time_window: 180,
    match_distance_threshold: 0.5,
    min_track_points: 8,
    optimization_steps: [0.3, 0.1],
    range_optimization_steps: [3000, 1500, 800, 400],
    cost_weights: {
      variance: 60.0,
      azimuth: 0.08,
      range: 4e-7,
      elevation: 0.05,
    },
    max_match_groups: 8000,
  },
}

// ========== 任务状态 ==========

/**
 * 任务状态枚举
 */
export type TaskStatus = 'pending' | 'extracting' | 'interpolating' | 'matching' | 'calculating' | 'completed' | 'failed'

/**
 * 任务状态显示信息
 */
export const TASK_STATUS_INFO: Record<TaskStatus, { label: string; color: string }> = {
  pending: { label: '等待中', color: '#9ca3af' },
  extracting: { label: '提取航迹', color: '#3b82f6' },
  interpolating: { label: '航迹插值', color: '#8b5cf6' },
  matching: { label: '航迹匹配', color: '#f59e0b' },
  calculating: { label: '计算误差', color: '#10b981' },
  completed: { label: '已完成', color: '#10b981' },
  failed: { label: '失败', color: '#ef4444' },
}

// ========== 任务类型 ==========

/**
 * 分析任务
 */
export interface ErrorAnalysisTask {
  id: number
  task_id: string
  radar_station_ids: string[]  // 雷达站站号（用于显示）
  track_ids: string[]
  user_id: number
  status: TaskStatus
  progress: number
  error_message?: string
  created_at: string
  started_at?: string
  completed_at?: string
}

/**
 * 任务列表响应
 */
export interface TaskListResponse {
  tasks: ErrorAnalysisTask[]
  total: number
  page: number
  limit: number
}

// ========== 结果类型 ==========

/**
 * 匹配点
 */
export interface MatchPoint {
  station_id: number
  point_id: number | null
  longitude: number
  latitude: number
  altitude: number | null
}

/**
 * 匹配组
 */
export interface MatchGroup {
  id: number
  group_id: number
  match_time: string
  match_points: MatchPoint[]
  point_count: number
  avg_distance: number | null
  max_distance: number | null
  variance: number | null
}

/**
 * 匹配统计
 */
export interface MatchStatistics {
  total_groups: number
  group_size_avg: number
  group_size_std: number
  distance_avg: number
  distance_std: number
  min_group_size: number
  max_group_size: number
}

/**
 * 航迹段
 */
export interface TrackSegment {
  id: number
  segment_id: number
  station_id: number
  track_id: number
  start_time: string
  end_time: string
  point_count: number
  start_point_index: number | null
  end_point_index: number | null
}

/**
 * 雷达站误差结果
 */
export interface ErrorResult {
  id: number
  station_id: number
  azimuth_error: number
  range_error: number
  elevation_error: number
  match_count: number
  confidence: number | null
  iterations: number | null
  final_cost: number | null
}

/**
 * 误差分析摘要
 */
export interface ErrorAnalysisSummary {
  total_stations: number
  total_matches: number
  processing_time: number
  segments_extracted: number
}

/**
 * 完整分析结果
 */
export interface ErrorAnalysisResult {
  task_id: string
  status: TaskStatus
  summary: ErrorAnalysisSummary
  errors: ErrorResult[]
  match_statistics: MatchStatistics
  config: ErrorAnalysisConfig
}

// ========== 图表数据类型 ==========

/**
 * 图表数据响应
 */
export interface ChartDataResponse {
  stations: string[]
  azimuth_errors: number[]
  range_errors: number[]
  elevation_errors: number[]
  confidences: number[]
  match_counts: number[]
  group_size_distribution: Record<string, number>
}

// ========== API 请求/响应类型 ==========

/**
 * 创建分析任务请求
 */
export interface CreateAnalysisRequest {
  radar_station_ids: number[]
  track_ids: string[]
  start_time?: string
  end_time?: string
  config?: Partial<ErrorAnalysisConfig>
}

/**
 * 获取任务列表参数
 */
export interface TaskListParams {
  skip?: number
  limit?: number
  status?: TaskStatus
}

/**
 * 获取匹配组参数
 */
export interface MatchGroupParams {
  segment_id?: number
  skip?: number
  limit?: number
}

/**
 * 雷达站信息 (用于数据查询)
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
 * 轨迹信息 (用于数据查询)
 */
export interface TrackInfo {
  batch_id: string
  point_count: number
  start_time: string
  end_time: string
}

/**
 * 时间范围 (用于数据查询)
 */
export interface TimeRange {
  start_time: string
  end_time: string
}

// ========== 段类型 (兼容旧版) ==========

/**
 * 轨迹段 (兼容旧版)
 */
export interface TrajectorySegment {
  segment_id: number
  start_index: number
  end_index: number
  start_time: string
  end_time: string
  point_count: number
  duration_seconds: number
  bbox: {
    min_lat: number
    max_lat: number
    min_lon: number
    max_lon: number
  }
}

/**
 * 段列表响应 (兼容旧版)
 */
export interface SegmentListResponse {
  total: number
  segments: TrajectorySegment[]
}

/**
 * 匹配组 (兼容旧版)
 */
export interface MatchGroupLegacy {
  group_id: number
  segment_id: number
  timestamp: string
  trajectory_point: {
    longitude: number
    latitude: number
    altitude: number
  }
  matches: MatchedPoint[]
  best_match: MatchedPoint
  avg_error: number
  match_count: number
}

/**
 * 匹配点 (兼容旧版)
 */
export interface MatchedPoint {
  trajectory_index: number
  radar_station_id: string
  radar_index: number
  trajectory_point: {
    longitude: number
    latitude: number
    altitude: number
    timestamp: string
  }
  radar_point: {
    longitude: number
    latitude: number
    altitude: number
    timestamp: string
  }
  time_diff: number
  distance: number
  horizontal_error: number
  vertical_error: number
  is_outlier: boolean
}

/**
 * 匹配组列表响应 (兼容旧版)
 */
export interface MatchGroupListResponse {
  total: number
  page: number
  page_size: number
  matches: MatchGroupLegacy[]
}

// ========== 历史任务详情类型 ==========

/**
 * 插值点
 */
export interface InterpolatedPoint {
  id: number
  station_id: number
  track_id: number
  time_seconds: number
  timestamp: string | null
  longitude: number
  latitude: number
  altitude: number | null
  is_original: boolean
}

/**
 * 航迹段详情
 */
export interface TrackSegmentDetail {
  id: number
  segment_id: number
  station_id: number
  track_id: number
  start_time: string
  end_time: string
  point_count: number
  start_point_index: number | null
  end_point_index: number | null
  duration_seconds: number
  station_name: string
}

/**
 * 匹配组详情
 */
export interface MatchGroupDetail {
  id: number
  group_id: number
  match_time: string
  match_points: MatchPoint[]
  point_count: number
  avg_distance: number | null
  max_distance: number | null
  variance: number | null
  station_ids: number[]
  time_difference_ms: number
}

/**
 * 误差结果详情
 */
export interface ErrorResultDetail {
  id: number
  station_id: number
  station_name: string
  azimuth_error: number
  range_error: number
  elevation_error: number
  match_count: number
  confidence: number | null
  iterations: number | null
  final_cost: number | null
  azimuth_quality: 'excellent' | 'good' | 'fair' | 'poor' | 'unknown'
  range_quality: 'excellent' | 'good' | 'fair' | 'poor' | 'unknown'
  elevation_quality: 'excellent' | 'good' | 'fair' | 'poor' | 'unknown'
}

/**
 * 插值汇总信息
 */
export interface InterpolationSummary {
  total_points: number
  original_points: number
  interpolated_points: number
  stations: Record<string, number>
}

/**
 * 流程步骤信息
 */
export interface ProcessStep {
  step_id: 'extracting' | 'interpolating' | 'matching' | 'calculating'
  step_name: string
  step_description: string
  status: 'pending' | 'running' | 'completed' | 'skipped' | 'failed'
  duration_seconds: number | null
  data_summary: Record<string, unknown>
}

/**
 * 完整任务详情响应
 */
export interface TaskDetailResponse {
  task_id: string
  status: TaskStatus
  progress: number
  error_message: string | null
  created_at: string
  started_at: string | null
  completed_at: string | null
  config: ErrorAnalysisConfig
  radar_station_ids: number[]
  track_ids: string[]
  process_steps: ProcessStep[]
  segments_summary: Record<string, unknown>
  interpolation_summary: InterpolationSummary | null
  match_summary: Record<string, unknown>
  segments: TrackSegmentDetail[]
  interpolated_points: InterpolatedPoint[]
  match_groups: MatchGroupDetail[]
  error_results: ErrorResultDetail[]
  processing_time_seconds: number
  total_segments: number
  total_match_groups: number
  total_interpolated_points: number
}
