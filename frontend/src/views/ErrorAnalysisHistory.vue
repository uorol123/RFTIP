/**
 * 误差分析 - 历史任务详情页面
 * 算法：基于梯度下降的迭代寻优算法
 *
 * 展示完整分析流程、各中间步骤数据和详细说明
 */
<template>
  <div class="error-analysis-history">
    <AppHeader />

    <!-- 页面导航 -->
    <div class="page-nav">
      <button class="back-btn" @click="goBack">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
        </svg>
        返回列表
      </button>
      <h1 class="page-title">任务详情</h1>
    </div>

    <!-- 加载状态 -->
    <div v-if="store.taskDetailLoading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>正在加载任务详情...</p>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error-container">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
      </svg>
      <p>{{ error }}</p>
      <button class="btn btn-primary" @click="loadData">重试</button>
    </div>

    <!-- 任务详情内容 -->
    <div v-else-if="store.taskDetail" class="content">

      <!-- 任务概览卡片 -->
      <section class="overview-card">
        <div class="overview-header">
          <div class="header-left">
            <h2>任务概览</h2>
            <span class="status-badge" :class="`status-${store.taskDetail.status}`">
              {{ statusInfo.label }}
            </span>
          </div>
          <div class="header-right">
            <span class="task-id">ID: {{ store.taskDetail.task_id }}</span>
          </div>
        </div>

        <div class="info-grid">
          <div class="info-item">
            <span class="label">创建时间</span>
            <span class="value">{{ formatTime(store.taskDetail.created_at) }}</span>
          </div>
          <div class="info-item">
            <span class="label">处理时间</span>
            <span class="value">{{ store.taskDetail.processing_time_seconds.toFixed(2) }} 秒</span>
          </div>
          <div class="info-item">
            <span class="label">雷达站数</span>
            <span class="value">{{ store.taskDetail.radar_station_ids.length }}</span>
          </div>
          <div class="info-item">
            <span class="label">轨迹数</span>
            <span class="value">{{ store.taskDetail.track_ids.length }}</span>
          </div>
          <div class="info-item">
            <span class="label">航迹段数</span>
            <span class="value">{{ store.taskDetail.total_segments }}</span>
          </div>
          <div class="info-item">
            <span class="label">匹配组数</span>
            <span class="value">{{ store.taskDetail.total_match_groups }}</span>
          </div>
        </div>
      </section>

      <!-- 算法流程说明 -->
      <section class="process-section">
        <h2>{{ algorithmDisplayName }}</h2>
        <p class="section-desc" v-if="!isSingleSourceMode">
          该算法通过对比不同雷达站观测同一目标时的位置差异，利用梯度下降法迭代优化，计算各雷达站的系统误差（方位角、距离、俯仰角）。
        </p>
        <p class="section-desc" v-else>
          该算法基于匀速运动模型对单站雷达轨迹进行平滑去噪，通过卡尔曼滤波输出修正后的轨迹和状态估计协方差，评估轨迹质量。
        </p>

        <!-- 水平时间线步骤导航 -->
        <div class="process-timeline">
          <div
            v-for="(step, index) in store.taskDetail.process_steps"
            :key="step.step_id"
            class="timeline-step"
            :class="['step-' + step.status, { active: activeStep === index }]"
            @click="activeStep = activeStep === index ? -1 : index"
          >
            <div class="step-number">{{ index + 1 }}</div>
            <div class="step-info">
              <span class="step-name">{{ step.step_name }}</span>
              <span class="step-status-badge" :class="step.status">{{ stepStatusLabel(step.status) }}</span>
            </div>
            <div class="step-connector" v-if="index < store.taskDetail.process_steps.length - 1"></div>
          </div>
        </div>

        <!-- 选中步骤的详情 -->
        <div v-if="activeStep >= 0 && store.taskDetail.process_steps[activeStep]" class="step-detail-card">
          <div class="detail-header">
            <h3>{{ store.taskDetail.process_steps[activeStep].step_name }}</h3>
            <span class="detail-status" :class="store.taskDetail.process_steps[activeStep].status">
              {{ stepStatusLabel(store.taskDetail.process_steps[activeStep].status) }}
            </span>
          </div>
          <p class="detail-description">{{ store.taskDetail.process_steps[activeStep].step_description }}</p>

          <!-- 步骤数据预览 -->
          <div class="detail-preview">
            <div
              v-for="(val, key) in getStepData(activeStep)"
              :key="key"
              class="preview-item"
            >
              <span class="preview-label">{{ key }}</span>
              <span class="preview-value">{{ val }}</span>
            </div>
          </div>
        </div>

        <!-- 步骤说明卡片（可点击展开） -->
        <div class="step-explain-cards">
          <div
            v-for="(step, index) in store.taskDetail.process_steps"
            :key="'explain-' + step.step_id"
            class="explain-card"
            :class="{ expanded: expandedStep === index }"
            @click="expandedStep = expandedStep === index ? -1 : index"
          >
            <div class="explain-header">
              <span class="explain-number">{{ index + 1 }}</span>
              <span class="explain-title">{{ step.step_name }}</span>
              <svg class="expand-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
              </svg>
            </div>
            <div class="explain-content" v-if="expandedStep === index">
              <p>{{ step.step_description }}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- 数据汇总 -->
      <section class="summary-section">
        <h2>数据汇总</h2>

        <div class="summary-cards">
          <!-- 航迹段汇总 -->
          <div class="summary-card">
            <div class="card-icon extracting">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
              </svg>
            </div>
            <div class="card-content">
              <h4>航迹提取</h4>
              <p class="card-desc">从原始雷达数据中提取的航迹段</p>
              <div class="card-stats">
                <span class="stat">
                  <strong>{{ store.taskDetail.segments_summary?.total_segments || 0 }}</strong> 段
                </span>
                <span class="stat">
                  <strong>{{ store.taskDetail.segments_summary?.total_points || 0 }}</strong> 点
                </span>
              </div>
            </div>
          </div>

          <!-- 插值汇总 -->
          <div class="summary-card">
            <div class="card-icon interpolating">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"/>
              </svg>
            </div>
            <div class="card-content">
              <h4>航迹插值</h4>
              <p class="card-desc">时间对齐和空间插值后的数据</p>
              <div class="card-stats" v-if="store.taskDetail.interpolation_summary">
                <span class="stat">
                  <strong>{{ store.taskDetail.interpolation_summary.original_points }}</strong> 原始点
                </span>
                <span class="stat">
                  <strong>{{ store.taskDetail.interpolation_summary.interpolated_points }}</strong> 插值点
                </span>
              </div>
            </div>
          </div>

          <!-- 匹配汇总 -->
          <div class="summary-card">
            <div class="card-icon matching">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"/>
              </svg>
            </div>
            <div class="card-content">
              <h4>航迹匹配</h4>
              <p class="card-desc">多雷达协同定位的匹配组</p>
              <div class="card-stats">
                <span class="stat">
                  <strong>{{ store.taskDetail.match_summary?.total_groups || 0 }}</strong> 组
                </span>
                <span class="stat">
                  <strong>{{ store.taskDetail.match_summary?.total_points || 0 }}</strong> 点
                </span>
              </div>
            </div>
          </div>

          <!-- 误差结果 -->
          <div class="summary-card">
            <div class="card-icon calculating">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
              </svg>
            </div>
            <div class="card-content">
              <h4>误差计算</h4>
              <p class="card-desc">各雷达站的系统误差结果</p>
              <div class="card-stats">
                <span class="stat">
                  <strong>{{ store.taskDetail.error_results?.length || 0 }}</strong> 雷达站
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 标签页 -->
      <section class="tabs-section">
        <div class="tabs-header">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            :class="['tab', { active: activeTab === tab.key }]"
            @click="activeTab = tab.key"
          >
            {{ tab.label }}
          </button>
        </div>

        <!-- 单源盲测模式: 平滑轨迹对比 -->
        <div v-if="isSingleSourceMode && activeTab === 'smoothed'" class="tab-content">
          <SmoothedTrajectoryView
            :trajectories="store.taskDetail.smoothed_trajectories"
          />
        </div>

        <!-- 单源盲测模式: 统计信息 -->
        <div v-if="isSingleSourceMode && activeTab === 'statistics'" class="tab-content">
          <div class="statistics-panel">
            <h4>处理统计</h4>
            <div class="stats-grid">
              <div class="stat-item">
                <span class="stat-label">处理时间</span>
                <span class="stat-value">{{ store.taskDetail.processing_time_seconds.toFixed(2) }} 秒</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">轨迹数量</span>
                <span class="stat-value">{{ store.taskDetail.track_ids.length }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">平滑轨迹组</span>
                <span class="stat-value">{{ store.taskDetail.smoothed_trajectories.length }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">总轨迹点数</span>
                <span class="stat-value">{{ store.taskDetail.smoothed_trajectories.reduce((sum, t) => sum + t.point_count, 0) }}</span>
              </div>
            </div>

            <!-- 误差统计 -->
            <h4>误差统计 (RMSE)</h4>
            <div class="stats-grid" v-if="store.taskDetail.smoothed_trajectories.length > 0">
              <div class="stat-item">
                <span class="stat-label">平均纬度偏差</span>
                <span class="stat-value">
                  {{ (store.taskDetail.smoothed_trajectories.reduce((sum, t) => sum + (t.rmse_lat || 0), 0) / store.taskDetail.smoothed_trajectories.length * 111000).toFixed(2) }} m
                </span>
              </div>
              <div class="stat-item">
                <span class="stat-label">平均距离偏差</span>
                <span class="stat-value">
                  {{ (store.taskDetail.smoothed_trajectories.reduce((sum, t) => sum + (t.rmse_lon || 0), 0) / store.taskDetail.smoothed_trajectories.length * 111000).toFixed(2) }} m
                </span>
              </div>
              <div class="stat-item">
                <span class="stat-label">平均高度偏差</span>
                <span class="stat-value">
                  {{ (store.taskDetail.smoothed_trajectories.reduce((sum, t) => sum + (t.rmse_alt || 0), 0) / store.taskDetail.smoothed_trajectories.length).toFixed(2) }} m
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- 多源参考模式 -->
        <template v-if="!isSingleSourceMode">
          <!-- 航迹段详情 -->
          <div v-if="activeTab === 'segments'" class="tab-content">
            <SegmentDetailView
              :segments="store.taskDetail.segments"
              :summary="store.taskDetail.segments_summary"
            />
          </div>

          <!-- 插值数据 -->
          <div v-if="activeTab === 'interpolation'" class="tab-content">
            <InterpolationView
              :summary="store.taskDetail.interpolation_summary"
            />
          </div>

          <!-- 匹配组 -->
          <div v-if="activeTab === 'matches'" class="tab-content">
            <MatchGroupDetailView
              :groups="store.taskDetail.match_groups"
              :summary="store.taskDetail.match_summary"
            />
          </div>

          <!-- 误差结果 -->
          <div v-if="activeTab === 'errors'" class="tab-content">
            <ErrorResultDetailView
              :results="store.taskDetail.error_results"
            />
          </div>
        </template>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useErrorAnalysisStore } from '@/stores/errorAnalysis'
import { useAppStore } from '@/stores/app'
import { TASK_STATUS_INFO } from '@/types/errorAnalysis'
import SegmentDetailView from '@/components/errorAnalysis/SegmentDetailView.vue'
import InterpolationView from '@/components/errorAnalysis/InterpolationView.vue'
import MatchGroupDetailView from '@/components/errorAnalysis/MatchGroupDetailView.vue'
import ErrorResultDetailView from '@/components/errorAnalysis/ErrorResultDetailView.vue'
import SmoothedTrajectoryView from '@/components/errorAnalysis/SmoothedTrajectoryView.vue'

const route = useRoute()
const router = useRouter()
const store = useErrorAnalysisStore()
const appStore = useAppStore()

const activeTab = ref('segments')
const activeStep = ref(-1)
const expandedStep = ref(-1)
const error = ref<string | null>(null)

// 单源盲测算法列表
const SINGLE_SOURCE_ALGORITHMS = ['kalman', 'particle_filter', 'spline']

// 判断是否为单源盲测模式
const isSingleSourceMode = computed(() => {
  const algorithmName = store.taskDetail?.algorithm_name || ''
  return SINGLE_SOURCE_ALGORITHMS.includes(algorithmName)
})

// 多源模式标签页
const multiSourceTabs = [
  { key: 'segments', label: '航迹段详情' },
  { key: 'interpolation', label: '插值数据' },
  { key: 'matches', label: '匹配组' },
  { key: 'errors', label: '误差结果' },
]

// 单源模式标签页
const singleSourceTabs = [
  { key: 'smoothed', label: '平滑轨迹对比' },
  { key: 'statistics', label: '统计信息' },
]

// 根据模式获取标签页
const tabs = computed(() => {
  return isSingleSourceMode.value ? singleSourceTabs.value : multiSourceTabs
})

const statusInfo = computed(() => {
  const status = store.taskDetail?.status || 'pending'
  return TASK_STATUS_INFO[status] || { label: status, color: '#9ca3af' }
})

// 获取算法显示名称
const algorithmDisplayName = computed(() => {
  const name = store.taskDetail?.algorithm_name || 'gradient_descent'
  const names: Record<string, string> = {
    gradient_descent: '基于梯度下降的迭代寻优算法',
    ransac: 'RANSAC 随机抽样一致性算法',
    weighted_lstsq: '加权最小二乘算法',
    kalman: '卡尔曼滤波算法',
    particle_filter: '粒子滤波算法',
    spline: '样条插值算法',
  }
  return names[name] || name
})

function formatTime(timeString: string): string {
  if (!timeString) return '-'
  const date = new Date(timeString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

function stepStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    completed: '已完成',
    running: '进行中',
    pending: '等待中',
    failed: '失败',
    skipped: '跳过'
  }
  return labels[status] || status
}

function getStepData(stepIndex: number): Record<string, unknown> {
  if (!store.taskDetail) return {}
  const step = store.taskDetail.process_steps[stepIndex]
  if (!step) return {}

  // 根据步骤返回相关数据
  const summaries = [
    store.taskDetail.segments_summary,
    store.taskDetail.interpolation_summary,
    store.taskDetail.match_summary,
    { stations: store.taskDetail.error_results?.length || 0 }
  ]

  return summaries[stepIndex] || step.data_summary || {}
}

function goBack() {
  router.push('/error-analysis/tasks')
}

async function loadData() {
  error.value = null
  const taskId = route.params.taskId as string

  if (!taskId) {
    error.value = '任务ID不存在'
    return
  }

  try {
    await store.loadTaskDetailFull(taskId, true, false)
  } catch (e: any) {
    error.value = e.message || '加载任务详情失败'
    appStore.error(error.value || '加载任务详情失败')
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.error-analysis-history {
  min-height: 100vh;
  background: #f5f7fa;
}

.page-nav {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 24px;
  background: white;
  border-bottom: 1px solid #e5e7eb;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  color: #374151;
  transition: all 0.2s;
}

.back-btn:hover {
  background: #f3f4f6;
  border-color: #9ca3af;
}

.back-btn svg {
  width: 16px;
  height: 16px;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.loading-container,
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 24px;
  gap: 16px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e5e7eb;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-container svg {
  width: 48px;
  height: 48px;
  color: #ef4444;
}

.error-container p {
  color: #6b7280;
  margin: 0;
}

.content {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

/* 概览卡片 */
.overview-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.overview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.overview-header h2 {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  color: white;
  background: v-bind('statusInfo.color');
}

.task-id {
  font-size: 12px;
  color: #6b7280;
  font-family: monospace;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-item .label {
  font-size: 12px;
  color: #6b7280;
}

.info-item .value {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

/* 流程说明 */
.process-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.process-section h2 {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.section-desc {
  font-size: 14px;
  color: #6b7280;
  margin: 0 0 24px 0;
  line-height: 1.6;
}

/* 水平时间线 */
.process-timeline {
  display: flex;
  align-items: center;
  gap: 0;
  margin-bottom: 24px;
  padding: 16px 0;
  overflow-x: auto;
}

.timeline-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  cursor: pointer;
  position: relative;
  transition: all 0.2s;
  min-width: 120px;
}

.timeline-step:hover {
  background: #f3f4f6;
  border-radius: 8px;
}

.timeline-step.active {
  background: #eff6ff;
  border-radius: 8px;
}

.step-number {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #e5e7eb;
  color: #6b7280;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.2s;
}

.timeline-step.step-completed .step-number {
  background: #10b981;
  color: white;
}

.timeline-step.step-running .step-number {
  background: #3b82f6;
  color: white;
  animation: pulse 2s infinite;
}

.timeline-step.step-failed .step-number {
  background: #ef4444;
  color: white;
}

.step-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.step-name {
  font-size: 13px;
  font-weight: 600;
  color: #1f2937;
}

.step-status-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 10px;
  background: #e5e7eb;
  color: #6b7280;
}

.step-status-badge.completed { background: #d1fae5; color: #059669; }
.step-status-badge.running { background: #dbeafe; color: #2563eb; }
.step-status-badge.failed { background: #fee2e2; color: #dc2626; }

.step-connector {
  position: absolute;
  right: -20px;
  width: 40px;
  height: 2px;
  background: #e5e7eb;
  z-index: 0;
}

.timeline-step.step-completed .step-connector {
  background: #10b981;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

/* 步骤详情卡片 */
.step-detail-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 20px 24px;
  margin-bottom: 24px;
  color: white;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.detail-header h3 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.detail-status {
  padding: 4px 12px;
  border-radius: 20px;
  background: rgba(255,255,255,0.2);
  font-size: 12px;
}

.detail-description {
  font-size: 14px;
  line-height: 1.6;
  margin: 0 0 16px 0;
  opacity: 0.95;
}

.detail-preview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 12px;
}

.preview-item {
  background: rgba(255,255,255,0.15);
  border-radius: 8px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.preview-label {
  font-size: 11px;
  opacity: 0.8;
}

.preview-value {
  font-size: 18px;
  font-weight: 700;
}

/* 步骤说明卡片（可折叠） */
.step-explain-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.explain-card {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.2s;
}

.explain-card:hover {
  border-color: #3b82f6;
}

.explain-card.expanded {
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

.explain-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  cursor: pointer;
}

.explain-number {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #3b82f6;
  color: white;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}

.explain-title {
  font-size: 14px;
  font-weight: 500;
  color: #1f2937;
  flex: 1;
}

.expand-icon {
  width: 16px;
  height: 16px;
  color: #9ca3af;
  transition: transform 0.2s;
}

.explain-card.expanded .expand-icon {
  transform: rotate(180deg);
}

.explain-content {
  padding: 0 16px 16px 52px;
}

.explain-content p {
  font-size: 13px;
  color: #6b7280;
  margin: 0;
  line-height: 1.6;
}

/* 响应式 */
@media (max-width: 768px) {
  .process-timeline {
    flex-direction: column;
    align-items: flex-start;
  }

  .step-connector {
    display: none;
  }

  .timeline-step {
    flex-direction: row;
    width: 100%;
    min-width: auto;
  }

  .step-explain-cards {
    grid-template-columns: 1fr;
  }
}

/* 汇总卡片 */
.summary-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.summary-section h2 {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 20px 0;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
}

.summary-card {
  display: flex;
  gap: 16px;
  padding: 20px;
  border-radius: 8px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
}

.card-icon {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
}

.card-icon svg {
  width: 24px;
  height: 24px;
  color: white;
}

.card-icon.extracting {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
}

.card-icon.interpolating {
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
}

.card-icon.matching {
  background: linear-gradient(135deg, #f59e0b, #d97706);
}

.card-icon.calculating {
  background: linear-gradient(135deg, #10b981, #059669);
}

.card-content h4 {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 4px 0;
}

.card-desc {
  font-size: 13px;
  color: #6b7280;
  margin: 0 0 12px 0;
}

.card-stats {
  display: flex;
  gap: 16px;
}

.stat {
  font-size: 13px;
  color: #6b7280;
}

.stat strong {
  color: #1f2937;
  font-weight: 600;
}

/* 标签页 */
.tabs-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.tabs-header {
  display: flex;
  gap: 8px;
  border-bottom: 1px solid #e5e7eb;
  margin-bottom: 24px;
}

.tab {
  padding: 12px 20px;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: #6b7280;
  transition: all 0.2s;
}

.tab:hover {
  color: #374151;
}

.tab.active {
  color: #3b82f6;
  border-bottom-color: #3b82f6;
}

.tab-content {
  min-height: 300px;
}

/* 统计面板 */
.statistics-panel {
  padding: 1.5rem;
  background: var(--bg-primary);
  border-radius: 0.5rem;
  border: 1px solid var(--border-color);
}

.statistics-panel h4 {
  margin: 0 0 1rem 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.statistics-panel h4:not(:first-child) {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border-color);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: 0.75rem;
  background: var(--bg-tertiary);
  border-radius: 0.375rem;
}

.stat-item .stat-label {
  font-size: 0.8125rem;
  color: var(--text-secondary);
}

.stat-item .stat-value {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
}
</style>
