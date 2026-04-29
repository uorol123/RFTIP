"""
样条平滑算法配置模型
"""
from pydantic import BaseModel, Field


class SplineAlgorithmConfig(BaseModel):
    """
    样条平滑算法配置

    用于单源盲测模式，对轨迹进行连续平滑处理
    """

    # ========== 平滑参数 ==========
    smoothing_factor: float = Field(
        default=0.1, ge=0.001, le=100.0,
        description="平滑因子（越大越平滑，但可能欠拟合）"
    )
    spline_degree: int = Field(
        default=3, ge=1, le=5,
        description="样条阶数（1=线性, 2=二次, 3=三次）"
    )

    # ========== 数据处理 ==========
    min_track_points: int = Field(default=5, ge=4, le=100, description="最小航迹点数")
    interpolate: bool = Field(
        default=False,
        description="是否在原始点之间插值（增加轨迹密度）"
    )
    interpolation_density: int = Field(
        default=10, ge=2, le=100,
        description="插值密度（每两个原始点之间插入的点数）"
    )

    class Config:
        use_enum_values = True
        from_attributes = True
        json_schema_extra = {
            "example": {
                "smoothing_factor": 0.1,
                "spline_degree": 3,
                "min_track_points": 5,
                "interpolate": False,
            }
        }
