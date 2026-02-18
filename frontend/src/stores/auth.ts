import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

// 与后端 UserResponse 保持一致的用户接口
export interface User {
  id: number
  username: string
  email: string
  full_name?: string
  phone?: string
  is_active: boolean
  is_superuser: boolean
  is_admin: boolean  // 前端计算字段，与 is_superuser 相同
  avatar_url?: string
  avatar?: string  // 前端兼容字段，与 avatar_url 相同
  created_at: string
  updated_at: string
}

export const useAuthStore = defineStore(
  'auth',
  () => {
    // State
    const token = ref<string | null>(localStorage.getItem('token'))
    const user = ref<User | null>(null)

    // Getters
    const isAuthenticated = computed(() => !!token.value && !!user.value)
    const isAdmin = computed(() => user.value?.is_superuser || user.value?.is_admin || false)

    // Actions
    function setToken(newToken: string) {
      token.value = newToken
      localStorage.setItem('token', newToken)
    }

    function setUser(newUser: User) {
      // 确保 is_admin 字段存在
      if (newUser && !('is_admin' in newUser)) {
        newUser = { ...newUser, is_admin: newUser.is_superuser }
      }
      // 确保 avatar 字段存在
      if (newUser && !('avatar' in newUser)) {
        newUser = { ...newUser, avatar: newUser.avatar_url }
      }
      user.value = newUser
      saveUserToStorage()
    }

    function updateUser(partialUser: Partial<User>) {
      if (user.value) {
        user.value = { ...user.value, ...partialUser }
        saveUserToStorage()
      }
    }

    function logout() {
      token.value = null
      user.value = null
      localStorage.removeItem('token')
      localStorage.removeItem('auth_user')
    }

    function saveUserToStorage() {
      if (user.value) {
        localStorage.setItem('auth_user', JSON.stringify(user.value))
      } else {
        localStorage.removeItem('auth_user')
      }
    }

    function loadUserFromStorage() {
      const savedUser = localStorage.getItem('auth_user')
      if (savedUser) {
        try {
          const parsed = JSON.parse(savedUser)
          // 确保兼容字段存在
          if (!('is_admin' in parsed)) {
            parsed.is_admin = parsed.is_superuser || false
          }
          if (!('avatar' in parsed)) {
            parsed.avatar = parsed.avatar_url || null
          }
          user.value = parsed
        } catch (e) {
          console.error('Failed to parse user from localStorage:', e)
        }
      }
    }

    // 初始化时从 localStorage 加载用户信息
    loadUserFromStorage()

    return {
      // State
      token,
      user,
      // Getters
      isAuthenticated,
      isAdmin,
      // Actions
      setToken,
      setUser,
      updateUser,
      logout,
      loadUserFromStorage,
      saveUserToStorage,
    }
  },
  {
    persist: {
      enabled: true,
      strategies: [
        {
          key: 'auth',
          storage: localStorage,
        },
      ],
    },
  }
)
