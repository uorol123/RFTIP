<template>
  <div class="page">
    <AppHeader />
    <div class="page-content">
      <div class="page-header">
        <div>
          <h1 class="page-title">禁飞区管理</h1>
          <p class="page-subtitle">配置和监控受限空域区域</p>
        </div>
        <button class="btn btn-primary" @click="showCreateModal = true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          创建禁飞区
        </button>
      </div>

      <div class="zones-layout">
        <!-- 禁飞区列表 -->
        <div class="zones-list">
          <div class="list-header">
            <h2>禁飞区列表 ({{ zones.length }})</h2>
            <label class="toggle-switch">
              <input type="checkbox" v-model="showActiveOnly" />
              <span class="toggle-slider"></span>
              <span class="toggle-label">仅显示启用</span>
            </label>
          </div>

          <div class="zones-grid">
            <div v-for="zone in filteredZones" :key="zone.id" class="zone-card" :class="{ inactive: !zone.is_active }">
              <div class="zone-header">
                <h3 class="zone-name">{{ zone.name }}</h3>
                <div class="zone-status">
                  <span :class="['status-badge', zone.is_active ? 'active' : 'inactive']">
                    {{ zone.is_active ? '启用' : '禁用' }}
                  </span>
                  <span class="zone-type">{{ zone.type === 'circle' ? '圆形' : '多边形' }}</span>
                </div>
              </div>
              <div class="zone-info">
                <div class="zone-detail">
                  <span class="detail-label">高度范围:</span>
                  <span class="detail-value">{{ zone.min_alt }}m - {{ zone.max_alt }}m</span>
                </div>
                <div class="zone-detail">
                  <span class="detail-label">预警通知:</span>
                  <span class="detail-value">{{ zone.notification ? '已启用' : '已禁用' }}</span>
                </div>
              </div>
              <div class="zone-actions">
                <button class="action-btn" title="编辑">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9m0 0l8-8m-8 8v2.031" />
                  </svg>
                </button>
                <button class="action-btn" title="删除">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 011-1h4a1 1 0 011 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </div>
            <div v-if="filteredZones.length === 0" class="empty-zones">
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
        </div>

        <!-- 地图区域 -->
        <div class="map-container">
          <div class="map-header">
            <h3>地图视图</h3>
            <div class="map-controls">
              <button class="map-btn" title="放大">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v6m3-3h-6" />
                </svg>
              </button>
              <button class="map-btn" title="缩小">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM13 10H7" />
                </svg>
              </button>
              <button class="map-btn" title="适应视图">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 0h-4" />
                </svg>
              </button>
            </div>
          </div>
          <div class="map-viewport">
            <div class="empty-map">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
              </svg>
              <p>地图区域</p>
              <p class="map-hint">创建禁飞区后将在此处显示</p>
            </div>
          </div>
          <div class="map-legend">
            <div class="legend-item">
              <div class="legend-color legend-active"></div>
              <span>启用区域</span>
            </div>
            <div class="legend-item">
              <div class="legend-color legend-inactive"></div>
              <span>禁用区域</span>
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
                <label class="form-label">区域名称</label>
                <input type="text" class="form-input" placeholder="例如：机场限制区" />
              </div>
              <div class="form-group">
                <label class="form-label">区域类型</label>
                <div class="type-selector">
                  <button class="type-option active" @click="zoneType = 'circle'">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <circle cx="12" cy="12" r="8" />
                    </svg>
                    <span>圆形区域</span>
                  </button>
                  <button class="type-option" @click="zoneType = 'polygon'">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                    </svg>
                    <span>多边形区域</span>
                  </button>
                </div>
              </div>
              <div class="form-row">
                <div class="form-group">
                  <label class="form-label">最低高度 (米)</label>
                  <input type="number" class="form-input" placeholder="0" />
                </div>
                <div class="form-group">
                  <label class="form-label">最高高度 (米)</label>
                  <input type="number" class="form-input" placeholder="1000" />
                </div>
              </div>
              <div class="form-group">
                <label class="checkbox-label">
                  <input type="checkbox" v-model="enableNotification" />
                  <span>启用预警通知</span>
                </label>
              </div>
              <div class="form-group" v-if="enableNotification">
                <label class="form-label">通知邮箱</label>
                <input type="email" class="form-input" placeholder="example@email.com" />
              </div>
            </div>
            <div class="modal-footer">
              <button class="btn btn-secondary" @click="showCreateModal = false">取消</button>
              <button class="btn btn-primary">创建</button>
            </div>
          </div>
        </div>
      </Teleport>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import AppHeader from '@/components/AppHeader.vue'

const showCreateModal = ref(false)
const showActiveOnly = ref(false)
const zoneType = ref('circle')
const enableNotification = ref(false)

const zones = ref([
  { id: 1, name: '机场限制区', type: 'circle', min_alt: 0, max_alt: 500, is_active: true, notification: true },
  { id: 2, name: '军事禁区', type: 'polygon', min_alt: 0, max_alt: 10000, is_active: true, notification: false },
  { id: 3, name: '临时限制区', type: 'circle', min_alt: 100, max_alt: 300, is_active: false, notification: false },
])

const filteredZones = computed(() => {
  if (showActiveOnly.value) {
    return zones.value.filter(z => z.is_active)
  }
  return zones.value
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
}

.zone-card:hover {
  border-color: var(--color-primary);
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

.empty-map {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
}

.empty-map svg {
  width: 4rem;
  height: 4rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.empty-map p {
  margin: 0.25rem 0;
  font-size: 0.875rem;
}

.map-hint {
  font-size: 0.8125rem;
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
}

.form-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
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
