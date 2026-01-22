# RFTIP 前端项目

**RadarFusionTrack Intelligence Platform - Frontend**

基于 Vue 3 + TypeScript + Vite 构建的雷达轨迹监测与智能分析平台前端应用。

---

## 技术栈

| 技术 | 版本 | 说明 |
| --- | --- | --- |
| Vue 3 | ^3.5.13 | 渐进式 JavaScript 框架 |
| TypeScript | ^5.6.3 | JavaScript 的超集 |
| Vite | ^6.0.5 | 新一代前端构建工具 |
| Cesium.js | - | 全球尺度 3D 地图可视化引擎（待集成） |

---

## 项目结构

```
frontend/
├── src/
│   ├── App.vue          # 根组件
│   ├── main.ts          # 应用入口
│   └── components/      # Vue 组件目录
├── index.html           # HTML 模板
├── vite.config.ts       # Vite 配置
├── tsconfig.json        # TypeScript 配置
├── package.json         # 依赖管理
└── README.md            # 本文档
```

---

## 功能模块（规划中）

### 1. 用户认证
- 用户注册/登录
- JWT Token 管理
- 个人信息管理

### 2. 数据文件管理
- CSV/Excel 文件上传
- 文件列表展示
- 公开/私有状态设置
- 文件删除

### 3. 轨迹可视化（核心）
- **Cesium.js 3D 地图集成**
- 原始轨迹（红线）与修正轨迹（绿线）同屏对比
- 高度感应墙展示
- 时间轴控制播放
- 多轨迹同时显示

### 4. 算法处理
- 多源参考模式（RANSAC）
- 单源盲测模式（卡尔曼滤波）
- 处理结果展示

### 5. AI 分析
- 整体轨迹分析报告展示
- 区间轨迹状态分析
- 飞行意图解读

### 6. 禁飞区管理
- 自定义禁飞区（圆形/多边形）
- 高度限制设置
- 入侵记录查看
- 邮件预警设置

---

## 开发指南

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm run dev
```

开发服务器运行在 `http://localhost:5173`

### 构建生产版本

```bash
npm run build
```

### 预览生产构建

```bash
npm run preview
```

---

## API 接口说明

前端与后端通信通过 RESTful API，后端地址：`http://localhost:8000`

| 端点 | 方法 | 说明 |
| --- | --- | --- |
| `/` | GET | 服务健康检查 |
| `/health` | GET | 健康状态 |
| `/api/auth/*` | - | 用户认证相关接口（待实现） |
| `/api/files/*` | - | 文件管理接口（待实现） |
| `/api/tracks/*` | - | 轨迹数据接口（待实现） |
| `/api/analysis/*` | - | AI 分析接口（待实现） |
| `/api/zones/*` | - | 禁飞区管理接口（待实现） |

---

## 数据文件格式

### 轨迹数据文件（CSV/Excel）

| 列名 | 必填 | 说明 |
| --- | --- | --- |
| batch_id | 是 | 飞机批号 |
| station_id | 否 | 雷达站号 |
| time_stamp | 是 | 时间（格式：YYYY-MM-DD HH:MM:SS.sss） |
| longitude | 是 | 经度 |
| latitude | 是 | 纬度 |
| altitude | 否 | 高度（米） |
| speed | 否 | 速度（m/s） |

### 雷达站数据文件（CSV/Excel）

| 列名 | 必填 | 说明 |
| --- | --- | --- |
| station_id | 是 | 站号 |
| longitude | 是 | 经度 |
| latitude | 是 | 纬度 |
| altitude | 否 | 高度（米） |
| description | 否 | 备注 |

---

## 开发注意事项

1. **TypeScript**: 优先使用 TypeScript 类型定义，避免使用 `any`
2. **组件拆分**: 将大型组件拆分为更小的可复用组件
3. **状态管理**: 考虑使用 Pinia 进行全局状态管理
4. **API 请求**: 统一使用 axios 或 fetch 封装请求
5. **Cesium 集成**: 注意 Cesium 的 API token 配置

---

## 浏览器支持

- Chrome >= 90
- Firefox >= 88
- Edge >= 90
- Safari >= 14

---

## IDE 推荐

[VS Code](https://code.visualstudio.com/) + [Vue (Official)](https://marketplace.visualstudio.com/items?itemName=Vue.volar)

---

## Vue DevTools

- Chromium-based browsers (Chrome, Edge, Brave, etc.):
  - [Vue.js devtools](https://chromewebstore.google.com/detail/vuejs-devtools/nhdogjmejiglipccpnnnanhbledajbpd)
- Firefox:
  - [Vue.js devtools](https://addons.mozilla.org/en-US/firefox/addon/vue-js-devtools/)

---

## 相关文档

- [Vue 3 官方文档](https://cn.vuejs.org/)
- [Vite 官方文档](https://cn.vitejs.dev/)
- [TypeScript 官方文档](https://www.typescriptlang.org/zh/)
- [Cesium.js 文档](https://cesium.com/learn/cesiumjs/)
- [项目主 README](../README.md)
