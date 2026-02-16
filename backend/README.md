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
├── app/                          # Main application package
│   ├── __init__.py
│   ├── models/                   # SQLAlchemy models
│   │   └── __init__.py
│   ├── routers/                  # API endpoints (FastAPI routers)
│   │   ├── __init__.py
│   │   ├── auth.py              # Authentication endpoints
│   │   └── health.py            # Health check endpoints
│   ├── schemas/                  # Pydantic models for request/response
│   │   └── __init__.py
│   └── services/                 # Business logic
│       └── __init__.py
├── core/                         # Core configuration and utilities
│   ├── __init__.py
│   ├── config.py                # Pydantic settings
│   └── database.py              # Database session and engine
├── migrations/                   # Alembic migration files
├── tests/                        # Test files
├── .env                         # Environment variables (not committed)
├── .env.example                 # Example environment variables
├── alembic.ini                  # Alembic configuration
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
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
- 轨迹数据解析入库
- 多源参考模式（RANSAC 算法）
- 单源盲测模式（卡尔曼滤波）
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

> **推荐方式：使用 Docker 部署依赖服务**
> 项目依赖 MySQL、Redis、MinIO 等服务，建议使用 Docker 快速搭建环境。详细说明请参考 [Docker 部署指南](./docker-deploy-guide.md)。

---

### 一、依赖服务部署

#### 1. MySQL 数据库

**方式 A：Docker 部署（推荐）**

```bash
# 启动 MySQL 容器
docker run -d --name mysql \
  -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=yourpassword \
  -e MYSQL_DATABASE=rftip \
  mysql:8.0
```

**方式 B：本地安装**

下载并安装 [MySQL 8.0+](https://dev.mysql.com/downloads/mysql/)，然后创建数据库：

```sql
CREATE DATABASE rftip CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### 2. Redis 缓存

**Docker 部署（推荐）**

```bash
docker run -d --name redis -p 6379:6379 redis
```

详细说明见：[Docker 部署指南 - Redis](./docker-deploy-guide.md#redis-缓存数据库)

#### 3. MinIO 对象存储

**Docker 部署（推荐）**

```bash
docker run -d --name minio \
  -p 9000:9000 -p 9001:9001 \
  -e MINIO_ROOT_USER=minioadmin \
  -e MINIO_ROOT_PASSWORD=minioadmin \
  minio/minio server /data --console-address ":9001"
```

访问控制台：http://localhost:9001

详细说明见：[Docker 部署指南 - MinIO](./docker-deploy-guide.md#minio-对象存储)

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
python tests/test_connections.py

# 测试 SMTP 邮箱配置
python tests/test_smtp.py
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

### 核心数据表

| 表名 | 说明 |
| --- | --- |
| users | 用户信息表 |
| user_login_logs | 用户登录日志表 |
| data_files | 数据文件表 |
| flight_tracks_raw | 原始飞行轨迹表 |
| flight_tracks_corrected | 修正后飞行轨迹表 |
| radar_stations | 雷达站信息表 |
| restricted_zones | 用户自定义禁飞区表 |
| zone_intrusions | 禁飞区入侵记录表 |

完整 SQL 建表语句请参考[主项目 README](../README.md#3-数据库设计)

---

## API 接口文档（规划）

### 用户认证

| 端点 | 方法 | 说明 |
| --- | --- | --- |
| `/api/auth/register` | POST | 用户注册 |
| `/api/auth/login` | POST | 用户登录 |
| `/api/auth/profile` | GET | 获取用户信息 |

### 文件管理

| 端点 | 方法 | 说明 |
| --- | --- | --- |
| `/api/files/upload` | POST | 上传数据文件 |
| `/api/files/list` | GET | 获取文件列表 |
| `/api/files/{file_id}` | GET | 获取文件详情 |
| `/api/files/{file_id}` | DELETE | 删除文件 |

### 轨迹处理

| 端点 | 方法 | 说明 |
| --- | --- | --- |
| `/api/tracks/process` | POST | 处理轨迹数据 |
| `/api/tracks/raw` | GET | 获取原始轨迹 |
| `/api/tracks/corrected` | GET | 获取修正轨迹 |

### AI 分析

| 端点 | 方法 | 说明 |
| --- | --- | --- |
| `/api/analysis/trajectory` | POST | 整体轨迹分析 |
| `/api/analysis/segment` | POST | 区间轨迹分析 |

### 禁飞区管理

| 端点 | 方法 | 说明 |
| --- | --- | --- |
| `/api/zones` | POST | 创建禁飞区 |
| `/api/zones` | GET | 获取禁飞区列表 |
| `/api/zones/{zone_id}` | DELETE | 删除禁飞区 |
| `/api/zones/intrusions` | GET | 获取入侵记录 |

---

## 核心算法说明

### 多源参考模式（RANSAC）

当多台雷达探测同一目标时，利用 RANSAC 算法剔除偏离群体的"坏点"站号，并计算该站的系统性偏差。

**适用场景：** 大部分雷达可靠，需要识别并校准故障/低精度雷达。

### 单源盲测模式（卡尔曼滤波）

采用卡尔曼滤波算法，基于物理运动模型（匀速/匀加速）对单站噪声数据进行预测与修正。

**适用场景：** 不确定可靠性，需要获得平滑连续的飞行轨迹。

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
该项目使用了mysql，redis，minio等第三方工具，建议使用docker进行环境搭建，可以参考docker-deploy-guide.md

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
