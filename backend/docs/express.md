# RFTIP 后端 API 文档

> 雷达轨迹监测与智能分析平台 - 后端接口规范
> Base URL: `http://localhost:8000/api`

---

## 📋 目录

1. [认证模块 (Auth)](#1-认证模块-auth)
2. [文件管理模块 (Files)](#2-文件管理模块-files)
3. [轨迹处理模块 (Tracks)](#3-轨迹处理模块-tracks)
4. [禁飞区管理模块 (Zones)](#4-禁飞区管理模块-zones)
5. [AI 分析模块 (Analysis)](#5-ai-分析模块-analysis)
6. [数据查询模块 (Query)](#6-数据查询模块-query)
7. [WebSocket 实时推送 (WebSocket)](#7-websocket-实时推送-websocket)
8. [健康检查模块 (Health)](#8-健康检查模块-health)

---

## 1. 认证模块 (Auth)

**Base Path**: `/api/auth`

### 1.1 发送邮箱验证码

```http
POST /api/auth/send-verification-code
```

**请求体**:
```json
{
  "email": "user@example.com"
}
```

**响应**:
```json
{
  "message": "验证码已发送",
  "email": "user@example.com",
  "expire_in": 300
}
```

**说明**:
- 验证码有效期为 5 分钟
- 每次发送会覆盖之前的验证码
- 验证码会在日志中打印（方便测试）
- 60 秒内不能重复发送

---

### 1.2 上传临时头像

```http
POST /api/auth/upload-temp-avatar
```

**请求头**:
```
Content-Type: multipart/form-data
```

**请求体** (form-data):
```
avatar: (binary) 头像文件
```

**响应**:
```json
{
  "temp_token": "a1b2c3d4e5f6...",
  "message": "临时头像上传成功，请在一小时内完成注册"
}
```

**说明**:
- 无需登录即可使用
- 头像文件支持：jpg、png、gif、webp（最大 5MB）
- 临时头像存储在 Redis，1 小时后自动过期
- 返回的 `temp_token` 用于注册时传入
- **IP 限流**：每 IP 每分钟最多上传 3 次，防止恶意攻击
- 前端可使用 FileReader 或 URL.createObjectURL 进行本地预览

---

### 1.3 用户注册

```http
POST /api/auth/register
```

**请求体**:
```json
{
  "username": "testuser",
  "email": "user@example.com",
  "password": "password123",
  "verification_code": "123456",
  "full_name": "张三",
  "phone": "13800138000",
  "temp_token": "a1b2c3d4e5f6..."
}
```

**响应**:
```json
{
  "id": 1,
  "username": "testuser",
  "email": "user@example.com",
  "full_name": "张三",
  "phone": "13800138000",
  "avatar_url": "avatars/user_1_abc123.jpg",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

**说明**:
- 需先调用发送验证码接口获取验证码
- 用户名: 3-50 字符
- 密码: 至少 6 字符
- `temp_token`: 可选，如果需要上传头像，需先调用 `POST /api/auth/upload-temp-avatar` 上传头像获取 temp_token
- 注册成功后，临时头像会被上传到 MinIO，Redis 中的临时数据会被删除
- 数据库存储的是 object_name（如 `avatars/user_1_abc123.jpg`），不是 MinIO URL

---

### 1.4 用户登录

```http
POST /api/auth/login
```

**请求体** (form-data):
```
username: testuser 或 user@example.com
password: password123
```

**响应**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "user@example.com"
  }
}
```

**说明**:
- 支持 username 或 email 登录
- Token 有效期 30 分钟
- 自动记录登录日志

---

### 1.5 用户登出

```http
POST /api/auth/logout
```

**请求头**:
```
Authorization: Bearer {access_token}
```

**响应**:
```json
{
  "message": "登出成功"
}
```

**说明**:
- 客户端应删除存储的 Token
- 自动记录登出时间

---

### 1.6 获取当前用户信息

```http
GET /api/auth/profile
```

**请求头**:
```
Authorization: Bearer {access_token}
```

**响应**:
```json
{
  "id": 1,
  "username": "testuser",
  "email": "user@example.com",
  "full_name": "张三",
  "phone": "13800138000",
  "avatar_url": null,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

### 1.7 更新用户信息

```http
PUT /api/auth/profile
```

**请求头**:
```
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

**请求体** (form-data):
```
full_name: 李四
phone: 13900139000
avatar: (binary) 头像文件 (可选)
```

**说明**:
- 使用 `multipart/form-data` 格式
- 支持直接上传头像文件
- 头像文件支持：jpg、png、gif、webp（最大 5MB）
- 上传新头像会自动删除旧头像

---

### 1.8 上传头像（登录后）

```http
POST /api/auth/upload-avatar
```

**请求头**:
```
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

**请求体** (form-data):
```
avatar: (binary) 头像文件
```

**响应**:
```json
{
  "avatar_id": "avatars/user_1_abc123.jpg",
  "message": "头像上传成功"
}
```

**说明**:
- 需要登录后才能使用
- 用于已注册用户更换头像
- 头像文件支持：jpg、png、gif、webp（最大 5MB）
- 返回的 `avatar_id`（即 object_name）用于更新用户信息
- 注意：注册时请使用 `POST /api/auth/upload-temp-avatar` 接口

---

### 1.9 获取头像

```http
GET /api/auth/avatar/{user_id}
```

**响应**: (image/jpeg) 头像图片文件

**说明**:
- 返回指定用户的头像图片文件
- 如果用户未设置头像，返回 404

---

### 1.10 修改密码

```http
POST /api/auth/change-password
```

**请求头**:
```
Authorization: Bearer {access_token}
```

**请求体**:
```json
{
  "old_password": "password123",
  "new_password": "newpassword456"
}
```

---

### 1.11 获取登录日志

```http
GET /api/auth/login-logs?limit=10
```

**请求头**:
```
Authorization: Bearer {access_token}
```

**响应**:
```json
[
  {
    "id": 1,
    "login_time": "2024-01-01T10:00:00Z",
    "logout_time": "2024-01-01T12:00:00Z",
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0...",
    "status": "success",
    "failure_reason": null
  }
]
```

---

### 📝 认证模块 - 前端反馈问题

1. **Token 刷新机制**: 当前 Token 有效期 30 分钟，是否需要 refresh_token 自动刷新？
2. **第三方登录**: 是否需要集成微信、GitHub 等第三方登录？
3. **手机验证码**: 当前仅支持邮箱验证码，是否需要添加短信验证码？
4. **密码重置**: 是否需要「忘记密码」功能？

---

## 2. 文件管理模块 (Files)

**Base Path**: `/api/files`

### 2.1 上传数据文件（单个）

```http
POST /api/files/upload
```

**请求头**:
```
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

**请求体** (form-data):
```
file: (binary) CSV 或 Excel 文件
category: trajectory (可选，分类: trajectory / radar_station)
```

**响应**:
```json
{
  "file_id": 1,
  "filename": "data.csv",
  "file_size": 1024000,
  "category": "trajectory",
  "status": "processing",
  "message": "文件上传成功，正在处理"
}
```

**说明**:
- 支持格式: CSV, Excel (.xlsx, .xls)
- 文件上传后**自动处理**：
  1. 解析文件内容
  2. 预处理过滤噪音点
  3. 直接存储到 MySQL
  4. 通过 WebSocket 推送进度
- **分类**：
  - `trajectory`: 轨迹数据文件
  - `radar_station`: 雷达站配置文件

---

### 2.2 批量上传数据文件

```http
POST /api/files/upload-batch
```

**请求头**:
```
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

**请求体** (form-data):
```
files: (binary) 多个 CSV 或 Excel 文件
category: trajectory (可选)
```

**响应**:
```json
{
  "task_id": "batch_123",
  "total_files": 5,
  "files": [
    {"file_id": 1, "filename": "data1.csv", "status": "processing"},
    {"file_id": 2, "filename": "data2.csv", "status": "processing"},
    {"file_id": 3, "filename": "data3.csv", "status": "pending"},
    {"file_id": 4, "filename": "data4.csv", "status": "pending"},
    {"file_id": 5, "filename": "data5.csv", "status": "pending"}
  ],
  "message": "批量上传任务已创建"
}
```

**说明**:
- 单次最多上传 10 个文件
- 每个文件独立处理
- 通过 WebSocket 推送每个文件的处理进度

---

### 2.3 生成文件分享链接

```http
POST /api/files/{file_id}/share
```

**请求头**:
```
Authorization: Bearer {access_token}
```

**请求体**:
```json
{
  "expire_hours": 24,
  "password": null,
  "max_downloads": null
}
```

**响应**:
```json
{
  "share_token": "abc123xyz",
  "share_url": "https://rftip.example.com/share/abc123xyz",
  "expire_at": "2024-01-02T10:00:00Z",
  "qr_code": "data:image/png;base64,iVBORw0KGgoAAA..."
}
```

**说明**:
- `expire_hours`: 过期小时数，默认 24 小时，最大 168 小时（7天）
- `password`: 访问密码，可选
- `max_downloads`: 最大下载次数，可选
- 返回二维码图片（base64），便于移动端扫码访问

---

### 2.4 访问分享文件

```http
GET /api/files/share/{share_token}
```

**请求头** (可选):
```
X-Share-Password: password123
```

**响应**: 文件流（直接下载）

---

### 2.5 获取文件列表

```http
GET /api/files/?skip=0&limit=20&category=trajectory
```

**请求头**:
```
Authorization: Bearer {access_token}
```

**查询参数**:
- `skip`: 跳过条数，默认 0
- `limit`: 返回条数，默认 20
- `category`: 分类筛选，trajectory / radar_station
- `status`: 状态筛选，pending / processing / completed / failed
- `search`: 文件名搜索

**响应**:
```json
{
  "total": 100,
  "files": [
    {
      "id": 1,
      "filename": "data.csv",
      "file_size": 1024000,
      "category": "trajectory",
      "row_count": 1000,
      "status": "completed",
      "is_public": false,
      "share_url": "https://rftip.example.com/share/abc123xyz",
      "uploaded_at": "2024-01-01T00:00:00Z",
      "processed_at": "2024-01-01T00:01:00Z"
    }
  ]
}
```

---

### 2.6 获取文件处理状态（实时）

```http
GET /api/files/{file_id}/status
```

**请求头**:
```
Authorization: Bearer {access_token}
```

**响应**:
```json
{
  "file_id": 1,
  "filename": "data.csv",
  "status": "processing",
  "progress": 45.5,
  "stage": "预处理中",
  "message": null,
  "processed_rows": 455,
  "total_rows": 1000,
  "outliers_filtered": 23
}
```

**状态说明**:
- `pending`: 等待处理
- `processing`: 正在处理（包含预处理阶段）
- `completed`: 处理完成
- `failed`: 处理失败

**处理阶段**:
- `解析中`: 读取文件内容
- `预处理中`: 过滤噪音点
- `存储中`: 写入数据库
- `完成`: 处理完成

---

### 2.7 获取文件详情

```http
GET /api/files/{file_id}
```

**请求头**:
```
Authorization: Bearer {access_token}
```

**响应**:
```json
{
  "id": 1,
  "filename": "data.csv",
  "file_size": 1024000,
  "category": "trajectory",
  "row_count": 1000,
  "status": "completed",
  "is_public": false,
  "uploaded_at": "2024-01-01T00:00:00Z",
  "processed_at": "2024-01-01T00:01:00Z",
  "share_info": {
    "share_token": "abc123xyz",
    "share_url": "https://rftip.example.com/share/abc123xyz",
    "expire_at": "2024-01-02T10:00:00Z",
    "download_count": 5
  }
}
```

---

### 2.8 删除文件

```http
DELETE /api/files/{file_id}
```

**请求头**:
```
Authorization: Bearer {access_token}
```

**响应**: 204 No Content

---

### 2.9 取消分享链接

```http
DELETE /api/files/{file_id}/share
```

**请求头**:
```
Authorization: Bearer {access_token}
```

**响应**: 204 No Content

---

### 2.10 文件处理 WebSocket

**WebSocket 连接**:
```
ws://localhost:8000/api/files/ws/{file_id}
```

**连接请求头**:
```
Authorization: Bearer {access_token}
```

**推送消息格式**:
```json
{
  "type": "progress",
  "file_id": 1,
  "data": {
    "status": "processing",
    "progress": 45.5,
    "stage": "预处理中",
    "processed_rows": 455,
    "total_rows": 1000,
    "outliers_filtered": 23,
    "message": "正在过滤噪音点..."
  }
}
```

**消息类型**:
- `progress`: 处理进度更新
- `completed`: 处理完成
- `error`: 处理错误

**处理完成消息**:
```json
{
  "type": "completed",
  "file_id": 1,
  "data": {
    "status": "completed",
    "progress": 100.0,
    "processed_rows": 1000,
    "outliers_filtered": 52,
    "tracks_detected": 45,
    "message": "处理完成"
  }
}
```

**前端使用示例**:
```javascript
const ws = new WebSocket(`ws://localhost:8000/api/files/ws/${file_id}`, {
  headers: { 'Authorization': `Bearer ${token}` }
});

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  if (message.type === 'progress') {
    updateProgress(message.data.progress);
    updateStatus(message.data.stage);
  } else if (message.type === 'completed') {
    showResults(message.data);
  }
};
```

---

### 📝 文件处理流程

```
┌─────────────┐
│  上传文件   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  解析文件   │ (支持 CSV/Excel，中英文列名自动识别)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  预处理     │ (按站号+批号分组，计算速度过滤噪音)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  存储到MySQL│ (原始轨迹数据)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  WebSocket  │ (推送完成消息)
│  推送进度   │
└─────────────┘
```

---

### 📝 文件管理模块 - 前端反馈问题

1. ~~文件预览~~ 不需要
2. ✅ 批量上传：已支持，单次最多 10 个文件
3. ✅ 分享链接：已支持，可选密码和过期时间
4. ✅ 文件分类：已支持，trajectory / radar_station
5. ✅ WebSocket 进度推送：已支持，实时推送处理进度

---

### 2.3 获取文件列表

```http
GET /api/files/?skip=0&limit=20
```

**请求头**:
```
Authorization: Bearer {access_token}
```

**响应**:
```json
{
  "total": 100,
  "files": [
    {
      "id": 1,
      "filename": "data.csv",
      "file_size": 1024000,
      "row_count": 1000,
      "status": "completed",
      "is_public": false,
      "uploaded_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

---

### 2.4 获取文件详情

```http
GET /api/files/{file_id}
```

**请求头**:
```
Authorization: Bearer {access_token}
```

---

### 2.5 删除文件

```http
DELETE /api/files/{file_id}
```

**请求头**:
```
Authorization: Bearer {access_token}
```

**响应**: 204 No Content

---

### 2.6 更新文件可见性

```http
PUT /api/files/{file_id}
```

**请求头**:
```
Authorization: Bearer {access_token}
```

**请求体**:
```json
{
  "is_public": true
}
```

---

### 2.7 获取文件处理状态

```http
GET /api/files/{file_id}/status
```

**请求头**:
```
Authorization: Bearer {access_token}
```

**响应**:
```json
{
  "file_id": 1,
  "status": "processing",
  "progress": 50.0,
  "message": null,
  "processed_rows": 500,
  "total_rows": 1000
}
```

**说明**:
- status: pending / processing / completed / failed

---

### 📝 文件管理模块 - 前端反馈问题

1. **文件预览**: 是否需要文件内容预览功能？
2. **批量上传**: 是否需要支持批量上传多个文件？
3. **文件分享**: 公开文件是否需要生成分享链接？
4. **文件分类**: 是否需要文件夹或标签分类功能？
5. **进度推送**: 文件处理进度是否需要 WebSocket 实时推送？

---

## 3. 轨迹处理模块 (Tracks)

**Base Path**: `/api/tracks`

> **v2.0 更新说明**：
> - 速度/航向从位置数据计算，不使用原始列
> - 时间窗口：1秒（基于数据分析）
> - 位置阈值：0.12度（约13.3km）
> - 支持中英文列名自动识别

### 3.1 处理轨迹数据

```http
POST /api/tracks/process
```

**请求头**:
```
Authorization: Bearer {access_token}
```

**请求体**:
```json
{
  "file_id": 1,
  "mode": "multi_source",
  "ransac_threshold": 0.5,
  "kalman_process_noise": 0.1,
  "kalman_measurement_noise": 1.0
}
```

**响应**:
```json
{
  "task_id": "task_123",
  "status": "completed",
  "message": "RANSAC处理完成，共处理 1000 个点",
  "total_points": 1000,
  "corrected_points": 950,
  "outliers_detected": 50
}
```

**说明**:
- **mode**: 处理模式
  - `multi_source`: 多源参考模式（RANSAC 算法）- 适用于多台雷达探测同一目标
  - `single_source`: 单源盲测模式（卡尔曼滤波）- 适用于单站数据平滑
- **ransac_threshold**: RANSAC 阈值（0-1），默认 0.5
- **kalman_process_noise**: 卡尔曼滤波过程噪声，默认 0.1
- **kalman_measurement_noise**: 卡尔曼滤波测量噪声，默认 1.0

**处理流程**：
1. 加载原始数据（自动识别中英文列名）
2. 预处理：按站号+批号分组，计算速度过滤噪音
3. 算法修正（RANSAC 或卡尔曼滤波）
4. 保存修正结果

---

### 3.2 查询原始轨迹数据

```http
GET /api/tracks/raw?file_id=1&track_id=TRK001&limit=1000
```

**请求头**:
```
Authorization: Bearer {access_token}
```

**查询参数**:
- `file_id` (可选): 文件 ID
- `track_id` (可选): 轨迹编号
- `start_time` (可选): 开始时间
- `end_time` (可选): 结束时间
- `limit`: 返回数量，默认 1000，最大 10000

**响应**:
```json
[
  {
    "id": 1,
    "track_id": "TRK001",
    "timestamp": "2024-01-01T10:00:00Z",
    "latitude": 39.9042,
    "longitude": 116.4074,
    "altitude": 10000,
    "radar_station_id": 1,
    "target_id": "TARGET_A",
    "raw_data": {}
  }
]
```

> **注意**：原始数据中的 `speed` 和 `heading` 列仅用于存储，不参与算法处理。实际速度/航向由算法从位置数据计算。

---

### 3.3 查询修正后轨迹数据

```http
GET /api/tracks/corrected?file_id=1&track_id=TRK001&limit=1000
```

**请求头**:
```
Authorization: Bearer {access_token}
```

**查询参数**: 同 3.2

**响应**:
```json
[
  {
    "id": 1,
    "raw_track_id": 100,
    "track_id": "TRK001",
    "timestamp": "2024-01-01T10:00:00Z",
    "latitude": 39.9045,
    "longitude": 116.4076,
    "altitude": 10050,
    "correction_method": "ransac",
    "confidence_score": 0.92,
    "is_outlier": 0,
    "correction_metadata": {
      "algorithm": "RANSAC",
      "parameters": {"residual_threshold": 0.5}
    }
  }
]
```

> **说明**：
> - `correction_method`: ransac / kalman / single / none
> - `confidence_score`: 修正置信度 (0-1)
> - `is_outlier`: 0=正常点, 1=离群点
> - 速度/航向需要从前端从位置数据计算，或调用分析接口获取

---

### 3.4 获取轨迹摘要

```http
GET /api/tracks/summary?track_id=TRK001
```

**请求头**:
```
Authorization: Bearer {access_token}
```

**响应**:
```json
{
  "track_id": "TRK001",
  "point_count": 100,
  "time_span": {
    "start": "2024-01-01T10:00:00Z",
    "end": "2024-01-01T11:00:00Z",
    "duration_seconds": 3600
  },
  "position": {
    "min_lat": 39.8,
    "max_lat": 40.0,
    "min_lng": 116.3,
    "max_lng": 116.5
  },
  "altitude": {
    "min": 8000,
    "max": 12000,
    "avg": 10000
  },
  "quality": {
    "avg_confidence": 0.92,
    "outlier_count": 5
  }
}
```

---

### 3.5 获取轨迹详情

```http
GET /api/tracks/{track_id}
```

**请求头**:
```
Authorization: Bearer {access_token}
```

**响应**:
```json
{
  "track_id": "TRK001",
  "file_id": 1,
  "point_count": 100,
  "start_time": "2024-01-01T10:00:00Z",
  "end_time": "2024-01-01T11:00:00Z",
  "duration_seconds": 3600,
  "raw_points": [...],
  "corrected_points": [...]
}
```

---

### 3.6 获取轨迹点数据

```http
GET /api/tracks/points?track_id=TRK001&limit=1000
```

**请求头**:
```
Authorization: Bearer {access_token}
```

---

### 3.7 查询轨迹处理任务状态

```http
GET /api/tracks/tasks/{task_id}
```

**请求头**:
```
Authorization: Bearer {access_token}
```

**响应**:
```json
{
  "task_id": "task_123",
  "status": "completed",
  "progress": 100.0,
  "message": "轨迹处理完成",
  "result": {
    "total_points": 1000,
    "corrected_points": 950,
    "outliers_detected": 50
  },
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:05:00Z"
}
```

---

### 📝 轨迹处理模块 - 前端反馈问题

1. **轨迹回放**: 需要什么格式的轨迹回放数据？
2. **3D 可视化**: 3D 地球上显示轨迹需要什么数据结构？
3. **多轨迹对比**: 是否需要同时显示多条轨迹进行对比？
4. **异常点标注**: 是否需要在地图上特别标注异常轨迹点？
5. **轨迹预测**: 是否需要轨迹预测/延伸功能？

---

## 4. 禁飞区管理模块 (Zones)

**Base Path**: `/api/zones`

### 4.1 创建禁飞区

```http
POST /api/zones/
```

**请求头**:
```
Authorization: Bearer {access_token}
```

**请求体**:
```json
{
  "zone_name": "首都机场禁飞区",
  "zone_type": "circle",
  "coordinates": "{\"type\": \"circle\", \"center\": {\"lat\": 39.9042, \"lng\": 116.4074}, \"radius\": 5000}",
  "min_altitude": 0,
  "max_altitude": 10000,
  "notification_email": "admin@example.com"
}
```

**说明**:
- **zone_type**: circle / polygon
- **coordinates** (JSON 字符串):
  - 圆形: `{"type": "circle", "center": {"lat": 0, "lng": 0}, "radius": 1000}`
  - 多边形: `{"type": "polygon", "vertices": [{"lat": 0, "lng": 0}, ...]}`

**响应**:
```json
{
  "id": 1,
  "zone_name": "首都机场禁飞区",
  "zone_type": "circle",
  "coordinates": "...",
  "min_altitude": 0,
  "max_altitude": 10000,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

### 4.2 获取禁飞区列表

```http
GET /api/zones/?skip=0&limit=20
```

**请求头**:
```
Authorization: Bearer {access_token}
```

---

### 4.3 获取禁飞区详情

```http
GET /api/zones/{zone_id}
```

**请求头**:
```
Authorization: Bearer {access_token}
```

---

### 4.4 更新禁飞区

```http
PUT /api/zones/{zone_id}
```

**请求头**:
```
Authorization: Bearer {access_token}
```

**请求体**:
```json
{
  "zone_name": "更新后的名称",
  "min_altitude": 0,
  "max_altitude": 15000,
  "notification_email": "new@example.com"
}
```

---

### 4.5 删除禁飞区

```http
DELETE /api/zones/{zone_id}
```

**请求头**:
```
Authorization: Bearer {access_token}
```

---

### 4.6 切换禁飞区激活状态

```http
PATCH /api/zones/{zone_id}/toggle
```

**请求头**:
```
Authorization: Bearer {access_token}
```

---

### 4.7 检测入侵

```http
POST /api/zones/detect-intrusions?track_id=TRK001
```

**请求头**:
```
Authorization: Bearer {access_token}
```

**查询参数**:
- `track_id`: 轨迹编号
- `start_time` (可选): 开始时间
- `end_time` (可选): 结束时间

**响应**:
```json
[
  {
    "id": 1,
    "zone_id": 1,
    "track_id": "TRK001",
    "timestamp": "2024-01-01T10:30:00Z",
    "latitude": 39.9042,
    "longitude": 116.4074,
    "altitude": 5000,
    "severity": "high",
    "duration_seconds": 120
  }
]
```

---

### 4.8 查询入侵记录

```http
GET /api/zones/intrusions/list?zone_id=1&limit=100
```

**请求头**:
```
Authorization: Bearer {access_token}
```

**查询参数**:
- `zone_id` (可选): 禁飞区 ID
- `track_id` (可选): 轨迹编号
- `start_time` (可选): 开始时间
- `end_time` (可选): 结束时间
- `limit`: 返回数量

**响应**:
```json
{
  "total": 50,
  "intrusions": [...]
}
```

---

### 📝 禁飞区管理模块 - 前端反馈问题

1. **地图绘制**: 需要什么样的地图组件来绘制禁飞区（圆形/多边形）？
2. **实时告警**: 入侵检测是否需要 WebSocket 实时推送？
3. **历史回放**: 是否需要入侵历史事件回放功能？
4. **批量导入**: 是否需要批量导入禁飞区坐标？
5. **3D 显示**: 禁飞区是否需要在 3D 地球上以立体方式显示？

---

## 5. AI 分析模块 (Analysis)

**Base Path**: `/api/analysis`

### 5.1 整体轨迹分析

```http
POST /api/analysis/trajectory
```

**请求头**:
```
Authorization: Bearer {access_token}
```

**请求体**:
```json
{
  "track_id": "TRK001",
  "start_time": "2024-01-01T10:00:00Z",
  "end_time": "2024-01-01T11:00:00Z",
  "analysis_type": "comprehensive",
  "include_predictions": true
}
```

**说明**:
- **analysis_type**: comprehensive / behavior / anomaly / pattern

**响应**:
```json
{
  "analysis_type": "comprehensive",
  "track_id": "TRK001",
  "analyzed_at": "2024-01-01T12:00:00Z",
  "summary": "轨迹分析完成",
  "features": [
    {
      "feature_name": "avg_speed",
      "feature_value": 245.5,
      "confidence": 1.0,
      "description": "平均速度（米/秒，从位置计算）"
    },
    {
      "feature_name": "max_speed",
      "feature_value": 280.0,
      "confidence": 1.0,
      "description": "最大速度（米/秒，从位置计算）"
    },
    {
      "feature_name": "avg_heading_change",
      "feature_value": 15.3,
      "confidence": 1.0,
      "description": "平均航向变化（度，从位置计算）"
    },
    {
      "feature_name": "outlier_ratio",
      "feature_value": 0.05,
      "confidence": 1.0,
      "description": "离群值比例"
    }
  ],
  "risk_level": "low",
  "recommendations": ["轨迹分析未发现明显异常"]
}
```

> **说明**：所有速度、航向特征均从位置数据计算，不使用原始列。速度单位为米/秒。

---

### 5.2 区间轨迹分析

```http
POST /api/analysis/segment
```

**请求头**:
```
Authorization: Bearer {access_token}
```

**请求体**:
```json
{
  "track_id": "TRK001",
  "start_time": "2024-01-01T10:00:00Z",
  "end_time": "2024-01-01T10:30:00Z",
  "analysis_type": "behavior"
}
```

**说明**:
- **analysis_type**: behavior / movement / characteristics

---

### 5.3 调用大语言模型分析

```http
POST /api/analysis/llm
```

**请求头**:
```
Authorization: Bearer {access_token}
```

**请求体**:
```json
{
  "prompt": "分析这条轨迹的飞行意图",
  "context_data": {...},
  "model": "deepseek",
  "max_tokens": 1000,
  "temperature": 0.7
}
```

**说明**:
- **model**: deepseek / ollama

**响应**:
```json
{
  "analysis_id": "ANL_001",
  "model": "deepseek",
  "result": "根据轨迹分析，该飞行器正在执行...",
  "tokens_used": 500,
  "generated_at": "2024-01-01T12:00:00Z"
}
```

---

### 5.4 生成综合分析报告

```http
GET /api/analysis/report/{track_id}?start_time=...&end_time=...
```

**请求头**:
```
Authorization: Bearer {access_token}
```

**响应**:
```json
{
  "track_id": "TRK001",
  "generated_at": "2024-01-01T12:00:00Z",
  "overall_assessment": "正常",
  "trajectory_analysis": {...},
  "behavior_analysis": {...},
  "anomaly_detection": {...},
  "risk_assessment": {...}
}
```

---

### 5.5 获取可提取特征列表

```http
GET /api/analysis/features/available
```

**请求头**:
```
Authorization: Bearer {access_token}
```

**响应**:
```json
{
  "position_features": ["latitude_range", "longitude_range", ...],
  "velocity_features": ["avg_speed", "max_speed", ...],
  "movement_features": ["avg_heading_change", ...],
  "temporal_features": ["duration_seconds", ...]
}
```

---

### 5.6 查询分析任务状态

```http
GET /api/analysis/tasks/{analysis_id}
```

**请求头**:
```
Authorization: Bearer {access_token}
```

---

### 📝 AI 分析模块 - 前端反馈问题

1. **分析可视化**: 分析结果需要什么样的图表展示？
2. **报告导出**: 是否需要 PDF/Word 报告导出功能？
3. **实时分析**: 分析过程是否需要实时进度展示？
4. **自定义特征**: 是否需要前端自定义选择要分析的特征？
5. **LLM 配置**: LLM 模型参数是否需要前端可配置？

---

## 6. 数据查询模块 (Query)

**Base Path**: `/api/query`

### 6.1 查询雷达站列表

```http
GET /api/query/radar-stations?status_filter=active
```

**请求头**:
```
Authorization: Bearer {access_token}
```

**查询参数**:
- `status_filter`: active / inactive / maintenance

**响应**:
```json
[
  {
    "id": 1,
    "station_code": "STATION_A",
    "station_name": "北京站",
    "latitude": 39.9042,
    "longitude": 116.4074,
    "altitude": 100,
    "status": "active"
  }
]
```

---

### 6.2 获取系统统计信息

```http
GET /api/query/statistics
```

**请求头**:
```
Authorization: Bearer {access_token}
```

**响应**:
```json
{
  "files": {"total": 100, "completed": 80, "processing": 5, "failed": 15},
  "tracks": {"raw_count": 10000, "corrected_count": 9500, "unique_tracks": 500},
  "radar_stations": {"total": 10, "active": 8},
  "zones": {"total": 20, "active": 15},
  "intrusions": {"total": 50, "high_severity": 10, "today": 2}
}
```

---

### 6.3 获取系统健康状态

```http
GET /api/query/health
```

**请求头**:
```
Authorization: Bearer {access_token}
```

**响应**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "components": {
    "database": {"status": "healthy"}
  }
}
```

---

### 📝 数据查询模块 - 前端反馈问题

1. **统计图表**: 统计数据需要什么样的图表展示？
2. **自定义时间范围**: 是否需要支持自定义时间范围统计？
3. **数据导出**: 是否需要统计数据导出功能？
4. **实时更新**: 统计数据是否需要定时刷新？

---

## 7. WebSocket 实时推送 (WebSocket)

**Base Path**: `/api/ws`

### 7.1 连接 WebSocket

```http
ws://localhost:8000/api/ws/{channel}
```

**连接请求头**:
```
Authorization: Bearer {access_token}
```

**频道列表**:
- `files:{file_id}`: 文件处理进度
- `tracks:{task_id}`: 轨迹处理任务状态
- `analysis:{analysis_id}`: 分析任务状态
- `intrusions`: 实时入侵告警
- `statistics`: 系统统计更新

### 7.2 文件处理进度推送

**连接 URL**:
```
ws://localhost:8000/api/ws/files/1
```

**推送消息**:
```json
{
  "type": "progress",
  "channel": "files:1",
  "timestamp": "2024-01-01T10:00:00Z",
  "data": {
    "file_id": 1,
    "status": "processing",
    "progress": 45.5,
    "stage": "预处理中",
    "processed_rows": 455,
    "total_rows": 1000,
    "outliers_filtered": 23,
    "message": "正在过滤噪音点..."
  }
}
```

**完成消息**:
```json
{
  "type": "completed",
  "channel": "files:1",
  "timestamp": "2024-01-01T10:01:00Z",
  "data": {
    "file_id": 1,
    "status": "completed",
    "progress": 100.0,
    "processed_rows": 1000,
    "outliers_filtered": 52,
    "tracks_detected": 45,
    "message": "处理完成"
  }
}
```

---

### 7.3 轨迹处理任务推送

**连接 URL**:
```
ws://localhost:8000/api/ws/tracks/task_123
```

**推送消息**:
```json
{
  "type": "status_update",
  "channel": "tracks:task_123",
  "timestamp": "2024-01-01T10:00:00Z",
  "data": {
    "task_id": "task_123",
    "status": "processing",
    "progress": 60.0,
    "stage": "算法修正中",
    "total_points": 1000,
    "processed_points": 600,
    "outliers_detected": 15
  }
}
```

---

### 7.4 实时入侵告警推送

**连接 URL**:
```
ws://localhost:8000/api/ws/intrusions
```

**推送消息**:
```json
{
  "type": "intrusion_detected",
  "channel": "intrusions",
  "timestamp": "2024-01-01T10:30:00Z",
  "data": {
    "intrusion_id": 123,
    "zone_name": "首都机场禁飞区",
    "track_id": "TRK001",
    "latitude": 39.9042,
    "longitude": 116.4074,
    "altitude": 5000,
    "severity": "high",
    "detected_at": "2024-01-01T10:30:00Z"
  }
}
```

---

### 7.5 系统统计更新推送

**连接 URL**:
```
ws://localhost:8000/api/ws/statistics
```

**推送消息**:
```json
{
  "type": "statistics_update",
  "channel": "statistics",
  "timestamp": "2024-01-01T10:00:00Z",
  "data": {
    "files": {"total": 100, "completed": 80, "processing": 5, "failed": 15},
    "tracks": {"raw_count": 10000, "corrected_count": 9500, "unique_tracks": 500},
    "intrusions": {"total": 50, "high_severity": 10, "today": 2}
  }
}
```

---

### 7.6 心跳机制

**服务端每30秒发送心跳**:
```json
{
  "type": "ping",
  "timestamp": "2024-01-01T10:00:00Z"
}
```

**客户端应响应**:
```json
{
  "type": "pong",
  "timestamp": "2024-01-01T10:00:00Z"
}
```

---

### 📝 WebSocket 前端使用示例

```javascript
// 连接文件处理进度频道
const ws = new WebSocket('ws://localhost:8000/api/ws/files/1', {
  headers: { 'Authorization': `Bearer ${token}` }
});

// 监听消息
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);

  switch (message.type) {
    case 'progress':
      updateProgressBar(message.data.progress);
      updateStatus(message.data.stage);
      break;
    case 'completed':
      showResults(message.data);
      break;
    case 'error':
      showError(message.data.message);
      break;
    case 'ping':
      // 响应心跳
      ws.send(JSON.stringify({ type: 'pong', timestamp: Date.now() }));
      break;
  }
};

// 监听连接事件
ws.onopen = () => console.log('WebSocket 已连接');
ws.onerror = (error) => console.error('WebSocket 错误:', error);
ws.onclose = () => console.log('WebSocket 已断开');
```

---

### 📝 WebSocket 模块 - 前端反馈问题

1. ✅ 文件处理进度：已支持
2. ✅ 轨迹处理状态：已支持
3. ✅ 实时入侵告警：已支持
4. ✅ 系统统计更新：已支持

---

## 8. 健康检查模块 (Health)

**Base Path**: `/api/health`

### 8.1 基础健康检查

```http
GET /api/health/
```

**响应**:
```json
{
  "status": "healthy",
  "service": "RFTIP API"
}
```

---

### 8.2 数据库连接检查

```http
GET /api/health/database
```

**响应**:
```json
{
  "status": "connected",
  "database": "MySQL"
}
```

---

### 📝 健康检查模块 - 前端反馈问题

1. **监控面板**: 是否需要完整的服务监控面板？
2. **告警通知**: 服务异常时是否需要邮件/短信告警？

---

## 📌 通用说明

### 认证方式

所有需要认证的接口都使用 Bearer Token:

```http
Authorization: Bearer {access_token}
```

Token 通过登录接口获取，有效期 30 分钟。

### 错误响应格式

```json
{
  "detail": "错误描述信息"
}
```

常见 HTTP 状态码:
- `200`: 成功
- `201`: 创建成功
- `204`: 成功（无返回内容）
- `400`: 请求参数错误
- `401`: 未认证
- `403`: 无权限
- `404`: 资源不存在
- `429`: 请求过于频繁
- `500`: 服务器错误

### 分页参数

列表接口通用分页参数:
- `skip`: 跳过条数，默认 0
- `limit`: 返回条数，通常有最大值限制

### 时间格式

所有时间使用 ISO 8601 格式: `2024-01-01T10:00:00Z`

---

## 🔄 待确认事项

### 前端需确认的问题汇总

| 模块 | 问题 | 优先级 |
|------|------|--------|
| 认证 | Token 刷新机制 | 高 |
| 认证 | 第三方登录 | 中 |
| 认证 | 手机验证码 | 中 |
| 认证 | 密码重置功能 | 中 |
| 文件 | 批量上传 | ✅ 已支持 |
| 文件 | 分享链接 | ✅ 已支持 |
| 文件 | 文件分类 | ✅ 已支持 (轨迹/雷达站) |
| 文件 | WebSocket 进度推送 | ✅ 已支持 |
| 轨迹 | 轨迹回放格式 | 高 |
| 轨迹 | 3D 可视化数据结构 | 高 |
| 轨迹 | 多轨迹对比 | 中 |
| 禁飞区 | 地图绘制组件 | 高 |
| 禁飞区 | 实时告警推送 | ✅ 已支持 |
| 禁飞区 | 3D 立体显示 | 中 |
| 分析 | 分析可视化图表 | 中 |
| 分析 | 报告导出 | 低 |
| 分析 | LLM 参数配置 | 低 |

---

## 📝 版本历史

### v2.0 (2026-02-19)
- **重大重构**：速度/航向从位置数据计算，不使用原始列
- **时间窗口调整**：1秒（基于数据分析）
- **位置阈值**：0.12度（约13.3km）
- **中文列名支持**：自动识别中英文列名
- **可扩展算法接口**：支持动态注册新算法

### v1.0 (2024-01-01)
- 初始版本

---

> 文档版本: v2.0
> 更新时间: 2026-02-19
