"""卡尔曼滤波算法模块"""
from app.utils.error_analysis.algorithms.kalman.algorithm import KalmanAlgorithm

__all__ = ["KalmanAlgorithm"]

from app.utils.error_analysis.registry import register_algorithm
register_algorithm(KalmanAlgorithm)
