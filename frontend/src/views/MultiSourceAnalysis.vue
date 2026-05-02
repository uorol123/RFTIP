<template>
  <div class="error-analysis-page">
    <AppHeader />

    <div class="error-analysis-container">
      <div class="page-header">
        <div>
          <h1 class="page-title">多源参考分析</h1>
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
        <router-link to="/error-analysis/multi-source" class="mode-tab active">多源参考</router-link>
        <router-link to="/error-analysis/single-source" class="mode-tab">单源盲测</router-link>
      </div>

      <div class="main-content">
        <div class="config-panel-wrapper">
          <ErrorConfigPanel
            :algorithm-mode="'multi_source'"
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
              title="开始多源参考分析"
              description="选择雷达站和航迹数据，配置分析参数后开始误差分析"
            >
              <template #icon>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
                </svg>
              </template>
            </EmptyState>
          </div>

          <div v-else-if="store.isTaskCompleted" class="results-section">
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

            <div v-if="activeTab === 'chart'" class="tab-content">
              <ErrorResultChart
                :chart-data="store.chartData"
                :loading="store.chartDataLoading"
              />
            </div>

            <div v-else-if="activeTab === 'table'" class="tab-content">
              <ErrorTable
                v-if="store.analysisResult"
                :results="store.analysisResult.errors"
                :loading="store.resultLoading"
              />
            </div>

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
import { ref, onUnmounted } from 'vue'
import { useErrorAnalysisStore } from '@/stores/errorAnalysis'
import { useAppStore } from '@/stores/app'
import EmptyState from '@/components/EmptyState.vue'
import AppHeader from '@/components/AppHeader.vue'
import ErrorConfigPanel from '@/components/errorAnalysis/ErrorConfigPanel.vue'
import ErrorProgressBar from '@/components/errorAnalysis/ErrorProgressBar.vue'
import ErrorResultChart from '@/components/errorAnalysis/ErrorResultChart.vue'
import ErrorTable from '@/components/errorAnalysis/ErrorTable.vue'
import MatchVisualization from '@/components/errorAnalysis/MatchVisualization.vue'

const store = useErrorAnalysisStore()
const appStore = useAppStore()

const activeTab = ref<'chart' | 'table' | 'matches'>('chart')

const tabs = [
  { key: 'chart' as const, label: '图表' },
  { key: 'table' as const, label: '详细数据' },
  { key: 'matches' as const, label: '匹配组' },
]

function handleAnalysisStart() {
  activeTab.value = 'chart'
}

function handleRetry() {
  store.clearCurrentTask()
}

async function handleSegmentChange(segmentId: number | null) {
  if (store.currentTask) {
    await store.loadMatchGroups(store.currentTask.task_id, {
      segment_id: segmentId ?? undefined,
      skip: 0,
      limit: 100,
    })
  }
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
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
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
  .tabs { overflow-x: auto; }
}
</style>
