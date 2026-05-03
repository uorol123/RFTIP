import { describe, it, expect } from 'vitest'
import { SINGLE_SOURCE_ALGORITHMS } from '@/types/errorAnalysis'

function isSingleSourceAlgorithm(name?: string): boolean {
  return !!name && SINGLE_SOURCE_ALGORITHMS.includes(name)
}

function getAlgorithmType(name?: string): string {
  return isSingleSourceAlgorithm(name) ? 'single_source' : 'multi_source'
}

describe('TaskManagement 辅助函数', () => {
  describe('isSingleSourceAlgorithm', () => {
    it('kalman 是单源算法', () => {
      expect(isSingleSourceAlgorithm('kalman')).toBe(true)
    })

    it('particle_filter 是单源算法', () => {
      expect(isSingleSourceAlgorithm('particle_filter')).toBe(true)
    })

    it('spline 是单源算法', () => {
      expect(isSingleSourceAlgorithm('spline')).toBe(true)
    })

    it('mrra 不是单源算法', () => {
      expect(isSingleSourceAlgorithm('mrra')).toBe(false)
    })

    it('ransac 不是单源算法', () => {
      expect(isSingleSourceAlgorithm('ransac')).toBe(false)
    })

    it('undefined 返回 false', () => {
      expect(isSingleSourceAlgorithm(undefined)).toBe(false)
    })

    it('空字符串返回 false', () => {
      expect(isSingleSourceAlgorithm('')).toBe(false)
    })

    it('未知算法名返回 false', () => {
      expect(isSingleSourceAlgorithm('unknown_algo')).toBe(false)
    })
  })

  describe('getAlgorithmType', () => {
    it('单源算法返回 single_source', () => {
      expect(getAlgorithmType('kalman')).toBe('single_source')
      expect(getAlgorithmType('particle_filter')).toBe('single_source')
      expect(getAlgorithmType('spline')).toBe('single_source')
    })

    it('多源算法返回 multi_source', () => {
      expect(getAlgorithmType('mrra')).toBe('multi_source')
      expect(getAlgorithmType('ransac')).toBe('multi_source')
      expect(getAlgorithmType('weighted_lstsq')).toBe('multi_source')
      expect(getAlgorithmType('ransac_heuristic')).toBe('multi_source')
    })

    it('undefined 默认返回 multi_source', () => {
      expect(getAlgorithmType(undefined)).toBe('multi_source')
    })
  })
})
