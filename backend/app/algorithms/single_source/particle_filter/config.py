"""
粒子滤波算法配置模型
"""
from pydantic import BaseModel, Field


class ParticleFilterAlgorithmConfig(BaseModel):
    """
    粒子滤波算法配置

    用于单源盲测模式，处理非线性非高斯噪声场景
    """

    # ========== 粒子参数 ==========
    num_particles: int = Field(
        default=1000, ge=100, le=10000,
        description="粒子数量"
    )
    process_noise_std: float = Field(
        default=0.001, ge=0.0001, le=1.0,
        description="过程噪声标准差（度）"
    )
    measurement_noise_std: float = Field(
        default=0.01, ge=0.0001, le=1.0,
        description="测量噪声标准差（度）"
    )

    # ========== 重采样 ==========
    resampling_method: str = Field(
        default="systematic",
        description="重采样方法: systematic（系统重采样）、multinomial（多项式重采样）"
    )
    effective_particle_threshold: float = Field(
        default=0.5, ge=0.1, le=1.0,
        description="有效粒子数阈值比例（低于此比例触发重采样）"
    )

    # ========== 数据处理 ==========
    min_track_points: int = Field(default=5, ge=2, le=100, description="最小航迹点数")

    class Config:
        use_enum_values = True
        from_attributes = True
        json_schema_extra = {
            "example": {
                "num_particles": 1000,
                "process_noise_std": 0.001,
                "measurement_noise_std": 0.01,
                "resampling_method": "systematic",
            }
        }
