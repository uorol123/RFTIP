import { describe, it, expect } from 'vitest'
import routes from '../routes'

describe('路由配置', () => {
  function findRoute(path: string) {
    return routes.find(r => r.path === path)
  }

  it('/error-analysis 重定向到多源分析', () => {
    const route = findRoute('/error-analysis')
    expect(route).toBeDefined()
    expect(route!.redirect).toBe('/error-analysis/multi-source')
  })

  it('/error-analysis/multi-source 指向 MultiSourceAnalysis', () => {
    const route = findRoute('/error-analysis/multi-source')
    expect(route).toBeDefined()
    expect(route!.name).toBe('MultiSourceAnalysis')
    expect(route!.meta?.title).toContain('多源')
  })

  it('/error-analysis/single-source 指向 SingleSourceAnalysis', () => {
    const route = findRoute('/error-analysis/single-source')
    expect(route).toBeDefined()
    expect(route!.name).toBe('SingleSourceAnalysis')
    expect(route!.meta?.title).toContain('单源')
  })

  it('/error-analysis/tasks 指向 TaskManagement', () => {
    const route = findRoute('/error-analysis/tasks')
    expect(route).toBeDefined()
    expect(route!.name).toBe('TaskManagement')
    expect(route!.meta?.title).toContain('任务')
  })

  it('/error-analysis/history/:taskId 指向 ErrorAnalysisHistory', () => {
    const route = findRoute('/error-analysis/history/:taskId')
    expect(route).toBeDefined()
    expect(route!.name).toBe('ErrorAnalysisHistory')
  })

  it('/error-analysis/smoothed/:taskId 指向 SmoothedTrajectoryHistory', () => {
    const route = findRoute('/error-analysis/smoothed/:taskId')
    expect(route).toBeDefined()
    expect(route!.name).toBe('SmoothedTrajectoryHistory')
  })

  it('误差分析路由总数为 6', () => {
    const errorRoutes = routes.filter(r => r.path.startsWith('/error-analysis'))
    expect(errorRoutes.length).toBe(6)
  })
})
