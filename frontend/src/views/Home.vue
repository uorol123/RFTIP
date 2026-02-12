<template>
  <div class="home-page">
    <GlobeBackground />

    <div class="content-overlay">
      <div class="hero-section">
        <div class="badge">
          <span class="badge-dot"></span>
          <span>实时监控中</span>
        </div>

        <h1 class="title">
          <span class="title-main">RFTIP</span>
          <span class="title-sub">雷达飞行轨迹智能平台</span>
        </h1>

        <p class="description">
          多源雷达数据融合 · 智能轨迹预测 · 实时态势感知
        </p>

        <div class="stats">
          <div class="stat-item">
            <span class="stat-value">10</span>
            <span class="stat-label">雷达站点</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <span class="stat-value">17</span>
            <span class="stat-label">监控航线</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <span class="stat-value">99.9%</span>
            <span class="stat-label">系统可用</span>
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
      <div class="legend">
        <span class="legend-item">
          <span class="dot green"></span>
          雷达站
        </span>
        <span class="legend-item">
          <span class="dot blue"></span>
          航线
        </span>
      </div>
      <span class="hint">拖拽旋转地球</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import GlobeBackground from '@/components/GlobeBackground.vue'

const router = useRouter()

function goToDashboard() {
  router.push('/dashboard')
}
</script>

<style scoped>
.home-page {
  position: relative;
  width: 100%;
  height: 100vh;
  overflow: hidden;
  background: #030712;
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
  max-width: 480px;
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
  background: linear-gradient(135deg, #60a5fa 0%, #34d399 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1;
}

.title-sub {
  display: block;
  font-size: 20px;
  font-weight: 500;
  color: #e2e8f0;
  margin-top: 8px;
  letter-spacing: 2px;
}

.description {
  color: #64748b;
  font-size: 15px;
  line-height: 1.6;
  margin: 0 0 32px 0;
}

.stats {
  display: flex;
  align-items: center;
  gap: 24px;
  margin-bottom: 36px;
}

.stat-item {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #f1f5f9;
}

.stat-label {
  font-size: 12px;
  color: #64748b;
  margin-top: 2px;
}

.stat-divider {
  width: 1px;
  height: 36px;
  background: rgba(100, 116, 139, 0.3);
}

.enter-btn {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 14px 28px;
  background: linear-gradient(135deg, #3b82f6 0%, #10b981 100%);
  border: none;
  border-radius: 10px;
  color: #fff;
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

.legend {
  display: flex;
  gap: 20px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #64748b;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.dot.green {
  background: #10b981;
}

.dot.blue {
  background: #60a5fa;
}

.hint {
  font-size: 12px;
  color: #475569;
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
    font-size: 16px;
  }

  .stats {
    gap: 16px;
  }

  .stat-value {
    font-size: 22px;
  }

  .footer-info {
    flex-direction: column;
    gap: 12px;
    bottom: 16px;
  }
}
</style>
