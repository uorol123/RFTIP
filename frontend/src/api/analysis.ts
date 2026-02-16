import apiClient from './client'
import { apiCall } from './client'
import type {
  AnalysisRequest,
  AnalysisResponse,
  AnalysisResult,
  FeatureInfo,
  AnalysisReport,
} from './types'

// 函数式导出
export async function analyzeTrajectory(data: AnalysisRequest): Promise<AnalysisResponse> {
  return apiCall(() =>
    apiClient.post<AnalysisResponse>('/analysis/trajectory', data)
  )
}

export async function analyzeSegment(data: AnalysisRequest): Promise<AnalysisResponse> {
  return apiCall(() =>
    apiClient.post<AnalysisResponse>('/analysis/segment', data)
  )
}

export async function llmAnalyze(data: {
  track_id: string
  prompt: string
  context?: string
}): Promise<{ result: string }> {
  return apiCall(() =>
    apiClient.post<{ result: string }>('/analysis/llm', data)
  )
}

export async function getResult(analysisId: string): Promise<AnalysisResponse> {
  return apiCall(() =>
    apiClient.get<AnalysisResponse>(`/analysis/result/${analysisId}`)
  )
}

export async function getAvailableFeatures(): Promise<FeatureInfo[]> {
  return apiCall(() =>
    apiClient.get<FeatureInfo[]>('/analysis/features/available')
  )
}

export async function generateReport(
  trackId: string,
  format: 'pdf' | 'json' = 'json'
): Promise<AnalysisReport> {
  return apiCall(() =>
    apiClient.get<AnalysisReport>(`/analysis/report/${trackId}`, {
      params: { format },
      responseType: format === 'pdf' ? 'blob' : 'json',
    })
  )
}

export async function getTaskStatus(analysisId: string): Promise<{
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress: number
  result?: AnalysisResult
  error?: string
}> {
  return apiCall(() =>
    apiClient.get(`/analysis/tasks/${analysisId}`)
  )
}

// 对象式导出（保持向后兼容）
export const analysisApi = {
  analyzeTrajectory,
  analyzeSegment,
  llmAnalyze,
  getResult,
  getAvailableFeatures,
  generateReport,
  getTaskStatus,
}
