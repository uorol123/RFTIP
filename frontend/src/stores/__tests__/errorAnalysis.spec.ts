import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useErrorAnalysisStore } from '@/stores/errorAnalysis'

describe('ErrorAnalysisStore 算法模式', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('初始状态为 multi_source（无算法选中）', () => {
    const store = useErrorAnalysisStore()
    expect(store.isSingleSourceMode).toBe(false)
    expect(store.isMultiSourceMode).toBe(true)
  })

  it('选择 kalman 后切换为 single_source', async () => {
    const store = useErrorAnalysisStore()
    store.availableAlgorithms = [
      { name: 'kalman', display_name: '卡尔曼', version: '1.0', description: '', supports_elevation: false },
    ] as any
    store.selectedAlgorithm = { name: 'kalman' } as any
    expect(store.isSingleSourceMode).toBe(true)
    expect(store.isMultiSourceMode).toBe(false)
  })

  it('选择 mrra 后为 multi_source', () => {
    const store = useErrorAnalysisStore()
    store.selectedAlgorithm = { name: 'mrra' } as any
    expect(store.isSingleSourceMode).toBe(false)
    expect(store.algorithmMode).toBe('multi_source')
  })

  it('选择 particle_filter 后为 single_source', () => {
    const store = useErrorAnalysisStore()
    store.selectedAlgorithm = { name: 'particle_filter' } as any
    expect(store.isSingleSourceMode).toBe(true)
    expect(store.algorithmMode).toBe('single_source')
  })

  it('选择 spline 后为 single_source', () => {
    const store = useErrorAnalysisStore()
    store.selectedAlgorithm = { name: 'spline' } as any
    expect(store.isSingleSourceMode).toBe(true)
  })

  it('选择 ransac 后为 multi_source', () => {
    const store = useErrorAnalysisStore()
    store.selectedAlgorithm = { name: 'ransac' } as any
    expect(store.isSingleSourceMode).toBe(false)
    expect(store.algorithmMode).toBe('multi_source')
  })
})
