import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, VueWrapper } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import AlgorithmSelector from '../AlgorithmSelector.vue'

const MULTI_SOURCE_ALGORITHMS = [
  { name: 'mrra', display_name: 'MRRA', version: '1.0', description: '', supports_elevation: true },
  { name: 'ransac', display_name: 'RANSAC', version: '1.0', description: '', supports_elevation: false },
  { name: 'weighted_lstsq', display_name: '加权最小二乘', version: '1.0', description: '', supports_elevation: false },
  { name: 'ransac_heuristic', display_name: 'RANSAC启发式', version: '1.0', description: '', supports_elevation: false },
]

const SINGLE_SOURCE_ALGORITHMS = [
  { name: 'kalman', display_name: '卡尔曼滤波', version: '1.0', description: '', supports_elevation: false },
  { name: 'particle_filter', display_name: '粒子滤波', version: '1.0', description: '', supports_elevation: false },
  { name: 'spline', display_name: '样条插值', version: '1.0', description: '', supports_elevation: false },
]

const ALL_ALGORITHMS = [...MULTI_SOURCE_ALGORITHMS, ...SINGLE_SOURCE_ALGORITHMS]

vi.mock('@/stores/errorAnalysis', () => ({
  useErrorAnalysisStore: vi.fn(() => ({
    availableAlgorithms: ALL_ALGORITHMS,
    currentPresets: [],
    currentConfigSchema: null,
    selectedAlgorithm: null,
    loadAlgorithms: vi.fn().mockResolvedValue(undefined),
    loadAlgorithmConfigSchema: vi.fn().mockResolvedValue(undefined),
    loadAlgorithmPresets: vi.fn().mockResolvedValue(undefined),
  })),
}))

describe('AlgorithmSelector 算法过滤', () => {
  let wrapper: VueWrapper<any>

  beforeEach(() => {
    const pinia = createPinia()
    setActivePinia(pinia)
  })

  async function mountSelector(mode?: 'all' | 'multi_source' | 'single_source') {
    wrapper = mount(AlgorithmSelector, {
      props: { mode },
      global: { plugins: [createPinia()] },
    })
    await wrapper.vm.$nextTick()
  }

  it('mode=multi_source 只显示多源算法', async () => {
    await mountSelector('multi_source')
    const options = wrapper.findAll('select option')
    const values = options.map(o => o.attributes('value')).filter(v => v !== '')
    expect(values).toEqual(expect.arrayContaining(['mrra', 'ransac', 'weighted_lstsq', 'ransac_heuristic']))
    expect(values).not.toContain('kalman')
    expect(values).not.toContain('particle_filter')
    expect(values).not.toContain('spline')
  })

  it('mode=single_source 只显示单源算法', async () => {
    await mountSelector('single_source')
    const options = wrapper.findAll('select option')
    const values = options.map(o => o.attributes('value')).filter(v => v !== '')
    expect(values).toEqual(expect.arrayContaining(['kalman', 'particle_filter', 'spline']))
    expect(values).not.toContain('mrra')
    expect(values).not.toContain('ransac')
  })

  it('mode=all 显示全部算法', async () => {
    await mountSelector('all')
    const options = wrapper.findAll('select option')
    const values = options.map(o => o.attributes('value')).filter(v => v !== '')
    expect(values.length).toBe(ALL_ALGORITHMS.length)
  })

  it('默认 mode=all', async () => {
    await mountSelector()
    const options = wrapper.findAll('select option')
    const values = options.map(o => o.attributes('value')).filter(v => v !== '')
    expect(values.length).toBe(ALL_ALGORITHMS.length)
  })
})
