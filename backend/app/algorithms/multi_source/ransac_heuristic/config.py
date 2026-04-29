"""
启发式 RANSAC 算法配置模型

通过启发式方法（偏差排序 + 差值突变检测）识别故障雷达站
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class RansacHeuristicCostWeights(BaseModel):
    """代价函数权重配置"""
    variance: float = Field(default=100.0, description="方差权重")
    azimuth_error_square: float = Field(default=0.15, description="方位角误差平方项权重（度^2）")
    range_error_square: float = Field(default=6e-7, description="距离误差平方项权重（米^2）")
    elevation_error_square: float = Field(default=0.1, description="俯仰角误差平方项权重（度^2）")


class RansacHeuristicAlgorithmConfig(BaseModel):
    """
    启发式 RANSAC 算法配置

    通过启发式方法识别故障雷达站：
    1. 计算每个匹配组的几何中心
    2. 计算每个站与中心的偏差
    3. 按偏差排序，检测差值突变点
    4. 突变点之前是健康站，之后是故障站
    """

    # ========== 数据处理配置 ==========
    grid_resolution: float = Field(default=0.2, ge=0.01, le=1.0, description="网格分辨率（度）")
    time_window: int = Field(default=60, ge=10, le=600, description="时间窗口长度（秒）")
    time_window_ratio: float = Field(default=0.75, ge=0.1, le=1.0, description="时间窗口比例")
    match_distance_threshold: float = Field(default=0.12, ge=0.01, le=1.0, description="匹配距离阈值（度）")

    # ========== 航迹提取配置 ==========
    min_track_points: int = Field(default=10, ge=3, le=100, description="最小航迹点数")

    # ========== 启发式 RANSAC 参数 ==========
    jump_threshold: float = Field(
        default=0.01, ge=0.001, le=1.0,
        description="差值突变阈值（度），用于检测健康站和故障站的边界"
    )
    min_healthy_stations: int = Field(
        default=2, ge=2, le=10,
        description="最少健康站数量，即使差值突变不明显也保留至少这么多健康站"
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
    cost_weights: Optional[RansacHeuristicCostWeights] = Field(
        default=None, description="代价函数权重"
    )

    class Config:
        use_enum_values = True
        from_attributes = True
        json_schema_extra = {
            "example": {
                "grid_resolution": 0.2,
                "time_window": 60,
                "match_distance_threshold": 0.12,
                "jump_threshold": 0.01,
                "min_healthy_stations": 2,
                "outlier_ratio_threshold": 0.5,
                "optimization_steps": [0.1, 0.01],
            }
        }
