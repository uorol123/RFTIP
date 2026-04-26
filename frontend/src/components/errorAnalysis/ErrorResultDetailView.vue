<template>
  <div class="error-result-detail-view">
    <div class="section-header">
      <h3>雷达误差结果</h3>
      <p class="section-desc">
        基于匹配组计算得到的各雷达站系统误差。误差值越小，表示该雷达站的校准精度越高。
      </p>
    </div>

    <!-- 质量等级说明 -->
    <div class="quality-legend">
      <span class="legend-title">质量评级标准：</span>
      <span class="legend-item excellent">优秀 ≤ 阈值</span>
      <span class="legend-item good">良好 ≤ 2×阈值</span>
      <span class="legend-item fair">一般 ≤ 3×阈值</span>
      <span class="legend-item poor">较差 > 3×阈值</span>
    </div>

    <!-- 误差表格 -->
    <div class="error-table-container">
      <table class="error-table">
        <thead>
          <tr>
            <th>雷达站</th>
            <th>方位角误差</th>
            <th>距离误差</th>
            <th>俯仰角误差</th>
            <th>匹配点数</th>
            <th>置信度</th>
            <th>迭代次数</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="result in results" :key="result.id">
            <td class="station-name">
              <div class="station-info">
                <span class="name">{{ result.station_name }}</span>
                <span class="id">#{{ result.station_id }}</span>
              </div>
            </td>
            <td class="error-value">
              <div class="error-content">
                <span class="value" :class="`quality-${result.azimuth_quality}`">
                  {{ result.azimuth_error.toFixed(3) }}°
                </span>
                <div class="quality-badge" :class="result.azimuth_quality">
                  {{ qualityLabels[result.azimuth_quality] }}
                </div>
              </div>
            </td>
            <td class="error-value">
              <div class="error-content">
                <span class="value" :class="`quality-${result.range_quality}`">
                  {{ result.range_error.toFixed(1) }} m
                </span>
                <div class="quality-badge" :class="result.range_quality">
                  {{ qualityLabels[result.range_quality] }}
                </div>
              </div>
            </td>
            <td class="error-value">
              <div class="error-content">
                <span class="value" :class="`quality-${result.elevation_quality}`">
                  {{ result.elevation_error.toFixed(3) }}°
                </span>
                <div class="quality-badge" :class="result.elevation_quality">
                  {{ qualityLabels[result.elevation_quality] }}
                </div>
              </div>
            </td>
            <td class="match-count">{{ result.match_count }}</td>
            <td class="confidence">
              <div class="confidence-bar">
                <div
                  class="confidence-fill"
                  :style="{ width: `${(result.confidence || 0) * 100}%` }"
                ></div>
              </div>
              <span class="confidence-text">
                {{ result.confidence ? (result.confidence * 100).toFixed(0) : '-' }}%
              </span>
            </td>
            <td class="iterations">
              {{ result.iterations ?? '-' }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 误差可视化 -->
    <div class="error-charts">
      <div class="chart-card">
        <h4>方位角误差对比</h4>
        <div class="bar-chart" ref="azimuthChartRef"></div>
      </div>
      <div class="chart-card">
        <h4>距离误差对比</h4>
        <div class="bar-chart" ref="rangeChartRef"></div>
      </div>
    </div>

    <!-- 算法说明 -->
    <div class="algorithm-info">
      <h4>误差计算方法</h4>
      <div class="algo-content">
        <p><strong>基于梯度下降的迭代寻优算法</strong>通过分步优化，计算使所有匹配组总代价最小的雷达误差参数：</p>
        <div class="formula">
          <code>J = w₁×方差 + w₂×Σ(方位角²) + w₃×Σ(距离²) + w₄×Σ(俯仰角²)</code>
        </div>
        <p>依次优化：方位角误差 → 距离误差 → 俯仰角误差（坐标下降法 + 多步长梯度下降）</p>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="results.length === 0" class="empty-state">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
      </svg>
      <p>暂无误差结果</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'
import type { ErrorResultDetail } from '@/types/errorAnalysis'
import * as echarts from 'echarts'

const props = defineProps<{
  results: ErrorResultDetail[]
}>()

const azimuthChartRef = ref<HTMLElement>()
const rangeChartRef = ref<HTMLElement>()

const qualityLabels: Record<string, string> = {
  excellent: '优秀',
  good: '良好',
  fair: '一般',
  poor: '较差',
  unknown: '未知',
}

function renderCharts() {
  nextTick(() => {
    if (azimuthChartRef.value && props.results.length > 0) {
      const azimuthChart = echarts.init(azimuthChartRef.value)
      azimuthChart.setOption({
        tooltip: { trigger: 'axis' },
        xAxis: {
          type: 'category',
          data: props.results.map(r => r.station_name),
          axisLabel: { rotate: 30 }
        },
        yAxis: { type: 'value', name: '度 (°)' },
        series: [{
          type: 'bar',
          data: props.results.map(r => ({
            value: Math.abs(r.azimuth_error),
            itemStyle: {
              color: r.azimuth_quality === 'excellent' ? '#10b981' :
                     r.azimuth_quality === 'good' ? '#3b82f6' :
                     r.azimuth_quality === 'fair' ? '#f59e0b' : '#ef4444'
            }
          }))
        }]
      })
    }

    if (rangeChartRef.value && props.results.length > 0) {
      const rangeChart = echarts.init(rangeChartRef.value)
      rangeChart.setOption({
        tooltip: { trigger: 'axis' },
        xAxis: {
          type: 'category',
          data: props.results.map(r => r.station_name),
          axisLabel: { rotate: 30 }
        },
        yAxis: { type: 'value', name: '米 (m)' },
        series: [{
          type: 'bar',
          data: props.results.map(r => ({
            value: Math.abs(r.range_error),
            itemStyle: {
              color: r.range_quality === 'excellent' ? '#10b981' :
                     r.range_quality === 'good' ? '#3b82f6' :
                     r.range_quality === 'fair' ? '#f59e0b' : '#ef4444'
            }
          }))
        }]
      })
    }
  })
}

watch(() => props.results, renderCharts, { deep: true })

onMounted(() => {
  if (props.results.length > 0) {
    renderCharts()
  }
})
</script>

<style scoped>
.error-result-detail-view {
  padding: 8px 0;
}

.section-header {
  margin-bottom: 20px;
}

.section-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.section-desc {
  font-size: 13px;
  color: #6b7280;
  margin: 0;
  line-height: 1.6;
}

.quality-legend {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 16px;
  background: #f9fafb;
  border-radius: 8px;
  margin-bottom: 20px;
  font-size: 12px;
}

.legend-title {
  color: #6b7280;
  font-weight: 500;
}

.legend-item {
  padding: 2px 8px;
  border-radius: 4px;
  color: white;
}

.legend-item.excellent { background: #10b981; }
.legend-item.good { background: #3b82f6; }
.legend-item.fair { background: #f59e0b; }
.legend-item.poor { background: #ef4444; }

.error-table-container {
  overflow-x: auto;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  margin-bottom: 24px;
}

.error-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

th, td {
  padding: 14px 16px;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

th {
  background: #fafafa;
  font-weight: 500;
  color: #6b7280;
  font-size: 12px;
}

tr:last-child td {
  border-bottom: none;
}

tr:hover {
  background: #fafafa;
}

.station-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.station-info .name {
  font-weight: 600;
  color: #1f2937;
}

.station-info .id {
  font-size: 11px;
  color: #9ca3af;
  font-family: monospace;
}

.error-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.error-value .value {
  font-family: monospace;
  font-weight: 600;
}

.error-value .value.quality-excellent { color: #10b981; }
.error-value .value.quality-good { color: #3b82f6; }
.error-value .value.quality-fair { color: #f59e0b; }
.error-value .value.quality-poor { color: #ef4444; }
.error-value .value.quality-unknown { color: #9ca3af; }

.quality-badge {
  display: inline-block;
  padding: 1px 6px;
  border-radius: 3px;
  font-size: 10px;
  color: white;
  width: fit-content;
}

.quality-badge.excellent { background: #10b981; }
.quality-badge.good { background: #3b82f6; }
.quality-badge.fair { background: #f59e0b; }
.quality-badge.poor { background: #ef4444; }
.quality-badge.unknown { background: #9ca3af; }

.match-count {
  color: #374151;
}

.confidence {
  display: flex;
  align-items: center;
  gap: 8px;
}

.confidence-bar {
  width: 60px;
  height: 6px;
  background: #e5e7eb;
  border-radius: 3px;
  overflow: hidden;
}

.confidence-fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #10b981);
  border-radius: 3px;
}

.confidence-text {
  font-size: 12px;
  color: #6b7280;
  min-width: 32px;
}

.iterations {
  color: #6b7280;
  font-family: monospace;
}

.error-charts {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.chart-card {
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.chart-card h4 {
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 16px 0;
}

.bar-chart {
  height: 200px;
}

.algorithm-info {
  padding: 20px;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.algorithm-info h4 {
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 12px 0;
}

.algo-content p {
  font-size: 13px;
  color: #4b5563;
  margin: 0 0 8px 0;
  line-height: 1.6;
}

.formula {
  padding: 12px 16px;
  background: white;
  border-radius: 6px;
  margin: 12px 0;
}

.formula code {
  font-size: 14px;
  font-family: 'Monaco', 'Menlo', monospace;
  color: #7c3aed;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px;
  color: #9ca3af;
}

.empty-state svg {
  width: 48px;
  height: 48px;
  margin-bottom: 16px;
}

.empty-state p {
  margin: 0;
  font-size: 14px;
}
</style>
