<template>
  <div class="algorithm-config-container">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>加载算法配置中...</p>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
      <button @click="retry" class="btn btn-secondary">重试</button>
    </div>

    <!-- 算法配置内容 -->
    <component
      v-else-if="currentComponent"
      :is="currentComponent"
      :algorithm-info="algorithmInfo"
      :config-schema="configSchema"
      :model-value="localConfig"
      :presets="presets"
      :disabled="disabled"
      :selected-station-count="selectedStationCount"
      :selected-track-count="selectedTrackCount"
      @update:model-value="handleConfigUpdate"
      @preset-applied="handlePresetApplied"
    />

    <!-- 空状态 -->
    <div v-else class="empty-state">
      <p>请先选择分析算法</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, shallowRef } from 'vue'
import { useErrorAnalysisStore } from '@/stores/errorAnalysis'
import type { AlgorithmInfo, PresetConfig, AlgorithmConfigSchema } from '@/types/errorAnalysis/algorithms'

// 动态导入组件
const AlgorithmConfigBase = () => import('./AlgorithmConfigBase.vue')
const GradientDescentConfig = () => import('./gradient_descent/GradientDescentConfig.vue')

// 算法配置组件映射
const ALGORITHM_CONFIG_COMPONENTS: Record<string, () => Promise<any>> = {
  gradient_descent: () => import('./gradient_descent/GradientDescentConfig.vue'),
  // 未来可以添加更多算法
  // least_squares: () => import('./least_squares/LeastSquaresConfig.vue'),
}

interface Props {
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
  'update:config': [config: Record<string, any>]
  'preset-applied': [preset: PresetConfig]
}>()

const store = useErrorAnalysisStore()

// 状态
const loading = ref(false)
const error = ref<string | null>(null)
const localConfig = ref<Record<string, any>>({})
const currentComponent = shallowRef<any>(null)

// 计算属性
const algorithmInfo = computed(() => store.selectedAlgorithm)
const configSchema = computed(() => store.currentConfigSchema)
const presets = computed(() => store.currentPresets)

// 监听算法变化
watch(() => store.selectedAlgorithm?.name, async (algorithmName) => {
  if (algorithmName) {
    await loadAlgorithmConfig(algorithmName)
  } else {
    currentComponent.value = null
    localConfig.value = {}
  }
}, { immediate: true })

// 监听配置变化
watch(() => store.currentAlgorithmConfig, (newConfig) => {
  localConfig.value = { ...newConfig }
}, { deep: true, immediate: true })

// 方法
const loadAlgorithmConfig = async (algorithmName: string) => {
  loading.value = true
  error.value = null

  try {
    // 加载算法配置 Schema 和预设
    await Promise.all([
      store.loadAlgorithmConfigSchema(algorithmName),
      store.loadAlgorithmPresets(algorithmName),
    ])

    // 动态加载算法配置组件
    const componentLoader = ALGORITHM_CONFIG_COMPONENTS[algorithmName]
    if (componentLoader) {
      currentComponent.value = (await componentLoader()).default
    } else {
      // 如果没有专用组件，使用基础组件
      currentComponent.value = (await import('./AlgorithmConfigBase.vue')).default
    }

    // 初始化配置
    if (configSchema.value && Object.keys(localConfig.value).length === 0) {
      resetConfigToDefault()
    }
  } catch (err: any) {
    error.value = err.message || '加载算法配置失败'
    console.error('加载算法配置失败:', err)
  } finally {
    loading.value = false
  }
}

const resetConfigToDefault = () => {
  if (!configSchema.value) return

  const config: Record<string, any> = {}
  for (const [key, schema] of Object.entries(configSchema.value.properties)) {
    config[key] = schema.default !== undefined ? schema.default : null
  }
  localConfig.value = config
  emit('update:config', config)
}

const handleConfigUpdate = (newConfig: Record<string, any>) => {
  localConfig.value = { ...newConfig }
  store.updateAlgorithmConfig(newConfig)
  emit('update:config', newConfig)
}

const handlePresetApplied = (preset: PresetConfig) => {
  emit('preset-applied', preset)
}

const retry = () => {
  if (store.selectedAlgorithm?.name) {
    loadAlgorithmConfig(store.selectedAlgorithm.name)
  }
}

// 初始化
onMounted(() => {
  if (store.selectedAlgorithm?.name) {
    loadAlgorithmConfig(store.selectedAlgorithm.name)
  }
})
</script>

<style scoped>
.algorithm-config-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  min-height: 200px;
}

.loading-state,
.error-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 2rem;
  background: var(--bg-secondary);
  border-radius: 0.5rem;
  text-align: center;
}

.loading-state p,
.error-state p,
.empty-state p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.spinner {
  width: 2rem;
  height: 2rem;
  border: 2px solid var(--border-color);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.btn-secondary:hover {
  background: var(--border-color);
}
</style>
