"""
误差分析算法集成模块
算法名称：基于梯度下降的迭代寻优算法

该模块实现了雷达误差分析功能，包括：
- 关键航迹提取
- 航迹插值
- 航迹匹配
- 误差计算（梯度下降迭代寻优）
"""

from app.utils.mrra.config import MrraConfig
from app.utils.mrra.track_extractor import TrackExtractor
from app.utils.mrra.track_interpolator import TrackInterpolator
from app.utils.mrra.track_matcher import TrackMatcher
from app.utils.mrra.error_calculator import ErrorCalculator

__all__ = [
    "MrraConfig",
    "TrackExtractor",
    "TrackInterpolator",
    "TrackMatcher",
    "ErrorCalculator",
]
