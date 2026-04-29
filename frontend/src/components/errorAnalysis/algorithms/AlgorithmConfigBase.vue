<template>
  <div class="algorithm-config-base">
    <slot name="header">
      <div class="config-header">
        <h3 class="config-title">{{ title }}</h3>
        <p v-if="description" class="config-description">{{ description }}</p>
      </div>
    </slot>

    <slot name="content">
      <div class="config-content">
        <!-- 默认内容：算法参数表单 -->
        <div v-if="configSchema" class="config-form">
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
              :disabled="disabled"
            />

            <!-- 枚举类型（下拉选择） -->
            <select
              v-else-if="schema.enum && schema.enum.length > 0"
              :id="`config-${key}`"
              v-model="localConfig[key]"
              class="form-select"
              :disabled="disabled"
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
              :disabled="disabled"
              @input="handleArrayInput(key, $event)"
            />

            <!-- 默认文本输入 -->
            <input
              v-else
              :id="`config-${key}`"
              v-model="localConfig[key]"
              type="text"
              class="form-input"
              :disabled="disabled"
            />

            <span v-if="schema.description" class="field-hint">
              {{ schema.description }}
            </span>
          </div>
        </div>
      </div>
    </slot>

    <slot name="footer">
      <div v-if="showConfigPreview" class="config-footer">
        <details class="config-preview">
          <summary>配置 JSON ({{ configJsonSize }} bytes)</summary>
          <pre>{{ JSON.stringify(localConfig, null, 2) }}</pre>
        </details>
      </div>
    </slot>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { AlgorithmConfigSchema } from '@/types/errorAnalysis/algorithms'

interface Props {
  title?: string
  description?: string
  configSchema?: AlgorithmConfigSchema | null
  modelValue: Record<string, any>
  disabled?: boolean
  showConfigPreview?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  title: '算法配置',
  description: '',
  configSchema: null,
  disabled: false,
  showConfigPreview: true,
})

const emit = defineEmits<{
  'update:modelValue': [config: Record<string, any>]
}>()

// 本地配置状态
const localConfig = ref<Record<string, any>>({ ...props.modelValue })
const arrayInputs = ref<Record<string, string>>({})

// 初始化数组输入 - 先定义函数
const updateArrayInputs = () => {
  for (const [key, value] of Object.entries(localConfig.value)) {
    if (Array.isArray(value)) {
      arrayInputs.value[key] = value.join(', ')
    }
  }
}

// 初始化数组输入
watch(() => props.modelValue, (newValue) => {
  localConfig.value = { ...newValue }
  updateArrayInputs()
}, { deep: true, immediate: true })

// 监听本地配置变化
watch(localConfig, (newValue) => {
  emit('update:modelValue', newValue)
}, { deep: true })

// 计算属性
const sortedConfigProperties = computed(() => {
  if (!props.configSchema?.properties) return {}

  const required = new Set(props.configSchema.required || [])
  const sorted: Record<string, any> = {}
  const optional: Record<string, any> = {}

  for (const [key, schema] of Object.entries(props.configSchema.properties)) {
    if (required.has(key)) {
      sorted[key] = schema
    } else {
      optional[key] = schema
    }
  }

  return { ...sorted, ...optional }
})

const configJsonSize = computed(() =>
  JSON.stringify(localConfig.value).length
)

// 方法
const isRequired = (key: string) => {
  return props.configSchema?.required?.includes(key) ?? false
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
</script>

<style scoped>
.algorithm-config-base {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.config-header {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.config-title {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.config-description {
  margin: 0;
  font-size: 0.875rem;
  color: var(--text-secondary);
  line-height: 1.5;
}

.config-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.config-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1rem;
  background: var(--bg-secondary);
  border-radius: 0.5rem;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.form-field label {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.required {
  color: var(--color-error);
}

.form-input,
.form-select {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 0.375rem;
  background: var(--bg-tertiary);
  color: var(--text-primary);
  font-size: 0.875rem;
  transition: all 0.2s;
}

.form-input:focus,
.form-select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

.form-input:disabled,
.form-select:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.field-hint {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.config-footer {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.config-preview {
  font-size: 0.8125rem;
}

.config-preview summary {
  padding: 0.5rem;
  background: var(--bg-secondary);
  border-radius: 0.375rem;
  cursor: pointer;
  user-select: none;
  color: var(--text-secondary);
}

.config-preview pre {
  padding: 0.5rem;
  background: var(--bg-tertiary);
  border-radius: 0.375rem;
  overflow-x: auto;
  margin-top: 0.5rem;
  font-size: 0.75rem;
}
</style>
