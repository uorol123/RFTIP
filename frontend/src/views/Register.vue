<template>
  <div class="register-page">
    <div class="register-background"></div>
    <div class="register-container">
      <div class="register-content glass">
        <div class="register-header">
          <div class="register-logo">
            <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
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
            <span>RFTIP</span>
          </div>
          <h1>Create Account</h1>
          <p>Register to access the Radar Tracking Platform</p>
        </div>
        <form @submit.prevent="handleRegister" class="register-form">
          <div class="form-row">
            <div class="form-group">
              <label for="username">Username</label>
              <div class="input-wrapper">
                <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/>
                  <circle cx="12" cy="7" r="4"/>
                </svg>
                <input
                  id="username"
                  v-model="form.username"
                  type="text"
                  placeholder="Enter username"
                  required
                  autocomplete="username"
                  :disabled="loading"
                  minlength="3"
                  maxlength="50"
                />
              </div>
            </div>
            <div class="form-group">
              <label for="email">Email</label>
              <div class="input-wrapper">
                <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
                </svg>
                <input
                  id="email"
                  v-model="form.email"
                  type="email"
                  placeholder="Enter email"
                  required
                  autocomplete="email"
                  :disabled="loading"
                />
              </div>
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label for="fullName">Full Name (Optional)</label>
              <div class="input-wrapper">
                <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                </svg>
                <input
                  id="fullName"
                  v-model="form.full_name"
                  type="text"
                  placeholder="Enter full name"
                  autocomplete="name"
                  :disabled="loading"
                />
              </div>
            </div>
            <div class="form-group"></div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label for="password">Password</label>
              <div class="input-wrapper">
                <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                  <path d="M7 11V7a5 5 0 0110 0v4"/>
                </svg>
                <input
                  id="password"
                  v-model="form.password"
                  type="password"
                  placeholder="Enter password"
                  required
                  autocomplete="new-password"
                  :disabled="loading"
                  minlength="8"
                />
              </div>
            </div>
            <div class="form-group">
              <label for="confirmPassword">Confirm Password</label>
              <div class="input-wrapper">
                <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
                </svg>
                <input
                  id="confirmPassword"
                  v-model="form.confirmPassword"
                  type="password"
                  placeholder="Enter password again"
                  required
                  autocomplete="new-password"
                  :disabled="loading"
                />
              </div>
            </div>
          </div>
          <div class="form-options">
            <label class="checkbox-wrapper">
              <input type="checkbox" v-model="form.agreeToTerms" required />
              <span>I agree to <a href="#" class="terms-link">Terms of Service</a> and <a href="#" class="terms-link">Privacy Policy</a></span>
            </label>
          </div>
          <button type="submit" class="submit-btn" :disabled="loading">
            <svg v-if="!loading" class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"/>
            </svg>
            <svg v-else class="btn-icon spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
            </svg>
            {{ loading ? 'Creating Account...' : 'Create Account' }}
          </button>
        </form>
        <div class="register-footer">
          <p>Already have an account? <router-link to="/login">Login</router-link></p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useAppStore } from '@/stores/app'
import { authApi } from '@/api'

const router = useRouter()
const authStore = useAuthStore()
const appStore = useAppStore()

const loading = ref(false)

const form = reactive({
  username: '',
  email: '',
  full_name: '',
  password: '',
  confirmPassword: '',
  agreeToTerms: false,
})

async function handleRegister() {
  // Password validation
  if (form.password !== form.confirmPassword) {
    appStore.error('Passwords do not match')
    return
  }

  if (form.password.length < 8) {
    appStore.error('Password must be at least 8 characters')
    return
  }

  if (!form.agreeToTerms) {
    appStore.error('Please agree to the Terms of Service')
    return
  }

  loading.value = true

  try {
    const response = await authApi.register({
      username: form.username,
      email: form.email,
      password: form.password,
      full_name: form.full_name || undefined,
    })

    // Store auth data (auto-login after registration)
    authStore.setToken(response.access_token)
    authStore.setUser(response.user)

    // Show success message
    appStore.success('注册成功！Welcome to RFTIP!')

    // Redirect to dashboard
    router.push('/dashboard')
  } catch (error: any) {
    appStore.error(error.message || 'Registration failed. Please try again.')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-primary);
  position: relative;
  overflow: hidden;
  transition: background 0.3s ease;
}

.register-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(ellipse 60% 40% at 20% 30%, rgba(59, 130, 246, 0.06), transparent), radial-gradient(ellipse 50% 30% at 80% 70%, rgba(16, 185, 129, 0.04), transparent);
  pointer-events: none;
}

.register-container {
  width: 100%;
  max-width: 520px;
  padding: 2rem;
  position: relative;
  z-index: 1;
}

.register-content {
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);
  border-radius: 1.5rem;
  padding: 2.5rem;
  box-shadow: var(--shadow-xl);
  transition: background 0.3s ease, border-color 0.3s ease;
}

.register-header {
  text-align: center;
  margin-bottom: 2rem;
}

.register-logo {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.register-logo svg {
  width: 48px;
  height: 48px;
}

.register-logo span {
  font-size: 1.5rem;
  font-weight: 700;
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.register-header h1 {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.register-header p {
  color: var(--text-secondary);
  font-size: 0.9375rem;
}

.register-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

@media (max-width: 640px) {
  .form-row {
    grid-template-columns: 1fr;
    gap: 1.25rem;
  }
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 1rem;
  width: 20px;
  height: 20px;
  color: var(--text-muted);
  pointer-events: none;
}

.form-group input {
  width: 100%;
  padding: 0.875rem 1rem 0.875rem 3rem;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 0.75rem;
  font-size: 0.9375rem;
  color: var(--text-primary);
  transition: all 0.2s ease;
}

.form-group input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.form-group input::placeholder {
  color: var(--text-muted);
}

.form-group input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-group input:hover:not(:focus):not(:disabled) {
  border-color: var(--border-hover);
}

.form-options {
  display: flex;
  align-items: center;
  font-size: 0.875rem;
}

.checkbox-wrapper {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  color: var(--text-secondary);
  cursor: pointer;
  line-height: 1.5;
}

.checkbox-wrapper input {
  width: 16px;
  height: 16px;
  accent-color: var(--color-primary);
  margin-top: 0.125rem;
  flex-shrink: 0;
  cursor: pointer;
}

.terms-link {
  color: var(--color-primary);
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s ease;
}

.terms-link:hover {
  color: var(--color-primary-light);
  text-decoration: underline;
}

.submit-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.875rem;
  background: var(--gradient-primary);
  color: #fff;
  border: none;
  border-radius: 0.75rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s ease;
  box-shadow: var(--shadow-md);
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.btn-icon {
  width: 18px;
  height: 18px;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.register-footer {
  text-align: center;
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border-color);
  color: var(--text-secondary);
  font-size: 0.9375rem;
}

.register-footer a {
  color: var(--color-primary);
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s ease;
}

.register-footer a:hover {
  color: var(--color-primary-light);
  text-decoration: underline;
}

@media (max-width: 640px) {
  .register-container {
    padding: 1rem;
  }

  .register-content {
    padding: 2rem 1.5rem;
  }

  .register-logo svg {
    width: 40px;
    height: 40px;
  }

  .register-logo span {
    font-size: 1.25rem;
  }

  .register-header h1 {
    font-size: 1.5rem;
  }
}
</style>
