<template>
  <header class="nav-header">
    <div class="nav-container">
      <div class="nav-brand">
        <svg class="brand-icon" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
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
        <span class="brand-text">RFTIP</span>
      </div>
      <nav class="nav-menu">
        <a href="#features" class="nav-link">功能特性</a>
        <a href="#about" class="nav-link">关于我们</a>
      </nav>
      <div class="nav-actions">
        <ThemeSwitch />
        <button class="btn-ghost" @click="goToLogin">登录</button>
        <button class="btn-primary" @click="goToRegister">注册</button>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import ThemeSwitch from './ThemeSwitch.vue'

const router = useRouter()

function goToLogin() {
  router.push('/login')
}

function goToRegister() {
  router.push('/register')
}
</script>

<style scoped>
.nav-header {
  background: var(--backdrop-bg);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--border-color);
  position: sticky;
  top: 1rem;
  left: 1rem;
  right: 1rem;
  border-radius: 1rem;
  z-index: 100;
  transition: background-color 0.3s ease, border-color 0.3s ease;
}

@media (max-width: 640px) {
  .nav-header {
    top: 0.5rem;
    left: 0.5rem;
    right: 0.5rem;
    border-radius: 0.75rem;
  }
}

.nav-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0.875rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
}

.brand-icon {
  width: 40px;
  height: 40px;
}

.brand-text {
  font-size: 1.375rem;
  font-weight: 700;
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav-menu {
  display: flex;
  gap: 2.5rem;
}

.nav-link {
  color: var(--text-muted);
  text-decoration: none;
  font-weight: 500;
  font-size: 0.9375rem;
  transition: color 0.2s ease;
  position: relative;
}

.nav-link::after {
  content: '';
  position: absolute;
  bottom: -0.25rem;
  left: 0;
  width: 0;
  height: 2px;
  background: var(--gradient-primary);
  transition: width 0.2s ease;
}

.nav-link:hover {
  color: var(--text-primary);
}

.nav-link:hover::after {
  width: 100%;
}

.nav-actions {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.btn-ghost {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  padding: 0.5rem 1rem;
  border-radius: 0.625rem;
  transition: all 0.2s ease;
}

.btn-ghost:hover {
  background: var(--bg-tertiary);
  border-color: var(--border-hover);
  color: var(--text-primary);
}

.btn-primary {
  background: var(--gradient-primary);
  border: none;
  color: #fff;
  font-weight: 600;
  font-size: 0.875rem;
  padding: 0.625rem 1.25rem;
  border-radius: 0.625rem;
  cursor: pointer;
  transition: all 0.25s ease;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.25);
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(59, 130, 246, 0.35);
}

@media (max-width: 768px) {
  .nav-menu {
    display: none;
  }
}
</style>
