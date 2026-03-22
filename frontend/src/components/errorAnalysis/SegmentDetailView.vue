<template>
  <div class="segment-detail-view">
    <div class="section-header">
      <h3>航迹段详情</h3>
      <p class="section-desc">
        从原始雷达数据中提取的飞机航迹段。每段航迹代表一架飞机在连续时间内的观测轨迹。
      </p>
    </div>

    <!-- 统计信息 -->
    <div class="stats-bar">
      <div class="stat-item">
        <span class="stat-label">航迹段总数</span>
        <span class="stat-value">{{ segments.length }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">总点数</span>
        <span class="stat-value">{{ summary?.total_points || 0 }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">涉及雷达站</span>
        <span class="stat-value">{{ stationCount }}</span>
      </div>
    </div>

    <!-- 按雷达站分组 -->
    <div class="station-groups">
      <div
        v-for="(group, stationName) in groupedByStation"
        :key="stationName"
        class="station-group"
      >
        <div class="group-header">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2"/>
          </svg>
          <span class="station-name">{{ stationName }}</span>
          <span class="segment-count">{{ group.length }} 段</span>
        </div>

        <div class="segments-table">
          <table>
            <thead>
              <tr>
                <th>段号</th>
                <th>轨迹ID</th>
                <th>开始时间</th>
                <th>结束时间</th>
                <th>持续时间</th>
                <th>点数</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="seg in group" :key="seg.id">
                <td class="segment-id">#{{ seg.segment_id }}</td>
                <td class="track-id">{{ seg.track_id }}</td>
                <td class="time">{{ formatTime(seg.start_time) }}</td>
                <td class="time">{{ formatTime(seg.end_time) }}</td>
                <td class="duration">{{ seg.duration_seconds.toFixed(1) }}s</td>
                <td class="point-count">{{ seg.point_count }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="segments.length === 0" class="empty-state">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
      </svg>
      <p>暂无航迹段数据</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { TrackSegmentDetail } from '@/types/errorAnalysis'

const props = defineProps<{
  segments: TrackSegmentDetail[]
  summary?: Record<string, unknown>
}>()

const groupedByStation = computed(() => {
  const groups: Record<string, TrackSegmentDetail[]> = {}
  for (const seg of props.segments) {
    const name = seg.station_name || `站${seg.station_id}`
    if (!groups[name]) {
      groups[name] = []
    }
    groups[name].push(seg)
  }
  return groups
})

const stationCount = computed(() => {
  return Object.keys(props.segments.reduce((acc, seg) => {
    acc[seg.station_id] = true
    return acc
  }, {} as Record<number, boolean>)).length
})

function formatTime(timeString: string): string {
  if (!timeString) return '-'
  const date = new Date(timeString)
  return date.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}
</script>

<style scoped>
.segment-detail-view {
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

.station-groups {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.station-group {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
}

.group-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #f3f4f6;
  border-bottom: 1px solid #e5e7eb;
}

.group-header svg {
  width: 18px;
  height: 18px;
  color: #6b7280;
}

.station-name {
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
}

.segment-count {
  margin-left: auto;
  font-size: 12px;
  color: #6b7280;
}

.segments-table {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

th, td {
  padding: 10px 16px;
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

.segment-id {
  font-weight: 600;
  color: #3b82f6;
}

.track-id {
  font-family: monospace;
  color: #6b7280;
}

.time {
  font-family: monospace;
  color: #374151;
}

.duration {
  color: #10b981;
  font-weight: 500;
}

.point-count {
  color: #374151;
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
