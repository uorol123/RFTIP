<template>
  <div class="error-progress-bar">
    <!-- 进度信息 -->
    <div class="progress-header">
      <div class="progress-status">
        <span class="status-badge" :class="`status-${status}`">
          <svg v-if="isRunning" class="status-icon processing" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="3" opacity="0.25"/>
            <path fill="none" stroke="currentColor" stroke-width="3" d="M12 2a10 10 0 0 1 10 10">
              <animateTransform attributeName="transform" type="rotate" from="0 12 12" to="360 12 12" dur="1s" repeatCount="indefinite"/>
            </path>
          </svg>
          <svg v-else-if="status === 'completed'" class="status-icon completed" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
          </svg>
          <svg v-else-if="status === 'failed'" class="status-icon failed" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
          </svg>
          <svg v-else class="status-icon pending" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle cx="12" cy="12" r="10" stroke-width="2"/>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6l4 2"/>
          </svg>
          {{ statusText }}
        </span>
        <span v-if="stage" class="progress-stage">{{ stage }}</span>
      </div>
      <div class="progress-percentage">{{ progress }}%</div>
    </div>

    <!-- 进度条 -->
    <div class="progress-bar-container">
      <div
        class="progress-bar-fill"
        :class="`progress-${status}`"
        :style="{ width: `${progress}%` }"
      >
        <div class="progress-shimmer"></div>
      </div>
    </div>

    <!-- 步骤指示器 -->
    <div class="progress-steps">
      <div
        v-for="(step, index) in steps"
        :key="index"
        class="progress-step"
        :class="{
          'is-active': currentStepIndex === index,
          'is-completed': currentStepIndex > index,
          'is-pending': currentStepIndex < index
        }"
      >
        <div class="step-circle">
          <svg v-if="currentStepIndex > index" class="step-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
          </svg>
          <svg v-else-if="currentStepIndex === index && isRunning" class="step-icon spinning" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="2"/>
            <path fill="none" stroke="currentColor" stroke-width="2" d="M12 2a10 10 0 0 1 10 10">
              <animateTransform attributeName="transform" type="rotate" from="0 12 12" to="360 12 12" dur="1s" repeatCount="indefinite"/>
            </path>
          </svg>
          <span v-else class="step-number">{{ index + 1 }}</span>
        </div>
        <div class="step-label">{{ step }}</div>
      </div>
    </div>

    <!-- 错误信息 -->
    <div v-if="error" class="progress-error">
      <svg class="error-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
      </svg>
      <span>{{ error }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { TaskStatus } from '@/types/errorAnalysis'
import { TASK_STATUS_INFO } from '@/types/errorAnalysis'

interface Props {
  status: TaskStatus
  progress: number
  stage?: string
  error?: string | null
}

const props = withDefaults(defineProps<Props>(), {
  stage: '',
  error: null,
})

const steps = [
  '数据准备',
  '轨迹匹配',
  '段分割',
  '误差计算',
  '统计分析',
]

const currentStepIndex = computed(() => {
  const progress = props.progress
  if (progress < 20) return 0
  if (progress < 40) return 1
  if (progress < 60) return 2
  if (progress < 80) return 3
  return 4
})

const statusText = computed(() => {
  return TASK_STATUS_INFO[props.status]?.label || '未知'
})

const isRunning = computed(() => {
  return ['pending', 'extracting', 'interpolating', 'matching', 'calculating'].includes(props.status)
})
</script>

<style scoped>
.error-progress-bar {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1.5rem;
  background: var(--bg-secondary);
  border-radius: 0.75rem;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.progress-status {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.375rem 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.8125rem;
  font-weight: 500;
}

.status-badge.status-pending,
.status-badge.status-extracting,
.status-badge.status-interpolating,
.status-badge.status-matching,
.status-badge.status-calculating {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.status-badge.status-completed {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.status-badge.status-failed {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.status-icon {
  width: 1rem;
  height: 1rem;
}

.status-icon.processing {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.progress-stage {
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.progress-percentage {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  font-variant-numeric: tabular-nums;
}

.progress-bar-container {
  height: 0.75rem;
  background: var(--bg-tertiary);
  border-radius: 0.375rem;
  overflow: hidden;
  position: relative;
}

.progress-bar-fill {
  height: 100%;
  border-radius: 0.375rem;
  position: relative;
  transition: width 0.3s ease-out;
  overflow: hidden;
}

.progress-bar-fill.progress-pending,
.progress-bar-fill.progress-extracting,
.progress-bar-fill.progress-interpolating,
.progress-bar-fill.progress-matching,
.progress-bar-fill.progress-calculating {
  background: linear-gradient(90deg, #3b82f6 0%, #60a5fa 100%);
}

.progress-bar-fill.progress-completed {
  background: linear-gradient(90deg, #10b981 0%, #34d399 100%);
}

.progress-bar-fill.progress-failed {
  background: linear-gradient(90deg, #ef4444 0%, #f87171 100%);
}

.progress-shimmer {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(255, 255, 255, 0.2) 50%,
    transparent 100%
  );
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% {
    left: -100%;
  }
  100% {
    left: 100%;
  }
}

.progress-steps {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
}

.progress-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
}

.step-circle {
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: var(--bg-tertiary);
  color: var(--text-muted);
  transition: all 0.3s;
}

.progress-step.is-active .step-circle {
  background: var(--color-primary);
  color: white;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
}

.progress-step.is-completed .step-circle {
  background: #10b981;
  color: white;
}

.step-icon {
  width: 1rem;
  height: 1rem;
}

.step-icon.spinning {
  animation: spin 1s linear infinite;
}

.step-number {
  font-size: 0.875rem;
  font-weight: 600;
}

.step-label {
  font-size: 0.75rem;
  color: var(--text-secondary);
  text-align: center;
}

.progress-step.is-active .step-label {
  color: var(--text-primary);
  font-weight: 500;
}

.progress-error {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: 0.5rem;
  color: #ef4444;
  font-size: 0.875rem;
}

.error-icon {
  width: 1.25rem;
  height: 1.25rem;
  flex-shrink: 0;
}

@media (max-width: 640px) {
  .progress-steps {
    flex-wrap: wrap;
  }

  .progress-step {
    min-width: calc(33.333% - 0.5rem);
  }

  .step-label {
    font-size: 0.6875rem;
  }
}
</style>
