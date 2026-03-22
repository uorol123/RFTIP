# MRRA 误差分析 API 使用文档

## 概述

MRRA (Multi-source Radar Registration Analysis) 误差分析功能用于计算多雷达系统的方位角、距离和俯仰角误差。

## 前置条件

1. 已上传航迹数据文件
2. 已配置雷达站位置信息
3. 数据已预处理并存储在数据库中

## API 端点

### 1. 创建分析任务

```http
POST /api/error-analysis/analyze
```

**请求体:**

```json
{
  "file_id": 1,
  "config": {
    "grid_resolution": 0.2,
    "time_window": 60,
    "match_distance_threshold": 0.12,
    "min_track_points": 10,
    "optimization_steps": [0.1, 0.01],
    "range_optimization_steps": [1000, 800, 500, 200, 100, 50, 20],
    "cost_weights": {
      "variance": 100.0,
      "azimuth": 0.15,
      "range": 6e-7,
      "elevation": 0.1
    },
    "max_match_groups": 15000
  }
}
```

**响应:**

```json
{
  "id": 1,
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "file_id": 1,
  "user_id": 1,
  "status": "pending",
  "progress": 0,
  "error_message": null,
  "created_at": "2025-03-22T10:00:00Z",
  "started_at": null,
  "completed_at": null
}
```

**状态说明:**

- `pending`: 等待执行
- `extracting`: 提取关键航迹
- `interpolating`: 航迹插值
- `matching`: 航迹匹配
- `calculating`: 计算误差
- `completed`: 完成
- `failed`: 失败

### 2. 获取默认配置

```http
GET /api/error-analysis/config
```

**响应:**

```json
{
  "grid_resolution": 0.2,
  "time_window": 60,
  "match_distance_threshold": 0.12,
  "min_track_points": 10,
  "optimization_steps": [0.1, 0.01],
  "range_optimization_steps": [1000, 800, 500, 200, 100, 50, 20],
  "cost_weights": {
    "variance": 100.0,
    "azimuth": 0.15,
    "range": 6e-7,
    "elevation": 0.1
  },
  "max_match_groups": 15000
}
```

### 3. 获取任务列表

```http
GET /api/error-analysis/tasks?page=1&limit=20
```

**响应:**

```json
{
  "tasks": [
    {
      "id": 1,
      "task_id": "550e8400-e29b-41d4-a716-446655440000",
      "file_id": 1,
      "user_id": 1,
      "status": "completed",
      "progress": 100,
      "error_message": null,
      "created_at": "2025-03-22T10:00:00Z",
      "started_at": "2025-03-22T10:00:05Z",
      "completed_at": "2025-03-22T10:05:30Z"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 20
}
```

### 4. 获取任务详情

```http
GET /api/error-analysis/tasks/{task_id}
```

**响应:** 同创建任务响应

### 5. 获取分析结果

```http
GET /api/error-analysis/tasks/{task_id}/results
```

**响应:**

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "summary": {
    "total_stations": 5,
    "total_matches": 12500,
    "processing_time": 325.5,
    "segments_extracted": 150
  },
  "errors": [
    {
      "id": 1,
      "station_id": 1001,
      "azimuth_error": 0.123,
      "range_error": 45.6,
      "elevation_error": 0.045,
      "match_count": 2500,
      "confidence": 0.95,
      "iterations": 150,
      "final_cost": 12.34
    }
  ],
  "match_statistics": {
    "total_groups": 12500,
    "group_size_avg": 2.5,
    "group_size_std": 0.5,
    "distance_avg": 0.023,
    "distance_std": 0.012,
    "min_group_size": 2,
    "max_group_size": 5
  },
  "config": {
    "grid_resolution": 0.2,
    "time_window": 60,
    ...
  }
}
```

### 6. 获取航迹段列表

```http
GET /api/error-analysis/tasks/{task_id}/segments?limit=100
```

**响应:**

```json
[
  {
    "id": 1,
    "segment_id": 1,
    "station_id": 1001,
    "track_id": "T001",
    "start_time": "2025-03-22T08:00:00Z",
    "end_time": "2025-03-22T08:05:00Z",
    "point_count": 15,
    "start_point_index": 2,
    "end_point_index": 16
  }
]
```

### 7. 获取匹配组列表

```http
GET /api/error-analysis/tasks/{task_id}/matches?limit=100
```

**响应:**

```json
[
  {
    "id": 1,
    "group_id": 1,
    "match_time": "2025-03-22T08:00:00Z",
    "match_points": [
      {
        "station_id": 1001,
        "point_id": 123,
        "longitude": 116.0,
        "latitude": 39.0,
        "altitude": 5000.0
      },
      {
        "station_id": 1002,
        "point_id": 456,
        "longitude": 116.0001,
        "latitude": 39.0001,
        "altitude": 5000.5
      }
    ],
    "point_count": 2,
    "avg_distance": 0.015,
    "max_distance": 0.020,
    "variance": 0.0001
  }
]
```

### 8. 获取图表数据

```http
GET /api/error-analysis/tasks/{task_id}/chart
```

**响应:**

```json
{
  "stations": ["站1001", "站1002", "站1003"],
  "azimuth_errors": [0.123, 0.098, 0.156],
  "range_errors": [45.6, 52.3, 38.9],
  "elevation_errors": [0.045, 0.038, 0.052],
  "confidences": [0.95, 0.92, 0.89],
  "match_counts": [2500, 2300, 2100],
  "group_size_distribution": {
    "2": 8000,
    "3": 3500,
    "4": 800,
    "5": 200
  }
}
```

## 配置参数说明

### 基础参数

| 参数 | 类型 | 默认值 | 范围 | 说明 |
|------|------|--------|------|------|
| grid_resolution | float | 0.2 | 0.01-1.0 | 空间网格分辨率（度） |
| time_window | int | 60 | 10-600 | 时间窗口长度（秒） |
| match_distance_threshold | float | 0.12 | 0.01-1.0 | 匹配距离阈值（度） |
| min_track_points | int | 10 | 3-100 | 最小航迹点数 |

### 优化参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| optimization_steps | array | [0.1, 0.01] | 方位角/俯仰角优化步长序列（度） |
| range_optimization_steps | array | [1000, 800, 500, 200, 100, 50, 20] | 距离优化步长序列（米） |

### 代价函数权重

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| cost_weights.variance | float | 100.0 | 匹配点聚集度方差权重 |
| cost_weights.azimuth | float | 0.15 | 方位角误差平方项权重 |
| cost_weights.range | float | 6e-7 | 距离误差平方项权重 |
| cost_weights.elevation | float | 0.1 | 俯仰角误差平方项权重 |

### 其他参数

| 参数 | 类型 | 默认值 | 范围 | 说明 |
|------|------|--------|------|------|
| max_match_groups | int | 15000 | 1000-100000 | 最大匹配组数（用于误差计算） |

## 使用示例

### Python 示例

```python
import requests
import time

# 基础URL
BASE_URL = "http://localhost:8000/api"
TOKEN = "your_access_token"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# 1. 创建分析任务
response = requests.post(
    f"{BASE_URL}/error-analysis/analyze",
    json={
        "file_id": 1,
        "config": {
            "grid_resolution": 0.2,
            "time_window": 60
        }
    },
    headers=headers
)

task = response.json()
task_id = task["task_id"]
print(f"创建任务: {task_id}")

# 2. 等待任务完成
while True:
    response = requests.get(
        f"{BASE_URL}/error-analysis/tasks/{task_id}",
        headers=headers
    )
    task_status = response.json()

    print(f"任务状态: {task_status['status']}, 进度: {task_status['progress']}%")

    if task_status['status'] in ['completed', 'failed']:
        break

    time.sleep(5)

# 3. 获取结果
if task_status['status'] == 'completed':
    response = requests.get(
        f"{BASE_URL}/error-analysis/tasks/{task_id}/results",
        headers=headers
    )
    results = response.json()

    print("分析结果:")
    for error in results['errors']:
        print(f"  站{error['station_id']}: "
              f"方位角={error['azimuth_error']:.3f}°, "
              f"距离={error['range_error']:.1f}m, "
              f"俯仰角={error['elevation_error']:.3f}°")
```

### cURL 示例

```bash
# 创建分析任务
curl -X POST "http://localhost:8000/api/error-analysis/analyze" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": 1,
    "config": {
      "grid_resolution": 0.2,
      "time_window": 60
    }
  }'

# 获取任务状态
curl -X GET "http://localhost:8000/api/error-analysis/tasks/TASK_ID" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 获取分析结果
curl -X GET "http://localhost:8000/api/error-analysis/tasks/TASK_ID/results" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 错误处理

API 使用标准 HTTP 状态码：

- `200 OK`: 请求成功
- `400 Bad Request`: 请求参数错误
- `401 Unauthorized`: 未授权
- `404 Not Found`: 资源不存在
- `500 Internal Server Error`: 服务器错误

错误响应格式：

```json
{
  "detail": "错误消息"
}
```

## 注意事项

1. 分析任务在后台执行，需要轮询任务状态获取结果
2. 大数据量分析可能需要较长时间（数分钟到数十分钟）
3. 建议根据实际数据调整配置参数以获得最佳结果
4. 确保数据库有足够的存储空间存储插值点和匹配结果
