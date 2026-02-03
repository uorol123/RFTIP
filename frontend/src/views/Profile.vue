<template>
  <div class="profile">
    <div class="page-header">
      <h1 class="page-title">User Profile</h1>
      <p class="page-subtitle">Manage your account settings and preferences</p>
    </div>

    <div class="profile-layout">
      <!-- Profile Info -->
      <div class="profile-card">
        <div class="profile-header">
          <div class="avatar-section">
            <div class="avatar">
              <img v-if="user?.avatar" :src="user.avatar" :alt="user.username" />
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                />
              </svg>
            </div>
            <button class="avatar-upload" @click="uploadAvatar">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"
                />
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"
                />
              </svg>
            </button>
          </div>
          <div class="profile-meta">
            <h2 class="profile-name">{{ user?.full_name || user?.username }}</h2>
            <p class="profile-email">{{ user?.email }}</p>
            <div class="profile-badges">
              <span v-if="user?.is_admin" class="badge badge-admin">Admin</span>
              <span v-if="user?.is_active" class="badge badge-active">Active</span>
            </div>
          </div>
        </div>

        <div class="profile-stats">
          <div class="stat">
            <span class="stat-value">{{ formatDate(user?.created_at) }}</span>
            <span class="stat-label">Member Since</span>
          </div>
        </div>
      </div>

      <!-- Profile Form -->
      <div class="settings-card">
        <div class="card-header">
          <h3 class="card-title">Profile Information</h3>
        </div>
        <div class="card-body">
          <form @submit.prevent="updateProfile">
            <div class="form-group">
              <label class="form-label">Username</label>
              <input
                v-model="profileForm.username"
                type="text"
                class="form-input"
                disabled
              />
              <span class="form-hint">Username cannot be changed</span>
            </div>

            <div class="form-group">
              <label class="form-label">Email</label>
              <input
                v-model="profileForm.email"
                type="email"
                class="form-input"
                required
              />
            </div>

            <div class="form-group">
              <label class="form-label">Full Name</label>
              <input
                v-model="profileForm.full_name"
                type="text"
                class="form-input"
              />
            </div>

            <div class="form-actions">
              <button type="submit" class="btn btn-primary" :disabled="updating">
                {{ updating ? 'Saving...' : 'Save Changes' }}
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- Change Password -->
      <div class="settings-card">
        <div class="card-header">
          <h3 class="card-title">Change Password</h3>
        </div>
        <div class="card-body">
          <form @submit.prevent="changePassword">
            <div class="form-group">
              <label class="form-label">Current Password</label>
              <input
                v-model="passwordForm.old_password"
                type="password"
                class="form-input"
                required
              />
            </div>

            <div class="form-group">
              <label class="form-label">New Password</label>
              <input
                v-model="passwordForm.new_password"
                type="password"
                class="form-input"
                required
                minlength="8"
              />
            </div>

            <div class="form-group">
              <label class="form-label">Confirm New Password</label>
              <input
                v-model="passwordForm.confirm_password"
                type="password"
                class="form-input"
                required
              />
            </div>

            <div class="form-actions">
              <button type="submit" class="btn btn-primary" :disabled="changingPassword">
                {{ changingPassword ? 'Changing...' : 'Change Password' }}
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- Login Logs -->
      <div class="settings-card settings-card-full">
        <div class="card-header">
          <h3 class="card-title">Login History</h3>
        </div>
        <div class="card-body">
          <div v-if="loadingLogs" class="logs-loading">
            <Loading :fullscreen="false" message="Loading login history..." />
          </div>
          <div v-else-if="loginLogs.length === 0" class="logs-empty">
            <EmptyState title="No login history" description="Your login activity will appear here" />
          </div>
          <div v-else class="logs-list">
            <div
              v-for="log in loginLogs"
              :key="log.id"
              :class="['log-entry', `log-${log.status}`]"
            >
              <div class="log-icon">
                <svg v-if="log.status === 'success'" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </div>
              <div class="log-details">
                <div class="log-time">{{ formatDateTime(log.login_time) }}</div>
                <div class="log-info">
                  <span class="log-ip">{{ log.ip_address }}</span>
                  <span class="log-agent">{{ formatUserAgent(log.user_agent) }}</span>
                </div>
              </div>
              <div class="log-status">
                <span :class="['status-badge', `status-${log.status}`]">
                  {{ log.status }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Avatar Upload Input -->
    <input
      ref="avatarInput"
      type="file"
      accept="image/*"
      style="display: none"
      @change="handleAvatarUpload"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, storeToRefs } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useAppStore } from '@/stores/app'
import { authApi } from '@/api'
import type { LoginLog, User } from '@/api/types'
import EmptyState from '@/components/EmptyState.vue'
import Loading from '@/components/Loading.vue'

const router = useRouter()
const authStore = useAuthStore()
const appStore = useAppStore()

const { user } = storeToRefs(authStore)

const updating = ref(false)
const changingPassword = ref(false)
const loadingLogs = ref(false)

const loginLogs = ref<LoginLog[]>([])

const profileForm = reactive({
  username: '',
  email: '',
  full_name: '',
})

const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: '',
})

const avatarInput = ref<HTMLInputElement | null>(null)

const loadProfileData = () => {
  if (user.value) {
    profileForm.username = user.value.username
    profileForm.email = user.value.email
    profileForm.full_name = user.value.full_name || ''
  }
}

const loadLoginLogs = async () => {
  loadingLogs.value = true
  try {
    const response = await authApi.getLoginLogs({ page: 1, page_size: 20 })
    loginLogs.value = response.data
  } catch (error: any) {
    appStore.error(error.message || 'Failed to load login logs')
  } finally {
    loadingLogs.value = false
  }
}

const updateProfile = async () => {
  updating.value = true
  try {
    await authApi.updateProfile({
      email: profileForm.email,
      full_name: profileForm.full_name,
    })

    // Update local user data
    const updatedUser = await authApi.getProfile()
    authStore.setUser(updatedUser)

    appStore.success('Profile updated successfully')
  } catch (error: any) {
    appStore.error(error.message || 'Failed to update profile')
  } finally {
    updating.value = false
  }
}

const changePassword = async () => {
  if (passwordForm.new_password !== passwordForm.confirm_password) {
    appStore.error('Passwords do not match')
    return
  }

  if (passwordForm.new_password.length < 8) {
    appStore.error('Password must be at least 8 characters')
    return
  }

  changingPassword.value = true
  try {
    await authApi.changePassword({
      old_password: passwordForm.old_password,
      new_password: passwordForm.new_password,
    })

    appStore.success('Password changed successfully')

    // Clear form
    passwordForm.old_password = ''
    passwordForm.new_password = ''
    passwordForm.confirm_password = ''
  } catch (error: any) {
    appStore.error(error.message || 'Failed to change password')
  } finally {
    changingPassword.value = false
  }
}

const uploadAvatar = () => {
  avatarInput.value?.click()
}

const handleAvatarUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]

  if (!file) return

  // Validate file type
  if (!file.type.startsWith('image/')) {
    appStore.error('Please select an image file')
    return
  }

  // Validate file size (max 5MB)
  if (file.size > 5 * 1024 * 1024) {
    appStore.error('Image must be smaller than 5MB')
    return
  }

  // In a real implementation, you would upload to a server
  // For now, just show a success message
  appStore.success('Avatar uploaded (demo mode)')
}

const formatDate = (dateString?: string): string => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
  })
}

const formatDateTime = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleString()
}

const formatUserAgent = (userAgent: string): string => {
  // Simplify user agent string
  if (userAgent.includes('Chrome')) return 'Chrome'
  if (userAgent.includes('Firefox')) return 'Firefox'
  if (userAgent.includes('Safari')) return 'Safari'
  if (userAgent.includes('Edge')) return 'Edge'
  return 'Browser'
}

onMounted(() => {
  loadProfileData()
  loadLoginLogs()
})
</script>

<style scoped>
.profile {
  padding: 1.5rem;
  max-width: 1000px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 2rem;
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

.profile-layout {
  display: grid;
  grid-template-columns: 1fr 1.5fr;
  gap: 1.5rem;
}

.profile-card {
  grid-row: 1 / 3;
}

.settings-card-full {
  grid-column: 1 / -1;
}

.profile-card,
.settings-card {
  border-radius: 1rem;
  background: var(--bg-secondary);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.profile-header {
  padding: 2rem;
  text-align: center;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(16, 185, 129, 0.1) 100%);
}

.avatar-section {
  position: relative;
  display: inline-block;
}

.avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: var(--bg-tertiary);
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar svg {
  width: 50px;
  height: 50px;
  color: var(--text-muted);
}

.avatar-upload {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 32px;
  height: 32px;
  padding: 0;
  border: 2px solid var(--bg-secondary);
  border-radius: 50%;
  background: var(--color-primary);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.avatar-upload:hover {
  background: #2563eb;
}

.avatar-upload svg {
  width: 16px;
  height: 16px;
}

.profile-meta {
  margin-top: 1rem;
}

.profile-name {
  margin: 0 0 0.25rem;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
}

.profile-email {
  margin: 0 0 0.75rem;
  color: var(--text-secondary);
  font-size: 0.9375rem;
}

.profile-badges {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
}

.badge {
  padding: 0.25rem 0.625rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.badge-admin {
  background: rgba(139, 92, 246, 0.1);
  color: #8b5cf6;
}

.badge-active {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.profile-stats {
  display: flex;
  justify-content: center;
  padding: 1.5rem;
  border-top: 1px solid var(--border-color, rgba(255, 255, 255, 0.1));
}

.stat {
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.stat-label {
  font-size: 0.8125rem;
  color: var(--text-muted);
}

.card-header {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--border-color, rgba(255, 255, 255, 0.1));
}

.card-title {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.card-body {
  padding: 1.5rem;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.form-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.form-input {
  padding: 0.625rem 0.875rem;
  border: 1px solid var(--border-color, rgba(255, 255, 255, 0.1));
  border-radius: 0.5rem;
  background: var(--bg-tertiary);
  color: var(--text-primary);
  font-size: 0.875rem;
}

.form-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.form-input:focus {
  outline: none;
  border-color: var(--color-primary);
}

.form-hint {
  font-size: 0.8125rem;
  color: var(--text-muted);
}

.form-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.625rem 1.5rem;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
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

.logs-loading,
.logs-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
}

.logs-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.log-entry {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-radius: 0.5rem;
  background: var(--bg-tertiary);
}

.log-icon {
  flex-shrink: 0;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.log-entry.log-success .log-icon {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.log-entry.log-failed .log-icon {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.log-icon svg {
  width: 1rem;
  height: 1rem;
}

.log-details {
  flex: 1;
}

.log-time {
  font-weight: 500;
  color: var(--text-primary);
}

.log-info {
  display: flex;
  gap: 0.75rem;
  margin-top: 0.125rem;
  font-size: 0.875rem;
  color: var(--text-muted);
}

.log-status {
  flex-shrink: 0;
}

.status-badge {
  padding: 0.25rem 0.625rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: capitalize;
}

.status-success {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.status-failed {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

@media (max-width: 768px) {
  .profile {
    padding: 1rem;
  }

  .profile-layout {
    grid-template-columns: 1fr;
  }

  .profile-card {
    grid-row: auto;
  }

  .logs-entry {
    flex-wrap: wrap;
  }
}
</style>
