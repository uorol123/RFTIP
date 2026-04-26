# 误差分析多算法架构使用指南

## 概述

RFTIP 误差分析模块现已支持多算法架构。本文档说明如何使用和扩展该架构。

## 当前支持的算法

### 1. 梯度下降算法 (gradient_descent)

**算法名称**: `gradient_descent`
**显示名称**: 基于梯度下降的迭代寻优算法
**版本**: 1.0.0
**描述**: 通过航迹匹配和梯度下降优化，计算雷达系统的方位角、距离和俯仰角误差

**特性**:
- 支持俯仰角误差计算
- 多种预设配置
- 可自定义参数

## API 使用

### 创建分析任务

```python
from app.schemas.error_analysis import ErrorAnalysisRequest, ErrorAnalysisConfig

# 创建请求
request = ErrorAnalysisRequest(
    radar_station_ids=[1, 2, 3],
    track_ids=["T001", "T002"],
    algorithm="gradient_descent",  # 指定算法
    config=ErrorAnalysisConfig(
        grid_resolution=0.2,
        time_window=60,
        match_distance_threshold=0.12,
    )
)

# 调用服务
service = ErrorAnalysisService(db)
response = service.create_analysis_task(request, user_id=1)
```

### 查询可用算法

```bash
GET /api/error-analysis/algorithms
```

响应示例：

```json
{
  "algorithms": [
    {
      "name": "gradient_descent",
      "version": "1.0.0",
      "display_name": "基于梯度下降的迭代寻优算法",
      "description": "通过航迹匹配和梯度下降优化计算雷达误差",
      "supports_elevation": true
    }
  ]
}
```

### 获取算法配置 Schema

```bash
GET /api/error-analysis/algorithms/{algorithm_name}/config-schema
```

### 获取算法预设配置

```bash
GET /api/error-analysis/algorithms/{algorithm_name}/presets
```

## 前端使用

### 基本用法

```vue
<template>
  <div>
    <AlgorithmSelector
      @update:algorithm="handleAlgorithmChange"
      @update:config="handleConfigChange"
    />

    <AlgorithmConfigContainer
      :disabled="isTaskRunning"
      @update:config="handleConfigUpdate"
    />
  </div>
</template>

<script setup>
import { AlgorithmSelector, AlgorithmConfigContainer } from '@/components/errorAnalysis'

function handleAlgorithmChange(algorithmName) {
  console.log('选择的算法:', algorithmName)
}

function handleConfigUpdate(config) {
  console.log('更新的配置:', config)
}
</script>
```

### 使用特定算法配置组件

```vue
<template>
  <GradientDescentConfig
    :algorithm-info="algorithmInfo"
    :config-schema="configSchema"
    v-model="localConfig"
    :presets="presets"
    @update:model-value="handleUpdate"
  />
</template>

<script setup>
import { GradientDescentConfig } from '@/components/errorAnalysis/algorithms'
</script>
```

## 添加新算法

### 后端实现

1. **创建算法类**:

```python
from app.utils.error_analysis.base import BaseErrorAnalysisAlgorithm, register_algorithm

class MyCustomAlgorithm(BaseErrorAnalysisAlgorithm):
    ALGORITHM_NAME = "my_custom_algorithm"
    ALGORITHM_VERSION = "1.0.0"
    ALGORITHM_DISPLAY_NAME = "我的自定义算法"
    ALGORITHM_DESCRIPTION = "算法描述"

    def _validate_config(self):
        # 验证配置
        pass

    def analyze(self, radar_station_ids, track_ids, db_session, progress_callback):
        # 实现分析逻辑
        pass

    def get_default_config(self):
        # 返回默认配置
        pass

    def get_config_schema(self):
        # 返回 JSON Schema
        pass

    def get_config_preset_profiles(self):
        # 返回预设配置
        pass

# 注册算法
register_algorithm(MyCustomAlgorithm)
```

2. **添加配置类**（可选）:

```python
from pydantic import BaseModel, Field

class MyCustomAlgorithmConfig(BaseModel):
    parameter1: float = Field(default=1.0, ge=0.1, le=10.0)
    parameter2: int = Field(default=100, ge=10, le=1000)
```

### 前端实现

1. **创建配置组件**:

```vue
<!-- MyCustomAlgorithmConfig.vue -->
<template>
  <AlgorithmConfigBase
    :title="algorithmInfo.display_name"
    :description="algorithmInfo.description"
    :config-schema="configSchema"
    v-model="localConfig"
  >
    <template #content>
      <!-- 自定义配置界面 -->
    </template>
  </AlgorithmConfigBase>
</template>

<script setup>
import AlgorithmConfigBase from '../AlgorithmConfigBase.vue'

// 组件实现
</script>
```

2. **注册组件映射**:

在 `AlgorithmConfigContainer.vue` 中添加：

```typescript
const ALGORITHM_CONFIG_COMPONENTS: Record<string, () => Promise<any>> = {
  gradient_descent: () => import('./gradient_descent/GradientDescentConfig.vue'),
  my_custom_algorithm: () => import('./my_custom_algorithm/MyCustomAlgorithmConfig.vue'),
}
```

## 预设配置

### 梯度下降算法预设

| 名称 | 说明 | 适用场景 |
|------|------|----------|
| standard | 标准配置 | 平衡精度与速度 |
| high_precision | 高精度配置 | 需要精确误差分析 |
| fast | 快速分析 | 大数据量初步筛选 |
| coarse | 粗粒度配置 | 低分辨率或大范围分析 |

### 自定义预设

在后端算法类中定义：

```python
def get_config_preset_profiles(self):
    return {
        "my_preset": MyAlgorithmConfig(
            parameter1=2.0,
            parameter2=200,
        )
    }
```

## 配置参数说明

### 梯度下降算法参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| grid_resolution | number | 0.2 | 网格分辨率（度） |
| time_window | number | 60 | 时间窗口（秒） |
| match_distance_threshold | number | 0.12 | 匹配距离阈值（度） |
| min_track_points | number | 10 | 最小航迹点数 |
| optimization_steps | number[] | [0.1, 0.01] | 方位角优化步长序列 |
| range_optimization_steps | number[] | [1000, 800, 500, 200, 100, 50, 20] | 距离优化步长序列（米） |
| max_match_groups | number | 15000 | 最大匹配组数 |
| cost_weights.variance | number | 100.0 | 方差权重 |
| cost_weights.azimuth_error_square | number | 0.15 | 方位角误差平方项权重 |
| cost_weights.range_error_square | number | 6e-7 | 距离误差平方项权重 |
| cost_weights.elevation_error_square | number | 0.1 | 俯仰角误差平方项权重 |

## 最佳实践

### 1. 算法选择

- **标准场景**: 使用 `gradient_descent` 算法的 `standard` 预设
- **高精度需求**: 使用 `high_precision` 预设
- **大数据量**: 使用 `fast` 预设进行初步筛选
- **资源受限**: 使用 `coarse` 预设

### 2. 参数调优

1. 从预设配置开始
2. 根据结果调整关键参数
3. 小幅度调整，逐步优化
4. 记录有效参数组合

### 3. 性能优化

- 合理设置 `max_match_groups` 避免内存溢出
- 大数据量使用较大 `grid_resolution`
- 高精度需求减小 `match_distance_threshold`

### 4. 错误处理

- 监控任务状态
- 处理失败任务的错误信息
- 合理设置超时时间

## 故障排除

### 常见问题

1. **任务执行失败**
   - 检查算法名称是否正确
   - 验证配置参数是否有效
   - 查看错误日志

2. **结果不准确**
   - 尝试不同的预设配置
   - 调整关键参数
   - 检查输入数据质量

3. **性能问题**
   - 减小 `max_match_groups`
   - 增大 `grid_resolution`
   - 使用 `fast` 预设

## 更新日志

### v1.0.0 (2024-03-22)
- 初始版本
- 支持梯度下降算法
- 实现多算法架构
- 添加预设配置
- 完善测试覆盖
