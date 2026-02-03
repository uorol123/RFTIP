<template>
  <div class="track-details">
    <div class="page-header">
      <button class="back-btn" @click="router.back()">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
      </button>
      <div>
        <h1 class="page-title">Track Details</h1>
        <p class="page-subtitle">{{ trackId || 'Loading...' }}</p>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <Loading :fullscreen="false" message="Loading track details..." />
    </div>

    <div v-else-if="track" class="details-content">
      <div class="info-cards">
        <div class="info-card">
          <div class="card-label">Track ID</div>
          <div class="card-value">{{ track.track_id }}</div>
        </div>
        <div class="info-card">
          <div class="card-label">Points</div>
          <div class="card-value">{{ track.point_count?.toLocaleString() }}</div>
        </div>
        <div class="info-card">
          <div class="card-label">Duration</div>
          <div class="card-value">{{ formatDuration(track.duration_seconds) }}</div>
        </div>
        <div class="info-card">
          <div class="card-label">File ID</div>
          <div class="card-value">{{ track.file_id }}</div>
        </div>
      </div>

      <div class="section">
        <h2 class="section-title">Time Range</h2>
        <div class="time-range">
          <div class="time-point">
            <div class="time-label">Start</div>
            <div class="time-value">{{ formatDateTime(track.start_time) }}</div>
          </div>
          <div class="time-line"></div>
          <div class="time-point">
            <div class="time-label">End</div>
            <div class="time-value">{{ formatDateTime(track.end_time) }}</div>
          </div>
        </div>
      </div>

      <div class="section">
        <h2 class="section-title">Visualization</h2>
        <div class="visualization-placeholder">
          <p>3D/2D visualization would be rendered here</p>
          <p class="text-muted">Track has {{ track.point_count }} points</p>
        </div>
      </div>

      <div class="section">
        <h2 class="section-title">Raw Data Points</h2>
        <div class="points-table-wrapper">
          <table class="points-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Latitude</th>
                <th>Longitude</th>
                <th>Altitude (m)</th>
                <th>Speed (m/s)</th>
                <th>Heading (°)</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(point, index) in displayPoints" :key="index">
                <td>{{ formatDateTime(point.timestamp) }}</td>
                <td>{{ point.latitude.toFixed(6) }}</td>
                <td>{{ point.longitude.toFixed(6) }}</td>
                <td>{{ point.altitude.toFixed(1) }}</td>
                <td>{{ point.speed.toFixed(1) }}</td>
                <td>{{ point.heading.toFixed(1) }}</td>
              </tr>
            </tbody>
          </table>
          <div v-if="track.points.length > 10" class="table-footer">
            <button class="btn-expand" @click="showAllPoints = !showAllPoints">
              {{ showAllPoints ? 'Show Less' : `Show All (${track.points.length})` }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="empty-state">
      <EmptyState
        title="Track not found"
        description="The requested track could not be found"
      >
        <template #action>
          <router-link to="/tracks" class="btn btn-primary">
            Browse Tracks
          </router-link>
        </template>
      </EmptyState>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { tracksApi } from '@/api'
import type { Track, TrackPoint } from '@/api/types'
import EmptyState from '@/components/EmptyState.vue'
import Loading from '@/components/Loading.vue'

const router = useRouter()
const route = useRoute()

const loading = ref(true)
const track = ref<Track | null>(null)
const showAllPoints = ref(false)

const trackId = computed(() => route.params.id as string)

const displayPoints = computed(() => {
  if (!track.value) return []
  if (showAllPoints.value) return track.value.points
  return track.value.points.slice(0, 10)
})

const loadTrackDetails = async () => {
  const fileId = route.query.file as string
  if (!fileId) {
    router.push('/tracks')
    return
  }

  loading.value = true
  try {
    const tracks = await tracksApi.getRaw({
      file_id: Number(fileId),
      track_id: trackId.value,
    })

    if (tracks.length > 0) {
      track.value = tracks[0]
    } else {
      track.value = null
    }
  } catch (error) {
    track.value = null
  } finally {
    loading.value = false
  }
}

const formatDuration = (seconds?: number): string => {
  if (!seconds) return '-'
  const hours = Math.floor(seconds / 3600)
  const mins = Math.floor((seconds % 3600) / 60)
  if (hours > 0) return `${hours}h ${mins}m`
  return `${mins}m`
}

const formatDateTime = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleString()
}

onMounted(() => {
  loadTrackDetails()
})
</script>

<style scoped>
.track-details {
  padding: 1.5rem;
  max-width: 1000px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
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

.info-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
}

.info-card {
  padding: 1.25rem;
  border-radius: 0.75rem;
  background: var(--bg-secondary);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.card-label {
  font-size: 0.8125rem;
  color: var(--text-muted);
  margin-bottom: 0.375rem;
}

.card-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
}

.section {
  border-radius: 1rem;
  background: var(--bg-secondary);
  padding: 1.5rem;
}

.section-title {
  margin: 0 0 1.25rem;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
}

.time-range {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.time-point {
  flex: 1;
}

.time-label {
  font-size: 0.8125rem;
  color: var(--text-muted);
  margin-bottom: 0.375rem;
}

.time-value {
  font-size: 1rem;
  font-weight: 500;
  color: var(--text-primary);
}

.time-line {
  flex: 1;
  height: 2px;
  background: linear-gradient(90deg, var(--color-primary) 0%, var(--color-accent) 100%);
}

.visualization-placeholder {
  height: 300px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: 0.5rem;
  background: var(--bg-tertiary);
  color: var(--text-secondary);
}

.text-muted {
  color: var(--text-muted);
  margin-top: 0.5rem;
}

.points-table-wrapper {
  overflow-x: auto;
}

.points-table {
  width: 100%;
  border-collapse: collapse;
}

.points-table th,
.points-table td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid var(--border-color, rgba(255, 255, 255, 0.05));
}

.points-table th {
  font-size: 0.8125rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-secondary);
}

.points-table td {
  font-size: 0.875rem;
  color: var(--text-primary);
}

.points-table tr:hover td {
  background: var(--bg-tertiary);
}

.table-footer {
  padding: 1rem;
  text-align: center;
}

.btn-expand {
  padding: 0.5rem 1rem;
  border: 1px solid var(--border-color, rgba(255, 255, 255, 0.1));
  border-radius: 0.5rem;
  background: transparent;
  color: var(--text-primary);
  font-size: 0.875rem;
  cursor: pointer;
}

.btn-expand:hover {
  background: var(--bg-tertiary);
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

.btn-primary {
  background: var(--color-primary);
  color: white;
}

.btn-primary:hover {
  background: #2563eb;
}

.empty-state {
  display: flex;
  justify-content: center;
  padding: 4rem 0;
}

@media (max-width: 640px) {
  .track-details {
    padding: 1rem;
  }

  .info-cards {
    grid-template-columns: 1fr 1fr;
  }

  .time-range {
    flex-direction: column;
  }

  .time-line {
    height: 50px;
    width: 2px;
  }
}
</style>
