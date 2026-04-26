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
      <div class="header">
        <h3>{{ algorithmInfo.display_name }}</h3>
        <p>{{ algorithmInfo.description }}</p>
      </div>
    </template>
    <template #content>
      <div class="content">
        <div class="section">
          <h4>参数预设</h4>
          <div class="preset-grid">
            <button v-for="preset in presets" :key="preset.name" class="preset-card"
              :class="{ active: selectedPreset === preset.name }" @click="applyPreset(preset)">
              <div class="preset-name">{{ preset.display_name }}</div>
              <div class="preset-desc">{{ getPresetDesc(preset.name) }}</div>
            </button>
          </div>
        </div>
        <div class="section">
          <h4>平滑参数</h4>
          <div class="subsection">
            <div class="form-row">
              <div class="form-group">
                <label>平滑因子</label>
                <input v-model.number="localConfig.smoothing_factor" type="number" step="0.01" min="0.001" max="100" class="form-input" :disabled="disabled" />
                <span class="hint">越大越平滑</span>
              </div>
              <div class="form-group">
                <label>样条阶数</label>
                <input v-model.number="localConfig.spline_degree" type="number" step="1" min="1" max="5" class="form-input" :disabled="disabled" />
              </div>
            </div>
            <div class="form-group">
              <label>
                <input type="checkbox" v-model="localConfig.interpolate" :disabled="disabled" />
                启用插值（增加轨迹密度）
              </label>
            </div>
            <div v-if="localConfig.interpolate" class="form-group">
              <label>插值密度</label>
              <input v-model.number="localConfig.interpolation_density" type="number" step="1" min="2" max="100" class="form-input" :disabled="disabled" />
            </div>
          </div>
        </div>
      </div>
    </template>
  </AlgorithmConfigBase>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import AlgorithmConfigBase from '../AlgorithmConfigBase.vue'
import type { AlgorithmInfo, PresetConfig, AlgorithmConfigSchema } from '@/types/errorAnalysis/algorithms'

interface Props {
  algorithmInfo: AlgorithmInfo; configSchema: AlgorithmConfigSchema | null
  modelValue: Record<string, any>; presets: PresetConfig[]; disabled?: boolean
  selectedStationCount?: number; selectedTrackCount?: number
}
const props = withDefaults(defineProps<Props>(), { disabled: false, selectedStationCount: 0, selectedTrackCount: 0 })
const emit = defineEmits<{ 'update:modelValue': [c: Record<string, any>]; 'preset-applied': [p: PresetConfig] }>()
const localConfig = ref<Record<string, any>>({ ...props.modelValue })
const selectedPreset = ref('')
watch(() => props.modelValue, v => { localConfig.value = { ...v } }, { deep: true, immediate: true })

const descMap: Record<string, string> = { standard: '默认三次样条', smooth: '更平滑', tight: '更贴合原始数据', interpolated: '插值增加密度' }
const getPresetDesc = (n: string) => descMap[n] || '自定义'
const applyPreset = (p: PresetConfig) => { selectedPreset.value = p.name; localConfig.value = { ...p.config }; emit('update:modelValue', localConfig.value) }
const handleConfigUpdate = (c: Record<string, any>) => { localConfig.value = { ...c }; selectedPreset.value = ''; emit('update:modelValue', c) }
</script>

<style scoped>
.header h3 { margin: 0 0 0.5rem; font-size: 1.1rem; }
.header p { margin: 0; font-size: 0.85rem; color: var(--text-secondary); }
.content { display: flex; flex-direction: column; gap: 1.5rem; }
.section h4 { margin: 0 0 0.75rem; font-size: 0.9rem; }
.preset-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.5rem; }
.preset-card { padding: 0.5rem; background: var(--bg-secondary); border: 2px solid transparent; border-radius: 0.5rem; cursor: pointer; text-align: left; transition: all 0.2s; }
.preset-card:hover { background: var(--bg-tertiary); }
.preset-card.active { border-color: var(--color-primary); }
.preset-name { font-weight: 500; font-size: 0.85rem; }
.preset-desc { font-size: 0.7rem; color: var(--text-muted); }
.subsection { display: flex; flex-direction: column; gap: 0.75rem; padding: 1rem; background: var(--bg-secondary); border-radius: 0.5rem; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; }
.form-group { display: flex; flex-direction: column; gap: 0.25rem; }
.form-group label { font-size: 0.75rem; font-weight: 500; color: var(--text-secondary); }
.form-input { padding: 0.5rem; border: 1px solid var(--border-color); border-radius: 0.375rem; background: var(--bg-tertiary); color: var(--text-primary); font-size: 0.85rem; }
.form-input:focus { outline: none; border-color: var(--color-primary); }
.form-input:disabled { opacity: 0.5; }
.hint { font-size: 0.65rem; color: var(--text-muted); }
</style>
