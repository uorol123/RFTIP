import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface DataFile {
  id: number
  userId: number
  fileName: string
  filePath: string
  dataType: 'track' | 'radar'
  isPublic: boolean
  uploadTime: string
  description?: string
}

export const useFileStore = defineStore('file', () => {
  // State
  const files = ref<DataFile[]>([])
  const selectedFileIds = ref<number[]>([])
  const currentFile = ref<DataFile | null>(null)

  // Actions
  function setFiles(newFiles: DataFile[]) {
    files.value = newFiles
  }

  function addFile(file: DataFile) {
    files.value.push(file)
  }

  function updateFile(fileId: number, updates: Partial<DataFile>) {
    const index = files.value.findIndex((f) => f.id === fileId)
    if (index > -1) {
      files.value[index] = { ...files.value[index], ...updates }
    }
  }

  function removeFile(fileId: number) {
    const index = files.value.findIndex((f) => f.id === fileId)
    if (index > -1) {
      files.value.splice(index, 1)
    }
    // 从选中列表中移除
    selectedFileIds.value = selectedFileIds.value.filter((id) => id !== fileId)
  }

  function selectFile(fileId: number) {
    if (!selectedFileIds.value.includes(fileId)) {
      selectedFileIds.value.push(fileId)
    }
  }

  function deselectFile(fileId: number) {
    selectedFileIds.value = selectedFileIds.value.filter((id) => id !== fileId)
  }

  function toggleFileSelection(fileId: number) {
    if (selectedFileIds.value.includes(fileId)) {
      deselectFile(fileId)
    } else {
      selectFile(fileId)
    }
  }

  function selectAllFiles() {
    selectedFileIds.value = files.value.map((f) => f.id)
  }

  function clearSelection() {
    selectedFileIds.value = []
  }

  function setCurrentFile(file: DataFile | null) {
    currentFile.value = file
  }

  return {
    // State
    files,
    selectedFileIds,
    currentFile,
    // Actions
    setFiles,
    addFile,
    updateFile,
    removeFile,
    selectFile,
    deselectFile,
    toggleFileSelection,
    selectAllFiles,
    clearSelection,
    setCurrentFile,
  }
})
