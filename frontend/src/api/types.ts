// API Response Types
export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

export interface ApiError {
  code: number
  message: string
  detail?: string
}

// User Types
export interface User {
  id: number
  username: string
  email: string
  full_name?: string
  avatar_url?: string  // 后端原始字段名
  avatar?: string  // 前端兼容字段
  is_active: boolean
  is_superuser: boolean  // 后端原始字段名
  is_admin: boolean  // 前端兼容字段
  created_at: string
  updated_at: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
  full_name?: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}

export interface LoginLog {
  id: number
  user_id: number
  ip_address: string
  user_agent: string
  login_time: string
  status: 'success' | 'failed'
}

// File Types
export interface DataFile {
  id: number
  file_name: string  // 后端原始字段名
  filename: string  // 前端兼容字段
  original_filename: string  // 前端兼容字段（与 filename 相同）
  file_size: number
  file_type: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  is_public: boolean
  upload_time: string
  processed_time?: string
  error_message?: string
  user_id: number  // 后端原始字段名
  owner_id: number  // 前端兼容字段
  owner_name?: string
  row_count?: number  // 后端原始字段名
  record_count?: number  // 前端兼容字段
}

export interface FileUploadResponse {
  file_id: number
  filename: string
  status: string
}

export interface FileProcessRequest {
  algorithm?: 'ransac' | 'kalman'
  ransac_threshold?: number
  kalman_process_noise?: number
  kalman_measurement_noise?: number
}

// Track Types
export interface TrackPoint {
  id: number
  track_id: string
  timestamp: string
  longitude: number
  latitude: number
  altitude: number
  speed: number
  heading: number
  is_corrected: boolean
}

export interface Track {
  track_id: string
  file_id: number
  points: TrackPoint[]
  point_count: number
  duration_seconds?: number
  start_time: string
  end_time: string
}

export interface TrackSummary {
  file_id: number
  total_tracks: number
  total_points: number
  corrected_points: number
  time_range: {
    start: string
    end: string
  }
  bbox: {
    min_lon: number
    max_lon: number
    min_lat: number
    max_lat: number
    min_alt: number
    max_alt: number
  }
}

export interface TrackProcessRequest {
  file_id: number
  algorithm?: 'ransac' | 'kalman' | 'both'
  ransac_threshold?: number
  kalman_process_noise?: number
  kalman_measurement_noise?: number
}

export interface TrackProcessResponse {
  task_id: string
  status: string
  message: string
}

// Zone Types
export interface NoFlyZone {
  id: number
  zone_name: string  // 后端原始字段名
  name: string  // 前端兼容字段
  zone_type: 'circle' | 'polygon'
  coordinates: string  // 后端原始字段（JSON 字符串）
  coordinates_array: number[][]  // 前端兼容字段（解析后的坐标数组）
  min_altitude: number
  max_altitude: number
  is_active: boolean
  notification_enabled: boolean  // 后端原始字段名
  email_alerts: boolean  // 前端兼容字段
  notification_email?: string  // 后端原始字段名
  alert_emails?: string[]  // 前端兼容字段
  created_at: string
  updated_at: string
}

export interface CreateZoneRequest {
  name: string
  zone_type: 'circle' | 'polygon'
  coordinates: number[][]
  min_altitude: number
  max_altitude: number
  is_active?: boolean
  email_alerts?: boolean
  alert_emails?: string[]
}

export interface IntrusionDetection {
  intrusions: Intrusion[]
  total_count: number
  detection_time: string
}

export interface Intrusion {
  id: number
  zone_id: number
  zone_name: string
  track_id: string
  timestamp: string
  longitude: number
  latitude: number
  altitude: number
  duration_seconds: number
}

// Analysis Types
export interface AnalysisRequest {
  track_id: string
  analysis_type?: 'overall' | 'segment'
  start_time?: string
  end_time?: string
  use_llm?: boolean
  llm_prompt?: string
}

export interface AnalysisResponse {
  analysis_id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  results?: AnalysisResult
  error?: string
}

export interface AnalysisResult {
  track_id: string
  analysis_type: string
  summary: {
    total_distance: number
    duration: number
    avg_speed: number
    max_altitude: number
    min_altitude: number
  }
  features: {
    feature_name: string
    value: number
    description: string
  }[]
  llm_analysis?: string
  created_at: string
}

export interface FeatureInfo {
  name: string
  description: string
  type: string
  extractable: boolean
}

export interface AnalysisReport {
  track_id: string
  format: 'pdf' | 'json'
  content: string
  created_at: string
}

// Pagination Types
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  pages: number
}

export interface PaginationParams {
  page?: number
  page_size?: number
  sort_by?: string
  order?: 'asc' | 'desc'
}
