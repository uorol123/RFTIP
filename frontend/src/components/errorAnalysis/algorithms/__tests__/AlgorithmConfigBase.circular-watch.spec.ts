/**
 * Issue #25: 多源参考分析页面卡死 - 循环 deep watch 测试
 *
 * 根因: AlgorithmConfigBase.vue 中 watch(localConfig, { deep: true }) emit 回父组件
 *      → 父组件更新 store/props → 触发 watch(props.modelValue, { deep: true })
 *      → localConfig = { ...newValue } 创建新对象 → 触发 watch(localConfig) → 无限循环
 */
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import AlgorithmConfigBase from '../AlgorithmConfigBase.vue'
import type { AlgorithmConfigSchema } from '@/types/errorAnalysis/algorithms'

const flushPromises = () => new Promise(resolve => setTimeout(resolve, 0))

const mockSchema: AlgorithmConfigSchema = {
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
    mode: {
      type: 'string',
      title: '模式',
      default: 'standard',
      enum: ['standard', 'high_precision', 'fast'],
    },
  },
  required: ['grid_resolution', 'time_window'],
}

describe('AlgorithmConfigBase - Issue #25 循环 watch 修复', () => {
  const mountComponent = (modelValue: Record<string, any> = { grid_resolution: 0.2, time_window: 60, mode: 'standard' }) => {
    const onUpdate = vi.fn()
    const wrapper = mount(AlgorithmConfigBase, {
      props: {
        modelValue,
        configSchema: mockSchema,
        showConfigPreview: false,
        'onUpdate:modelValue': onUpdate,
      },
    })
    return { wrapper, onUpdate }
  }

  it('挂载后不应因 immediate watch 触发多余的 emit', async () => {
    const { onUpdate } = mountComponent()

    await flushPromises()
    await flushPromises()

    // 初始同步不应产生回传 emit（值未变）
    const emitCount = onUpdate.mock.calls.length
    expect(emitCount).toBeLessThanOrEqual(1)
  })

  it('父组件回设相同值时不应触发 emit（打破循环）', async () => {
    const { wrapper, onUpdate } = mountComponent()

    await flushPromises()
    onUpdate.mockClear()

    // 模拟循环: 父组件将相同值通过 props 传回
    for (let i = 0; i < 5; i++) {
      await wrapper.setProps({
        modelValue: { grid_resolution: 0.2, time_window: 60, mode: 'standard' },
      })
      await flushPromises()
    }

    // 相同值不应触发任何 emit（循环已打破）
    expect(onUpdate.mock.calls.length).toBe(0)
  })

  it('用户修改配置值时应正确 emit', async () => {
    const { wrapper, onUpdate } = mountComponent()

    await flushPromises()
    onUpdate.mockClear()

    // 模拟用户修改 number input
    const inputs = wrapper.findAll('input[type="number"]')
    expect(inputs.length).toBeGreaterThan(0)

    await inputs[0].setValue(0.5)
    await flushPromises()

    // 值确实变了，应该 emit 一次
    expect(onUpdate.mock.calls.length).toBeGreaterThanOrEqual(1)
    expect(onUpdate.mock.calls[0][0]).toHaveProperty('grid_resolution')
  })

  it('用户修改枚举值时应正确 emit', async () => {
    const { wrapper, onUpdate } = mountComponent()

    await flushPromises()
    onUpdate.mockClear()

    const select = wrapper.find('select')
    expect(select.exists()).toBe(true)

    await select.setValue('high_precision')
    await flushPromises()

    expect(onUpdate.mock.calls.length).toBeGreaterThanOrEqual(1)
    const emitted = onUpdate.mock.calls[0][0]
    expect(emitted.mode).toBe('high_precision')
  })

  it('连续多次 setProps 相同值后，emit 总数应保持有限', async () => {
    const { wrapper, onUpdate } = mountComponent()
    await flushPromises()
    onUpdate.mockClear()

    // 快速连续 setProps 10 次，模拟高频循环
    for (let i = 0; i < 10; i++) {
      await wrapper.setProps({
        modelValue: { grid_resolution: 0.2, time_window: 60, mode: 'standard' },
      })
    }
    await flushPromises()

    // 不应有 emit（值始终相同）
    expect(onUpdate.mock.calls.length).toBe(0)
  })
})
