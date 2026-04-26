/**
 * 误差分析算法类型定义
 * 支持多算法扩展架构
 */

// ========== 算法信息 ==========

/**
 * 算法信息
 */
export interface AlgorithmInfo {
  name: string                      // 算法唯一标识 (如: gradient_descent)
  version: string                   // 版本号
  display_name: string              // 显示名称
  description: string               // 描述
  supports_elevation: boolean       // 是否支持俯仰角误差计算
}

/**
 * 算法列表响应
 */
export interface AlgorithmsListResponse {
  algorithms: AlgorithmInfo[]
}

// ========== 配置 Schema ==========

/**
 * 算法配置 Schema (JSON Schema 格式)
 */
export interface AlgorithmConfigSchema {
  type: 'object'
  properties: Record<string, {
    type: string
    title: string
    description?: string
    default?: any
    minimum?: number
    maximum?: number
    enum?: any[]
    items?: any
    [key: string]: any
  }>
  required?: string[]
  additionalProperties?: boolean
}

// ========== 预设配置 ==========

/**
 * 预设配置
 */
export interface PresetConfig {
  name: string                      // 预设名称 (如: standard, high_precision)
  display_name: string               // 显示名称
  config: Record<string, any>        // 配置参数
}

/**
 * 算法预设配置响应
 */
export interface AlgorithmPresetsResponse {
  algorithm: string                 // 算法名称
  presets: PresetConfig[]           // 预设配置列表
}

// ========== 配置验证 ==========

/**
 * 配置验证响应
 */
export interface ConfigValidationResponse {
  valid: boolean                    // 是否有效
  errors?: string[]                 // 错误信息列表
}

// ========== 创建任务请求（新版本） ==========

/**
 * 创建分析任务请求 V2（支持算法选择）
 */
export interface CreateAnalysisRequestV2 {
  algorithm: string                 // 算法名称
  radar_station_ids: number[]       // 雷达站ID列表
  track_ids: string[]               // 轨迹ID列表
  start_time?: string               // 开始时间（可选）
  end_time?: string                 // 结束时间（可选）
  config?: Record<string, any>      // 算法特定配置（可选）
  preset_name?: string              // 使用预设配置名称（可选）
}

// ========== 代价函数权重 ==========

/**
 * 代价函数权重配置
 */
export interface CostWeights {
  variance: number                  // 方差权重
  azimuth_error_square: number      // 方位角误差平方项权重
  range_error_square: number        // 距离误差平方项权重
  elevation_error_square: number    // 俯仰角误差平方项权重
}

// ========== MRRA 算法特定配置 ==========

/**
 * MRRA 算法配置（基于梯度下降的迭代寻优算法）
 */
export interface MrraAlgorithmConfig {
  // 基础参数
  grid_resolution?: number          // 网格分辨率（度）
  time_window?: number              // 时间窗口（秒）
  time_window_ratio?: number        // 时间窗口比例
  match_distance_threshold?: number // 匹配距离阈值（度）

  // 航迹提取配置
  min_track_points?: number         // 最小航迹点数

  // 优化参数
  optimization_steps?: number[]     // 方位角优化步长序列
  range_optimization_steps?: number[] // 距离优化步长序列
  max_match_groups?: number         // 最大匹配组数

  // 代价函数权重
  cost_weights?: CostWeights        // 代价函数权重
}

/**
 * 默认 MRRA 配置
 */
export const DEFAULT_MRRA_CONFIG: MrraAlgorithmConfig = {
  grid_resolution: 0.2,
  time_window: 60,
  time_window_ratio: 0.75,
  match_distance_threshold: 0.12,
  min_track_points: 10,
  optimization_steps: [0.1, 0.01],
  range_optimization_steps: [1000, 800, 500, 200, 100, 50, 20],
  max_match_groups: 15000,
  cost_weights: {
    variance: 100.0,
    azimuth_error_square: 0.15,
    range_error_square: 6e-7,
    elevation_error_square: 0.1,
  },
}
