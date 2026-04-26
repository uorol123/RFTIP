# 误差分析算法模块

本模块实现了可插拔的误差分析算法架构，支持动态添加新的算法而无需修改核心代码。

## 架构概述

```
error_analysis/
├── __init__.py              # 模块入口，自动注册所有算法
├── base.py                  # 算法基类，定义统一接口
├── registry.py              # 算法注册表，管理所有算法
├── factory.py               # 算法工厂，创建算法实例
├── README.md                # 本文件，新增算法指南
└── algorithms/              # 算法实现目录
    ├── __init__.py          # 自动导入并注册所有算法
    ├── gradient_descent/    # MRRA 算法（基于梯度下降的迭代寻优）
    │   ├── __init__.py
    │   ├── algorithm.py     # 算法实现
    │   ├── config.py        # Pydantic 配置模型
    │   └── metadata.py      # 前端UI元数据
    └── algorithm_template/  # 算法模板（新增算法时使用）
        └── ...
```

## 快速开始：新增一个算法

### 步骤 1: 创建算法目录

在 `algorithms/` 下创建新的算法目录：

```bash
cd backend/app/utils/error_analysis/algorithms
mkdir your_algorithm_name
cd your_algorithm_name
```

### 步骤 2: 创建算法文件

创建以下文件：

```bash
touch __init__.py algorithm.py config.py metadata.py
```

### 步骤 3: 实现配置模型

在 `config.py` 中使用 Pydantic 定义配置：

```python
"""
算法配置模型

使用 Pydantic BaseModel 确保配置的类型安全和验证
"""
from typing import List
from pydantic import BaseModel, Field


class YourAlgorithmCostWeights(BaseModel):
    """代价函数权重"""
    weight1: float = Field(default=1.0, ge=0, description="权重1说明")
    weight2: float = Field(default=0.5, ge=0, description="权重2说明")


class YourAlgorithmConfig(BaseModel):
    """
    算法配置

    所有参数都应该有：
    - 类型注解
    - 默认值
    - 验证规则（ge, le等）
    - 描述信息
    """

    # 数据处理参数
    param1: float = Field(
        default=1.0,
        ge=0.1,
        le=10.0,
        description="参数1说明"
    )

    # 优化参数
    param2: int = Field(
        default=100,
        ge=10,
        le=1000,
        description="参数2说明"
    )

    # 嵌套对象
    cost_weights: YourAlgorithmCostWeights = Field(
        default_factory=YourAlgorithmCostWeights
    )

    # 列表类型
    steps: List[float] = Field(
        default=[0.1, 0.01],
        description="优化步长序列"
    )
```

### 步骤 4: 实现算法类

在 `algorithm.py` 中继承 `BaseErrorAnalysisAlgorithm`：

```python
"""
算法实现
"""
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.utils.error_analysis.base import (
    BaseErrorAnalysisAlgorithm,
    AnalysisResult,
    ProgressCallback,
    register_algorithm,
)
from app.utils.error_analysis.algorithms.your_algorithm.config import YourAlgorithmConfig
from sqlalchemy.orm import Session
from core.logging import get_logger

logger = get_logger(__name__)


@register_algorithm  # 装饰器自动注册算法
class YourAlgorithm(BaseErrorAnalysisAlgorithm):
    """
    算法显示名称

    简要描述算法的原理和用途
    """

    # ========== 算法元信息（必须覆盖） ==========
    ALGORITHM_NAME = "your_algorithm"           # 唯一标识符
    ALGORITHM_VERSION = "1.0.0"                # 版本号
    ALGORITHM_DISPLAY_NAME = "你的算法名称"     # 显示名称
    ALGORITHM_DESCRIPTION = "算法详细描述..."  # 描述

    # 配置类（用于工厂创建）
    ConfigClass = YourAlgorithmConfig

    def __init__(self, config: YourAlgorithmConfig):
        super().__init__(config)
        logger.info(f"初始化 {self.ALGORITHM_NAME} 算法")

    def _validate_config(self):
        """验证配置参数（Pydantic自动验证，可添加额外逻辑）"""
        if not isinstance(self.config, YourAlgorithmConfig):
            raise ValueError("配置类型错误")

    def analyze(
        self,
        radar_station_ids: List[int],
        track_ids: List[str],
        db_session: Session,
        progress_callback: Optional[ProgressCallback] = None
    ) -> AnalysisResult:
        """
        执行误差分析

        这是算法的核心方法，实现完整的分析流程：
        1. 数据加载和预处理
        2. 航迹匹配/计算
        3. 误差估计
        4. 结果整理
        """
        start_time = datetime.now()
        task_id = f"{self.ALGORITHM_NAME}_{int(start_time.timestamp())}"

        result = AnalysisResult(
            task_id=task_id,
            algorithm_name=self.ALGORITHM_NAME,
            algorithm_version=self.ALGORITHM_VERSION,
            status="running",
            progress=0.0,
            started_at=start_time,
        )

        try:
            # 步骤1: 数据加载 (10%)
            if progress_callback:
                progress_callback.on_progress(0.1, "加载数据")

            # TODO: 实现数据加载逻辑
            data = self._load_data(db_session, radar_station_ids, track_ids)

            # 步骤2: 数据处理 (30%)
            if progress_callback:
                progress_callback.on_progress(0.3, "处理数据")

            # TODO: 实现数据处理逻辑
            processed = self._process_data(data)

            # 步骤3: 误差计算 (70%)
            if progress_callback:
                progress_callback.on_progress(0.7, "计算误差")

            # TODO: 实现误差计算逻辑
            errors = self._calculate_errors(processed)

            # 完成 (100%)
            result.status = "completed"
            result.progress = 1.0
            result.errors = errors
            result.completed_at = datetime.now()
            result.processing_time_seconds = (
                result.completed_at - start_time
            ).total_seconds()

            logger.info(f"[{task_id}] 分析完成")
            return result

        except Exception as e:
            logger.error(f"[{task_id}] 分析失败: {str(e)}")
            result.status = "failed"
            result.error_message = str(e)
            result.completed_at = datetime.now()
            if progress_callback:
                progress_callback.on_error(str(e))
            return result

    def _load_data(self, db, station_ids, track_ids):
        """加载数据（私有方法示例）"""
        # TODO: 实现数据加载
        pass

    def _process_data(self, data):
        """处理数据（私有方法示例）"""
        # TODO: 实现数据处理
        pass

    def _calculate_errors(self, processed):
        """计算误差（私有方法示例）"""
        # TODO: 实现误差计算
        # 返回格式: {station_id: {azimuth: float, range: float, elevation: float}}
        return {}

    @staticmethod
    def get_default_config() -> YourAlgorithmConfig:
        """获取默认配置"""
        return YourAlgorithmConfig()

    @staticmethod
    def get_config_class():
        """获取配置类（用于工厂）"""
        return YourAlgorithmConfig

    @staticmethod
    def get_config_schema() -> Dict[str, Any]:
        """
        获取配置的 JSON Schema

        用于前端动态生成配置表单
        """
        return YourAlgorithmConfig.model_json_schema()

    @staticmethod
    def get_config_preset_profiles() -> Dict[str, YourAlgorithmConfig]:
        """
        获取预设配置方案（可选）

        返回预设名称 -> 配置对象的字典
        """
        return {
            "standard": YourAlgorithmConfig(),
            "high_precision": YourAlgorithmConfig(
                param1=0.5,  # 更精细的参数
            ),
            "fast": YourAlgorithmConfig(
                param1=2.0,  # 更粗糙但快速的参数
            ),
        }

    @staticmethod
    def supports_elevation() -> bool:
        """
        是否支持俯仰角误差计算
        """
        return True
```

### 步骤 5: 定义元数据

在 `metadata.py` 中定义前端UI需要的元数据：

```python
"""
算法元数据

定义前端UI渲染所需的所有信息
"""
from app.utils.error_analysis.base import AlgorithmMetadata, DataTypeRequirement


def get_metadata() -> AlgorithmMetadata:
    """
    获取算法元数据

    元数据包含：
    - 算法基本信息
    - 支持的数据类型
    - 前端UI配置
    - 性能预估信息
    """
    return AlgorithmMetadata(
        # 基本信息
        name="your_algorithm",
        display_name="你的算法名称",
        description="算法的详细描述，说明原理、适用场景等",
        version="1.0.0",

        # 能力声明
        supports_elevation=True,  # 是否支持俯仰角误差
        supported_data_types=[
            DataTypeRequirement.RADAR_STATIONS,    # 需要雷达站数据
            DataTypeRequirement.TRACK_POINTS,       # 需要航迹点数据
            # DataTypeRequirement.INTERPOLATED_POINTS,  # 需要插值点数据
            # DataTypeRequirement.REFERENCE_TRAJECTORY,  # 需要参考轨迹
        ],

        # UI配置
        category="general",  # general | advanced | experimental
        requires_min_stations=2,  # 最少需要几个雷达站
        requires_min_tracks=1,    # 最少需要几条轨迹

        # 性能预估
        estimated_time_per_1000_points=1.0,  # 每1000个点约1秒
        max_recommended_points=1000000,        # 最大推荐点数
    )


def get_ui_config_schema() -> dict:
    """
    获取前端UI配置Schema

    定义：
    - 数据选择器如何显示
    - 参数如何分组
    - 预设配置有哪些
    """
    return {
        # 数据选择器配置
        "data_selector": {
            "type": "standard",  # standard | custom
            "allow_multi_station": True,  # 是否允许多选雷达站
            "allow_multi_track": True,      # 是否允许多选轨迹
            "min_stations": 2,
            "min_tracks": 1,
        },

        # 参数分组（用于UI组织）
        "parameter_groups": [
            {
                "name": "basic",
                "label": "基础参数",
                "description": "影响分析精度的基本参数",
                "parameters": [
                    "param1",
                    "param2",
                ]
            },
            {
                "name": "advanced",
                "label": "高级参数",
                "description": "优化和性能相关参数",
                "parameters": [
                    "steps",
                    "cost_weights.weight1",
                    "cost_weights.weight2",
                ]
            }
        ],

        # 预设配置
        "presets": [
            {
                "name": "standard",
                "label": "标准配置",
                "description": "平衡精度与速度",
            },
            {
                "name": "high_precision",
                "label": "高精度",
                "description": "更精细的分析",
            },
            {
                "name": "fast",
                "label": "快速分析",
                "description": "速度优先",
            },
        ]
    }
```

### 步骤 6: 创建 `__init__.py`

```python
"""
你的算法模块

导出算法类和元数据
"""
from app.utils.error_analysis.algorithms.your_algorithm.algorithm import YourAlgorithm
from app.utils.error_analysis.algorithms.your_algorithm.metadata import get_metadata, get_ui_config_schema

__all__ = [
    "YourAlgorithm",
    "get_metadata",
    "get_ui_config_schema",
]
```

### 步骤 7: 注册算法

在 `algorithms/__init__.py` 中添加导入：

```python
# 你的算法
from app.utils.error_analysis.algorithms.your_algorithm import YourAlgorithm

# 注册算法（使用装饰器自动注册，但需要导入才会生效）
# 如果类上已经使用了 @register_algorithm 装饰器，导入即可自动注册
```

### 步骤 8: 测试算法

创建测试文件 `tests/test_your_algorithm.py`：

```python
import pytest
from app.utils.error_analysis.factory import AlgorithmFactory
from app.utils.error_analysis.algorithms.your_algorithm.config import YourAlgorithmConfig


def test_algorithm_creation():
    """测试算法创建"""
    config = YourAlgorithmConfig()
    algorithm = AlgorithmFactory.create_algorithm("your_algorithm", config)
    assert algorithm is not None
    assert algorithm.ALGORITHM_NAME == "your_algorithm"


def test_config_validation():
    """测试配置验证"""
    # 有效配置
    config = YourAlgorithmConfig(param1=1.0)
    assert config.param1 == 1.0

    # 无效配置应该抛出异常
    with pytest.raises(ValueError):
        YourAlgorithmConfig(param1=-1)  # ge=0 应该失败


def test_analyze():
    """测试分析流程"""
    # TODO: 添加完整的分析测试
    pass
```

## 已实现的算法

| 算法ID | 目录 | 显示名称 | 描述 | 状态 |
|--------|------|----------|------|------|
| `gradient_descent` | `gradient_descent/` | 基于梯度下降的迭代寻优算法 | 通过航迹匹配和梯度下降优化计算雷达系统误差 | ✅ 已实现 |

## API 端点

后端提供以下 API 端点供前端调用：

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/algorithms/list` | GET | 获取所有可用算法列表 |
| `/api/v1/algorithms/{name}` | GET | 获取算法详细信息 |
| `/api/v1/algorithms/{name}/schema` | GET | 获取配置 JSON Schema |
| `/api/v1/algorithms/{name}/metadata` | GET | 获取算法元数据和 UI 配置 |
| `/api/v1/algorithms/{name}/presets` | GET | 获取预设配置方案 |
| `/api/v1/algorithms/{name}/validate` | POST | 验证配置参数 |

## 算法开发最佳实践

### 1. 配置验证

使用 Pydantic 的验证功能确保配置正确：

```python
class MyConfig(BaseModel):
    value: float = Field(gt=0, le=100)  # 大于0，小于等于100
```

### 2. 进度报告

使用 `ProgressCallback` 报告分析进度：

```python
if progress_callback:
    progress_callback.on_progress(0.5, "处理中")
    progress_callback.on_step_complete("数据处理", 10.5)
```

### 3. 错误处理

捕获并妥善处理异常：

```python
try:
    result = self._calculate_errors(data)
except Exception as e:
    logger.error(f"计算失败: {e}")
    result.error_message = str(e)
    result.status = "failed"
```

### 4. 日志记录

使用统一的 logger：

```python
from core.logging import get_logger
logger = get_logger(__name__)
logger.info("信息")
logger.warning("警告")
logger.error("错误")
```

### 5. 数据库操作

使用传入的 `db_session`，不要创建新的会话：

```python
def analyze(self, ..., db_session: Session, ...):
    # 使用 db_session 查询数据
    stations = db_session.query(RadarStation).all()
    # 不要: Session() ...
```

## 常见问题

### Q: 如何调试算法？

A: 可以直接运行算法：

```python
from app.utils.error_analysis.factory import AlgorithmFactory

algorithm = AlgorithmFactory.create_algorithm("your_algorithm")
result = algorithm.analyze(station_ids, track_ids, db_session)
print(result.errors)
```

### Q: 算法没有出现在列表中？

A: 检查：
1. 是否在 `algorithms/__init__.py` 中导入了算法
2. 是否使用了 `@register_algorithm` 装饰器
3. `ALGORITHM_NAME` 是否唯一

### Q: 如何复用现有代码？

A: 可以参考 `gradient_descent/` 的实现，或者继承 `ErrorCalculator` 等工具类。

### Q: 前端如何显示我的算法？

A: 只要正确实现了元数据和配置 Schema，前端会自动识别并显示算法。

## 相关文档

- [算法基类文档](./base.py)
- [注册表文档](./registry.py)
- [工厂文档](./factory.py)
- [MRRA 算法实现](./gradient_descent/)
- [前端组件文档](../../../../frontend/src/components/errorAnalysis/)
