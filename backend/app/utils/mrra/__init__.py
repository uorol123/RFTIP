"""
MRRA (Multi-source Radar Registration Analysis) 集成模块

该模块实现了基于MRRA算法的雷达误差分析功能，包括：
- 关键航迹提取
- 航迹插值
- 航迹匹配
- 误差计算
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
