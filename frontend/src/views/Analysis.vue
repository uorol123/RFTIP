<template>
  <div class="analysis">
    <div class="page-header">
      <div>
        <h1 class="page-title">AI Trajectory Analysis</h1>
        <p class="page-subtitle">Analyze radar tracks with AI-powered insights</p>
      </div>
    </div>

    <div class="analysis-layout">
      <!-- Configuration Panel -->
      <div class="config-panel">
        <div class="panel-header">
          <h2 class="panel-title">Analysis Configuration</h2>
        </div>

        <div class="panel-content">
          <!-- Track Selection -->
          <div class="config-section">
            <h3 class="section-label">Select Track</h3>
            <select v-model="selectedTrackId" class="config-select" @change="loadTrackData">
              <option value="">Select a track...</option>
              <option v-for="track in availableTracks" :key="track.track_id" :value="track.track_id">
                {{ track.track_id }} ({{ track.point_count }} points)
              </option>
            </select>
          </div>

          <!-- Analysis Type -->
          <div class="config-section">
            <h3 class="section-label">Analysis Type</h3>
            <div class="radio-group">
              <label class="radio-option">
                <input type="radio" v-model="analysisType" value="overall" />
                <span>Overall Analysis</span>
              </label>
              <label class="radio-option">
                <input type="radio" v-model="analysisType" value="segment" />
                <span>Segment Analysis</span>
              </label>
            </div>
          </div>

          <!-- Segment Range (for segment analysis) -->
          <div v-if="analysisType === 'segment'" class="config-section">
            <h3 class="section-label">Time Range</h3>
            <div class="time-range">
              <div class="time-input">
                <label class="input-label">Start</label>
                <input
                  v-model="segmentStart"
                  type="datetime-local"
                  class="config-input"
                />
              </div>
              <div class="time-input">
                <label class="input-label">End</label>
                <input
                  v-model="segmentEnd"
                  type="datetime-local"
                  class="config-input"
                />
              </div>
            </div>
          </div>

          <!-- LLM Analysis -->
          <div class="config-section">
            <h3 class="section-label">LLM Analysis</h3>
            <label class="toggle-option">
              <input type="checkbox" v-model="useLLM" />
              <span>Use Large Language Model</span>
            </label>
            <div v-if="useLLM" class="llm-prompt">
              <label class="input-label">Custom Prompt (optional)</label>
              <textarea
                v-model="llmPrompt"
                class="config-textarea"
                rows="4"
                placeholder="Enter custom analysis prompt..."
              ></textarea>
            </div>
          </div>

          <!-- Features -->
          <div class="config-section">
            <h3 class="section-label">Extractable Features</h3>
            <div v-if="loadingFeatures" class="features-loading">
              <span>Loading features...</span>
            </div>
            <div v-else class="features-list">
              <label
                v-for="feature in availableFeatures"
                :key="feature.name"
                class="feature-option"
              >
                <input type="checkbox" v-model="selectedFeatures" :value="feature.name" />
                <span>{{ feature.name }}</span>
                <span class="feature-desc">{{ feature.description }}</span>
              </label>
            </div>
          </div>

          <!-- Analyze Button -->
          <button
            class="btn-analyze"
            @click="runAnalysis"
            :disabled="!selectedTrackId || analyzing"
          >
            <svg v-if="!analyzing" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
              />
            </svg>
            <svg v-else class="spin" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
              />
            </svg>
            {{ analyzing ? 'Analyzing...' : 'Run Analysis' }}
          </button>
        </div>
      </div>

      <!-- Results Panel -->
      <div class="results-panel">
        <div v-if="!selectedTrackId" class="empty-results">
          <EmptyState
            title="No track selected"
            description="Select a track from the configuration panel to analyze"
          />
        </div>

        <div v-else-if="analyzing" class="analyzing-state">
          <Loading :fullscreen="false" message="Running AI analysis..." />
        </div>

        <div v-else-if="!analysisResult" class="empty-results">
          <EmptyState
            title="No analysis results"
            description="Configure options and run analysis to see results"
          />
        </div>

        <div v-else class="results-content">
          <div class="results-header">
            <h2 class="results-title">Analysis Results</h2>
            <div class="results-actions">
              <button class="btn btn-secondary btn-sm" @click="generateReport('json')">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                  />
                </svg>
                Export JSON
              </button>
              <button class="btn btn-primary btn-sm" @click="generateReport('pdf')">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
                Generate PDF
              </button>
            </div>
          </div>

          <!-- Summary -->
          <div class="result-section">
            <h3 class="result-section-title">Summary</h3>
            <div class="summary-cards">
              <div class="summary-card">
                <div class="card-label">Total Distance</div>
                <div class="card-value">{{ formatDistance(analysisResult.summary.total_distance) }}</div>
              </div>
              <div class="summary-card">
                <div class="card-label">Duration</div>
                <div class="card-value">{{ formatDuration(analysisResult.summary.duration) }}</div>
              </div>
              <div class="summary-card">
                <div class="card-label">Avg Speed</div>
                <div class="card-value">{{ formatSpeed(analysisResult.summary.avg_speed) }}</div>
              </div>
              <div class="summary-card">
                <div class="card-label">Altitude Range</div>
                <div class="card-value">
                  {{ analysisResult.summary.min_altitude }}m - {{ analysisResult.summary.max_altitude }}m
                </div>
              </div>
            </div>
          </div>

          <!-- Extracted Features -->
          <div v-if="analysisResult.features?.length" class="result-section">
            <h3 class="result-section-title">Extracted Features</h3>
            <div class="features-grid">
              <div
                v-for="feature in analysisResult.features"
                :key="feature.feature_name"
                class="feature-card"
              >
                <div class="feature-name">{{ feature.feature_name }}</div>
                <div class="feature-value">{{ feature.value.toFixed(4) }}</div>
                <div class="feature-description">{{ feature.description }}</div>
              </div>
            </div>
          </div>

          <!-- LLM Analysis -->
          <div v-if="analysisResult.llm_analysis" class="result-section">
            <h3 class="result-section-title">AI Analysis</h3>
            <div class="llm-result">
              {{ analysisResult.llm_analysis }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAppStore } from '@/stores/app'
import { analysisApi, tracksApi } from '@/api'
import type { Track, AnalysisResult, FeatureInfo } from '@/api/types'
import EmptyState from '@/components/EmptyState.vue'
import Loading from '@/components/Loading.vue'

const appStore = useAppStore()

const availableTracks = ref<Track[]>([])
const selectedTrackId = ref('')
const analyzing = ref(false)
const loadingFeatures = ref(false)

const analysisType = ref<'overall' | 'segment'>('overall')
const segmentStart = ref('')
const segmentEnd = ref('')
const useLLM = ref(false)
const llmPrompt = ref('')
const selectedFeatures = ref<string[]>([])

const availableFeatures = ref<FeatureInfo[]>([])
const analysisResult = ref<AnalysisResult | null>(null)

const loadAvailableTracks = async () => {
  try {
    // Load tracks from files
    const response = await tracksApi.getRaw({ file_id: 1, limit: 100 })
    availableTracks.value = response
  } catch (error) {
    // Ignore error for now
  }
}

const loadTrackData = () => {
  // Reset analysis when track changes
  analysisResult.value = null
}

const loadFeatures = async () => {
  loadingFeatures.value = true
  try {
    availableFeatures.value = await analysisApi.getAvailableFeatures()
    selectedFeatures.value = availableFeatures.value
      .filter(f => f.extractable)
      .map(f => f.name)
  } catch (error: any) {
    appStore.error(error.message || 'Failed to load features')
  } finally {
    loadingFeatures.value = false
  }
}

const runAnalysis = async () => {
  if (!selectedTrackId.value) return

  analyzing.value = true
  try {
    const response = await analysisApi.analyzeTrajectory({
      track_id: selectedTrackId.value,
      analysis_type: analysisType.value,
      start_time: segmentStart.value || undefined,
      end_time: segmentEnd.value || undefined,
      use_llm: useLLM.value,
      llm_prompt: llmPrompt.value || undefined,
    })

    // Poll for completion
    pollAnalysisStatus(response.analysis_id)
  } catch (error: any) {
    appStore.error(error.message || 'Failed to start analysis')
    analyzing.value = false
  }
}

const pollAnalysisStatus = async (analysisId: string) => {
  const interval = setInterval(async () => {
    try {
      const status = await analysisApi.getTaskStatus(analysisId)

      if (status.status === 'completed' && status.result) {
        clearInterval(interval)
        analyzing.value = false
        analysisResult.value = status.result
        appStore.success('Analysis completed')
      } else if (status.status === 'failed') {
        clearInterval(interval)
        analyzing.value = false
        appStore.error(status.error || 'Analysis failed')
      }
    } catch (error) {
      clearInterval(interval)
      analyzing.value = false
    }
  }, 2000)
}

const generateReport = async (format: 'pdf' | 'json') => {
  if (!selectedTrackId.value) return

  try {
    const report = await analysisApi.generateReport(selectedTrackId.value, format)

    if (format === 'json') {
      // Download JSON
      const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `analysis-${selectedTrackId.value}.json`
      a.click()
      URL.revokeObjectURL(url)
      appStore.success('Report downloaded')
    } else {
      // Handle PDF download
      const blob = new Blob([report.content], { type: 'application/pdf' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `analysis-${selectedTrackId.value}.pdf`
      a.click()
      URL.revokeObjectURL(url)
      appStore.success('Report generated')
    }
  } catch (error: any) {
    appStore.error(error.message || 'Failed to generate report')
  }
}

const formatDistance = (meters: number): string => {
  if (meters >= 1000) return (meters / 1000).toFixed(2) + ' km'
  return meters.toFixed(0) + ' m'
}

const formatDuration = (seconds: number): string => {
  const hours = Math.floor(seconds / 3600)
  const mins = Math.floor((seconds % 3600) / 60)
  if (hours > 0) return `${hours}h ${mins}m`
  return `${mins}m ${Math.floor(seconds % 60)}s`
}

const formatSpeed = (mps: number): string => {
  const kmh = mps * 3.6
  return kmh.toFixed(1) + ' km/h'
}

onMounted(() => {
  loadAvailableTracks()
  loadFeatures()
})
</script>

<style scoped>
.analysis {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.page-header {
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

.analysis-layout {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.config-panel {
  width: 320px;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-color, rgba(255, 255, 255, 0.1));
  display: flex;
  flex-direction: column;
}

.panel-header {
  padding: 1rem;
  border-bottom: 1px solid var(--border-color, rgba(255, 255, 255, 0.1));
}

.panel-title {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.panel-content {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.config-section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.section-label {
  margin: 0;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-secondary);
}

.config-select,
.config-input,
.config-textarea {
  width: 100%;
  padding: 0.625rem 0.875rem;
  border: 1px solid var(--border-color, rgba(255, 255, 255, 0.1));
  border-radius: 0.5rem;
  background: var(--bg-tertiary);
  color: var(--text-primary);
  font-size: 0.875rem;
}

.config-textarea {
  resize: vertical;
  min-height: 80px;
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

.toggle-option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.time-range {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
}

.time-input {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.input-label {
  font-size: 0.8125rem;
  color: var(--text-secondary);
}

.llm-prompt {
  margin-top: 0.75rem;
}

.features-loading {
  color: var(--text-muted);
  font-size: 0.875rem;
}

.features-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: 200px;
  overflow-y: auto;
}

.feature-option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 0.375rem;
}

.feature-option:hover {
  background: var(--bg-tertiary);
}

.feature-desc {
  margin-left: auto;
  font-size: 0.75rem;
  color: var(--text-muted);
}

.btn-analyze {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.875rem;
  border: none;
  border-radius: 0.5rem;
  background: var(--color-primary);
  color: white;
  font-size: 0.9375rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-analyze:hover:not(:disabled) {
  background: #2563eb;
}

.btn-analyze:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-analyze svg {
  width: 1.125rem;
  height: 1.125rem;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.results-panel {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

.empty-results,
.analyzing-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.results-content {
  max-width: 900px;
  margin: 0 auto;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.results-title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
}

.results-actions {
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

.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.8125rem;
}

.result-section {
  margin-bottom: 2rem;
}

.result-section-title {
  margin: 0 0 1rem;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
}

.summary-card {
  padding: 1.25rem;
  border-radius: 0.75rem;
  background: var(--bg-secondary);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.card-label {
  font-size: 0.8125rem;
  color: var(--text-muted);
  margin-bottom: 0.5rem;
}

.card-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.feature-card {
  padding: 1rem;
  border-radius: 0.5rem;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color, rgba(255, 255, 255, 0.1));
}

.feature-name {
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.375rem;
}

.feature-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-primary);
  margin-bottom: 0.25rem;
}

.feature-description {
  font-size: 0.8125rem;
  color: var(--text-muted);
}

.llm-result {
  padding: 1.25rem;
  border-radius: 0.75rem;
  background: var(--bg-secondary);
  color: var(--text-primary);
  line-height: 1.7;
  white-space: pre-wrap;
}

@media (max-width: 768px) {
  .analysis-layout {
    flex-direction: column;
  }

  .config-panel {
    width: 100%;
    max-height: 40vh;
  }

  .summary-cards {
    grid-template-columns: 1fr 1fr;
  }

  .results-header {
    flex-direction: column;
    align-items: stretch;
  }

  .results-actions {
    justify-content: stretch;
  }

  .results-actions .btn {
    flex: 1;
  }
}
</style>
