"""
MRRA 算法配置

使用 Pydantic 定义配置模型，确保类型安全和验证
"""
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator


class MrraCostWeights(BaseModel):
    """代价函数权重配置"""
    variance: float = Field(default=100.0, description="方差权重")
    azimuth_error_square: float = Field(default=0.15, description="方位角误差平方项权重（度^2）")
    range_error_square: float = Field(default=6e-7, description="距离误差平方项权重（米^2）")
    elevation_error_square: float = Field(default=0.1, description="俯仰角误差平方项权重（度^2）")


class MrraAlgorithmConfig(BaseModel):
    """
    MRRA 算法配置（基于梯度下降的迭代寻优算法）

    包含所有可配置的算法参数
    """

    # ========== 数据处理配置 ==========
    grid_resolution: float = Field(default=0.2, ge=0.01, le=1.0, description="网格分辨率（度）")
    time_window: int = Field(default=60, ge=10, le=600, description="时间窗口长度（秒）")
    time_window_ratio: float = Field(default=0.75, ge=0.1, le=1.0, description="时间窗口比例")
    match_distance_threshold: float = Field(default=0.12, ge=0.01, le=1.0, description="匹配距离阈值（度）")

    # ========== 航迹提取配置 ==========
    min_track_points: int = Field(default=10, ge=3, le=100, description="最小航迹点数")

    # ========== 优化参数 ==========
    optimization_steps: List[float] = Field(default=[0.1, 0.01], description="方位角优化步长序列（度）")
    range_optimization_steps: List[float] = Field(
        default=[1000, 800, 500, 200, 100, 50, 20],
        description="距离优化步长序列（米）"
    )
    max_match_groups: int = Field(default=15000, ge=1000, le=100000, description="最大匹配组数")

    # ========== 代价函数权重 ==========
    cost_weights: Optional[MrraCostWeights] = Field(default=None, description="代价函数权重")

    @model_validator(mode='before')
    @classmethod
    def validate_cost_weights(cls, values):
        """允许 cost_weights 为 null"""
        if isinstance(values, dict) and values.get('cost_weights') is None:
            values['cost_weights'] = None
        return values

    @field_validator('optimization_steps')
    @classmethod
    def validate_optimization_steps(cls, v: List[float]) -> List[float]:
        """验证优化步长序列"""
        if not v:
            return [0.1, 0.01]
        for i in range(len(v) - 1):
            if v[i] <= v[i + 1]:
                raise ValueError("优化步长应该是递减的")
        return v

    @field_validator('range_optimization_steps')
    @classmethod
    def validate_range_optimization_steps(cls, v: List[float]) -> List[float]:
        """验证距离优化步长序列"""
        if not v:
            return [1000, 800, 500, 200, 100, 50, 20]
        for i in range(len(v) - 1):
            if v[i] <= v[i + 1]:
                raise ValueError("距离优化步长应该是递减的")
        return v

    class Config:
        """Pydantic 配置"""
        use_enum_values = True
        from_attributes = True
        json_schema_extra = {
            "example": {
                "grid_resolution": 0.2,
                "time_window": 60,
                "match_distance_threshold": 0.12,
                "optimization_steps": [0.1, 0.01],
                "cost_weights": {
                    "variance": 100.0,
                    "azimuth_error_square": 0.15,
                    "range_error_square": 6e-7,
                    "elevation_error_square": 0.1,
                }
            }
        }
