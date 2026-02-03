<template>
  <div class="file-details">
    <div class="page-header">
      <div class="header-left">
        <button class="back-btn" @click="router.back()">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <div>
          <h1 class="page-title">File Details</h1>
          <p class="page-subtitle">{{ file?.original_filename || 'Loading...' }}</p>
        </div>
      </div>
      <div class="header-actions">
        <button
          v-if="file?.status === 'completed'"
          class="btn btn-primary"
          @click="processFile"
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
          Process Tracks
        </button>
        <button class="btn btn-danger" @click="confirmDelete">
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

    <div v-if="loading" class="loading-state">
      <Loading :fullscreen="false" message="Loading file details..." />
    </div>

    <div v-else-if="file" class="details-content">
      <div class="details-grid">
        <!-- File Info Card -->
        <div class="info-card">
          <div class="card-header">
            <h2 class="card-title">File Information</h2>
            <span :class="['status-badge', `status-${file.status}`]">
              {{ file.status }}
            </span>
          </div>
          <div class="card-body">
            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">File Name</span>
                <span class="info-value">{{ file.original_filename }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">File Size</span>
                <span class="info-value">{{ formatFileSize(file.file_size) }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">File Type</span>
                <span class="info-value">{{ file.file_type }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Visibility</span>
                <span class="info-value">
                  {{ file.is_public ? 'Public' : 'Private' }}
                </span>
              </div>
              <div class="info-item">
                <span class="info-label">Uploaded</span>
                <span class="info-value">{{ formatDateTime(file.upload_time) }}</span>
              </div>
              <div v-if="file.processed_time" class="info-item">
                <span class="info-label">Processed</span>
                <span class="info-value">{{ formatDateTime(file.processed_time) }}</span>
              </div>
              <div v-if="file.record_count" class="info-item">
                <span class="info-label">Records</span>
                <span class="info-value">{{ file.record_count?.toLocaleString() }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Track Summary Card -->
        <div v-if="trackSummary" class="info-card">
          <div class="card-header">
            <h2 class="card-title">Track Summary</h2>
          </div>
          <div class="card-body">
            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">Total Tracks</span>
                <span class="info-value">{{ trackSummary.total_tracks }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Total Points</span>
                <span class="info-value">{{ trackSummary.total_points?.toLocaleString() }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Corrected Points</span>
                <span class="info-value">{{ trackSummary.corrected_points?.toLocaleString() }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Time Range</span>
                <span class="info-value">
                  {{ formatDate(trackSummary.time_range.start) }} - {{ formatDate(trackSummary.time_range.end) }}
                </span>
              </div>
              <div class="info-item">
                <span class="info-label">Min Altitude</span>
                <span class="info-value">{{ trackSummary.bbox.min_altitude }}m</span>
              </div>
              <div class="info-item">
                <span class="info-label">Max Altitude</span>
                <span class="info-value">{{ trackSummary.bbox.max_altitude }}m</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Tracks List -->
      <div v-if="tracks.length > 0" class="tracks-section">
        <div class="section-header">
          <h2 class="section-title">Tracks ({{ tracks.length }})</h2>
          <router-link to="/tracks" class="btn btn-secondary btn-sm">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"
              />
            </svg>
            Visualize
          </router-link>
        </div>
        <div class="tracks-grid">
          <div
            v-for="track in tracks"
            :key="track.track_id"
            class="track-card"
            @click="viewTrack(track)"
          >
            <div class="track-header">
              <span class="track-id">{{ track.track_id }}</span>
              <span class="track-points">{{ track.point_count }} points</span>
            </div>
            <div class="track-meta">
              <span>{{ formatTime(track.start_time) }} - {{ formatTime(track.end_time) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation -->
    <ConfirmDialog
      v-model:show="showDeleteDialog"
      title="Delete File"
      :message="`Are you sure you want to delete '${file?.original_filename}'? This action cannot be undone.`"
      type="danger"
      confirm-text="Delete"
      @confirm="handleDelete"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { filesApi, tracksApi } from '@/api'
import type { DataFile, Track, TrackSummary } from '@/api/types'
import Loading from '@/components/Loading.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'

const router = useRouter()
const route = useRoute()
const appStore = useAppStore()

const loading = ref(true)
const file = ref<DataFile | null>(null)
const tracks = ref<Track[]>([])
const trackSummary = ref<TrackSummary | null>(null)
const showDeleteDialog = ref(false)

const loadFileDetails = async () => {
  const fileId = Number(route.params.id)
  if (!fileId) {
    router.push('/data')
    return
  }

  loading.value = true
  try {
    const [fileData, summaryData, tracksData] = await Promise.all([
      filesApi.get(fileId),
      tracksApi.getSummary(fileId).catch(() => null),
      tracksApi.getRaw({ file_id: fileId, limit: 20 }).catch(() => []),
    ])

    file.value = fileData
    trackSummary.value = summaryData
    tracks.value = tracksData
  } catch (error: any) {
    appStore.error(error.message || 'Failed to load file details')
    router.push('/data')
  } finally {
    loading.value = false
  }
}

const processFile = () => {
  if (!file.value) return
  router.push(`/tracks?file=${file.value.id}`)
}

const confirmDelete = () => {
  showDeleteDialog.value = true
}

const handleDelete = async () => {
  if (!file.value) return

  try {
    await filesApi.delete(file.value.id)
    appStore.success('File deleted successfully')
    router.push('/data')
  } catch (error: any) {
    appStore.error(error.message || 'Failed to delete file')
  }
}

const viewTrack = (track: Track) => {
  router.push(`/tracks/${track.track_id}`)
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

const formatDateTime = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleString()
}

const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleDateString()
}

const formatTime = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

onMounted(() => {
  loadFileDetails()
})
</script>

<style scoped>
.file-details {
  padding: 1.5rem;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.back-btn {
  width: 2.5rem;
  height: 2.5rem;
  padding: 0;
  border: none;
  border-radius: 0.5rem;
  background: var(--bg-tertiary);
  color: var(--text-primary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.back-btn:hover {
  background: var(--bg-primary);
}

.back-btn svg {
  width: 1.25rem;
  height: 1.25rem;
}

.page-title {
  margin: 0 0 0.25rem;
  font-size: 1.5rem;
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

.loading-state {
  display: flex;
  justify-content: center;
  padding: 4rem 0;
}

.details-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.info-card {
  border-radius: 1rem;
  background: var(--bg-secondary);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--border-color, rgba(255, 255, 255, 0.1));
}

.card-title {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.status-badge {
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

.card-body {
  padding: 1.5rem;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.info-label {
  font-size: 0.8125rem;
  color: var(--text-muted);
}

.info-value {
  font-size: 0.9375rem;
  font-weight: 500;
  color: var(--text-primary);
}

.tracks-section {
  border-radius: 1rem;
  background: var(--bg-secondary);
  padding: 1.5rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.section-title {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
}

.tracks-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.track-card {
  padding: 1rem;
  border-radius: 0.5rem;
  background: var(--bg-tertiary);
  cursor: pointer;
  transition: all 0.2s;
}

.track-card:hover {
  background: var(--bg-primary);
  transform: translateY(-2px);
}

.track-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.track-id {
  font-weight: 600;
  color: var(--text-primary);
}

.track-points {
  font-size: 0.8125rem;
  color: var(--text-muted);
}

.track-meta {
  font-size: 0.8125rem;
  color: var(--text-secondary);
}

@media (max-width: 768px) {
  .file-details {
    padding: 1rem;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-actions {
    width: 100%;
  }

  .header-actions .btn {
    flex: 1;
    justify-content: center;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }

  .tracks-grid {
    grid-template-columns: 1fr;
  }
}
</style>
