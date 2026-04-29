<template>
  <AlgorithmConfigBase
    :title="algorithmInfo.display_name"
    :description="algorithmInfo.description"
    :config-schema="configSchema"
    :model-value="localConfig"
    :disabled="disabled"
    @update:model-value="handleConfigUpdate"
  >
    <template #header>
      <div class="gd-config-header">
        <h3 class="config-title">{{ algorithmInfo.display_name }}</h3>
        <p class="config-description">{{ algorithmInfo.description }}</p>

        <!-- 算法元信息 -->
        <div class="algorithm-meta">
          <span class="version">版本: {{ algorithmInfo.version }}</span>
          <span v-if="algorithmInfo.supports_elevation" class="badge">
            支持俯仰角
          </span>
        </div>
      </div>
    </template>

    <template #content>
      <div class="gd-config-content">
        <!-- 预设配置选择 -->
        <div class="config-section">
          <h4 class="section-title">参数预设方案</h4>
          <div class="preset-grid">
            <button
              v-for="preset in presets"
              :key="preset.name"
              class="preset-card"
              :class="{ active: selectedPreset === preset.name }"
              @click="applyPreset(preset)"
            >
              <div class="preset-name">{{ preset.display_name }}</div>
              <div class="preset-desc">{{ getPresetDescription(preset.name) }}</div>
            </button>
          </div>
        </div>

        <!-- 数据选择 -->
        <div class="config-section">
          <h4 class="section-title">数据选择</h4>
          <div class="data-selection">
            <div class="selection-item">
              <label>选择雷达站</label>
              <div class="station-count">
                已选择 {{ selectedStationCount }} 个雷达站
              </div>
            </div>
            <div class="selection-item">
              <label>选择轨迹</label>
              <div class="track-count">
                已选择 {{ selectedTrackCount }} 条轨迹
              </div>
            </div>
          </div>
        </div>

        <!-- 算法参数配置 -->
        <div class="config-section">
          <h4 class="section-title">算法参数配置</h4>

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
                  :disabled="disabled"
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
                  :disabled="disabled"
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
                  :disabled="disabled"
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
                  :disabled="disabled"
                />
              </div>
            </div>
          </div>

          <!-- 优化参数 -->
          <div class="subsection">
            <h5 class="subsection-title">优化参数</h5>
            <div class="form-group">
              <label class="form-label">方位角优化步长</label>
              <input
                v-model="optimizationStepsStr"
                type="text"
                class="form-input"
                placeholder="用逗号分隔，例如: 0.1, 0.01"
                :disabled="disabled"
              />
            </div>
            <div class="form-group">
              <label class="form-label">距离优化步长</label>
              <input
                v-model="rangeOptimizationStepsStr"
                type="text"
                class="form-input"
                placeholder="用逗号分隔，例如: 1000, 500, 100"
                :disabled="disabled"
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
                :disabled="disabled"
              />
            </div>
          </div>

          <!-- 代价函数权重 -->
          <div v-if="localConfig.cost_weights" class="subsection">
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
                  :disabled="disabled"
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
                  :disabled="disabled"
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
                  :disabled="disabled"
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
                  :disabled="disabled"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </AlgorithmConfigBase>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import AlgorithmConfigBase from '../AlgorithmConfigBase.vue'
import type { AlgorithmInfo, PresetConfig, AlgorithmConfigSchema } from '@/types/errorAnalysis/algorithms'
import { DEFAULT_MRRA_CONFIG } from '@/types/errorAnalysis/algorithms'

interface Props {
  algorithmInfo: AlgorithmInfo
  configSchema: AlgorithmConfigSchema | null
  modelValue: Record<string, any>
  presets: PresetConfig[]
  disabled?: boolean
  selectedStationCount?: number
  selectedTrackCount?: number
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
  selectedStationCount: 0,
  selectedTrackCount: 0,
})

const emit = defineEmits<{
  'update:modelValue': [config: Record<string, any>]
  'preset-applied': [preset: PresetConfig]
}>()

// 本地配置状态
const localConfig = ref<Record<string, any>>({ ...props.modelValue })
const selectedPreset = ref<string>('')

// 初始化配置
watch(() => props.modelValue, (newValue) => {
  localConfig.value = { ...newValue }
}, { deep: true, immediate: true })

// 字符串形式的优化步长
const optimizationStepsStr = computed({
  get: () => (localConfig.value.optimization_steps || []).join(', '),
  set: (value: string) => {
    const steps = value.split(',').map(s => parseFloat(s.trim())).filter(n => !isNaN(n) && n > 0)
    if (steps.length > 0) {
      localConfig.value = { ...localConfig.value, optimization_steps: steps }
      emit('update:modelValue', localConfig.value)
    }
  }
})

const rangeOptimizationStepsStr = computed({
  get: () => (localConfig.value.range_optimization_steps || []).join(', '),
  set: (value: string) => {
    const steps = value.split(',').map(s => parseInt(s.trim())).filter(n => !isNaN(n) && n > 0)
    if (steps.length > 0) {
      localConfig.value = { ...localConfig.value, range_optimization_steps: steps }
      emit('update:modelValue', localConfig.value)
    }
  }
})

// 预设配置描述
const presetDescriptions: Record<string, string> = {
  standard: '与原项目默认参数一致，平衡精度与速度',
  high_precision: '更精细的分析，适用于需要精确误差的场景',
  fast: '大数据量初步筛选，速度优先',
  coarse: '低分辨率或大范围分析',
}

// 方法
const getPresetDescription = (presetName: string): string => {
  return presetDescriptions[presetName] || '自定义配置'
}

const applyPreset = (preset: PresetConfig) => {
  selectedPreset.value = preset.name
  localConfig.value = { ...preset.config }
  emit('update:modelValue', localConfig.value)
  emit('preset-applied', preset)
}

const handleConfigUpdate = (newConfig: Record<string, any>) => {
  localConfig.value = { ...newConfig }
  selectedPreset.value = '' // 清除预设选择
  emit('update:modelValue', newConfig)
}
</script>

<style scoped>
.gd-config-header {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.config-title {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
}

.config-description {
  margin: 0;
  font-size: 0.875rem;
  color: var(--text-secondary);
  line-height: 1.5;
}

.algorithm-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.8125rem;
  color: var(--text-muted);
}

.version {
  font-family: monospace;
}

.badge {
  padding: 0.125rem 0.5rem;
  background: var(--color-primary);
  color: white;
  border-radius: 1rem;
  font-size: 0.75rem;
}

.gd-config-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

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

/* 预设配置 */
.preset-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}

.preset-card {
  padding: 0.75rem;
  background: var(--bg-secondary);
  border: 2px solid transparent;
  border-radius: 0.5rem;
  cursor: pointer;
  text-align: left;
  transition: all 0.2s;
}

.preset-card:hover {
  background: var(--bg-tertiary);
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

/* 数据选择 */
.data-selection {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 1rem;
  background: var(--bg-secondary);
  border-radius: 0.5rem;
}

.selection-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.selection-item label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.station-count,
.track-count {
  font-size: 0.8125rem;
  color: var(--color-primary);
  font-weight: 500;
}

/* 参数配置 */
.subsection {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 1rem;
  background: var(--bg-secondary);
  border-radius: 0.5rem;
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

.form-input {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 0.375rem;
  background: var(--bg-tertiary);
  color: var(--text-primary);
  font-size: 0.875rem;
  transition: all 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

.form-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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
