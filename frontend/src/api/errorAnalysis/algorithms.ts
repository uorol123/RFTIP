/**
 * 误差分析算法 API
 * 提供算法列表、配置 Schema、预设配置等接口
 */
import { apiCall } from '../client'
import apiClient from '../client'
import type {
  AlgorithmInfo,
  AlgorithmsListResponse,
  AlgorithmConfigSchema,
  AlgorithmPresetsResponse,
  ConfigValidationResponse,
} from '@/types/errorAnalysis/algorithms'

/**
 * 算法相关 API
 */
export const algorithmsApi = {
  /**
   * 获取所有可用算法列表
   */
  async listAlgorithms(): Promise<AlgorithmsListResponse> {
    return apiCall(() =>
      apiClient.get<AlgorithmsListResponse>('/error-analysis/algorithms')
    )
  },

  /**
   * 获取算法详细信息
   */
  async getAlgorithmInfo(name: string): Promise<AlgorithmInfo> {
    return apiCall(() =>
      apiClient.get<AlgorithmInfo>(`/error-analysis/algorithms/${name}`)
    )
  },

  /**
   * 获取算法配置 Schema
   */
  async getAlgorithmConfigSchema(name: string): Promise<AlgorithmConfigSchema> {
    return apiCall(() =>
      apiClient.get<AlgorithmConfigSchema>(
        `/error-analysis/algorithms/${name}/config-schema`
      )
    )
  },

  /**
   * 获取算法预设配置
   */
  async getAlgorithmPresets(name: string): Promise<AlgorithmPresetsResponse> {
    return apiCall(() =>
      apiClient.get<AlgorithmPresetsResponse>(
        `/error-analysis/algorithms/${name}/presets`
      )
    )
  },

  /**
   * 验证算法配置
   */
  async validateAlgorithmConfig(
    name: string,
    config: Record<string, any>
  ): Promise<ConfigValidationResponse> {
    return apiCall(() =>
      apiClient.post<ConfigValidationResponse>(
        `/error-analysis/algorithms/${name}/validate-config`,
        config
      )
    )
  },
}
