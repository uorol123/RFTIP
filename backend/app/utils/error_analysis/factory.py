"""
算法工厂

根据算法名称和配置创建算法实例
"""
from typing import Optional, Dict, Any
from app.utils.error_analysis.registry import registry
from app.utils.error_analysis.base import BaseErrorAnalysisAlgorithm
from core.logging import get_logger

logger = get_logger(__name__)


class AlgorithmFactory:
    """算法工厂类"""

    @staticmethod
    def create_algorithm(
        algorithm_name: str,
        config: Optional[Any] = None
    ) -> BaseErrorAnalysisAlgorithm:
        """
        创建算法实例

        Args:
            algorithm_name: 算法名称
            config: 算法配置（如果为None，使用默认配置）

        Returns:
            算法实例

        Raises:
            ValueError: 算法不存在时
        """
        algorithm_class = registry.get(algorithm_name)
        if algorithm_class is None:
            available = ", ".join([alg["name"] for alg in registry.list_algorithms()])
            raise ValueError(
                f"未知算法: '{algorithm_name}'. "
                f"可用算法: {available}"
            )

        # 使用默认配置（如果未提供）
        if config is None:
            # 创建临时实例获取默认配置
            temp_instance = object.__new__(algorithm_class)
            config = temp_instance.get_default_config()

        logger.info(f"创建算法实例: {algorithm_name}")
        return algorithm_class(config)

    @staticmethod
    def create_algorithm_from_dict(
        algorithm_name: str,
        config_dict: Dict[str, Any]
    ) -> BaseErrorAnalysisAlgorithm:
        """
        从字典配置创建算法实例

        Args:
            algorithm_name: 算法名称
            config_dict: 配置字典

        Returns:
            算法实例
        """
        algorithm_class = registry.get(algorithm_name)
        if algorithm_class is None:
            raise ValueError(f"未知算法: '{algorithm_name}'")

        # 尝试获取配置类
        config_class = None
        if hasattr(algorithm_class, 'get_config_class'):
            config_class = algorithm_class.get_config_class()
        elif hasattr(algorithm_class, 'ConfigClass'):
            config_class = algorithm_class.ConfigClass

        if config_class:
            config = config_class(**config_dict)
        else:
            # 使用字典作为配置
            config = config_dict

        return algorithm_class(config)

    @staticmethod
    def get_algorithm_info(algorithm_name: str) -> Optional[Dict[str, any]]:
        """获取算法信息"""
        algorithm_class = registry.get(algorithm_name)
        if algorithm_class is None:
            return None

        return {
            "name": algorithm_class.ALGORITHM_NAME,
            "version": algorithm_class.ALGORITHM_VERSION,
            "display_name": algorithm_class.ALGORITHM_DISPLAY_NAME,
            "description": algorithm_class.ALGORITHM_DESCRIPTION,
            "supports_elevation": algorithm_class.supports_elevation(),
        }
