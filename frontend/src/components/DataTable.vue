<template>
  <div class="data-table-wrapper">
    <div v-if="showHeader" class="data-table-header">
      <div class="table-title">
        <h3>{{ title }}</h3>
        <span v-if="subtitle" class="table-subtitle">{{ subtitle }}</span>
      </div>
      <div v-if="$slots.actions" class="table-actions">
        <slot name="actions" />
      </div>
    </div>

    <div class="data-table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th v-if="selectable" class="table-select">
              <input
                type="checkbox"
                :checked="isAllSelected"
                :indeterminate="isSomeSelected"
                @change="toggleSelectAll"
              />
            </th>
            <th
              v-for="column in columns"
              :key="column.key"
              :class="['table-header', column.class, { sortable: column.sortable }]"
              :style="{ width: column.width }"
              @click="column.sortable && sortBy(column.key)"
            >
              {{ column.label }}
              <span
                v-if="column.sortable"
                :class="['sort-indicator', getSortClass(column.key)]"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
                </svg>
              </span>
            </th>
            <th v-if="$slots['row-actions']" class="table-actions-header">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td :colspan="columnCount" class="table-loading">
              <div class="spinner"></div>
              <span>Loading...</span>
            </td>
          </tr>
          <tr v-else-if="!data.length">
            <td :colspan="columnCount" class="table-empty">
              <EmptyState
                :title="emptyTitle"
                :description="emptyDescription"
              >
                <template v-if="$slots['empty-action']" #action>
                  <slot name="empty-action" />
                </template>
              </EmptyState>
            </td>
          </tr>
          <tr
            v-else
            v-for="(row, index) in data"
            :key="row[rowKey] ?? index"
            :class="['table-row', { 'is-selected': isRowSelected(row), clickable: clickable }]"
            @click="clickable && $emit('row-click', row)"
          >
            <td v-if="selectable" class="table-select">
              <input
                type="checkbox"
                :checked="isRowSelected(row)"
                @change="toggleRowSelection(row)"
                @click.stop
              />
            </td>
            <td
              v-for="column in columns"
              :key="column.key"
              :class="['table-cell', column.class]"
            >
              <slot
                v-if="$slots[`cell-${column.key}`]"
                :name="`cell-${column.key}`"
                :row="row"
                :value="getColumnValue(row, column.key)"
              >
                {{ getColumnValue(row, column.key) }}
              </slot>
              <span v-else-if="column.render">
                {{ column.render(row, getColumnValue(row, column.key)) }}
              </span>
              <span v-else>{{ getColumnValue(row, column.key) }}</span>
            </td>
            <td v-if="$slots['row-actions']" class="table-row-actions">
              <slot name="row-actions" :row="row" />
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showPagination && totalPages > 1" class="data-table-footer">
      <div class="table-info">
        Showing {{ startIndex + 1 }} to {{ endIndex }} of {{ totalItems }} entries
      </div>
      <div class="table-pagination">
        <button
          class="pagination-btn"
          :disabled="currentPage === 1"
          @click="$emit('page-change', currentPage - 1)"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <span class="pagination-info">{{ currentPage }} / {{ totalPages }}</span>
        <button
          class="pagination-btn"
          :disabled="currentPage === totalPages"
          @click="$emit('page-change', currentPage + 1)"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import EmptyState from './EmptyState.vue'

interface Column {
  key: string
  label: string
  width?: string
  sortable?: boolean
  class?: string
  render?: (row: any, value: any) => string
}

interface Props {
  columns: Column[]
  data: any[]
  rowKey?: string
  loading?: boolean
  selectable?: boolean
  clickable?: boolean
  showHeader?: boolean
  showPagination?: boolean
  title?: string
  subtitle?: string
  currentPage?: number
  pageSize?: number
  totalItems?: number
  emptyTitle?: string
  emptyDescription?: string
}

interface Emits {
  (e: 'row-click', row: any): void
  (e: 'selection-change', selectedRows: any[]): void
  (e: 'sort-change', sortBy: string, order: 'asc' | 'desc'): void
  (e: 'page-change', page: number): void
}

const props = withDefaults(defineProps<Props>(), {
  rowKey: 'id',
  loading: false,
  selectable: false,
  clickable: false,
  showHeader: true,
  showPagination: true,
  currentPage: 1,
  pageSize: 10,
  totalItems: 0,
  emptyTitle: 'No data',
  emptyDescription: 'No entries to display',
})

const emit = defineEmits<Emits>()

const selectedRows = ref<Set<any>>(new Set())
const sortColumn = ref<string>('')
const sortOrder = ref<'asc' | 'desc'>('asc')

const columnCount = computed(() => {
  return props.columns.length + (props.selectable ? 1 : 0) + (hasRowActions.value ? 1 : 0)
})

const hasRowActions = computed(() => {
  return !!useSlots()['row-actions']
})

const isAllSelected = computed(() => {
  return props.data.length > 0 && selectedRows.value.size === props.data.length
})

const isSomeSelected = computed(() => {
  return selectedRows.value.size > 0 && selectedRows.value.size < props.data.length
})

const isRowSelected = (row: any) => {
  return selectedRows.value.has(row[props.rowKey])
}

const toggleRowSelection = (row: any) => {
  const key = row[props.rowKey]
  if (selectedRows.value.has(key)) {
    selectedRows.value.delete(key)
  } else {
    selectedRows.value.add(key)
  }
  emitSelectionChange()
}

const toggleSelectAll = () => {
  if (isAllSelected.value) {
    selectedRows.value.clear()
  } else {
    props.data.forEach(row => selectedRows.value.add(row[props.rowKey]))
  }
  emitSelectionChange()
}

const emitSelectionChange = () => {
  const selected = props.data.filter(row => selectedRows.value.has(row[props.rowKey]))
  emit('selection-change', selected)
}

const sortBy = (column: string) => {
  if (sortColumn.value === column) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortColumn.value = column
    sortOrder.value = 'asc'
  }
  emit('sort-change', column, sortOrder.value)
}

const getSortClass = (column: string) => {
  if (sortColumn.value !== column) return ''
  return sortOrder.value === 'asc' ? 'sort-asc' : 'sort-desc'
}

const getColumnValue = (row: any, key: string) => {
  return key.split('.').reduce((obj, k) => obj?.[k], row)
}

const totalPages = computed(() => {
  return Math.ceil(props.totalItems / props.pageSize)
})

const startIndex = computed(() => {
  return (props.currentPage - 1) * props.pageSize
})

const endIndex = computed(() => {
  return Math.min(startIndex.value + props.pageSize, props.totalItems)
})
</script>

<style scoped>
.data-table-wrapper {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.data-table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.table-title h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1.125rem;
  font-weight: 600;
}

.table-subtitle {
  margin-left: 0.75rem;
  color: var(--text-muted);
  font-size: 0.875rem;
}

.table-actions {
  display: flex;
  gap: 0.75rem;
}

.data-table-container {
  overflow-x: auto;
  border-radius: 0.75rem;
  background: var(--bg-secondary);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table thead {
  background: var(--bg-tertiary);
  border-bottom: 1px solid var(--border-color, rgba(255, 255, 255, 0.1));
}

.table-header {
  padding: 0.875rem 1rem;
  text-align: left;
  font-weight: 600;
  font-size: 0.8125rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-secondary);
  user-select: none;
}

.table-header.sortable {
  cursor: pointer;
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

.table-select {
  width: 2.5rem !important;
  text-align: center;
}

.table-select input {
  cursor: pointer;
}

.table-row {
  border-bottom: 1px solid var(--border-color, rgba(255, 255, 255, 0.05));
  transition: background 0.2s;
}

.table-row:last-child {
  border-bottom: none;
}

.table-row.clickable {
  cursor: pointer;
}

.table-row.clickable:hover {
  background: var(--bg-tertiary);
}

.table-row.is-selected {
  background: rgba(59, 130, 246, 0.1);
}

.table-cell {
  padding: 0.875rem 1rem;
  color: var(--text-primary);
  font-size: 0.875rem;
}

.table-loading,
.table-empty {
  padding: 3rem 1rem;
  text-align: center;
}

.table-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  color: var(--text-secondary);
}

.spinner {
  width: 1.5rem;
  height: 1.5rem;
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

.table-row-actions {
  padding: 0.5rem 1rem;
  white-space: nowrap;
}

.data-table-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
  padding: 0.75rem 1rem;
  border-radius: 0.75rem;
  background: var(--bg-secondary);
}

.table-info {
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.table-pagination {
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

.pagination-info {
  color: var(--text-secondary);
  font-size: 0.875rem;
}

@media (max-width: 640px) {
  .data-table-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .data-table-footer {
    flex-direction: column;
    align-items: stretch;
  }

  .table-pagination {
    justify-content: center;
  }
}
</style>
