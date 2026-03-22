<template>
  <div class="error-config-panel">
    <div class="config-header">
      <h3 class="config-title">误差分析配置</h3>
      <div class="config-actions">
        <button
          v-if="showAdvanced"
          class="btn btn-secondary btn-sm"
          @click="resetToDefaults"
        >
          重置
        </button>
        <button
          class="btn btn-secondary btn-sm"
          @click="showAdvanced = !showAdvanced"
        >
          {{ showAdvanced ? '收起' : '高级' }}
        </button>
      </div>
    </div>

    <!-- 步骤1: 选择雷达站 -->
    <div class="config-section">
      <h4 class="section-title">1. 选择雷达站</h4>
      <p class="section-hint">选择进行误差分析的雷达站（至少选择2个）</p>
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
    </div>

    <!-- 步骤2: 选择轨迹 -->
    <div v-if="selectedStationIds.length >= 2" class="config-section">
      <h4 class="section-title">2. 选择航迹</h4>
      <p class="section-hint">
        已选择 {{ selectedStationIds.length }} 个雷达站，
        {{ selectedTrackIds.length }} 条轨迹
      </p>

      <!-- 加载按钮 -->
      <div class="quick-actions">
        <button
          class="btn btn-primary btn-sm"
          :disabled="loadingTracks"
          @click="loadTracksForSelectedStations"
        >
          {{ loadingTracks ? '加载中...' : '加载航迹数据' }}
        </button>
      </div>

      <!-- 轨迹列表 -->
      <div v-if="trackList.length > 0" class="track-list">
        <div
          v-for="track in trackList"
          :key="track.batch_id"
          class="track-item"
          :class="{
            selected: isTrackSelected(track.batch_id),
            disabled: track.station_ids.length < 2
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
              <span v-if="track.station_ids.length < 2" class="warning-badge">
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

      <!-- 已选轨迹汇总 -->
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
        <div v-if="involvedStationIds.length < 2" class="warning-hint">
          至少需要2个雷达站才能进行分析
        </div>
      </div>
    </div>

    <!-- 步骤3: 配置参数 -->
    <div v-if="selectedTrackIds.length > 0 && involvedStationIds.length >= 2" class="config-section">
      <h4 class="section-title">3. 分析配置</h4>

      <!-- 预设配置 -->
      <div class="subsection">
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

      <!-- 基础参数 -->
      <div class="subsection">
        <h5 class="subsection-title">基础参数</h5>
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

      <!-- 高级配置 -->
      <div v-if="showAdvanced" class="subsection advanced">
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
              v-model.number="localConfig.cost_weights.azimuth"
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
              v-model.number="localConfig.cost_weights.range"
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
              v-model.number="localConfig.cost_weights.elevation"
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
    </div>

    <!-- 操作按钮 -->
    <div class="config-actions-footer">
      <button
        class="btn btn-primary"
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
      <div v-if="!canStartAnalysis" class="start-hint">
        {{ startHintText }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, watchEffect, onMounted } from 'vue'
import { useErrorAnalysisStore } from '@/stores/errorAnalysis'
import { useAppStore } from '@/stores/app'
import type { RadarStationInfo, TrackInfo, PresetProfile } from '@/types/errorAnalysis'

interface TrackWithStations extends TrackInfo {
  station_ids: number[]
}

const store = useErrorAnalysisStore()
const appStore = useAppStore()

const showAdvanced = ref(false)
const activePreset = ref<PresetProfile>('standard')

// 雷达站和轨迹数据
const availableRadarStations = ref<RadarStationInfo[]>([])
const trackList = ref<TrackWithStations[]>([])
const loadingTracks = ref(false)
const hasLoadedTracks = ref(false)

// 选中的轨迹
const selectedTrackIds = ref<string[]>([])

// 本地配置副本 - 使用 ref + watchEffect 确保响应式追踪 config 的任何变化
const localConfig = ref(store.config)

// 显式追踪 store.config 的变化并同步到 localConfig
watchEffect(() => {
  localConfig.value = store.config
})

// 字符串形式的优化步长
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

// 预设配置信息
const presetInfo: Record<PresetProfile, { label: string; description: string }> = {
  standard: { label: '标准配置', description: '与原项目默认参数一致，平衡精度与速度' },
  high_precision: { label: '高精度', description: '更精细的分析，适用于需要精确误差的场景' },
  fast: { label: '快速分析', description: '大数据量初步筛选，速度优先' },
  coarse: { label: '粗粒度', description: '低分辨率或大范围分析' },
}

// 选择状态
const selectedStationIds = computed(() => store.selectedRadarStations.map(s => s.id))

// 涉及某条轨迹的雷达站
const involvedStationIds = computed(() => {
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
  return (
    selectedTrackIds.value.length > 0 &&
    involvedStationIds.value.length >= 2
  )
})

const startHintText = computed(() => {
  if (selectedTrackIds.value.length === 0) return '请选择航迹'
  if (involvedStationIds.value.length < 2) return '选中的轨迹至少需要2个雷达站观测'
  return ''
})

// 加载雷达站列表
async function loadRadarStations() {
  try {
    availableRadarStations.value = await store.loadRadarStations()
  } catch (error: any) {
    appStore.error(error.message || '加载雷达站列表失败')
  }
}

// 加载选中雷达站的轨迹
async function loadTracksForSelectedStations() {
  if (selectedStationIds.value.length < 2) {
    appStore.warning('请先选择至少2个雷达站')
    return
  }

  loadingTracks.value = true
  hasLoadedTracks.value = true
  selectedTrackIds.value = []
  trackList.value = []

  try {
    // 获取每个选中雷达站的轨迹
    const stationTracks: Map<string, Set<string>> = new Map()

    for (const stationId of selectedStationIds.value) {
      const tracks = await store.loadRadarStationTracks(stationId)
      stationTracks.set(stationId.toString(), new Set(tracks.map(t => t.batch_id)))
    }

    // 找出所有轨迹
    const allBatchIds = new Set<string>()
    stationTracks.forEach((batches) => {
      batches.forEach(batchId => allBatchIds.add(batchId))
    })

    // 构建轨迹列表，包含每个轨迹被哪些雷达站观测
    const trackMap: Map<string, TrackWithStations> = new Map()

    for (const batchId of allBatchIds) {
      const observingStations: number[] = []
      for (const stationId of selectedStationIds.value) {
        if (stationTracks.get(stationId.toString())?.has(batchId)) {
          observingStations.push(stationId)
        }
      }

      // 获取轨迹详情（从任意一个有数据的雷达站）
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

    // 转换为数组并按时间排序
    trackList.value = Array.from(trackMap.values()).sort((a, b) => {
      return new Date(a.start_time).getTime() - new Date(b.start_time).getTime()
    })

  } catch (error: any) {
    appStore.error(error.message || '加载轨迹失败')
  } finally {
    loadingTracks.value = false
  }
}

// 选择操作
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
  // 清空轨迹选择和列表
  selectedTrackIds.value = []
  trackList.value = []
  hasLoadedTracks.value = false
}

function isTrackSelected(batchId: string): boolean {
  return selectedTrackIds.value.includes(batchId)
}

function toggleTrack(track: TrackWithStations) {
  // 只有至少2个雷达站观测到的轨迹才能选
  if (track.station_ids.length < 2) return

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

// 应用预设
function applyPreset(preset: PresetProfile) {
  console.log('[Debug] applyPreset called with:', preset)
  console.log('[Debug] Before applyPreset, store.config:', JSON.stringify(store.config))
  activePreset.value = preset
  store.applyPreset(preset)
  console.log('[Debug] After applyPreset, store.config:', JSON.stringify(store.config))
  appStore.success(`已应用${presetInfo[preset].label}配置`)
}

// 重置为默认值
function resetToDefaults() {
  store.resetConfig()
  activePreset.value = 'standard'
  trackList.value = []
  selectedTrackIds.value = []
  hasLoadedTracks.value = false
  appStore.info('配置已重置')
}

// 格式化时间
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

// 开始分析
async function handleStartAnalysis() {
  if (!canStartAnalysis.value) return

  try {
    // 只传入有数据的雷达站
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

// 初始化
onMounted(() => {
  loadRadarStations()
})

// 调试：监控 store.config 的变化
watch(() => store.config, (newConfig) => {
  console.log('[Debug] store.config changed:', newConfig)
}, { deep: true })

// 调试：监控 localConfig 的变化
watch(localConfig, (newLocalConfig) => {
  console.log('[Debug] localConfig changed:', newLocalConfig)
}, { deep: true })
</script>

<style scoped>
.error-config-panel {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 1.5rem;
  background: var(--bg-secondary);
  border-radius: 0.75rem;
}

.config-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.config-title {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
}

.config-actions {
  display: flex;
  gap: 0.5rem;
}

/* 配置区块 */
.config-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
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

/* 雷达站列表 */
.radar-station-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: 200px;
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

/* 轨迹列表 */
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

/* 已选轨迹汇总 */
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

/* 快速操作 */
.quick-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

/* 预设配置 */
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

/* 高级配置 */
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

/* 提示信息 */
.empty-hint,
.warning-hint,
.loading-hint {
  padding: 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.8125rem;
  text-align: center;
}

.empty-hint,
.loading-hint {
  background: var(--bg-tertiary);
  color: var(--text-muted);
}

.warning-hint {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

/* 按钮 */
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

.btn-outline {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
}

.btn-outline:hover:not(:disabled) {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

/* 底部操作区 */
.config-actions-footer {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}

.start-hint {
  font-size: 0.8125rem;
  color: var(--text-muted);
  text-align: center;
}

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
}
</style>
