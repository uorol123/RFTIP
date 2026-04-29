"""
误差分析算法配置模块
算法名称：基于梯度下降的迭代寻优算法

使用 Pydantic BaseModel 管理所有算法配置参数
"""
from typing import List, Tuple
from pydantic import BaseModel, Field, field_validator


class CostWeights(BaseModel):
    """代价函数权重配置"""
    variance: float = Field(default=100.0, description="方差权重")
    azimuth_error_square: float = Field(default=0.15, description="方位角误差平方项权重（度^2）")
    range_error_square: float = Field(default=6e-7, description="距离误差平方项权重（米^2）")
    elevation_error_square: float = Field(default=0.1, description="俯仰角误差平方项权重（度^2）")


class MrraConfig(BaseModel):
    """
    误差分析算法配置（基于梯度下降的迭代寻优算法）

    包含所有可配置的算法参数
    """

    # ========== 数据处理配置 ==========
    grid_resolution: float = Field(default=0.2, ge=0.01, le=1.0, description="网格分辨率（度）")
    time_window: int = Field(default=60, ge=10, le=600, description="时间窗口长度（秒）")
    time_window_ratio: float = Field(default=0.75, ge=0.1, le=1.0, description="时间窗口比例（用于检测持续航迹）")
    match_distance_threshold: float = Field(default=0.12, ge=0.01, le=1.0, description="匹配距离阈值（度）")

    # ========== 航迹提取配置 ==========
    min_track_points: int = Field(default=10, ge=3, le=100, description="最小航迹点数")

    # ========== 误差计算配置 ==========
    optimization_steps: List[float] = Field(default=[0.1, 0.01], description="方位角/俯仰角优化步长序列（度）")
    range_optimization_steps: List[float] = Field(
        default=[1000, 800, 500, 200, 100, 50, 20],
        description="距离优化步长序列（米）"
    )
    cost_weights: CostWeights = Field(default_factory=CostWeights, description="代价函数权重")
    max_match_groups: int = Field(default=15000, ge=1000, le=100000, description="最大匹配组数（用于误差计算）")

    # ========== 可视化配置 ==========
    max_display_tracks: int = Field(default=100, ge=10, le=1000, description="最大显示航迹数")
    colors: str = Field(default="bgrcykmbgrcykmbgrcykmbgrcykmbgrcykmbgrcykmbgrcykmbgrcykmbgrcykm", description="颜色序列")

    @field_validator('optimization_steps')
    @classmethod
    def validate_optimization_steps(cls, v: List[float]) -> List[float]:
        """验证优化步长序列"""
        if not v or len(v) == 0:
            return [0.1, 0.01]
        # 确保步长是递减的
        for i in range(len(v) - 1):
            if v[i] <= v[i + 1]:
                raise ValueError(f"优化步长应该是递减的: {v}")
        return v

    @field_validator('range_optimization_steps')
    @classmethod
    def validate_range_steps(cls, v: List[float]) -> List[float]:
        """验证距离优化步长序列"""
        if not v or len(v) == 0:
            return [1000, 800, 500, 200, 100, 50, 20]
        # 确保步长是递减的
        for i in range(len(v) - 1):
            if v[i] <= v[i + 1]:
                raise ValueError(f"距离优化步长应该是递减的: {v}")
        return v

    def get_optimization_steps(self) -> Tuple[float, ...]:
        """获取优化步长元组"""
        return tuple(self.optimization_steps)

    def get_range_optimization_steps(self) -> Tuple[float, ...]:
        """获取距离优化步长元组"""
        return tuple(self.range_optimization_steps)

    class Config:
        """Pydantic 配置"""
        use_enum_values = True
        from_attributes = True


# 默认配置实例
default_config = MrraConfig()
