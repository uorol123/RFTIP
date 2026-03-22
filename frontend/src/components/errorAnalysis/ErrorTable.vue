<template>
  <div class="error-table">
    <div class="table-header">
      <h3 class="table-title">雷达站误差明细</h3>
      <div class="table-actions">
        <div class="search-box">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
          </svg>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索雷达站..."
            class="search-input"
          />
        </div>
        <button class="btn btn-secondary btn-sm" @click="exportCSV">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
          </svg>
          导出CSV
        </button>
      </div>
    </div>

    <div v-if="loading" class="table-loading">
      <div class="spinner"></div>
      <span>加载中...</span>
    </div>

    <div v-else-if="filteredResults.length === 0" class="table-empty">
      <EmptyState
        title="暂无数据"
        description="完成分析后将显示误差明细"
      />
    </div>

    <div v-else class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th
              v-for="column in columns"
              :key="column.key"
              :class="['table-header', { sortable: column.sortable }]"
              @click="column.sortable && sortBy(column.key)"
            >
              {{ column.label }}
              <span
                v-if="column.sortable"
                :class="['sort-indicator', getSortClass(column.key)]"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7"/>
                </svg>
              </span>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="result in paginatedResults"
            :key="result.id"
            class="table-row"
          >
            <td class="table-cell">{{ result.station_id }}</td>
            <td class="table-cell numeric">{{ formatNumber(result.azimuth_error) }}</td>
            <td class="table-cell numeric">{{ formatNumber(result.range_error) }}</td>
            <td class="table-cell numeric">{{ formatNumber(result.elevation_error) }}</td>
            <td class="table-cell numeric">{{ result.match_count }}</td>
            <td class="table-cell numeric">{{ formatNumber(result.confidence) }}</td>
            <td class="table-cell numeric">{{ result.iterations ?? '-' }}</td>
            <td class="table-cell numeric">{{ formatNumber(result.final_cost) }}</td>
            <td class="table-cell">
              <span class="badge" :class="getBadgeClass(result)">
                {{ getBadgeText(result) }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 分页 -->
    <div v-if="totalPages > 1" class="table-pagination">
      <div class="pagination-info">
        显示 {{ startIndex + 1 }}-{{ endIndex }}，共 {{ filteredResults.length }} 条
      </div>
      <div class="pagination-controls">
        <button
          class="pagination-btn"
          :disabled="currentPage === 1"
          @click="currentPage--"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
          </svg>
        </button>
        <span class="pagination-pages">{{ currentPage }} / {{ totalPages }}</span>
        <button
          class="pagination-btn"
          :disabled="currentPage === totalPages"
          @click="currentPage++"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import EmptyState from '@/components/EmptyState.vue'
import type { ErrorResult } from '@/types/errorAnalysis'

interface Props {
  results: ErrorResult[]
  loading: boolean
}

const props = defineProps<Props>()

const columns = [
  { key: 'station_id', label: '雷达站ID', sortable: true },
  { key: 'azimuth', label: '方位角误差', sortable: true },
  { key: 'range', label: '距离误差', sortable: true },
  { key: 'elevation', label: '俯仰角误差', sortable: true },
  { key: 'matches', label: '匹配点数', sortable: true },
  { key: 'confidence', label: '置信度', sortable: true },
  { key: 'iterations', label: '迭代次数', sortable: true },
  { key: 'cost', label: '最终代价', sortable: true },
  { key: 'quality', label: '质量评级', sortable: false },
]

const searchQuery = ref('')
const sortColumn = ref<string>('azimuth')
const sortOrder = ref<'asc' | 'desc'>('asc')
const currentPage = ref(1)
const pageSize = 10

// 过滤结果
const filteredResults = computed(() => {
  if (!props.results) return []
  if (!searchQuery.value) return props.results

  const query = searchQuery.value.toLowerCase()
  return props.results.filter(result =>
    result.station_id.toString().toLowerCase().includes(query)
  )
})

// 排序结果
const sortedResults = computed(() => {
  const results = [...filteredResults.value]
  results.sort((a, b) => {
    let aVal: number
    let bVal: number

    switch (sortColumn.value) {
      case 'azimuth':
        aVal = a.azimuth_error
        bVal = b.azimuth_error
        break
      case 'range':
        aVal = a.range_error
        bVal = b.range_error
        break
      case 'elevation':
        aVal = a.elevation_error
        bVal = b.elevation_error
        break
      case 'matches':
        aVal = a.match_count
        bVal = b.match_count
        break
      case 'confidence':
        aVal = a.confidence ?? 0
        bVal = b.confidence ?? 0
        break
      case 'iterations':
        aVal = a.iterations ?? 0
        bVal = b.iterations ?? 0
        break
      case 'cost':
        aVal = a.final_cost ?? 0
        bVal = b.final_cost ?? 0
        break
      default:
        aVal = a.azimuth_error
        bVal = b.azimuth_error
    }

    return sortOrder.value === 'asc' ? aVal - bVal : bVal - aVal
  })
  return results
})

// 分页结果
const paginatedResults = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  const end = start + pageSize
  return sortedResults.value.slice(start, end)
})

const totalPages = computed(() => Math.ceil(sortedResults.value.length / pageSize))
const startIndex = computed(() => (currentPage.value - 1) * pageSize)
const endIndex = computed(() => Math.min(startIndex.value + pageSize, sortedResults.value.length))

// 排序
function sortBy(column: string) {
  if (sortColumn.value === column) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortColumn.value = column
    sortOrder.value = 'asc'
  }
}

function getSortClass(column: string) {
  if (sortColumn.value !== column) return ''
  return sortOrder.value === 'asc' ? 'sort-asc' : 'sort-desc'
}

// 格式化数字
function formatNumber(value: number | null | undefined): string {
  if (value === null || value === undefined) return '-'
  return value.toFixed(6)
}

// 质量评级
function getBadgeClass(result: ErrorResult) {
  const confidence = result.confidence ?? 0
  if (confidence >= 0.95) return 'badge-excellent'
  if (confidence >= 0.85) return 'badge-good'
  if (confidence >= 0.70) return 'badge-fair'
  return 'badge-poor'
}

function getBadgeText(result: ErrorResult) {
  const confidence = result.confidence ?? 0
  if (confidence >= 0.95) return '优秀'
  if (confidence >= 0.85) return '良好'
  if (confidence >= 0.70) return '一般'
  return '较差'
}

// 导出CSV
function exportCSV() {
  if (!props.results || props.results.length === 0) return

  const headers = [
    '雷达站ID',
    '方位角误差',
    '距离误差',
    '俯仰角误差',
    '匹配点数',
    '置信度',
    '迭代次数',
    '最终代价',
  ]

  const rows = sortedResults.value.map(result => [
    result.station_id,
    result.azimuth_error.toFixed(6),
    result.range_error.toFixed(6),
    result.elevation_error.toFixed(6),
    result.match_count.toString(),
    (result.confidence ?? 0).toFixed(6),
    result.iterations?.toString() ?? '',
    (result.final_cost ?? 0).toFixed(6),
  ])

  const csvContent = [
    headers.join(','),
    ...rows.map(row => row.join(',')),
  ].join('\n')

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `error-analysis-${Date.now()}.csv`
  link.click()
}
</script>

<style scoped>
.error-table {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1.5rem;
  background: var(--bg-secondary);
  border-radius: 0.75rem;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.table-title {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
}

.table-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.375rem 0.75rem;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 0.375rem;
}

.search-box svg {
  width: 1rem;
  height: 1rem;
  color: var(--text-muted);
  flex-shrink: 0;
}

.search-input {
  border: none;
  background: transparent;
  outline: none;
  font-size: 0.875rem;
  color: var(--text-primary);
  min-width: 150px;
}

.search-input::placeholder {
  color: var(--text-muted);
}

.table-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 3rem 1rem;
  color: var(--text-secondary);
}

.spinner {
  width: 2rem;
  height: 2rem;
  border: 2px solid var(--bg-tertiary);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.table-empty {
  padding: 1rem 0;
}

.table-container {
  overflow-x: auto;
  border-radius: 0.5rem;
  background: var(--bg-primary);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.table-header {
  padding: 0.75rem 1rem;
  text-align: left;
  font-weight: 600;
  font-size: 0.8125rem;
  color: var(--text-secondary);
  background: var(--bg-tertiary);
  white-space: nowrap;
}

.table-header.sortable {
  cursor: pointer;
  user-select: none;
}

.table-header.sortable:hover {
  color: var(--text-primary);
}

.sort-indicator {
  display: inline-flex;
  margin-left: 0.375rem;
  opacity: 0.3;
}

.sort-indicator.sort-asc,
.sort-indicator.sort-desc {
  opacity: 1;
}

.sort-indicator svg {
  width: 0.75rem;
  height: 0.75rem;
}

.sort-asc svg {
  transform: rotate(0deg);
}

.sort-desc svg {
  transform: rotate(180deg);
}

.table-row {
  border-bottom: 1px solid var(--border-color);
  transition: background 0.2s;
}

.table-row:last-child {
  border-bottom: none;
}

.table-row:hover {
  background: var(--bg-tertiary);
}

.table-cell {
  padding: 0.75rem 1rem;
  font-size: 0.875rem;
  color: var(--text-primary);
}

.table-cell.numeric {
  font-variant-numeric: tabular-nums;
  text-align: right;
}

.badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.badge-excellent {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.badge-good {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.badge-fair {
  background: rgba(249, 115, 22, 0.1);
  color: #f97316;
}

.badge-poor {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.table-pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 1rem;
  background: var(--bg-primary);
  border-radius: 0.5rem;
}

.pagination-info {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.pagination-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  padding: 0;
  border: none;
  border-radius: 0.375rem;
  background: var(--bg-tertiary);
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.2s;
}

.pagination-btn:hover:not(:disabled) {
  background: var(--color-primary);
  color: white;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-btn svg {
  width: 1rem;
  height: 1rem;
}

.pagination-pages {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.375rem 0.75rem;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-sm {
  font-size: 0.75rem;
  padding: 0.3125rem 0.625rem;
}

.btn-secondary {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.btn-secondary:hover {
  background: var(--border-color);
}

.btn svg {
  width: 0.875rem;
  height: 0.875rem;
}

@media (max-width: 640px) {
  .table-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .table-actions {
    width: 100%;
  }

  .search-box {
    flex: 1;
    min-width: 0;
  }

  .table-pagination {
    flex-direction: column;
    align-items: stretch;
  }

  .pagination-controls {
    justify-content: center;
  }
}
</style>
