<template>
  <section class="landing-page">
    <!-- Theme Toggle -->
    <div class="theme-toggle-wrapper">
      <button @click="toggleTheme" class="theme-toggle-btn">
        <svg v-if="themeStore.isDark" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="5"/>
          <line x1="12" y1="1" x2="12" y2="3"/>
          <line x1="12" y1="21" x2="12" y2="23"/>
          <line x1="4.22" y1="4.22" x2="19.78" y2="19.78"/>
          <line x1="12" y1="21" x2="12" y2="23"/>
        </svg>
        <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 12.79A9 9 0 1 1 21 12.79z"/>
        </svg>
      </button>
    </div>

    <!-- Navigation -->
    <nav class="landing-nav">
      <div class="nav-brand font-display">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
          <circle cx="12" cy="12" r="3" fill="currentColor" stroke="none"/>
          <line x1="12" y1="2" x2="12" y2="4"/>
          <line x1="12" y1="4" x2="12" y2="5" transform="rotate(45)"/>
          <line x1="12" y1="4" x2="12" y2="5" transform="rotate(-45)"/>
        </svg>
        <span>RFTIP</span>
      </div>
      <div class="nav-links">
        <router-link to="/dashboard" class="nav-link">进入控制台</router-link>
        <router-link to="/login" class="nav-link nav-link-auth">登录</router-link>
      </div>
    </nav>

    <!-- 3D Globe Background -->
    <GlobeBackground />

    <!-- Hero Content Overlay -->
    <main class="content-overlay">
      <div class="hero-section">
        <div class="hero-badge">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="2" fill="currentColor"/>
          </svg>
          <span>雷达轨迹监测与智能分析平台</span>
        </div>

        <h1 class="hero-title font-display">
          <span class="title-line">多源数据融合</span>
          <span class="title-line title-gradient">轨迹智能分析</span>
        </h1>

        <p class="hero-desc">
          基于 RANSAC <span class="highlight">去噪算法</span> 和 Kalman <span class="highlight">滤波校准</span>
          <br>实现雷达误差校准与轨迹优化的智能分析系统
        </p>

        <!-- Feature Cards -->
        <div class="feature-cards">
          <div class="feature-card" @click="scrollToFeatures">
            <div class="feature-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 0 1-2-2H5a2 2 0 0 0-2 2v4"/>
                <polyline points="17,8 12,3 7,8"/>
                <line x1="12" y1="8" x2="12" y2="16"/>
                <line x1="9" y1="20" x2="15" y2="20"/>
              </svg>
            </div>
            <div class="feature-text">
              <h3 class="feature-title">RANSAC 去噪</h3>
              <p>多源雷达数据融合算法</p>
            </div>
          </div>

          <div class="feature-card" @click="scrollToFeatures">
            <div class="feature-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2a10 10 0 0 0 8 12"/>
                <path d="M12 2a10 10 0 0 0 8 12"/>
                <path d="M14.5 9a2.5 2.5 0 0 0 2 12"/>
                <path d="M9.5 9a2.5 2.5 0 0 2 12"/>
                <path d="M14.5 9a2.5 2.5 0 0 2 12"/>
              </svg>
            </div>
            <div class="feature-text">
              <h3 class="feature-title">Kalman 滤波</h3>
              <p>自适应轨迹误差校准</p>
            </div>
          </div>

          <div class="feature-card" @click="scrollToFeatures">
            <div class="feature-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <path d="M12 22s-6 7l-3.22 3"/>
                <path d="M12 22s-6 7l-3.22 3" fill="currentColor" stroke="none"/>
              </svg>
            </div>
            <div class="feature-text">
              <h3 class="feature-title">AI 意图分析</h3>
              <p>MCP 工具链 + 大模型推理</p>
            </div>
          </div>
        </div>

        <div class="cta-section">
          <router-link to="/dashboard" class="cta-button font-display">
            <span>进入控制台</span>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="5" y1="12" x2="19" y2="12"/>
              <polyline points="12,5 19,12"/>
            </svg>
          </router-link>
        </div>
      </div>
    </main>
  </section>
</template>

<script setup lang="ts">
import { useThemeStore } from '@/stores/theme'
import GlobeBackground from '@/components/GlobeBackground.vue'

const themeStore = useThemeStore()

function toggleTheme() {
  themeStore.toggleTheme()
}

function scrollToFeatures() {
  const features = document.querySelector('.feature-cards')
  if (features) {
    features.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
  }
}
</script>

<style scoped>
.landing-page {
  position: relative;
  min-height: 100vh;
  background: var(--bg-primary);
  overflow: hidden;
}

/* Theme Toggle */
.theme-toggle-wrapper {
  position: fixed;
  top: 1.5rem;
  right: 1.5rem;
  z-index: 100;
}

.theme-toggle-btn {
  width: 2.5rem;
  height: 2.5rem;
  background: var(--glass-bg);
  backdrop-filter: blur(10px);
  border: 1px solid var(--glass-border);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-accent);
  cursor: pointer;
  transition: all 0.3s ease;
}

.theme-toggle-btn:hover {
  background: var(--bg-elevated);
  border-color: var(--color-accent);
  box-shadow: var(--shadow-md);
  transform: scale(1.05);
}

.theme-toggle-btn svg {
  width: 1.25rem;
  height: 1.25rem;
}

/* Navigation */
.landing-nav {
  position: fixed;
  top: 1.5rem;
  left: 1.5rem;
  right: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 50;
  backdrop-filter: blur(10px);
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: var(--text-primary);
  font-weight: 700;
  font-size: 1rem;
  letter-spacing: 0.02em;
}

.nav-brand svg {
  width: 1.75rem;
  height: 1.75rem;
  color: var(--color-accent);
}

.nav-links {
  display: flex;
  gap: 2rem;
}

.nav-link {
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
  transition: color 0.3s ease;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
}

.nav-link:hover {
  color: var(--color-accent);
  background: rgba(99, 102, 241, 0.1);
}

.nav-link-auth {
  background: var(--gradient-primary);
  color: var(--text-inverse);
  padding: 0.5rem 1.5rem;
  border-radius: 0.5rem;
}

.nav-link-auth:hover {
  box-shadow: var(--shadow-md), 0 0 20px rgba(99, 102, 241, 0.3);
}

/* Hero Content Overlay */
.content-overlay {
  position: relative;
  z-index: 10;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 6rem 2rem;
  pointer-events: none;
}

.hero-section {
  max-width: 600px;
  text-align: left;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: rgba(99, 102, 241, 0.15);
  border: 1px solid rgba(99, 102, 241, 0.3);
  border-radius: 2rem;
  color: var(--color-accent);
  font-size: 0.8125rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  margin-bottom: 1.5rem;
}

.hero-badge svg {
  width: 1rem;
  height: 1rem;
}

.hero-title {
  font-size: clamp(2rem, 5vw, 3.5rem);
  font-weight: 800;
  line-height: 1.1;
  letter-spacing: -0.02em;
  margin-bottom: 1rem;
}

.title-line {
  display: block;
}

.title-gradient {
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-desc {
  font-size: 1.125rem;
  line-height: 1.8;
  color: var(--text-secondary);
  margin-bottom: 2.5rem;
  max-width: 500px;
}

.hero-desc .highlight {
  color: var(--color-accent);
  font-weight: 600;
}

/* Feature Cards */
.feature-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-bottom: 2rem;
}

.feature-card {
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  border: 1px solid var(--border-color);
  border-radius: 1rem;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  pointer-events: auto;
}

.feature-card:hover {
  transform: translateY(-8px);
  box-shadow: var(--shadow-lg), 0 0 40px rgba(99, 102, 241, 0.2);
  border-color: var(--color-accent);
}

.feature-icon {
  width: 2.5rem;
  height: 2.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(99, 102, 241, 0.1);
  border-radius: 0.75rem;
  margin-bottom: 1rem;
}

.feature-icon svg {
  width: 1.5rem;
  height: 1.5rem;
}

.feature-text {
  text-align: left;
}

.feature-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.feature-text p {
  font-size: 0.875rem;
  color: var(--text-secondary);
  line-height: 1.5;
}

/* CTA Section */
.cta-section {
  margin-top: 2rem;
}

.cta-button {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 2rem;
  background: var(--gradient-primary);
  color: var(--text-inverse);
  border-radius: 2rem;
  font-size: 1.125rem;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.3s ease;
}

.cta-button:hover {
  box-shadow: var(--shadow-lg), 0 0 40px rgba(99, 102, 241, 0.4);
  transform: translateY(-2px);
}

.cta-button svg {
  width: 1.25rem;
  height: 1.25rem;
}

/* Responsive */
@media (max-width: 1024px) {
  .content-overlay {
    padding: 4rem 1.5rem;
  }

  .hero-section {
    text-align: center;
  }

  .feature-cards {
    grid-template-columns: 1fr;
  }

  .feature-card {
    padding: 1.25rem;
  }
}

@media (max-width: 768px) {
  .landing-nav {
    left: 1rem;
    right: 4rem;
  }

  .nav-links {
    display: none;
  }

  .hero-title {
    font-size: 2rem;
  }
}
</style>
