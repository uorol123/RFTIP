"""
MRRA 算法适配器

将现有的MRRA模块适配到新的算法架构
"""
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.utils.error_analysis.base import (
    BaseErrorAnalysisAlgorithm,
    AnalysisResult,
    ProgressCallback,
)
from app.utils.error_analysis.registry import register_algorithm
from app.utils.error_analysis.algorithms.mrra.config import MrraAlgorithmConfig, MrraCostWeights
from app.utils.mrra.track_extractor import TrackExtractor
from app.utils.mrra.track_interpolator import TrackInterpolator
from app.utils.mrra.track_matcher import TrackMatcher
from app.utils.mrra.error_calculator import ErrorCalculator
from app.models.flight_track import RadarStation
from sqlalchemy.orm import Session
from core.logging import get_logger

logger = get_logger(__name__)


class MrraAlgorithm(BaseErrorAnalysisAlgorithm):
    """
    MRRA 算法
    基于梯度下降的迭代寻优算法
    """

    ALGORITHM_NAME = "gradient_descent"
    ALGORITHM_VERSION = "1.0.0"
    ALGORITHM_DISPLAY_NAME = "基于梯度下降的迭代寻优算法"
    ALGORITHM_DESCRIPTION = (
        "通过航迹匹配和梯度下降优化，"
        "计算雷达系统的方位角、距离和俯仰角误差。"
    )

    # 配置类（用于工厂创建）
    ConfigClass = MrraAlgorithmConfig

    def __init__(self, config: MrraAlgorithmConfig):
        super().__init__(config)
        # 使用现有的MRRA模块组件
        self.track_extractor = None
        self.track_interpolator = None
        self.track_matcher = None
        self.error_calculator = None

    def _validate_config(self):
        """验证配置（Pydantic自动验证）"""
        # MrraAlgorithmConfig 使用 Pydantic，已自动验证
        if not isinstance(self.config, MrraAlgorithmConfig):
            raise ValueError(f"配置必须是 MrraAlgorithmConfig 类型")

    def analyze(
        self,
        task_id: str,
        radar_station_ids: List[int],
        track_ids: List[str],
        db_session: Session,
        progress_callback: Optional[ProgressCallback] = None
    ) -> AnalysisResult:
        """
        执行误差分析

        Args:
            task_id: 任务ID
            radar_station_ids: 雷达站ID列表
            track_ids: 轨迹ID列表
            db_session: 数据库会话
            progress_callback: 进度回调

        Returns:
            AnalysisResult: 分析结果
        """
        start_time = datetime.now()

        result = AnalysisResult(
            task_id=task_id,
            algorithm_name=self.ALGORITHM_NAME,
            algorithm_version=self.ALGORITHM_VERSION,
            status="running",
            progress=0.0,
            started_at=start_time,
        )

        try:
            # 获取雷达站位置
            radar_stations = db_session.query(RadarStation).filter(
                RadarStation.id.in_(radar_station_ids)
            ).all()

            radar_positions = {
                station.station_id: (station.longitude, station.latitude, station.altitude)
                for station in radar_stations
            }

            # 初始化组件
            self._init_components(radar_positions)

            # 步骤1: 提取航迹
            if progress_callback:
                progress_callback.on_progress(0.1, "提取航迹")

            logger.info(f"[{task_id}] 开始提取航迹...")
            key_tracks = self._extract_tracks(db_session, track_ids, radar_positions)
            result.progress = 0.25

            # 步骤2: 航迹插值
            if progress_callback:
                progress_callback.on_progress(0.25, "航迹插值")

            logger.info(f"[{task_id}] 开始航迹插值...")
            segments = self._interpolate_tracks(db_session, task_id, key_tracks)
            result.progress = 0.5

            # 步骤3: 航迹匹配
            if progress_callback:
                progress_callback.on_progress(0.5, "航迹匹配")

            logger.info(f"[{task_id}] 开始航迹匹配...")
            matched_groups = self._match_tracks(db_session, task_id)
            result.progress = 0.75

            # 步骤4: 计算误差
            if progress_callback:
                progress_callback.on_progress(0.75, "计算误差")

            logger.info(f"[{task_id}] 开始计算误差...")
            errors = self._calculate_errors(matched_groups, radar_positions)
            result.progress = 1.0

            # 完成结果
            result.status = "completed"
            result.errors = errors
            result.completed_at = datetime.now()
            result.processing_time_seconds = (
                result.completed_at - start_time
            ).total_seconds()
            result.match_statistics = {
                "total_segments": len(segments),
                "total_match_groups": len(matched_groups),
            }

            logger.info(f"[{task_id}] 分析完成，耗时 {result.processing_time_seconds:.2f} 秒")

            return result

        except Exception as e:
            logger.error(f"[{task_id}] 分析失败: {str(e)}", exc_info=True)
            result.status = "failed"
            result.error_message = str(e)
            result.completed_at = datetime.now()
            if progress_callback:
                progress_callback.on_error(str(e))
            return result

    def _init_components(self, radar_positions: Dict[int, tuple]):
        """初始化MRRA组件"""
        # 将配置转换为现有MRRA模块需要的格式
        from app.utils.mrra.config import MrraConfig

        # 如果 cost_weights 为 None，使用默认值
        weights = self.config.cost_weights or MrraCostWeights()

        mrra_config = MrraConfig()
        mrra_config.GRID_RESOLUTION = self.config.grid_resolution
        mrra_config.TIME_WINDOW = self.config.time_window
        mrra_config.TIME_WINDOW_RATIO = self.config.time_window_ratio
        mrra_config.MATCH_DISTANCE_THRESHOLD = self.config.match_distance_threshold
        mrra_config.MIN_TRACK_POINTS = self.config.min_track_points
        mrra_config.OPTIMIZATION_STEPS = tuple(self.config.optimization_steps)
        mrra_config.RANGE_OPTIMIZATION_STEPS = tuple(self.config.range_optimization_steps)
        mrra_config.MAX_MATCH_GROUPS = self.config.max_match_groups
        mrra_config.COST_WEIGHT_VARIANCE = weights.variance
        mrra_config.COST_WEIGHT_AZIMUTH_ERROR_SQUARE = weights.azimuth_error_square
        mrra_config.COST_WEIGHT_RANGE_ERROR_SQUARE = weights.range_error_square
        mrra_config.COST_WEIGHT_ELEVATION_ERROR_SQUARE = weights.elevation_error_square

        self.track_extractor = TrackExtractor(mrra_config)
        self.track_interpolator = TrackInterpolator(mrra_config)
        self.track_matcher = TrackMatcher(mrra_config)
        self.error_calculator = ErrorCalculator(mrra_config)

    def _extract_tracks(self, db, track_ids, radar_positions):
        """提取航迹"""
        from app.services.error_analysis_service import load_track_points_by_track_ids

        station_data = load_track_points_by_track_ids(db, track_ids, radar_positions)

        # 使用TrackExtractor提取关键航迹
        return self.track_extractor.extract_all(station_data)

    def _interpolate_tracks(self, db, task_id, key_tracks):
        """插值航迹"""
        from app.services.error_analysis_service import interpolate_and_save_tracks

        return interpolate_and_save_tracks(db, task_id, key_tracks, self.track_interpolator.config)

    def _match_tracks(self, db, task_id):
        """匹配航迹"""
        from app.services.error_analysis_service import match_tracks_from_database

        return match_tracks_from_database(db, task_id, self.track_matcher.config)

    def _calculate_errors(self, matched_groups, radar_positions):
        """计算误差"""
        # 调用ErrorCalculator
        opt_az, opt_r, opt_elev = self.error_calculator.optimize_station_errors_separately(
            matched_groups,
            {sid: 0.0 for sid in radar_positions.keys()},
            radar_positions
        )

        # 格式化结果
        errors = {}
        for sid in radar_positions.keys():
            errors[sid] = {
                "azimuth_error": opt_az.get(sid, 0.0),
                "range_error": opt_r.get(sid, 0.0),
                "elevation_error": opt_elev.get(sid, 0.0),
            }

        return errors

    @staticmethod
    def get_default_config() -> MrraAlgorithmConfig:
        """获取默认配置"""
        return MrraAlgorithmConfig()

    @staticmethod
    def get_config_class():
        """获取配置类"""
        return MrraAlgorithmConfig

    def get_config_schema(self) -> Dict[str, Any]:
        """获取配置 JSON Schema"""
        return MrraAlgorithmConfig.model_json_schema()

    def get_config_preset_profiles(self) -> Dict[str, MrraAlgorithmConfig]:
        """获取预设配置"""
        return {
            "standard": MrraAlgorithmConfig(),
            "high_precision": MrraAlgorithmConfig(
                grid_resolution=0.1,
                optimization_steps=[0.05, 0.01, 0.005]
            ),
            "fast": MrraAlgorithmConfig(
                grid_resolution=0.5,
                optimization_steps=[0.2, 0.05]
            ),
        }
