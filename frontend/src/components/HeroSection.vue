<template>
  <section class="hero">
    <div class="hero-bg"></div>
    <div class="hero-grid">
      <div class="hero-content">
        <div class="hero-badge">
          <svg class="badge-icon" viewBox="0 0 20 20" fill="currentColor">
            <path d="M10 2a6 6 0 00-6 6v3.586l-.707.707A1 1 0 004 14h12a1 1 0 00.707-1.707L16 11.586V8a6 6 0 00-6-6zM10 18a3 3 0 01-3-3h6a3 3 0 01-3 3z"/>
          </svg>
          <span>智能雷达追踪系统</span>
        </div>
        <h1 class="hero-title">
          <span class="title-gradient">RFTIP</span>
          <br>
          <span class="title-light">雷达轨迹融合追踪平台</span>
        </h1>
        <p class="hero-subtitle">
          基于 RANSAC 与卡尔曼滤波算法的多源雷达数据智能融合系统
        </p>
        <p class="hero-description">
          融合先进的轨迹分析技术与 AI 驱动的预测模型，为您提供专业、精准的雷达轨迹监测与追踪解决方案
        </p>
        <div class="hero-actions">
          <button class="btn btn-primary" @click="goToLogin">
            <svg class="btn-icon" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 1.414L10.586 9H7a1 1 0 100 2h3.586l-1.293 1.293a1 1 0 101.414 1.414l3-3a1 1 0 000-1.414z" clip-rule="evenodd"/>
            </svg>
            立即开始
          </button>
          <button class="btn btn-secondary" @click="learnMore">
            了解更多
            <svg class="btn-icon btn-icon-right" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"/>
            </svg>
          </button>
        </div>
        <div class="hero-stats">
          <div class="stat-item">
            <div class="stat-value">99.9%</div>
            <div class="stat-label">追踪准确率</div>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <div class="stat-value">50+</div>
            <div class="stat-label">雷达站点</div>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <div class="stat-value">24/7</div>
            <div class="stat-label">实时监控</div>
          </div>
        </div>
      </div>
      <div class="hero-visual">
        <div class="radar-container">
          <svg class="radar-svg" viewBox="0 0 400 400">
            <defs>
              <radialGradient id="radarGrad" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stop-color="#3B82F6" stop-opacity="0"/>
                <stop offset="100%" stop-color="#3B82F6" stop-opacity="0.1"/>
              </radialGradient>
              <linearGradient id="scanGrad" x1="50%" y1="50%" x2="100%" y2="0%">
                <stop offset="0%" stop-color="#3B82F6" stop-opacity="0"/>
                <stop offset="100%" stop-color="#10B981" stop-opacity="0.8"/>
              </linearGradient>
            </defs>
            <circle cx="200" cy="200" r="180" fill="url(#radarGrad)"/>
            <circle cx="200" cy="200" r="150" fill="none" stroke="#3B82F6" stroke-width="1" stroke-opacity="0.3"/>
            <circle cx="200" cy="200" r="100" fill="none" stroke="#3B82F6" stroke-width="1" stroke-opacity="0.4"/>
            <circle cx="200" cy="200" r="50" fill="none" stroke="#3B82F6" stroke-width="1" stroke-opacity="0.5"/>
            <line x1="200" y1="20" x2="200" y2="380" stroke="#3B82F6" stroke-width="1" stroke-opacity="0.2"/>
            <line x1="20" y1="200" x2="380" y2="200" stroke="#3B82F6" stroke-width="1" stroke-opacity="0.2"/>
            <g class="scan-line">
              <line x1="200" y1="200" x2="370" y2="30" stroke="url(#scanGrad)" stroke-width="2" stroke-linecap="round"/>
            </g>
            <circle cx="280" cy="120" r="6" fill="#10B981" class="blip"/>
            <circle cx="150" cy="250" r="5" fill="#3B82F6" class="blip"/>
            <circle cx="300" cy="280" r="4" fill="#10B981" class="blip"/>
            <circle cx="100" cy="180" r="7" fill="#3B82F6" class="blip"/>
          </svg>
          <div class="radar-glow"></div>
        </div>
        <div class="floating-cards">
          <div class="float-card float-card-1 glass">
            <svg class="card-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
            </svg>
            <div class="card-content">
              <div class="card-title">轨迹融合</div>
              <div class="card-value">2,847</div>
            </div>
          </div>
          <div class="float-card float-card-2 glass">
            <svg class="card-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <path d="M12 6v6l4 2"/>
            </svg>
            <div class="card-content">
              <div class="card-title">实时预警</div>
              <div class="card-value">Active</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

function goToLogin() {
  router.push('/login')
}

function learnMore() {
  document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' })
}
</script>

<style scoped>
.hero {
  position: relative;
  min-height: calc(100vh - 90px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 5rem 2rem 3rem;
  background: var(--gradient-subtle);
  overflow: hidden;
  transition: background 0.3s ease;
}

.hero-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background:
    radial-gradient(ellipse 80% 50% at 50% -20%, rgba(59, 130, 246, 0.08), transparent),
    radial-gradient(ellipse 60% 40% at 80% 60%, rgba(16, 185, 129, 0.05), transparent);
  pointer-events: none;
}

.hero-grid {
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4rem;
  align-items: center;
  position: relative;
  z-index: 1;
}

@media (max-width: 1024px) {
  .hero-grid {
    grid-template-columns: 1fr;
    text-align: center;
    gap: 3rem;
  }

  .hero-actions {
    justify-content: center;
  }

  .hero-stats {
    justify-content: center;
  }
}

.hero-content {
  display: flex;
  flex-direction: column;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 2rem;
  align-self: flex-start;
  margin-bottom: 1.5rem;
}

.badge-icon {
  width: 16px;
  height: 16px;
  color: var(--color-primary);
}

.hero-badge span {
  color: var(--text-secondary);
  font-size: 0.8125rem;
  font-weight: 500;
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 800;
  line-height: 1.1;
  margin-bottom: 1.5rem;
  letter-spacing: -0.03em;
}

.title-gradient {
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  background-size: 200% auto;
  animation: gradient-shift 3s ease infinite;
}

@keyframes gradient-shift {
  0%, 100% { background-position: 0% center; }
  50% { background-position: 100% center; }
}

.title-light {
  color: var(--text-primary);
}

.hero-subtitle {
  font-size: 1.25rem;
  color: var(--color-primary);
  font-weight: 600;
  margin-bottom: 0.75rem;
}

.hero-description {
  font-size: 1.0625rem;
  color: var(--text-secondary);
  line-height: 1.7;
  margin-bottom: 2.5rem;
  max-width: 540px;
}

.hero-actions {
  display: flex;
  gap: 1rem;
  margin-bottom: 3rem;
  flex-wrap: wrap;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.875rem 1.75rem;
  border-radius: 0.75rem;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.25s ease;
  border: none;
}

.btn-icon {
  width: 18px;
  height: 18px;
}

.btn-icon-right {
  width: 16px;
  height: 16px;
}

.btn-primary {
  background: var(--gradient-primary);
  color: #fff;
  box-shadow: 0 4px 14px rgba(59, 130, 246, 0.3);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
}

.btn-secondary {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  backdrop-filter: blur(10px);
}

.btn-secondary:hover {
  background: var(--bg-tertiary);
  border-color: var(--border-hover);
  transform: translateY(-2px);
}

.hero-stats {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.stat-item {
  text-align: left;
}

.stat-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--text-muted);
  margin-top: 0.25rem;
}

.stat-divider {
  width: 1px;
  height: 40px;
  background: var(--border-color);
}

.hero-visual {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.radar-container {
  position: relative;
  width: 100%;
  max-width: 450px;
  aspect-ratio: 1;
}

.radar-svg {
  width: 100%;
  height: 100%;
}

.scan-line {
  transform-origin: 200px 200px;
  animation: radar-scan 4s linear infinite;
}

@keyframes radar-scan {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.blip {
  animation: blink 2s ease-in-out infinite;
}

.blip:nth-child(2) { animation-delay: 0s; }
.blip:nth-child(3) { animation-delay: 0.5s; }
.blip:nth-child(4) { animation-delay: 1s; }
.blip:nth-child(5) { animation-delay: 1.5s; }

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

.radar-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(59, 130, 246, 0.15) 0%, transparent 70%);
  border-radius: 50%;
  filter: blur(40px);
  animation: glow-pulse 3s ease-in-out infinite;
}

@keyframes glow-pulse {
  0%, 100% { opacity: 0.5; transform: translate(-50%, -50%) scale(1); }
  50% { opacity: 0.8; transform: translate(-50%, -50%) scale(1.1); }
}

.floating-cards {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
}

.float-card {
  position: absolute;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  border-radius: 1rem;
  animation: float-card 6s ease-in-out infinite;
  pointer-events: auto;
}

.float-card-1 {
  top: 10%;
  right: -20px;
  animation-delay: 0s;
}

.float-card-2 {
  bottom: 15%;
  left: -10px;
  animation-delay: 3s;
}

@keyframes float-card {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.card-icon {
  width: 24px;
  height: 24px;
  color: var(--color-primary);
  flex-shrink: 0;
}

.card-title {
  font-size: 0.75rem;
  color: var(--text-muted);
  font-weight: 500;
}

.card-value {
  font-size: 1rem;
  color: var(--text-primary);
  font-weight: 600;
}

@media (max-width: 768px) {
  .hero {
    padding: 4rem 1.5rem 2rem;
  }

  .hero-title {
    font-size: 2.25rem;
  }

  .hero-subtitle {
    font-size: 1.0625rem;
  }

  .hero-description {
    font-size: 0.9375rem;
  }

  .hero-badge {
    align-self: center;
  }

  .btn {
    padding: 0.75rem 1.5rem;
    font-size: 0.9375rem;
  }

  .hero-stats {
    gap: 1.5rem;
  }

  .stat-value {
    font-size: 1.375rem;
  }

  .radar-container {
    max-width: 350px;
  }

  .float-card {
    display: none;
  }
}
</style>
