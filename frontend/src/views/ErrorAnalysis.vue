<template>
  <div class="error-analysis-page">
    <AppHeader />

    <div class="error-analysis-container">
      <!-- 页面标题 -->
      <div class="page-header">
        <div>
          <h1 class="page-title">误差分析</h1>
          <p class="page-subtitle">{{ store.currentAlgorithmName }}</p>
        </div>
        <div class="header-actions">
          <button class="btn btn-secondary" @click="showHistory = true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            历史任务
          </button>
          <router-link to="/data" class="btn btn-secondary">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/>
            </svg>
            上传数据
          </router-link>
        </div>
      </div>

      <!-- 主内容区 -->
      <div class="main-content">
        <!-- 左侧配置面板 -->
        <div class="config-panel-wrapper">
          <ErrorConfigPanel
            @start="handleAnalysisStart"
          />
        </div>

        <!-- 右侧内容区 -->
        <div class="content-panel-wrapper">
          <!-- 进度条 -->
          <div v-if="store.currentTask" class="progress-section">
            <ErrorProgressBar
              :status="store.currentTask.status"
              :progress="store.taskProgress"
              :error="store.currentTask.error_message"
            />
          </div>

          <!-- 空状态 -->
          <div v-if="!store.currentTask" class="empty-section">
            <EmptyState
              title="开始误差分析"
              description="选择数据文件并配置分析参数，然后点击开始分析按钮"
            >
              <template #icon>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
                </svg>
              </template>
            </EmptyState>
          </div>

          <!-- 分析结果 -->
          <div v-else-if="store.isTaskCompleted" class="results-section">
            <!-- 标签页 -->
            <div class="tabs">
              <button
                v-for="tab in tabs"
                :key="tab.key"
                class="tab-btn"
                :class="{ active: activeTab === tab.key }"
                @click="activeTab = tab.key"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path v-if="tab.key === 'chart'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z"/>
                  <path v-else-if="tab.key === 'table'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"/>
                  <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/>
                </svg>
                {{ tab.label }}
              </button>
            </div>

            <!-- 图表 -->
            <div v-if="activeTab === 'chart'" class="tab-content">
              <ErrorResultChart
                :chart-data="store.chartData"
                :loading="store.chartDataLoading"
              />
            </div>

            <!-- 表格 -->
            <div v-else-if="activeTab === 'table'" class="tab-content">
              <ErrorTable
                v-if="store.analysisResult"
                :results="store.analysisResult.errors"
                :loading="store.resultLoading"
              />
            </div>

            <!-- 匹配可视化 -->
            <div v-else-if="activeTab === 'matches'" class="tab-content">
              <MatchVisualization
                :match-groups="store.matchGroups"
                :segments="store.segments"
                :loading="store.matchGroupsLoading"
                :total-groups="store.matchGroupsTotal"
                @segment-change="handleSegmentChange"
              />
            </div>
          </div>

          <!-- 失败状态 -->
          <div v-else-if="store.isTaskFailed" class="error-section">
            <div class="error-card">
              <svg class="error-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
              </svg>
              <h3>分析失败</h3>
              <p>{{ store.currentTask?.error_message || '未知错误' }}</p>
              <button class="btn btn-primary" @click="handleRetry">
                重新开始
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 历史任务 -->
      <div v-if="showHistory" class="history-section">
        <div class="history-header">
          <h2 class="history-title">历史任务</h2>
          <button class="btn btn-secondary btn-sm" @click="showHistory = false">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
        <div class="history-list">
          <div
            v-for="task in historyTasks"
            :key="task.id"
            class="history-item"
          >
            <div class="history-status" :class="`status-${task.status}`">
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
            <div class="history-info">
              <div class="history-id">任务 #{{ task.id }}</div>
              <div class="history-meta">
                <span class="history-algorithm">{{ task.algorithm_name || 'gradient_descent' }}</span>
                <span class="history-time">{{ formatTime(task.created_at) }}</span>
              </div>
              <div class="history-details">
                <div class="detail-item">
                  <span class="detail-label">雷达站:</span>
                  <span class="detail-value">{{ task.radar_station_ids?.join(', ') || '-' }}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">轨迹:</span>
                  <span class="detail-value">{{ task.track_ids?.slice(0, 3).join(', ') }}{{ task.track_ids?.length > 3 ? '...' : '' }}</span>
                </div>
              </div>
            </div>
            <div class="history-progress" v-if="task.status === 'pending' || task.status === 'extracting' || task.status === 'interpolating' || task.status === 'matching' || task.status === 'calculating'">
              {{ task.progress }}%
            </div>
            <div class="history-actions">
              <button
                v-if="task.status === 'completed'"
                class="btn btn-primary btn-sm"
                @click="viewTaskDetail(task.task_id)"
              >
                查看详情
              </button>
              <button
                v-else-if="task.status === 'pending' || task.status === 'extracting' || task.status === 'interpolating' || task.status === 'matching' || task.status === 'calculating'"
                class="btn btn-secondary btn-sm"
                @click="loadHistoryTask(task.task_id)"
              >
                查看进度
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useErrorAnalysisStore } from '@/stores/errorAnalysis'
import { useAppStore } from '@/stores/app'
import EmptyState from '@/components/EmptyState.vue'
import AppHeader from '@/components/AppHeader.vue'
import ErrorConfigPanel from '@/components/errorAnalysis/ErrorConfigPanel.vue'
import ErrorProgressBar from '@/components/errorAnalysis/ErrorProgressBar.vue'
import ErrorResultChart from '@/components/errorAnalysis/ErrorResultChart.vue'
import ErrorTable from '@/components/errorAnalysis/ErrorTable.vue'
import MatchVisualization from '@/components/errorAnalysis/MatchVisualization.vue'

const router = useRouter()
const store = useErrorAnalysisStore()
const appStore = useAppStore()

const showHistory = ref(false)
const historyTasks = ref<any[]>([])
const activeTab = ref<'chart' | 'table' | 'matches'>('chart')

const tabs = [
  { key: 'chart' as const, label: '图表' },
  { key: 'table' as const, label: '详细数据' },
  { key: 'matches' as const, label: '匹配组' },
]

// 分析开始
function handleAnalysisStart() {
  activeTab.value = 'chart'
}

// 重新开始
function handleRetry() {
  store.clearCurrentTask()
}

// 段变化处理
async function handleSegmentChange(segmentId: number | null) {
  if (store.currentTask) {
    await store.loadMatchGroups(store.currentTask.task_id, {
      segment_id: segmentId ?? undefined,
      skip: 0,
      limit: 100,
    })
  }
}

// 加载历史任务
async function loadHistoryTasks() {
  try {
    const response = await store.loadTaskList({ limit: 10 })
    historyTasks.value = store.taskList
  } catch (error: any) {
    appStore.error(error.message || '加载历史任务失败')
  }
}

// 加载历史任务详情
async function loadHistoryTask(taskId: string) {
  try {
    await store.loadTaskDetail(taskId)
    if (store.currentTask?.status === 'completed') {
      await Promise.all([
        store.loadAnalysisResult(taskId),
        store.loadSegments(taskId),
        store.loadChartData(taskId),
        store.loadMatchGroups(taskId, { skip: 0, limit: 100 }),
      ])
    }
    showHistory.value = false
  } catch (error: any) {
    appStore.error(error.message || '加载任务失败')
  }
}

// 查看任务详情（跳转到详情页）
function viewTaskDetail(taskId: string) {
  router.push(`/error-analysis/history/${taskId}`)
}

// 格式化时间
function formatTime(dateString: string) {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

onMounted(() => {
  loadHistoryTasks()
})

onUnmounted(() => {
  store.stopPolling()
})
</script>

<style scoped>
.error-analysis-page {
  min-height: 100vh;
  background: var(--bg-primary);
}

.error-analysis-container {
  padding: 1.5rem;
  max-width: 1600px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
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

.main-content {
  display: grid;
  grid-template-columns: 350px 1fr;
  gap: 1.5rem;
  align-items: start;
}

.config-panel-wrapper {
  position: sticky;
  top: 1.5rem;
}

.content-panel-wrapper {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.progress-section {
  margin-bottom: -0.5rem;
}

.empty-section,
.results-section,
.error-section {
  padding: 1rem 0;
}

.tabs {
  display: flex;
  gap: 0.5rem;
  padding: 0.5rem;
  background: var(--bg-secondary);
  border-radius: 0.5rem;
  margin-bottom: 1rem;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.375rem;
  background: transparent;
  color: var(--text-secondary);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-btn:hover {
  color: var(--text-primary);
  background: var(--bg-tertiary);
}

.tab-btn.active {
  background: var(--color-primary);
  color: white;
}

.tab-btn svg {
  width: 1rem;
  height: 1rem;
}

.tab-content {
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.error-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 3rem 2rem;
  background: var(--bg-secondary);
  border-radius: 0.75rem;
  text-align: center;
}

.error-icon {
  width: 4rem;
  height: 4rem;
  color: #ef4444;
}

.error-card h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
}

.error-card p {
  margin: 0;
  color: var(--text-secondary);
}

.history-section {
  margin-top: 2rem;
  padding: 1.5rem;
  background: var(--bg-secondary);
  border-radius: 0.75rem;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.history-title {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background: var(--bg-tertiary);
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.history-item:hover {
  background: var(--bg-primary);
}

.history-status {
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.history-status.status-completed {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.history-status.status-failed {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.history-status.status-processing,
.history-status.status-pending {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.history-status svg {
  width: 1rem;
  height: 1rem;
}

.history-info {
  flex: 1;
}

.history-id {
  font-weight: 500;
  color: var(--text-primary);
}

.history-time {
  font-size: 0.8125rem;
  color: var(--text-muted);
}

.history-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.25rem;
}

.history-algorithm {
  font-size: 0.75rem;
  padding: 0.125rem 0.5rem;
  background: var(--bg-tertiary);
  border-radius: 0.25rem;
  color: var(--text-secondary);
}

.history-details {
  margin-top: 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8125rem;
}

.detail-label {
  color: var(--text-muted);
  min-width: 3rem;
}

.detail-value {
  color: var(--text-secondary);
  font-family: monospace;
  font-size: 0.75rem;
}

.history-progress {
  font-weight: 600;
  color: var(--color-primary);
}

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

.btn svg {
  width: 1rem;
  height: 1rem;
}

.btn-primary {
  background: var(--color-primary);
  color: white;
}

.btn-primary:hover {
  background: #2563eb;
}

.btn-secondary {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.btn-secondary:hover {
  background: var(--bg-tertiary);
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.8125rem;
}

@media (max-width: 1024px) {
  .main-content {
    grid-template-columns: 1fr;
  }

  .config-panel-wrapper {
    position: static;
  }
}

@media (max-width: 640px) {
  .error-analysis-container {
    padding: 1rem;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .tabs {
    overflow-x: auto;
  }
}
</style>
