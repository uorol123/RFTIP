import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import { setupRouterGuards } from './router/guards'

// 导入路由配置（不包含 guards）
import routes from './router/routes'

const app = createApp(App)

// 创建 Pinia 实例并先安装
const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)
app.use(pinia)

// 创建 Router
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  },
})

// 在 Pinia 安装后再设置路由守卫
setupRouterGuards(router)

// 安装 Router
app.use(router)

app.mount('#app')
