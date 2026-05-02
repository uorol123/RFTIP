"""
MRRA 算法实现（坐标下降迭代寻优）

算法流程：
1. 复用预处理模块的航迹提取、插值、匹配流程获取匹配组
2. 使用坐标下降法依次优化方位角、距离、俯仰角误差
3. 输出各雷达站的系统误差
"""
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.algorithms.base import (
    BaseErrorAnalysisAlgorithm,
    AnalysisResult,
    ProgressCallback,
)
from app.algorithms.multi_source.mrra.config import MrraAlgorithmConfig, MrraCostWeights
from app.algorithms.multi_source.preprocessing.config import MrraConfig, CostWeights
from app.algorithms.multi_source.preprocessing.track_extractor import load_track_points_by_track_ids, extract_key_tracks
from app.algorithms.multi_source.preprocessing.track_interpolator import interpolate_and_save_tracks
from app.algorithms.multi_source.preprocessing.track_matcher import match_tracks_from_database, save_matched_groups
from app.algorithms.multi_source.preprocessing.error_calculator import ErrorCalculator
from app.models.flight_track import RadarStation, FlightTrackRaw
from sqlalchemy.orm import Session
from core.logging import get_logger

logger = get_logger(__name__)


class MrraAlgorithm(BaseErrorAnalysisAlgorithm):
    """
    MRRA 算法（Multi-Radar Reference Analysis）

    使用坐标下降法，依次优化各雷达站的方位角、距离、俯仰角系统误差。
    """

    ALGORITHM_NAME = "mrra"
    ALGORITHM_VERSION = "1.0.0"
    ALGORITHM_DISPLAY_NAME = "MRRA 坐标下降迭代寻优"
    ALGORITHM_DESCRIPTION = (
        "通过航迹匹配和坐标下降迭代寻优，"
        "依次计算各雷达站的方位角、距离和俯仰角系统误差。"
    )

    ConfigClass = MrraAlgorithmConfig

    def __init__(self, config: MrraAlgorithmConfig):
        super().__init__(config)

    def _validate_config(self):
        if not isinstance(self.config, MrraAlgorithmConfig):
            raise ValueError("配置必须是 MrraAlgorithmConfig 类型")

    def analyze(
        self,
        task_id: str,
        radar_station_ids: List[int],
        track_ids: List[str],
        db_session: Session,
        progress_callback: Optional[ProgressCallback] = None,
    ) -> AnalysisResult:
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
                station.id: (station.longitude, station.latitude, station.altitude or 0.0)
                for station in radar_stations
            }

            if not radar_positions:
                raise ValueError("没有找到指定的雷达站位置信息")

            # 构建预处理配置
            mrra_config = self._build_mrra_config()

            # 步骤1: 加载并提取航迹
            if progress_callback:
                progress_callback.on_progress(0.1, "加载并提取航迹")
            self._update_task_progress(db_session, task_id, 10, "加载并提取航迹")

            station_data = load_track_points_by_track_ids(
                db_session, track_ids, radar_positions
            )
            if not station_data:
                raise ValueError("没有找到有效的航迹数据")

            key_tracks = extract_key_tracks(station_data, mrra_config)
            if not key_tracks:
                raise ValueError("没有提取到关键航迹")

            result.progress = 0.3

            # 步骤2: 插值
            if progress_callback:
                progress_callback.on_progress(0.3, "航迹插值")
            self._update_task_progress(db_session, task_id, 40, "航迹插值")

            first_track = db_session.query(FlightTrackRaw).filter(
                FlightTrackRaw.batch_id.in_(track_ids)
            ).order_by(FlightTrackRaw.timestamp).first()
            reference_time = (
                first_track.timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
                if first_track
                else datetime.utcnow()
            )

            interpolate_and_save_tracks(
                db_session, task_id, key_tracks, mrra_config, reference_time
            )

            result.progress = 0.5

            # 步骤3: 匹配
            if progress_callback:
                progress_callback.on_progress(0.5, "航迹匹配")
            self._update_task_progress(db_session, task_id, 60, "航迹匹配")

            matched_groups = match_tracks_from_database(
                db_session, task_id, mrra_config
            )
            if not matched_groups:
                raise ValueError("没有匹配到航迹组")

            save_matched_groups(db_session, task_id, matched_groups, reference_time)

            result.progress = 0.7

            # 步骤4: 计算误差
            if progress_callback:
                progress_callback.on_progress(0.7, "计算系统误差")
            self._update_task_progress(db_session, task_id, 80, "误差计算中")

            error_calc = ErrorCalculator(mrra_config)
            station_errors = error_calc.calculate_radar_errors(matched_groups, radar_positions)

            errors = {}
            for sid, (az_err, range_err, elev_err) in station_errors.items():
                errors[sid] = {
                    "azimuth_error": az_err,
                    "range_error": range_err,
                    "elevation_error": elev_err,
                }

            result.progress = 1.0

            # 完成
            result.status = "completed"
            result.errors = errors
            result.completed_at = datetime.now()
            result.processing_time_seconds = (
                result.completed_at - start_time
            ).total_seconds()
            result.match_statistics = {
                "total_match_groups": len(matched_groups),
            }
            result.metadata = {
                "algorithm": "mrra",
            }

            logger.info(
                f"[{task_id}] MRRA 分析完成，耗时 {result.processing_time_seconds:.2f} 秒"
            )

            return result

        except Exception as e:
            logger.error(f"[{task_id}] MRRA 分析失败: {str(e)}", exc_info=True)
            result.status = "failed"
            result.error_message = str(e)
            result.completed_at = datetime.now()
            if progress_callback:
                progress_callback.on_error(str(e))
            return result

    def _build_mrra_config(self) -> MrraConfig:
        """将算法配置转换为预处理模块的 MrraConfig"""
        weights = self.config.cost_weights or MrraCostWeights()
        cost_weights = CostWeights(
            variance=weights.variance,
            azimuth_error_square=weights.azimuth_error_square,
            range_error_square=weights.range_error_square,
            elevation_error_square=weights.elevation_error_square,
        )
        return MrraConfig(
            grid_resolution=self.config.grid_resolution,
            time_window=self.config.time_window,
            time_window_ratio=self.config.time_window_ratio,
            match_distance_threshold=self.config.match_distance_threshold,
            min_track_points=self.config.min_track_points,
            optimization_steps=self.config.optimization_steps,
            range_optimization_steps=self.config.range_optimization_steps,
            max_match_groups=self.config.max_match_groups,
            cost_weights=cost_weights,
        )

    def _update_task_progress(
        self, db: Session, task_id: str, progress: int, message: str
    ):
        """更新数据库中任务的进度"""
        try:
            from app.models.error_analysis import ErrorAnalysisTask
            task = db.query(ErrorAnalysisTask).filter(
                ErrorAnalysisTask.task_id == task_id
            ).first()
            if task:
                task.progress = progress
                db.commit()
        except Exception:
            pass

    @staticmethod
    def get_default_config() -> MrraAlgorithmConfig:
        return MrraAlgorithmConfig()

    @staticmethod
    def get_config_class():
        return MrraAlgorithmConfig

    def get_config_schema(self) -> Dict[str, Any]:
        return MrraAlgorithmConfig.model_json_schema()

    def get_config_preset_profiles(self) -> Dict[str, MrraAlgorithmConfig]:
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
