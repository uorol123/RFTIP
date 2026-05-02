# RFTIP 后端项目

**RadarFusionTrack Intelligence Platform - Backend**

基于 FastAPI (Python) 构建的智能雷达轨迹分析平台后端服务。

---

## 技术栈

| 技术 | 版本 | 说明 |
| --- | --- | --- |
| FastAPI | - | 高性能异步 Web 框架 |
| Python | >= 3.12 | 编程语言 |
| SQLAlchemy | - | Python SQL 工具包和 ORM |
| MySQL | 8.0 | 关系型数据库 |
| PyMySQL | - | MySQL 驱动 |
| PyJWT | - | JWT 认证支持 |
| python-multipart | - | 文件上传支持 |
| MinIO SDK | - | S3 兼容对象存储（可选） |

---

## 项目结构

```
backend/
├── app/                          # 应用主目录
│   ├── __init__.py
│   ├── algorithms/               # 算法模块
│   │   ├── base.py              # 算法基类
│   │   ├── registry.py          # 算法注册表
│   │   ├── factory.py           # 算法工厂
│   │   ├── multi_source/        # 多源参考模式
│   │   │   ├── preprocessing/   #   预处理（提取、插值、匹配）
│   │   │   ├── mrra/            #   MRRA 梯度下降算法
│   │   │   ├── ransac/          #   RANSAC 算法
│   │   │   ├── ransac_heuristic/#   RANSAC 启发式算法
│   │   │   └── weighted_lstsq/  #   加权最小二乘算法
│   │   └── single_source/       # 单源盲测模式
│   │       ├── kalman/          #   卡尔曼滤波
│   │       ├── particle_filter/ #   粒子滤波
│   │       └── spline/          #   样条拟合
│   ├── models/                   # SQLAlchemy 数据模型
│   ├── routers/                  # API 路由端点
│   ├── schemas/                  # Pydantic 请求/响应模型
│   └── services/                 # 业务逻辑层
├── core/                         # 核心配置与工具
│   ├── config.py                # 应用配置
│   ├── database.py              # 数据库连接与会话
│   ├── exceptions.py            # 自定义异常
│   ├── error_handler.py         # 全局异常处理
│   ├── middleware.py            # 中间件
│   └── logging.py               # 日志配置
├── tests/                        # 测试文件
├── .env                         # 环境变量（不提交）
├── .env.example                 # 环境变量示例
├── main.py                      # 应用入口
├── requirements.txt             # Python 依赖
└── README.md                    # 本文档
```

---

## 功能模块（规划中）

### 1. 用户认证模块
- 用户注册/登录
- JWT Token 生成与验证
- 密码加密存储
- 登录日志记录

### 2. 文件管理模块
- CSV/Excel 文件上传
- 文件解析与验证
- 文件存储（本地/MinIO）
- 公开/私有状态管理
- 文件删除

### 3. 轨迹数据处理模块
- 轨迹数据解析入库（支持中英文列名）
- **预处理管道**：速度/航向从位置计算，噪音过滤
- **多源参考模式**（RANSAC 算法）：1秒时间窗口 + 0.12度位置阈值
- **单源盲测模式**（卡尔曼滤波）：基于运动模型平滑
- **可扩展算法接口**：支持动态注册新算法
- 修正结果存储

### 4. AI 分析模块
- 轨迹特征提取
- MCP Server 集成
- 大模型调用（DeepSeek/Ollama）
- 分析报告生成

### 5. 禁飞区管理模块
- 禁飞区创建（圆形/多边形）
- 高度限制设置
- 实时入侵检测
- 邮件预警通知

### 6. 数据查询模块
- 轨迹数据查询（带权限控制）
- 雷达站数据查询
- 禁飞区查询
- 入侵记录查询

---

## 快速开始

> **规划中：** 后端依赖服务（MySQL、Redis、MinIO）将通过 Docker Compose 一键部署，目前需手动启动各服务。

---

### 一、依赖服务部署（手动）

项目依赖 MySQL、Redis、MinIO 三个服务，需分别启动：

```bash
# MySQL
docker run -d --name mysql -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=yourpassword \
  -e MYSQL_DATABASE=rftip \
  mysql:8.0

# Redis
docker run -d --name redis -p 6379:6379 redis

# MinIO
docker run -d --name minio -p 9000:9000 -p 9001:9001 \
  -e MINIO_ROOT_USER=minioadmin \
  -e MINIO_ROOT_PASSWORD=minioadmin \
  minio/minio server /data --console-address ":9001"
```

---

### 二、后端应用部署

#### 1. 环境准备

**安装 Python 3.12+**

**创建虚拟环境**

```bash
python -m venv venv
```

**激活虚拟环境**

Windows:
```bash
venv\Scripts\activate
```

Linux/Mac:
```bash
source venv/bin/activate
```

#### 2. 安装依赖

```bash
pip install -r requirements.txt
```

#### 3. 配置环境变量

复制环境变量模板：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置数据库连接等信息

> **生成 SECRET_KEY**：`python -c "import secrets; print(secrets.token_hex(32))"`

#### 4. 初始化服务

运行初始化脚本，自动创建数据库表和 MinIO 存储桶：

```bash
python init_services.py
```

该脚本会自动：
- 创建数据库和所有表
- 检查 Redis 连接
- 创建 MinIO 存储桶
- 创建必要的目录（logs/、uploads/、exports/）

#### 5. 验证配置（可选）

运行测试脚本验证各服务连接：

```bash
# 测试 MySQL、Redis、MinIO 连接
python init_services.py
```

---

### 三、启动应用

**开发模式：**

```bash
python main.py
```

或使用 uvicorn：

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**生产模式：**

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

或使用 Gunicorn + Uvicorn：

```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

### 四、访问服务

| 服务 | 地址 |
|------|------|
| API 服务 | http://localhost:8000 |
| API 文档 | http://localhost:8000/docs |
| MinIO 控制台 | http://localhost:9001 |

---

## 数据库设计

### 用户与文件

| 表名 | 说明 |
| --- | --- |
| users | 用户信息表 |
| user_login_logs | 用户登录日志表 |
| data_files | 上传文件表（MinIO 存储） |

### 轨迹数据

| 表名 | 说明 |
| --- | --- |
| flight_tracks_raw | 原始飞行轨迹表 |
| flight_tracks_corrected | 修正后飞行轨迹表 |
| radar_stations | 雷达站信息表 |

### 误差分析

| 表名 | 说明 |
| --- | --- |
| error_analysis_tasks | 误差分析任务表 |
| track_segments | 轨迹段表 |
| match_groups | 匹配组表 |
| error_results | 误差结果表 |
| track_interpolated_points | 轨迹插值点表 |
| smoothed_trajectory_results | 平滑轨迹结果表 |

### 禁飞区

| 表名 | 说明 |
| --- | --- |
| restricted_zones | 用户自定义禁飞区表 |
| zone_intrusions | 禁飞区入侵记录表 |


## 核心算法说明

### 重要变更说明

**v2.0 重构更新**（基于真实数据分析）：

1. **不使用原始速度/航向列**：原始数据中的 `speed` 和 `heading` 列存在数据质量问题（速度单位不明确、航向值0-5度非真实方位角），系统现在**完全从位置数据计算速度和航向**

2. **时间窗口参数调整**：基于真实数据分析（95%分位数=1.000秒），同时观测时间窗口从5秒调整为**1秒**

3. **位置匹配阈值**：采用**0.12度**（约13.3km）作为位置匹配阈值

### 预处理管道

```python
# 速度计算（Haversine距离 + 时间差）
def calculate_velocity(point1, point2):
    distance = haversine_distance(point1['lat'], point1['lon'],
                                  point2['lat'], point2['lon'])
    time_diff = (point2['timestamp'] - point1['timestamp']).total_seconds()
    speed_mps = distance / time_diff
    speed_kmh = speed_mps * 3.6
    heading = calculate_bearing(point1, point2)
    return speed_mps, speed_kmh, heading
```

**噪音过滤规则**：
- 最小速度：50 km/h（失速速度以上）
- 最大速度：800 km/h（民航飞机最大速度）

### 多源参考模式

当多台雷达探测同一目标时，提供以下算法进行误差分析：

**MRRA（坐标下降迭代寻优）**：依次优化各雷达站的方位角、距离、俯仰角系统误差。通过航迹提取、插值、匹配形成匹配组后，使用坐标下降迭代寻优寻找最小代价函数对应的误差参数。

**RANSAC（随机抽样一致性）**：利用 RANSAC 算法剔除偏离群体的"坏点"站号。

**启发式 RANSAC**：通过偏差排序与差值突变检测识别故障雷达站。

**同时观测匹配条件**：
1. 时间差 ≤ 1秒
2. 位置距离 ≤ 0.12度（约13.3km）
3. 不同雷达站

**适用场景**：大部分雷达可靠，需要识别并校准故障/低精度雷达。

### 单源盲测模式（卡尔曼滤波）

采用卡尔曼滤波算法，基于物理运动模型（匀速）对单站噪声数据进行预测与修正。

**状态向量**：`[lat, lng, alt, velocity_lat, velocity_lng, velocity_alt]`

**适用场景**：不确定可靠性，需要获得平滑连续的飞行轨迹。

### 可扩展算法接口

```python
# 支持动态注册新算法
AlgorithmFactory.register_algorithm('particle', ParticleFilterAlgorithm)

# 使用算法
algorithm = AlgorithmFactory.create_algorithm('particle', num_particles=200)
result = algorithm.correct(observations)
```

### 数据分析结果

| 参数 | 分析结果 | 选择依据 |
|------|---------|----------|
| TIME_WINDOW_MATCH | 95%分位数 = 1.000秒 | 选择1秒窗口 |
| POSITION_THRESHOLD | 98%观测 < 0.12度 | 参考文档推荐值 |
| MAX_SPEED_KMH | 民航飞机巡航速度 | 800 km/h |
| MIN_SPEED_KMH | 失速速度以上 | 50 km/h |

---

## 安全说明

1. **密码加密**: 使用 bcrypt 或类似算法加密存储
2. **JWT 认证**: 所有受保护接口需要有效的 JWT Token
3. **SQL 注入防护**: 使用参数化查询（SQLAlchemy）
4. **CORS 配置**: 前端地址需要正确配置
5. **文件上传**: 验证文件类型和大小，防止恶意文件

---

## 部署说明

### 生产环境部署

1. **使用 Gunicorn + Uvicorn**

```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

2. **环境变量配置**

确保所有敏感信息通过环境变量配置，不要硬编码。

3. **数据库连接池**

配置合适的连接池大小以提高性能。

---

## 配置文件说明
配置文件位于 `.env` 文件中，在项目一级目录，仓库提供一个示例文件 `.env.example`

### 配置参考
该项目使用了mysql，redis，minio等第三方工具，建议使用docker进行环境搭建，详见上方各服务的 Docker 部署命令。

### 邮箱配置说明
根据你使用的邮箱，按以下步骤获取授权码：

#### QQ 邮箱
1. 登录 QQ 邮箱网页版
2. 点击「设置」→「账户」
3. 找到「POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务」
4. 开启「IMAP/SMTP服务」
5. 生成授权码（不是 QQ 密码！）

#### 163 邮箱
1. 登录 163 邮箱网页版
2. 点击「设置」→「POP3/SMTP/IMAP」
3. 开启「IMAP/SMTP服务」
4. 发送短信验证后获取授权码

#### Gmail
1. 开启两步验证
2. 进入 Google 账户安全设置
3. 生成「应用专用密码」

### 配置验证
在tests目录下，运行test_smtp.py脚本可以测试配置是否正确

## 相关文档

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [SQLAlchemy 官方文档](https://docs.sqlalchemy.org/)
- [MySQL 官方文档](https://dev.mysql.com/doc/)
- [项目主 README](../README.md)
