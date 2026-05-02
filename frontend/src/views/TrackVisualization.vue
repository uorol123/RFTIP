<template>
  <div class="page">
    <AppHeader />
    <div class="page-content">
      <div class="page-header">
        <div>
          <h1 class="page-title">轨迹可视化</h1>
          <p class="page-subtitle">查看三维雷达轨迹可视化</p>
        </div>
        <div class="header-actions">
          <button class="btn btn-secondary">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
            </svg>
            导入数据
          </button>
          <button class="btn btn-primary">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
            </svg>
            处理设置
          </button>
        </div>
      </div>

      <!-- 可视化区域 -->
      <div class="visualization-container">
        <div class="viewport">
          <div v-if="!selectedFileId" class="empty-viewport">
            <div class="viewport-placeholder">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
              </svg>
              <h3>{{ files.length === 0 ? '暂无轨迹数据' : '请选择文件进行可视化' }}</h3>
              <p>{{ files.length === 0 ? '请先在数据管理页面上传并处理雷达数据文件' : '从右侧列表中选择一个已完成的文件' }}</p>
              <button v-if="files.length === 0" class="btn btn-primary" @click="navigateToData">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                </svg>
                前往数据管理
              </button>
            </div>
          </div>
          <div v-else class="viewport-content">
            <div class="viewport-header">
              <span class="viewport-file-name">{{ files.find(f => f.id === selectedFileId)?.filename }}</span>
              <button class="btn-close-viewport" @click="selectedFileId = null">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div class="viewport-canvas">
              <p class="canvas-placeholder">3D 可视化区域</p>
              <p class="canvas-hint">轨迹数据将在此处显示</p>
            </div>
          </div>
        </div>

        <!-- 控制面板 -->
        <div class="control-panel">
          <div class="panel-section">
            <h3 class="panel-title">显示设置</h3>
            <div class="control-group">
              <label class="control-label">轨迹颜色</label>
              <div class="color-options">
                <div class="color-option color-blue active"></div>
                <div class="color-option color-green"></div>
                <div class="color-option color-orange"></div>
                <div class="color-option color-purple"></div>
              </div>
            </div>
            <div class="control-group">
              <label class="control-label">轨迹粗细</label>
              <input type="range" min="1" max="10" value="3" class="slider" />
            </div>
            <div class="control-group">
              <label class="checkbox-label">
                <input type="checkbox" checked />
                <span>显示原始轨迹</span>
              </label>
            </div>
            <div class="control-group">
              <label class="checkbox-label">
                <input type="checkbox" checked />
                <span>显示校正轨迹</span>
              </label>
            </div>
            <div class="control-group">
              <label class="checkbox-label">
                <input type="checkbox" />
                <span>显示轨迹点</span>
              </label>
            </div>
          </div>

          <div class="panel-section">
            <h3 class="panel-title">视图控制</h3>
            <div class="view-buttons">
              <button class="view-btn active" title="3D 视图">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 10l-2 1m0 0l-2-1m2 1v2.5M20 7l-2 1m2-1l-2-1m2 1v2.5M14 4l-2-1-2 1M4 7l2-1M4 7l2 1M4 7v2.5M12 21l-2-1m2 1l2-1m-2 1v-2.5M6 18l-2-1v-2.5M18 18l2-1v-2.5" />
                </svg>
                3D
              </button>
              <button class="view-btn" title="俯视图">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
                </svg>
                俯视
              </button>
              <button class="view-btn" title="侧视图">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2" />
                </svg>
                侧视
              </button>
            </div>
          </div>

          <div class="panel-section">
            <h3 class="panel-title">轨迹列表</h3>
            <div class="track-list">
              <div v-if="loading" class="track-list-loading">
                <svg class="spinner" viewBox="0 0 24 24">
                  <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="3" stroke-dasharray="32" stroke-linecap="round" />
                </svg>
                <p>加载中...</p>
              </div>
              <div v-else-if="files.length === 0" class="track-list-empty">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <p>暂无轨迹数据</p>
                <button class="btn-link" @click="navigateToData">前往上传</button>
              </div>
              <div v-else class="track-list-items">
                <div
                  v-for="file in files"
                  :key="file.id"
                  class="track-list-item"
                  :class="{ active: selectedFileId === file.id }"
                  @click="selectFile(file)"
                >
                  <div class="track-item-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
                    </svg>
                  </div>
                  <div class="track-item-info">
                    <div class="track-item-name">{{ file.filename }}</div>
                    <div class="track-item-meta">
                      <span class="track-item-rows">{{ file.row_count || 0 }} 行数据</span>
                      <span class="track-item-date">{{ formatDate(file.uploaded_at) }}</span>
                    </div>
                  </div>
                  <div class="track-item-status status-completed">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppHeader from '@/components/AppHeader.vue'
import { filesApi } from '@/api/files'
import { useAppStore } from '@/stores/app'
import type { FileItem } from '@/api/types'

const router = useRouter()
const appStore = useAppStore()

const files = ref<FileItem[]>([])
const loading = ref(false)
const selectedFileId = ref<number | null>(null)

// 加载已完成的文件列表
const loadFiles = async () => {
  loading.value = true
  try {
    const response = await filesApi.getFileList({
      skip: 0,
      limit: 50,
      status: 'completed',
      category: 'trajectory', // 只显示轨迹数据文件
    })
    files.value = response.files
  } catch (error: any) {
    appStore.error(error.message || '加载文件列表失败')
  } finally {
    loading.value = false
  }
}

// 选择文件进行可视化
const selectFile = (file: FileItem) => {
  selectedFileId.value = file.id
  // TODO: 加载该文件的轨迹数据进行可视化
}

// 导航到数据管理页面上传文件
const navigateToData = () => {
  router.push('/data')
}

// 格式化日期
const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (days === 0) {
    const hours = Math.floor(diff / (1000 * 60 * 60))
    if (hours === 0) {
      const minutes = Math.floor(diff / (1000 * 60))
      return minutes <= 1 ? '刚刚' : `${minutes} 分钟前`
    }
    return `${hours} 小时前`
  } else if (days === 1) {
    return '昨天'
  } else if (days < 7) {
    return `${days} 天前`
  } else {
    return date.toLocaleDateString('zh-CN')
  }
}

onMounted(() => {
  loadFiles()
})
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: var(--bg-primary);
}

.page-content {
  padding: 1.5rem;
  max-width: 1600px;
  margin: 0 auto;
  height: calc(100vh - 65px);
  display: flex;
  flex-direction: column;
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
  transition: all 0.2s;
  text-decoration: none;
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
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
}

.btn-secondary:hover {
  background: var(--bg-primary);
}

.visualization-container {
  display: grid;
  grid-template-columns: 1fr 280px;
  gap: 1rem;
  flex: 1;
  min-height: 0;
}

.viewport {
  background: var(--bg-secondary);
  border-radius: 1rem;
  overflow: hidden;
  position: relative;
}

.empty-viewport {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.viewport-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 3rem;
  text-align: center;
}

.viewport-placeholder svg {
  width: 4rem;
  height: 4rem;
  color: var(--text-muted);
  opacity: 0.5;
  margin-bottom: 1.5rem;
}

.viewport-placeholder h3 {
  margin: 0 0 0.5rem;
  font-size: 1.125rem;
  color: var(--text-primary);
}

.viewport-placeholder p {
  margin: 0 0 1.5rem;
  color: var(--text-muted);
  font-size: 0.875rem;
}

.control-panel {
  background: var(--bg-secondary);
  border-radius: 1rem;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  overflow-y: auto;
}

.panel-section {
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 1rem;
}

.panel-section:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.panel-title {
  margin: 0 0 1rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-primary);
}

.control-group {
  margin-bottom: 1rem;
}

.control-group:last-child {
  margin-bottom: 0;
}

.control-label {
  display: block;
  margin-bottom: 0.5rem;
  font-size: 0.8125rem;
  color: var(--text-secondary);
}

.color-options {
  display: flex;
  gap: 0.5rem;
}

.color-option {
  width: 1.5rem;
  height: 1.5rem;
  border-radius: 50%;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.2s;
}

.color-option.active {
  border-color: var(--text-primary);
}

.color-blue { background: #3b82f6; }
.color-green { background: #10b981; }
.color-orange { background: #f97316; }
.color-purple { background: #8b5cf6; }

.slider {
  width: 100%;
  accent-color: var(--color-primary);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8125rem;
  color: var(--text-secondary);
  cursor: pointer;
}

.checkbox-label input {
  accent-color: var(--color-primary);
}

.view-buttons {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.5rem;
}

.view-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
  padding: 0.75rem 0.5rem;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.view-btn:hover {
  background: var(--bg-primary);
  color: var(--text-primary);
}

.view-btn.active {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: white;
}

.view-btn svg {
  width: 1.125rem;
  height: 1.125rem;
}

.view-btn span {
  font-size: 0.75rem;
}

.track-list {
  max-height: 200px;
  overflow-y: auto;
}

.track-list-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem 1rem;
  text-align: center;
  color: var(--text-muted);
}

.track-list-empty svg {
  width: 2rem;
  height: 2rem;
  margin-bottom: 0.5rem;
  opacity: 0.5;
}

.track-list-empty p {
  margin: 0;
  font-size: 0.8125rem;
}

.track-list-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem 1rem;
  color: var(--text-muted);
}

.spinner {
  width: 2rem;
  height: 2rem;
  animation: spin 1s linear infinite;
  margin-bottom: 0.5rem;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.btn-link {
  margin-top: 0.5rem;
  padding: 0;
  background: transparent;
  border: none;
  color: var(--color-primary);
  font-size: 0.8125rem;
  cursor: pointer;
  text-decoration: underline;
}

.track-list-items {
  display: flex;
  flex-direction: column;
}

.track-list-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: background 0.2s;
}

.track-list-item:hover {
  background: var(--bg-tertiary);
}

.track-list-item.active {
  background: rgba(59, 130, 246, 0.1);
}

.track-item-icon {
  flex-shrink: 0;
  width: 1.5rem;
  height: 1.5rem;
  color: var(--text-muted);
}

.track-item-icon svg {
  width: 100%;
  height: 100%;
}

.track-item-info {
  flex: 1;
  min-width: 0;
}

.track-item-name {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.track-item-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.125rem;
}

.track-item-rows {
  font-size: 0.75rem;
  color: var(--color-primary);
}

.track-item-date {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.track-item-status {
  flex-shrink: 0;
  width: 1.25rem;
  height: 1.25rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.track-item-status svg {
  width: 0.75rem;
  height: 0.75rem;
}

.status-completed {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

/* Viewport content styles */
.viewport-content {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.viewport-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  background: var(--bg-tertiary);
  border-bottom: 1px solid var(--border-color);
}

.viewport-file-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.btn-close-viewport {
  width: 1.75rem;
  height: 1.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: 0.375rem;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s;
}

.btn-close-viewport:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.btn-close-viewport svg {
  width: 1rem;
  height: 1rem;
}

.viewport-canvas {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(180deg, var(--bg-secondary) 0%, var(--bg-tertiary) 100%);
}

.canvas-placeholder {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.canvas-hint {
  font-size: 0.875rem;
  color: var(--text-muted);
}

@media (max-width: 1024px) {
  .visualization-container {
    grid-template-columns: 1fr;
    grid-template-rows: 1fr auto;
  }

  .viewport {
    min-height: 400px;
  }

  .control-panel {
    max-height: 300px;
  }
}

@media (max-width: 768px) {
  .page-content {
    padding: 1rem;
  }

  .page-header {
    flex-direction: column;
    align-items: stretch;
  }

  .header-actions {
    flex-direction: column;
  }

  .header-actions .btn {
    width: 100%;
    justify-content: center;
  }
}
</style>
