<template>
  <Teleport to="body">
    <div class="dialog-overlay" @click="handleClose">
      <div class="dialog-container" @click.stop>
        <div class="dialog-header">
          <h2 class="dialog-title">个人资料</h2>
          <button class="dialog-close" @click="handleClose">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>

        <div class="dialog-body">
          <!-- 头像上传 -->
          <div class="avatar-section">
            <div class="avatar-preview">
              <img v-if="previewUrl" :src="previewUrl" alt="头像" />
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
              </svg>
            </div>
            <div class="avatar-actions">
              <input
                ref="fileInputRef"
                type="file"
                accept="image/jpeg,image/png,image/gif,image/webp"
                @change="handleFileChange"
                style="display: none"
              />
              <button class="btn btn-secondary" @click="selectAvatar" :disabled="uploading">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                </svg>
                {{ uploading ? '上传中...' : '更换头像' }}
              </button>
              <span class="avatar-hint">支持 JPG、PNG、GIF、WEBP，最大 5MB</span>
            </div>
          </div>

          <!-- 表单 -->
          <form @submit.prevent="handleSubmit">
            <div class="form-group">
              <label class="form-label">用户名</label>
              <input type="text" class="form-input" :value="user?.username" disabled />
              <span class="form-hint">用户名不能修改</span>
            </div>

            <div class="form-group">
              <label class="form-label" for="full_name">姓名</label>
              <input
                id="full_name"
                type="text"
                class="form-input"
                v-model="formData.full_name"
                placeholder="请输入姓名"
              />
            </div>

            <div class="form-group">
              <label class="form-label" for="email">邮箱</label>
              <input type="email" class="form-input" :value="user?.email" disabled />
              <span class="form-hint">邮箱不能修改</span>
            </div>

            <div class="form-group">
              <label class="form-label" for="phone">手机号</label>
              <input
                id="phone"
                type="tel"
                class="form-input"
                v-model="formData.phone"
                placeholder="请输入手机号"
              />
            </div>

            <div class="dialog-actions">
              <button type="button" class="btn btn-ghost" @click="handleClose" :disabled="saving">
                取消
              </button>
              <button type="submit" class="btn btn-primary" :disabled="saving">
                <svg v-if="saving" class="spinner" viewBox="0 0 24 24">
                  <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="3" stroke-dasharray="32" stroke-linecap="round"/>
                </svg>
                {{ saving ? '保存中...' : '保存' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { authApi } from '@/api/auth'

interface Props {
  user: any
  avatarUrl?: string | null
}

interface Emits {
  (e: 'close'): void
  (e: 'updated', user: any): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const fileInputRef = ref<HTMLInputElement>()
const uploading = ref(false)
const saving = ref(false)

const formData = ref({
  full_name: props.user?.full_name || '',
  phone: props.user?.phone || '',
})

const previewUrl = ref<string | null>(props.avatarUrl)

// 监听 avatarUrl 变化
watch(() => props.avatarUrl, (newUrl) => {
  previewUrl.value = newUrl
})

const handleClose = () => {
  emit('close')
}

const selectAvatar = () => {
  fileInputRef.value?.click()
}

const handleFileChange = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  // 验证文件类型
  const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
  if (!validTypes.includes(file.type)) {
    alert('请选择 JPG、PNG、GIF 或 WEBP 格式的图片')
    return
  }

  // 验证文件大小 (5MB)
  if (file.size > 5 * 1024 * 1024) {
    alert('图片大小不能超过 5MB')
    return
  }

  // 显示预览
  previewUrl.value = URL.createObjectURL(file)

  // 上传头像
  uploading.value = true
  try {
    await authApi.uploadAvatar(file)
    // 刷新页面或通知父组件更新
    window.location.reload()
  } catch (error: any) {
    console.error('上传头像失败:', error)
    alert(error.message || '上传头像失败，请重试')
    previewUrl.value = props.avatarUrl
  } finally {
    uploading.value = false
    // 清空 input 以便重复选择同一文件
    if (fileInputRef.value) {
      fileInputRef.value.value = ''
    }
  }
}

const handleSubmit = async () => {
  saving.value = true
  try {
    const updatedUser = await authApi.update({
      full_name: formData.value.full_name || undefined,
      phone: formData.value.phone || undefined,
    })
    emit('updated', updatedUser)
  } catch (error: any) {
    console.error('更新个人资料失败:', error)
    alert(error.message || '更新失败，请重试')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.dialog-container {
  background: var(--bg-elevated);
  border-radius: 1rem;
  width: 100%;
  max-width: 480px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.dialog-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem;
  border-bottom: 1px solid var(--border-color);
}

.dialog-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
}

.dialog-close {
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

.dialog-close:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.dialog-close svg {
  width: 1.25rem;
  height: 1.25rem;
}

.dialog-body {
  padding: 1.5rem;
  max-height: calc(100vh - 200px);
  overflow-y: auto;
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
}

.avatar-preview {
  width: 6rem;
  height: 6rem;
  border-radius: 50%;
  background: var(--gradient-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.avatar-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-preview svg {
  width: 2.5rem;
  height: 2.5rem;
  color: white;
}

.avatar-actions {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.avatar-hint {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.form-group {
  margin-bottom: 1.25rem;
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

.form-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background: var(--bg-tertiary);
}

.form-hint {
  display: block;
  margin-top: 0.375rem;
  font-size: 0.75rem;
  color: var(--text-muted);
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.625rem 1.25rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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

.btn-secondary {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
}

.btn-secondary:hover:not(:disabled) {
  background: var(--bg-tertiary);
}

.btn-ghost {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
}

.btn-ghost:hover:not(:disabled) {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
