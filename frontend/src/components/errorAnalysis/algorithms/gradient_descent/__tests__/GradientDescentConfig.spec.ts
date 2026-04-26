/**
 * GradientDescentConfig 组件测试
 */
import { describe, it, expect, beforeEach } from 'vitest'
import { mount, VueWrapper } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import GradientDescentConfig from '../GradientDescentConfig.vue'
import AlgorithmConfigBase from '../../AlgorithmConfigBase.vue'
import type { AlgorithmInfo, AlgorithmConfigSchema, PresetConfig } from '@/types/errorAnalysis/algorithms'

describe('GradientDescentConfig', () => {
  let wrapper: VueWrapper<any>

  const mockAlgorithmInfo: AlgorithmInfo = {
    name: 'gradient_descent',
    version: '1.0.0',
    display_name: '基于梯度下降的迭代寻优算法',
    description: '通过航迹匹配和梯度下降优化计算雷达系统误差',
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
      optimization_steps: {
        type: 'array',
        title: '优化步长',
        default: [0.1, 0.01],
      },
      cost_weights: {
        type: 'object',
        title: '代价函数权重',
        properties: {
          variance: { type: 'number', default: 100.0 },
          azimuth_error_square: { type: 'number', default: 0.15 },
          range_error_square: { type: 'number', default: 6e-7 },
          elevation_error_square: { type: 'number', default: 0.1 },
        },
      },
    },
    required: ['grid_resolution', 'time_window'],
  }

  const mockPresets: PresetConfig[] = [
    {
      name: 'standard',
      display_name: '标准配置',
      config: {
        grid_resolution: 0.2,
        time_window: 60,
        optimization_steps: [0.1, 0.01],
        cost_weights: {
          variance: 100.0,
          azimuth_error_square: 0.15,
          range_error_square: 6e-7,
          elevation_error_square: 0.1,
        },
      },
    },
    {
      name: 'high_precision',
      display_name: '高精度配置',
      config: {
        grid_resolution: 0.1,
        time_window: 30,
        optimization_steps: [0.05, 0.01, 0.005],
        cost_weights: {
          variance: 150.0,
          azimuth_error_square: 0.2,
          range_error_square: 8e-7,
          elevation_error_square: 0.15,
        },
      },
    },
  ]

  const defaultConfig = {
    grid_resolution: 0.2,
    time_window: 60,
    match_distance_threshold: 0.12,
    min_track_points: 10,
    optimization_steps: [0.1, 0.01],
    range_optimization_steps: [1000, 800, 500, 200, 100, 50, 20],
    max_match_groups: 15000,
    cost_weights: {
      variance: 100.0,
      azimuth_error_square: 0.15,
      range_error_square: 6e-7,
      elevation_error_square: 0.1,
    },
  }

  beforeEach(() => {
    const pinia = createPinia()
    setActivePinia(pinia)
  })

  it('应该正确渲染算法信息', () => {
    wrapper = mount(GradientDescentConfig, {
      global: {
        plugins: [createPinia()],
        stubs: {
          AlgorithmConfigBase: true,
        },
      },
      props: {
        algorithmInfo: mockAlgorithmInfo,
        configSchema: mockConfigSchema,
        modelValue: { ...defaultConfig },
        presets: mockPresets,
        disabled: false,
        selectedStationCount: 3,
        selectedTrackCount: 5,
      },
    })

    expect(wrapper.find('.config-title').text()).toBe(mockAlgorithmInfo.display_name)
    expect(wrapper.find('.config-description').text()).toBe(mockAlgorithmInfo.description)
  })

  it('应该显示算法元信息', () => {
    wrapper = mount(GradientDescentConfig, {
      global: {
        plugins: [createPinia()],
        stubs: {
          AlgorithmConfigBase: true,
        },
      },
      props: {
        algorithmInfo: mockAlgorithmInfo,
        configSchema: mockConfigSchema,
        modelValue: { ...defaultConfig },
        presets: mockPresets,
        disabled: false,
      },
    })

    expect(wrapper.find('.version').text()).toContain('1.0.0')
    expect(wrapper.find('.badge').exists()).toBe(true)
    expect(wrapper.find('.badge').text()).toBe('支持俯仰角')
  })

  it('应该渲染所有预设配置', () => {
    wrapper = mount(GradientDescentConfig, {
      global: {
        plugins: [createPinia()],
        stubs: {
          AlgorithmConfigBase: true,
        },
      },
      props: {
        algorithmInfo: mockAlgorithmInfo,
        configSchema: mockConfigSchema,
        modelValue: { ...defaultConfig },
        presets: mockPresets,
        disabled: false,
      },
    })

    const presetCards = wrapper.findAll('.preset-card')
    expect(presetCards.length).toBe(2)
    expect(presetCards[0].text()).toContain('标准配置')
    expect(presetCards[1].text()).toContain('高精度配置')
  })

  it('应该在点击预设时应用配置', async () => {
    wrapper = mount(GradientDescentConfig, {
      global: {
        plugins: [createPinia()],
        stubs: {
          AlgorithmConfigBase: true,
        },
      },
      props: {
        algorithmInfo: mockAlgorithmInfo,
        configSchema: mockConfigSchema,
        modelValue: { ...defaultConfig },
        presets: mockPresets,
        disabled: false,
      },
    })

    const presetCards = wrapper.findAll('.preset-card')
    await presetCards[1].trigger('click')

    // 验证事件触发
    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    expect(wrapper.emitted('preset-applied')).toBeTruthy()
  })

  it('应该正确显示数据选择信息', () => {
    wrapper = mount(GradientDescentConfig, {
      global: {
        plugins: [createPinia()],
        stubs: {
          AlgorithmConfigBase: true,
        },
      },
      props: {
        algorithmInfo: mockAlgorithmInfo,
        configSchema: mockConfigSchema,
        modelValue: { ...defaultConfig },
        presets: mockPresets,
        disabled: false,
        selectedStationCount: 3,
        selectedTrackCount: 5,
      },
    })

    expect(wrapper.find('.station-count').text()).toBe('已选择 3 个雷达站')
    expect(wrapper.find('.track-count').text()).toBe('已选择 5 条轨迹')
  })

  it('应该正确处理优化步长的字符串输入', async () => {
    wrapper = mount(GradientDescentConfig, {
      global: {
        plugins: [createPinia()],
        stubs: {
          AlgorithmConfigBase: true,
        },
      },
      props: {
        algorithmInfo: mockAlgorithmInfo,
        configSchema: mockConfigSchema,
        modelValue: { ...defaultConfig },
        presets: mockPresets,
        disabled: false,
      },
    })

    const input = wrapper.find('input[placeholder="用逗号分隔，例如: 0.1, 0.01"]')
    await input.setValue('0.5, 0.1, 0.01')

    // 验证配置更新
    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
  })

  it('应该正确禁用所有输入', () => {
    wrapper = mount(GradientDescentConfig, {
      global: {
        plugins: [createPinia()],
        stubs: {
          AlgorithmConfigBase: true,
        },
      },
      props: {
        algorithmInfo: mockAlgorithmInfo,
        configSchema: mockConfigSchema,
        modelValue: { ...defaultConfig },
        presets: mockPresets,
        disabled: true,
      },
    })

    const inputs = wrapper.findAll('input')
    inputs.forEach(input => {
      expect(input.attributes('disabled')).toBeDefined()
    })
  })
})
