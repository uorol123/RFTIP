<template>
  <div class="task-management-page">
    <AppHeader />

    <div class="task-management-container">
      <div class="page-header">
        <div>
          <h1 class="page-title">任务管理</h1>
          <p class="page-subtitle">所有误差分析任务历史记录</p>
        </div>
        <div class="header-actions">
          <router-link to="/error-analysis/multi-source" class="btn btn-secondary">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"/>
            </svg>
            多源分析
          </router-link>
          <router-link to="/error-analysis/single-source" class="btn btn-secondary">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"/>
            </svg>
            单源分析
          </router-link>
        </div>
      </div>

      <!-- 筛选栏 -->
      <div class="filter-bar">
        <div class="filter-group">
          <label class="filter-label">算法类型</label>
          <select v-model="filterAlgorithmType" class="filter-select" @change="loadTasks">
            <option value="all">全部</option>
            <option value="multi_source">多源参考</option>
            <option value="single_source">单源盲测</option>
          </select>
        </div>
        <div class="filter-group">
          <label class="filter-label">任务状态</label>
          <select v-model="filterStatus" class="filter-select" @change="currentPage = 1; loadTasks()">
            <option value="">全部</option>
            <option value="pending">等待中</option>
            <option value="extracting">提取航迹</option>
            <option value="interpolating">航迹插值</option>
            <option value="matching">航迹匹配</option>
            <option value="calculating">计算误差</option>
            <option value="completed">已完成</option>
            <option value="failed">失败</option>
          </select>
        </div>
        <button class="btn btn-secondary btn-sm" @click="loadTasks">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="14" height="14">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
          </svg>
          刷新
        </button>
      </div>

      <!-- 加载状态 -->
      <div v-if="store.taskListLoading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>加载任务列表...</p>
      </div>

      <!-- 任务列表 -->
      <div v-else-if="filteredTasks.length > 0" class="task-list">
        <div
          v-for="task in filteredTasks"
          :key="task.id"
          class="task-card"
          @click="viewTaskDetail(task)"
        >
          <div class="task-left">
            <div class="task-status-icon" :class="`status-${task.status}`">
              <svg v-if="task.status === 'completed'" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
              </svg>
              <svg v-else-if="task.status === 'failed'" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <circle cx="12" cy="12" r="10" stroke-width="2"/>
                <path fill="none" stroke="currentColor" stroke-width="2" d="M12 2a10 10 0 0 1 10 10">
                  <animateTransform attributeName="transform" type="rotate" from="0 12 12" to="360 12 12" dur="1s" repeatCount="indefinite"/>
                </path>
              </svg>
            </div>
            <div class="task-info">
              <div class="task-title-row">
                <span class="task-id">任务 #{{ task.id }}</span>
                <span class="task-type-badge" :class="getAlgorithmType(task.algorithm_name)">
                  {{ isSingleSourceAlgorithm(task.algorithm_name) ? '单源盲测' : '多源参考' }}
                </span>
              </div>
              <div class="task-meta">
                <span class="task-algorithm">{{ task.algorithm_name || '--' }}</span>
                <span class="task-time">{{ formatTime(task.created_at) }}</span>
              </div>
              <div class="task-details">
                <span class="detail-chip">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="12" height="12">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
                  </svg>
                  {{ task.radar_station_ids?.length || 0 }} 站
                </span>
                <span class="detail-chip">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="12" height="12">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"/>
                  </svg>
                  {{ task.track_ids?.length || 0 }} 轨迹
                </span>
              </div>
            </div>
          </div>
          <div class="task-right">
            <span class="status-label" :class="`label-${task.status}`">
              {{ getStatusLabel(task.status) }}
            </span>
            <div v-if="isTaskProcessing(task.status)" class="task-progress">
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: `${task.progress || 0}%` }"></div>
              </div>
              <span class="progress-text">{{ task.progress || 0 }}%</span>
            </div>
            <button
              v-if="task.status === 'completed'"
              class="btn btn-primary btn-sm"
              @click.stop="viewTaskDetail(task)"
            >
              查看详情
            </button>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else class="empty-state">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
        </svg>
        <h3>暂无任务记录</h3>
        <p>开始一次分析来创建第一个任务</p>
        <div class="empty-actions">
          <router-link to="/error-analysis/multi-source" class="btn btn-primary">
            多源参考分析
          </router-link>
          <router-link to="/error-analysis/single-source" class="btn btn-secondary">
            单源盲测分析
          </router-link>
        </div>
      </div>

      <!-- 分页 -->
      <div v-if="totalPages > 1" class="pagination">
        <button
          class="btn btn-secondary btn-sm"
          :disabled="currentPage <= 1"
          @click="currentPage--; loadTasks()"
        >
          上一页
        </button>
        <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
        <button
          class="btn btn-secondary btn-sm"
          :disabled="currentPage >= totalPages"
          @click="currentPage++; loadTasks()"
        >
          下一页
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useErrorAnalysisStore } from '@/stores/errorAnalysis'
import { useAppStore } from '@/stores/app'
import type { ErrorAnalysisTask } from '@/types/errorAnalysis'
import { SINGLE_SOURCE_ALGORITHMS } from '@/types/errorAnalysis'
import AppHeader from '@/components/AppHeader.vue'

const router = useRouter()
const store = useErrorAnalysisStore()
const appStore = useAppStore()

const filterAlgorithmType = ref<'all' | 'multi_source' | 'single_source'>('all')
const filterStatus = ref('')
const currentPage = ref(1)
const pageSize = 20

function isSingleSourceAlgorithm(name?: string): boolean {
  return !!name && SINGLE_SOURCE_ALGORITHMS.includes(name)
}

function getAlgorithmType(name?: string): string {
  return isSingleSourceAlgorithm(name) ? 'single_source' : 'multi_source'
}

const filteredTasks = computed(() => {
  let tasks = store.taskList
  if (filterAlgorithmType.value !== 'all') {
    tasks = tasks.filter(t => {
      const isSingle = isSingleSourceAlgorithm(t.algorithm_name)
      return filterAlgorithmType.value === 'single_source' ? isSingle : !isSingle
    })
  }
  return tasks
})

const totalPages = computed(() => Math.ceil(store.taskListTotal / pageSize))

function isTaskProcessing(status: string): boolean {
  return ['pending', 'extracting', 'interpolating', 'matching', 'calculating'].includes(status)
}

function getStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    pending: '等待中',
    extracting: '提取航迹',
    interpolating: '航迹插值',
    matching: '航迹匹配',
    calculating: '计算误差',
    completed: '已完成',
    failed: '失败',
  }
  return labels[status] || status
}

function formatTime(dateString: string): string {
  if (!dateString) return '--'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function viewTaskDetail(task: ErrorAnalysisTask) {
  if (task.status !== 'completed') return
  const isSingle = isSingleSourceAlgorithm(task.algorithm_name)
  if (isSingle) {
    router.push(`/error-analysis/smoothed/${task.task_id}`)
  } else {
    router.push(`/error-analysis/history/${task.task_id}`)
  }
}

async function loadTasks() {
  try {
    await store.loadTaskList({
      skip: (currentPage.value - 1) * pageSize,
      limit: pageSize,
      status: filterStatus.value || undefined,
    })
  } catch (error: any) {
    appStore.error(error.message || '加载任务列表失败')
  }
}

onMounted(() => {
  loadTasks()
})
</script>

<style scoped>
.task-management-page {
  min-height: 100vh;
  background: var(--bg-primary);
}

.task-management-container {
  padding: 1.5rem;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.page-title {
  margin: 0 0 0.25rem;
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text-primary);
}

.page-subtitle {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.9375rem;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
}

/* 筛选栏 */
.filter-bar {
  display: flex;
  align-items: flex-end;
  gap: 1rem;
  padding: 1rem 1.25rem;
  background: var(--bg-secondary);
  border-radius: 0.75rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.filter-label {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.filter-select {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 0.375rem;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 0.875rem;
}

/* 任务列表 */
.task-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.task-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
  background: var(--bg-secondary);
  border-radius: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.task-card:hover {
  border-color: var(--color-primary);
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.1);
}

.task-card:hover:not(:has(.task-right .btn:hover)) {
  background: var(--bg-tertiary);
}

.task-left {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex: 1;
  min-width: 0;
}

.task-status-icon {
  width: 2.5rem;
  height: 2.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  flex-shrink: 0;
}

.task-status-icon svg {
  width: 1.25rem;
  height: 1.25rem;
}

.task-status-icon.status-completed { background: rgba(16, 185, 129, 0.1); color: #10b981; }
.task-status-icon.status-failed { background: rgba(239, 68, 68, 0.1); color: #ef4444; }
.task-status-icon.status-pending,
.task-status-icon.status-extracting,
.task-status-icon.status-interpolating,
.task-status-icon.status-matching,
.task-status-icon.status-calculating {
  background: rgba(59, 130, 246, 0.1); color: #3b82f6;
}

.task-info {
  flex: 1;
  min-width: 0;
}

.task-title-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.task-id {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 0.9375rem;
}

.task-type-badge {
  font-size: 0.6875rem;
  padding: 0.125rem 0.5rem;
  border-radius: 1rem;
  font-weight: 500;
}

.task-type-badge.multi_source {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.task-type-badge.single_source {
  background: rgba(139, 92, 246, 0.1);
  color: #8b5cf6;
}

.task-meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-top: 0.375rem;
}

.task-algorithm {
  font-size: 0.8125rem;
  padding: 0.125rem 0.5rem;
  background: var(--bg-tertiary);
  border-radius: 0.25rem;
  color: var(--text-secondary);
  font-family: monospace;
}

.task-time {
  font-size: 0.8125rem;
  color: var(--text-muted);
}

.task-details {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.375rem;
}

.detail-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.task-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.5rem;
  flex-shrink: 0;
}

.status-label {
  font-size: 0.8125rem;
  font-weight: 500;
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
}

.status-label.label-completed { background: rgba(16, 185, 129, 0.1); color: #10b981; }
.status-label.label-failed { background: rgba(239, 68, 68, 0.1); color: #ef4444; }
.status-label.label-pending,
.status-label.label-extracting,
.status-label.label-interpolating,
.status-label.label-matching,
.status-label.label-calculating {
  background: rgba(59, 130, 246, 0.1); color: #3b82f6;
}

.task-progress {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: 120px;
}

.progress-bar {
  flex: 1;
  height: 4px;
  background: var(--bg-tertiary);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--color-primary);
  border-radius: 2px;
  transition: width 0.3s;
}

.progress-text {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--color-primary);
  min-width: 2rem;
  text-align: right;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 4rem 2rem;
  background: var(--bg-secondary);
  border-radius: 0.75rem;
  text-align: center;
}

.empty-state svg {
  width: 3rem;
  height: 3rem;
  color: var(--text-muted);
}

.empty-state h3 {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
}

.empty-state p {
  margin: 0;
  color: var(--text-secondary);
}

.empty-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

/* 加载 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 4rem 2rem;
}

.loading-spinner {
  width: 2rem;
  height: 2rem;
  border: 3px solid var(--border-color);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-state p {
  color: var(--text-secondary);
  margin: 0;
}

/* 分页 */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border-color);
}

.page-info {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

/* 按钮 */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.25rem;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  text-decoration: none;
  transition: all 0.2s;
}

.btn svg { width: 1rem; height: 1rem; }

.btn:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-sm { padding: 0.375rem 0.75rem; font-size: 0.8125rem; }

.btn-primary { background: var(--color-primary); color: white; }
.btn-primary:hover { background: #2563eb; }

.btn-secondary { background: var(--bg-secondary); color: var(--text-primary); }
.btn-secondary:hover { background: var(--bg-tertiary); }

@media (max-width: 768px) {
  .task-card { flex-direction: column; align-items: flex-start; gap: 0.75rem; }
  .task-right { flex-direction: row; align-items: center; width: 100%; justify-content: space-between; }
  .filter-bar { flex-direction: column; align-items: stretch; }
}
</style>
