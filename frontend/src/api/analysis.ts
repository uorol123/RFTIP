import apiClient from './client'
import { apiCall } from './client'
import type {
  AnalysisRequest,
  AnalysisResponse,
  AnalysisResult,
  FeatureInfo,
  AnalysisReport,
} from './types'

export const analysisApi = {
  /**
   * Analyze trajectory (overall or segment)
   */
  analyzeTrajectory: async (data: AnalysisRequest): Promise<AnalysisResponse> => {
    return apiCall(() =>
      apiClient.post<AnalysisResponse>('/analysis/trajectory', data)
    )
  },

  /**
   * Analyze trajectory segment
   */
  analyzeSegment: async (data: AnalysisRequest): Promise<AnalysisResponse> => {
    return apiCall(() =>
      apiClient.post<AnalysisResponse>('/analysis/segment', data)
    )
  },

  /**
   * LLM-based analysis
   */
  llmAnalyze: async (data: {
    track_id: string
    prompt: string
    context?: string
  }): Promise<{ result: string }> => {
    return apiCall(() =>
      apiClient.post<{ result: string }>('/analysis/llm', data)
    )
  },

  /**
   * Get analysis result
   */
  getResult: async (analysisId: string): Promise<AnalysisResponse> => {
    return apiCall(() =>
      apiClient.get<AnalysisResponse>(`/analysis/result/${analysisId}`)
    )
  },

  /**
   * Get available features
   */
  getAvailableFeatures: async (): Promise<FeatureInfo[]> => {
    return apiCall(() =>
      apiClient.get<FeatureInfo[]>('/analysis/features/available')
    )
  },

  /**
   * Generate analysis report
   */
  generateReport: async (
    trackId: string,
    format: 'pdf' | 'json' = 'json'
  ): Promise<AnalysisReport> => {
    return apiCall(() =>
      apiClient.get<AnalysisReport>(`/analysis/report/${trackId}`, {
        params: { format },
        responseType: format === 'pdf' ? 'blob' : 'json',
      })
    )
  },

  /**
   * Get analysis task status
   */
  getTaskStatus: async (analysisId: string): Promise<{
    status: 'pending' | 'processing' | 'completed' | 'failed'
    progress: number
    result?: AnalysisResult
    error?: string
  }> => {
    return apiCall(() =>
      apiClient.get(`/analysis/tasks/${analysisId}`)
    )
  },
}
