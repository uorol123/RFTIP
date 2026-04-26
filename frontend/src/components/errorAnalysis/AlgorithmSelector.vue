<template>
  <div class="algorithm-selector">
    <!-- 算法选择下拉框 -->
    <div class="selector-row">
      <label>分析算法</label>
      <select
        v-model="localSelectedAlgorithm"
        :disabled="loading || disabled"
        class="form-select"
        @change="handleAlgorithmChange"
      >
        <option value="">请选择算法</option>
        <option
          v-for="algorithm in algorithms"
          :key="algorithm.name"
          :value="algorithm.name"
        >
          {{ algorithm.display_name }}
        </option>
      </select>
    </div>

    <!-- 算法描述 -->
    <div v-if="selectedAlgorithmInfo" class="algorithm-description">
      <p>{{ selectedAlgorithmInfo.description }}</p>
      <div class="algorithm-meta">
        <span class="version">版本: {{ selectedAlgorithmInfo.version }}</span>
        <span v-if="selectedAlgorithmInfo.supports_elevation" class="badge">
          支持俯仰角
        </span>
      </div>
    </div>

    <!-- 预设配置选择 -->
    <div v-if="presets.length > 0" class="selector-row">
      <label>预设配置</label>
      <select
        v-model="localSelectedPreset"
        :disabled="disabled"
        class="form-select"
        @change="handlePresetChange"
      >
        <option value="">自定义配置</option>
        <option
          v-for="preset in presets"
          :key="preset.name"
          :value="preset.name"
        >
          {{ preset.display_name }}
        </option>
      </select>
    </div>

    <!-- 动态配置表单 -->
    <div v-if="configSchema && showCustomConfig" class="config-form">
      <h4>算法参数</h4>

      <div
        v-for="(schema, key) in sortedConfigProperties"
        :key="key"
        class="form-field"
      >
        <label :for="`config-${key}`">
          {{ schema.title || key }}
          <span v-if="isRequired(key)" class="required">*</span>
        </label>

        <!-- 数字类型输入 -->
        <input
          v-if="schema.type === 'number' || schema.type === 'integer'"
          :id="`config-${key}`"
          v-model.number="localConfig[key]"
          type="number"
          class="form-input"
          :min="schema.minimum"
          :max="schema.maximum"
          :step="schema.type === 'integer' ? 1 : 0.01"
        />

        <!-- 枚举类型（下拉选择） -->
        <select
          v-else-if="schema.enum && schema.enum.length > 0"
          :id="`config-${key}`"
          v-model="localConfig[key]"
          class="form-select"
        >
          <option
            v-for="option in schema.enum"
            :key="String(option)"
            :value="option"
          >
            {{ option }}
          </option>
        </select>

        <!-- 数组类型（逗号分隔） -->
        <input
          v-else-if="schema.type === 'array'"
          :id="`config-${key}`"
          v-model="arrayInputs[key]"
          type="text"
          class="form-input"
          placeholder="用逗号分隔，如: 0.1, 0.01"
          @input="handleArrayInput(key, $event)"
        />

        <!-- 默认文本输入 -->
        <input
          v-else
          :id="`config-${key}`"
          v-model="localConfig[key]"
          type="text"
          class="form-input"
        />

        <span v-if="schema.description" class="field-hint">
          {{ schema.description }}
        </span>
      </div>
    </div>

    <!-- 配置预览 -->
    <div v-if="localConfig" class="config-preview">
      <details>
        <summary>配置 JSON ({{ configJsonSize }} bytes)</summary>
        <pre>{{ JSON.stringify(localConfig, null, 2) }}</pre>
      </details>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useErrorAnalysisStore } from '@/stores/errorAnalysis'
import { algorithmsApi } from '@/api/errorAnalysis/algorithms'
import type { AlgorithmInfo, AlgorithmConfigSchema } from '@/types/errorAnalysis/algorithms'

interface Props {
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
})

const emit = defineEmits<{
  'update:algorithm': [algorithm: string]
  'update:config': [config: Record<string, any>]
}>()

const store = useErrorAnalysisStore()

// 本地状态
const localSelectedAlgorithm = ref<string>('')
const localSelectedPreset = ref<string | ''>('')
const localConfig = ref<Record<string, any>>({})
const arrayInputs = ref<Record<string, string>>({})
const loading = ref(false)

// 计算属性
const algorithms = computed(() => store.availableAlgorithms)
const selectedAlgorithmInfo = computed(() =>
  algorithms.value.find(a => a.name === localSelectedAlgorithm.value)
)
const presets = computed(() => store.currentPresets)
const configSchema = computed(() => store.currentConfigSchema)

const showCustomConfig = computed(() => !localSelectedPreset.value)

const configJsonSize = computed(() =>
  JSON.stringify(localConfig.value).length
)

// 排序后的配置属性（将必填字段排在前面）
const sortedConfigProperties = computed(() => {
  if (!configSchema.value?.properties) return {}

  const required = new Set(configSchema.value.required || [])
  const sorted: Record<string, any> = {}
  const optional: Record<string, any> = {}

  for (const [key, schema] of Object.entries(configSchema.value.properties)) {
    if (required.has(key)) {
      sorted[key] = schema
    } else {
      optional[key] = schema
    }
  }

  return { ...sorted, ...optional }
})

// 方法
const isRequired = (key: string) => {
  return configSchema.value?.required?.includes(key) ?? false
}

const handleAlgorithmChange = async () => {
  if (!localSelectedAlgorithm.value) return

  loading.value = true
  try {
    // 加载算法配置 Schema 和预设
    await Promise.all([
      store.loadAlgorithmConfigSchema(localSelectedAlgorithm.value),
      store.loadAlgorithmPresets(localSelectedAlgorithm.value),
    ])

    // 重置配置
    resetConfigToDefault()

    emit('update:algorithm', localSelectedAlgorithm.value)
    emit('update:config', localConfig.value)
  } catch (error: any) {
    console.error('加载算法配置失败:', error)
  } finally {
    loading.value = false
  }
}

const handlePresetChange = () => {
  if (localSelectedPreset.value) {
    const preset = presets.value.find(p => p.name === localSelectedPreset.value)
    if (preset) {
      localConfig.value = { ...preset.config }
      updateArrayInputs()
    }
  } else {
    resetConfigToDefault()
  }
  emit('update:config', localConfig.value)
}

const resetConfigToDefault = () => {
  if (!configSchema.value) return

  const config: Record<string, any> = {}
  for (const [key, schema] of Object.entries(configSchema.value.properties)) {
    config[key] = schema.default !== undefined ? schema.default : null
  }
  localConfig.value = config
  updateArrayInputs()
}

const updateArrayInputs = () => {
  for (const [key, value] of Object.entries(localConfig.value)) {
    if (Array.isArray(value)) {
      arrayInputs.value[key] = value.join(', ')
    }
  }
}

const handleArrayInput = (key: string, event: Event) => {
  const target = event.target as HTMLInputElement
  const strValue = target.value

  if (!strValue.trim()) {
    localConfig.value[key] = []
    return
  }

  // 尝试解析为数字数组或字符串数组
  const parts = strValue.split(',').map(s => s.trim())
  const numbers = parts.map(p => Number(p))

  if (numbers.every(n => !isNaN(n))) {
    localConfig.value[key] = numbers
  } else {
    localConfig.value[key] = parts
  }
}

// 监听配置变化
watch(localConfig, (newConfig) => {
  emit('update:config', newConfig)
}, { deep: true })

// 初始化
onMounted(async () => {
  // 加载算法列表
  loading.value = true
  try {
    await store.loadAlgorithms()
    if (algorithms.value.length > 0) {
      // 默认选择第一个算法
      localSelectedAlgorithm.value = algorithms.value[0].name
      await handleAlgorithmChange()
    }
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.algorithm-selector {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.selector-row {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.selector-row label {
  font-weight: 500;
  color: var(--color-text-secondary);
  font-size: 0.9rem;
}

.form-select,
.form-input {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  font-size: 0.9rem;
  background: var(--color-bg);
}

.form-select:disabled,
.form-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.algorithm-description {
  padding: 0.75rem;
  background: var(--color-bg-secondary);
  border-radius: 4px;
  font-size: 0.85rem;
}

.algorithm-description p {
  margin: 0;
  line-height: 1.5;
}

.algorithm-meta {
  display: flex;
  gap: 1rem;
  margin-top: 0.5rem;
  font-size: 0.8rem;
  color: var(--color-text-muted);
}

.version {
  font-family: monospace;
}

.badge {
  padding: 2px 8px;
  background: var(--color-primary);
  color: white;
  border-radius: 12px;
  font-size: 0.75rem;
}

.config-form {
  padding: 1rem;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  background: var(--color-bg-secondary);
}

.config-form h4 {
  margin: 0 0 1rem 0;
  font-size: 0.95rem;
  color: var(--color-text);
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  margin-bottom: 1rem;
}

.form-field label {
  font-size: 0.85rem;
  color: var(--color-text-secondary);
}

.required {
  color: var(--color-error);
}

.field-hint {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  margin-top: 0.25rem;
}

.config-preview {
  font-size: 0.8rem;
}

.config-preview details {
  cursor: pointer;
}

.config-preview summary {
  padding: 0.5rem;
  background: var(--color-bg-secondary);
  border-radius: 4px;
  user-select: none;
}

.config-preview pre {
  padding: 0.5rem;
  background: var(--color-bg);
  border-radius: 4px;
  overflow-x: auto;
  margin-top: 0.5rem;
  font-size: 0.75rem;
}
</style>
