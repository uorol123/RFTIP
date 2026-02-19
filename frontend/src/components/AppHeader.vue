<template>
  <header class="app-header">
    <div class="header-container">
      <div class="header-brand">
        <router-link to="/dashboard" class="brand-link">
          <svg class="brand-icon" viewBox="0 0 48 48" fill="none">
            <circle cx="24" cy="24" r="20" stroke="url(#grad1)" stroke-width="2"/>
            <circle cx="24" cy="24" r="14" stroke="url(#grad1)" stroke-width="1.5" stroke-opacity="0.6"/>
            <circle cx="24" cy="24" r="8" stroke="url(#grad1)" stroke-width="1" stroke-opacity="0.3"/>
            <line x1="24" y1="24" x2="40" y2="10" stroke="url(#grad1)" stroke-width="2" stroke-linecap="round"/>
            <circle cx="40" cy="10" r="3" fill="url(#grad1)"/>
            <defs>
              <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#3B82F6"/>
                <stop offset="100%" stop-color="#10B981"/>
              </linearGradient>
            </defs>
          </svg>
          <span class="brand-text">RFTIP</span>
        </router-link>
      </div>

      <nav class="header-nav">
        <router-link to="/dashboard" class="nav-item" active-class="active">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
          </svg>
          仪表板
        </router-link>
        <router-link to="/data" class="nav-item" active-class="active">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
          </svg>
          数据管理
        </router-link>
        <router-link to="/tracks" class="nav-item" active-class="active">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"/>
          </svg>
          轨迹可视化
        </router-link>
        <router-link to="/zones" class="nav-item" active-class="active">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
          </svg>
          禁飞区
        </router-link>
      </nav>

      <div class="header-actions">
        <ThemeSwitch />
        <div class="user-menu" ref="userMenuRef">
          <button class="user-button" @click="toggleUserMenu">
            <div class="user-avatar">
              <img v-if="avatarUrl" :src="avatarUrl" :alt="user?.username" />
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
              </svg>
            </div>
            <span class="user-name">{{ user?.full_name || user?.username }}</span>
            <svg class="dropdown-icon" :class="{ open: showUserMenu }" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
            </svg>
          </button>
          <div v-if="showUserMenu" class="user-dropdown">
            <div class="dropdown-header">
              <div class="dropdown-avatar">
                <img v-if="avatarUrl" :src="avatarUrl" :alt="user?.username" />
                <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                </svg>
              </div>
              <div class="dropdown-user-info">
                <div class="dropdown-user-name">{{ user?.full_name || user?.username }}</div>
                <div class="dropdown-user-email">{{ user?.email }}</div>
              </div>
            </div>
            <div class="dropdown-divider"></div>
            <button class="dropdown-item" @click="openProfileDialog">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
              </svg>
              个人资料
            </button>
            <button class="dropdown-item" @click="openChangePasswordDialog">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"/>
              </svg>
              修改密码
            </button>
            <div class="dropdown-divider"></div>
            <button class="dropdown-item dropdown-item-danger" @click="handleLogout">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
              </svg>
              退出登录
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 个人资料弹窗 -->
    <UserProfileDialog
      v-if="showProfileDialog"
      :user="user"
      :avatar-url="avatarUrl"
      @close="closeProfileDialog"
      @updated="handleProfileUpdated"
    />

    <!-- 修改密码弹窗 -->
    <ChangePasswordDialog
      v-if="showChangePasswordDialog"
      @close="closeChangePasswordDialog"
    />
  </header>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useAuthStore } from '@/stores/auth'
import { useAppStore } from '@/stores/app'
import { authApi } from '@/api/auth'
import ThemeSwitch from './ThemeSwitch.vue'
import UserProfileDialog from './UserProfileDialog.vue'
import ChangePasswordDialog from './ChangePasswordDialog.vue'

const router = useRouter()
const authStore = useAuthStore()
const appStore = useAppStore()

const { user } = storeToRefs(authStore)

const showUserMenu = ref(false)
const showProfileDialog = ref(false)
const showChangePasswordDialog = ref(false)
const userMenuRef = ref<HTMLElement>()

const avatarUrl = computed(() => {
  if (user.value?.avatar_url) {
    return `${import.meta.env.VITE_API_BASE_URL || '/api'}/auth/avatar/${user.value.id}?t=${Date.now()}`
  }
  return null
})

const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value
}

const closeUserMenu = () => {
  showUserMenu.value = false
}

const openProfileDialog = () => {
  closeUserMenu()
  showProfileDialog.value = true
}

const closeProfileDialog = () => {
  showProfileDialog.value = false
}

const openChangePasswordDialog = () => {
  closeUserMenu()
  showChangePasswordDialog.value = true
}

const closeChangePasswordDialog = () => {
  showChangePasswordDialog.value = false
}

const handleProfileUpdated = async (updatedUser: any) => {
  authStore.setUser(updatedUser)
  appStore.success('个人资料已更新')
}

const handleLogout = async () => {
  closeUserMenu()
  try {
    await authApi.logout()
  } catch (error) {
    // Ignore logout API errors
  } finally {
    authStore.logout()
    router.push('/login')
  }
}

const handleClickOutside = (event: MouseEvent) => {
  if (userMenuRef.value && !userMenuRef.value.contains(event.target as Node)) {
    closeUserMenu()
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.app-header {
  background: var(--backdrop-bg);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--border-color);
  position: sticky;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
}

.header-container {
  max-width: 1600px;
  margin: 0 auto;
  padding: 0.75rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 2rem;
}

.header-brand {
  flex-shrink: 0;
}

.brand-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  text-decoration: none;
}

.brand-icon {
  width: 36px;
  height: 36px;
  flex-shrink: 0;
}

.brand-text {
  font-size: 1.25rem;
  font-weight: 700;
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-nav {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1rem;
  border-radius: 0.625rem;
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.2s;
}

.nav-item:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.nav-item.active {
  background: var(--color-primary);
  color: white;
}

.nav-item svg {
  width: 1.125rem;
  height: 1.125rem;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-shrink: 0;
}

.user-menu {
  position: relative;
}

.user-button {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.375rem 0.75rem 0.375rem 0.375rem;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 2rem;
  cursor: pointer;
  transition: all 0.2s;
}

.user-button:hover {
  background: var(--bg-tertiary);
  border-color: var(--border-hover);
}

.user-avatar {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  background: var(--gradient-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-avatar svg {
  width: 1.25rem;
  height: 1.25rem;
  color: white;
}

.user-name {
  max-width: 120px;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dropdown-icon {
  width: 1rem;
  height: 1rem;
  color: var(--text-muted);
  transition: transform 0.2s;
}

.dropdown-icon.open {
  transform: rotate(180deg);
}

.user-dropdown {
  position: absolute;
  top: calc(100% + 0.5rem);
  right: 0;
  min-width: 260px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-color);
  border-radius: 0.75rem;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  animation: dropIn 0.2s ease;
}

@keyframes dropIn {
  from {
    opacity: 0;
    transform: translateY(-8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.dropdown-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background: var(--bg-secondary);
}

.dropdown-avatar {
  width: 3rem;
  height: 3rem;
  border-radius: 50%;
  background: var(--gradient-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  flex-shrink: 0;
}

.dropdown-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.dropdown-avatar svg {
  width: 1.5rem;
  height: 1.5rem;
  color: white;
}

.dropdown-user-info {
  flex: 1;
  min-width: 0;
}

.dropdown-user-name {
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dropdown-user-email {
  font-size: 0.8125rem;
  color: var(--text-muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dropdown-divider {
  height: 1px;
  background: var(--border-color);
  margin: 0;
}

.dropdown-item {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background: transparent;
  border: none;
  color: var(--text-secondary);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s;
}

.dropdown-item:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.dropdown-item svg {
  width: 1.125rem;
  height: 1.125rem;
}

.dropdown-item-danger {
  color: #ef4444;
}

.dropdown-item-danger:hover {
  background: rgba(239, 68, 68, 0.1);
}

@media (max-width: 1024px) {
  .header-nav {
    display: none;
  }
}

@media (max-width: 640px) {
  .header-container {
    padding: 0.75rem 1rem;
  }

  .user-name {
    display: none;
  }

  .user-button {
    padding: 0.375rem;
  }
}
</style>
