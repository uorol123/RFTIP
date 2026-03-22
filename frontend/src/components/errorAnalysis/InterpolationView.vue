<template>
  <div class="interpolation-view">
    <div class="section-header">
      <h3>航迹插值数据</h3>
      <p class="section-desc">
        对航迹进行时间对齐和空间插值，使不同雷达站的航迹能够在同一时间点进行比较。插值后的数据用于多雷达协同定位。
      </p>
    </div>

    <!-- 插值说明 -->
    <div class="interpolation-explain">
      <div class="explain-item">
        <div class="explain-icon original">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle cx="12" cy="12" r="4"/>
          </svg>
        </div>
        <div class="explain-content">
          <h4>原始点</h4>
          <p>雷达实际观测到的航迹点</p>
        </div>
      </div>
      <div class="arrow">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6"/>
        </svg>
      </div>
      <div class="explain-item">
        <div class="explain-icon interpolated">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle cx="12" cy="12" r="3"/>
            <circle cx="6" cy="6" r="2"/>
            <circle cx="18" cy="18" r="2"/>
          </svg>
        </div>
        <div class="explain-content">
          <h4>插值点</h4>
          <p>基于线性插值生成的时间对齐点</p>
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div v-if="summary" class="stats-cards">
      <div class="stat-card">
        <div class="stat-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle cx="12" cy="12" r="10"/>
          </svg>
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ summary.total_points }}</span>
          <span class="stat-label">总点数</span>
        </div>
      </div>

      <div class="stat-card primary">
        <div class="stat-icon original">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle cx="12" cy="12" r="6"/>
          </svg>
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ summary.original_points }}</span>
          <span class="stat-label">原始点</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon interpolated">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle cx="12" cy="12" r="4"/>
            <circle cx="6" cy="8" r="2"/>
            <circle cx="18" cy="16" r="2"/>
          </svg>
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ summary.interpolated_points }}</span>
          <span class="stat-label">插值点</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon ratio">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
          </svg>
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ interpolationRatio }}%</span>
          <span class="stat-label">插值比例</span>
        </div>
      </div>
    </div>

    <!-- 各站点统计 -->
    <div class="station-stats">
      <h4>各雷达站插值点数</h4>
      <div class="station-bars">
        <div
          v-for="(count, station) in summary?.stations || {}"
          :key="station"
          class="station-bar-item"
        >
          <div class="station-info">
            <span class="station-name">{{ station }}</span>
            <span class="station-count">{{ count }} 点</span>
          </div>
          <div class="bar-container">
            <div
              class="bar-fill"
              :style="{ width: `${(count / maxStationCount) * 100}%` }"
            ></div>
          </div>
        </div>
      </div>
    </div>

    <!-- 算法说明 -->
    <div class="algorithm-info">
      <h4>插值算法说明</h4>
      <div class="algo-content">
        <p><strong>方法：</strong>线性插值（Linear Interpolation）</p>
        <p><strong>原理：</strong>根据相邻两个观测点的时间和位置，计算中间时刻的位置坐标。</p>
        <div class="formula">
          <code>
            P(t) = P₁ + (P₂ - P₁) × (t - t₁) / (t₂ - t₁)
          </code>
        </div>
        <p class="note">
          其中 P₁、P₂ 为相邻观测点，t₁、t₂ 为对应时间，t 为插值时间点，P(t) 为计算出的中间位置。
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { InterpolationSummary } from '@/types/errorAnalysis'

const props = defineProps<{
  summary: InterpolationSummary | null
}>()

const interpolationRatio = computed(() => {
  if (!props.summary || props.summary.original_points === 0) return 0
  const ratio = (props.summary.interpolated_points / props.summary.original_points) * 100
  return ratio.toFixed(1)
})

const maxStationCount = computed(() => {
  if (!props.summary?.stations) return 1
  return Math.max(...Object.values(props.summary.stations), 1)
})
</script>

<style scoped>
.interpolation-view {
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

.interpolation-explain {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 24px;
  padding: 24px;
  background: #f9fafb;
  border-radius: 8px;
  margin-bottom: 24px;
}

.explain-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.explain-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: white;
  border: 2px solid;
}

.explain-icon.original {
  border-color: #3b82f6;
}

.explain-icon.original svg {
  color: #3b82f6;
}

.explain-icon.interpolated {
  border-color: #8b5cf6;
}

.explain-icon.interpolated svg {
  color: #8b5cf6;
}

.explain-icon svg {
  width: 24px;
  height: 24px;
}

.explain-content h4 {
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 4px 0;
}

.explain-content p {
  font-size: 12px;
  color: #6b7280;
  margin: 0;
}

.arrow svg {
  width: 24px;
  height: 24px;
  color: #9ca3af;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.stat-card.primary {
  background: #eff6ff;
  border-color: #bfdbfe;
}

.stat-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background: white;
}

.stat-icon svg {
  width: 20px;
  height: 20px;
  color: #6b7280;
}

.stat-icon.original svg {
  color: #3b82f6;
}

.stat-icon.interpolated svg {
  color: #8b5cf6;
}

.stat-icon.ratio svg {
  color: #10b981;
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #1f2937;
}

.stat-label {
  font-size: 12px;
  color: #6b7280;
}

.station-stats {
  margin-bottom: 24px;
}

.station-stats h4 {
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 16px 0;
}

.station-bars {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.station-bar-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.station-info {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
}

.station-name {
  color: #374151;
}

.station-count {
  color: #6b7280;
  font-family: monospace;
}

.bar-container {
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #8b5cf6);
  border-radius: 4px;
  transition: width 0.3s ease;
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
  font-size: 13px;
  font-family: 'Monaco', 'Menlo', monospace;
  color: #7c3aed;
}

.note {
  font-size: 12px !important;
  color: #9ca3af !important;
}
</style>
