"""
加权最小二乘融合算法配置模型
"""
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator


class WeightedLstsqCostWeights(BaseModel):
    """代价函数权重配置"""
    variance: float = Field(default=100.0, description="方差权重")
    azimuth_error_square: float = Field(default=0.15, description="方位角误差平方项权重（度^2）")
    range_error_square: float = Field(default=6e-7, description="距离误差平方项权重（米^2）")
    elevation_error_square: float = Field(default=0.1, description="俯仰角误差平方项权重（度^2）")


class WeightedLstsqAlgorithmConfig(BaseModel):
    """
    加权最小二乘融合算法配置

    用于多源参考模式，综合多雷达观测数据，
    根据各站可靠性权重进行融合，输出最优估计轨迹和各站系统误差。
    """

    # ========== 数据处理配置 ==========
    grid_resolution: float = Field(default=0.2, ge=0.01, le=1.0, description="网格分辨率（度）")
    time_window: int = Field(default=60, ge=10, le=600, description="时间窗口长度（秒）")
    time_window_ratio: float = Field(default=0.75, ge=0.1, le=1.0, description="时间窗口比例")
    match_distance_threshold: float = Field(default=0.12, ge=0.01, le=1.0, description="匹配距离阈值（度）")

    # ========== 航迹提取配置 ==========
    min_track_points: int = Field(default=10, ge=3, le=100, description="最小航迹点数")

    # ========== 融合参数 ==========
    weighting_method: str = Field(
        default="inverse_variance",
        description="权重计算方法: inverse_variance（反方差）、uniform（均匀）、match_count（按匹配数）"
    )
    outlier_removal: bool = Field(
        default=True,
        description="是否在融合前移除离群观测（基于 3-sigma 准则）"
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
    cost_weights: Optional[WeightedLstsqCostWeights] = Field(
        default=None, description="代价函数权重"
    )

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
                "weighting_method": "inverse_variance",
                "outlier_removal": True,
                "optimization_steps": [0.1, 0.01],
                "cost_weights": {
                    "variance": 100.0,
                    "azimuth_error_square": 0.15,
                    "range_error_square": 6e-7,
                    "elevation_error_square": 0.1,
                }
            }
        }
