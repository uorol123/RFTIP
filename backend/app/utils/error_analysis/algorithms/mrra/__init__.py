"""
MRRA 算法实现

基于梯度下降的迭代寻优算法
"""
from app.utils.error_analysis.base import BaseErrorAnalysisAlgorithm
from app.utils.error_analysis.registry import register_algorithm
from app.utils.error_analysis.algorithms.mrra.algorithm import MrraAlgorithm

__all__ = ["MrraAlgorithm"]

# 自动注册算法
register_algorithm(MrraAlgorithm)
