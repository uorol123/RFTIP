<template>
  <div class="smoothed-trajectory-detail">
    <!-- 算法说明 -->
    <section class="algorithm-info">
      <h2>{{ algorithmDisplayName }}</h2>
      <p class="algorithm-desc">
        基于匀速运动模型的卡尔曼滤波算法，对单站雷达轨迹进行平滑去噪。
        通过对比原始轨迹与平滑后轨迹的偏差，评估观测数据的质量。
      </p>
    </section>

    <!-- 处理概览 -->
    <section class="overview-section">
      <div class="overview-grid">
        <div class="overview-card">
          <div class="card-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
          </div>
          <div class="card-content">
            <span class="card-value">{{ taskDetail.processing_time_seconds.toFixed(2) }}</span>
            <span class="card-label">处理时间 (秒)</span>
          </div>
        </div>

        <div class="overview-card">
          <div class="card-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"/>
            </svg>
          </div>
          <div class="card-content">
            <span class="card-value">{{ taskDetail.track_ids.length }}</span>
            <span class="card-label">轨迹数量</span>
          </div>
        </div>

        <div class="overview-card">
          <div class="card-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
            </svg>
          </div>
          <div class="card-content">
            <span class="card-value">{{ taskDetail.smoothed_trajectories.length }}</span>
            <span class="card-label">平滑轨迹组</span>
          </div>
        </div>

        <div class="overview-card">
          <div class="card-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
            </svg>
          </div>
          <div class="card-content">
            <span class="card-value">{{ totalPoints }}</span>
            <span class="card-label">总轨迹点数</span>
          </div>
        </div>
      </div>
    </section>

    <!-- 雷达站信息 -->
    <section class="station-section">
      <h3>参与雷达站</h3>
      <div class="station-badges">
        <span
          v-for="stationId in taskDetail.radar_station_ids"
          :key="stationId"
          class="station-badge"
        >
          {{ getStationName(stationId) }}
        </span>
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

      <!-- 平滑轨迹对比 -->
      <div v-if="activeTab === 'trajectory'" class="tab-content">
        <SmoothedTrajectoryView
          v-if="taskDetail.smoothed_trajectories.length > 0"
          :trajectories="taskDetail.smoothed_trajectories"
        />
        <EmptyState
          v-else
          title="暂无平滑轨迹数据"
          description="该任务没有生成平滑轨迹数据"
        />
      </div>

      <!-- 统计信息 -->
      <div v-if="activeTab === 'statistics'" class="tab-content">
        <div class="statistics-panel">
          <h4>误差统计 (RMSE)</h4>
          <div class="stats-grid" v-if="taskDetail.smoothed_trajectories.length > 0">
            <div class="stat-item">
              <span class="stat-label">平均纬度偏差</span>
              <span class="stat-value">
                {{ avgRmseLat.toFixed(2) }} m
              </span>
            </div>
            <div class="stat-item">
              <span class="stat-label">平均距离偏差</span>
              <span class="stat-value">
                {{ avgRmseLon.toFixed(2) }} m
              </span>
            </div>
            <div class="stat-item">
              <span class="stat-label">平均高度偏差</span>
              <span class="stat-value">
                {{ avgRmseAlt.toFixed(2) }} m
              </span>
            </div>
          </div>

          <h4>各轨迹详情</h4>
          <div class="trajectory-list">
            <div
              v-for="traj in taskDetail.smoothed_trajectories"
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
              <div class="trajectory-config" v-if="traj.process_noise || traj.measurement_noise">
                <span class="config-label">配置:</span>
                <span v-if="traj.process_noise">过程噪声: {{ traj.process_noise }}</span>
                <span v-if="traj.measurement_noise">观测噪声: {{ traj.measurement_noise }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { TaskDetailResponse } from '@/types/errorAnalysis'
import SmoothedTrajectoryView from './SmoothedTrajectoryView.vue'
import EmptyState from '@/components/EmptyState.vue'

interface Props {
  taskDetail: TaskDetailResponse
}

const props = defineProps<Props>()

const activeTab = ref('trajectory')

const tabs = [
  { key: 'trajectory', label: '轨迹对比' },
  { key: 'statistics', label: '统计信息' },
]

const algorithmDisplayName = computed(() => {
  const name = props.taskDetail.algorithm_name || 'kalman'
  const names: Record<string, string> = {
    kalman: '卡尔曼滤波算法',
    particle_filter: '粒子滤波算法',
    spline: '样条插值算法',
  }
  return names[name] || name
})

const totalPoints = computed(() => {
  return props.taskDetail.smoothed_trajectories.reduce((sum, t) => sum + t.point_count, 0)
})

const avgRmseLat = computed(() => {
  const trajs = props.taskDetail.smoothed_trajectories
  if (trajs.length === 0) return 0
  const sum = trajs.reduce((s, t) => s + (t.rmse_lat ?? 0), 0)
  return (sum / trajs.length) * 111000
})

const avgRmseLon = computed(() => {
  const trajs = props.taskDetail.smoothed_trajectories
  if (trajs.length === 0) return 0
  const sum = trajs.reduce((s, t) => s + (t.rmse_lon ?? 0), 0)
  return (sum / trajs.length) * 111000
})

const avgRmseAlt = computed(() => {
  const trajs = props.taskDetail.smoothed_trajectories
  if (trajs.length === 0) return 0
  const sum = trajs.reduce((s, t) => s + (t.rmse_alt ?? 0), 0)
  return sum / trajs.length
})

function getStationName(stationId: number): string {
  // 从 trajectories 中查找站名
  const traj = props.taskDetail.smoothed_trajectories.find(t => t.station_id === stationId)
  if (traj) return traj.station_name
  return `站${stationId}`
}
</script>

<style scoped>
.smoothed-trajectory-detail {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* 算法信息 */
.algorithm-info {
  background: white;
  border-radius: 0.75rem;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.algorithm-info h2 {
  margin: 0 0 0.5rem 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
}

.algorithm-desc {
  margin: 0;
  font-size: 0.9375rem;
  color: var(--text-secondary);
  line-height: 1.6;
}

/* 概览卡片 */
.overview-section {
  background: white;
  border-radius: 0.75rem;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.overview-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: var(--bg-tertiary);
  border-radius: 0.5rem;
}

.card-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.5rem;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
}

.card-icon svg {
  width: 24px;
  height: 24px;
}

.card-content {
  display: flex;
  flex-direction: column;
}

.card-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
}

.card-label {
  font-size: 0.8125rem;
  color: var(--text-secondary);
}

/* 雷达站信息 */
.station-section {
  background: white;
  border-radius: 0.75rem;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.station-section h3 {
  margin: 0 0 1rem 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.station-badges {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.station-badge {
  padding: 0.5rem 1rem;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
  border-radius: 2rem;
  font-size: 0.875rem;
  font-weight: 500;
}

/* 标签页 */
.tabs-section {
  background: white;
  border-radius: 0.75rem;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.tabs-header {
  display: flex;
  gap: 0.5rem;
  border-bottom: 1px solid var(--border-color);
  margin-bottom: 1.5rem;
}

.tab {
  padding: 0.75rem 1.5rem;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  font-size: 0.9375rem;
  font-weight: 500;
  color: var(--text-secondary);
  transition: all 0.2s;
}

.tab:hover {
  color: var(--text-primary);
}

.tab.active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
}

.tab-content {
  min-height: 400px;
}

/* 统计面板 */
.statistics-panel h4 {
  margin: 0 0 1rem 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.statistics-panel h4:not(:first-child) {
  margin-top: 2rem;
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
  padding: 1rem;
  background: var(--bg-tertiary);
  border-radius: 0.5rem;
}

.stat-label {
  font-size: 0.8125rem;
  color: var(--text-secondary);
}

.stat-value {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
}

/* 轨迹列表 */
.trajectory-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.trajectory-card {
  padding: 1rem;
  background: var(--bg-tertiary);
  border-radius: 0.5rem;
  border: 1px solid var(--border-color);
}

.trajectory-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--border-color);
}

.trajectory-station {
  font-weight: 600;
  color: var(--text-primary);
}

.trajectory-batch {
  font-size: 0.8125rem;
  color: var(--text-muted);
}

.trajectory-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
}

.mini-stat {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.mini-label {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.mini-value {
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--text-primary);
}

.trajectory-config {
  display: flex;
  gap: 1rem;
  margin-top: 0.75rem;
  padding-top: 0.5rem;
  border-top: 1px solid var(--border-color);
  font-size: 0.75rem;
  color: var(--text-muted);
}

@media (max-width: 768px) {
  .trajectory-stats {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
