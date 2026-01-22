<template>
  <section id="features" class="features-section">
    <div class="features-container">
      <div class="section-header">
        <div class="section-badge">核心功能</div>
        <h2 class="section-title">专业的雷达轨迹分析工具</h2>
        <p class="section-subtitle">助力智能决策，提供精准的追踪与分析能力</p>
      </div>
      <div class="features-grid">
        <FeatureCard
          svg-icon="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"
          title="3D 轨迹可视化"
          description="基于 Cesium.js 的全球尺度 3D 地图，支持原始轨迹与修正轨迹同屏对比，高度感应墙展示"
          icon-bg="rgba(59, 130, 246, 0.12)"
        />
        <FeatureCard
          svg-icon="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"
          title="多源数据融合"
          description="采用 RANSAC 算法进行多源参考模式处理，融合多雷达站数据，提高轨迹精度"
          icon-bg="rgba(16, 185, 129, 0.12)"
        />
        <FeatureCard
          svg-icon="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
          title="单源盲测处理"
          description="基于卡尔曼滤波算法的单源盲测模式，实现对单一雷达数据的智能修正"
          icon-bg="rgba(139, 92, 246, 0.12)"
        />
        <FeatureCard
          svg-icon="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
          title="AI 智能分析"
          description="整体轨迹分析报告、区间状态分析、飞行意图解读，提供深度洞察"
          icon-bg="rgba(236, 72, 153, 0.12)"
        />
        <FeatureCard
          svg-icon="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
          title="禁飞区管理"
          description="自定义圆形/多边形禁飞区，设置高度限制，入侵实时预警邮件通知"
          icon-bg="rgba(245, 158, 11, 0.12)"
        />
        <FeatureCard
          svg-icon="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
          title="时间轴回放"
          description="支持轨迹时间轴控制播放，多轨迹同时显示，全方位回放历史数据"
          icon-bg="rgba(20, 184, 166, 0.12)"
        />
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import FeatureCard from './FeatureCard.vue'
</script>

<style scoped>
.features-section {
  background: var(--bg-primary);
  padding: 6rem 2rem;
  position: relative;
  transition: background 0.3s ease;
}

.features-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  max-width: 1400px;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.15), transparent);
}

.features-container {
  max-width: 1400px;
  margin: 0 auto;
}

.section-header {
  text-align: center;
  margin-bottom: 4rem;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.section-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.375rem 1rem;
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 2rem;
  color: var(--color-primary);
  font-size: 0.8125rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
  letter-spacing: 0.05em;
}

.section-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 1rem;
  letter-spacing: -0.02em;
}

.section-subtitle {
  font-size: 1.0625rem;
  color: var(--text-secondary);
  line-height: 1.6;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}

@media (max-width: 1024px) {
  .features-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .features-grid {
    grid-template-columns: 1fr;
  }

  .section-title {
    font-size: 2rem;
  }
}
</style>
