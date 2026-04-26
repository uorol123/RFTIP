"""
误差分析算法模块

提供插件化的误差分析算法架构，支持：
- 算法注册与发现
- 统一的算法接口
- 动态配置管理

使用示例:
    from app.utils.error_analysis import registry, AlgorithmFactory

    # 列出所有算法
    algorithms = registry.list_algorithms()

    # 创建算法实例
    algorithm = AlgorithmFactory.create_algorithm("mrra", config)
    result = await algorithm.analyze(...)
"""

from app.utils.error_analysis.registry import registry, AlgorithmRegistry
from app.utils.error_analysis.factory import AlgorithmFactory
from app.utils.error_analysis.base import (
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
from app.utils.error_analysis.algorithms import register_all_algorithms
register_all_algorithms()
