"""
加权最小二乘融合算法模块
"""
from app.utils.error_analysis.algorithms.weighted_lstsq.algorithm import WeightedLstsqAlgorithm

__all__ = ["WeightedLstsqAlgorithm"]

from app.utils.error_analysis.registry import register_algorithm
register_algorithm(WeightedLstsqAlgorithm)
