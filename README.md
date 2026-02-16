# 智能雷达轨迹分析平台

**RadarFusionTrack Intelligence Platform (RFTIP)**

---

## 1. 项目背景与目标

**核心问题**：多个传感器对目标探测时可能存在系统性偏差，如何利用不同方法对各传感器探测到的目标数据进行误差计算，分析比较各算法并可视化？

本项目针对雷达观测数据受环境干扰和设备精度影响产生噪声的问题，构建一个集**多算法误差分析**、**轨迹优化估计**、**大模型轨迹分析**以及**禁飞区检测**于一体的 Web 可视化平台，实现以下目标：

1. 分析各雷达站的系统性误差，评估其可靠性
2. 综合多源数据，测算出最可能的实际飞行轨迹
3. 利用大模型对优化后的轨迹进行智能分析
4. 提供禁飞区自定义设置与入侵检测功能

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
| **MCP** | 自建 MCP Server | 坐标逆地理编码、轨迹语义化描述（位置→地名转换） |

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
-- 数据文件表（数据只存一份，通过 file_id 关联）
CREATE TABLE data_files (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL COMMENT '上传用户ID',
    file_name VARCHAR(255) NOT NULL COMMENT '原始文件名',
    file_path VARCHAR(500) NOT NULL COMMENT '存储路径(MinIO)',
    data_type ENUM('track', 'radar') NOT NULL COMMENT '数据类型：track=飞行轨迹，radar=雷达站',
    is_public BOOLEAN DEFAULT FALSE COMMENT '是否公开（其他用户可查看引用）',
    upload_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
    description VARCHAR(500) COMMENT '文件描述',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE INDEX idx_user_file (user_id, file_name)  -- 同一用户文件不重复
) COMMENT '数据文件表';
```

### 3.3 轨迹数据表（通过 file_id 关联）

```sql
-- 原始飞行轨迹表
CREATE TABLE flight_tracks_raw (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    file_id BIGINT NOT NULL COMMENT '来源文件ID（数据不重复存储）',
    batch_id VARCHAR(50) NOT NULL COMMENT '飞机批号（原始值，显示时加用户前缀区分）',
    station_id VARCHAR(50) COMMENT '雷达站号',
    time_stamp DATETIME(6) NOT NULL COMMENT '观测时间',
    longitude DECIMAL(10, 7) COMMENT '经度',
    latitude DECIMAL(10, 7) COMMENT '纬度',
    altitude FLOAT COMMENT '高度（米，可选）',
    speed FLOAT COMMENT '速度（m/s，可选）',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (file_id) REFERENCES data_files(id) ON DELETE CASCADE,
    INDEX idx_file (file_id),
    INDEX idx_batch_time (batch_id, time_stamp)
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
    INDEX idx_batch_time (batch_id, time_stamp)
) COMMENT '修正后飞行轨迹表';
```

### 3.4 雷达站数据表（通过 file_id 关联）

```sql
-- 雷达站信息表
CREATE TABLE radar_stations (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    file_id BIGINT NOT NULL COMMENT '来源文件ID',
    station_id VARCHAR(50) NOT NULL COMMENT '站号（原始值）',
    longitude DECIMAL(10, 7) NOT NULL COMMENT '经度',
    latitude DECIMAL(10, 7) NOT NULL COMMENT '纬度',
    altitude FLOAT COMMENT '雷达站高度（米）',
    description VARCHAR(255) COMMENT '备注说明',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (file_id) REFERENCES data_files(id) ON DELETE CASCADE,
    INDEX idx_file (file_id)
) COMMENT '雷达站信息表';
```

### 3.5 禁飞区表

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

## 4. 数据权限与隔离

### 4.1 数据归属原则

* **数据只存一份：** 轨迹和雷达站数据通过 `file_id` 关联到 `data_files` 表，不直接存储 `user_id`
* **用户只能操作自己的文件：** `data_files.user_id` 标识文件归属
* **文件可选择公开：** `is_public = TRUE` 时，其他用户可以查看和引用该文件

### 4.2 数据查询权限

```sql
-- 查询我能访问的轨迹数据（自己的私有文件 + 公开文件）
SELECT t.*
FROM flight_tracks_raw t
JOIN data_files f ON t.file_id = f.id
WHERE f.user_id = ?        -- 我的私有文件
   OR f.is_public = TRUE;  -- 公开文件

-- 查询我能访问的雷达站数据（同样逻辑）
SELECT r.*
FROM radar_stations r
JOIN data_files f ON r.file_id = f.id
WHERE f.user_id = ? OR f.is_public = TRUE;
```

### 4.3 标识符区分（解决用户间批号/站号重复问题）

* **存储：** 保留原始 `batch_id` 和 `station_id`
* **显示：** 前端拼接用户标识前缀，如 `"UserA_B123"` 或 `"UserB_B123"`
* **筛选：** 使用原始值 + 权限过滤

```javascript
// 前端显示示例
function displayBatchId(batchId, ownerUserId) {
    return `${ownerUserId}_${batchId}`;  // "1001_ABC123"
}

// API 查询示例
async function queryTracks(batchId, currentUserId) {
    return await db.fetchAll(`
        SELECT t.* FROM flight_tracks_raw t
        JOIN data_files f ON t.file_id = f.id
        WHERE t.batch_id = ? AND (f.user_id = ? OR f.is_public = TRUE)
    `, [batchId, currentUserId]);
}
```

### 4.4 禁飞区检测逻辑

```python
async def check_zone_intrusions(user_id: int, batch_id: str):
    # 1. 获取该用户设置的所有禁飞区
    zones = await db.fetch_all(
        "SELECT * FROM restricted_zones WHERE user_id = ?", (user_id,)
    )

    # 2. 获取该用户上传的轨迹数据
    tracks = await db.fetch_all("""
        SELECT t.* FROM flight_tracks_raw t
        JOIN data_files f ON t.file_id = f.id
        WHERE t.batch_id = ? AND f.user_id = ?
    """, (batch_id, user_id))

    # 3. 检测禁飞区入侵并生成报告
    intrusions = []
    for track in tracks:
        for zone in zones:
            if point_in_zone(track.lon, track.lat, zone):
                intrusion = await record_intrusion(zone.id, batch_id, track)
                intrusions.append(intrusion)

    # 4. 如有入侵，生成报告并通知用户
    if intrusions:
        await generate_intrusion_report(user_id, intrusions)
    ```

---

## 5. 核心功能模块

### 5.1 雷达误差分析与轨迹优化（核心功能）

针对多雷达站探测多目标的场景，系统提供多种算法模式进行误差分析与轨迹估计：

#### 5.1.1 多源参考模式（Multi-Source Reference Mode）

**适用场景**：多个雷达同时观测同一目标，且大部分雷达是可靠的

**算法实现**：
- **RANSAC (随机抽样一致性)**：剔除偏离群体的"坏点"雷达站，识别故障/低精度设备
- **加权最小二乘法**：根据各雷达的可靠性权重进行融合
- **系统误差估计**：计算每个雷达站的系统性偏差（固定偏差、比例偏差）

**输出结果**：
- 各雷达站的误差评估报告
- 故障雷达识别结果
- 融合后的优化轨迹

#### 5.1.2 单源盲测模式（Single-Source Blind Mode）

**适用场景**：无法确定雷达可靠性，所有数据都视为潜在噪声

**算法实现**：
- **卡尔曼滤波 (Kalman Filter)**：基于物理运动模型（匀速/匀加速）对单站数据进行预测与修正
- **粒子滤波**：处理非线性非高斯噪声场景
- **样条平滑**：获得连续平滑的轨迹曲线

**输出结果**：
- 平滑去噪后的飞行轨迹
- 状态估计协方差（不确定性评估）

#### 5.1.3 算法综合比较与可视化

- 多算法并行计算结果对比
- 误差指标可视化（RMSE、MAE、偏差分布）
- 算法性能评估报告

#### 5.1.4 GPU 加速（规划中）

- 利用 CUDA 加速矩阵运算
- 并行化多目标轨迹处理
- 实时计算性能提升

---

### 5.2 飞行轨迹 AI 智能分析

#### 5.2.1 MCP 坐标转语义

通过自建 MCP Server 实现坐标到地理信息的转换：

```python
# MCP 工具示例
mcp_tool.reverse_geocode(lon, lat)  # 返回: "上海市浦东新区"
mcp_tool.get_location_info(lon, lat)  # 返回: 行政区划、地标、空域信息
```

#### 5.2.2 轨迹文字化描述

将优化后的轨迹转换为自然语言描述：

```
示例输出：
"该航班于 2024-01-15 08:30 从上海浦东国际机场起飞，
巡航高度 10000 米，沿预定航线飞行，
于 10:45 降落北京首都国际机场。
全程约 1178 公里，平均速度 850 km/h。
期间在济南空域有约 30 度的航向调整。"
```

#### 5.2.3 大模型分析报告

基于轨迹特征和语义描述，调用大模型进行：

- **飞行意图识别**：民航/军用/训练/侦察等
- **轨迹质量评估**：平滑度、合理性评分
- **异常行为检测**：偏离航线、高度异常、速度突变等
- **综合分析报告**：生成结构化的分析文档

---

### 5.3 禁飞区检测与报告

#### 5.3.1 禁飞区管理

用户可自定义禁飞区，支持：

- **圆形区域**：圆心坐标 + 半径
- **多边形区域**：任意多边形顶点坐标
- **高度限制**：最低/最高高度约束
- **时效设置**：禁飞起止时间（可选）

#### 5.3.2 入侵检测

系统自动检测上传的轨迹数据是否与用户设置的禁飞区相交：

- **几何算法**：点-圆包含判断、点-多边形射线法
- **高度检测**：判断是否在高度限制范围内
- **时间匹配**：考虑禁飞区的时效性

#### 5.3.3 检测报告

当检测到入侵时，生成报告并通知用户：

- 入侵时间、位置坐标
- 侵入禁飞区名称
- 持续时长
- 轨迹可视化标注
- 邮件/站内通知

---

### 5.5 三维可视化展示

基于 **Cesium.js** 实现全球尺度轨迹可视化：

#### 5.5.1 多维轨迹对比
- **原始雷达数据**：多条彩色线分别展示各雷达站的原始观测轨迹
- **优化轨迹**：粗线突出显示算法融合后的最可能轨迹
- **同屏对比**：直观展现去噪前后差异

#### 5.5.2 雷达站位置标注
- 在三维地图上标注各雷达站的精确位置
- 支持点击查看雷达站详情（站号、坐标、误差分析结果）

#### 5.5.3 高度可视化
- **高度感应墙**：轨迹线下方的垂直投影墙，直观展示飞机高度变化
- **颜色映射**：根据高度着色（低空=蓝色，高空=红色）
- **3D 立体感**：真实呈现飞行空间姿态

#### 5.5.4 禁飞区渲染
- **圆形/多边形区域**在三维地图上绘制
- 半透明显示，不影响轨迹观察
- 高度范围可视化（柱状体展示高度限制）

#### 5.5.5 误差分析可视化
- **误差热力图**：各雷达站的误差分布热力图
- **误差矢量图**：显示各雷达站在各观测点的方向和大小
- **误差统计图表**：RMSE、MAE、偏差分布的柱状图/箱线图

#### 5.5.6 动画回放
- 支持时间轴控制的轨迹动态回放
- 可调节回放速度
- 支持暂停/继续/跳转

#### 5.5.7 交互功能
- 鼠标悬停显示轨迹点详细信息
- 点击选中目标查看完整分析报告
- 支持视角跟随（相机跟随飞机移动）

---

## 6. 用户权限与数据管理

### 6.1 数据归属

| 数据类型 | 归属 | 共享方式 |
| --- | --- | --- |
| data_files（文件记录） | 上传用户 | 可设为公开 |
| flight_tracks_raw（轨迹数据） | 通过 file_id 关联 | 随文件公开性 |
| radar_stations（雷达站数据） | 通过 file_id 关联 | 随文件公开性 |
| restricted_zones（禁飞区） | 用户本人 | 私有 |
| zone_intrusions（入侵记录） | 用户本人 | 私有 |

### 6.2 权限控制

* **私有文件：** 仅自己可访问
* **公开文件：** 其他用户可查看和引用，但不可删除
* **禁飞区：** 仅自己可管理，预警也只通知自己

---

## 7. 业务流程图

```
用户注册/登录
      │
      ▼
┌─────────────────────┐
│   上传雷达数据文件    │
│   (CSV/Excel格式)    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐     ┌─────────────────────┐
│   数据解析与入库     │     │   设置禁飞区(可选)  │
│   (多雷达+多目标)    │     └─────────────────────┘
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────────────┐
│           选择算法模式                        │
│  ┌───────────────┐    ┌───────────────────┐  │
│  │ 多源参考模式   │    │  单源盲测模式      │  │
│  │ (RANSAC等)   │    │  (卡尔曼滤波等)    │  │
│  └───────────────┘    └───────────────────┘  │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│           算法并行计算                        │
│  • 各雷达误差分析                            │
│  • 轨迹优化估计                              │
│  • 算法性能比较                              │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐     ┌───────────────────┐
│    优化轨迹输出       │     │   禁飞区入侵检测    │
└──────────────────┬──────────────────────────┘     └─────────┬─────────┘
                   │                                        │
                   ▼                                        ▼
        ┌──────────────────┐                    ┌──────────────────┐
        │   MCP坐标转语义   │                    │   生成检测报告     │
        │   (轨迹文字化)    │                    └──────────────────┘
        └────────┬─────────┘
                   │
                   ▼
        ┌──────────────────┐
        │   大模型智能分析  │
        │ (意图/质量/异常) │
        └────────┬─────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│         三维可视化展示 (Cesium.js)           │
│  • 多轨迹对比  • 误差热力图  • 动画回放      │
└─────────────────────────────────────────────┘
```

---

## 8. 数据文件格式说明

### 8.1 轨迹数据文件（CSV/Excel）

支持**多雷达站同时观测多目标**的数据格式：

| 列名 | 必填 | 说明 |
| --- | --- | --- |
| batch_id | 是 | 飞机批号/目标标识 |
| station_id | 是 | 雷达站号（多源数据必填） |
| time_stamp | 是 | 观测时间（格式：YYYY-MM-DD HH:MM:SS.sss） |
| longitude | 是 | 经度 |
| latitude | 是 | 纬度 |
| altitude | 否 | 高度（米） |
| speed | 否 | 速度（m/s） |

**数据示例**：

```
batch_id,station_id,time_stamp,longitude,latitude,altitude,speed
TARGET001,RADAR_A,2024-01-15 08:00:00.000,121.8000,31.2000,10000,250
TARGET001,RADAR_B,2024-01-15 08:00:00.500,121.8010,31.2010,10005,248
TARGET001,RADAR_C,2024-01-15 08:00:01.000,121.7995,31.1995,9995,252
TARGET002,RADAR_A,2024-01-15 08:00:00.000,120.5000,30.1000,8000,200
...
```

### 8.2 雷达站数据文件（CSV/Excel）

| 列名 | 必填 | 说明 |
| --- | --- | --- |
| station_id | 是 | 站号 |
| longitude | 是 | 经度 |
| latitude | 是 | 纬度 |
| altitude | 否 | 雷达站高度（米） |
| description | 否 | 备注 |

---

## 9. 项目创新点

- **多算法融合对比**：提供 RANSAC、卡尔曼滤波等多种算法，支持综合分析比较
- **场景自适应**：区分"多源参考"与"单源盲测"两种实际工程场景
- **MCP 语义增强**：自建 MCP Server 实现坐标到地理信息的语义转换，让大模型"理解"飞行轨迹
- **AI 深度分析**：轨迹文字化 + 大模型分析，实现从数据到洞察的智能转化
- **可视化专业性**：Cesium.js 三维展示，支持轨迹对比、误差热力图、动画回放
- **GPU 加速支持**：预留 GPU 加速接口，提升大规模数据处理性能

---

## 10. 技术参考

* **MCP Python SDK:** https://github.com/modelcontextprotocol/python-sdk
* **Cesium.js:** https://cesium.com/cesiumjs/
* **FastAPI:** https://fastapi.tiangolo.com/
* **DeepSeek API:** https://platform.deepseek.com/
