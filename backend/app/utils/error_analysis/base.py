"""
误差分析算法基类

定义所有误差分析算法必须实现的统一接口
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class AnalysisResult:
    """统一的分析结果格式"""
    task_id: str
    algorithm_name: str
    algorithm_version: str

    # 任务状态
    status: str  # 'pending', 'running', 'completed', 'failed'
    progress: float  # 0.0 - 1.0
    error_message: Optional[str] = None

    # 时间信息
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # 分析结果
    errors: Dict[int, Dict[str, float]] = field(default_factory=dict)  # station_id -> {azimuth, range, elevation}
    match_statistics: Dict[str, Any] = field(default_factory=dict)
    processing_time_seconds: float = 0.0

    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)


class ProgressCallback:
    """进度回调接口"""

    def on_progress(self, progress: float, message: str):
        """报告进度

        Args:
            progress: 进度值 (0.0 - 1.0)
            message: 进度消息
        """
        pass

    def on_step_complete(self, step_name: str, duration: float):
        """报告步骤完成

        Args:
            step_name: 步骤名称
            duration: 耗时（秒）
        """
        pass

    def on_error(self, error: str):
        """报告错误

        Args:
            error: 错误消息
        """
        pass


class BaseErrorAnalysisAlgorithm(ABC):
    """
    误差分析算法基类

    所有算法必须继承此类并实现抽象方法
    """

    # 算法元信息（子类必须覆盖）
    ALGORITHM_NAME: str = "base"
    ALGORITHM_VERSION: str = "1.0.0"
    ALGORITHM_DISPLAY_NAME: str = "基础算法"
    ALGORITHM_DESCRIPTION: str = "算法描述"

    def __init__(self, config):
        """
        初始化算法

        Args:
            config: 算法配置对象
        """
        self.config = config
        self._validate_config()

    @abstractmethod
    def _validate_config(self):
        """
        验证配置参数

        Raises:
            ValueError: 配置无效时抛出
        """
        pass

    @abstractmethod
    def analyze(
        self,
        radar_station_ids: List[int],
        track_ids: List[str],
        db_session: Any,
        progress_callback: Optional[ProgressCallback] = None
    ) -> AnalysisResult:
        """
        执行误差分析

        Args:
            radar_station_ids: 雷达站ID列表
            track_ids: 轨迹ID列表
            db_session: 数据库会话
            progress_callback: 进度回调（可选）

        Returns:
            AnalysisResult: 分析结果
        """
        pass

    def get_default_config(self):
        """
        获取算法的默认配置

        Returns:
            默认配置对象
        """
        raise NotImplementedError

    def get_config_schema(self) -> Dict[str, Any]:
        """
        获取配置参数的JSON Schema（用于前端验证）

        Returns:
            Dict: JSON Schema
        """
        raise NotImplementedError

    def get_config_preset_profiles(self) -> Dict[str, Any]:
        """
        获取预设配置方案（可选）

        Returns:
            Dict: 预设配置名称 -> 配置对象
        """
        return {}

    @classmethod
    def supports_elevation(cls) -> bool:
        """
        算法是否支持俯仰角误差计算

        Returns:
            bool: 是否支持
        """
        return True

    def estimate_processing_time(
        self,
        station_count: int,
        track_count: int,
        total_points: int
    ) -> float:
        """
        估算处理时间（秒）

        Args:
            station_count: 雷达站数量
            track_count: 轨迹数量
            total_points: 总点数

        Returns:
            float: 预估时间（秒）
        """
        # 默认估算：每1000个点约1秒
        return max(1.0, total_points / 1000.0)
