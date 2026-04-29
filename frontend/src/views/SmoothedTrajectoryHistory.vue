<template>
  <div class="smoothed-trajectory-history">
    <AppHeader />

    <!-- 页面导航 -->
    <div class="page-nav">
      <button class="back-btn" @click="goBack">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
        </svg>
        返回列表
      </button>
      <h1 class="page-title">单源盲测详情</h1>
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

      <!-- 算法信息卡片 -->
      <section class="algorithm-card">
        <div class="algorithm-header">
          <div class="algorithm-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
            </svg>
          </div>
          <div class="algorithm-info">
            <h2>{{ algorithmDisplayName }}</h2>
            <p>基于匀速运动模型的卡尔曼滤波，对单站雷达轨迹进行平滑去噪</p>
          </div>
          <span class="status-badge" :class="`status-${store.taskDetail.status}`">
            {{ statusInfo.label }}
          </span>
        </div>
      </section>

      <!-- 概览卡片 -->
      <section class="overview-section">
        <div class="overview-grid">
          <div class="overview-card">
            <div class="card-icon processing">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            <div class="card-content">
              <span class="card-value">{{ store.taskDetail.processing_time_seconds.toFixed(2) }}s</span>
              <span class="card-label">处理时间</span>
            </div>
          </div>

          <div class="overview-card">
            <div class="card-icon stations">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
              </svg>
            </div>
            <div class="card-content">
              <span class="card-value">{{ store.taskDetail.radar_station_ids.length }}</span>
              <span class="card-label">雷达站</span>
            </div>
          </div>

          <div class="overview-card">
            <div class="card-icon tracks">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"/>
              </svg>
            </div>
            <div class="card-content">
              <span class="card-value">{{ store.taskDetail.track_ids.length }}</span>
              <span class="card-label">轨迹</span>
            </div>
          </div>

          <div class="overview-card">
            <div class="card-icon points">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
              </svg>
            </div>
            <div class="card-content">
              <span class="card-value">{{ totalPoints }}</span>
              <span class="card-label">轨迹点数</span>
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

        <!-- 轨迹对比 -->
        <div v-if="activeTab === 'trajectory'" class="tab-content">
          <SmoothedTrajectoryView
            v-if="store.taskDetail.smoothed_trajectories.length > 0"
            :trajectories="store.taskDetail.smoothed_trajectories"
          />
          <div v-else class="empty-state">
            <p>暂无平滑轨迹数据</p>
          </div>
        </div>

        <!-- 统计信息 -->
        <div v-if="activeTab === 'statistics'" class="tab-content">
          <div class="statistics-panel">
            <h4>误差统计 (RMSE)</h4>
            <div class="stats-grid" v-if="store.taskDetail.smoothed_trajectories.length > 0">
              <div class="stat-card">
                <span class="stat-label">平均纬度偏差</span>
                <span class="stat-value">{{ avgRmseLat.toFixed(2) }} m</span>
              </div>
              <div class="stat-card">
                <span class="stat-label">平均距离偏差</span>
                <span class="stat-value">{{ avgRmseLon.toFixed(2) }} m</span>
              </div>
              <div class="stat-card">
                <span class="stat-label">平均高度偏差</span>
                <span class="stat-value">{{ avgRmseAlt.toFixed(2) }} m</span>
              </div>
            </div>

            <h4>各轨迹详情</h4>
            <div class="trajectory-list">
              <div
                v-for="traj in store.taskDetail.smoothed_trajectories"
                :key="traj.id"
                class="trajectory-card"
              >
                <div class="trajectory-header">
                  <span class="trajectory-station">{{ traj.station_name }}</span>
                  <span class="trajectory-batch">批次: {{ traj.batch_id }}</span>
                </div>
                <div class="trajectory-stats">
                  <div class="mini-stat">
                    <span class="mini-label">点数</span>
                    <span class="mini-value">{{ traj.point_count }}</span>
                  </div>
                  <div class="mini-stat">
                    <span class="mini-label">纬度RMSE</span>
                    <span class="mini-value">{{ ((traj.rmse_lat ?? 0) * 111000).toFixed(2) }} m</span>
                  </div>
                  <div class="mini-stat">
                    <span class="mini-label">距离RMSE</span>
                    <span class="mini-value">{{ ((traj.rmse_lon ?? 0) * 111000).toFixed(2) }} m</span>
                  </div>
                  <div class="mini-stat">
                    <span class="mini-label">高度RMSE</span>
                    <span class="mini-value">{{ (traj.rmse_alt ?? 0).toFixed(2) }} m</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
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
import SmoothedTrajectoryView from '@/components/errorAnalysis/SmoothedTrajectoryView.vue'

const route = useRoute()
const router = useRouter()
const store = useErrorAnalysisStore()
const appStore = useAppStore()

const activeTab = ref('trajectory')
const error = ref<string | null>(null)

const tabs = [
  { key: 'trajectory', label: '轨迹对比' },
  { key: 'statistics', label: '统计信息' },
]

const statusInfo = computed(() => {
  const status = store.taskDetail?.status || 'pending'
  return TASK_STATUS_INFO[status] || { label: status, color: '#9ca3af' }
})

const algorithmDisplayName = computed(() => {
  const name = store.taskDetail?.algorithm_name || 'kalman'
  const names: Record<string, string> = {
    kalman: '卡尔曼滤波算法',
    particle_filter: '粒子滤波算法',
    spline: '样条插值算法',
  }
  return names[name] || name
})

const totalPoints = computed(() => {
  if (!store.taskDetail?.smoothed_trajectories) return 0
  return store.taskDetail.smoothed_trajectories.reduce((sum, t) => sum + t.point_count, 0)
})

const avgRmseLat = computed(() => {
  const trajs = store.taskDetail?.smoothed_trajectories || []
  if (trajs.length === 0) return 0
  const sum = trajs.reduce((s, t) => s + (t.rmse_lat ?? 0), 0)
  return (sum / trajs.length) * 111000
})

const avgRmseLon = computed(() => {
  const trajs = store.taskDetail?.smoothed_trajectories || []
  if (trajs.length === 0) return 0
  const sum = trajs.reduce((s, t) => s + (t.rmse_lon ?? 0), 0)
  return (sum / trajs.length) * 111000
})

const avgRmseAlt = computed(() => {
  const trajs = store.taskDetail?.smoothed_trajectories || []
  if (trajs.length === 0) return 0
  const sum = trajs.reduce((s, t) => s + (t.rmse_alt ?? 0), 0)
  return sum / trajs.length
})

function goBack() {
  router.push('/error-analysis')
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
.smoothed-trajectory-history {
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

/* 算法卡片 */
.algorithm-card {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  color: white;
}

.algorithm-header {
  display: flex;
  align-items: center;
  gap: 16px;
}

.algorithm-icon {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
}

.algorithm-icon svg {
  width: 28px;
  height: 28px;
}

.algorithm-info {
  flex: 1;
}

.algorithm-info h2 {
  margin: 0 0 4px 0;
  font-size: 20px;
  font-weight: 600;
}

.algorithm-info p {
  margin: 0;
  opacity: 0.9;
  font-size: 14px;
}

.status-badge {
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  background: rgba(255, 255, 255, 0.2);
}

/* 概览卡片 */
.overview-section {
  margin-bottom: 24px;
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.overview-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.card-icon {
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

.card-icon.processing { background: linear-gradient(135deg, #3b82f6, #2563eb); }
.card-icon.stations { background: linear-gradient(135deg, #8b5cf6, #7c3aed); }
.card-icon.tracks { background: linear-gradient(135deg, #f59e0b, #d97706); }
.card-icon.points { background: linear-gradient(135deg, #10b981, #059669); }

.card-content {
  display: flex;
  flex-direction: column;
}

.card-value {
  font-size: 24px;
  font-weight: 700;
  color: #1f2937;
}

.card-label {
  font-size: 13px;
  color: #6b7280;
}

/* 标签页 */
.tabs-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
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
  min-height: 400px;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 300px;
  color: #6b7280;
}

/* 统计面板 */
.statistics-panel h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.statistics-panel h4:not(:first-child) {
  margin-top: 32px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.stat-card {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 16px;
  background: #f3f4f6;
  border-radius: 8px;
}

.stat-label {
  font-size: 13px;
  color: #6b7280;
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
}

/* 轨迹列表 */
.trajectory-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.trajectory-card {
  padding: 16px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.trajectory-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e5e7eb;
}

.trajectory-station {
  font-weight: 600;
  color: #1f2937;
}

.trajectory-batch {
  font-size: 13px;
  color: #6b7280;
}

.trajectory-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.mini-stat {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.mini-label {
  font-size: 12px;
  color: #9ca3af;
}

.mini-value {
  font-size: 14px;
  font-weight: 500;
  color: #1f2937;
}

@media (max-width: 1024px) {
  .overview-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .trajectory-stats {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .algorithm-header {
    flex-direction: column;
    text-align: center;
  }

  .overview-grid {
    grid-template-columns: 1fr;
  }

  .trajectory-stats {
    grid-template-columns: 1fr;
  }
}
</style>
