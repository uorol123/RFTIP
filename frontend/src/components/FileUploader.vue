<template>
  <div
    :class="['file-uploader', { 'is-dragging': isDragging, 'has-error': error }]"
    @dragenter.prevent="onDragEnter"
    @dragleave.prevent="onDragLeave"
    @dragover.prevent
    @drop.prevent="onDrop"
  >
    <input
      ref="fileInput"
      type="file"
      :accept="accept"
      :multiple="multiple"
      class="file-input"
      @change="onFileChange"
    />

    <div v-if="!files.length" class="uploader-prompt">
      <div class="uploader-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="1.5"
            d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
          />
        </svg>
      </div>
      <p class="uploader-text">
        {{ dragText }}
      </p>
      <p class="uploader-hint">
        or <span class="uploader-link" @click="selectFiles">browse files</span>
      </p>
      <p class="uploader-formats">
        Accepted formats: {{ formatList }}
      </p>
      <label v-if="showPrivacy" class="uploader-privacy">
        <input type="checkbox" v-model="isPublic" />
        <span>Make file public</span>
      </label>
    </div>

    <div v-else class="uploader-files">
      <div v-for="(file, index) in files" :key="index" class="uploader-file">
        <div class="file-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="1.5"
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
        </div>
        <div class="file-info">
          <div class="file-name">{{ file.name }}</div>
          <div class="file-size">{{ formatSize(file.size) }}</div>
        </div>
        <button type="button" class="file-remove" @click="removeFile(index)">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      </div>

      <button v-if="multiple" type="button" class="uploader-add" @click="selectFiles">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Add more files
      </button>
    </div>

    <div v-if="error" class="uploader-error">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
      {{ error }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface Props {
  accept?: string
  multiple?: boolean
  maxSize?: number // in bytes
  maxFiles?: number
  showPrivacy?: boolean
}

interface Emits {
  (e: 'update:modelValue', files: File[]): void
  (e: 'upload', files: File[], isPublic: boolean): void
}

const props = withDefaults(defineProps<Props>(), {
  accept: '.csv,.xlsx,.xls',
  multiple: false,
  maxSize: 50 * 1024 * 1024, // 50MB
  maxFiles: 10,
  showPrivacy: true,
})

const emit = defineEmits<Emits>()

const fileInput = ref<HTMLInputElement | null>(null)
const files = ref<File[]>([])
const isDragging = ref(false)
const isPublic = ref(false)
const error = ref('')

const dragText = computed(() => {
  return isDragging.value ? 'Drop files here' : 'Drag and drop files here'
})

const formatList = computed(() => {
  return props.accept.split(',').map(s => s.trim().replace('.', '').toUpperCase()).join(', ')
})

const formatSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

const selectFiles = () => {
  fileInput.value?.click()
}

const validateFile = (file: File): boolean => {
  // Check file extension
  const ext = '.' + file.name.split('.').pop()?.toLowerCase()
  const accepted = props.accept.split(',').map(s => s.trim().toLowerCase())
  if (!accepted.includes(ext)) {
    error.value = `Invalid file type. Accepted: ${props.accept}`
    return false
  }

  // Check file size
  if (file.size > props.maxSize) {
    error.value = `File too large. Maximum size: ${formatSize(props.maxSize)}`
    return false
  }

  return true
}

const onDragEnter = (e: DragEvent) => {
  isDragging.value = true
}

const onDragLeave = (e: DragEvent) => {
  isDragging.value = false
}

const onDrop = (e: DragEvent) => {
  isDragging.value = false
  error.value = ''

  const droppedFiles = Array.from(e.dataTransfer?.files || [])

  if (droppedFiles.length === 0) return

  const validFiles = droppedFiles.filter(validateFile)

  if (props.multiple) {
    if (files.value.length + validFiles.length > props.maxFiles) {
      error.value = `Maximum ${props.maxFiles} files allowed`
      return
    }
    files.value = [...files.value, ...validFiles]
  } else {
    files.value = validFiles.slice(0, 1)
  }

  emit('update:modelValue', files.value)
}

const onFileChange = (e: Event) => {
  const target = e.target as HTMLInputElement
  const selectedFiles = Array.from(target.files || [])

  if (selectedFiles.length === 0) return

  const validFiles = selectedFiles.filter(validateFile)

  if (props.multiple) {
    if (files.value.length + validFiles.length > props.maxFiles) {
      error.value = `Maximum ${props.maxFiles} files allowed`
      return
    }
    files.value = [...files.value, ...validFiles]
  } else {
    files.value = validFiles.slice(0, 1)
  }

  emit('update:modelValue', files.value)
}

const removeFile = (index: number) => {
  files.value.splice(index, 1)
  emit('update:modelValue', files.value)
}

const upload = () => {
  if (files.value.length === 0) return
  emit('upload', files.value, isPublic.value)
}

const clear = () => {
  files.value = []
  error.value = ''
  isPublic.value = false
}

defineExpose({
  upload,
  clear,
})
</script>

<style scoped>
.file-uploader {
  position: relative;
  padding: 2rem;
  border-radius: 1rem;
  background: var(--bg-secondary);
  border: 2px dashed var(--border-color, rgba(255, 255, 255, 0.1));
  transition: all 0.3s ease;
}

.file-uploader.is-dragging {
  border-color: var(--color-primary);
  background: rgba(59, 130, 246, 0.05);
}

.file-uploader.has-error {
  border-color: #ef4444;
}

.file-input {
  display: none;
}

.uploader-prompt {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.uploader-icon {
  width: 3rem;
  height: 3rem;
  color: var(--color-primary);
}

.uploader-icon svg {
  width: 100%;
  height: 100%;
}

.uploader-text {
  margin: 0.5rem 0 0;
  color: var(--text-primary);
  font-size: 1rem;
  font-weight: 500;
}

.uploader-hint {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.9375rem;
}

.uploader-link {
  color: var(--color-primary);
  cursor: pointer;
  text-decoration: underline;
}

.uploader-formats {
  margin: 0.25rem 0 0;
  color: var(--text-muted);
  font-size: 0.8125rem;
}

.uploader-privacy {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1rem;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.uploader-privacy input {
  cursor: pointer;
}

.uploader-files {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.uploader-file {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  border-radius: 0.5rem;
  background: var(--bg-tertiary);
}

.file-icon {
  flex-shrink: 0;
  width: 2rem;
  height: 2rem;
  color: var(--color-primary);
}

.file-icon svg {
  width: 100%;
  height: 100%;
}

.file-info {
  flex: 1;
  min-width: 0;
}

.file-name {
  color: var(--text-primary);
  font-size: 0.875rem;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-size {
  color: var(--text-muted);
  font-size: 0.8125rem;
}

.file-remove {
  flex-shrink: 0;
  width: 1.5rem;
  height: 1.5rem;
  padding: 0;
  border: none;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  border-radius: 0.25rem;
  transition: all 0.2s;
}

.file-remove:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.uploader-add {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  width: 100%;
  padding: 0.75rem;
  border: 1px dashed var(--border-color, rgba(255, 255, 255, 0.1));
  border-radius: 0.5rem;
  background: transparent;
  color: var(--text-secondary);
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.uploader-add:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.uploader-error {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1rem;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  font-size: 0.875rem;
}

.uploader-error svg {
  flex-shrink: 0;
  width: 1rem;
  height: 1rem;
}
</style>
