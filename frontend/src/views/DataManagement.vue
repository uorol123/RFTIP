<template>
  <div class="page">
    <AppHeader />
    <div class="page-content">
      <div class="page-header">
        <div>
          <h1 class="page-title">数据管理</h1>
          <p class="page-subtitle">上传和管理您的雷达数据文件</p>
        </div>
        <button class="btn btn-primary" @click="openUploadModal">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          上传文件
        </button>
      </div>

      <!-- 筛选栏 -->
      <div class="filters-bar">
        <div class="filter-group">
          <div class="search-box">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              type="text"
              placeholder="搜索文件..."
              v-model="searchQuery"
              @input="handleSearch"
            />
          </div>
          <select class="filter-select" v-model="statusFilter" @change="loadFiles">
            <option value="">全部状态</option>
            <option value="pending">待处理</option>
            <option value="processing">处理中</option>
            <option value="completed">已完成</option>
            <option value="failed">失败</option>
          </select>
        </div>
        <div class="filter-group">
          <select class="filter-select" v-model="categoryFilter" @change="loadFiles">
            <option value="">全部分类</option>
            <option value="trajectory">轨迹数据</option>
            <option value="radar_station">雷达站配置</option>
          </select>
        </div>
      </div>

      <!-- 文件列表 -->
      <div class="files-container">
        <div v-if="loading && !files.length" class="loading-state">
          <svg class="spinner" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="3" stroke-dasharray="32" stroke-linecap="round" />
          </svg>
          <p>加载中...</p>
        </div>

        <div v-else-if="!files.length" class="files-table">
          <div class="table-body">
            <div class="table-row empty">
              <div class="empty-state">
                <div class="empty-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <div class="empty-title">暂无数据文件</div>
                <div class="empty-desc">点击"上传文件"开始使用</div>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="files-table">
          <div class="table-header">
            <div class="table-cell">文件名</div>
            <div class="table-cell">大小</div>
            <div class="table-cell">分类</div>
            <div class="table-cell">状态</div>
            <div class="table-cell">上传时间</div>
            <div class="table-cell">操作</div>
          </div>
          <div class="table-body">
            <div
              v-for="file in files"
              :key="file.id"
              class="table-row"
              :class="{ processing: file.status === 'processing' }"
            >
              <div class="table-cell file-name">
                <svg class="file-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span>{{ file.filename }}</span>
              </div>
              <div class="table-cell">{{ formatFileSize(file.file_size) }}</div>
              <div class="table-cell">
                <span class="category-badge" :class="file.category">
                  {{ file.category === 'trajectory' ? '轨迹数据' : '雷达站配置' }}
                </span>
              </div>
              <div class="table-cell">
                <span class="status-badge" :class="file.status">
                  {{ getStatusText(file.status) }}
                </span>
                <div v-if="file.status === 'processing' && fileProgress[file.id]" class="progress-info">
                  <div class="progress-text">{{ fileProgress[file.id]?.stage || '处理中' }} {{ Math.round(fileProgress[file.id]?.progress || 0) }}%</div>
                  <div class="progress-bar">
                    <div class="progress-fill" :style="{ width: (fileProgress[file.id]?.progress || 0) + '%' }"></div>
                  </div>
                  <div v-if="fileProgress[file.id]?.message" class="progress-message">{{ fileProgress[file.id].message }}</div>
                </div>
              </div>
              <div class="table-cell">{{ formatDate(file.uploaded_at) }}</div>
              <div class="table-cell actions">
                <button
                  class="action-btn"
                  @click="handleShare(file)"
                  :title="'分享文件'"
                  :disabled="file.status !== 'completed'"
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
                  </svg>
                </button>
                <button
                  class="action-btn danger"
                  :class="{ deleting: deletingIds.has(file.id) }"
                  :disabled="deletingIds.has(file.id)"
                  @click="handleDelete(file)"
                  :title="deletingIds.has(file.id) ? '删除中...' : '删除文件'"
                >
                  <svg v-if="!deletingIds.has(file.id)" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                  <svg v-else class="spinner-icon" viewBox="0 0 24 24">
                    <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="3" stroke-dasharray="32" stroke-linecap="round" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 上传弹窗 -->
      <Teleport to="body">
        <div v-if="showUploadModal" class="modal-overlay" @click="closeUploadModal">
          <div class="modal-content" @click.stop>
            <div class="modal-header">
              <h2 class="modal-title">上传数据文件</h2>
              <button class="modal-close" @click="closeUploadModal">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div class="modal-body">
              <div class="upload-area" @click="handleFileSelect" @drop.prevent="handleDrop" @dragover.prevent>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <p>拖拽文件到此处或点击选择</p>
                <p class="upload-hint">支持 CSV、Excel 格式的雷达数据文件</p>
                <input
                  ref="fileInputRef"
                  type="file"
                  accept=".csv,.xlsx,.xls"
                  multiple
                  @change="handleFileChange"
                  style="display: none"
                />
              </div>

              <div v-if="selectedFiles.length" class="selected-files">
                <div v-for="(file, index) in selectedFiles" :key="index" class="selected-file-item">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <span class="file-name-text">{{ file.name }}</span>
                  <span class="file-size">{{ formatFileSize(file.size) }}</span>
                  <button class="remove-file" @click.stop="removeFile(index)">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">文件分类</label>
                <select v-model="uploadCategory" class="form-select">
                  <option value="trajectory">轨迹数据</option>
                  <option value="radar_station">雷达站配置</option>
                </select>
              </div>
            </div>
            <div class="modal-footer">
              <button class="btn btn-secondary" @click="closeUploadModal">取消</button>
              <button
                class="btn btn-primary"
                @click="handleUpload"
                :disabled="!selectedFiles.length || uploading"
              >
                <svg v-if="uploading" class="spinner" viewBox="0 0 24 24">
                  <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="3" stroke-dasharray="32" stroke-linecap="round" />
                </svg>
                {{ uploading ? '上传中...' : selectedFiles.length > 1 ? `上传 ${selectedFiles.length} 个文件` : '上传文件' }}
              </button>
            </div>
          </div>
        </div>
      </Teleport>

      <!-- 分享弹窗 -->
      <Teleport to="body">
        <div v-if="showShareModal" class="modal-overlay" @click="showShareModal = false">
          <div class="modal-content share-modal" @click.stop>
            <div class="modal-header">
              <h2 class="modal-title">分享文件</h2>
              <button class="modal-close" @click="showShareModal = false">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div class="modal-body">
              <div v-if="shareLoading" class="share-loading">
                <svg class="spinner" viewBox="0 0 24 24">
                  <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="3" stroke-dasharray="32" stroke-linecap="round" />
                </svg>
                <p>生成分享链接中...</p>
              </div>
              <div v-else-if="shareInfo" class="share-info">
                <div class="qr-code" v-if="shareInfo.qr_code">
                  <img :src="shareInfo.qr_code" alt="QR Code" />
                </div>
                <div class="share-link-box">
                  <label class="form-label">分享链接</label>
                  <div class="share-link-input">
                    <input :value="shareInfo.share_url" readonly />
                    <button class="copy-btn" @click="copyShareLink">复制</button>
                  </div>
                </div>
                <div class="share-expire">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  过期时间: {{ formatDate(shareInfo.expire_at) }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </Teleport>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, onBeforeUnmount, computed } from 'vue'
import { storeToRefs } from 'pinia'
import AppHeader from '@/components/AppHeader.vue'
import { useAuthStore } from '@/stores/auth'
import { useAppStore } from '@/stores/app'
import { filesApi, createFileProgressWebSocket } from '@/api/files'
import type { FileItem, FileStatusResponse, FileCategory } from '@/api/types'

const authStore = useAuthStore()
const appStore = useAppStore()
const { token } = storeToRefs(authStore)

// 状态
const loading = ref(false)
const files = ref<FileItem[]>([])
const fileProgress = ref<Record<number, FileStatusResponse>>({})
const deletingIds = ref<Set<number>>(new Set())
const searchQuery = ref('')
const statusFilter = ref('')
const categoryFilter = ref('')
const isPageActive = ref(true)  // 跟踪页面是否活跃

// 上传相关
const showUploadModal = ref(false)
const uploading = ref(false)
const selectedFiles = ref<File[]>([])
const uploadCategory = ref<FileCategory>('trajectory')
const fileInputRef = ref<HTMLInputElement>()

// 分享相关
const showShareModal = ref(false)
const shareLoading = ref(false)
const shareInfo = ref<{ share_url: string; qr_code: string; expire_at: string } | null>(null)
const currentShareFile = ref<FileItem | null>(null)

// WebSocket 连接池
const wsConnections = ref<Map<number, WebSocket>>(new Map())

// 加载文件列表
const loadFiles = async () => {
  loading.value = true
  try {
    const response = await filesApi.getFileList({
      skip: 0,
      limit: 100,
      status: statusFilter.value as any || undefined,
      category: categoryFilter.value as FileCategory || undefined,
      search: searchQuery.value || undefined,
    })
    files.value = response.files

    // 为处理中的文件建立 WebSocket 连接
    response.files.forEach((file) => {
      if (file.status === 'processing') {
        connectFileWebSocket(file.id)
      }
    })
  } catch (error: any) {
    appStore.error(error.message || '加载文件列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索处理
let searchTimeout: ReturnType<typeof setTimeout>
const handleSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadFiles()
  }, 500)
}

// 连接文件处理 WebSocket
const connectFileWebSocket = (fileId: number) => {
  // 如果已存在连接，先关闭
  if (wsConnections.value.has(fileId)) {
    return
  }

  const ws = createFileProgressWebSocket(fileId, token.value || '', {
    onProgress: (data) => {
      fileProgress.value[fileId] = data
    },
    onCompleted: (data) => {
      fileProgress.value[fileId] = data
      // 更新文件状态
      const file = files.value.find((f) => f.id === fileId)
      if (file) {
        file.status = 'completed'
      }
      // 关闭连接
      ws.close()
      wsConnections.value.delete(fileId)
    },
    onError: (error) => {
      // 只在页面活跃时显示错误
      if (isPageActive.value) {
        appStore.error(error, 4000)
      }
      const file = files.value.find((f) => f.id === fileId)
      if (file) {
        file.status = 'failed'
      }
      ws.close()
      wsConnections.value.delete(fileId)
    },
    onClose: () => {
      wsConnections.value.delete(fileId)
    },
  })

  wsConnections.value.set(fileId, ws)
}

// 打开上传弹窗
const openUploadModal = () => {
  showUploadModal.value = true
  selectedFiles.value = []
  uploadCategory.value = 'trajectory'
}

// 关闭上传弹窗
const closeUploadModal = () => {
  showUploadModal.value = false
  selectedFiles.value = []
  if (fileInputRef.value) {
    fileInputRef.value.value = ''
  }
}

// 文件选择
const handleFileSelect = () => {
  fileInputRef.value?.click()
}

const handleFileChange = (e: Event) => {
  const target = e.target as HTMLInputElement
  if (target.files) {
    selectedFiles.value = Array.from(target.files)
  }
}

// 拖拽上传
const handleDrop = (e: DragEvent) => {
  if (e.dataTransfer?.files) {
    selectedFiles.value = Array.from(e.dataTransfer.files)
  }
}

// 移除选中的文件
const removeFile = (index: number) => {
  selectedFiles.value.splice(index, 1)
}

// 上传文件
const handleUpload = async () => {
  if (!selectedFiles.value.length) return

  uploading.value = true
  try {
    if (selectedFiles.value.length === 1) {
      // 单文件上传
      const response = await filesApi.uploadFile(selectedFiles.value[0], uploadCategory.value)
      appStore.success(response.message || '文件上传成功')

      // 立即连接 WebSocket 监听处理进度
      connectFileWebSocket(response.file_id)
    } else {
      // 批量上传
      const response = await filesApi.uploadFilesBatch(selectedFiles.value, uploadCategory.value)
      appStore.success(response.message || '批量上传任务已创建')

      // 为所有文件连接 WebSocket
      response.files.forEach((file) => {
        connectFileWebSocket(file.file_id)
      })
    }

    closeUploadModal()
    // 延迟刷新列表，给文件处理一点时间
    setTimeout(() => loadFiles(), 500)
  } catch (error: any) {
    appStore.error(error.message || '文件上传失败')
  } finally {
    uploading.value = false
  }
}

// 分享文件
const handleShare = async (file: FileItem) => {
  currentShareFile.value = file
  shareInfo.value = null
  shareLoading.value = true
  showShareModal.value = true

  try {
    const response = await filesApi.shareFile(file.id, {
      expire_hours: 24,
    })
    shareInfo.value = response
  } catch (error: any) {
    appStore.error(error.message || '生成分享链接失败')
    showShareModal.value = false
  } finally {
    shareLoading.value = false
  }
}

// 复制分享链接
const copyShareLink = async () => {
  if (shareInfo.value?.share_url) {
    try {
      await navigator.clipboard.writeText(shareInfo.value.share_url)
      appStore.success('分享链接已复制')
    } catch {
      appStore.error('复制失败')
    }
  }
}

// 删除文件
const handleDelete = async (file: FileItem) => {
  if (!confirm(`确定要删除文件 "${file.filename}" 吗？`)) return

  // 添加删除状态
  deletingIds.value.add(file.id)

  try {
    await filesApi.deleteFile(file.id)

    // 立即从列表中移除文件（乐观更新）
    const index = files.value.findIndex(f => f.id === file.id)
    if (index > -1) {
      files.value.splice(index, 1)
    }

    appStore.success('文件删除成功', 5000)
  } catch (error: any) {
    // 删除失败，移除删除状态
    deletingIds.value.delete(file.id)
    appStore.error(error.message || '文件删除失败', 5000)
  } finally {
    // 无论成功失败都移除删除状态
    deletingIds.value.delete(file.id)
  }
}

// 格式化文件大小
const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
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

// 获取状态文本
const getStatusText = (status: string): string => {
  const statusMap: Record<string, string> = {
    pending: '待处理',
    processing: '处理中',
    completed: '已完成',
    failed: '失败',
  }
  return statusMap[status] || status
}

// 定时刷新间隔
let refreshInterval: ReturnType<typeof setInterval> | null = null

// 组件挂载时加载文件
onMounted(() => {
  loadFiles()

  // 定时刷新处理中的文件状态
  refreshInterval = setInterval(() => {
    const hasProcessing = files.value.some((f) => f.status === 'processing')
    if (hasProcessing) {
      loadFiles()
    }
  }, 5000)
})

// 组件卸载前清理
onBeforeUnmount(() => {
  // 标记页面即将卸载
  isPageActive.value = false

  // 关闭所有 WebSocket 连接
  wsConnections.value.forEach((ws) => {
    try {
      ws.close()
    } catch (e) {
      // 忽略关闭时的错误
    }
  })
  wsConnections.value.clear()
})

// 组件卸载时清理定时器
onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: var(--bg-primary);
}

.page-content {
  padding: 1.5rem;
  max-width: 1400px;
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
}

.btn svg {
  width: 1rem;
  height: 1rem;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--color-primary);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn-secondary {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.btn-secondary:hover:not(:disabled) {
  background: var(--bg-primary);
}

.filters-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  gap: 0.75rem;
  flex: 1;
  min-width: 0;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
  min-width: 200px;
  max-width: 400px;
  padding: 0.625rem 1rem;
  border-radius: 0.5rem;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
}

.search-box svg {
  flex-shrink: 0;
  width: 1rem;
  height: 1rem;
  color: var(--text-muted);
}

.search-box input {
  flex: 1;
  border: none;
  background: transparent;
  color: var(--text-primary);
  font-size: 0.875rem;
  outline: none;
}

.filter-select {
  padding: 0.625rem 2rem 0.625rem 1rem;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 0.875rem;
  cursor: pointer;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  color: var(--text-muted);
}

.spinner {
  width: 2rem;
  height: 2rem;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.files-container {
  background: var(--bg-secondary);
  border-radius: 1rem;
  overflow: hidden;
}

.files-table {
  width: 100%;
}

.table-header {
  display: grid;
  grid-template-columns: 2fr 100px 100px 140px 180px 120px;
  gap: 1rem;
  padding: 1rem 1.5rem;
  background: var(--bg-tertiary);
  border-bottom: 1px solid var(--border-color);
}

.table-cell {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
}

.table-body {
  min-height: 300px;
}

.table-row {
  display: grid;
  grid-template-columns: 2fr 100px 100px 140px 180px 120px;
  gap: 1rem;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--border-color);
  align-items: center;
}

.table-row:hover {
  background: var(--bg-tertiary);
}

.table-row.empty {
  display: block;
}

.table-row.processing {
  background: rgba(59, 130, 246, 0.05);
}

.file-name {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  overflow: hidden;
}

.file-icon {
  flex-shrink: 0;
  width: 1rem;
  height: 1rem;
  color: var(--text-muted);
}

.file-name span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.category-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.category-badge.trajectory {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.category-badge.radar_station {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.status-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-badge.pending {
  background: rgba(148, 163, 184, 0.1);
  color: var(--text-muted);
}

.status-badge.processing {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.status-badge.completed {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.status-badge.failed {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.progress-info {
  width: 100%;
  margin-top: 0.25rem;
}

.progress-text {
  font-size: 0.75rem;
  color: var(--text-secondary);
  margin-bottom: 0.25rem;
  display: flex;
  justify-content: space-between;
}

.progress-bar {
  width: 100%;
  height: 3px;
  background: var(--bg-tertiary);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--color-primary);
  transition: width 0.3s ease;
}

.progress-message {
  font-size: 0.7rem;
  color: var(--text-muted);
  margin-top: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  width: 2rem;
  height: 2rem;
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

.action-btn:hover:not(:disabled) {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.action-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.action-btn.danger:hover:not(:disabled) {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.action-btn svg {
  width: 1rem;
  height: 1rem;
}

.action-btn.deleting {
  cursor: wait;
  opacity: 0.7;
}

.spinner-icon {
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

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.empty-icon {
  width: 4rem;
  height: 4rem;
  margin-bottom: 1rem;
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
  color: var(--text-muted);
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  width: 100%;
  max-width: 500px;
  border-radius: 1rem;
  background: var(--bg-elevated);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid var(--border-color);
}

.modal-title {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
}

.modal-close {
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: 0.5rem;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s;
}

.modal-close:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.modal-close svg {
  width: 1.25rem;
  height: 1.25rem;
}

.modal-body {
  padding: 1.5rem;
}

.upload-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 2rem;
  border: 2px dashed var(--border-color);
  border-radius: 0.75rem;
  background: var(--bg-tertiary);
  cursor: pointer;
  transition: all 0.2s;
}

.upload-area:hover {
  border-color: var(--color-primary);
  background: rgba(59, 130, 246, 0.05);
}

.upload-area svg {
  width: 3rem;
  height: 3rem;
  color: var(--text-muted);
  margin-bottom: 1rem;
}

.upload-area p {
  margin: 0.5rem 0;
  color: var(--text-primary);
  font-size: 0.9375rem;
}

.upload-hint {
  color: var(--text-muted);
  font-size: 0.8125rem;
}

.selected-files {
  margin-top: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.selected-file-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background: var(--bg-secondary);
  border-radius: 0.5rem;
}

.selected-file-item svg {
  width: 1rem;
  height: 1rem;
  color: var(--text-muted);
  flex-shrink: 0;
}

.file-name-text {
  flex: 1;
  font-size: 0.875rem;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-size {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.remove-file {
  width: 1.5rem;
  height: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: 0.25rem;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s;
}

.remove-file:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.remove-file svg {
  width: 0.875rem;
  height: 0.875rem;
}

.form-group {
  margin-top: 1.5rem;
}

.form-label {
  display: block;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.form-select {
  width: 100%;
  padding: 0.625rem 1rem;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 0.875rem;
  cursor: pointer;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--border-color);
}

/* Share Modal */
.share-modal {
  max-width: 400px;
}

.share-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem;
  color: var(--text-muted);
}

.share-loading .spinner {
  width: 2.5rem;
  height: 2.5rem;
}

.share-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
}

.qr-code {
  padding: 1rem;
  background: white;
  border-radius: 0.5rem;
}

.qr-code img {
  width: 150px;
  height: 150px;
  display: block;
}

.share-link-box {
  width: 100%;
}

.share-link-input {
  display: flex;
  gap: 0.5rem;
}

.share-link-input input {
  flex: 1;
  padding: 0.625rem 1rem;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 0.875rem;
}

.copy-btn {
  padding: 0.625rem 1rem;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.copy-btn:hover {
  background: #2563eb;
}

.share-expire {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: var(--bg-tertiary);
  border-radius: 0.5rem;
  color: var(--text-secondary);
  font-size: 0.8125rem;
}

.share-expire svg {
  width: 1rem;
  height: 1rem;
}

@media (max-width: 768px) {
  .page-content {
    padding: 1rem;
  }

  .table-header,
  .table-row {
    grid-template-columns: 1fr 80px 80px 80px;
  }

  .table-cell:nth-child(5),
  .table-cell:nth-child(6) {
    display: none;
  }

  .filters-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .search-box {
    max-width: none;
  }
}
</style>
