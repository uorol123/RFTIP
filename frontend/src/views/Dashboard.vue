<template>
  <div class="dashboard-page">
    <AppHeader />
    <div class="dashboard">
      <div class="dashboard-header">
        <div>
          <h1 class="dashboard-title">欢迎回来，{{ user?.username || '用户' }}！</h1>
          <p class="dashboard-subtitle">这是您的雷达轨迹分析控制台</p>
        </div>
        <div class="header-actions">
          <button class="btn btn-primary" @click="navigateToUpload">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            上传数据
          </button>
        </div>
      </div>

      <div class="dashboard-content">
      <!-- 统计卡片 -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon stat-icon-blue">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
          </div>
          <div class="stat-content">
            <div class="stat-label">数据文件</div>
            <div class="stat-value">{{ stats.totalFiles }}</div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon stat-icon-green">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
              />
            </svg>
          </div>
          <div class="stat-content">
            <div class="stat-label">轨迹总数</div>
            <div class="stat-value">{{ formatNumber(stats.totalTracks) }}</div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon stat-icon-purple">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
              />
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
              />
            </svg>
          </div>
          <div class="stat-content">
            <div class="stat-label">禁飞区</div>
            <div class="stat-value">{{ stats.totalZones }}</div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon stat-icon-orange">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          </div>
          <div class="stat-content">
            <div class="stat-label">入侵记录</div>
            <div class="stat-value">{{ stats.recentIntrusions }}</div>
          </div>
        </div>
      </div>

      <!-- 快捷操作 -->
      <div class="dashboard-section">
        <h2 class="section-title">快捷操作</h2>
        <div class="quick-actions">
          <router-link to="/data" class="quick-action">
            <div class="quick-action-icon quick-action-icon-blue">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                />
              </svg>
            </div>
            <div class="quick-action-content">
              <div class="quick-action-title">数据管理</div>
              <div class="quick-action-desc">上传和管理雷达数据文件</div>
            </div>
          </router-link>

          <router-link to="/tracks" class="quick-action">
            <div class="quick-action-icon quick-action-icon-green">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"
                />
              </svg>
            </div>
            <div class="quick-action-content">
              <div class="quick-action-title">轨迹可视化</div>
              <div class="quick-action-desc">查看三维轨迹可视化</div>
            </div>
          </router-link>

          <router-link to="/zones" class="quick-action">
            <div class="quick-action-icon quick-action-icon-purple">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
                />
              </svg>
            </div>
            <div class="quick-action-content">
              <div class="quick-action-title">禁飞区管理</div>
              <div class="quick-action-desc">配置禁飞区和预警</div>
            </div>
          </router-link>

          <router-link to="/analysis" class="quick-action">
            <div class="quick-action-icon quick-action-icon-orange">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                />
              </svg>
            </div>
            <div class="quick-action-content">
              <div class="quick-action-title">AI 分析</div>
              <div class="quick-action-desc">智能分析轨迹模式</div>
            </div>
          </router-link>
        </div>
      </div>

      <!-- 最近文件 -->
      <div class="dashboard-section">
        <div class="section-header">
          <h2 class="section-title">最近文件</h2>
          <router-link to="/data" class="section-link">查看全部</router-link>
        </div>
        <div v-if="recentFiles.length === 0" class="section-empty">
          <div class="empty-state">
            <div class="empty-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
            </div>
            <div class="empty-title">暂无数据文件</div>
            <div class="empty-desc">上传您的第一个雷达数据文件开始使用</div>
            <router-link to="/data" class="btn btn-primary">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              上传文件
            </router-link>
          </div>
        </div>
        <div v-else class="files-list">
          <div
            v-for="file in recentFiles"
            :key="file.id"
            class="file-item"
            @click="navigateToFile(file.id)"
          >
            <div class="file-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
            </div>
            <div class="file-info">
              <div class="file-name">{{ file.original_filename || file.file_name }}</div>
              <div class="file-meta">
                <span class="file-status" :class="`status-${file.status}`">
                  {{ getStatusText(file.status) }}
                </span>
                <span class="file-date">{{ formatDate(file.upload_time) }}</span>
              </div>
            </div>
            <div class="file-size">{{ formatFileSize(file.file_size) }}</div>
          </div>
        </div>
      </div>

      <!-- 最近活动 -->
      <div class="dashboard-section">
        <h2 class="section-title">最近活动</h2>
        <div v-if="activities.length === 0" class="section-empty">
          <div class="empty-state">
            <div class="empty-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <div class="empty-title">暂无活动记录</div>
            <div class="empty-desc">您的活动将显示在这里</div>
          </div>
        </div>
        <div v-else class="activity-list">
          <div v-for="activity in activities" :key="activity.id" class="activity-item">
            <div class="activity-icon" :class="`activity-icon-${activity.type}`">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path
                  v-if="activity.type === 'upload'"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                />
                <path
                  v-else-if="activity.type === 'analysis'"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                />
                <path
                  v-else-if="activity.type === 'zone'"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
                />
                <path
                  v-else
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <div class="activity-content">
              <div class="activity-text">{{ activity.text }}</div>
              <div class="activity-time">{{ formatRelativeTime(activity.time) }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useAuthStore } from '@/stores/auth'
import AppHeader from '@/components/AppHeader.vue'

const router = useRouter()
const authStore = useAuthStore()

const { user } = storeToRefs(authStore)

const recentFiles = ref<any[]>([])

interface Activity {
  id: number
  type: 'upload' | 'analysis' | 'zone' | 'success'
  text: string
  time: string
}

const activities = ref<Activity[]>([
  {
    id: 1,
    type: 'upload',
    text: '文件 "radar_data_2024.csv" 上传成功',
    time: new Date(Date.now() - 2 * 60 * 1000).toISOString(),
  },
  {
    id: 2,
    type: 'analysis',
    text: '轨迹 #12345 的分析已完成',
    time: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
  },
  {
    id: 3,
    type: 'zone',
    text: '新禁飞区 "机场限制区" 已创建',
    time: new Date(Date.now() - 60 * 60 * 1000).toISOString(),
  },
])

const stats = ref({
  totalFiles: 0,
  totalTracks: 0,
  totalZones: 0,
  recentIntrusions: 0,
})

const loadDashboardData = async () => {
  // 静态数据，暂时不调用 API
  stats.value = {
    totalFiles: 0,
    totalTracks: 0,
    totalZones: 0,
    recentIntrusions: 0,
  }
  recentFiles.value = []
}

const navigateToUpload = () => {
  router.push('/data')
}

const navigateToFile = (fileId: number) => {
  router.push(`/data/${fileId}`)
}

const getStatusText = (status: string): string => {
  const statusMap: Record<string, string> = {
    pending: '待处理',
    processing: '处理中',
    completed: '已完成',
    failed: '失败',
  }
  return statusMap[status] || status
}

const formatNumber = (num: number): string => {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}

const formatFileSize = (bytes: number): string => {
  if (!bytes) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

const formatDate = (dateString: string): string => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return '刚刚'
  if (diffMins < 60) return `${diffMins}分钟前`
  if (diffHours < 24) return `${diffHours}小时前`
  if (diffDays < 7) return `${diffDays}天前`
  return date.toLocaleDateString('zh-CN')
}

const formatRelativeTime = (dateString: string): string => {
  return formatDate(dateString)
}

onMounted(() => {
  loadDashboardData()
})
</script>

<style scoped>
.dashboard-page {
  min-height: 100vh;
  background: var(--bg-primary);
}

.dashboard {
  padding: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.dashboard-title {
  margin: 0 0 0.25rem;
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text-primary);
}

.dashboard-subtitle {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.9375rem;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
}

.dashboard-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1rem;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem;
  border-radius: 1rem;
  background: var(--bg-secondary);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  flex-shrink: 0;
  width: 3rem;
  height: 3rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.75rem;
}

.stat-icon svg {
  width: 1.5rem;
  height: 1.5rem;
}

.stat-icon-blue {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.stat-icon-green {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.stat-icon-purple {
  background: rgba(139, 92, 246, 0.1);
  color: #8b5cf6;
}

.stat-icon-orange {
  background: rgba(249, 115, 22, 0.1);
  color: #f97316;
}

.stat-content {
  flex: 1;
}

.stat-label {
  color: var(--text-secondary);
  font-size: 0.8125rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.stat-value {
  color: var(--text-primary);
  font-size: 1.75rem;
  font-weight: 700;
  line-height: 1.2;
}

.dashboard-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-title {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
}

.section-link {
  color: var(--color-primary);
  font-size: 0.875rem;
  font-weight: 500;
  text-decoration: none;
}

.section-link:hover {
  text-decoration: underline;
}

.section-empty {
  padding: 2rem 0;
}

.empty-state {
  text-align: center;
  padding: 3rem 1rem;
}

.empty-icon {
  width: 4rem;
  height: 4rem;
  margin: 0 auto 1rem;
  color: var(--text-muted);
  opacity: 0.5;
}

.empty-icon svg {
  width: 100%;
  height: 100%;
}

.empty-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.empty-desc {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-bottom: 1.5rem;
}

.quick-actions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.quick-action {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-radius: 0.75rem;
  background: var(--bg-secondary);
  text-decoration: none;
  transition: all 0.2s;
}

.quick-action:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.quick-action-icon {
  flex-shrink: 0;
  width: 2.5rem;
  height: 2.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.5rem;
}

.quick-action-icon svg {
  width: 1.25rem;
  height: 1.25rem;
}

.quick-action-icon-blue {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.quick-action-icon-green {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.quick-action-icon-purple {
  background: rgba(139, 92, 246, 0.1);
  color: #8b5cf6;
}

.quick-action-icon-orange {
  background: rgba(249, 115, 22, 0.1);
  color: #f97316;
}

.quick-action-content {
  flex: 1;
}

.quick-action-title {
  color: var(--text-primary);
  font-size: 0.875rem;
  font-weight: 600;
}

.quick-action-desc {
  color: var(--text-muted);
  font-size: 0.8125rem;
}

.files-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  background: var(--bg-secondary);
  cursor: pointer;
  transition: background 0.2s;
}

.file-item:hover {
  background: var(--bg-tertiary);
}

.file-icon {
  flex-shrink: 0;
  width: 2rem;
  height: 2rem;
  color: var(--color-primary);
}

.file-icon svg {
  width: 100%;
  height: 100%;
}

.file-info {
  flex: 1;
  min-width: 0;
}

.file-name {
  color: var(--text-primary);
  font-size: 0.875rem;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.125rem;
}

.file-status {
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: capitalize;
}

.status-completed {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.status-processing {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.status-pending {
  background: rgba(249, 115, 22, 0.1);
  color: #f97316;
}

.status-failed {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.file-date {
  color: var(--text-muted);
  font-size: 0.8125rem;
}

.file-size {
  flex-shrink: 0;
  color: var(--text-muted);
  font-size: 0.8125rem;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.activity-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.75rem 0;
}

.activity-icon {
  flex-shrink: 0;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.5rem;
}

.activity-icon svg {
  width: 1rem;
  height: 1rem;
}

.activity-icon-upload {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.activity-icon-analysis {
  background: rgba(139, 92, 246, 0.1);
  color: #8b5cf6;
}

.activity-icon-zone {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.activity-icon-success {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.activity-content {
  flex: 1;
}

.activity-text {
  color: var(--text-primary);
  font-size: 0.875rem;
}

.activity-time {
  color: var(--text-muted);
  font-size: 0.8125rem;
  margin-top: 0.125rem;
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

@media (max-width: 768px) {
  .dashboard {
    padding: 1rem;
  }

  .stats-grid,
  .quick-actions {
    grid-template-columns: 1fr;
  }

  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
