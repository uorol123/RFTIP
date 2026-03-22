<template>
  <div class="match-visualization">
    <div class="vis-header">
      <h3 class="vis-title">匹配组详情</h3>
      <div class="vis-actions">
        <div class="stats-summary">
          <div class="stat-item">
            <span class="stat-label">总匹配组</span>
            <span class="stat-value">{{ totalGroups }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">当前页</span>
            <span class="stat-value">{{ currentPage }} / {{ totalPages }}</span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="loading" class="vis-loading">
      <div class="spinner"></div>
      <span>加载中...</span>
    </div>

    <div v-else-if="matchGroups.length === 0" class="vis-empty">
      <EmptyState
        title="暂无匹配数据"
        description="完成分析后将显示匹配组信息"
      />
    </div>

    <div v-else class="vis-content">
      <!-- 匹配组卡片 -->
      <div class="match-groups">
        <div
          v-for="group in paginatedGroups"
          :key="group.id"
          class="match-group-card"
        >
          <div class="group-header">
            <div class="group-title">
              <span class="group-id">匹配组 #{{ group.group_id }}</span>
              <span class="group-time">{{ formatTime(group.match_time) }}</span>
            </div>
            <div class="group-stats">
              <span class="stat-badge">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/>
                </svg>
                {{ group.point_count }} 个点
              </span>
              <span v-if="group.avg_distance !== null" class="stat-badge" :class="getQualityClass(group.avg_distance)">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/>
                </svg>
                平均距离: {{ group.avg_distance.toFixed(4) }}°
              </span>
            </div>
          </div>

          <div class="group-content">
            <!-- 匹配点列表 -->
            <div class="matches-list">
              <div class="matches-header">
                <span>匹配点</span>
                <span class="matches-count">{{ group.match_points.length }}</span>
              </div>
              <div class="matches-items">
                <div
                  v-for="(point, index) in group.match_points"
                  :key="index"
                  class="match-item"
                >
                  <div class="match-info">
                    <span class="match-station">站点 {{ point.station_id }}</span>
                  </div>
                  <div class="match-details">
                    <span class="match-detail">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
                      </svg>
                      {{ point.latitude.toFixed(4) }}, {{ point.longitude.toFixed(4) }}
                    </span>
                    <span v-if="point.altitude !== null" class="match-detail">
                      高度: {{ point.altitude.toFixed(1) }}m
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 统计信息 -->
            <div v-if="group.variance !== null" class="group-stats-detail">
              <div class="stat-row">
                <span class="stat-label">方差:</span>
                <span class="stat-value">{{ group.variance.toFixed(6) }}</span>
              </div>
              <div v-if="group.max_distance !== null" class="stat-row">
                <span class="stat-label">最大距离:</span>
                <span class="stat-value">{{ group.max_distance.toFixed(4) }}°</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 分页 -->
      <div v-if="totalPages > 1" class="vis-pagination">
        <button
          class="pagination-btn"
          :disabled="currentPage === 1"
          @click="currentPage--"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
          </svg>
          上一页
        </button>
        <div class="pagination-pages">
          <button
            v-for="page in visiblePages"
            :key="page"
            class="page-btn"
            :class="{ active: page === currentPage }"
            @click="currentPage = page"
          >
            {{ page }}
          </button>
        </div>
        <button
          class="pagination-btn"
          :disabled="currentPage === totalPages"
          @click="currentPage++"
        >
          下一页
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import EmptyState from '@/components/EmptyState.vue'
import type { MatchGroup, TrackSegment } from '@/types/errorAnalysis'

interface Props {
  matchGroups: MatchGroup[]
  segments: TrackSegment[]
  loading: boolean
  totalGroups: number
  pageSize?: number
}

const props = withDefaults(defineProps<Props>(), {
  pageSize: 6,
})

const emit = defineEmits<{
  segmentChange: [segmentId: number | null]
}>()

const selectedSegmentId = ref<number | null>(null)
const currentPage = ref(1)

// 分页后的匹配组
const paginatedGroups = computed(() => {
  const start = (currentPage.value - 1) * props.pageSize
  const end = start + props.pageSize
  return props.matchGroups.slice(start, end)
})

const totalPages = computed(() => Math.ceil(props.matchGroups.length / props.pageSize))

// 可见的页码
const visiblePages = computed(() => {
  const pages: number[] = []
  const maxVisible = 5
  let start = Math.max(1, currentPage.value - Math.floor(maxVisible / 2))
  let end = Math.min(totalPages.value, start + maxVisible - 1)

  if (end - start < maxVisible - 1) {
    start = Math.max(1, end - maxVisible + 1)
  }

  for (let i = start; i <= end; i++) {
    pages.push(i)
  }

  return pages
})

// 处理段变化
function handleSegmentChange() {
  currentPage.value = 1
  emit('segmentChange', selectedSegmentId.value)
}

// 质量等级
function getQualityClass(avgDistance: number) {
  if (avgDistance < 0.05) return 'quality-excellent'
  if (avgDistance < 0.1) return 'quality-good'
  if (avgDistance < 0.2) return 'quality-fair'
  return 'quality-poor'
}

// 格式化时间
function formatTime(dateString: string) {
  const date = new Date(dateString)
  return date.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

// 重置页码
watch(() => props.matchGroups, () => {
  currentPage.value = 1
})
</script>

<style scoped>
.match-visualization {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 1.5rem;
  background: var(--bg-secondary);
  border-radius: 0.75rem;
}

.vis-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.vis-title {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
}

.vis-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.stats-summary {
  display: flex;
  gap: 1rem;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-label {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.stat-value {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.vis-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 3rem 1rem;
  color: var(--text-secondary);
}

.spinner {
  width: 2rem;
  height: 2rem;
  border: 2px solid var(--bg-tertiary);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.vis-empty {
  padding: 1rem 0;
}

.vis-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.match-groups {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.match-group-card {
  padding: 1rem;
  background: var(--bg-primary);
  border-radius: 0.5rem;
  border: 1px solid var(--border-color);
}

.group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--border-color);
}

.group-title {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.group-id {
  font-weight: 600;
  color: var(--text-primary);
}

.group-time {
  font-size: 0.8125rem;
  color: var(--text-muted);
}

.group-stats {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.stat-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.25rem 0.625rem;
  border-radius: 0.25rem;
  background: var(--bg-tertiary);
  font-size: 0.8125rem;
  color: var(--text-secondary);
}

.stat-badge svg {
  width: 0.875rem;
  height: 0.875rem;
}

.stat-badge.quality-excellent {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.stat-badge.quality-good {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.stat-badge.quality-fair {
  background: rgba(249, 115, 22, 0.1);
  color: #f97316;
}

.stat-badge.quality-poor {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.group-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.matches-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.matches-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.matches-items {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.match-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.625rem 0.75rem;
  background: var(--bg-tertiary);
  border-radius: 0.375rem;
  transition: all 0.2s;
}

.match-item:hover {
  background: var(--bg-primary);
}

.match-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-width: 100px;
}

.match-station {
  font-weight: 500;
  color: var(--text-primary);
}

.match-details {
  display: flex;
  gap: 1rem;
  flex: 1;
}

.match-detail {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.8125rem;
  color: var(--text-secondary);
}

.match-detail svg {
  width: 0.875rem;
  height: 0.875rem;
  color: var(--text-muted);
}

.group-stats-detail {
  display: flex;
  gap: 1.5rem;
  padding: 0.75rem;
  background: var(--bg-tertiary);
  border-radius: 0.375rem;
}

.stat-row {
  display: flex;
  gap: 0.5rem;
  font-size: 0.8125rem;
}

.stat-row .stat-label {
  color: var(--text-secondary);
}

.stat-row .stat-value {
  color: var(--text-primary);
  font-weight: 500;
}

.vis-pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 0;
}

.pagination-btn {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.375rem;
  background: var(--bg-tertiary);
  color: var(--text-primary);
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.pagination-btn:hover:not(:disabled) {
  background: var(--color-primary);
  color: white;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-btn svg {
  width: 1rem;
  height: 1rem;
}

.pagination-pages {
  display: flex;
  gap: 0.375rem;
}

.page-btn {
  min-width: 2rem;
  height: 2rem;
  padding: 0;
  border: none;
  border-radius: 0.375rem;
  background: var(--bg-tertiary);
  color: var(--text-primary);
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.page-btn:hover {
  background: var(--color-primary);
  color: white;
}

.page-btn.active {
  background: var(--color-primary);
  color: white;
}

@media (max-width: 640px) {
  .vis-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .match-details {
    flex-direction: column;
    gap: 0.25rem;
  }

  .vis-pagination {
    flex-wrap: wrap;
  }
}
</style>
