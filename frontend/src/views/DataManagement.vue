<template>
  <div class="data-management">
    <div class="page-header">
      <div>
        <h1 class="page-title">Data Management</h1>
        <p class="page-subtitle">Upload and manage your radar data files</p>
      </div>
      <button class="btn btn-primary" @click="showUploadModal = true">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Upload File
      </button>
    </div>

    <!-- Upload Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showUploadModal" class="modal-overlay" @click="closeUploadModal">
          <div class="modal-content" @click.stop>
            <div class="modal-header">
              <h2 class="modal-title">Upload Data File</h2>
              <button class="modal-close" @click="closeUploadModal">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div class="modal-body">
              <FileUploader
                ref="uploaderRef"
                v-model="filesToUpload"
                @upload="handleUpload"
              />
              <div v-if="uploadProgress.show" class="upload-progress">
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: uploadProgress.percent + '%' }"></div>
                </div>
                <div class="progress-text">{{ uploadProgress.text }}</div>
              </div>
            </div>
            <div class="modal-footer">
              <button class="btn btn-secondary" @click="closeUploadModal">Cancel</button>
              <button
                class="btn btn-primary"
                :disabled="filesToUpload.length === 0 || uploadProgress.uploading"
                @click="startUpload"
              >
                {{ uploadProgress.uploading ? 'Uploading...' : 'Upload' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Filters -->
    <div class="filters-bar">
      <div class="filter-group">
        <div class="search-box">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search files..."
            @input="handleSearch"
          />
        </div>
        <select v-model="statusFilter" class="filter-select" @change="loadFiles">
          <option value="">All Status</option>
          <option value="pending">Pending</option>
          <option value="processing">Processing</option>
          <option value="completed">Completed</option>
          <option value="failed">Failed</option>
        </select>
      </div>
      <div v-if="selectedFiles.length > 0" class="bulk-actions">
        <span class="selected-count">{{ selectedFiles.length }} selected</span>
        <button class="btn btn-danger btn-sm" @click="confirmDeleteSelected">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
            />
          </svg>
          Delete
        </button>
      </div>
    </div>

    <!-- Files Table -->
    <DataTable
      :columns="columns"
      :data="files"
      :loading="loading"
      :selectable="true"
      :clickable="true"
      :current-page="pagination.page"
      :page-size="pagination.pageSize"
      :total-items="pagination.total"
      title="Files"
      @row-click="viewFile"
      @selection-change="handleSelectionChange"
      @page-change="handlePageChange"
    >
      <template #cell-filename="{ row, value }">
        <div class="filename-cell">
          <div class="file-icon-small">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
          </div>
          <span class="filename-text">{{ value }}</span>
        </div>
      </template>
      <template #cell-status="{ value }">
        <span :class="['status-badge', `status-${value}`]">
          {{ value }}
        </span>
      </template>
      <template #cell-file_size="{ value }">
        {{ formatFileSize(value) }}
      </template>
      <template #cell-upload_time="{ value }">
        {{ formatDate(value) }}
      </template>
      <template #cell-is_public="{ row }">
        <button
          class="visibility-toggle"
          @click.stop="toggleVisibility(row)"
          :title="row.is_public ? 'Public' : 'Private'"
        >
          <svg v-if="row.is_public" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
            />
          </svg>
        </button>
      </template>
      <template #row-actions="{ row }">
        <div class="row-actions">
          <button
            v-if="row.status === 'completed'"
            class="action-btn"
            @click.stop="processFile(row)"
            title="Process file"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
              />
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </button>
          <button
            class="action-btn action-btn-danger"
            @click.stop="confirmDelete(row)"
            title="Delete file"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
              />
            </svg>
          </button>
        </div>
      </template>
    </DataTable>

    <!-- Delete Confirmation -->
    <ConfirmDialog
      v-model:show="showDeleteDialog"
      title="Delete File"
      :message="`Are you sure you want to delete '${fileToDelete?.original_filename}'? This action cannot be undone.`"
      type="danger"
      confirm-text="Delete"
      @confirm="handleDelete"
    />

    <!-- Bulk Delete Confirmation -->
    <ConfirmDialog
      v-model:show="showBulkDeleteDialog"
      title="Delete Selected Files"
      :message="`Are you sure you want to delete ${selectedFiles.length} file(s)? This action cannot be undone.`"
      type="danger"
      confirm-text="Delete"
      @confirm="handleBulkDelete"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { filesApi } from '@/api'
import type { DataFile } from '@/api/types'
import DataTable from '@/components/DataTable.vue'
import FileUploader from '@/components/FileUploader.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'

const router = useRouter()
const appStore = useAppStore()

const loading = ref(false)
const files = ref<DataFile[]>([])
const selectedFiles = ref<DataFile[]>([])
const filesToUpload = ref<File[]>([])

const showUploadModal = ref(false)
const showDeleteDialog = ref(false)
const showBulkDeleteDialog = ref(false)
const fileToDelete = ref<DataFile | null>(null)

const uploaderRef = ref<InstanceType<typeof FileUploader> | null>(null)

const searchQuery = ref('')
const statusFilter = ref('')

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0,
})

const uploadProgress = reactive({
  show: false,
  uploading: false,
  percent: 0,
  text: '',
})

const columns = [
  { key: 'filename', label: 'File Name', sortable: true },
  { key: 'file_size', label: 'Size', sortable: true, width: '100px' },
  { key: 'status', label: 'Status', sortable: true, width: '120px' },
  { key: 'upload_time', label: 'Uploaded', sortable: true, width: '180px' },
  { key: 'is_public', label: 'Visibility', width: '80px' },
]

const loadFiles = async () => {
  loading.value = true
  try {
    const response = await filesApi.list({
      page: pagination.page,
      page_size: pagination.pageSize,
      status: statusFilter.value || undefined,
      search: searchQuery.value || undefined,
    })
    files.value = response.items
    pagination.total = response.total
  } catch (error: any) {
    appStore.error(error.message || 'Failed to load files')
  } finally {
    loading.value = false
  }
}

const handleSearch = debounce(() => {
  pagination.page = 1
  loadFiles()
}, 500)

function debounce(fn: Function, delay: number) {
  let timeoutId: ReturnType<typeof setTimeout>
  return (...args: any[]) => {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => fn(...args), delay)
  }
}

const handleSelectionChange = (selection: DataFile[]) => {
  selectedFiles.value = selection
}

const handlePageChange = (page: number) => {
  pagination.page = page
  loadFiles()
}

const viewFile = (file: DataFile) => {
  router.push(`/data/${file.id}`)
}

const closeUploadModal = () => {
  showUploadModal.value = false
  filesToUpload.value = []
  uploadProgress.show = false
  uploaderRef.value?.clear()
}

const startUpload = async () => {
  if (filesToUpload.value.length === 0) return

  uploadProgress.show = true
  uploadProgress.uploading = true
  uploadProgress.percent = 0

  try {
    for (let i = 0; i < filesToUpload.value.length; i++) {
      const file = filesToUpload.value[i]
      uploadProgress.text = `Uploading ${file.name}...`

      await filesApi.upload(file, false)

      uploadProgress.percent = Math.round(((i + 1) / filesToUpload.value.length) * 100)
    }

    uploadProgress.text = 'Upload complete!'
    appStore.success('Files uploaded successfully')

    setTimeout(() => {
      closeUploadModal()
      loadFiles()
    }, 1000)
  } catch (error: any) {
    uploadProgress.text = 'Upload failed'
    appStore.error(error.message || 'Failed to upload files')
  } finally {
    uploadProgress.uploading = false
  }
}

const handleUpload = (files: File[], isPublic: boolean) => {
  // Upload logic handled in startUpload
}

const toggleVisibility = async (file: DataFile) => {
  try {
    await filesApi.updateVisibility(file.id, !file.is_public)
    appStore.success(file.is_public ? 'File set to private' : 'File set to public')
    loadFiles()
  } catch (error: any) {
    appStore.error(error.message || 'Failed to update visibility')
  }
}

const processFile = (file: DataFile) => {
  router.push(`/tracks?file=${file.id}`)
}

const confirmDelete = (file: DataFile) => {
  fileToDelete.value = file
  showDeleteDialog.value = true
}

const confirmDeleteSelected = () => {
  showBulkDeleteDialog.value = true
}

const handleDelete = async () => {
  if (!fileToDelete.value) return

  try {
    await filesApi.delete(fileToDelete.value.id)
    appStore.success('File deleted successfully')
    showDeleteDialog.value = false
    loadFiles()
  } catch (error: any) {
    appStore.error(error.message || 'Failed to delete file')
  }
}

const handleBulkDelete = async () => {
  try {
    await Promise.all(
      selectedFiles.value.map(file => filesApi.delete(file.id))
    )
    appStore.success(`${selectedFiles.value.length} file(s) deleted`)
    showBulkDeleteDialog.value = false
    selectedFiles.value = []
    loadFiles()
  } catch (error: any) {
    appStore.error(error.message || 'Failed to delete files')
  }
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
  })
}

onMounted(() => {
  loadFiles()
})
</script>

<style scoped>
.data-management {
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

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.btn-secondary:hover {
  background: var(--bg-primary);
}

.btn-danger {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.btn-danger:hover {
  background: rgba(239, 68, 68, 0.2);
}

.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.8125rem;
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
  backdrop-filter: blur(4px);
  z-index: 9999;
  padding: 1rem;
}

.modal-content {
  width: 100%;
  max-width: 550px;
  border-radius: 1rem;
  background: var(--bg-secondary);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid var(--border-color, rgba(255, 255, 255, 0.1));
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
  padding: 0;
  border: none;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  border-radius: 0.375rem;
  transition: all 0.2s;
}

.modal-close:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.modal-close svg {
  width: 1rem;
  height: 1rem;
}

.modal-body {
  padding: 1.5rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--border-color, rgba(255, 255, 255, 0.1));
}

.upload-progress {
  margin-top: 1rem;
}

.progress-bar {
  height: 0.5rem;
  background: var(--bg-tertiary);
  border-radius: 0.25rem;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--color-primary);
  transition: width 0.3s ease;
}

.progress-text {
  margin-top: 0.5rem;
  color: var(--text-secondary);
  font-size: 0.875rem;
  text-align: center;
}

/* Filters */
.filters-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
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
  border: 1px solid var(--border-color, rgba(255, 255, 255, 0.1));
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

.search-box input::placeholder {
  color: var(--text-muted);
}

.filter-select {
  padding: 0.625rem 2rem 0.625rem 1rem;
  border: 1px solid var(--border-color, rgba(255, 255, 255, 0.1));
  border-radius: 0.5rem;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 0.875rem;
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%2394a3b8'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M19 9l-7 7-7-7'%3E%3C/path%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.5rem center;
  background-size: 1rem;
}

.bulk-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.selected-count {
  color: var(--text-secondary);
  font-size: 0.875rem;
}

/* Table cells */
.filename-cell {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.file-icon-small {
  flex-shrink: 0;
  width: 1.5rem;
  height: 1.5rem;
  color: var(--color-primary);
}

.file-icon-small svg {
  width: 100%;
  height: 100%;
}

.filename-text {
  color: var(--text-primary);
  font-size: 0.875rem;
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.625rem;
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

.visibility-toggle {
  padding: 0.375rem;
  border: none;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  border-radius: 0.25rem;
  transition: all 0.2s;
}

.visibility-toggle:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.visibility-toggle svg {
  width: 1.125rem;
  height: 1.125rem;
}

.row-actions {
  display: flex;
  gap: 0.375rem;
}

.action-btn {
  padding: 0.375rem;
  border: none;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  border-radius: 0.25rem;
  transition: all 0.2s;
}

.action-btn:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.action-btn-danger:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.action-btn svg {
  width: 1rem;
  height: 1rem;
}

/* Modal animations */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-active .modal-content,
.modal-leave-active .modal-content {
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal-content,
.modal-leave-to .modal-content {
  transform: scale(0.95);
  opacity: 0;
}

@media (max-width: 768px) {
  .data-management {
    padding: 1rem;
  }

  .filters-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .search-box {
    max-width: none;
  }

  .bulk-actions {
    justify-content: space-between;
  }
}
</style>
