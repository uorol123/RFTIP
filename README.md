# 基于多源数据融合的雷达轨迹监测与智能分析平台

**RadarFusionTrack Intelligence Platform (RFTIP)**

---

## 1. 项目背景与目标

在现代化空域管理中，雷达观测数据常受环境干扰和设备精度影响产生噪声。本项目旨在构建一个集**轨迹去噪优化**、**自适应误差校准**、**地理信息增强**以及**大模型意图识别**于一体的 Web 可视化平台，解决原始雷达数据"看得见但看不准、看不懂"的问题。

---

## 2. 技术栈架构

| 维度 | 技术选型 | 说明 |
| --- | --- | --- |
| **前端框架** | Vue 3 + Vite + TypeScript | 高性能响应式界面开发 |
| **三维引擎** | **Cesium.js** | 实现全球尺度下的飞机轨迹、高度、地理围栏可视化 |
| **后端框架** | FastAPI (Python) | 异步高性能架构，原生支持 Python 科学计算库 |
| **数据库** | MySQL 8.0 | 存储用户信息、轨迹数据及 AI 分析结果 |
| **文件存储** | MinIO (或本地 Static 存储) | 兼容 S3 协议，存储 CSV/Excel 轨迹数据文件 |
| **大模型** | DeepSeek / Ollama | 飞行意图推理与分析报告生成 |
| **MCP** | 自建 MCP Server | 逆地理编码、禁飞区检查、轨迹特征提取 |

---

## 3. 数据库设计

### 3.1 用户相关表

```sql
-- 用户信息表
CREATE TABLE users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    email VARCHAR(100) NOT NULL UNIQUE COMMENT '邮箱（用于接收预警通知）',
    password_hash VARCHAR(255) NOT NULL COMMENT '加密后的密码',
    avatar_url VARCHAR(500) COMMENT '头像URL',
    role ENUM('user', 'admin') DEFAULT 'user' COMMENT '用户角色',
    is_active BOOLEAN DEFAULT TRUE COMMENT '账号状态',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) COMMENT '用户信息表';

-- 用户登录日志表
CREATE TABLE user_login_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL COMMENT '用户ID',
    login_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '登录时间',
    ip_address VARCHAR(45) COMMENT 'IP地址',
    device_info VARCHAR(255) COMMENT '设备信息',
    status ENUM('success', 'failed') DEFAULT 'success' COMMENT '登录状态',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) COMMENT '用户登录日志表';
```

### 3.2 数据文件表

```sql
-- 用户数据文件表
CREATE TABLE data_files (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL COMMENT '上传用户ID',
    file_name VARCHAR(255) NOT NULL COMMENT '原始文件名',
    file_path VARCHAR(500) NOT NULL COMMENT '存储路径(MinIO)',
    file_type ENUM('csv', 'xlsx', 'excel') DEFAULT 'csv' COMMENT '文件类型',
    data_type ENUM('track', 'radar') NOT NULL COMMENT '数据类型：track=飞行轨迹，radar=雷达站',
    is_public BOOLEAN DEFAULT FALSE COMMENT '是否公开（其他用户可查看）',
    upload_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
    description VARCHAR(500) COMMENT '文件描述',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) COMMENT '用户数据文件表';
```

### 3.3 雷达站与轨迹数据表

```sql
-- 雷达站信息表
CREATE TABLE radar_stations (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    file_id BIGINT NOT NULL COMMENT '来源文件ID',
    station_id VARCHAR(50) NOT NULL COMMENT '站号（雷达站唯一标识）',
    longitude DECIMAL(10, 7) NOT NULL COMMENT '经度',
    latitude DECIMAL(10, 7) NOT NULL COMMENT '纬度',
    altitude FLOAT COMMENT '雷达站高度（米）',
    description VARCHAR(255) COMMENT '备注说明',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (file_id) REFERENCES data_files(id) ON DELETE CASCADE
) COMMENT '雷达站信息表';

-- 原始飞行轨迹表
CREATE TABLE flight_tracks_raw (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    file_id BIGINT NOT NULL COMMENT '来源文件ID',
    batch_id VARCHAR(50) NOT NULL COMMENT '飞机批号（同一架飞机的唯一标识）',
    station_id VARCHAR(50) COMMENT '雷达站号',
    time_stamp DATETIME(6) NOT NULL COMMENT '观测时间',
    longitude DECIMAL(10, 7) COMMENT '经度',
    latitude DECIMAL(10, 7) COMMENT '纬度',
    altitude FLOAT COMMENT '高度（米，可选）',
    speed FLOAT COMMENT '速度（m/s，可选）',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (file_id) REFERENCES data_files(id) ON DELETE CASCADE,
    INDEX idx_batch (batch_id),
    INDEX idx_time (time_stamp)
) COMMENT '原始飞行轨迹表';

-- 修正后飞行轨迹表（算法处理结果）
CREATE TABLE flight_tracks_corrected (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    batch_id VARCHAR(50) NOT NULL COMMENT '飞机批号',
    time_stamp DATETIME(6) NOT NULL COMMENT '修正后时间',
    longitude DECIMAL(10, 7) NOT NULL COMMENT '修正后经度',
    latitude DECIMAL(10, 7) NOT NULL COMMENT '修正后纬度',
    altitude FLOAT COMMENT '修正后高度（米）',
    speed FLOAT COMMENT '修正后速度（m/s）',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_batch (batch_id),
    INDEX idx_time (time_stamp)
) COMMENT '修正后飞行轨迹表';
```

### 3.4 禁飞区表

```sql
-- 用户自定义禁飞区表
CREATE TABLE restricted_zones (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL COMMENT '所属用户ID',
    name VARCHAR(100) NOT NULL COMMENT '禁飞区名称',
    zone_type ENUM('circle', 'polygon') NOT NULL COMMENT '区域类型：圆形/多边形',
    -- 圆形区域参数
    center_lon DECIMAL(10, 7) COMMENT '圆心经度',
    center_lat DECIMAL(10, 7) COMMENT '圆心纬度',
    radius_km FLOAT COMMENT '半径（公里）',
    -- 多边形区域参数（JSON格式存储顶点）
    polygon_coords JSON COMMENT '多边形顶点坐标JSON',
    min_altitude FLOAT COMMENT '最小高度限制（米），0表示无限制',
    max_altitude FLOAT COMMENT '最大高度限制（米），NULL表示无限制',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    alert_email BOOLEAN DEFAULT TRUE COMMENT '是否发送邮件预警',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) COMMENT '用户自定义禁飞区表';

-- 禁飞区入侵记录表
CREATE TABLE zone_intrusions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    zone_id BIGINT NOT NULL COMMENT '禁飞区ID',
    batch_id VARCHAR(50) NOT NULL COMMENT '入侵飞机批号',
    intrusion_time DATETIME NOT NULL COMMENT '入侵时间',
    location_lon DECIMAL(10, 7) NOT NULL COMMENT '入侵位置经度',
    location_lat DECIMAL(10, 7) NOT NULL COMMENT '入侵位置纬度',
    altitude FLOAT COMMENT '入侵时高度',
    alert_sent BOOLEAN DEFAULT FALSE COMMENT '是否已发送邮件预警',
    alert_sent_time DATETIME COMMENT '预警发送时间',
    processed BOOLEAN DEFAULT FALSE COMMENT '是否已处理',
    FOREIGN KEY (zone_id) REFERENCES restricted_zones(id) ON DELETE CASCADE
) COMMENT '禁飞区入侵记录表';
```

---

## 4. 核心功能模块

### 4.1 轨迹处理与场景自适应算法

系统支持用户根据实际工况预设两种分析场景：

**场景一：多源参考模式（大部分雷达可靠）**

* **原理：** 当多台雷达探测同一目标时，利用 **RANSAC (随机抽样一致性)** 算法剔除偏离群体的"坏点"站号，并计算该站的系统性偏差。
* **目的：** 自动识别并校准故障/低精度雷达。

**场景二：单源盲测模式（不确定可靠性）**

* **原理：** 采用 **卡尔曼滤波 (Kalman Filter)**。基于物理运动模型（匀速/匀加速）对单站噪声数据进行预测与修正。
* **目的：** 获得平滑连续的飞行轨迹，消除雷达跳变点。

---

### 4.2 飞行轨迹 AI 分析（MCP 模式）

系统通过 MCP Server 获取空间上下文，结合大模型生成分析报告。

#### 4.2.1 整体轨迹分析

1. 用户选择一架飞机的完整轨迹
2. MCP 工具提取轨迹特征（起飞点、降落点、转弯点、巡航高度、总里程等）
3. 将特征数据发送给大模型
4. 大模型生成整体分析报告（飞行意图、轨迹质量评估、异常检测等）

#### 4.2.2 区间轨迹分析

1. 用户选择一架飞机 + 时间区间
2. MCP 工具分析该区间的：
   - 起始位置 / 结束位置
   - 平均速度 / 最大速度
   - 高度变化
   - 航向变化
3. 大模型输出该时段的飞行状态描述

#### 4.2.3 禁飞区预警

1. 用户自定义禁飞区（圆形/多边形，可设置高度限制）
2. 当飞机进入禁飞区时：
   - 系统自动记录入侵事件
   - 调用 MCP 查询入侵位置详情
   - 结合大模型分析入侵情况
   - 发送邮件通知用户

---

### 4.3 三维数字孪生可视化

* **多维轨迹对比：** 动态同屏对比"原始噪声轨迹（红线）"与"算法优化轨迹（绿线）"
* **高度感应墙：** 轨迹线下方的垂直投影墙，直观展示飞机高度变化
* **禁飞区可视化：** 在三维地图上渲染用户设置的禁飞区域
* **实时告警：** 当飞机侵入禁飞区时自动改变轨迹颜色并弹窗提醒

---

## 5. 用户权限与数据管理

### 5.1 数据归属

| 数据类型 | 归属 | 共享方式 |
| --- | --- | --- |
| 用户信息 | 用户本人 | 私有 |
| 上传文件（雷达站/轨迹） | 上传用户 | 可设为公开或私有 |
| 修正轨迹 | 系统生成 | 随原始数据归属 |
| 禁飞区设置 | 用户本人 | 私有 |
| 入侵记录 | 用户本人 | 私有 |

### 5.2 权限控制

* **私有数据：** 仅自己可访问、操作
* **公开数据：** 其他用户可查看，但不可修改或删除
* **文件共享：** 用户可随时切换文件的公开/私有状态

---

## 6. 业务流程图

```
用户注册/登录
      │
      ▼
┌─────────────────┐
│  上传数据文件    │ -> CSV/Excel 格式
│  (轨迹/雷达站)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│  数据解析入库    │ ->  │  选择处理场景   │
│  (原始轨迹表)    │     │  (多源/单源)    │
└────────┬────────┘     └────────┬────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│  算法处理       │     │  用户交互分析   │
│  (修正轨迹表)    │     │  (AI分析/区间)  │
└────────┬────────┘     └─────────────────┘
         │
         ▼
┌─────────────────┐
│  三维可视化展示  │
│  (Cesium.js)    │
└─────────────────┘
```

---

## 7. 数据文件格式说明

### 7.1 轨迹数据文件（CSV/Excel）

| 列名 | 必填 | 说明 |
| --- | --- | --- |
| batch_id | 是 | 飞机批号 |
| station_id | 否 | 雷达站号 |
| time_stamp | 是 | 时间（格式：YYYY-MM-DD HH:MM:SS.sss） |
| longitude | 是 | 经度 |
| latitude | 是 | 纬度 |
| altitude | 否 | 高度（米） |
| speed | 否 | 速度（m/s） |

### 7.2 雷达站数据文件（CSV/Excel）

| 列名 | 必填 | 说明 |
| --- | --- | --- |
| station_id | 是 | 站号 |
| longitude | 是 | 经度 |
| latitude | 是 | 纬度 |
| altitude | 否 | 高度（米） |
| description | 否 | 备注 |

---

## 8. 项目创新点

* **算法灵活性：** 区分"已知基准"与"未知基准"两种工程实际场景
* **AI 分析深度：** 基于 MCP 工具增强地理语义，让大模型理解"飞机在哪里、在干什么"
* **交互专业性：** 结合 Cesium 三维引擎，提供行业演示标准的 4D 可视化效果
* **用户个性化：** 支持用户自定义禁飞区 + 邮件预警通知
* **数据自主性：** 文件上传、共享/私有可控

---

## 9. 技术参考

* **MCP Python SDK:** https://github.com/modelcontextprotocol/python-sdk
* **Cesium.js:** https://cesium.com/cesiumjs/
* **FastAPI:** https://fastapi.tiangolo.com/
* **DeepSeek API:** https://platform.deepseek.com/
