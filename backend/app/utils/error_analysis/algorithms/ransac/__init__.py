"""
RANSAC 算法模块

随机抽样一致性算法，用于多源参考模式
"""
from app.utils.error_analysis.algorithms.ransac.algorithm import RansacAlgorithm

__all__ = ["RansacAlgorithm"]

# 注册到全局算法注册表
from app.utils.error_analysis.registry import register_algorithm
register_algorithm(RansacAlgorithm)
