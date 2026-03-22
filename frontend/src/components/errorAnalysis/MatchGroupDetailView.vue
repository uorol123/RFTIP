<template>
  <div class="match-group-detail-view">
    <div class="section-header">
      <h3>航迹匹配组</h3>
      <p class="section-desc">
        在时间窗口内，将不同雷达站观测到的同一架飞机进行匹配，形成匹配组。匹配组用于计算雷达系统误差。
      </p>
    </div>

    <!-- 统计信息 -->
    <div class="stats-bar">
      <div class="stat-item">
        <span class="stat-label">匹配组总数</span>
        <span class="stat-value">{{ summary?.total_groups || 0 }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">总匹配点数</span>
        <span class="stat-value">{{ summary?.total_points || 0 }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">平均距离</span>
        <span class="stat-value">{{ avgDistance }} m</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">涉及雷达站</span>
        <span class="stat-value">{{ summary?.stations_involved || 0 }}</span>
      </div>
    </div>

    <!-- 匹配说明 -->
    <div class="match-explain">
      <div class="explain-step">
        <div class="step-num">1</div>
        <div class="step-content">
          <h4>时间窗口对齐</h4>
          <p>将不同雷达站在同一时间窗口内的观测点进行对齐</p>
        </div>
      </div>
      <div class="step-arrow">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6"/>
        </svg>
      </div>
      <div class="explain-step">
        <div class="step-num">2</div>
        <div class="step-content">
          <h4>空间距离计算</h4>
          <p>计算不同雷达站观测点之间的空间距离</p>
        </div>
      </div>
      <div class="step-arrow">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6"/>
        </svg>
      </div>
      <div class="explain-step">
        <div class="step-num">3</div>
        <div class="step-content">
          <h4>最优匹配</h4>
          <p>选择距离最小的点作为匹配对</p>
        </div>
      </div>
    </div>

    <!-- 匹配组列表 -->
    <div class="match-groups-list">
      <h4>匹配组详情</h4>

      <div class="groups-table-container">
        <table class="groups-table">
          <thead>
            <tr>
              <th>组号</th>
              <th>匹配时间</th>
              <th>点数</th>
              <th>涉及雷达站</th>
              <th>平均距离</th>
              <th>最大距离</th>
              <th>方差</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="group in displayGroups" :key="group.id">
              <td class="group-id">#{{ group.group_id }}</td>
              <td class="match-time">{{ formatTime(group.match_time) }}</td>
              <td class="point-count">{{ group.point_count }}</td>
              <td class="stations">
                <span
                  v-for="sid in group.station_ids"
                  :key="sid"
                  class="station-badge"
                >
                  站{{ sid }}
                </span>
              </td>
              <td class="avg-distance" :class="distanceClass(group.avg_distance)">
                {{ group.avg_distance?.toFixed(2) || '-' }} m
              </td>
              <td class="max-distance">
                {{ group.max_distance?.toFixed(2) || '-' }} m
              </td>
              <td class="variance">
                {{ group.variance?.toFixed(4) || '-' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 分页 -->
      <div v-if="totalPages > 1" class="pagination">
        <button
          class="page-btn"
          :disabled="currentPage === 1"
          @click="currentPage--"
        >
          上一页
        </button>
        <span class="page-info">
          第 {{ currentPage }} / {{ totalPages }} 页
        </span>
        <button
          class="page-btn"
          :disabled="currentPage === totalPages"
          @click="currentPage++"
        >
          下一页
        </button>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="groups.length === 0" class="empty-state">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"/>
      </svg>
      <p>暂无匹配组数据</p>
      <span>请确保选择了多个雷达站的共同轨迹</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { MatchGroupDetail } from '@/types/errorAnalysis'

const props = defineProps<{
  groups: MatchGroupDetail[]
  summary?: Record<string, unknown>
}>()

const currentPage = ref(1)
const pageSize = 20

const totalPages = computed(() => Math.ceil(props.groups.length / pageSize))

const displayGroups = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return props.groups.slice(start, start + pageSize)
})

const avgDistance = computed(() => {
  const val = props.summary?.avg_distance_mean as number
  return val ? val.toFixed(2) : '0.00'
})

function formatTime(timeString: string): string {
  if (!timeString) return '-'
  const date = new Date(timeString)
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

function distanceClass(distance: number | null): string {
  if (distance === null) return ''
  if (distance < 50) return 'excellent'
  if (distance < 100) return 'good'
  if (distance < 200) return 'fair'
  return 'poor'
}
</script>

<style scoped>
.match-group-detail-view {
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

.stats-bar {
  display: flex;
  gap: 32px;
  padding: 16px 20px;
  background: #f9fafb;
  border-radius: 8px;
  margin-bottom: 24px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-label {
  font-size: 12px;
  color: #6b7280;
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
}

.match-explain {
  display: flex;
  align-items: flex-start;
  justify-content: center;
  gap: 16px;
  padding: 20px;
  background: #f9fafb;
  border-radius: 8px;
  margin-bottom: 24px;
}

.explain-step {
  display: flex;
  gap: 12px;
  max-width: 200px;
}

.step-num {
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #3b82f6;
  color: white;
  font-size: 14px;
  font-weight: 600;
}

.step-content h4 {
  font-size: 13px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 4px 0;
}

.step-content p {
  font-size: 12px;
  color: #6b7280;
  margin: 0;
  line-height: 1.4;
}

.step-arrow svg {
  width: 20px;
  height: 20px;
  color: #9ca3af;
  margin-top: 4px;
}

.match-groups-list h4 {
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 16px 0;
}

.groups-table-container {
  overflow-x: auto;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.groups-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

th, td {
  padding: 12px 16px;
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

.group-id {
  font-weight: 600;
  color: #3b82f6;
}

.match-time {
  font-family: monospace;
  color: #374151;
}

.point-count {
  color: #374151;
}

.stations {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.station-badge {
  padding: 2px 8px;
  background: #e0e7ff;
  color: #4338ca;
  border-radius: 4px;
  font-size: 11px;
}

.avg-distance, .max-distance, .variance {
  font-family: monospace;
}

.avg-distance.excellent { color: #10b981; }
.avg-distance.good { color: #3b82f6; }
.avg-distance.fair { color: #f59e0b; }
.avg-distance.poor { color: #ef4444; }

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 20px;
}

.page-btn {
  padding: 8px 16px;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  color: #374151;
  transition: all 0.2s;
}

.page-btn:hover:not(:disabled) {
  background: #f3f4f6;
  border-color: #9ca3af;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 13px;
  color: #6b7280;
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
  font-weight: 500;
  color: #6b7280;
}

.empty-state span {
  margin-top: 8px;
  font-size: 13px;
}
</style>
