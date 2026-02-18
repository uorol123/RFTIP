<template>
  <div class="login-page">
    <GlobeBackground />

    <!-- 主内容区 -->
    <div class="content-wrapper">
      <!-- Header -->
      <header class="header">
        <router-link to="/" class="logo">
          <div class="logo-icon">
            <svg viewBox="0 0 48 48" fill="none" class="w-6 h-6">
              <circle cx="24" cy="24" r="16" stroke="white" stroke-width="2.5" opacity="0.3"/>
              <circle cx="24" cy="24" r="10" stroke="white" stroke-width="2" opacity="0.6"/>
              <line x1="24" y1="24" x2="38" y2="12" stroke="white" stroke-width="2.5" stroke-linecap="round"/>
              <circle cx="38" cy="12" r="4" fill="white"/>
            </svg>
          </div>
          <span class="logo-text">RFTIP</span>
        </router-link>

        <router-link to="/" class="back-link">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
          返回首页
        </router-link>
      </header>

      <!-- Main Content -->
      <main class="main-content">
        <div class="login-card">
          <!-- Card Header -->
          <div class="card-header">
            <div class="card-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-8 h-8">
                <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/>
                <circle cx="12" cy="7" r="4"/>
              </svg>
            </div>
            <h2 class="card-title">欢迎回来</h2>
            <p class="card-subtitle">登录以继续您的数据分析之旅</p>
          </div>

          <!-- Form -->
          <form @submit.prevent="handleLogin" class="login-form">
            <!-- Username Field -->
            <div class="form-field">
              <label for="username" class="field-label">
                用户名或邮箱
              </label>
              <div class="input-wrapper">
                <div class="input-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-5 h-5">
                    <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/>
                    <circle cx="12" cy="7" r="4"/>
                  </svg>
                </div>
                <input
                  id="username"
                  v-model="form.username"
                  type="text"
                  placeholder="输入用户名或邮箱"
                  required
                  autocomplete="username"
                  :disabled="loading"
                  class="form-input"
                />
              </div>
            </div>

            <!-- Password Field -->
            <div class="form-field">
              <label for="password" class="field-label">
                密码
              </label>
              <div class="input-wrapper">
                <div class="input-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-5 h-5">
                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                    <path d="M7 11V7a5 5 0 0110 0v4"/>
                  </svg>
                </div>
                <input
                  id="password"
                  v-model="form.password"
                  :type="showPassword ? 'text' : 'password'"
                  placeholder="输入密码"
                  required
                  autocomplete="current-password"
                  :disabled="loading"
                  class="form-input pr-12"
                />
                <button
                  type="button"
                  @click="showPassword = !showPassword"
                  class="password-toggle"
                >
                  <svg v-if="!showPassword" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-5 h-5">
                    <path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                    <path d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                  </svg>
                  <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-5 h-5">
                    <path d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/>
                  </svg>
                </button>
              </div>
            </div>

            <!-- Remember & Forgot -->
            <div class="form-actions">
              <label class="checkbox-label">
                <input type="checkbox" v-model="form.remember" class="sr-only peer">
                <div class="checkbox-custom"></div>
                <span>记住我</span>
              </label>
              <router-link to="/forgot-password" class="forgot-link">
                忘记密码？
              </router-link>
            </div>

            <!-- Submit Button -->
            <button
              type="submit"
              :disabled="loading || !form.username || !form.password"
              class="submit-btn"
            >
              <svg v-if="loading" viewBox="0 0 24 24" fill="none" class="w-5 h-5 animate-spin">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" opacity="0.25"/>
                <path d="M12 2A10 10 0 0112 22" stroke="currentColor" stroke-width="4" fill="none" stroke-linecap="round"/>
              </svg>
              <span>{{ loading ? '登录中...' : '登录' }}</span>
            </button>
          </form>

          <!-- Footer -->
          <div class="card-footer">
            <p>还没有账号？
              <router-link to="/register" class="register-link">
                立即注册
              </router-link>
            </p>
          </div>
        </div>

        <!-- Copyright -->
        <p class="copyright">© 2026 RFTIP. All rights reserved.</p>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useAppStore } from '@/stores/app'
import GlobeBackground from '@/components/GlobeBackground.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const appStore = useAppStore()

const loading = ref(false)
const showPassword = ref(false)

const form = reactive({
  username: '',
  password: '',
  remember: false,
})

async function handleLogin() {
  loading.value = true

  try {
    // 使用 URL-encoded 格式发送登录请求
    const params = new URLSearchParams()
    params.append('username', form.username)
    params.append('password', form.password)

    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: params,
    }).then(res => {
      if (!res.ok) throw new Error('登录失败，请检查用户名和密码')
      return res.json()
    })

    // Store auth data
    authStore.setToken(response.access_token)
    authStore.setUser(response.user)

    // Show success message
    appStore.success('登录成功！')

    // Redirect to dashboard or return URL
    const redirect = (route.query.redirect as string) || '/dashboard'
    router.push(redirect)
  } catch (error: any) {
    appStore.error(error.message || '登录失败，请检查用户名和密码')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  position: relative;
  width: 100%;
  height: 100vh;
  overflow: hidden;
}

.content-wrapper {
  position: relative;
  z-index: 10;
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* Header */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 32px;
  flex-shrink: 0;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
}

.logo-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.logo-text {
  font-size: 18px;
  font-weight: 700;
  color: white;
  letter-spacing: 0.5px;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  border-radius: 8px;
  transition: all 0.2s;
  cursor: pointer;
}

.back-link:hover {
  color: white;
  background: rgba(255, 255, 255, 0.1);
}

/* Main Content */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px 32px 32px;
}

.login-card {
  width: 100%;
  max-width: 420px;
  background: rgba(17, 24, 39, 0.8);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 32px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

/* Card Header */
.card-header {
  text-align: center;
  margin-bottom: 28px;
}

.card-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 16px;
  border-radius: 16px;
  background: linear-gradient(135deg, #3b82f6, #10b981);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 20px rgba(59, 130, 246, 0.3);
  color: white;
}

.card-title {
  font-size: 24px;
  font-weight: 700;
  color: white;
  margin: 0 0 8px;
}

.card-subtitle {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
}

/* Form */
.login-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 24px;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.field-label {
  font-size: 13px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 14px;
  color: rgba(255, 255, 255, 0.4);
  pointer-events: none;
}

.form-input {
  width: 100%;
  padding: 12px 14px 12px 44px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: white;
  font-size: 14px;
  transition: all 0.2s;
}

.form-input::placeholder {
  color: rgba(255, 255, 255, 0.3);
}

.form-input:focus {
  outline: none;
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(59, 130, 246, 0.5);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.form-input.pr-12 {
  padding-right: 48px;
}

.password-toggle {
  position: absolute;
  right: 12px;
  color: rgba(255, 255, 255, 0.4);
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  transition: color 0.2s;
}

.password-toggle:hover {
  color: rgba(255, 255, 255, 0.7);
}

/* Form Actions */
.form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
}

.checkbox-custom {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 6px;
  transition: all 0.2s;
  position: relative;
}

.peer:checked ~ .checkbox-custom {
  background: rgba(59, 130, 246, 0.2);
  border-color: #3b82f6;
}

.peer:checked ~ .checkbox-custom::after {
  content: '';
  position: absolute;
  top: 2px;
  left: 5px;
  width: 4px;
  height: 8px;
  border: solid #3b82f6;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.forgot-link {
  font-size: 13px;
  color: #3b82f6;
  text-decoration: none;
  transition: color 0.2s;
}

.forgot-link:hover {
  color: #60a5fa;
}

/* Submit Button */
.submit-btn {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #3b82f6, #10b981);
  border: none;
  border-radius: 12px;
  color: white;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
}

.submit-btn:active:not(:disabled) {
  transform: translateY(0);
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

/* Card Footer */
.card-footer {
  text-align: center;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.card-footer p {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
}

.register-link {
  color: #3b82f6;
  text-decoration: none;
  font-weight: 600;
  transition: color 0.2s;
}

.register-link:hover {
  color: #60a5fa;
}

/* Copyright */
.copyright {
  text-align: center;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
  margin-top: 20px;
}

/* Responsive */
@media (max-width: 640px) {
  .header {
    padding: 12px 20px;
  }

  .main-content {
    padding: 16px 20px 24px;
  }

  .login-card {
    padding: 24px;
    border-radius: 16px;
  }

  .card-title {
    font-size: 20px;
  }
}
</style>
