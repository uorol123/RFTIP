# Docker 容器部署指南

## 文档规则说明

本文档用于统一管理各类 Docker 容器的部署说明。请按以下规则添加新容器：

### 模块结构规范

每个容器的说明必须包含以下模块（按顺序）：

1. **概述** - 容器名称、用途简介
2. **端口映射** - 列出所有映射端口及用途
3. **启动命令** - 包含：
   - 拉取镜像命令
   - 启动容器命令（含环境变量）
   - Windows 单行版本
4. **访问信息** - API地址、Web控制台、默认账号密码
5. **常用操作** - 查看状态、日志、启停、删除等
6. **数据持久化** - 如何保留数据（如需）
7. **客户端连接示例** - Python/其他语言连接代码
8. **Docker Compose** - 推荐的生产环境配置
9. **注意事项** - 安全提示、常见问题

### 格式规范

- 使用二级标题 `##` 作为容器主标题
- 使用三级标题 `###` 作为模块子标题
- 代码块标明语言类型（bash、python、yaml）
- 重要警告使用 **加粗** 标注

---

## MinIO 对象存储

### 概述

MinIO 是一个高性能的分布式对象存储系统，兼容 Amazon S3 API。适用于存储图片、视频、文档等非结构化数据。

### 端口映射

| 端口 | 用途 | 说明 |
|------|------|------|
| 9000 | API 端口 | S3 兼容 API 访问 |
| 9001 | 控制台端口 | Web 管理界面 |

### 启动命令

**1. 拉取镜像（首次使用）**

```bash
docker pull minio/minio
```

**2. 启动 MinIO 容器**

```bash
docker run -d --name minio \
  -p 9000:9000 \
  -p 9001:9001 \
  -e MINIO_ROOT_USER=minioadmin \
  -e MINIO_ROOT_PASSWORD=minioadmin \
  minio/minio server /data --console-address ":9001"
```

**Windows 单行版本：**

```bash
docker run -d --name minio -p 9000:9000 -p 9001:9001 -e MINIO_ROOT_USER=minioadmin -e MINIO_ROOT_PASSWORD=minioadmin minio/minio server /data --console-address ":9001"
```

### 访问信息

| 项目 | 地址/值 |
|------|---------|
| API 地址 | http://localhost:9000 |
| Web 控制台 | http://localhost:9001 |
| 默认账号 | minioadmin |
| 默认密码 | minioadmin |

### 常用操作

```bash
# 查看容器状态
docker ps

# 查看日志
docker logs minio

# 停止容器
docker stop minio

# 启动容器
docker start minio

# 删除容器（需先停止）
docker rm minio

# 删除镜像
docker rmi minio/minio
```

### 数据持久化

当前配置数据存储在容器内，容器删除后数据会丢失。

如需保留数据，添加 `-v` 参数：

```bash
docker run -d --name minio \
  -p 9000:9000 \
  -p 9001:9001 \
  -e MINIO_ROOT_USER=minioadmin \
  -e MINIO_ROOT_PASSWORD=minioadmin \
  -v minio_data:/data \
  minio/minio server /data --console-address ":9001"
```

### Python 连接示例

```python
from minio import Minio

client = Minio(
    endpoint="localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False  # HTTP 使用 False，HTTPS 使用 True
)

# 创建存储桶
# client.make_bucket("mybucket")

# 上传文件
# client.fput_object("mybucket", "object-name", "local-file-path")
```

### Docker Compose（推荐）

```yaml
version: '3.8'

services:
  minio:
    image: minio/minio
    container_name: minio
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    command: server /data --console-address ":9001"
    volumes:
      - minio_data:/data

volumes:
  minio_data:
```

**使用方式：** 保存为 `docker-compose.yml`，然后执行 `docker compose up -d`

### 注意事项

1. **生产环境务必修改默认账号密码！** 修改 `MINIO_ROOT_USER` 和 `MINIO_ROOT_PASSWORD` 环境变量
2. **端口占用：** 如果 9000 或 9001 端口被占用，修改映射为 `-p 9002:9000 -p 9003:9001`
3. **分布式部署：** 生产环境建议使用分布式模式，参考官方文档

---

## Redis 缓存数据库

### 概述

Redis 是一个开源的内存数据结构存储系统，可用作数据库、缓存和消息中间件。支持字符串、哈希、列表、集合等多种数据结构。

### 端口映射

| 端口 | 用途 | 说明 |
|------|------|------|
| 6379 | 服务端口 | Redis 默认连接端口 |

### 启动命令

**1. 拉取镜像（首次使用）**

```bash
docker pull redis
```

**2. 启动 Redis 容器（基础版本）**

```bash
docker run -d --name redis -p 6379:6379 redis
```

**3. 启动 Redis 容器（带密码，推荐）**

```bash
docker run -d --name redis \
  -p 6379:6379 \
  redis --requirepass yourpassword
```

**Windows 单行版本（带密码）：**

```bash
docker run -d --name redis -p 6379:6379 redis --requirepass yourpassword
```

### 访问信息

| 项目 | 值 |
|------|-----|
| 连接地址 | localhost:6379 |
| 无密码版本 | 无需认证 |
| 带密码版本 | 使用 `--requirepass` 设置的密码 |

### 常用操作

```bash
# 查看容器状态
docker ps

# 查看日志
docker logs redis

# 进入 CLI（无密码）
docker exec -it redis redis-cli

# 进入 CLI（带密码）
docker exec -it redis redis-cli -a yourpassword

# 停止容器
docker stop redis

# 启动容器
docker start redis

# 删除容器（需先停止）
docker rm redis

# 删除镜像
docker rmi redis
```

### 数据持久化

如需数据持久化，添加 `-v` 参数：

```bash
docker run -d --name redis -p 6379:6379 -v redis_data:/data redis
```

Redis 默认开启 RDB 持久化，如需调整需自定义配置。

### Python 连接示例

**无密码版本：**

```python
import redis

client = redis.Redis(
    host='localhost',
    port=6379,
    decode_responses=True
)

client.set('key', 'value')
print(client.get('key'))
```

**带密码版本：**

```python
import redis

client = redis.Redis(
    host='localhost',
    port=6379,
    password='yourpassword',
    decode_responses=True
)

client.set('key', 'value')
print(client.get('key'))
```

### Docker Compose（推荐）

**基础版本：**

```yaml
version: '3.8'

services:
  redis:
    image: redis
    container_name: redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

**带密码版本：**

```yaml
version: '3.8'

services:
  redis:
    image: redis
    container_name: redis
    ports:
      - "6379:6379"
    command: redis-server --requirepass yourpassword
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

**使用方式：** 保存为 `docker-compose.yml`，然后执行 `docker compose up -d`

### 注意事项

1. **生产环境务必设置密码**，避免未授权访问
2. **自定义配置：** 如需自定义配置，可用 `-v` 挂载 `redis.conf` 文件
3. **端口占用：** 端口 6379 是 Redis 默认端口，被占用时可修改映射
4. **内存管理：** 注意配置最大内存限制和淘汰策略，避免内存耗尽

---

## MySQL 关系型数据库

### 概述

MySQL 是最流行的开源关系型数据库管理系统，广泛应用于 Web 应用程序的数据存储。支持事务处理、外键约束、视图、存储过程等完整的关系数据库功能。

### 端口映射

| 端口 | 用途 | 说明 |
|------|------|------|
| 3306 | 服务端口 | MySQL 默认连接端口 |

### 启动命令

**1. 拉取镜像（首次使用）**

```bash
docker pull mysql
```

**2. 启动 MySQL 容器（基础版本）**

```bash
docker run -d --name mysql \
  -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=rootpassword \
  mysql
```

**3. 启动 MySQL 容器（推荐配置）**

```bash
docker run -d --name mysql \
  -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=rootpassword \
  -e MYSQL_DATABASE=mydb \
  -e MYSQL_USER=myuser \
  -e MYSQL_PASSWORD=mypassword \
  mysql
```

**Windows 单行版本（推荐配置）：**

```bash
docker run -d --name mysql -p 3306:3306 -e MYSQL_ROOT_PASSWORD=rootpassword -e MYSQL_DATABASE=mydb -e MYSQL_USER=myuser -e MYSQL_PASSWORD=mypassword mysql
```

### 访问信息

| 项目 | 值 |
|------|-----|
| 连接地址 | localhost:3306 |
| Root 用户 | root |
| Root 密码 | `MYSQL_ROOT_PASSWORD` 设置的值 |
| 额外数据库 | `MYSQL_DATABASE` 设置的数据库名 |
| 额外用户 | `MYSQL_USER` 设置的用户名 |
| 额外用户密码 | `MYSQL_PASSWORD` 设置的密码 |

### 常用操作

```bash
# 查看容器状态
docker ps

# 查看日志
docker logs mysql

# 进入 MySQL CLI
docker exec -it mysql mysql -uroot -p

# 停止容器
docker stop mysql

# 启动容器
docker start mysql

# 删除容器（需先停止）
docker rm mysql

# 删除镜像
docker rmi mysql
```

### 数据持久化

当前配置数据存储在容器内，容器删除后数据会丢失。

如需保留数据，添加 `-v` 参数：

```bash
docker run -d --name mysql \
  -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=rootpassword \
  -v mysql_data:/var/lib/mysql \
  mysql
```

### Python 连接示例

**使用 pymysql：**

```python
import pymysql

connection = pymysql.connect(
    host='localhost',
    port=3306,
    user='root',
    password='rootpassword',
    database='mydb'
)

cursor = connection.cursor()
cursor.execute("SELECT VERSION()")
version = cursor.fetchone()
print(f"MySQL version: {version[0]}")

connection.close()
```

**使用 mysql-connector-python：**

```python
import mysql.connector

connection = mysql.connector.connect(
    host='localhost',
    port=3306,
    user='root',
    password='rootpassword',
    database='mydb'
)

cursor = connection.cursor()
cursor.execute("SELECT VERSION()")
version = cursor.fetchone()
print(f"MySQL version: {version[0]}")

connection.close()
```

### Docker Compose（推荐）

**基础版本：**

```yaml
version: '3.8'

services:
  mysql:
    image: mysql
    container_name: mysql
    ports:
      - "3306:3306"
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
    volumes:
      - mysql_data:/var/lib/mysql

volumes:
  mysql_data:
```

**完整配置版本：**

```yaml
version: '3.8'

services:
  mysql:
    image: mysql
    container_name: mysql
    ports:
      - "3306:3306"
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: mydb
      MYSQL_USER: myuser
      MYSQL_PASSWORD: mypassword
    volumes:
      - mysql_data:/var/lib/mysql
    restart: unless-stopped

volumes:
  mysql_data:
```

**使用方式：** 保存为 `docker-compose.yml`，然后执行 `docker compose up -d`

### 注意事项

1. **生产环境务必使用强密码**，修改所有默认密码环境变量
2. **字符集设置：** 默认使用 `latin1`，如需 UTF-8 支持添加：`--character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci`
3. **时区设置：** 默认为 UTC，如需本地时区添加：`-e TZ=Asia/Shanghai`
4. **端口占用：** 端口 3306 是 MySQL 默认端口，被占用时可修改映射
5. **备份策略：** 生产环境建议定期备份，可使用 `docker exec mysql mysqldump` 命令
6. **配置文件：** 如需自定义配置，可用 `-v` 挂载自定义 `my.cnf` 文件到 `/etc/mysql/conf.d/`

---


