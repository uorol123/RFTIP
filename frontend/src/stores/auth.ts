import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface User {
  id: number
  username: string
  email: string
  avatarUrl?: string
  role: 'user' | 'admin'
  isActive: boolean
  createdAt: string
  updatedAt: string
}

export const useAuthStore = defineStore(
  'auth',
  () => {
    // State
    const token = ref<string | null>(localStorage.getItem('token'))
    const user = ref<User | null>(null)

    // Getters
    const isAuthenticated = computed(() => !!token.value)
    const isAdmin = computed(() => user.value?.role === 'admin')

    // Actions
    function setToken(newToken: string) {
      token.value = newToken
      localStorage.setItem('token', newToken)
    }

    function setUser(newUser: User) {
      user.value = newUser
    }

    function logout() {
      token.value = null
      user.value = null
      localStorage.removeItem('token')
    }

    // 初始化时从 localStorage 加载用户信息
    function loadUserFromStorage() {
      const savedUser = localStorage.getItem('user')
      if (savedUser) {
        try {
          user.value = JSON.parse(savedUser)
        } catch (e) {
          console.error('Failed to parse user from localStorage:', e)
        }
      }
    }

    function saveUserToStorage() {
      if (user.value) {
        localStorage.setItem('user', JSON.stringify(user.value))
      }
    }

    // 调用一次以加载用户信息
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
