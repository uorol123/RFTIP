"""
算法模块

提供插件化的误差分析算法架构，支持：
- 算法注册与发现
- 统一的算法接口
- 动态配置管理
"""

from app.algorithms.registry import registry, AlgorithmRegistry
from app.algorithms.factory import AlgorithmFactory
from app.algorithms.base import (
    BaseErrorAnalysisAlgorithm,
    AnalysisResult,
    ProgressCallback,
)

__all__ = [
    "registry",
    "AlgorithmRegistry",
    "AlgorithmFactory",
    "BaseErrorAnalysisAlgorithm",
    "AnalysisResult",
    "ProgressCallback",
]

# 自动注册所有算法
from app.algorithms.algorithms_init import register_all_algorithms
register_all_algorithms()
