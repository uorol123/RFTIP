"""
RANSAC 算法配置模型
"""
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator


class RansacCostWeights(BaseModel):
    """代价函数权重配置"""
    variance: float = Field(default=100.0, description="方差权重")
    azimuth_error_square: float = Field(default=0.15, description="方位角误差平方项权重（度^2）")
    range_error_square: float = Field(default=6e-7, description="距离误差平方项权重（米^2）")
    elevation_error_square: float = Field(default=0.1, description="俯仰角误差平方项权重（度^2）")


class RansacAlgorithmConfig(BaseModel):
    """
    RANSAC 算法配置

    用于多源参考模式，通过随机抽样一致性剔除故障/低精度雷达站
    """

    # ========== 数据处理配置 ==========
    grid_resolution: float = Field(default=0.2, ge=0.01, le=1.0, description="网格分辨率（度）")
    time_window: int = Field(default=60, ge=10, le=600, description="时间窗口长度（秒）")
    time_window_ratio: float = Field(default=0.75, ge=0.1, le=1.0, description="时间窗口比例")
    match_distance_threshold: float = Field(default=0.12, ge=0.01, le=1.0, description="匹配距离阈值（度）")

    # ========== 航迹提取配置 ==========
    min_track_points: int = Field(default=10, ge=3, le=100, description="最小航迹点数")

    # ========== RANSAC 参数 ==========
    residual_threshold: float = Field(
        default=0.5, ge=0.01, le=5.0,
        description="RANSAC 残差阈值（度），小于此值的观测点被视为内点"
    )
    min_samples: int = Field(
        default=2, ge=2, le=10,
        description="RANSAC 最小样本数，即认为一组数据有效所需的最少数据点数"
    )
    max_iterations: int = Field(
        default=200, ge=10, le=1000,
        description="RANSAC 最大迭代次数"
    )
    outlier_ratio_threshold: float = Field(
        default=0.5, ge=0.1, le=0.9,
        description="离群率阈值，某雷达站被判定为故障的离群比例"
    )

    # ========== 优化参数 ==========
    optimization_steps: List[float] = Field(
        default=[0.1, 0.01],
        description="方位角优化步长序列（度）"
    )
    range_optimization_steps: List[float] = Field(
        default=[1000, 800, 500, 200, 100, 50, 20],
        description="距离优化步长序列（米）"
    )
    max_match_groups: int = Field(default=15000, ge=1000, le=100000, description="最大匹配组数")

    # ========== 代价函数权重 ==========
    cost_weights: Optional[RansacCostWeights] = Field(default=None, description="代价函数权重")

    @model_validator(mode='before')
    @classmethod
    def validate_cost_weights(cls, values):
        """允许 cost_weights 为 null"""
        if isinstance(values, dict) and values.get('cost_weights') is None:
            values['cost_weights'] = None
        return values

    class Config:
        use_enum_values = True
        from_attributes = True
        json_schema_extra = {
            "example": {
                "grid_resolution": 0.2,
                "time_window": 60,
                "match_distance_threshold": 0.12,
                "residual_threshold": 0.5,
                "min_samples": 2,
                "max_iterations": 200,
                "outlier_ratio_threshold": 0.5,
                "optimization_steps": [0.1, 0.01],
                "cost_weights": {
                    "variance": 100.0,
                    "azimuth_error_square": 0.15,
                    "range_error_square": 6e-7,
                    "elevation_error_square": 0.1,
                }
            }
        }
