<template>
  <div class="home-page">
    <GlobeBackground />

    <!-- 主题切换按钮 -->
    <button class="theme-toggle" @click="toggleTheme" :title="isDark ? '切换到亮色主题' : '切换到深色主题'">
      <svg v-if="isDark" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="5"/>
        <line x1="12" y1="1" x2="12" y2="3"/>
        <line x1="12" y1="21" x2="12" y2="23"/>
        <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
        <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
        <line x1="1" y1="12" x2="3" y2="12"/>
        <line x1="21" y1="12" x2="23" y2="12"/>
        <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
        <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
      </svg>
      <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
      </svg>
    </button>

    <div class="content-overlay">
      <div class="hero-section">
        <div class="badge">
          <span class="badge-dot"></span>
          <span>雷达飞行轨迹智能平台</span>
        </div>

        <h1 class="title">
          <span class="title-main">RFTIP</span>
          <span class="title-sub">基于多源数据融合的雷达轨迹监测与智能分析平台</span>
        </h1>

        <p class="description">
          集成多算法误差分析、轨迹优化估计、大模型轨迹分析以及禁飞区检测于一体的智能平台
        </p>

        <div class="core-features">
          <div class="feature-item">
            <div class="feature-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2v4m0 12v4M4.93 4.93l2.83 2.83m8.48 8.48l2.83 2.83M2 12h4m12 0h4M4.93 19.07l2.83-2.83m8.48-8.48l2.83-2.83"/>
              </svg>
            </div>
            <div class="feature-content">
              <h3>雷达误差分析</h3>
              <p>多源参考模式（RANSAC、加权最小二乘）与单源盲测模式（卡尔曼滤波、粒子滤波）</p>
            </div>
          </div>

          <div class="feature-item">
            <div class="feature-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                <circle cx="9" cy="7" r="4"/>
                <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
              </svg>
            </div>
            <div class="feature-content">
              <h3>AI智能分析</h3>
              <p>MCP坐标转语义、轨迹文字化描述、大模型飞行意图识别与分析报告生成</p>
            </div>
          </div>

          <div class="feature-item">
            <div class="feature-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
              </svg>
            </div>
            <div class="feature-content">
              <h3>禁飞区检测</h3>
              <p>自定义禁飞区设置（圆形/多边形）、入侵检测与报告生成</p>
            </div>
          </div>

          <div class="feature-item">
            <div class="feature-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                <circle cx="12" cy="10" r="3"/>
              </svg>
            </div>
            <div class="feature-content">
              <h3>三维可视化</h3>
              <p>基于Cesium.js的全球尺度轨迹可视化、雷达站标注、高度可视化</p>
            </div>
          </div>
        </div>

        <button class="enter-btn" @click="goToDashboard">
          <span>进入控制台</span>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M5 12h14M12 5l7 7-7 7"/>
          </svg>
        </button>
      </div>
    </div>

    <div class="footer-info">
      <!-- <div class="tech-stack">
        <span class="tech-item">Vue 3</span>
        <span class="tech-item">Cesium.js</span>
        <span class="tech-item">FastAPI</span>
        <span class="tech-item">DeepSeek</span>
      </div> -->
      <span class="hint">拖拽旋转地球 · 点击进入控制台</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useThemeStore } from '@/stores/theme'
import { useAuthStore } from '@/stores/auth'
import GlobeBackground from '@/components/GlobeBackground.vue'

const router = useRouter()
const themeStore = useThemeStore()
const authStore = useAuthStore()
const { isDark } = storeToRefs(themeStore)
const { toggleTheme } = themeStore

function goToDashboard() {
  if (authStore.isAuthenticated) {
    router.push('/dashboard')
  } else {
    router.push('/login')
  }
}
</script>

<style scoped>
.home-page {
  position: relative;
  width: 100%;
  height: 100vh;
  overflow: hidden;
  background: var(--bg-primary);
  transition: background-color 0.4s ease;
}

.theme-toggle {
  position: absolute;
  top: 24px;
  right: 24px;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.3s ease;
  z-index: 20;
  backdrop-filter: blur(10px);
}

.theme-toggle:hover {
  background: var(--bg-secondary);
  border-color: var(--color-primary);
  color: var(--color-primary);
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(59, 130, 246, 0.15);
}

.theme-toggle:active {
  transform: translateY(0);
}

.content-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  padding-left: 8%;
  z-index: 10;
  pointer-events: none;
}

.hero-section {
  max-width: 600px;
  pointer-events: auto;
}

.badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.3);
  border-radius: 20px;
  font-size: 13px;
  color: #10b981;
  margin-bottom: 24px;
}

.badge-dot {
  width: 6px;
  height: 6px;
  background: #10b981;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.title {
  margin: 0 0 16px 0;
}

.title-main {
  display: block;
  font-size: 64px;
  font-weight: 700;
  letter-spacing: -2px;
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1;
}

.title-sub {
  display: block;
  font-size: 18px;
  font-weight: 500;
  color: var(--text-primary);
  margin-top: 8px;
  letter-spacing: 1px;
}

.description {
  color: var(--text-secondary);
  font-size: 15px;
  line-height: 1.6;
  margin: 0 0 32px 0;
}

.core-features {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 36px;
}

.feature-item {
  display: flex;
  gap: 12px;
  padding: 16px;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  transition: all 0.3s ease;
}

.feature-item:hover {
  background: var(--bg-secondary);
  border-color: var(--color-primary);
  transform: translateY(-2px);
}

.feature-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(59, 130, 246, 0.1);
  border-radius: 8px;
  color: var(--color-primary);
  flex-shrink: 0;
}

.feature-content h3 {
  margin: 0 0 6px 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.feature-content p {
  margin: 0;
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.5;
}

.enter-btn {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 14px 28px;
  background: var(--gradient-primary);
  border: none;
  border-radius: 10px;
  color: var(--text-inverse);
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 24px rgba(59, 130, 246, 0.3);
}

.enter-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(59, 130, 246, 0.4);
}

.enter-btn svg {
  transition: transform 0.3s ease;
}

.enter-btn:hover svg {
  transform: translateX(4px);
}

.footer-info {
  position: absolute;
  bottom: 24px;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 32px;
  z-index: 10;
  pointer-events: none;
}

.tech-stack {
  display: flex;
  gap: 12px;
}

.tech-item {
  padding: 4px 10px;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 4px;
  font-size: 12px;
  color: var(--text-muted);
}

.hint {
  font-size: 12px;
  color: var(--text-muted);
}

@media (max-width: 768px) {
  .content-overlay {
    padding: 24px;
    align-items: flex-end;
    padding-bottom: 100px;
  }

  .title-main {
    font-size: 48px;
  }

  .title-sub {
    font-size: 14px;
  }

  .core-features {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .feature-item {
    padding: 12px;
  }

  .footer-info {
    flex-direction: column;
    gap: 12px;
    bottom: 16px;
  }
}
</style>
