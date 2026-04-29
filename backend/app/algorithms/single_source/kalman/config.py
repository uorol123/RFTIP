"""
卡尔曼滤波算法配置模型
"""
from pydantic import BaseModel, Field


class KalmanAlgorithmConfig(BaseModel):
    """
    卡尔曼滤波算法配置

    用于单源盲测模式，基于物理运动模型对单站数据进行预测与修正
    """

    # ========== 滤波参数 ==========
    process_noise: float = Field(
        default=0.1, ge=0.001, le=10.0,
        description="过程噪声协方差（越大越信任观测）"
    )
    measurement_noise: float = Field(
        default=1.0, ge=0.01, le=100.0,
        description="测量噪声协方差（越大越信任模型）"
    )
    initial_uncertainty: float = Field(
        default=100.0, ge=1.0, le=10000.0,
        description="初始状态不确定性"
    )

    # ========== 数据处理配置 ==========
    min_track_points: int = Field(
        default=5, ge=2, le=100,
        description="最小航迹点数"
    )

    class Config:
        use_enum_values = True
        from_attributes = True
        json_schema_extra = {
            "example": {
                "process_noise": 0.1,
                "measurement_noise": 1.0,
                "initial_uncertainty": 100.0,
                "min_track_points": 5,
            }
        }
