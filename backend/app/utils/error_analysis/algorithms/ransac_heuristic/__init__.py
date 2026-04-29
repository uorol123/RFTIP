"""
启发式 RANSAC 算法模块

通过启发式方法识别故障雷达站
"""
from app.utils.error_analysis.algorithms.ransac_heuristic.algorithm import RansacHeuristicAlgorithm

__all__ = ["RansacHeuristicAlgorithm"]

# 注册到全局算法注册表
from app.utils.error_analysis.registry import register_algorithm
register_algorithm(RansacHeuristicAlgorithm)
