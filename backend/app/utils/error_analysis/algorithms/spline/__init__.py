"""样条平滑算法模块"""
from app.utils.error_analysis.algorithms.spline.algorithm import SplineAlgorithm

__all__ = ["SplineAlgorithm"]

from app.utils.error_analysis.registry import register_algorithm
register_algorithm(SplineAlgorithm)
