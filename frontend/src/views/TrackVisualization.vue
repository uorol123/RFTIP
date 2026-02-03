<template>
  <div class="track-visualization">
    <div class="page-header">
      <div>
        <h1 class="page-title">Track Visualization</h1>
        <p class="page-subtitle">Visualize radar trajectory data in 3D</p>
      </div>
      <div class="header-actions">
        <button class="btn btn-secondary" @click="showSettings = !showSettings">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
            />
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
            />
          </svg>
          Settings
        </button>
        <button class="btn btn-primary" @click="processTracks" :disabled="!selectedFileId || processing">
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
          {{ processing ? 'Processing...' : 'Process' }}
        </button>
      </div>
    </div>

    <div class="visualization-layout">
      <!-- Sidebar -->
      <div class="sidebar" :class="{ 'sidebar-collapsed': !showSettings }">
        <div class="sidebar-header">
          <h2 class="sidebar-title">Configuration</h2>
        </div>

        <div class="sidebar-content">
          <!-- File Selection -->
          <div class="config-section">
            <h3 class="section-label">Data Source</h3>
            <select v-model="selectedFileId" class="config-select" @change="loadFileTracks">
              <option value="">Select a file...</option>
              <option v-for="file in availableFiles" :key="file.id" :value="file.id">
                {{ file.original_filename }}
              </option>
            </select>
          </div>

          <!-- Processing Options -->
          <div class="config-section">
            <h3 class="section-label">Processing Algorithm</h3>
            <div class="radio-group">
              <label class="radio-option">
                <input type="radio" v-model="algorithm" value="ransac" />
                <span>RANSAC</span>
              </label>
              <label class="radio-option">
                <input type="radio" v-model="algorithm" value="kalman" />
                <span>Kalman Filter</span>
              </label>
              <label class="radio-option">
                <input type="radio" v-model="algorithm" value="both" />
                <span>Both</span>
              </label>
            </div>
          </div>

          <!-- Parameters -->
          <div class="config-section">
            <h3 class="section-label">Parameters</h3>

            <div class="param-group">
              <label class="param-label">RANSAC Threshold</label>
              <input
                v-model.number="ransacThreshold"
                type="number"
                step="0.1"
                min="0"
                class="config-input"
              />
            </div>

            <div class="param-group">
              <label class="param-label">Process Noise (Kalman)</label>
              <input
                v-model.number="processNoise"
                type="number"
                step="0.01"
                min="0"
                class="config-input"
              />
            </div>

            <div class="param-group">
              <label class="param-label">Measurement Noise (Kalman)</label>
              <input
                v-model.number="measurementNoise"
                type="number"
                step="0.01"
                min="0"
                class="config-input"
              />
            </div>
          </div>

          <!-- Display Options -->
          <div class="config-section">
            <h3 class="section-label">Display Options</h3>

            <label class="toggle-option">
              <input type="checkbox" v-model="showRawTracks" />
              <span>Show Raw Tracks</span>
            </label>

            <label class="toggle-option">
              <input type="checkbox" v-model="showCorrectedTracks" />
              <span>Show Corrected Tracks</span>
            </label>

            <label class="toggle-option">
              <input type="checkbox" v-model="showAltitudeWall" />
              <span>Show Altitude Wall</span>
            </label>

            <div class="param-group">
              <label class="param-label">Track Opacity</label>
              <input
                v-model.number="trackOpacity"
                type="range"
                min="0.1"
                max="1"
                step="0.1"
                class="config-slider"
              />
            </div>
          </div>

          <!-- Track Info -->
          <div v-if="selectedTrack" class="config-section">
            <h3 class="section-label">Track Information</h3>
            <div class="track-info">
              <div class="info-row">
                <span class="info-label">Track ID:</span>
                <span class="info-value">{{ selectedTrack.track_id }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Points:</span>
                <span class="info-value">{{ selectedTrack.point_count }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Duration:</span>
                <span class="info-value">{{ formatDuration(selectedTrack.duration_seconds) }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Start:</span>
                <span class="info-value">{{ formatTime(selectedTrack.start_time) }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">End:</span>
                <span class="info-value">{{ formatTime(selectedTrack.end_time) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Main Visualization -->
      <div class="visualization-main">
        <div v-if="!selectedFileId" class="empty-state">
          <EmptyState
            title="No data source selected"
            description="Select a file from the sidebar to visualize tracks"
          >
            <template #action>
              <router-link to="/data" class="btn btn-primary">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                Upload Files
              </router-link>
            </template>
          </EmptyState>
        </div>

        <div v-else-if="loading" class="loading-state">
          <Loading :fullscreen="false" message="Loading tracks..." />
        </div>

        <div v-else-if="!tracks.length" class="empty-state">
          <EmptyState
            title="No tracks found"
            description="Process the file to generate tracks"
          />
        </div>

        <div v-else class="visualization-container">
          <ThreeRadar v-if="show3D" />
          <div v-else class="map-placeholder">
            <p>2D Map View (Leaflet)</p>
          </div>

          <!-- View Toggle -->
          <div class="view-toggle">
            <button
              :class="['toggle-btn', { active: show3D }]"
              @click="show3D = true"
            >
              3D View
            </button>
            <button
              :class="['toggle-btn', { active: !show3D }]"
              @click="show3D = false"
            >
              2D Map
            </button>
          </div>

          <!-- Track List Overlay -->
          <div class="tracks-overlay">
            <div class="overlay-header">
              <h3>Tracks ({{ tracks.length }})</h3>
              <button class="overlay-close" @click="showTrackList = false">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div class="tracks-list">
              <div
                v-for="track in tracks"
                :key="track.track_id"
                :class="['track-item', { active: selectedTrack?.track_id === track.track_id }]"
                @click="selectTrack(track)"
              >
                <div class="track-id">{{ track.track_id }}</div>
                <div class="track-meta">{{ track.point_count }} points</div>
              </div>
            </div>
          </div>

          <!-- Toggle Tracks Button -->
          <button v-if="!showTrackList" class="toggle-tracks-btn" @click="showTrackList = true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M4 6h16M4 12h16M4 18h16"
              />
            </svg>
            Tracks
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { filesApi, tracksApi } from '@/api'
import type { DataFile, Track } from '@/api/types'
import EmptyState from '@/components/EmptyState.vue'
import Loading from '@/components/Loading.vue'
import ThreeRadar from '@/components/ThreeRadar.vue'

const route = useRoute()
const appStore = useAppStore()

const showSettings = ref(true)
const showTrackList = ref(true)
const show3D = ref(true)

const loading = ref(false)
const processing = ref(false)

const availableFiles = ref<DataFile[]>([])
const selectedFileId = ref<number | null>(null)
const tracks = ref<Track[]>([])
const selectedTrack = ref<Track | null>(null)

// Processing parameters
const algorithm = ref<'ransac' | 'kalman' | 'both'>('ransac')
const ransacThreshold = ref(1.0)
const processNoise = ref(0.1)
const measurementNoise = ref(0.1)

// Display options
const showRawTracks = ref(true)
const showCorrectedTracks = ref(true)
const showAltitudeWall = ref(false)
const trackOpacity = ref(0.8)

const loadAvailableFiles = async () => {
  try {
    const response = await filesApi.list({ page: 1, page_size: 100, status: 'completed' })
    availableFiles.value = response.items

    // Check if file ID is in route query
    const fileParam = route.query.file
    if (fileParam) {
      selectedFileId.value = Number(fileParam) as number
      await loadFileTracks()
    }
  } catch (error: any) {
    appStore.error(error.message || 'Failed to load files')
  }
}

const loadFileTracks = async () => {
  if (!selectedFileId.value) return

  loading.value = true
  try {
    const [rawTracks, correctedTracks] = await Promise.all([
      tracksApi.getRaw({ file_id: selectedFileId.value }),
      tracksApi.getCorrected({ file_id: selectedFileId.value }).catch(() => []),
    ])

    // Combine tracks
    tracks.value = rawTracks
    if (correctedTracks.length > 0) {
      tracks.value = [...tracks.value, ...correctedTracks]
    }

    if (tracks.value.length > 0) {
      selectedTrack.value = tracks.value[0]
    }
  } catch (error: any) {
    appStore.error(error.message || 'Failed to load tracks')
  } finally {
    loading.value = false
  }
}

const processTracks = async () => {
  if (!selectedFileId.value) return

  processing.value = true
  try {
    const response = await tracksApi.process({
      file_id: selectedFileId.value,
      algorithm: algorithm.value,
      ransac_threshold: ransacThreshold.value,
      kalman_process_noise: processNoise.value,
      kalman_measurement_noise: measurementNoise.value,
    })

    appStore.success('Track processing started')

    // Poll for completion
    pollTaskStatus(response.task_id)
  } catch (error: any) {
    appStore.error(error.message || 'Failed to process tracks')
    processing.value = false
  }
}

const pollTaskStatus = async (taskId: string) => {
  const interval = setInterval(async () => {
    try {
      const status = await tracksApi.getTaskStatus(taskId)

      if (status.status === 'completed') {
        clearInterval(interval)
        processing.value = false
        appStore.success('Track processing completed')
        await loadFileTracks()
      } else if (status.status === 'failed') {
        clearInterval(interval)
        processing.value = false
        appStore.error(status.error || 'Processing failed')
      }
    } catch (error) {
      clearInterval(interval)
      processing.value = false
    }
  }, 2000)
}

const selectTrack = (track: Track) => {
  selectedTrack.value = track
}

const formatDuration = (seconds?: number): string => {
  if (!seconds) return '-'
  const hours = Math.floor(seconds / 3600)
  const mins = Math.floor((seconds % 3600) / 60)
  if (hours > 0) return `${hours}h ${mins}m`
  return `${mins}m`
}

const formatTime = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleTimeString()
}

onMounted(() => {
  loadAvailableFiles()
})
</script>

<style scoped>
.track-visualization {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--border-color, rgba(255, 255, 255, 0.1));
  background: var(--bg-secondary);
}

.page-title {
  margin: 0 0 0.25rem;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
}

.page-subtitle {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.875rem;
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

.visualization-layout {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.sidebar {
  width: 300px;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-color, rgba(255, 255, 255, 0.1));
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
}

.sidebar-collapsed {
  width: 0;
  overflow: hidden;
}

.sidebar-header {
  padding: 1rem;
  border-bottom: 1px solid var(--border-color, rgba(255, 255, 255, 0.1));
}

.sidebar-title {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

.config-section {
  margin-bottom: 1.5rem;
}

.section-label {
  margin: 0 0 0.75rem;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-secondary);
}

.config-select,
.config-input {
  width: 100%;
  padding: 0.625rem 0.875rem;
  border: 1px solid var(--border-color, rgba(255, 255, 255, 0.1));
  border-radius: 0.5rem;
  background: var(--bg-tertiary);
  color: var(--text-primary);
  font-size: 0.875rem;
}

.config-slider {
  width: 100%;
  accent-color: var(--color-primary);
}

.radio-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.radio-option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.radio-option input {
  cursor: pointer;
}

.toggle-option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
  cursor: pointer;
}

.toggle-option input {
  cursor: pointer;
}

.param-group {
  margin-bottom: 1rem;
}

.param-label {
  display: block;
  margin-bottom: 0.375rem;
  font-size: 0.8125rem;
  color: var(--text-secondary);
}

.track-info {
  padding: 0.75rem;
  border-radius: 0.5rem;
  background: var(--bg-tertiary);
}

.info-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  font-size: 0.8125rem;
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-label {
  color: var(--text-muted);
}

.info-value {
  color: var(--text-primary);
  font-weight: 500;
}

.visualization-main {
  flex: 1;
  position: relative;
  overflow: hidden;
}

.visualization-container {
  width: 100%;
  height: 100%;
  position: relative;
}

.empty-state,
.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.map-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  background: var(--bg-tertiary);
  color: var(--text-muted);
}

.view-toggle {
  position: absolute;
  top: 1rem;
  right: 1rem;
  display: flex;
  background: var(--bg-secondary);
  border-radius: 0.5rem;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.toggle-btn {
  padding: 0.5rem 1rem;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.toggle-btn.active {
  background: var(--color-primary);
  color: white;
}

.tracks-overlay {
  position: absolute;
  top: 1rem;
  left: 1rem;
  width: 250px;
  max-height: calc(100% - 2rem);
  background: var(--bg-secondary);
  border-radius: 0.75rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
}

.overlay-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--border-color, rgba(255, 255, 255, 0.1));
}

.overlay-header h3 {
  margin: 0;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-primary);
}

.overlay-close {
  width: 1.5rem;
  height: 1.5rem;
  padding: 0;
  border: none;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  border-radius: 0.25rem;
}

.overlay-close:hover {
  background: var(--bg-tertiary);
}

.overlay-close svg {
  width: 1rem;
  height: 1rem;
}

.tracks-list {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
}

.track-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.625rem 0.75rem;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: background 0.2s;
}

.track-item:hover {
  background: var(--bg-tertiary);
}

.track-item.active {
  background: rgba(59, 130, 246, 0.1);
}

.track-id {
  color: var(--text-primary);
  font-size: 0.8125rem;
  font-weight: 500;
}

.track-meta {
  color: var(--text-muted);
  font-size: 0.75rem;
}

.toggle-tracks-btn {
  position: absolute;
  bottom: 1rem;
  left: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1rem;
  border: none;
  border-radius: 0.5rem;
  background: var(--bg-secondary);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  color: var(--text-primary);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
}

.toggle-tracks-btn svg {
  width: 1rem;
  height: 1rem;
}

@media (max-width: 768px) {
  .sidebar {
    position: absolute;
    z-index: 100;
    height: 100%;
    box-shadow: 4px 0 12px rgba(0, 0, 0, 0.15);
  }

  .tracks-overlay {
    width: 200px;
  }
}
</style>
