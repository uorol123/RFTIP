/**
 * MRRA 误差分析状态管理 (新版)
 *
 * 新工作流: 选择雷达站 -> 选择飞机轨迹 -> 选择时间范围 -> 开始分析
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  ErrorAnalysisConfig,
  ErrorAnalysisTask,
  ErrorAnalysisResult,
  TrackSegment,
  MatchGroup,
  ChartDataResponse,
  RadarStationInfo,
  TrackInfo,
  TimeRange,
  PresetProfile,
  TaskDetailResponse,
} from '@/types/errorAnalysis'
import {
  errorAnalysisApi,
  type CreateAnalysisRequest,
  type TaskListParams,
  type MatchGroupParams,
} from '@/api/errorAnalysis'
import { DEFAULT_ERROR_ANALYSIS_CONFIG, PRESET_PROFILES } from '@/types/errorAnalysis'

export const useErrorAnalysisStore = defineStore('errorAnalysis', () => {
  // ========== 状态 ==========

  // 配置
  const config = ref<ErrorAnalysisConfig>({ ...DEFAULT_ERROR_ANALYSIS_CONFIG })

  // 选择的数据 (新版工作流)
  const selectedRadarStations = ref<RadarStationInfo[]>([])
  const selectedTracks = ref<TrackInfo[]>([])
  const timeRange = ref<TimeRange | null>(null)

  // 当前任务
  const currentTask = ref<ErrorAnalysisTask | null>(null)
  const taskLoading = ref(false)

  // 任务列表
  const taskList = ref<ErrorAnalysisTask[]>([])
  const taskListTotal = ref(0)
  const taskListLoading = ref(false)

  // 分析结果
  const analysisResult = ref<ErrorAnalysisResult | null>(null)
  const resultLoading = ref(false)

  // 轨迹段
  const segments = ref<TrackSegment[]>([])
  const segmentsTotal = ref(0)
  const segmentsLoading = ref(false)

  // 匹配组
  const matchGroups = ref<MatchGroup[]>([])
  const matchGroupsTotal = ref(0)
  const matchGroupsPage = ref(1)
  const matchGroupsLoading = ref(false)

  // 图表数据
  const chartData = ref<ChartDataResponse | null>(null)
  const chartDataLoading = ref(false)

  // 轮询控制
  const pollingInterval = ref<number | null>(null)

  // 任务详情（用于历史任务查看）
  const taskDetail = ref<TaskDetailResponse | null>(null)
  const taskDetailLoading = ref(false)

  // ========== 计算属性 ==========

  const hasValidSelection = computed(() => {
    return (
      selectedRadarStations.value.length > 0 &&
      selectedTracks.value.length > 0
    )
  })

  const hasValidConfig = computed(() => {
    return (
      config.value.grid_resolution > 0 &&
      config.value.time_window > 0 &&
      config.value.match_distance_threshold > 0 &&
      config.value.min_track_points >= 3
    )
  })

  const isTaskRunning = computed(() => {
    const status = currentTask.value?.status
    return status === 'pending' || status === 'extracting' ||
           status === 'interpolating' || status === 'matching' ||
           status === 'calculating'
  })

  const isTaskCompleted = computed(() => {
    return currentTask.value?.status === 'completed'
  })

  const isTaskFailed = computed(() => {
    return currentTask.value?.status === 'failed'
  })

  const taskProgress = computed(() => {
    return currentTask.value?.progress ?? 0
  })

  // ========== 数据查询操作 ==========

  /**
   * 加载所有雷达站
   */
  async function loadRadarStations(): Promise<RadarStationInfo[]> {
    try {
      return await errorAnalysisApi.getRadarStations()
    } catch (error: any) {
      console.error('Failed to load radar stations:', error)
      throw error
    }
  }

  /**
   * 加载某雷达站的轨迹
   */
  async function loadRadarStationTracks(stationId: number): Promise<TrackInfo[]> {
    try {
      return await errorAnalysisApi.getRadarStationTracks(stationId)
    } catch (error: any) {
      console.error('Failed to load tracks:', error)
      throw error
    }
  }

  /**
   * 加载共同轨迹 (多雷达站共同观测到的)
   */
  async function loadCommonTracks(stationIds: number[]): Promise<TrackInfo[]> {
    try {
      return await errorAnalysisApi.getCommonTracks(stationIds.join(','))
    } catch (error: any) {
      console.error('Failed to load common tracks:', error)
      throw error
    }
  }

  /**
   * 加载轨迹时间范围
   */
  async function loadTracksTimeRange(batchIds: string[]): Promise<TimeRange> {
    try {
      return await errorAnalysisApi.getTracksTimeRange(batchIds.join(','))
    } catch (error: any) {
      console.error('Failed to load time range:', error)
      throw error
    }
  }

  // ========== 选择操作 ==========

  /**
   * 选择雷达站
   */
  function selectRadarStations(stations: RadarStationInfo[]) {
    selectedRadarStations.value = stations
    // 清空已选择的轨迹，因为雷达站变了
    selectedTracks.value = []
    timeRange.value = null
  }

  /**
   * 选择轨迹
   */
  function selectTracks(tracks: TrackInfo[]) {
    selectedTracks.value = tracks
  }

  /**
   * 设置时间范围
   */
  function setTimeRange(range: TimeRange | null) {
    timeRange.value = range
  }

  // ========== 配置操作 ==========

  /**
   * 加载默认配置
   */
  async function loadDefaultConfig() {
    try {
      const defaultConfig = await errorAnalysisApi.getDefaultConfig()
      config.value = { ...defaultConfig }
    } catch (error: any) {
      console.error('Failed to load default config:', error)
      // 使用本地默认配置
      config.value = { ...DEFAULT_ERROR_ANALYSIS_CONFIG }
    }
  }

  /**
   * 更新配置
   */
  function updateConfig(updates: Partial<ErrorAnalysisConfig>) {
    config.value = { ...config.value, ...updates }
  }

  /**
   * 应用预设配置
   */
  function applyPreset(preset: PresetProfile) {
    const presetConfig = PRESET_PROFILES[preset]
    console.log('[Store] applyPreset called with:', preset)
    console.log('[Store] presetConfig:', JSON.stringify(presetConfig))
    if (presetConfig) {
      // 创建新对象并替换，确保触发响应式更新
      const newConfig = {
        grid_resolution: presetConfig.grid_resolution,
        time_window: presetConfig.time_window,
        match_distance_threshold: presetConfig.match_distance_threshold,
        min_track_points: presetConfig.min_track_points,
        optimization_steps: [...presetConfig.optimization_steps],
        range_optimization_steps: [...presetConfig.range_optimization_steps],
        cost_weights: { ...presetConfig.cost_weights },
        max_match_groups: presetConfig.max_match_groups,
      }
      console.log('[Store] newConfig to apply:', JSON.stringify(newConfig))
      config.value = newConfig
      console.log('[Store] config.value after assignment:', JSON.stringify(config.value))
    }
  }

  /**
   * 重置配置
   */
  function resetConfig() {
    config.value = { ...DEFAULT_ERROR_ANALYSIS_CONFIG }
    selectedRadarStations.value = []
    selectedTracks.value = []
    timeRange.value = null
  }

  // ========== 任务操作 ==========

  /**
   * 创建分析任务
   */
  async function createAnalysis() {
    if (!hasValidSelection.value) {
      throw new Error('请选择雷达站和轨迹')
    }

    taskLoading.value = true
    try {
      const request: CreateAnalysisRequest = {
        radar_station_ids: selectedRadarStations.value.map(s => s.id),
        track_ids: selectedTracks.value.map(t => t.batch_id),
        start_time: timeRange.value?.start_time,
        end_time: timeRange.value?.end_time,
        config: { ...config.value },
      }
      const task = await errorAnalysisApi.createAnalysis(request)
      currentTask.value = task

      // 开始轮询任务状态
      startPolling()

      return task
    } catch (error: any) {
      console.error('Failed to create analysis:', error)
      throw error
    } finally {
      taskLoading.value = false
    }
  }

  /**
   * 加载任务列表
   */
  async function loadTaskList(params?: TaskListParams) {
    taskListLoading.value = true
    try {
      const response = await errorAnalysisApi.getTaskList(params)
      taskList.value = response.tasks
      taskListTotal.value = response.total
    } catch (error: any) {
      console.error('Failed to load task list:', error)
      throw error
    } finally {
      taskListLoading.value = false
    }
  }

  /**
   * 加载任务详情
   */
  async function loadTaskDetail(taskId: string) {
    taskLoading.value = true
    try {
      const task = await errorAnalysisApi.getTaskDetail(taskId)
      currentTask.value = task
      return task
    } catch (error: any) {
      console.error('Failed to load task detail:', error)
      throw error
    } finally {
      taskLoading.value = false
    }
  }

  /**
   * 加载分析结果
   */
  async function loadAnalysisResult(taskId: string) {
    resultLoading.value = true
    try {
      const result = await errorAnalysisApi.getAnalysisResult(taskId)
      analysisResult.value = result
      return result
    } catch (error: any) {
      console.error('Failed to load analysis result:', error)
      throw error
    } finally {
      resultLoading.value = false
    }
  }

  /**
   * 加载轨迹段
   */
  async function loadSegments(taskId: string) {
    segmentsLoading.value = true
    try {
      const result = await errorAnalysisApi.getSegments(taskId)
      segments.value = result
      segmentsTotal.value = result.length
    } catch (error: any) {
      console.error('Failed to load segments:', error)
      throw error
    } finally {
      segmentsLoading.value = false
    }
  }

  /**
   * 加载匹配组
   */
  async function loadMatchGroups(taskId: string, params?: MatchGroupParams) {
    matchGroupsLoading.value = true
    try {
      const matches = await errorAnalysisApi.getMatchGroups(taskId, params)
      matchGroups.value = matches
      matchGroupsTotal.value = matches.length
      matchGroupsPage.value = 1
    } catch (error: any) {
      console.error('Failed to load match groups:', error)
      throw error
    } finally {
      matchGroupsLoading.value = false
    }
  }

  /**
   * 加载图表数据
   */
  async function loadChartData(taskId: string) {
    chartDataLoading.value = true
    try {
      const data = await errorAnalysisApi.getChartData(taskId)
      chartData.value = data
      return data
    } catch (error: any) {
      console.error('Failed to load chart data:', error)
      throw error
    } finally {
      chartDataLoading.value = false
    }
  }

  /**
   * 加载完整任务详情
   */
  async function loadTaskDetailFull(
    taskId: string,
    includeIntermediate = true,
    includePoints = false
  ) {
    taskDetailLoading.value = true
    try {
      const data = await errorAnalysisApi.getTaskDetailFull(
        taskId,
        includeIntermediate,
        includePoints
      )
      taskDetail.value = data
      return data
    } catch (error: any) {
      console.error('Failed to load task detail:', error)
      throw error
    } finally {
      taskDetailLoading.value = false
    }
  }

  // ========== 轮询控制 ==========

  /**
   * 开始轮询任务状态
   */
  function startPolling() {
    stopPolling()
    pollingInterval.value = window.setInterval(async () => {
      if (currentTask.value && isTaskRunning.value) {
        try {
          const task = await errorAnalysisApi.getTaskDetail(currentTask.value.task_id)
          currentTask.value = task

          // 如果任务完成，加载结果
          if (task.status === 'completed') {
            stopPolling()
            await Promise.all([
              loadAnalysisResult(task.task_id),
              loadSegments(task.task_id),
              loadChartData(task.task_id),
            ])
          } else if (task.status === 'failed') {
            stopPolling()
          }
        } catch (error) {
          console.error('Polling error:', error)
        }
      } else {
        stopPolling()
      }
    }, 2000) // 每2秒轮询一次
  }

  /**
   * 停止轮询
   */
  function stopPolling() {
    if (pollingInterval.value !== null) {
      clearInterval(pollingInterval.value)
      pollingInterval.value = null
    }
  }

  // ========== 清除操作 ==========

  /**
   * 清除当前任务
   */
  function clearCurrentTask() {
    stopPolling()
    currentTask.value = null
    analysisResult.value = null
    segments.value = []
    matchGroups.value = []
    chartData.value = null
  }

  /**
   * 清除所有状态
   */
  function clearAll() {
    clearCurrentTask()
    taskList.value = []
    taskListTotal.value = 0
    resetConfig()
  }

  return {
    // 状态
    config,
    selectedRadarStations,
    selectedTracks,
    timeRange,
    currentTask,
    taskLoading,
    taskList,
    taskListTotal,
    taskListLoading,
    analysisResult,
    resultLoading,
    segments,
    segmentsTotal,
    segmentsLoading,
    matchGroups,
    matchGroupsTotal,
    matchGroupsPage,
    matchGroupsLoading,
    chartData,
    chartDataLoading,
    taskDetail,
    taskDetailLoading,

    // 计算属性
    hasValidSelection,
    hasValidConfig,
    isTaskRunning,
    isTaskCompleted,
    isTaskFailed,
    taskProgress,

    // 数据查询操作
    loadRadarStations,
    loadRadarStationTracks,
    loadCommonTracks,
    loadTracksTimeRange,

    // 选择操作
    selectRadarStations,
    selectTracks,
    setTimeRange,

    // 配置操作
    loadDefaultConfig,
    updateConfig,
    applyPreset,
    resetConfig,

    // 任务操作
    createAnalysis,
    loadTaskList,
    loadTaskDetail,
    loadTaskDetailFull,
    loadAnalysisResult,
    loadSegments,
    loadMatchGroups,
    loadChartData,

    // 轮询控制
    startPolling,
    stopPolling,

    // 清除操作
    clearCurrentTask,
    clearAll,
  }
})
