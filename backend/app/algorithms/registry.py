"""
算法注册表

管理所有可用的误差分析算法
"""
from typing import Dict, Type, List, Optional
from app.algorithms.base import BaseErrorAnalysisAlgorithm


class AlgorithmRegistry:
    """
    算法注册表（单例模式）
    """

    _instance: Optional['AlgorithmRegistry'] = None
    _algorithms: Dict[str, Type[BaseErrorAnalysisAlgorithm]] = {}

    def __new__(cls) -> 'AlgorithmRegistry':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def register(
        self,
        algorithm_class: Type[BaseErrorAnalysisAlgorithm]
    ) -> Type[BaseErrorAnalysisAlgorithm]:
        """
        注册算法

        Args:
            algorithm_class: 算法类

        Returns:
            算法类（支持装饰器语法）
        """
        name = algorithm_class.ALGORITHM_NAME
        if name in self._algorithms:
            raise ValueError(f"算法 '{name}' 已注册")

        self._algorithms[name] = algorithm_class
        return algorithm_class

    def unregister(self, algorithm_name: str):
        """注销算法"""
        if algorithm_name in self._algorithms:
            del self._algorithms[algorithm_name]

    def get(self, algorithm_name: str) -> Optional[Type[BaseErrorAnalysisAlgorithm]]:
        """获取算法类"""
        return self._algorithms.get(algorithm_name)

    def list_algorithms(self) -> List[Dict[str, any]]:
        """
        列出所有已注册算法

        Returns:
            算法信息列表
        """
        return [
            {
                "name": alg.ALGORITHM_NAME,
                "version": alg.ALGORITHM_VERSION,
                "display_name": alg.ALGORITHM_DISPLAY_NAME,
                "description": alg.ALGORITHM_DESCRIPTION,
                "supports_elevation": alg.supports_elevation(),
            }
            for alg in self._algorithms.values()
        ]

    def is_registered(self, algorithm_name: str) -> bool:
        """检查算法是否已注册"""
        return algorithm_name in self._algorithms


# 全局注册表实例
registry = AlgorithmRegistry()


def register_algorithm(algorithm_class: Type[BaseErrorAnalysisAlgorithm]):
    """
    装饰器：注册算法

    Usage:
        @register_algorithm
        class MyAlgorithm(BaseErrorAnalysisAlgorithm):
            ...
    """
    return registry.register(algorithm_class)
