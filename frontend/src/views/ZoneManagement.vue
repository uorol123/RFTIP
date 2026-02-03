<template>
  <div class="zone-management">
    <div class="page-header">
      <div>
        <h1 class="page-title">No-Fly Zone Management</h1>
        <p class="page-subtitle">Configure and monitor restricted airspace zones</p>
      </div>
      <button class="btn btn-primary" @click="showCreateModal = true">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Create Zone
      </button>
    </div>

    <div class="zones-layout">
      <!-- Zone List -->
      <div class="zones-list">
        <div class="list-header">
          <h2>Zones ({{ zones.length }})</h2>
          <div class="filter-toggle">
            <label class="toggle-switch">
              <input type="checkbox" v-model="showActiveOnly" />
              <span class="toggle-slider"></span>
              <span class="toggle-label">Active only</span>
            </label>
          </div>
        </div>

        <div v-if="loading" class="list-loading">
          <Loading :fullscreen="false" message="Loading zones..." />
        </div>

        <div v-else-if="!filteredZones.length" class="list-empty">
          <EmptyState
            title="No zones found"
            description="Create a no-fly zone to get started"
          />
        </div>

        <div v-else class="zone-cards">
          <div
            v-for="zone in filteredZones"
            :key="zone.id"
            :class="['zone-card', { active: selectedZone?.id === zone.id }]"
            @click="selectZone(zone)"
          >
            <div class="zone-card-header">
              <div class="zone-type-badge" :class="`type-${zone.zone_type}`">
                {{ zone.zone_type === 'circle' ? 'Circle' : 'Polygon' }}
              </div>
              <div :class="['zone-status', zone.is_active ? 'status-active' : 'status-inactive']">
                {{ zone.is_active ? 'Active' : 'Inactive' }}
              </div>
            </div>
            <h3 class="zone-name">{{ zone.name }}</h3>
            <div class="zone-meta">
              <div class="meta-item">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                  />
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                  />
                </svg>
                {{ zone.min_altitude }}m - {{ zone.max_altitude }}m
              </div>
              <div v-if="zone.email_alerts" class="meta-item">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                  />
                </svg>
                Email alerts enabled
              </div>
            </div>
            <div class="zone-card-actions">
              <button
                class="action-btn"
                @click.stop="zoomToZone(zone)"
                title="Zoom to zone"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7"
                  />
                </svg>
              </button>
              <button
                class="action-btn"
                @click.stop="editZone(zone)"
                title="Edit zone"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                  />
                </svg>
              </button>
              <button
                class="action-btn action-btn-danger"
                @click.stop="confirmDelete(zone)"
                title="Delete zone"
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
          </div>
        </div>
      </div>

      <!-- Map -->
      <div class="zones-map">
        <div id="zone-map" class="map-container"></div>

        <!-- Map Controls -->
        <div class="map-controls">
          <button
            class="map-btn"
            @click="detectIntrusions"
            :disabled="!selectedZone || detecting"
            title="Detect intrusions"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
            Detect
          </button>
          <button class="map-btn" @click="refreshMap" title="Refresh map">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
              />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showCreateModal" class="modal-overlay" @click="closeModal">
          <div class="modal-content modal-large" @click.stop>
            <div class="modal-header">
              <h2 class="modal-title">
                {{ editingZone ? 'Edit Zone' : 'Create No-Fly Zone' }}
              </h2>
              <button class="modal-close" @click="closeModal">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div class="modal-body">
              <div class="form-grid">
                <div class="form-group">
                  <label class="form-label">Zone Name</label>
                  <input
                    v-model="zoneForm.name"
                    type="text"
                    class="form-input"
                    placeholder="Enter zone name"
                  />
                </div>

                <div class="form-group">
                  <label class="form-label">Zone Type</label>
                  <select v-model="zoneForm.zone_type" class="form-select">
                    <option value="circle">Circle</option>
                    <option value="polygon">Polygon</option>
                  </select>
                </div>

                <div class="form-group">
                  <label class="form-label">Min Altitude (meters)</label>
                  <input
                    v-model.number="zoneForm.min_altitude"
                    type="number"
                    min="0"
                    class="form-input"
                  />
                </div>

                <div class="form-group">
                  <label class="form-label">Max Altitude (meters)</label>
                  <input
                    v-model.number="zoneForm.max_altitude"
                    type="number"
                    min="0"
                    class="form-input"
                  />
                </div>

                <div class="form-group form-group-full">
                  <label class="form-label">Coordinates (JSON array of [[lon, lat], ...])</label>
                  <textarea
                    v-model="coordinatesJson"
                    class="form-textarea"
                    rows="3"
                    placeholder='[[116.3974, 39.9093], [116.4074, 39.9193], ...]'
                  ></textarea>
                </div>

                <div class="form-group">
                  <label class="form-label flex items-center gap-2">
                    <input type="checkbox" v-model="zoneForm.is_active" />
                    <span>Active</span>
                  </label>
                </div>

                <div class="form-group">
                  <label class="form-label flex items-center gap-2">
                    <input type="checkbox" v-model="zoneForm.email_alerts" />
                    <span>Email Alerts</span>
                  </label>
                </div>

                <div v-if="zoneForm.email_alerts" class="form-group form-group-full">
                  <label class="form-label">Alert Emails (comma separated)</label>
                  <input
                    v-model="alertEmailsString"
                    type="text"
                    class="form-input"
                    placeholder="email1@example.com, email2@example.com"
                  />
                </div>
              </div>
            </div>
            <div class="modal-footer">
              <button class="btn btn-secondary" @click="closeModal">Cancel</button>
              <button class="btn btn-primary" @click="saveZone">
                {{ editingZone ? 'Save Changes' : 'Create Zone' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Delete Confirmation -->
    <ConfirmDialog
      v-model:show="showDeleteDialog"
      title="Delete Zone"
      :message="`Are you sure you want to delete '${zoneToDelete?.name}'? This action cannot be undone.`"
      type="danger"
      confirm-text="Delete"
      @confirm="handleDelete"
    />

    <!-- Intrusion Results -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showIntrusions" class="modal-overlay" @click="showIntrusions = false">
          <div class="modal-content" @click.stop>
            <div class="modal-header">
              <h2 class="modal-title">Intrusion Detection Results</h2>
              <button class="modal-close" @click="showIntrusions = false">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div class="modal-body">
              <div v-if="intrusions.length === 0" class="text-center py-8">
                <p class="text-muted">No intrusions detected</p>
              </div>
              <div v-else class="intrusions-list">
                <div v-for="intrusion in intrusions" :key="intrusion.id" class="intrusion-item">
                  <div class="intrusion-header">
                    <span class="intrusion-zone">{{ intrusion.zone_name }}</span>
                    <span class="intrusion-time">{{ formatTime(intrusion.timestamp) }}</span>
                  </div>
                  <div class="intrusion-details">
                    <span>Track: {{ intrusion.track_id }}</span>
                    <span>Duration: {{ formatDuration(intrusion.duration_seconds) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import L from 'leaflet'
import { useAppStore } from '@/stores/app'
import { zonesApi } from '@/api'
import type { NoFlyZone, Intrusion, CreateZoneRequest } from '@/api/types'
import EmptyState from '@/components/EmptyState.vue'
import Loading from '@/components/Loading.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'

const appStore = useAppStore()

const loading = ref(false)
const detecting = ref(false)

const zones = ref<NoFlyZone[]>([])
const selectedZone = ref<NoFlyZone | null>(null)
const showActiveOnly = ref(false)

const showCreateModal = ref(false)
const showDeleteDialog = ref(false)
const showIntrusions = ref(false)
const editingZone = ref<NoFlyZone | null>(null)
const zoneToDelete = ref<NoFlyZone | null>(null)

const intrusions = ref<Intrusion[]>([])

const zoneForm = ref<CreateZoneRequest>({
  name: '',
  zone_type: 'circle',
  coordinates: [],
  min_altitude: 0,
  max_altitude: 1000,
  is_active: true,
  email_alerts: false,
  alert_emails: [],
})

const alertEmailsString = ref('')

const coordinatesJson = computed({
  get: () => JSON.stringify(zoneForm.value.coordinates || []),
  set: (value: string) => {
    try {
      zoneForm.value.coordinates = JSON.parse(value)
    } catch {
      // Invalid JSON, ignore
    }
  },
})

const filteredZones = computed(() => {
  if (showActiveOnly.value) {
    return zones.value.filter(z => z.is_active)
  }
  return zones.value
})

// Map setup
let map: L.Map | null = null
let zoneLayer: L.GeoJSON | null = null

const initMap = () => {
  map = L.map('zone-map').setView([39.9042, 116.4074], 10)

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors',
  }).addTo(map)

  zoneLayer = L.geoJSON(undefined, {
    style: (feature) => ({
      color: feature?.properties?.isActive ? '#ef4444' : '#94a3b8',
      fillColor: feature?.properties?.isActive ? 'rgba(239, 68, 68, 0.2)' : 'rgba(148, 163, 184, 0.2)',
      fillOpacity: 0.5,
      weight: 2,
    }),
  }).addTo(map)
}

const loadZones = async () => {
  loading.value = true
  try {
    const response = await zonesApi.list()
    zones.value = response.items
    updateMapZones()
  } catch (error: any) {
    appStore.error(error.message || 'Failed to load zones')
  } finally {
    loading.value = false
  }
}

const updateMapZones = () => {
  if (!zoneLayer) return

  const features = zones.value.map(zone => {
    const coordinates = zone.coordinates.map((coord: number[]) => [coord[1], coord[0]] as [number, number])

    let geometry: GeoJSON.Polygon | GeoJSON.Point
    if (zone.zone_type === 'circle') {
      geometry = {
        type: 'Point',
        coordinates: [coordinates[0][1], coordinates[0][0]],
      }
    } else {
      geometry = {
        type: 'Polygon',
        coordinates: [coordinates as [number, number][]],
      }
    }

    return {
      type: 'Feature' as const,
      properties: {
        id: zone.id,
        name: zone.name,
        isActive: zone.is_active,
      },
      geometry,
    }
  })

  zoneLayer.addData(features)
}

const selectZone = (zone: NoFlyZone) => {
  selectedZone.value = zone
  zoomToZone(zone)
}

const zoomToZone = (zone: NoFlyZone) => {
  if (!map) return

  const coords = zone.coordinates.map((c: number[]) => [c[1], c[0]] as [number, number])
  const bounds = L.latLngBounds(coords)
  map.fitBounds(bounds, { padding: [50, 50] })
}

const editZone = (zone: NoFlyZone) => {
  editingZone.value = zone
  zoneForm.value = {
    name: zone.name,
    zone_type: zone.zone_type,
    coordinates: zone.coordinates,
    min_altitude: zone.min_altitude,
    max_altitude: zone.max_altitude,
    is_active: zone.is_active,
    email_alerts: zone.email_alerts,
    alert_emails: zone.alert_emails,
  }
  alertEmailsString.value = zone.alert_emails?.join(', ') || ''
  showCreateModal.value = true
}

const closeModal = () => {
  showCreateModal.value = false
  editingZone.value = null
  zoneForm.value = {
    name: '',
    zone_type: 'circle',
    coordinates: [],
    min_altitude: 0,
    max_altitude: 1000,
    is_active: true,
    email_alerts: false,
    alert_emails: [],
  }
  alertEmailsString.value = ''
}

const saveZone = async () => {
  try {
    zoneForm.value.alert_emails = alertEmailsString.value
      .split(',')
      .map(e => e.trim())
      .filter(e => e)

    if (editingZone.value) {
      await zonesApi.update(editingZone.value.id, zoneForm.value)
      appStore.success('Zone updated successfully')
    } else {
      await zonesApi.create(zoneForm.value)
      appStore.success('Zone created successfully')
    }

    closeModal()
    loadZones()
  } catch (error: any) {
    appStore.error(error.message || 'Failed to save zone')
  }
}

const confirmDelete = (zone: NoFlyZone) => {
  zoneToDelete.value = zone
  showDeleteDialog.value = true
}

const handleDelete = async () => {
  if (!zoneToDelete.value) return

  try {
    await zonesApi.delete(zoneToDelete.value.id)
    appStore.success('Zone deleted successfully')
    showDeleteDialog.value = false
    loadZones()
  } catch (error: any) {
    appStore.error(error.message || 'Failed to delete zone')
  }
}

const detectIntrusions = async () => {
  if (!selectedZone.value) return

  detecting.value = true
  try {
    const response = await zonesApi.detectIntrusions({ zone_id: selectedZone.value.id })
    intrusions.value = response.intrusions
    showIntrusions.value = true

    if (response.intrusions.length > 0) {
      appStore.warning(`Detected ${response.intrusions.length} intrusion(s)`)
    } else {
      appStore.success('No intrusions detected')
    }
  } catch (error: any) {
    appStore.error(error.message || 'Failed to detect intrusions')
  } finally {
    detecting.value = false
  }
}

const refreshMap = () => {
  if (zoneLayer) {
    zoneLayer.clearLayers()
    updateMapZones()
  }
}

const formatTime = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleString()
}

const formatDuration = (seconds: number): string => {
  const mins = Math.floor(seconds / 60)
  if (mins < 60) return `${mins}m`
  const hours = Math.floor(mins / 60)
  return `${hours}h ${mins % 60}m`
}

onMounted(() => {
  initMap()
  loadZones()
})

onUnmounted(() => {
  if (map) {
    map.remove()
    map = null
  }
})
</script>

<style scoped>
.zone-management {
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

.zones-layout {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.zones-list {
  width: 350px;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-color, rgba(255, 255, 255, 0.1));
  display: flex;
  flex-direction: column;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color, rgba(255, 255, 255, 0.1));
}

.list-header h2 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.toggle-switch {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.toggle-switch input {
  display: none;
}

.toggle-slider {
  position: relative;
  width: 36px;
  height: 20px;
  background: var(--bg-tertiary);
  border-radius: 20px;
  transition: background 0.3s;
}

.toggle-slider::before {
  content: '';
  position: absolute;
  top: 2px;
  left: 2px;
  width: 16px;
  height: 16px;
  background: white;
  border-radius: 50%;
  transition: transform 0.3s;
}

.toggle-switch input:checked + .toggle-slider {
  background: var(--color-primary);
}

.toggle-switch input:checked + .toggle-slider::before {
  transform: translateX(16px);
}

.toggle-label {
  font-size: 0.8125rem;
  color: var(--text-secondary);
}

.list-loading,
.list-empty {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.zone-cards {
  flex: 1;
  overflow-y: auto;
  padding: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.zone-card {
  padding: 1rem;
  border-radius: 0.75rem;
  background: var(--bg-tertiary);
  cursor: pointer;
  transition: all 0.2s;
}

.zone-card:hover {
  background: var(--bg-primary);
}

.zone-card.active {
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid var(--color-primary);
}

.zone-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.zone-type-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.6875rem;
  font-weight: 600;
  text-transform: uppercase;
}

.type-circle {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.type-polygon {
  background: rgba(139, 92, 246, 0.1);
  color: #8b5cf6;
}

.zone-status {
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.6875rem;
  font-weight: 500;
}

.status-active {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.status-inactive {
  background: rgba(148, 163, 184, 0.1);
  color: #94a3b8;
}

.zone-name {
  margin: 0 0 0.75rem;
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--text-primary);
}

.zone-meta {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
  margin-bottom: 0.75rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8125rem;
  color: var(--text-secondary);
}

.meta-item svg {
  width: 0.875rem;
  height: 0.875rem;
}

.zone-card-actions {
  display: flex;
  gap: 0.375rem;
}

.action-btn {
  flex: 1;
  padding: 0.5rem;
  border: none;
  background: var(--bg-secondary);
  color: var(--text-muted);
  cursor: pointer;
  border-radius: 0.375rem;
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

.zones-map {
  flex: 1;
  position: relative;
}

.map-container {
  width: 100%;
  height: 100%;
}

.map-controls {
  position: absolute;
  top: 1rem;
  right: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.map-btn {
  width: 2.5rem;
  height: 2.5rem;
  padding: 0;
  border: none;
  border-radius: 0.5rem;
  background: var(--bg-secondary);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  color: var(--text-primary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.map-btn:hover:not(:disabled) {
  background: var(--color-primary);
  color: white;
}

.map-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.map-btn svg {
  width: 1rem;
  height: 1rem;
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
  max-width: 500px;
  border-radius: 1rem;
  background: var(--bg-secondary);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  overflow: hidden;
}

.modal-large {
  max-width: 600px;
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
}

.modal-close:hover {
  background: var(--bg-tertiary);
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

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-group-full {
  grid-column: 1 / -1;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.form-label {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.form-input,
.form-select,
.form-textarea {
  padding: 0.625rem 0.875rem;
  border: 1px solid var(--border-color, rgba(255, 255, 255, 0.1));
  border-radius: 0.5rem;
  background: var(--bg-tertiary);
  color: var(--text-primary);
  font-size: 0.875rem;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: var(--color-primary);
}

.intrusions-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.intrusion-item {
  padding: 0.75rem;
  border-radius: 0.5rem;
  background: var(--bg-tertiary);
}

.intrusion-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.375rem;
}

.intrusion-zone {
  font-weight: 600;
  color: var(--text-primary);
}

.intrusion-time {
  font-size: 0.8125rem;
  color: var(--text-muted);
}

.intrusion-details {
  display: flex;
  gap: 1rem;
  font-size: 0.8125rem;
  color: var(--text-secondary);
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
  .zones-layout {
    flex-direction: column;
  }

  .zones-list {
    width: 100%;
    max-height: 40vh;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
