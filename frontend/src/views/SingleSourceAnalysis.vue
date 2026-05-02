<template>
  <div class="error-analysis-page">
    <AppHeader />

    <div class="error-analysis-container">
      <div class="page-header">
        <div>
          <h1 class="page-title">单源盲测分析</h1>
          <p class="page-subtitle">{{ store.currentAlgorithmName }}</p>
        </div>
        <div class="header-actions">
          <router-link to="/error-analysis/tasks" class="btn btn-secondary">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            任务管理
          </router-link>
          <router-link to="/data" class="btn btn-secondary">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/>
            </svg>
            上传数据
          </router-link>
        </div>
      </div>

      <div class="mode-switch">
        <router-link to="/error-analysis/multi-source" class="mode-tab">多源参考</router-link>
        <router-link to="/error-analysis/single-source" class="mode-tab active">单源盲测</router-link>
      </div>

      <div class="main-content">
        <div class="config-panel-wrapper">
          <ErrorConfigPanel
            :algorithm-mode="'single_source'"
            @start="handleAnalysisStart"
          />
        </div>

        <div class="content-panel-wrapper">
          <div v-if="store.currentTask" class="progress-section">
            <ErrorProgressBar
              :status="store.currentTask.status"
              :progress="store.taskProgress"
              :error="store.currentTask.error_message"
            />
          </div>

          <div v-if="!store.currentTask" class="empty-section">
            <EmptyState
              title="开始单源盲测分析"
              description="选择一个雷达站和一条目标航迹，配置平滑参数后开始轨迹平滑处理"
            >
              <template #icon>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                </svg>
              </template>
            </EmptyState>
          </div>

          <div v-else-if="store.isTaskCompleted && store.taskDetail" class="results-section">
            <SmoothedTrajectoryView
              v-if="store.taskDetail.smoothed_trajectories.length > 0"
              :trajectories="store.taskDetail.smoothed_trajectories"
            />
            <div v-else class="empty-result">
              <p>分析完成，但未生成平滑轨迹数据</p>
            </div>
          </div>

          <div v-else-if="store.isTaskFailed" class="error-section">
            <div class="error-card">
              <svg class="error-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
              </svg>
              <h3>分析失败</h3>
              <p>{{ store.currentTask?.error_message || '未知错误' }}</p>
              <button class="btn btn-primary" @click="handleRetry">重新开始</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onUnmounted } from 'vue'
import { useErrorAnalysisStore } from '@/stores/errorAnalysis'
import EmptyState from '@/components/EmptyState.vue'
import AppHeader from '@/components/AppHeader.vue'
import ErrorConfigPanel from '@/components/errorAnalysis/ErrorConfigPanel.vue'
import ErrorProgressBar from '@/components/errorAnalysis/ErrorProgressBar.vue'
import SmoothedTrajectoryView from '@/components/errorAnalysis/SmoothedTrajectoryView.vue'

const store = useErrorAnalysisStore()

function handleAnalysisStart() {
  // no-op, results render automatically when completed
}

function handleRetry() {
  store.clearCurrentTask()
}

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
  margin-bottom: 1rem;
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

.mode-switch {
  display: flex;
  gap: 0;
  margin-bottom: 1.5rem;
  background: var(--bg-secondary);
  border-radius: 0.5rem;
  padding: 0.25rem;
  width: fit-content;
}

.mode-tab {
  padding: 0.5rem 1.25rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary);
  text-decoration: none;
  transition: all 0.2s;
  cursor: pointer;
}

.mode-tab:hover {
  color: var(--text-primary);
  background: var(--bg-tertiary);
}

.mode-tab.active {
  background: var(--color-primary);
  color: white;
}

.main-content {
  display: grid;
  grid-template-columns: 350px 1fr;
  gap: 1.5rem;
  align-items: start;
}

.config-panel-wrapper {
  position: sticky;
  top: 5rem;
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

.empty-result {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  color: var(--text-secondary);
  background: var(--bg-secondary);
  border-radius: 0.75rem;
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

.btn-primary { background: var(--color-primary); color: white; }
.btn-primary:hover { background: #2563eb; }

.btn-secondary { background: var(--bg-secondary); color: var(--text-primary); }
.btn-secondary:hover { background: var(--bg-tertiary); }

@media (max-width: 1024px) {
  .main-content { grid-template-columns: 1fr; }
  .config-panel-wrapper { position: static; }
}

@media (max-width: 640px) {
  .error-analysis-container { padding: 1rem; }
  .page-header { flex-direction: column; align-items: flex-start; }
}
</style>
