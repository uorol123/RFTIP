/**
 * AlgorithmConfigContainer 组件测试
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, VueWrapper } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import AlgorithmConfigContainer from '../AlgorithmConfigContainer.vue'
import { useErrorAnalysisStore } from '@/stores/errorAnalysis'
import type { AlgorithmInfo, AlgorithmConfigSchema, PresetConfig } from '@/types/errorAnalysis/algorithms'

// Mock store
vi.mock('@/stores/errorAnalysis', () => ({
  useErrorAnalysisStore: vi.fn(() => ({
    selectedAlgorithm: null,
    currentConfigSchema: null,
    currentPresets: [],
    currentAlgorithmConfig: {},
    loadAlgorithmConfigSchema: vi.fn(),
    loadAlgorithmPresets: vi.fn(),
    updateAlgorithmConfig: vi.fn(),
  })),
}))

describe('AlgorithmConfigContainer', () => {
  let wrapper: VueWrapper<any>
  let store: any

  const mockAlgorithmInfo: AlgorithmInfo = {
    name: 'gradient_descent',
    version: '1.0.0',
    display_name: '基于梯度下降的迭代寻优算法',
    description: '通过航迹匹配和梯度下降优化计算雷达误差',
    supports_elevation: true,
  }

  const mockConfigSchema: AlgorithmConfigSchema = {
    type: 'object',
    properties: {
      grid_resolution: {
        type: 'number',
        title: '网格分辨率',
        default: 0.2,
        minimum: 0.01,
        maximum: 1.0,
      },
      time_window: {
        type: 'number',
        title: '时间窗口',
        default: 60,
        minimum: 10,
        maximum: 600,
      },
    },
    required: ['grid_resolution', 'time_window'],
  }

  const mockPresets: PresetConfig[] = [
    {
      name: 'standard',
      display_name: '标准配置',
      config: { grid_resolution: 0.2, time_window: 60 },
    },
    {
      name: 'high_precision',
      display_name: '高精度配置',
      config: { grid_resolution: 0.1, time_window: 30 },
    },
  ]

  beforeEach(() => {
    // 创建新的 pinia 实例
    const pinia = createPinia()
    setActivePinia(pinia)

    // 获取 store 实例
    store = useErrorAnalysisStore()

    // 设置默认返回值
    store.selectedAlgorithm = mockAlgorithmInfo
    store.currentConfigSchema = mockConfigSchema
    store.currentPresets = mockPresets
    store.currentAlgorithmConfig = {}
  })

  it('应该正确渲染加载状态', () => {
    store.selectedAlgorithm = null

    wrapper = mount(AlgorithmConfigContainer, {
      global: {
        plugins: [createPinia()],
      },
    })

    expect(wrapper.find('.loading-state').exists()).toBe(true)
  })

  it('应该正确渲染算法配置组件', async () => {
    wrapper = mount(AlgorithmConfigContainer, {
      global: {
        plugins: [createPinia()],
        stubs: {
          GradientDescentConfig: true,
        },
      },
    })

    await wrapper.vm.$nextTick()

    // 验证算法信息传递
    expect(wrapper.vm.algorithmInfo).toEqual(mockAlgorithmInfo)
    expect(wrapper.vm.configSchema).toEqual(mockConfigSchema)
    expect(wrapper.vm.presets).toEqual(mockPresets)
  })

  it('应该在配置更新时触发事件', async () => {
    wrapper = mount(AlgorithmConfigContainer, {
      global: {
        plugins: [createPinia()],
        stubs: {
          GradientDescentConfig: {
            template: '<div @click="$emit(\'update:modelValue\', { grid_resolution: 0.3 })">Mock</div>',
          },
        },
      },
      props: {
        disabled: false,
        selectedStationCount: 3,
        selectedTrackCount: 5,
      },
    })

    await wrapper.vm.$nextTick()

    // 模拟配置更新
    await wrapper.vm.handleConfigUpdate({ grid_resolution: 0.3 })

    // 验证事件触发
    expect(wrapper.emitted('update:config')).toBeTruthy()
    expect(wrapper.emitted('update:config')[0]).toEqual([{ grid_resolution: 0.3 }])
  })

  it('应该在预设应用时触发事件', async () => {
    wrapper = mount(AlgorithmConfigContainer, {
      global: {
        plugins: [createPinia()],
        stubs: {
          GradientDescentConfig: {
            template: '<div @click="$emit(\'preset-applied\', presets[0])">Mock</div>',
          },
        },
      },
      props: {
        disabled: false,
      },
    })

    await wrapper.vm.$nextTick()

    const preset = mockPresets[0]
    await wrapper.vm.handlePresetApplied(preset)

    expect(wrapper.emitted('preset-applied')).toBeTruthy()
    expect(wrapper.emitted('preset-applied')[0]).toEqual([preset])
  })

  it('应该正确处理禁用状态', () => {
    wrapper = mount(AlgorithmConfigContainer, {
      global: {
        plugins: [createPinia()],
        stubs: {
          GradientDescentConfig: true,
        },
      },
      props: {
        disabled: true,
      },
    })

    expect(wrapper.props('disabled')).toBe(true)
  })

  it('应该显示错误状态', async () => {
    // 模拟加载失败
    store.loadAlgorithmConfigSchema = vi.fn().mockRejectedValue(new Error('加载失败'))

    wrapper = mount(AlgorithmConfigContainer, {
      global: {
        plugins: [createPinia()],
      },
    })

    await wrapper.vm.$nextTick()
    await wrapper.vm.loadAlgorithmConfig('gradient_descent')

    expect(wrapper.vm.error).toBeTruthy()
    expect(wrapper.find('.error-state').exists()).toBe(true)
  })
})
