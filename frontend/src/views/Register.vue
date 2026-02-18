<template>
  <div class="register-page">
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
        <div class="register-container">
          <!-- Page Title -->
          <div class="page-header">
            <div class="page-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-10 h-10">
                <path d="M16 21v-2a4 4 0 00-4-4H6a4 4 0 00-4 4v2"/>
                <circle cx="9" cy="7" r="4"/>
                <path d="M22 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75"/>
              </svg>
            </div>
            <h1 class="page-title">创建账户</h1>
            <p class="page-subtitle">开启您的智能数据分析之旅</p>
          </div>

          <!-- Registration Form -->
          <form @submit.prevent="handleRegister" class="register-form">
            <!-- Avatar Upload Section -->
            <div class="avatar-section">
              <div class="avatar-wrapper">
                <!-- Avatar Preview -->
                <div class="avatar-preview">
                  <img
                    v-if="avatarPreview"
                    :src="avatarPreview"
                    alt="Avatar"
                    class="avatar-img"
                  />
                  <div v-else class="avatar-placeholder">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="w-12 h-12">
                      <path d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                    </svg>
                  </div>
                </div>

                <!-- Upload Button -->
                <label class="avatar-upload-btn" @click="handleAvatarUploadClick">
                  <input
                    ref="avatarInputRef"
                    type="file"
                    accept="image/*"
                    @change="handleAvatarSelect"
                    class="hidden"
                  />
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4">
                    <path d="M12 4v16m8-8H4"/>
                  </svg>
                </label>

                <!-- Remove Button -->
                <button
                  v-if="avatarPreview"
                  type="button"
                  @click="removeAvatar"
                  class="avatar-remove-btn"
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-3 h-3">
                    <path d="M6 18L18 6M6 6l12 12"/>
                  </svg>
                </button>
              </div>
            </div>

            <!-- Form Fields Grid -->
            <div class="form-fields">
              <!-- Username -->
              <div class="form-field">
                <label class="field-label">用户名</label>
                <div class="input-wrapper">
                  <div class="input-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4">
                      <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/>
                      <circle cx="12" cy="7" r="4"/>
                    </svg>
                  </div>
                  <input
                    v-model="form.username"
                    type="text"
                    placeholder="3-50个字符"
                    required
                    autocomplete="username"
                    :disabled="loading"
                    minlength="3"
                    maxlength="50"
                    class="form-input"
                  />
                </div>
              </div>

              <!-- Email -->
              <div class="form-field">
                <label class="field-label">邮箱地址</label>
                <div class="input-wrapper">
                  <div class="input-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4">
                      <path d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
                    </svg>
                  </div>
                  <input
                    v-model="form.email"
                    type="email"
                    placeholder="example@email.com"
                    required
                    autocomplete="email"
                    :disabled="loading"
                    class="form-input"
                    :class="{ 'has-error': errors.email }"
                    @blur="validateField('email')"
                  />
                </div>
                <span v-if="errors.email" class="field-error">{{ errors.email }}</span>
              </div>

              <!-- Verification Code -->
              <div class="form-field form-field-full">
                <label class="field-label">验证码</label>
                <div class="code-input-group">
                  <div class="input-wrapper input-wrapper-flex">
                    <div class="input-icon">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4">
                        <path d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
                      </svg>
                    </div>
                    <input
                      v-model="form.verification_code"
                      type="text"
                      placeholder="6位数字"
                      required
                      :disabled="loading"
                      maxlength="6"
                      pattern="[0-9]{6}"
                      class="form-input"
                    />
                  </div>
                  <button
                    type="button"
                    :disabled="!canSendCode || codeSending"
                    @click="handleSendCode"
                    class="code-btn"
                  >
                    {{ codeButtonText }}
                  </button>
                </div>
              </div>

              <!-- Password -->
              <div class="form-field">
                <label class="field-label">密码</label>
                <div class="input-wrapper">
                  <div class="input-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4">
                      <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                      <path d="M7 11V7a5 5 0 0110 0v4"/>
                    </svg>
                  </div>
                  <input
                    v-model="form.password"
                    :type="showPassword ? 'text' : 'password'"
                    placeholder="至少6位"
                    required
                    autocomplete="new-password"
                    :disabled="loading"
                    minlength="6"
                    class="form-input pr-10"
                    :class="{ 'has-error': errors.password }"
                    @blur="validateField('password')"
                  />
                  <button
                    type="button"
                    @click="showPassword = !showPassword"
                    class="password-toggle"
                  >
                    <svg v-if="!showPassword" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4">
                      <path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                      <path d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                    </svg>
                    <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4">
                      <path d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/>
                    </svg>
                  </button>
                </div>
                <span v-if="errors.password" class="field-error">{{ errors.password }}</span>
              </div>

              <!-- Confirm Password -->
              <div class="form-field">
                <label class="field-label">确认密码</label>
                <div class="input-wrapper">
                  <div class="input-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4">
                      <path d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
                    </svg>
                  </div>
                  <input
                    v-model="form.confirm_password"
                    :type="showConfirmPassword ? 'text' : 'password'"
                    placeholder="再次输入"
                    required
                    autocomplete="new-password"
                    :disabled="loading"
                    class="form-input pr-10"
                    :class="{ 'has-error': errors.confirm_password }"
                    @blur="validateField('confirm_password')"
                  />
                  <button
                    type="button"
                    @click="showConfirmPassword = !showConfirmPassword"
                    class="password-toggle"
                  >
                    <svg v-if="!showConfirmPassword" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4">
                      <path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                      <path d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                    </svg>
                    <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4">
                      <path d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/>
                    </svg>
                  </button>
                </div>
                <span v-if="errors.confirm_password" class="field-error">{{ errors.confirm_password }}</span>
              </div>

              <!-- Full Name (Optional) -->
              <div class="form-field form-field-full">
                <label class="field-label">全名（可选）</label>
                <div class="input-wrapper">
                  <div class="input-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4">
                      <path d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                    </svg>
                  </div>
                  <input
                    v-model="form.full_name"
                    type="text"
                    placeholder="请输入您的全名"
                    autocomplete="name"
                    :disabled="loading"
                    maxlength="100"
                    class="form-input"
                  />
                </div>
              </div>

              <!-- Phone (Optional) -->
              <div class="form-field form-field-full">
                <label class="field-label">手机号（可选）</label>
                <div class="input-wrapper">
                  <div class="input-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4">
                      <path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6 19.79 19.79 0 01-3.07-8.67A2 2 0 014.11 2h3a2 2 0 012 1.72 12.84 12.84 0 00.7 2.81 2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45 12.84 12.84 0 002.81.7A2 2 0 0122 16.92z"/>
                    </svg>
                  </div>
                  <input
                    v-model="form.phone"
                    type="tel"
                    placeholder="请输入手机号"
                    autocomplete="tel"
                    :disabled="loading"
                    maxlength="11"
                    class="form-input"
                    :class="{ 'has-error': errors.phone }"
                    @blur="validateField('phone')"
                  />
                </div>
                <span v-if="errors.phone" class="field-error">{{ errors.phone }}</span>
              </div>
            </div>

            <!-- Terms -->
            <div class="terms-section">
              <label class="checkbox-label">
                <input type="checkbox" v-model="form.agreeToTerms" class="sr-only peer">
                <div class="checkbox-custom"></div>
                <span>我已阅读并同意
                  <router-link to="/terms" class="link">服务条款</router-link>
                  和
                  <router-link to="/privacy" class="link">隐私政策</router-link>
                </span>
              </label>
            </div>

            <!-- Submit Button -->
            <button
              type="submit"
              :disabled="loading || !isFormValid"
              class="submit-btn"
            >
              <svg v-if="loading" viewBox="0 0 24 24" fill="none" class="w-5 h-5 animate-spin">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" opacity="0.25"/>
                <path d="M12 2A10 10 0 0112 22" stroke="currentColor" stroke-width="4" fill="none" stroke-linecap="round"/>
              </svg>
              <span>{{ loading ? '注册中...' : '创建账户' }}</span>
            </button>
          </form>

          <!-- Footer -->
          <div class="footer">
            <p>已有账号？
              <router-link to="/login" class="login-link">
                立即登录
              </router-link>
            </p>
          </div>

          <!-- Copyright -->
          <p class="copyright">© 2026 RFTIP. All rights reserved.</p>
        </div>
      </main>
    </div>

    <!-- Avatar Cropper Modal -->
    <div v-if="showCropper" class="modal-overlay">
      <div class="modal-content">
        <div class="modal-header">
          <h3>裁剪头像</h3>
          <button type="button" @click="closeCropper" class="modal-close">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-5 h-5">
              <path d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>

        <div class="cropper-wrapper">
          <Cropper
            ref="cropperRef"
            :src="imageToCrop"
            :stencil-props="{
              aspectRatio: 1,
              movable: true,
              resizable: true,
            }"
            :canvas="{
              width: 300,
              height: 300,
            }"
            class="cropper"
          />
        </div>

        <div class="modal-actions">
          <button type="button" @click="closeCropper" class="btn-secondary" :disabled="avatarUploading">取消</button>
          <button type="button" @click="confirmCrop" class="btn-primary" :disabled="avatarUploading">
            <svg v-if="avatarUploading" viewBox="0 0 24 24" fill="none" class="w-4 h-4 animate-spin">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" opacity="0.25"/>
              <path d="M12 2A10 10 0 0112 22" stroke="currentColor" stroke-width="4" fill="none" stroke-linecap="round"/>
            </svg>
            <span>{{ avatarUploading ? '上传中...' : '确认裁剪' }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useAppStore } from '@/stores/app'
import { authApi } from '@/api'
import GlobeBackground from '@/components/GlobeBackground.vue'
import { Cropper } from 'vue-advanced-cropper'
import 'vue-advanced-cropper/dist/style.css'

const router = useRouter()
const authStore = useAuthStore()
const appStore = useAppStore()

const loading = ref(false)
const codeSending = ref(false)
const countdown = ref(0)
const showPassword = ref(false)
const showConfirmPassword = ref(false)

// Avatar state
const avatarPreview = ref<string | null>(null)
const avatarFile = ref<File | null>(null)
const avatarTempToken = ref<string | null>(null)
const avatarUploading = ref(false)
const showCropper = ref(false)
const imageToCrop = ref<string>('')
const cropperRef = ref<InstanceType<typeof Cropper> | null>(null)
const avatarInputRef = ref<HTMLInputElement | null>(null)

const form = reactive({
  username: '',
  email: '',
  phone: '',
  verification_code: '',
  password: '',
  confirm_password: '',
  full_name: '',
  agreeToTerms: false,
})

// 表单验证错误
const errors = reactive({
  email: '',
  phone: '',
  password: '',
  confirm_password: '',
})

// 验证规则
const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

const validatePhone = (phone: string): boolean => {
  // 中国大陆手机号：1开头，11位数字
  const phoneRegex = /^1[3-9]\d{9}$/
  return phone === '' || phoneRegex.test(phone)
}

const validatePassword = (password: string): boolean => {
  return password.length >= 6
}

// 实时验证
function validateField(field: string) {
  switch (field) {
    case 'email':
      errors.email = form.email && !validateEmail(form.email) ? '请输入有效的邮箱地址' : ''
      break
    case 'phone':
      errors.phone = form.phone && !validatePhone(form.phone) ? '请输入有效的手机号' : ''
      break
    case 'password':
      errors.password = form.password && !validatePassword(form.password) ? '密码至少6位' : ''
      // 密码变化时重新检查确认密码
      if (form.confirm_password) {
        errors.confirm_password = form.confirm_password !== form.password ? '两次输入的密码不一致' : ''
      }
      break
    case 'confirm_password':
      errors.confirm_password = form.confirm_password && form.confirm_password !== form.password ? '两次输入的密码不一致' : ''
      break
  }
}

const canSendCode = computed(() => {
  return form.email && countdown.value === 0
})

const codeButtonText = computed(() => {
  if (countdown.value > 0) {
    return `${countdown.value}秒后重试`
  }
  return codeSending.value ? '发送中...' : '获取验证码'
})

const isFormValid = computed(() => {
  return form.username &&
         form.email &&
         form.verification_code &&
         form.password &&
         form.confirm_password &&
         form.agreeToTerms &&
         !errors.email &&
         !errors.phone &&
         !errors.password &&
         !errors.confirm_password
})

// Avatar handling
function handleAvatarUploadClick() {
  // 清空 input 值，确保每次都能触发 change 事件
  if (avatarInputRef.value) {
    avatarInputRef.value.value = ''
  }
}

function handleAvatarSelect(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  if (!file.type.startsWith('image/')) {
    appStore.error('请选择图片文件')
    return
  }

  if (file.size > 5 * 1024 * 1024) {
    appStore.error('图片大小不能超过5MB')
    return
  }

  const reader = new FileReader()
  reader.onload = (e) => {
    imageToCrop.value = e.target?.result as string
    showCropper.value = true
  }
  reader.readAsDataURL(file)
}

async function confirmCrop() {
  if (!cropperRef.value) return

  const { canvas } = cropperRef.value.getResult()
  canvas.toBlob(async (blob) => {
    if (blob) {
      const file = new File([blob], 'avatar.jpg', { type: 'image/jpeg' })
      avatarFile.value = file
      avatarPreview.value = URL.createObjectURL(blob)

      // 立即上传获取 temp_token
      avatarUploading.value = true
      try {
        const response = await authApi.uploadTempAvatar(file)
        avatarTempToken.value = response.temp_token
        appStore.success('头像上传成功')
      } catch (error: any) {
        appStore.error(error.message || '头像上传失败')
        // 上传失败时重置
        avatarPreview.value = null
        avatarFile.value = null
        avatarTempToken.value = null
      } finally {
        avatarUploading.value = false
        closeCropper()
      }
    }
  }, 'image/jpeg', 0.9)
}

function closeCropper() {
  showCropper.value = false
  imageToCrop.value = ''
}

function removeAvatar() {
  avatarPreview.value = null
  avatarFile.value = null
  avatarTempToken.value = null
}

async function handleSendCode() {
  if (!canSendCode.value || codeSending.value) return

  codeSending.value = true

  try {
    await authApi.sendVerificationCode(form.email)
    appStore.success('验证码已发送到您的邮箱')

    countdown.value = 60
    const timer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) {
        clearInterval(timer)
      }
    }, 1000)
  } catch (error: any) {
    appStore.error(error.message || '验证码发送失败')
  } finally {
    codeSending.value = false
  }
}

async function handleRegister() {
  if (form.password !== form.confirm_password) {
    appStore.error('两次输入的密码不一致')
    return
  }

  if (form.password.length < 6) {
    appStore.error('密码长度至少为6位')
    return
  }

  if (form.verification_code.length !== 6) {
    appStore.error('请输入6位验证码')
    return
  }

  loading.value = true

  try {
    // 构建注册请求数据
    const requestData = {
      username: form.username,
      email: form.email,
      password: form.password,
      verification_code: form.verification_code,
      full_name: form.full_name || undefined,
      phone: form.phone || undefined,
      temp_token: avatarTempToken.value || undefined,
    }

    // 发送注册请求
    await authApi.register(requestData)

    appStore.success('注册成功！请登录您的账户')

    // 注册成功后跳转到登录页
    router.push('/login')
  } catch (error: any) {
    appStore.error(error.message || '注册失败，请重试')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-page {
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
  align-items: center;
  justify-content: center;
  padding: 16px 32px 32px;
  overflow-y: auto;
}

.register-container {
  width: 100%;
  max-width: 900px;
}

/* Page Header */
.page-header {
  text-align: center;
  margin-bottom: 24px;
}

.page-icon {
  width: 72px;
  height: 72px;
  margin: 0 auto 16px;
  border-radius: 18px;
  background: linear-gradient(135deg, #3b82f6, #10b981);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 20px rgba(59, 130, 246, 0.3);
  color: white;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: white;
  margin: 0 0 8px;
}

.page-subtitle {
  font-size: 15px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
}

/* Register Form */
.register-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 24px;
}

/* Avatar Section */
.avatar-section {
  display: flex;
  justify-content: center;
  margin-bottom: 8px;
}

.avatar-wrapper {
  position: relative;
}

.avatar-preview {
  width: 88px;
  height: 88px;
  border-radius: 50%;
  overflow: hidden;
  border: 3px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  background: rgba(59, 130, 246, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(59, 130, 246, 0.5);
}

.avatar-upload-btn {
  position: absolute;
  bottom: 0;
  right: -4px;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6, #10b981);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
  transition: transform 0.2s;
}

.avatar-upload-btn:hover {
  transform: scale(1.1);
}

.avatar-remove-btn {
  position: absolute;
  top: -4px;
  right: -4px;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: #ef4444;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(239, 68, 68, 0.3);
  transition: background 0.2s;
}

.avatar-remove-btn:hover {
  background: #dc2626;
}

/* Form Fields */
.form-fields {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-field-full {
  grid-column: 1 / -1;
}

.field-label {
  font-size: 12px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-wrapper-flex {
  flex: 1;
}

.input-icon {
  position: absolute;
  left: 12px;
  color: rgba(255, 255, 255, 0.4);
  pointer-events: none;
}

.form-input {
  width: 100%;
  padding: 10px 12px 10px 38px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  color: white;
  font-size: 13px;
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

.form-input.pr-10 {
  padding-right: 40px;
}

.form-input.has-error {
  border-color: #ef4444;
  background: rgba(239, 68, 68, 0.05);
}

.form-input.has-error:focus {
  border-color: #ef4444;
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

.field-error {
  font-size: 11px;
  color: #ef4444;
  margin-top: 2px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.field-error::before {
  content: '';
  width: 3px;
  height: 3px;
  border-radius: 50%;
  background: #ef4444;
}

.password-toggle {
  position: absolute;
  right: 10px;
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

/* Code Input Group */
.code-input-group {
  display: flex;
  gap: 10px;
}

.code-btn {
  padding: 10px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  color: #3b82f6;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
  cursor: pointer;
  transition: all 0.2s;
}

.code-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(59, 130, 246, 0.3);
}

.code-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Terms Section */
.terms-section {
  padding: 12px 0;
}

.checkbox-label {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  line-height: 1.5;
}

.checkbox-custom {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 4px;
  transition: all 0.2s;
  position: relative;
  flex-shrink: 0;
  margin-top: 1px;
}

.peer:checked ~ .checkbox-custom {
  background: rgba(59, 130, 246, 0.2);
  border-color: #3b82f6;
}

.peer:checked ~ .checkbox-custom::after {
  content: '';
  position: absolute;
  top: 2px;
  left: 4px;
  width: 3px;
  height: 7px;
  border: solid #3b82f6;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.checkbox-label .link {
  color: #3b82f6;
  text-decoration: none;
  margin: 0 2px;
}

.checkbox-label .link:hover {
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

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

/* Footer */
.footer {
  text-align: center;
  padding: 16px 0;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.footer p {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
}

.login-link {
  color: #3b82f6;
  text-decoration: none;
  font-weight: 600;
  transition: color 0.2s;
}

.login-link:hover {
  color: #60a5fa;
}

/* Copyright */
.copyright {
  text-align: center;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
  margin-top: 16px;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
}

.modal-content {
  width: 100%;
  max-width: 450px;
  background: rgba(17, 24, 39, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.modal-header h3 {
  font-size: 18px;
  font-weight: 700;
  color: white;
  margin: 0;
}

.modal-close {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.05);
  border: none;
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  transition: all 0.2s;
}

.modal-close:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.cropper-wrapper {
  height: 320px;
  margin-bottom: 20px;
  border-radius: 12px;
  overflow: hidden;
  background: rgba(0, 0, 0, 0.2);
}

.modal-actions {
  display: flex;
  gap: 12px;
}

.btn-secondary,
.btn-primary {
  flex: 1;
  padding: 12px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.8);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.08);
}

.btn-primary {
  background: linear-gradient(135deg, #3b82f6, #10b981);
  border: none;
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
}

/* Responsive */
@media (max-width: 768px) {
  .header {
    padding: 12px 20px;
  }

  .main-content {
    padding: 16px 20px 24px;
  }

  .form-fields {
    grid-template-columns: 1fr;
  }

  .form-field-full {
    grid-column: auto;
  }

  .page-title {
    font-size: 22px;
  }

  .modal-content {
    padding: 20px;
  }

  .cropper-wrapper {
    height: 280px;
  }
}
</style>
