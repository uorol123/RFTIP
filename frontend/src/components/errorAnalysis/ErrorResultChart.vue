<template>
  <div class="error-result-chart">
    <div class="chart-header">
      <h3 class="chart-title">误差分析结果</h3>
      <div class="chart-actions">
        <button class="btn btn-secondary btn-sm" @click="exportChart">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
          </svg>
          导出图表
        </button>
      </div>
    </div>

    <div v-if="loading" class="chart-loading">
      <div class="spinner"></div>
      <span>加载中...</span>
    </div>

    <div v-else-if="!chartData" class="chart-empty">
      <EmptyState
        title="暂无图表数据"
        description="完成分析后将显示图表"
      />
    </div>

    <div v-else class="chart-content">
      <!-- 误差对比柱状图 -->
      <div class="chart-section">
        <h4 class="chart-section-title">各雷达站误差对比</h4>
        <div ref="barChartRef" class="chart-container"></div>
      </div>

      <!-- 匹配统计柱状图 -->
      <div class="chart-section">
        <h4 class="chart-section-title">匹配点数量</h4>
        <div ref="pieChartRef" class="chart-container pie-chart-container"></div>
      </div>

      <!-- 图表说明 -->
      <div class="chart-legend">
        <div class="legend-item">
          <span class="legend-color" style="background: #3b82f6;"></span>
          <span class="legend-label">方位角误差</span>
        </div>
        <div class="legend-item">
          <span class="legend-color" style="background: #8b5cf6;"></span>
          <span class="legend-label">距离误差</span>
        </div>
        <div class="legend-item">
          <span class="legend-color" style="background: #10b981;"></span>
          <span class="legend-label">俯仰角误差</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import EmptyState from '@/components/EmptyState.vue'
import type { ChartDataResponse } from '@/types/errorAnalysis'

interface Props {
  chartData: ChartDataResponse | null
  loading: boolean
}

const props = defineProps<Props>()

const barChartRef = ref<HTMLElement>()
const pieChartRef = ref<HTMLElement>()

let barChart: echarts.ECharts | null = null
let pieChart: echarts.ECharts | null = null

// 初始化柱状图 - 显示各雷达站的误差
function initBarChart() {
  if (!barChartRef.value || !props.chartData) return

  if (barChart) {
    barChart.dispose()
  }

  barChart = echarts.init(barChartRef.value)

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow',
      },
    },
    legend: {
      show: false,
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      data: props.chartData.stations,
      axisLabel: {
        rotate: 45,
        interval: 0,
      },
    },
    yAxis: {
      type: 'value',
      name: '误差值',
      axisLabel: {
        formatter: '{value}',
      },
    },
    series: [
      {
        name: '方位角误差',
        type: 'bar',
        data: props.chartData.azimuth_errors,
        itemStyle: {
          color: '#3b82f6',
          borderRadius: [4, 4, 0, 0],
        },
      },
      {
        name: '距离误差',
        type: 'bar',
        data: props.chartData.range_errors,
        itemStyle: {
          color: '#8b5cf6',
          borderRadius: [4, 4, 0, 0],
        },
      },
      {
        name: '俯仰角误差',
        type: 'bar',
        data: props.chartData.elevation_errors,
        itemStyle: {
          color: '#10b981',
          borderRadius: [4, 4, 0, 0],
        },
      },
    ],
  }

  barChart.setOption(option)
}

// 初始化柱状图 - 显示匹配点数量
function initPieChart() {
  if (!pieChartRef.value || !props.chartData) return

  if (pieChart) {
    pieChart.dispose()
  }

  pieChart = echarts.init(pieChartRef.value)

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow',
      },
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      data: props.chartData.stations,
      axisLabel: {
        rotate: 45,
        interval: 0,
      },
    },
    yAxis: {
      type: 'value',
      name: '匹配点数',
      axisLabel: {
        formatter: '{value}',
      },
    },
    series: [
      {
        name: '匹配点数',
        type: 'bar',
        data: props.chartData.match_counts,
        itemStyle: {
          color: '#f59e0b',
          borderRadius: [4, 4, 0, 0],
        },
      },
    ],
  }

  pieChart.setOption(option)
}

// 更新图表
function updateCharts() {
  if (props.chartData) {
    nextTick(() => {
      initBarChart()
      initPieChart()
    })
  }
}

// 导出图表
function exportChart() {
  if (barChart) {
    const url = barChart.getDataURL({
      type: 'png',
      pixelRatio: 2,
      backgroundColor: '#fff',
    })
    const link = document.createElement('a')
    link.href = url
    link.download = `error-comparison-${Date.now()}.png`
    link.click()
  }
}

// 响应式调整
function handleResize() {
  barChart?.resize()
  pieChart?.resize()
}

onMounted(() => {
  updateCharts()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  barChart?.dispose()
  pieChart?.dispose()
})

watch(() => props.chartData, updateCharts, { deep: true })
</script>

<style scoped>
.error-result-chart {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 1.5rem;
  background: var(--bg-secondary);
  border-radius: 0.75rem;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-title {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
}

.chart-actions {
  display: flex;
  gap: 0.5rem;
}

.chart-loading,
.chart-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 3rem;
  color: var(--text-muted);
}

.spinner {
  width: 2rem;
  height: 2rem;
  border: 3px solid var(--border-color);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.chart-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.chart-section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.chart-section-title {
  margin: 0;
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--text-primary);
}

.chart-container {
  width: 100%;
  height: 300px;
  background: var(--bg-tertiary);
  border-radius: 0.5rem;
  padding: 0.5rem;
}

.pie-chart-container {
  height: 200px;
}

.chart-legend {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.legend-color {
  width: 1rem;
  height: 1rem;
  border-radius: 0.25rem;
}

.legend-label {
  font-size: 0.8125rem;
  color: var(--text-secondary);
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.8125rem;
}

.btn-secondary {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.btn-secondary:hover {
  background: var(--border-color);
}

.btn svg {
  width: 1rem;
  height: 1rem;
}
</style>
