<template>
  <div class="page">
    <AppHeader />
    <div class="page-content">
      <div class="page-header">
        <div>
          <h1 class="page-title">禁飞区管理</h1>
          <p class="page-subtitle">配置和监控受限空域区域</p>
        </div>
        <div class="header-actions">
          <button class="btn btn-secondary" @click="activeTab = activeTab === 'zones' ? 'intrusions' : 'zones'">
            {{ activeTab === 'zones' ? '入侵记录' : '禁飞区管理' }}
          </button>
          <button v-if="activeTab === 'zones'" class="btn btn-primary" @click="openCreateModal">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            创建禁飞区
          </button>
        </div>
      </div>

      <div class="zones-layout">
        <!-- 左侧面板 -->
        <div class="zones-list">
          <!-- 禁飞区列表 -->
          <template v-if="activeTab === 'zones'">
            <div class="list-header">
              <h2>禁飞区列表 ({{ zones.length }})</h2>
              <label class="toggle-switch">
                <input type="checkbox" v-model="showActiveOnly" />
                <span class="toggle-slider"></span>
                <span class="toggle-label">仅显示启用</span>
              </label>
            </div>
            <div class="zones-grid">
              <div
                v-for="zone in filteredZones"
                :key="zone.id"
                class="zone-card"
                :class="{ inactive: !zone.is_active, selected: selectedZoneId === zone.id }"
                @click="selectedZoneId = zone.id"
              >
                <div class="zone-header">
                  <h3 class="zone-name">{{ zone.zone_name }}</h3>
                  <div class="zone-status">
                    <span :class="['status-badge', zone.is_active ? 'active' : 'inactive']">
                      {{ zone.is_active ? '启用' : '禁用' }}
                    </span>
                    <span class="zone-type">{{ zone.zone_type === 'circle' ? '圆形' : '多边形' }}</span>
                  </div>
                </div>
                <div class="zone-info">
                  <div class="zone-detail">
                    <span class="detail-label">高度范围:</span>
                    <span class="detail-value">{{ zone.min_altitude }}m - {{ zone.max_altitude }}m</span>
                  </div>
                  <div class="zone-detail">
                    <span class="detail-label">预警通知:</span>
                    <span class="detail-value">{{ zone.notification_enabled ? '已启用' : '已禁用' }}</span>
                  </div>
                </div>
                <div class="zone-actions">
                  <button
                    class="action-btn"
                    :title="zone.is_active ? '禁用' : '启用'"
                    @click.stop="toggleZone(zone)"
                  >
                    <svg v-if="zone.is_active" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                    <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                    {{ zone.is_active ? '禁用' : '启用' }}
                  </button>
                  <button class="action-btn danger" title="删除" @click.stop="deleteZone(zone)">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 011-1h4a1 1 0 011 1v3M4 7h16" />
                    </svg>
                    删除
                  </button>
                </div>
              </div>
              <div v-if="loading" class="empty-zones">
                <p>加载中...</p>
              </div>
              <div v-else-if="filteredZones.length === 0" class="empty-zones">
                <div class="empty-state">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  <p>暂无禁飞区</p>
                  <p class="empty-desc">点击"创建禁飞区"开始添加</p>
                </div>
              </div>
            </div>
          </template>

          <!-- 入侵记录列表 -->
          <template v-else>
            <div class="list-header">
              <h2>入侵记录 ({{ intrusions.length }})</h2>
            </div>
            <div class="zones-grid">
              <div v-for="intrusion in intrusions" :key="intrusion.id" class="zone-card intrusion-card">
                <div class="zone-header">
                  <h3 class="zone-name">轨迹 {{ intrusion.track_id }}</h3>
                  <span :class="['severity-badge', intrusion.severity]">{{ severityLabel(intrusion.severity) }}</span>
                </div>
                <div class="zone-info">
                  <div class="zone-detail">
                    <span class="detail-label">位置:</span>
                    <span class="detail-value">{{ intrusion.latitude.toFixed(4) }}, {{ intrusion.longitude.toFixed(4) }}</span>
                  </div>
                  <div class="zone-detail">
                    <span class="detail-label">高度:</span>
                    <span class="detail-value">{{ intrusion.altitude?.toFixed(1) ?? '-' }} m</span>
                  </div>
                  <div class="zone-detail">
                    <span class="detail-label">时间:</span>
                    <span class="detail-value">{{ formatTime(intrusion.timestamp) }}</span>
                  </div>
                </div>
              </div>
              <div v-if="intrusions.length === 0" class="empty-zones">
                <div class="empty-state">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <p>暂无入侵记录</p>
                </div>
              </div>
            </div>
          </template>
        </div>

        <!-- 地图区域 -->
        <div class="map-container">
          <div class="map-header">
            <h3>地图视图</h3>
            <div class="map-controls">
              <button class="map-btn" title="适应视图" @click="fitMapView">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 0h-4" />
                </svg>
              </button>
            </div>
          </div>
          <div class="map-viewport" ref="mapContainer"></div>
          <div class="map-legend">
            <div class="legend-item">
              <div class="legend-color legend-active"></div>
              <span>启用区域</span>
            </div>
            <div class="legend-item">
              <div class="legend-color legend-inactive"></div>
              <span>禁用区域</span>
            </div>
            <div v-if="activeTab === 'intrusions'" class="legend-item">
              <div class="legend-color legend-intrusion"></div>
              <span>入侵点</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 创建弹窗 -->
      <Teleport to="body">
        <div v-if="showCreateModal" class="modal-overlay" @click="showCreateModal = false">
          <div class="modal-content" @click.stop>
            <div class="modal-header">
              <h2 class="modal-title">创建禁飞区</h2>
              <button class="modal-close" @click="showCreateModal = false">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div class="modal-body">
              <div class="form-group">
                <label class="form-label">区域名称 *</label>
                <input type="text" class="form-input" v-model="form.zone_name" placeholder="例如：机场限制区" />
              </div>
              <div class="form-group">
                <label class="form-label">区域类型</label>
                <div class="type-selector">
                  <button :class="['type-option', { active: form.zone_type === 'circle' }]" @click="form.zone_type = 'circle'">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <circle cx="12" cy="12" r="8" />
                    </svg>
                    <span>圆形区域</span>
                  </button>
                  <button :class="['type-option', { active: form.zone_type === 'polygon' }]" @click="form.zone_type = 'polygon'">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                    </svg>
                    <span>多边形区域</span>
                  </button>
                </div>
              </div>

              <!-- 圆形参数 -->
              <template v-if="form.zone_type === 'circle'">
                <div class="form-row">
                  <div class="form-group">
                    <label class="form-label">中心纬度 *</label>
                    <input type="number" step="0.000001" class="form-input" v-model.number="form.circleCenter.lat" placeholder="39.9042" />
                  </div>
                  <div class="form-group">
                    <label class="form-label">中心经度 *</label>
                    <input type="number" step="0.000001" class="form-input" v-model.number="form.circleCenter.lng" placeholder="116.4074" />
                  </div>
                </div>
                <div class="form-group">
                  <label class="form-label">半径 (米) *</label>
                  <input type="number" class="form-input" v-model.number="form.circleRadius" placeholder="1000" />
                </div>
              </template>

              <!-- 多边形参数 -->
              <template v-if="form.zone_type === 'polygon'">
                <div class="form-group">
                  <label class="form-label">多边形顶点 (每行一个: 纬度,经度)</label>
                  <textarea
                    class="form-input form-textarea"
                    v-model="form.polygonText"
                    placeholder="39.9100,116.4000&#10;39.9000,116.4100&#10;39.8900,116.3900"
                    rows="4"
                  ></textarea>
                </div>
              </template>

              <div class="form-row">
                <div class="form-group">
                  <label class="form-label">最低高度 (米)</label>
                  <input type="number" class="form-input" v-model.number="form.min_altitude" placeholder="0" />
                </div>
                <div class="form-group">
                  <label class="form-label">最高高度 (米)</label>
                  <input type="number" class="form-input" v-model.number="form.max_altitude" placeholder="10000" />
                </div>
              </div>
              <div class="form-group">
                <label class="checkbox-label">
                  <input type="checkbox" v-model="form.notification_enabled" />
                  <span>启用预警通知</span>
                </label>
              </div>
              <div class="form-group" v-if="form.notification_enabled">
                <label class="form-label">通知邮箱</label>
                <input type="email" class="form-input" v-model="form.notification_email" placeholder="example@email.com" />
              </div>
              <div v-if="formError" class="form-error">{{ formError }}</div>
            </div>
            <div class="modal-footer">
              <button class="btn btn-secondary" @click="showCreateModal = false">取消</button>
              <button class="btn btn-primary" @click="createZone" :disabled="creating">
                {{ creating ? '创建中...' : '创建' }}
              </button>
            </div>
          </div>
        </div>
      </Teleport>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import AppHeader from '@/components/AppHeader.vue'
import { zonesApi } from '@/api/zones'

// --- State ---
const activeTab = ref<'zones' | 'intrusions'>('zones')
const loading = ref(false)
const zones = ref<any[]>([])
const intrusions = ref<any[]>([])
const selectedZoneId = ref<number | null>(null)
const showActiveOnly = ref(false)
const showCreateModal = ref(false)
const creating = ref(false)
const formError = ref('')

const mapContainer = ref<HTMLElement | null>(null)
let map: L.Map | null = null
let zoneLayers: L.LayerGroup = L.layerGroup()
let intrusionLayers: L.LayerGroup = L.layerGroup()

const form = ref({
  zone_name: '',
  zone_type: 'circle' as 'circle' | 'polygon',
  circleCenter: { lat: 39.9042, lng: 116.4074 },
  circleRadius: 1000,
  polygonText: '',
  min_altitude: 0,
  max_altitude: 10000,
  notification_enabled: false,
  notification_email: '',
})

const filteredZones = computed(() => {
  if (showActiveOnly.value) return zones.value.filter(z => z.is_active)
  return zones.value
})

// --- API ---
async function fetchZones() {
  loading.value = true
  try {
    const res = await zonesApi.list()
    zones.value = Array.isArray(res) ? res : (res as any).items ?? []
  } catch {
    zones.value = []
  } finally {
    loading.value = false
  }
}

async function fetchIntrusions() {
  try {
    const res = await zonesApi.getIntrusions({ limit: 200 })
    intrusions.value = (res as any).intrusions ?? (Array.isArray(res) ? res : [])
  } catch {
    intrusions.value = []
  }
}

async function createZone() {
  formError.value = ''
  if (!form.value.zone_name.trim()) {
    formError.value = '请输入区域名称'
    return
  }

  let coordinates: string
  if (form.value.zone_type === 'circle') {
    coordinates = JSON.stringify({
      type: 'circle',
      center: { lat: form.value.circleCenter.lat, lng: form.value.circleCenter.lng },
      radius: form.value.circleRadius,
    })
  } else {
    const vertices = form.value.polygonText
      .split('\n')
      .map(line => line.trim())
      .filter(Boolean)
      .map(line => {
        const [lat, lng] = line.split(',').map(Number)
        return { lat, lng }
      })
    if (vertices.length < 3) {
      formError.value = '多边形至少需要 3 个顶点'
      return
    }
    coordinates = JSON.stringify({ type: 'polygon', vertices })
  }

  creating.value = true
  try {
    await zonesApi.create({
      zone_name: form.value.zone_name,
      zone_type: form.value.zone_type,
      coordinates,
      min_altitude: form.value.min_altitude,
      max_altitude: form.value.max_altitude,
      is_active: true,
      notification_enabled: form.value.notification_enabled,
      notification_email: form.value.notification_email || undefined,
    } as any)
    showCreateModal.value = false
    resetForm()
    await fetchZones()
  } catch (e: any) {
    formError.value = e?.message || '创建失败'
  } finally {
    creating.value = false
  }
}

async function deleteZone(zone: any) {
  if (!confirm(`确定删除禁飞区「${zone.zone_name}」？`)) return
  try {
    await zonesApi.delete(zone.id)
    if (selectedZoneId.value === zone.id) selectedZoneId.value = null
    await fetchZones()
  } catch { /* ignore */ }
}

async function toggleZone(zone: any) {
  try {
    await zonesApi.toggleActive(zone.id, !zone.is_active)
    await fetchZones()
  } catch { /* ignore */ }
}

function openCreateModal() {
  resetForm()
  showCreateModal.value = true
}

function resetForm() {
  form.value = {
    zone_name: '',
    zone_type: 'circle',
    circleCenter: { lat: 39.9042, lng: 116.4074 },
    circleRadius: 1000,
    polygonText: '',
    min_altitude: 0,
    max_altitude: 10000,
    notification_enabled: false,
    notification_email: '',
  }
  formError.value = ''
}

// --- Map ---
function initMap() {
  if (!mapContainer.value || map) return
  map = L.map(mapContainer.value, { zoomControl: false }).setView([39.9042, 116.4074], 10)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap',
    maxZoom: 19,
  }).addTo(map)
  zoneLayers.addTo(map)
  intrusionLayers.addTo(map)
}

function renderZoneLayers() {
  zoneLayers.clearLayers()
  for (const zone of zones.value) {
    try {
      const coords = JSON.parse(zone.coordinates)
      let layer: L.Layer
      const style = {
        color: zone.is_active ? '#10b981' : '#94a3b8',
        weight: 2,
        fillColor: zone.is_active ? '#10b981' : '#94a3b8',
        fillOpacity: 0.15,
        dashArray: zone.is_active ? undefined : '5,5',
      }

      if (zone.zone_type === 'circle' && coords.center) {
        layer = L.circle([coords.center.lat, coords.center.lng], {
          ...style,
          radius: coords.radius,
        })
      } else if (zone.zone_type === 'polygon' && coords.vertices) {
        const latlngs = coords.vertices.map((v: any) => [v.lat, v.lng] as [number, number])
        layer = L.polygon(latlngs, style)
      } else {
        continue
      }

      ;(layer as any).bindPopup(`
        <strong>${zone.zone_name}</strong><br/>
        类型: ${zone.zone_type === 'circle' ? '圆形' : '多边形'}<br/>
        高度: ${zone.min_altitude}m - ${zone.max_altitude}m<br/>
        状态: ${zone.is_active ? '启用' : '禁用'}
      `)
      zoneLayers.addLayer(layer)

      // Highlight selected zone
      if (selectedZoneId.value === zone.id) {
        const highlight = {
          color: '#3b82f6',
          weight: 3,
          fillColor: '#3b82f6',
          fillOpacity: 0.25,
        }
        let hl: L.Layer
        if (zone.zone_type === 'circle' && coords.center) {
          hl = L.circle([coords.center.lat, coords.center.lng], { ...highlight, radius: coords.radius })
        } else {
          const latlngs = coords.vertices.map((v: any) => [v.lat, v.lng] as [number, number])
          hl = L.polygon(latlngs, highlight)
        }
        zoneLayers.addLayer(hl)
      }
    } catch { /* skip invalid coords */ }
  }
}

function renderIntrusionLayers() {
  intrusionLayers.clearLayers()
  for (const intrusion of intrusions.value) {
    const marker = L.circleMarker([intrusion.latitude, intrusion.longitude], {
      radius: 6,
      color: '#ef4444',
      fillColor: '#ef4444',
      fillOpacity: 0.8,
      weight: 2,
    })
    marker.bindPopup(`
      <strong>入侵告警</strong><br/>
      轨迹: ${intrusion.track_id}<br/>
      严重程度: ${severityLabel(intrusion.severity)}<br/>
      位置: ${intrusion.latitude.toFixed(4)}, ${intrusion.longitude.toFixed(4)}<br/>
      高度: ${intrusion.altitude?.toFixed(1) ?? '-'} m<br/>
      时间: ${formatTime(intrusion.timestamp)}
    `)
    intrusionLayers.addLayer(marker)
  }
}

function fitMapView() {
  if (!map) return
  const allBounds = L.latLngBounds([])
  zoneLayers.eachLayer(layer => {
    if ((layer as any).getBounds) allBounds.extend((layer as any).getBounds())
  })
  intrusionLayers.eachLayer(layer => {
    if ((layer as any).getLatLng) allBounds.extend((layer as any).getLatLng())
  })
  if (allBounds.isValid()) {
    map.fitBounds(allBounds, { padding: [40, 40] })
  }
}

function severityLabel(s: string) {
  return s === 'high' ? '高危' : s === 'medium' ? '中危' : '低危'
}

function formatTime(t: string) {
  if (!t) return '-'
  return new Date(t).toLocaleString('zh-CN')
}

// --- Watchers ---
watch(zones, () => {
  renderZoneLayers()
  fitMapView()
}, { deep: true })

watch(intrusions, () => {
  renderIntrusionLayers()
  fitMapView()
})

watch(selectedZoneId, () => {
  renderZoneLayers()
  // Pan to selected zone
  if (selectedZoneId.value && map) {
    const zone = zones.value.find(z => z.id === selectedZoneId.value)
    if (zone) {
      try {
        const coords = JSON.parse(zone.coordinates)
        if (coords.center) {
          map.setView([coords.center.lat, coords.center.lng], 12)
        } else if (coords.vertices?.length) {
          const latlngs = coords.vertices.map((v: any) => [v.lat, v.lng])
          map.fitBounds(latlngs, { padding: [40, 40] })
        }
      } catch { /* ignore */ }
    }
  }
})

watch(activeTab, async (tab) => {
  if (tab === 'intrusions') {
    await fetchIntrusions()
    zoneLayers.clearLayers()
  } else {
    intrusionLayers.clearLayers()
    renderZoneLayers()
  }
  nextTick(() => {
    map?.invalidateSize()
    fitMapView()
  })
})

// --- Lifecycle ---
onMounted(async () => {
  await fetchZones()
  nextTick(() => {
    initMap()
    renderZoneLayers()
    fitMapView()
  })
})

onUnmounted(() => {
  map?.remove()
  map = null
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

.header-actions {
  display: flex;
  gap: 0.5rem;
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

.zones-layout {
  display: grid;
  grid-template-columns: 400px 1fr;
  gap: 1rem;
  flex: 1;
  min-height: 0;
}

.zones-list {
  background: var(--bg-secondary);
  border-radius: 1rem;
  padding: 1rem;
  overflow-y: auto;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.list-header h2 {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
}

.toggle-switch {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8125rem;
  color: var(--text-secondary);
  cursor: pointer;
}

.toggle-switch input {
  display: none;
}

.toggle-slider {
  width: 2.5rem;
  height: 1.25rem;
  background: var(--bg-tertiary);
  border-radius: 1rem;
  position: relative;
  transition: all 0.3s;
}

.toggle-slider::before {
  content: '';
  position: absolute;
  width: 1rem;
  height: 1rem;
  background: white;
  border-radius: 50%;
  top: 0.125rem;
  left: 0.125rem;
  transition: all 0.3s;
}

.toggle-switch input:checked + .toggle-slider {
  background: var(--color-primary);
}

.toggle-switch input:checked + .toggle-slider::before {
  transform: translateX(1.25rem);
}

.zones-grid {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.zone-card {
  background: var(--bg-tertiary);
  border-radius: 0.75rem;
  padding: 1rem;
  border: 1px solid var(--border-color);
  transition: all 0.2s;
  cursor: pointer;
}

.zone-card:hover {
  border-color: var(--color-primary);
}

.zone-card.selected {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

.zone-card.inactive {
  opacity: 0.6;
}

.zone-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
}

.zone-name {
  margin: 0;
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--text-primary);
}

.zone-status {
  display: flex;
  gap: 0.5rem;
}

.status-badge {
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-badge.active {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.status-badge.inactive {
  background: rgba(148, 163, 184, 0.1);
  color: #94a3b8;
}

.severity-badge {
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.severity-badge.high {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

.severity-badge.medium {
  background: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
}

.severity-badge.low {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
}

.zone-type {
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  background: rgba(139, 92, 246, 0.1);
  color: #8b5cf6;
}

.zone-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.zone-detail {
  display: flex;
  justify-content: space-between;
  font-size: 0.8125rem;
}

.detail-label {
  color: var(--text-muted);
}

.detail-value {
  color: var(--text-primary);
  font-weight: 500;
}

.zone-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.375rem;
  padding: 0.5rem;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  font-size: 0.8125rem;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  background: var(--bg-primary);
  color: var(--text-primary);
}

.action-btn.danger:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  border-color: rgba(239, 68, 68, 0.3);
}

.action-btn svg {
  width: 0.875rem;
  height: 0.875rem;
}

.empty-zones {
  padding: 2rem 0;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem;
  text-align: center;
  color: var(--text-muted);
}

.empty-state svg {
  width: 3rem;
  height: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.empty-state p {
  margin: 0;
  font-size: 0.875rem;
}

.empty-desc {
  font-size: 0.8125rem;
}

.map-container {
  background: var(--bg-secondary);
  border-radius: 1rem;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.map-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.map-header h3 {
  margin: 0;
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--text-primary);
}

.map-controls {
  display: flex;
  gap: 0.25rem;
}

.map-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 0.375rem;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.map-btn:hover {
  background: var(--bg-primary);
  color: var(--text-primary);
}

.map-btn svg {
  width: 0.875rem;
  height: 0.875rem;
}

.map-viewport {
  flex: 1;
  min-height: 400px;
}

.map-legend {
  display: flex;
  gap: 1rem;
  padding: 0.75rem 1rem;
  border-top: 1px solid var(--border-color);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8125rem;
  color: var(--text-secondary);
}

.legend-color {
  width: 0.75rem;
  height: 0.75rem;
  border-radius: 0.125rem;
}

.legend-active {
  background: rgba(16, 185, 129, 0.3);
  border: 1px solid #10b981;
}

.legend-inactive {
  background: rgba(148, 163, 184, 0.3);
  border: 1px solid #94a3b8;
}

.legend-intrusion {
  background: rgba(239, 68, 68, 0.3);
  border: 1px solid #ef4444;
  border-radius: 50%;
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

.form-group {
  margin-bottom: 1rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-label {
  display: block;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.form-input {
  width: 100%;
  padding: 0.625rem 0.875rem;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  font-size: 0.875rem;
  background: var(--bg-secondary);
  color: var(--text-primary);
  transition: all 0.2s;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-textarea {
  resize: vertical;
  font-family: monospace;
}

.form-error {
  color: #ef4444;
  font-size: 0.8125rem;
  margin-top: 0.5rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--text-secondary);
  cursor: pointer;
}

.checkbox-label input {
  accent-color: var(--color-primary);
}

.type-selector {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.type-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.type-option:hover {
  background: var(--bg-primary);
  color: var(--text-primary);
}

.type-option.active {
  background: rgba(59, 130, 246, 0.1);
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.type-option svg {
  width: 1.5rem;
  height: 1.5rem;
}

.type-option span {
  font-size: 0.8125rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--border-color);
}

@media (max-width: 1024px) {
  .zones-layout {
    grid-template-columns: 1fr;
    grid-template-rows: 1fr 1fr;
  }

  .zones-list {
    max-height: 300px;
  }

  .map-viewport {
    min-height: 300px;
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

  .type-selector {
    grid-template-columns: 1fr;
  }

  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
