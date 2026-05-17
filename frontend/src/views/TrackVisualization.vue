<template>
  <div class="page">
    <AppHeader />
    <div class="page-content">
      <div class="page-header">
        <div>
          <h1 class="page-title">轨迹可视化</h1>
          <p class="page-subtitle">查看轨迹数据与禁飞区入侵检测</p>
        </div>
        <div class="header-actions">
          <button
            v-if="selectedFileId"
            class="btn btn-danger"
            :disabled="detecting"
            @click="runIntrusionDetection"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4.5c-.77-.833-2.694-.833-3.464 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            {{ detecting ? '检测中...' : '禁飞区入侵检测' }}
          </button>
          <router-link to="/data" class="btn btn-secondary">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
            </svg>
            上传数据
          </router-link>
        </div>
      </div>

      <div class="visualization-container">
        <!-- 地图主区域 -->
        <div class="viewport">
          <div v-if="!selectedFileId" class="empty-viewport">
            <div class="viewport-placeholder">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
              </svg>
              <h3>{{ files.length === 0 ? '暂无轨迹数据' : '请从右侧选择一个数据文件' }}</h3>
              <p>{{ files.length === 0 ? '请先上传雷达轨迹数据文件' : '选择文件后可查看轨迹并进行入侵检测' }}</p>
              <router-link v-if="files.length === 0" to="/data" class="btn btn-primary">
                前往上传
              </router-link>
            </div>
          </div>
          <div v-else class="viewport-content">
            <div class="viewport-header">
              <span class="viewport-file-name">{{ files.find(f => f.id === selectedFileId)?.file_name }}</span>
              <div class="viewport-header-actions">
                <span v-if="intrusionResults.length > 0" class="intrusion-count-badge">
                  {{ intrusionResults.length }} 个入侵点
                </span>
                <button class="btn-close-viewport" @click="selectedFileId = null">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
            <div class="map-canvas" ref="mapContainer"></div>
          </div>
        </div>

        <!-- 右侧控制面板 -->
        <div class="control-panel">
          <div class="panel-section">
            <h3 class="panel-title">数据文件</h3>
            <div class="file-list">
              <div v-if="loading" class="file-list-loading">
                <svg class="spinner" viewBox="0 0 24 24">
                  <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="3" stroke-dasharray="32" stroke-linecap="round" />
                </svg>
                <p>加载中...</p>
              </div>
              <div v-else-if="files.length === 0" class="file-list-empty">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <p>暂无已处理的文件</p>
                <router-link class="btn-link" to="/data">前往上传</router-link>
              </div>
              <div v-else class="file-list-items">
                <div
                  v-for="file in files"
                  :key="file.id"
                  class="file-list-item"
                  :class="{ active: selectedFileId === file.id }"
                  @click="selectFile(file)"
                >
                  <div class="file-item-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <div class="file-item-info">
                    <div class="file-item-name">{{ file.file_name }}</div>
                    <div class="file-item-meta">
                      <span class="file-item-rows">{{ file.row_count || 0 }} 行</span>
                      <span class="file-item-date">{{ formatDate(file.upload_time) }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 轨迹统计 -->
          <div v-if="trackStats" class="panel-section">
            <h3 class="panel-title">轨迹信息</h3>
            <div class="stats-grid">
              <div class="stat-item">
                <span class="stat-label">轨迹点数</span>
                <span class="stat-value">{{ trackStats.pointCount }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">轨迹条数</span>
                <span class="stat-value">{{ trackStats.trackCount }}</span>
              </div>
            </div>
          </div>

          <!-- 入侵检测结果 -->
          <div v-if="intrusionResults.length > 0" class="panel-section">
            <h3 class="panel-title">入侵检测结果 ({{ intrusionResults.length }})</h3>
            <div class="intrusion-list">
              <div v-for="(item, idx) in intrusionResults" :key="idx" class="intrusion-item">
                <span :class="['severity-dot', item.severity]"></span>
                <div class="intrusion-info">
                  <span class="intrusion-pos">{{ item.latitude.toFixed(4) }}, {{ item.longitude.toFixed(4) }}</span>
                  <span class="intrusion-alt">{{ item.altitude?.toFixed(1) ?? '-' }} m</span>
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
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import AppHeader from '@/components/AppHeader.vue'
import { filesApi } from '@/api/files'
import { tracksApi } from '@/api/tracks'
import { zonesApi } from '@/api/zones'
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()

const loading = ref(false)
const files = ref<any[]>([])
const selectedFileId = ref<number | null>(null)
const detecting = ref(false)
const intrusionResults = ref<any[]>([])
const trackStats = ref<{ pointCount: number; trackCount: number } | null>(null)

const mapContainer = ref<HTMLElement | null>(null)
let map: L.Map | null = null
let trackLayer = L.polyline([], { color: '#3b82f6', weight: 2 })
let zoneOverlay = L.layerGroup()
let intrusionMarkers = L.layerGroup()

// --- Load files ---
async function loadFiles() {
  loading.value = true
  try {
    const res = await filesApi.getFileList({ skip: 0, limit: 100, status: 'completed', category: 'trajectory' })
    files.value = res.files || []
  } catch {
    files.value = []
  } finally {
    loading.value = false
  }
}

// --- Select file ---
async function selectFile(file: any) {
  selectedFileId.value = file.id
  intrusionResults.value = []
  trackStats.value = null

  try {
    const tracks = await tracksApi.getRaw({ file_id: file.id, limit: 10000 })
    const points = (tracks || []).map((t: any) => [t.latitude, t.longitude] as [number, number])

    // Count unique track_ids (batch_id)
    const trackIds = new Set((tracks || []).map((t: any) => t.track_id))
    trackStats.value = { pointCount: points.length, trackCount: trackIds.size }

    await nextTick()
    renderTracks(points)
  } catch (e: any) {
    appStore.error(e?.message || '加载轨迹数据失败')
  }
}

// --- Map ---
function initMap() {
  if (!mapContainer.value || map) return
  map = L.map(mapContainer.value, { zoomControl: false }).setView([39.9042, 116.4074], 10)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap',
    maxZoom: 19,
  }).addTo(map)
  trackLayer.addTo(map)
  zoneOverlay.addTo(map)
  intrusionMarkers.addTo(map)
}

function renderTracks(points: [number, number][]) {
  if (!map) { initMap(); if (!map) return }

  intrusionMarkers.clearLayers()
  zoneOverlay.clearLayers()
  trackLayer.setLatLngs(points)

  if (points.length > 0) {
    L.circleMarker(points[0], { radius: 5, color: '#10b981', fillColor: '#10b981', fillOpacity: 1 })
      .bindPopup('起点').addTo(map!)
    L.circleMarker(points[points.length - 1], { radius: 5, color: '#ef4444', fillColor: '#ef4444', fillOpacity: 1 })
      .bindPopup('终点').addTo(map!)

    map.fitBounds(L.latLngBounds(points), { padding: [40, 40] })
  }

  loadZoneOverlay()
}

async function loadZoneOverlay() {
  zoneOverlay.clearLayers()
  try {
    const res = await zonesApi.list()
    const zones = Array.isArray(res) ? res : (res as any).items ?? []
    for (const zone of zones) {
      if (!zone.is_active) continue
      try {
        const coords = JSON.parse(zone.coordinates)
        const style = { color: '#10b981', weight: 1, fillColor: '#10b981', fillOpacity: 0.08, dashArray: '4,4' }
        let layer: L.Layer
        if (zone.zone_type === 'circle' && coords.center) {
          layer = L.circle([coords.center.lat, coords.center.lng], { ...style, radius: coords.radius })
        } else if (zone.zone_type === 'polygon' && coords.vertices) {
          const latlngs = coords.vertices.map((v: any) => [v.lat, v.lng] as [number, number])
          layer = L.polygon(latlngs, style)
        } else continue
        ;(layer as any).bindPopup(`<strong>${zone.zone_name}</strong>`)
        zoneOverlay.addLayer(layer)
      } catch { /* skip */ }
    }
  } catch { /* ignore */ }
}

// --- Intrusion detection by file ---
async function runIntrusionDetection() {
  if (!selectedFileId.value) return
  detecting.value = true
  try {
    const intrusions = await zonesApi.detectIntrusionsByFile(selectedFileId.value)
    intrusionResults.value = intrusions || []
    if (intrusions.length === 0) {
      appStore.success('未检测到禁飞区入侵')
    } else {
      appStore.error(`检测到 ${intrusions.length} 个入侵点，已发送预警邮件`)
      renderIntrusionMarkers(intrusions)
    }
  } catch (e: any) {
    appStore.error(e?.message || '入侵检测失败')
  } finally {
    detecting.value = false
  }
}

function renderIntrusionMarkers(intrusions: any[]) {
  if (!map) return
  intrusionMarkers.clearLayers()
  for (const i of intrusions) {
    const marker = L.circleMarker([i.latitude, i.longitude], {
      radius: 7, color: '#ef4444', fillColor: '#ef4444', fillOpacity: 0.85, weight: 2,
    })
    marker.bindPopup(`
      <strong>入侵告警</strong><br/>
      轨迹: ${i.track_id}<br/>
      严重程度: ${i.severity === 'high' ? '高危' : i.severity === 'medium' ? '中危' : '低危'}<br/>
      位置: ${i.latitude.toFixed(4)}, ${i.longitude.toFixed(4)}<br/>
      高度: ${i.altitude?.toFixed(1) ?? '-'} m
    `)
    intrusionMarkers.addLayer(marker)
  }
}

watch(selectedFileId, (val) => {
  if (!val && map) {
    trackLayer.setLatLngs([])
    intrusionMarkers.clearLayers()
    zoneOverlay.clearLayers()
  }
})

function formatDate(dateStr: string | null): string {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - d.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  if (days === 0) {
    const hours = Math.floor(diff / (1000 * 60 * 60))
    return hours === 0 ? '刚刚' : `${hours} 小时前`
  }
  if (days === 1) return '昨天'
  if (days < 7) return `${days} 天前`
  return d.toLocaleDateString('zh-CN')
}

onMounted(() => { loadFiles() })
onUnmounted(() => { map?.remove(); map = null })
</script>

<style scoped>
.page { min-height: 100vh; background: var(--bg-primary); }
.page-content { padding: 1.5rem; max-width: 1600px; margin: 0 auto; height: calc(100vh - 65px); display: flex; flex-direction: column; }
.page-header { display: flex; justify-content: space-between; align-items: center; gap: 1rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
.page-title { margin: 0 0 0.25rem; font-size: 1.75rem; font-weight: 700; color: var(--text-primary); }
.page-subtitle { margin: 0; color: var(--text-secondary); font-size: 0.9375rem; }
.header-actions { display: flex; gap: 0.75rem; }
.btn { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.625rem 1.25rem; border: none; border-radius: 0.5rem; font-size: 0.875rem; font-weight: 500; cursor: pointer; transition: all 0.2s; text-decoration: none; }
.btn svg { width: 1rem; height: 1rem; }
.btn-primary { background: var(--color-primary); color: white; }
.btn-primary:hover { background: #2563eb; }
.btn-secondary { background: var(--bg-tertiary); border: 1px solid var(--border-color); color: var(--text-primary); }
.btn-secondary:hover { background: var(--bg-primary); }
.btn-danger { background: #ef4444; color: white; }
.btn-danger:hover:not(:disabled) { background: #dc2626; }
.btn-danger:disabled { opacity: 0.6; cursor: not-allowed; }

.visualization-container { display: grid; grid-template-columns: 1fr 300px; gap: 1rem; flex: 1; min-height: 0; }
.viewport { background: var(--bg-secondary); border-radius: 1rem; overflow: hidden; position: relative; }
.empty-viewport { height: 100%; display: flex; align-items: center; justify-content: center; }
.viewport-placeholder { display: flex; flex-direction: column; align-items: center; padding: 3rem; text-align: center; }
.viewport-placeholder svg { width: 4rem; height: 4rem; color: var(--text-muted); opacity: 0.5; margin-bottom: 1.5rem; }
.viewport-placeholder h3 { margin: 0 0 0.5rem; font-size: 1.125rem; color: var(--text-primary); }
.viewport-placeholder p { margin: 0 0 1.5rem; color: var(--text-muted); font-size: 0.875rem; }
.viewport-content { height: 100%; display: flex; flex-direction: column; }
.viewport-header { display: flex; align-items: center; justify-content: space-between; padding: 0.75rem 1rem; background: var(--bg-tertiary); border-bottom: 1px solid var(--border-color); }
.viewport-file-name { font-size: 0.875rem; font-weight: 500; color: var(--text-primary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.viewport-header-actions { display: flex; align-items: center; gap: 0.75rem; }
.intrusion-count-badge { padding: 0.25rem 0.625rem; background: rgba(239, 68, 68, 0.1); color: #ef4444; border-radius: 0.375rem; font-size: 0.75rem; font-weight: 500; }
.btn-close-viewport { width: 1.75rem; height: 1.75rem; display: flex; align-items: center; justify-content: center; background: transparent; border: none; border-radius: 0.375rem; color: var(--text-muted); cursor: pointer; }
.btn-close-viewport:hover { background: var(--bg-secondary); color: var(--text-primary); }
.btn-close-viewport svg { width: 1rem; height: 1rem; }
.map-canvas { flex: 1; min-height: 400px; }

.control-panel { background: var(--bg-secondary); border-radius: 1rem; padding: 1rem; display: flex; flex-direction: column; gap: 1rem; overflow-y: auto; }
.panel-section { border-bottom: 1px solid var(--border-color); padding-bottom: 1rem; }
.panel-section:last-child { border-bottom: none; padding-bottom: 0; }
.panel-title { margin: 0 0 0.75rem; font-size: 0.875rem; font-weight: 600; color: var(--text-primary); }

.file-list { max-height: 280px; overflow-y: auto; }
.file-list-loading, .file-list-empty { display: flex; flex-direction: column; align-items: center; padding: 2rem 1rem; text-align: center; color: var(--text-muted); }
.file-list-empty svg { width: 2rem; height: 2rem; margin-bottom: 0.5rem; opacity: 0.5; }
.file-list-empty p { margin: 0; font-size: 0.8125rem; }
.spinner { width: 2rem; height: 2rem; animation: spin 1s linear infinite; margin-bottom: 0.5rem; }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
.btn-link { margin-top: 0.5rem; padding: 0; background: transparent; border: none; color: var(--color-primary); font-size: 0.8125rem; cursor: pointer; text-decoration: underline; }

.file-list-items { display: flex; flex-direction: column; }
.file-list-item { display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem; border-radius: 0.5rem; cursor: pointer; transition: background 0.2s; }
.file-list-item:hover { background: var(--bg-tertiary); }
.file-list-item.active { background: rgba(59, 130, 246, 0.1); }
.file-item-icon { flex-shrink: 0; width: 1.5rem; height: 1.5rem; color: var(--text-muted); }
.file-item-icon svg { width: 100%; height: 100%; }
.file-item-info { flex: 1; min-width: 0; }
.file-item-name { font-size: 0.8125rem; font-weight: 500; color: var(--text-primary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.file-item-meta { display: flex; align-items: center; gap: 0.5rem; margin-top: 0.125rem; }
.file-item-rows { font-size: 0.75rem; color: var(--color-primary); }
.file-item-date { font-size: 0.75rem; color: var(--text-muted); white-space: nowrap; }

.stats-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; }
.stat-item { display: flex; flex-direction: column; gap: 0.125rem; padding: 0.5rem; background: var(--bg-tertiary); border-radius: 0.375rem; }
.stat-label { font-size: 0.6875rem; color: var(--text-muted); }
.stat-value { font-size: 0.8125rem; font-weight: 600; color: var(--text-primary); }

.intrusion-list { display: flex; flex-direction: column; gap: 0.375rem; max-height: 200px; overflow-y: auto; }
.intrusion-item { display: flex; align-items: center; gap: 0.5rem; padding: 0.375rem 0.5rem; background: var(--bg-tertiary); border-radius: 0.375rem; font-size: 0.75rem; }
.severity-dot { width: 0.5rem; height: 0.5rem; border-radius: 50%; flex-shrink: 0; background: #f59e0b; }
.severity-dot.high { background: #ef4444; }
.severity-dot.medium { background: #f59e0b; }
.severity-dot.low { background: #10b981; }
.intrusion-info { display: flex; gap: 0.75rem; color: var(--text-secondary); }
.intrusion-pos { font-family: monospace; }
.intrusion-alt { color: var(--text-muted); }

@media (max-width: 1024px) {
  .visualization-container { grid-template-columns: 1fr; grid-template-rows: 1fr auto; }
  .viewport { min-height: 400px; }
  .control-panel { max-height: 300px; }
}
@media (max-width: 768px) {
  .page-content { padding: 1rem; }
  .page-header { flex-direction: column; align-items: stretch; }
  .header-actions { flex-direction: column; }
  .header-actions .btn { width: 100%; justify-content: center; }
}
</style>
