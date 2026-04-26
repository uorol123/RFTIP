<template>
  <div class="error-config-panel">
    <!-- 步骤指示器 -->
    <div class="stepper">
      <div
        v-for="(step, index) in steps"
        :key="step.key"
        class="stepper-item"
        :class="{
          active: currentStep === index,
          completed: index < currentStep,
          clickable: index <= currentStep,
        }"
        @click="goToStep(index)"
      >
        <div class="stepper-dot">
          <svg v-if="index < currentStep" viewBox="0 0 24 24" fill="currentColor" width="14" height="14">
            <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
          </svg>
          <span v-else>{{ index + 1 }}</span>
        </div>
        <span class="stepper-label">{{ step.label }}</span>
      </div>
    </div>

    <!-- 步骤0: 选择算法 -->
    <div v-if="currentStep === 0" class="step-content">
      <AlgorithmSelector
        :disabled="store.isTaskRunning"
        @update:algorithm="handleAlgorithmChange"
        @update:config="handleAlgorithmConfigChange"
      />
      <div v-if="store.selectedAlgorithm" class="algorithm-config-wrapper">
        <AlgorithmConfigContainer
          :disabled="store.isTaskRunning"
          :selected-station-count="selectedStationIds.length"
          :selected-track-count="selectedTrackIds.length"
          @update:config="handleAlgorithmConfigUpdate"
          @preset-applied="handlePresetApplied"
        />
      </div>
      <div class="step-footer">
        <button class="btn btn-primary" :disabled="!canGoNext(0)" @click="nextStep">
          下一步
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="16" height="16">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
          </svg>
        </button>
        <p v-if="!canGoNext(0)" class="step-hint">请选择分析算法</p>
      </div>
    </div>

    <!-- 步骤1: 选择雷达站 -->
    <div v-if="currentStep === 1" class="step-content">
      <div class="step-header">
        <h4 class="section-title">选择雷达站</h4>
        <p class="section-hint">
          {{ store.isSingleSourceMode ? '选择进行平滑处理的雷达站（单站）' : '选择进行误差分析的雷达站（至少选择 2 个）' }}
        </p>
      </div>
      <div class="radar-station-list">
        <div
          v-for="station in availableRadarStations"
          :key="station.id"
          class="radar-station-item"
          :class="{ selected: isStationSelected(station.id) }"
          @click="toggleStation(station)"
        >
          <div class="station-checkbox">
            <svg v-if="isStationSelected(station.id)" viewBox="0 0 24 24" fill="currentColor">
              <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
            </svg>
          </div>
          <div class="station-info">
            <div class="station-name">{{ station.station_id }}</div>
            <div class="station-coords">
              ({{ station.latitude.toFixed(4) }}, {{ station.longitude.toFixed(4) }})
            </div>
          </div>
        </div>
      </div>
      <div v-if="availableRadarStations.length === 0" class="empty-hint">
        暂无可用雷达站，请先上传雷达站数据
      </div>
      <div class="step-footer">
        <button class="btn btn-secondary" @click="prevStep">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="16" height="16">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
          </svg>
          上一步
        </button>
        <button class="btn btn-primary" :disabled="!canGoNext(1)" @click="nextStep">
          下一步
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="16" height="16">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
          </svg>
        </button>
        <p v-if="!canGoNext(1)" class="step-hint">
          {{ store.isSingleSourceMode ? '请选择 1 个雷达站' : '请选择至少 2 个雷达站' }}
        </p>
      </div>
    </div>

    <!-- 步骤2: 选择航迹 -->
    <div v-if="currentStep === 2" class="step-content">
      <div class="step-header">
        <h4 class="section-title">选择航迹</h4>
        <p class="section-hint">
          已选择 {{ selectedStationIds.length }} 个雷达站，
          {{ selectedTrackIds.length }} 条轨迹
        </p>
      </div>

      <div class="quick-actions">
        <button
          class="btn btn-primary btn-sm"
          :disabled="loadingTracks"
          @click="loadTracksForSelectedStations"
        >
          {{ loadingTracks ? '加载中...' : '加载航迹数据' }}
        </button>
      </div>

      <div v-if="trackList.length > 0" class="track-list">
        <div
          v-for="track in trackList"
          :key="track.batch_id"
          class="track-item"
          :class="{
            selected: isTrackSelected(track.batch_id),
            disabled: store.isSingleSourceMode ? false : track.station_ids.length < 2
          }"
          @click="toggleTrack(track)"
        >
          <div class="track-checkbox">
            <svg v-if="isTrackSelected(track.batch_id)" viewBox="0 0 24 24" fill="currentColor">
              <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
            </svg>
          </div>
          <div class="track-info">
            <div class="track-header">
              <span class="track-id">{{ track.batch_id }}</span>
              <span v-if="!store.isSingleSourceMode && track.station_ids.length < 2" class="warning-badge">
                只有一个雷达站观测，不可选
              </span>
            </div>
            <div class="track-meta">
              {{ track.point_count }} 点 |
              {{ formatTime(track.start_time) }} ~ {{ formatTime(track.end_time) }}
            </div>
            <div class="track-stations">
              <span
                v-for="sid in track.station_ids"
                :key="sid"
                class="station-badge"
                :class="{ active: isStationSelected(sid) }"
              >
                {{ getStationName(sid) }}
              </span>
              <span v-if="track.station_ids.length === 0" class="no-station">
                无数据
              </span>
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="hasLoadedTracks && trackList.length === 0" class="empty-hint">
        选中的雷达站没有共同的观测轨迹
      </div>

      <div v-if="selectedTrackIds.length > 0" class="selected-summary">
        <div class="summary-title">已选轨迹涉及的雷达站：</div>
        <div class="summary-stations">
          <span
            v-for="sid in involvedStationIds"
            :key="sid"
            class="station-badge active"
          >
            {{ getStationName(sid) }}
          </span>
        </div>
        <div v-if="!store.isSingleSourceMode && involvedStationIds.length < 2" class="warning-hint">
          至少需要2个雷达站才能进行分析
        </div>
      </div>

      <div class="step-footer">
        <button class="btn btn-secondary" @click="prevStep">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="16" height="16">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
          </svg>
          上一步
        </button>
        <button class="btn btn-primary" :disabled="!canGoNext(2)" @click="nextStep">
          下一步
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="16" height="16">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
          </svg>
        </button>
        <p v-if="!canGoNext(2)" class="step-hint">{{ step2Hint }}</p>
      </div>
    </div>

    <!-- 步骤3: 确认并开始 -->
    <div v-if="currentStep === 3" class="step-content">
      <div class="step-header">
        <h4 class="section-title">{{ store.isSingleSourceMode ? '确认并开始平滑' : '确认并开始分析' }}</h4>
        <p class="section-hint">
          {{ store.isSingleSourceMode ? '选择平滑算法参数后开始处理轨迹' : '确认配置参数后开始误差分析' }}
        </p>
      </div>

      <!-- 参数预设（多源参考模式显示） -->
      <div v-if="!store.isSingleSourceMode" class="subsection">
        <h5 class="subsection-title">参数预设方案</h5>
        <div class="preset-grid">
          <button
            v-for="(info, key) in presetInfo"
            :key="key"
            class="preset-card"
            :class="{ active: activePreset === key }"
            @click="applyPreset(key)"
          >
            <div class="preset-name">{{ info.label }}</div>
            <div class="preset-desc">{{ info.description }}</div>
          </button>
        </div>
      </div>

      <!-- 基础参数（多源参考模式显示MRRA参数，单源盲测显示各自的参数） -->
      <div class="subsection">
        <h5 class="subsection-title">{{ store.isSingleSourceMode ? '平滑参数' : '基础参数' }}</h5>
        <div v-if="store.isSingleSourceMode">
          <!-- 单源盲测参数: min_track_points -->
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">最小航迹点数</label>
              <input
                v-model.number="localConfig.min_track_points"
                type="number"
                step="1"
                min="2"
                max="100"
                class="form-input"
                :disabled="store.isTaskRunning"
              />
            </div>
          </div>
        </div>
        <div v-else>
          <!-- 多源参考参数 -->
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">网格分辨率（度）</label>
              <input
                v-model.number="localConfig.grid_resolution"
                type="number"
                step="0.01"
                min="0.01"
                max="1"
                class="form-input"
                :disabled="store.isTaskRunning"
              />
            </div>
            <div class="form-group">
              <label class="form-label">时间窗口（秒）</label>
              <input
                v-model.number="localConfig.time_window"
                type="number"
                step="10"
                min="10"
                max="600"
                class="form-input"
                :disabled="store.isTaskRunning"
              />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">匹配距离阈值（度）</label>
              <input
                v-model.number="localConfig.match_distance_threshold"
                type="number"
                step="0.01"
                min="0.01"
                max="1"
                class="form-input"
                :disabled="store.isTaskRunning"
              />
            </div>
            <div class="form-group">
              <label class="form-label">最小航迹点数</label>
              <input
                v-model.number="localConfig.min_track_points"
                type="number"
                step="1"
                min="3"
                max="100"
                class="form-input"
                :disabled="store.isTaskRunning"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- 高级配置（仅多源参考模式显示） -->
      <div v-if="showAdvanced && !store.isSingleSourceMode" class="subsection advanced">
        <h5 class="subsection-title">代价函数权重</h5>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">方差权重</label>
            <input
              v-model.number="localConfig.cost_weights.variance"
              type="number"
              step="1"
              min="0"
              class="form-input"
              :disabled="store.isTaskRunning"
            />
          </div>
          <div class="form-group">
            <label class="form-label">方位角误差权重</label>
            <input
              v-model.number="localConfig.cost_weights.azimuth_error_square"
              type="number"
              step="0.01"
              min="0"
              class="form-input"
              :disabled="store.isTaskRunning"
            />
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">距离误差权重</label>
            <input
              v-model.number="localConfig.cost_weights.range_error_square"
              type="number"
              step="1e-7"
              min="0"
              class="form-input"
              :disabled="store.isTaskRunning"
            />
          </div>
          <div class="form-group">
            <label class="form-label">俯仰角误差权重</label>
            <input
              v-model.number="localConfig.cost_weights.elevation_error_square"
              type="number"
              step="0.01"
              min="0"
              class="form-input"
              :disabled="store.isTaskRunning"
            />
          </div>
        </div>

        <h5 class="subsection-title" style="margin-top: 1rem;">优化参数</h5>
        <div class="form-group">
          <label class="form-label">方位角优化步长</label>
          <input
            v-model="optimizationStepsStr"
            type="text"
            class="form-input"
            placeholder="用逗号分隔，例如: 0.1, 0.01"
            :disabled="store.isTaskRunning"
          />
        </div>
        <div class="form-group">
          <label class="form-label">距离优化步长</label>
          <input
            v-model="rangeOptimizationStepsStr"
            type="text"
            class="form-input"
            placeholder="用逗号分隔，例如: 1000, 500, 100"
            :disabled="store.isTaskRunning"
          />
        </div>
        <div class="form-group">
          <label class="form-label">最大匹配组数</label>
          <input
            v-model.number="localConfig.max_match_groups"
            type="number"
            step="1000"
            min="1000"
            max="100000"
            class="form-input"
            :disabled="store.isTaskRunning"
          />
        </div>
      </div>

      <!-- 配置摘要 -->
      <div class="config-summary">
        <div class="summary-row">
          <span class="summary-label">算法</span>
          <span class="summary-value">{{ store.currentAlgorithmName || store.selectedAlgorithm || '--' }}</span>
        </div>
        <div class="summary-row">
          <span class="summary-label">雷达站</span>
          <span class="summary-value">{{ store.selectedRadarStations.map(s => s.station_id).join(', ') }}</span>
        </div>
        <div class="summary-row">
          <span class="summary-label">轨迹数</span>
          <span class="summary-value">{{ selectedTrackIds.length }} 条</span>
        </div>
      </div>

      <div class="step-footer">
        <button class="btn btn-secondary" @click="prevStep">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="16" height="16">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
          </svg>
          上一步
        </button>
        <button
          class="btn btn-primary btn-start"
          :disabled="!canStartAnalysis || store.isTaskRunning"
          @click="handleStartAnalysis"
        >
          <svg v-if="store.taskLoading" class="spinner" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="3" opacity="0.25"/>
            <path fill="none" stroke="currentColor" stroke-width="3" d="M12 2a10 10 0 0 1 10 10">
              <animateTransform attributeName="transform" type="rotate" from="0 12 12" to="360 12 12" dur="1s" repeatCount="indefinite"/>
            </path>
          </svg>
          {{ store.taskLoading ? '创建中...' : '开始分析' }}
        </button>
      </div>

      <!-- 高级开关 -->
      <div class="advanced-toggle">
        <button class="btn btn-secondary btn-sm" @click="showAdvanced = !showAdvanced">
          {{ showAdvanced ? '收起高级' : '高级参数' }}
        </button>
        <button
          v-if="showAdvanced"
          class="btn btn-secondary btn-sm"
          @click="resetToDefaults"
        >
          重置
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, watchEffect, onMounted } from 'vue'
import { useErrorAnalysisStore } from '@/stores/errorAnalysis'
import { useAppStore } from '@/stores/app'
import {
  AlgorithmSelector,
  AlgorithmConfigContainer,
} from '@/components/errorAnalysis'
import type { RadarStationInfo, TrackInfo, PresetProfile } from '@/types/errorAnalysis'
import type { PresetConfig } from '@/types/errorAnalysis/algorithms'

interface TrackWithStations extends TrackInfo {
  station_ids: number[]
}

const store = useErrorAnalysisStore()
const appStore = useAppStore()

// ---- 步骤管理 ----
const currentStep = ref(0)

const steps = [
  { key: 'algorithm', label: '选择算法' },
  { key: 'stations', label: '选择雷达站' },
  { key: 'tracks', label: '选择航迹' },
  { key: 'confirm', label: '确认分析' },
]

function canGoNext(step: number): boolean {
  switch (step) {
    case 0: return !!store.selectedAlgorithm
    case 1:
      if (store.isSingleSourceMode) {
        return selectedStationIds.value.length === 1
      }
      return selectedStationIds.value.length >= 2
    case 2:
      if (store.isSingleSourceMode) {
        return selectedTrackIds.value.length > 0
      }
      return selectedTrackIds.value.length > 0 && involvedStationIds.value.length >= 2
    default: return false
  }
}

const step2Hint = computed(() => {
  if (selectedTrackIds.value.length === 0) return '请选择至少 1 条航迹'
  if (store.isSingleSourceMode) return ''
  if (involvedStationIds.value.length < 2) return '选中的轨迹至少需要 2 个雷达站观测'
  return ''
})

function nextStep() {
  if (canGoNext(currentStep.value) && currentStep.value < steps.length - 1) {
    currentStep.value++
  }
}

function prevStep() {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

function goToStep(index: number) {
  // 只能跳到当前步或之前已完成的步骤
  if (index <= currentStep.value) {
    currentStep.value = index
  }
}

// ---- 原有逻辑 ----
const showAdvanced = ref(false)
const activePreset = ref<PresetProfile>('standard')

const availableRadarStations = ref<RadarStationInfo[]>([])
const trackList = ref<TrackWithStations[]>([])
const loadingTracks = ref(false)
const hasLoadedTracks = ref(false)
const selectedTrackIds = ref<string[]>([])

// 单源盲测模式隐藏MRRA相关参数
const isShowMrraParams = computed(() => !store.isSingleSourceMode)

const localConfig = ref<Record<string, any>>({})

watchEffect(() => {
  // 使用算法特定的配置
  localConfig.value = { ...store.currentAlgorithmConfig }
})

const optimizationStepsStr = computed({
  get: () => store.config.optimization_steps.join(', '),
  set: (value: string) => {
    const steps = value.split(',').map(s => parseFloat(s.trim())).filter(n => !isNaN(n) && n > 0)
    if (steps.length > 0) {
      store.updateConfig({ optimization_steps: steps })
    }
  }
})

const rangeOptimizationStepsStr = computed({
  get: () => store.config.range_optimization_steps.join(', '),
  set: (value: string) => {
    const steps = value.split(',').map(s => parseInt(s.trim())).filter(n => !isNaN(n) && n > 0)
    if (steps.length > 0) {
      store.updateConfig({ range_optimization_steps: steps })
    }
  }
})

const presetInfo: Record<PresetProfile, { label: string; description: string }> = {
  standard: { label: '标准配置', description: '平衡精度与速度' },
  high_precision: { label: '高精度', description: '更精细的分析，适用于需要精确误差的场景' },
  fast: { label: '快速分析', description: '大数据量初步筛选，速度优先' },
  coarse: { label: '粗粒度', description: '低分辨率或大范围分析' },
}

const selectedStationIds = computed(() => store.selectedRadarStations.map(s => s.id))

const involvedStationIds = computed(() => {
  // 单源模式：直接返回所选雷达站（只有一个）
  if (store.isSingleSourceMode) {
    return selectedStationIds.value
  }
  // 多源模式：从轨迹中统计涉及的雷达站
  const stationIds = new Set<number>()
  for (const trackId of selectedTrackIds.value) {
    const track = trackList.value.find(t => t.batch_id === trackId)
    if (track) {
      track.station_ids.forEach(sid => stationIds.add(sid))
    }
  }
  return Array.from(stationIds)
})

const canStartAnalysis = computed(() => {
  if (selectedTrackIds.value.length === 0) return false
  if (store.isSingleSourceMode) return true
  return involvedStationIds.value.length >= 2
})

async function loadRadarStations() {
  try {
    availableRadarStations.value = await store.loadRadarStations()
  } catch (error: any) {
    appStore.error(error.message || '加载雷达站列表失败')
  }
}

async function loadTracksForSelectedStations() {
  // 单源模式只需一个雷达站
  if (selectedStationIds.value.length < 1) {
    appStore.warning('请先选择至少1个雷达站')
    return
  }

  // 多源模式需要至少2个雷达站
  if (!store.isSingleSourceMode && selectedStationIds.value.length < 2) {
    appStore.warning('请先选择至少2个雷达站')
    return
  }

  loadingTracks.value = true
  hasLoadedTracks.value = true
  selectedTrackIds.value = []
  trackList.value = []

  try {
    // 单源模式：直接加载所选雷达站的轨迹
    if (store.isSingleSourceMode) {
      const stationId = selectedStationIds.value[0]
      const tracks = await store.loadRadarStationTracks(stationId)
      trackList.value = tracks.map(t => ({
        ...t,
        station_ids: [stationId],
      }))
      loadingTracks.value = false
      return
    }

    // 多源模式：查找多站共同观测的轨迹
    const stationTracks: Map<string, Set<string>> = new Map()

    for (const stationId of selectedStationIds.value) {
      const tracks = await store.loadRadarStationTracks(stationId)
      stationTracks.set(stationId.toString(), new Set(tracks.map(t => t.batch_id)))
    }

    const allBatchIds = new Set<string>()
    stationTracks.forEach((batches) => {
      batches.forEach(batchId => allBatchIds.add(batchId))
    })

    const trackMap: Map<string, TrackWithStations> = new Map()

    for (const batchId of allBatchIds) {
      const observingStations: number[] = []
      for (const stationId of selectedStationIds.value) {
        if (stationTracks.get(stationId.toString())?.has(batchId)) {
          observingStations.push(stationId)
        }
      }

      let trackInfo: TrackInfo | null = null
      for (const stationId of observingStations) {
        try {
          const tracks = await store.loadRadarStationTracks(stationId)
          trackInfo = tracks.find(t => t.batch_id === batchId) || null
          if (trackInfo) break
        } catch {
          // continue
        }
      }

      if (trackInfo) {
        trackMap.set(batchId, {
          ...trackInfo,
          station_ids: observingStations,
        })
      }
    }

    trackList.value = Array.from(trackMap.values()).sort((a, b) => {
      return new Date(a.start_time).getTime() - new Date(b.start_time).getTime()
    })

  } catch (error: any) {
    appStore.error(error.message || '加载轨迹失败')
  } finally {
    loadingTracks.value = false
  }
}

function isStationSelected(stationId: number): boolean {
  return selectedStationIds.value.includes(stationId)
}

function toggleStation(station: RadarStationInfo) {
  const current = store.selectedRadarStations
  if (isStationSelected(station.id)) {
    store.selectRadarStations(current.filter(s => s.id !== station.id))
  } else {
    store.selectRadarStations([...current, station])
  }
  selectedTrackIds.value = []
  trackList.value = []
  hasLoadedTracks.value = false
}

function isTrackSelected(batchId: string): boolean {
  return selectedTrackIds.value.includes(batchId)
}

function toggleTrack(track: TrackWithStations) {
  // 单源模式：允许选择任何轨迹
  if (!store.isSingleSourceMode && track.station_ids.length < 2) return
  if (isTrackSelected(track.batch_id)) {
    selectedTrackIds.value = selectedTrackIds.value.filter(id => id !== track.batch_id)
  } else {
    selectedTrackIds.value = [...selectedTrackIds.value, track.batch_id]
  }
}

function getStationName(stationId: number): string {
  const station = availableRadarStations.value.find(s => s.id === stationId)
  return station?.station_id || `站${stationId}`
}

function applyPreset(preset: PresetProfile) {
  activePreset.value = preset
  store.applyPreset(preset)
  appStore.success(`已应用${presetInfo[preset].label}配置`)
}

async function handleAlgorithmChange(algorithmName: string) {
  await store.selectAlgorithm(algorithmName)
}

function handleAlgorithmConfigChange(config: Record<string, any>) {
  store.updateAlgorithmConfig(config)
}

function handleAlgorithmConfigUpdate(config: Record<string, any>) {
  store.updateAlgorithmConfig(config)
  store.updateConfig(config)
}

function handlePresetApplied(preset: PresetConfig) {
  store.updateAlgorithmConfig(preset.config)
  store.updateConfig(preset.config)

  const presetNameMap: Record<string, PresetProfile> = {
    standard: 'standard',
    high_precision: 'high_precision',
    fast: 'fast',
    coarse: 'coarse',
  }
  activePreset.value = presetNameMap[preset.name] || 'standard'
  appStore.success(`已应用${preset.display_name}配置`)
}

function resetToDefaults() {
  store.resetConfig()
  activePreset.value = 'standard'
  trackList.value = []
  selectedTrackIds.value = []
  hasLoadedTracks.value = false
  appStore.info('配置已重置')
}

function formatTime(dateString: string): string {
  if (!dateString) return '--'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

async function handleStartAnalysis() {
  if (!canStartAnalysis.value) return

  try {
    const involvedStations = availableRadarStations.value.filter(s =>
      involvedStationIds.value.includes(s.id)
    )
    store.selectRadarStations(involvedStations)
    store.selectTracks(
      selectedTrackIds.value.map(id => trackList.value.find(t => t.batch_id === id)!)
    )

    await store.createAnalysis()
    appStore.success('分析任务已创建')
  } catch (error: any) {
    appStore.error(error.message || '创建分析任务失败')
  }
}

onMounted(() => {
  loadRadarStations()
})

watch(() => store.config, (newConfig) => {
  // config synced via watchEffect
}, { deep: true })
</script>

<style scoped>
.error-config-panel {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  padding: 1.25rem;
  background: var(--bg-secondary);
  border-radius: 0.75rem;
}

/* ===== 步骤指示器 ===== */
.stepper {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 0.25rem;
}

.stepper-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.375rem;
  flex: 1;
  position: relative;
  cursor: default;
}

/* 步骤之间的连线 */
.stepper-item:not(:last-child)::after {
  content: '';
  position: absolute;
  top: 12px;
  left: calc(50% + 14px);
  width: calc(100% - 28px);
  height: 2px;
  background: var(--border-color);
  transition: background 0.3s;
}

.stepper-item.completed:not(:last-child)::after {
  background: var(--color-primary);
}

.stepper-item.clickable {
  cursor: pointer;
}

.stepper-dot {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-tertiary);
  color: var(--text-muted);
  font-size: 0.75rem;
  font-weight: 600;
  border: 2px solid var(--border-color);
  transition: all 0.3s;
  position: relative;
  z-index: 1;
}

.stepper-item.active .stepper-dot {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: white;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.15);
}

.stepper-item.completed .stepper-dot {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: white;
}

.stepper-label {
  font-size: 0.6875rem;
  color: var(--text-muted);
  font-weight: 500;
  text-align: center;
  white-space: nowrap;
  transition: color 0.3s;
}

.stepper-item.active .stepper-label {
  color: var(--color-primary);
  font-weight: 600;
}

.stepper-item.completed .stepper-label {
  color: var(--text-primary);
}

/* ===== 步骤内容 ===== */
.step-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  animation: stepFadeIn 0.25s ease-out;
}

@keyframes stepFadeIn {
  from {
    opacity: 0;
    transform: translateX(8px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.step-header {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.section-title {
  margin: 0;
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--text-primary);
}

.section-hint {
  margin: 0;
  font-size: 0.8125rem;
  color: var(--text-secondary);
}

.step-footer {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--border-color);
}

.step-hint {
  margin: 0;
  font-size: 0.8125rem;
  color: var(--text-muted);
}

/* ===== 算法配置 ===== */
.algorithm-config-wrapper {
  padding: 1rem;
  background: var(--bg-tertiary);
  border-radius: 0.5rem;
}

/* ===== 雷达站列表 ===== */
.radar-station-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: 280px;
  overflow-y: auto;
}

.radar-station-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: var(--bg-tertiary);
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid transparent;
}

.radar-station-item:hover {
  background: var(--bg-primary);
}

.radar-station-item.selected {
  border-color: var(--color-primary);
  background: rgba(59, 130, 246, 0.1);
}

.station-checkbox {
  width: 1.25rem;
  height: 1.25rem;
  border-radius: 0.25rem;
  border: 2px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;
}

.radar-station-item.selected .station-checkbox {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: white;
}

.station-checkbox svg {
  width: 0.875rem;
  height: 0.875rem;
}

.station-name {
  font-weight: 500;
  color: var(--text-primary);
}

.station-coords {
  font-size: 0.75rem;
  color: var(--text-muted);
}

/* ===== 轨迹列表 ===== */
.track-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: 300px;
  overflow-y: auto;
}

.track-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.75rem;
  background: var(--bg-tertiary);
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid transparent;
}

.track-item:hover:not(.disabled) {
  background: var(--bg-primary);
}

.track-item.selected {
  border-color: var(--color-primary);
  background: rgba(59, 130, 246, 0.1);
}

.track-item.disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.track-checkbox {
  width: 1.25rem;
  height: 1.25rem;
  border-radius: 0.25rem;
  border: 2px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  margin-top: 0.25rem;
  flex-shrink: 0;
}

.track-item.selected .track-checkbox {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: white;
}

.track-item.disabled .track-checkbox {
  background: var(--bg-tertiary);
}

.track-checkbox svg {
  width: 0.875rem;
  height: 0.875rem;
}

.track-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.track-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.track-id {
  font-weight: 500;
  color: var(--text-primary);
}

.warning-badge {
  font-size: 0.6875rem;
  padding: 0.125rem 0.375rem;
  background: rgba(245, 158, 11, 0.2);
  color: #f59e0b;
  border-radius: 0.25rem;
}

.track-meta {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.track-stations {
  display: flex;
  gap: 0.375rem;
  flex-wrap: wrap;
  margin-top: 0.25rem;
}

.station-badge {
  font-size: 0.6875rem;
  padding: 0.125rem 0.5rem;
  background: var(--bg-primary);
  color: var(--text-secondary);
  border-radius: 1rem;
  border: 1px solid var(--border-color);
}

.station-badge.active {
  background: rgba(59, 130, 246, 0.15);
  color: var(--color-primary);
  border-color: var(--color-primary);
}

.no-station {
  font-size: 0.6875rem;
  color: var(--text-muted);
}

/* ===== 已选汇总 ===== */
.selected-summary {
  padding: 1rem;
  background: var(--bg-tertiary);
  border-radius: 0.5rem;
}

.summary-title {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
}

.summary-stations {
  display: flex;
  gap: 0.375rem;
  flex-wrap: wrap;
}

/* ===== 配置摘要（确认步骤） ===== */
.config-summary {
  padding: 1rem;
  background: var(--bg-tertiary);
  border-radius: 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.875rem;
}

.summary-label {
  color: var(--text-secondary);
}

.summary-value {
  font-weight: 500;
  color: var(--text-primary);
}

/* ===== 快速操作 ===== */
.quick-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

/* ===== 预设配置 ===== */
.preset-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.5rem;
}

.preset-card {
  padding: 0.75rem;
  background: var(--bg-tertiary);
  border: 2px solid transparent;
  border-radius: 0.5rem;
  cursor: pointer;
  text-align: left;
  transition: all 0.2s;
}

.preset-card:hover {
  background: var(--bg-primary);
}

.preset-card.active {
  border-color: var(--color-primary);
  background: rgba(59, 130, 246, 0.1);
}

.preset-name {
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 0.25rem;
}

.preset-desc {
  font-size: 0.75rem;
  color: var(--text-muted);
  line-height: 1.4;
}

/* ===== 子区域 ===== */
.subsection {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 1rem;
  background: var(--bg-tertiary);
  border-radius: 0.5rem;
}

.subsection.advanced {
  background: var(--bg-primary);
}

.subsection-title {
  margin: 0;
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.form-label {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.form-select,
.form-input {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 0.375rem;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 0.875rem;
  transition: all 0.2s;
}

.form-select:focus,
.form-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

.form-select:disabled,
.form-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ===== 提示信息 ===== */
.empty-hint,
.warning-hint {
  padding: 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.8125rem;
  text-align: center;
}

.empty-hint {
  background: var(--bg-tertiary);
  color: var(--text-muted);
}

.warning-hint {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

/* ===== 按钮 ===== */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.8125rem;
}

.btn-primary {
  background: var(--color-primary);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn-secondary {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.btn-secondary:hover:not(:disabled) {
  background: var(--border-color);
}

.btn-start {
  flex: 1;
  padding: 0.625rem 1.25rem;
}

/* ===== 高级开关 ===== */
.advanced-toggle {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}

/* ===== Spinner ===== */
.spinner {
  width: 1rem;
  height: 1rem;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@media (max-width: 640px) {
  .form-row {
    grid-template-columns: 1fr;
  }

  .preset-grid {
    grid-template-columns: 1fr;
  }

  .stepper-label {
    font-size: 0.625rem;
  }
}
</style>
