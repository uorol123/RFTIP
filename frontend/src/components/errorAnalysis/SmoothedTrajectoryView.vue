<template>
  <div class="smoothed-trajectory-view">
    <!-- 概览信息 -->
    <div class="overview-section">
      <h3 class="section-title">平滑轨迹分析结果</h3>
      <div class="overview-cards">
        <div class="overview-card" v-for="traj in trajectories" :key="traj.id">
          <div class="card-header">
            <span class="station-name">{{ traj.station_name }}</span>
            <span class="batch-id">批次: {{ traj.batch_id }}</span>
          </div>
          <div class="card-stats">
            <div class="stat">
              <span class="stat-label">轨迹点数</span>
              <span class="stat-value">{{ traj.point_count }}</span>
            </div>
            <div class="stat">
              <span class="stat-label">纬度RMSE</span>
              <span class="stat-value">{{ ((traj.rmse_lat ?? 0) * 111000).toFixed(2) }} m</span>
            </div>
            <div class="stat">
              <span class="stat-label">距离RMSE</span>
              <span class="stat-value">{{ ((traj.rmse_lon ?? 0) * 111000).toFixed(2) }} m</span>
            </div>
            <div class="stat">
              <span class="stat-label">高度RMSE</span>
              <span class="stat-value">{{ (traj.rmse_alt ?? 0).toFixed(2) }} m</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 控制面板 -->
    <div class="control-section">
      <div class="control-group">
        <label class="checkbox-label">
          <input type="checkbox" v-model="showOriginal" />
          <span class="checkbox-custom original"></span>
          显示原始轨迹
        </label>
      </div>
      <div class="control-group">
        <label class="checkbox-label">
          <input type="checkbox" v-model="showSmoothed" />
          <span class="checkbox-custom smoothed"></span>
          显示平滑轨迹
        </label>
      </div>
      <div class="control-group">
        <label class="checkbox-label">
          <input type="checkbox" v-model="showDiff" />
          <span class="checkbox-custom diff"></span>
          显示偏差向量
        </label>
      </div>
    </div>

    <!-- 轨迹对比图 -->
    <div class="trajectory-map" ref="mapContainer">
      <svg :width="mapWidth" :height="mapHeight" class="trajectory-svg">
        <!-- 坐标系背景 -->
        <defs>
          <pattern id="grid" width="50" height="50" patternUnits="userSpaceOnUse">
            <path d="M 50 0 L 0 0 0 50" fill="none" stroke="#e5e7eb" stroke-width="0.5"/>
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#grid)" />

        <!-- 原始轨迹（仅显示点） -->
        <circle
          v-if="showOriginal && selectedTraj"
          v-for="(point, i) in selectedTraj.original_trajectory"
          :key="'orig-' + i"
          :cx="getPointX(point.longitude)"
          :cy="getPointY(point.latitude)"
          r="3"
          fill="#ef4444"
          fill-opacity="0.6"
        />

        <!-- 平滑轨迹 -->
        <path
          v-if="showSmoothed && selectedTraj"
          :d="getSmoothedPath(selectedTraj)"
          fill="none"
          stroke="#3b82f6"
          stroke-width="2.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        />

        <!-- 偏差向量 -->
        <g v-if="showDiff && selectedTraj">
          <line
            v-for="(point, i) in getDiffVectors(selectedTraj)"
            :key="i"
            :x1="point.x1" :y1="point.y1"
            :x2="point.x2" :y2="point.y2"
            stroke="#10b981"
            stroke-width="1"
            stroke-opacity="0.5"
          />
        </g>

        <!-- 端点标记 -->
        <g v-if="selectedTraj">
          <!-- 原始轨迹起点 -->
          <circle
            v-if="showOriginal && selectedTraj.original_trajectory.length > 0 && selectedTraj.original_trajectory[0]"
            :cx="getPointX(selectedTraj.original_trajectory[0].longitude)"
            :cy="getPointY(selectedTraj.original_trajectory[0].latitude)"
            r="4"
            fill="#ef4444"
          />
          <!-- 平滑轨迹起点 -->
          <circle
            v-if="showSmoothed && selectedTraj.smoothed_trajectory.length > 0 && selectedTraj.smoothed_trajectory[0]"
            :cx="getPointX(selectedTraj.smoothed_trajectory[0].longitude)"
            :cy="getPointY(selectedTraj.smoothed_trajectory[0].latitude)"
            r="4"
            fill="#3b82f6"
          />
        </g>
      </svg>

      <!-- 图例 -->
      <div class="map-legend">
        <div class="legend-item">
          <span class="legend-dot original"></span>
          <span>原始轨迹</span>
        </div>
        <div class="legend-item">
          <span class="legend-line smoothed"></span>
          <span>平滑轨迹</span>
        </div>
        <div class="legend-item">
          <span class="legend-line diff"></span>
          <span>偏差向量</span>
        </div>
      </div>
    </div>

    <!-- 轨迹选择 -->
    <div class="trajectory-selector" v-if="trajectories.length > 1">
      <span class="selector-label">选择轨迹:</span>
      <div class="selector-buttons">
        <button
          v-for="traj in trajectories"
          :key="traj.id"
          :class="['selector-btn', { active: selectedTraj?.id === traj.id }]"
          @click="selectedTraj = traj"
        >
          {{ traj.station_name }} - {{ traj.batch_id }}
        </button>
      </div>
    </div>

    <!-- 详细数据表 -->
    <div class="data-table-section">
      <h4 class="table-title">轨迹点详情</h4>
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>序号</th>
              <th>原始经度</th>
              <th>原始纬度</th>
              <th>平滑经度</th>
              <th>平滑纬度</th>
              <th>经度偏差 (m)</th>
              <th>纬度偏差 (m)</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(point, i) in displayedPoints" :key="i">
              <td>{{ i + 1 }}</td>
              <td>{{ point.orig.longitude.toFixed(6) }}</td>
              <td>{{ point.orig.latitude.toFixed(6) }}</td>
              <td>{{ point.smooth.longitude.toFixed(6) }}</td>
              <td>{{ point.smooth.latitude.toFixed(6) }}</td>
              <td>{{ ((point.orig.longitude - point.smooth.longitude) * 111000).toFixed(2) }}</td>
              <td>{{ ((point.orig.latitude - point.smooth.latitude) * 111000).toFixed(2) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="selectedTraj && selectedTraj.point_count > 20" class="table-pagination">
        <button class="page-btn" :disabled="tablePage <= 1" @click="tablePage--">上一页</button>
        <span class="page-info">第 {{ tablePage }} / {{ tablePages }} 页</span>
        <button class="page-btn" :disabled="tablePage >= tablePages" @click="tablePage++">下一页</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { SmoothedTrajectoryResult } from '@/types/errorAnalysis'

interface Props {
  trajectories: SmoothedTrajectoryResult[]
}

const props = defineProps<Props>()

const showOriginal = ref(true)
const showSmoothed = ref(true)
const showDiff = ref(false)
const selectedTraj = ref<SmoothedTrajectoryResult | null>(null)
const tablePage = ref(1)
const tablePageSize = 20
const mapWidth = 800
const mapHeight = 500

// 计算包围盒
const bounds = computed(() => {
  if (!selectedTraj.value) return null

  const orig = selectedTraj.value.original_trajectory
  const smooth = selectedTraj.value.smoothed_trajectory

  let minLon = Infinity, maxLon = -Infinity
  let minLat = Infinity, maxLat = -Infinity

  const allPoints = [...orig, ...smooth]
  for (const p of allPoints) {
    if (p.longitude < minLon) minLon = p.longitude
    if (p.longitude > maxLon) maxLon = p.longitude
    if (p.latitude < minLat) minLat = p.latitude
    if (p.latitude > maxLat) maxLat = p.latitude
  }

  // 添加边距
  const lonMargin = (maxLon - minLon) * 0.1 || 0.001
  const latMargin = (maxLat - minLat) * 0.1 || 0.001

  return {
    minLon: minLon - lonMargin,
    maxLon: maxLon + lonMargin,
    minLat: minLat - latMargin,
    maxLat: maxLat + latMargin,
  }
})

// 坐标转换
function getPointX(lon: number): number {
  if (!bounds.value) return 0
  const ratio = (lon - bounds.value.minLon) / (bounds.value.maxLon - bounds.value.minLon)
  return ratio * mapWidth
}

function getPointY(lat: number): number {
  if (!bounds.value) return 0
  // 纬度反向（纬度增大会上移）
  const ratio = (bounds.value.maxLat - lat) / (bounds.value.maxLat - bounds.value.minLat)
  return ratio * mapHeight
}

// 生成 SVG 路径
function getOriginalPath(traj: SmoothedTrajectoryResult): string {
  const points = traj.original_trajectory
  if (points.length === 0) return ''

  return points.map((p, i) => {
    const x = getPointX(p.longitude)
    const y = getPointY(p.latitude)
    return `${i === 0 ? 'M' : 'L'} ${x} ${y}`
  }).join(' ')
}

function getSmoothedPath(traj: SmoothedTrajectoryResult): string {
  const points = traj.smoothed_trajectory
  if (points.length === 0) return ''

  return points.map((p, i) => {
    const x = getPointX(p.longitude)
    const y = getPointY(p.latitude)
    return `${i === 0 ? 'M' : 'L'} ${x} ${y}`
  }).join(' ')
}

// 生成偏差向量
function getDiffVectors(traj: SmoothedTrajectoryResult) {
  const vectors = []
  const orig = traj.original_trajectory
  const smooth = traj.smoothed_trajectory
  const len = Math.min(orig.length, smooth.length)

  for (let i = 0; i < len; i++) {
    const o = orig[i]
    const s = smooth[i]
    if (!o || !s) continue

    const x1 = getPointX(o.longitude)
    const y1 = getPointY(o.latitude)
    const x2 = getPointX(s.longitude)
    const y2 = getPointY(s.latitude)

    vectors.push({ x1, y1, x2, y2 })
  }

  return vectors
}

// 配对的轨迹点详情
interface DisplayPoint {
  orig: { longitude: number; latitude: number; altitude: number | null }
  smooth: { longitude: number; latitude: number; altitude: number | null }
}

const displayedPoints = computed((): DisplayPoint[] => {
  if (!selectedTraj.value) return []

  const orig = selectedTraj.value.original_trajectory
  const smooth = selectedTraj.value.smoothed_trajectory
  const len = Math.min(orig.length, smooth.length, tablePage.value * tablePageSize)

  const points: DisplayPoint[] = []
  for (let i = (tablePage.value - 1) * tablePageSize; i < len; i++) {
    const o = orig[i]
    const s = smooth[i]
    if (o && s) {
      points.push({ orig: o, smooth: s })
    }
  }

  return points
})

const tablePages = computed(() => {
  if (!selectedTraj.value) return 1
  return Math.ceil(selectedTraj.value.point_count / tablePageSize)
})

// 自动选择第一个轨迹
watch(() => props.trajectories, (newTrajs) => {
  if (newTrajs.length > 0 && !selectedTraj.value) {
    const firstTraj = newTrajs[0]
    if (firstTraj) {
      selectedTraj.value = firstTraj
    }
  }
}, { immediate: true })

watch(selectedTraj, () => {
  tablePage.value = 1
})
</script>

<style scoped>
.smoothed-trajectory-view {
  padding: 1.5rem;
  background: var(--bg-secondary);
  border-radius: 0.75rem;
}

.section-title {
  margin: 0 0 1rem 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
}

/* 概览卡片 */
.overview-section {
  margin-bottom: 1.5rem;
}

.overview-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
}

.overview-card {
  padding: 1rem;
  background: var(--bg-primary);
  border-radius: 0.5rem;
  border: 1px solid var(--border-color);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--border-color);
}

.station-name {
  font-weight: 600;
  color: var(--text-primary);
}

.batch-id {
  font-size: 0.8125rem;
  color: var(--text-muted);
}

.card-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}

.stat {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stat-label {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.stat-value {
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--text-primary);
}

/* 控制面板 */
.control-section {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: var(--bg-primary);
  border-radius: 0.5rem;
}

.control-group {
  display: flex;
  align-items: center;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.checkbox-label input {
  display: none;
}

.checkbox-custom {
  width: 1rem;
  height: 1rem;
  border: 2px solid var(--border-color);
  border-radius: 0.25rem;
  transition: all 0.2s;
}

.checkbox-custom.original {
  border-color: #ef4444;
  background: #ef4444;
}

.checkbox-custom.smoothed {
  border-color: #3b82f6;
  background: #3b82f6;
}

.checkbox-custom.diff {
  border-color: #10b981;
  background: #10b981;
}

.checkbox-label input:checked + .checkbox-custom {
  background: currentColor;
}

.checkbox-label input:checked + .checkbox-custom.original {
  background: #ef4444;
}

.checkbox-label input:checked + .checkbox-custom.smoothed {
  background: #3b82f6;
}

.checkbox-label input:checked + .checkbox-custom.diff {
  background: #10b981;
}

/* 轨迹图 */
.trajectory-map {
  position: relative;
  background: var(--bg-primary);
  border-radius: 0.5rem;
  border: 1px solid var(--border-color);
  overflow: hidden;
  margin-bottom: 1rem;
}

.trajectory-svg {
  display: block;
  width: 100%;
  height: auto;
}

.map-legend {
  position: absolute;
  bottom: 1rem;
  right: 1rem;
  display: flex;
  gap: 1rem;
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 0.375rem;
  border: 1px solid var(--border-color);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.legend-line {
  width: 1.5rem;
  height: 2px;
  border-radius: 1px;
}

.legend-dot {
  width: 0.75rem;
  height: 0.75rem;
  border-radius: 50%;
}

.legend-line.original {
  background: #ef4444;
}

.legend-line.smoothed {
  background: #3b82f6;
}

.legend-line.diff {
  background: #10b981;
}

.legend-dot.original {
  background: #ef4444;
  opacity: 0.6;
}

/* 轨迹选择器 */
.trajectory-selector {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.selector-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.selector-buttons {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.selector-btn {
  padding: 0.5rem 1rem;
  border: 1px solid var(--border-color);
  border-radius: 0.375rem;
  background: var(--bg-primary);
  color: var(--text-secondary);
  font-size: 0.8125rem;
  cursor: pointer;
  transition: all 0.2s;
}

.selector-btn:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.selector-btn.active {
  border-color: var(--color-primary);
  background: var(--color-primary);
  color: white;
}

/* 数据表 */
.data-table-section {
  background: var(--bg-primary);
  border-radius: 0.5rem;
  border: 1px solid var(--border-color);
  padding: 1rem;
}

.table-title {
  margin: 0 0 1rem 0;
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--text-primary);
}

.table-container {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.8125rem;
}

.data-table th,
.data-table td {
  padding: 0.625rem 0.75rem;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

.data-table th {
  font-weight: 600;
  color: var(--text-secondary);
  background: var(--bg-tertiary);
}

.data-table td {
  color: var(--text-primary);
  font-family: monospace;
}

.data-table tr:hover td {
  background: var(--bg-tertiary);
}

.table-pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}

.page-btn {
  padding: 0.375rem 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 0.375rem;
  background: var(--bg-primary);
  color: var(--text-secondary);
  font-size: 0.8125rem;
  cursor: pointer;
  transition: all 0.2s;
}

.page-btn:hover:not(:disabled) {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 0.8125rem;
  color: var(--text-muted);
}
</style>
