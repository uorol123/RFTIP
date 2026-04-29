"""
RANSAC 算法实现（适配误差分析框架）

算法流程：
1. 复用 MRRA 的航迹提取、插值、匹配流程获取匹配组
2. 对每个匹配组应用 RANSAC，识别离群观测点（故障/低精度雷达站）
3. 统计各雷达站的离群率，判定故障站
4. 基于内点数据计算各站系统误差（方位角、距离、俯仰角）
"""
import math
import numpy as np
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from collections import defaultdict

from sklearn.linear_model import RANSACRegressor

from app.algorithms.base import (
    BaseErrorAnalysisAlgorithm,
    AnalysisResult,
    ProgressCallback,
)
from app.algorithms.multi_source.ransac.config import RansacAlgorithmConfig, RansacCostWeights
from app.algorithms.multi_source.preprocessing.config import MrraConfig
from app.algorithms.multi_source.preprocessing.track_extractor import load_track_points_by_track_ids, extract_key_tracks
from app.algorithms.multi_source.preprocessing.track_interpolator import interpolate_and_save_tracks
from app.algorithms.multi_source.preprocessing.track_matcher import match_tracks_from_database, save_matched_groups
from app.algorithms.multi_source.preprocessing.error_calculator import ErrorCalculator
from app.models.flight_track import RadarStation, FlightTrackRaw
from sqlalchemy.orm import Session
from core.logging import get_logger

logger = get_logger(__name__)


class RansacAlgorithm(BaseErrorAnalysisAlgorithm):
    """
    RANSAC 随机抽样一致性算法

    通过 RANSAC 剔除偏离群体的"坏点"雷达站，识别故障/低精度设备，
    然后基于内点计算系统误差。
    """

    ALGORITHM_NAME = "ransac"
    ALGORITHM_VERSION = "1.0.0"
    ALGORITHM_DISPLAY_NAME = "RANSAC 随机抽样一致性算法"
    ALGORITHM_DESCRIPTION = (
        "通过随机抽样一致性（RANSAC）从多雷达匹配组中剔除离群观测，"
        "识别故障或低精度雷达站，并基于内点计算各站的系统误差。"
    )

    ConfigClass = RansacAlgorithmConfig

    def __init__(self, config: RansacAlgorithmConfig):
        super().__init__(config)

    def _validate_config(self):
        if not isinstance(self.config, RansacAlgorithmConfig):
            raise ValueError("配置必须是 RansacAlgorithmConfig 类型")

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

            # 构建 MRRA 兼容配置（复用航迹提取、插值、匹配流程）
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

            # 步骤4: RANSAC 分析（核心步骤）
            if progress_callback:
                progress_callback.on_progress(0.7, "RANSAC 离群点检测与误差计算")
            self._update_task_progress(db_session, task_id, 80, "RANSAC 分析中")

            ransac_results = self._ransac_analyze(matched_groups, radar_positions)

            result.progress = 1.0

            # 完成
            result.status = "completed"
            result.errors = ransac_results["errors"]
            result.completed_at = datetime.now()
            result.processing_time_seconds = (
                result.completed_at - start_time
            ).total_seconds()
            result.match_statistics = {
                "total_match_groups": len(matched_groups),
                "station_outlier_rates": ransac_results["outlier_rates"],
                "fault_stations": ransac_results["fault_stations"],
                "inlier_match_groups": ransac_results["inlier_count"],
            }
            result.metadata = {
                "algorithm": "ransac",
                "residual_threshold": self.config.residual_threshold,
                "min_samples": self.config.min_samples,
                "max_iterations": self.config.max_iterations,
                "outlier_ratio_threshold": self.config.outlier_ratio_threshold,
            }

            logger.info(
                f"[{task_id}] RANSAC 分析完成，耗时 {result.processing_time_seconds:.2f} 秒，"
                f"故障站: {ransac_results['fault_stations']}"
            )

            return result

        except Exception as e:
            logger.error(f"[{task_id}] RANSAC 分析失败: {str(e)}", exc_info=True)
            result.status = "failed"
            result.error_message = str(e)
            result.completed_at = datetime.now()
            if progress_callback:
                progress_callback.on_error(str(e))
            return result

    def _build_mrra_config(self) -> MrraConfig:
        """将 RANSAC 配置转换为 MRRA 兼容配置"""
        # 如果 cost_weights 为 None，使用默认值
        weights = self.config.cost_weights or RansacCostWeights()
        return MrraConfig(
            grid_resolution=self.config.grid_resolution,
            time_window=self.config.time_window,
            time_window_ratio=self.config.time_window_ratio,
            match_distance_threshold=self.config.match_distance_threshold,
            min_track_points=self.config.min_track_points,
            optimization_steps=self.config.optimization_steps,
            range_optimization_steps=self.config.range_optimization_steps,
            max_match_groups=self.config.max_match_groups,
            cost_weights={
                "variance": weights.variance,
                "azimuth_error_square": weights.azimuth_error_square,
                "range_error_square": weights.range_error_square,
                "elevation_error_square": weights.elevation_error_square,
            },
        )

    def _ransac_analyze(
        self,
        matched_groups: List[List[Dict]],
        radar_positions: Dict[int, Tuple],
    ) -> Dict[str, Any]:
        """
        对匹配组执行 RANSAC 分析

        1. 对每个匹配组，将多雷达观测点转为坐标矩阵
        2. 用 RANSACRegressor 区分内点和离群点
        3. 统计各站的离群率
        4. 基于内点数据用 ErrorCalculator 计算系统误差
        """
        # 统计每个站在所有匹配组中的离群次数
        station_total = defaultdict(int)
        station_outlier = defaultdict(int)

        # 过滤后的匹配组（仅保留内点）
        inlier_groups = []

        inlier_count = 0

        for group in matched_groups:
            if len(group) < self.config.min_samples:
                inlier_groups.append(group)
                inlier_count += 1
                continue

            # 提取坐标
            lats = np.array([p["latitude"] for p in group])
            lons = np.array([p["longitude"] for p in group])
            station_ids = [p["station_id"] for p in group]

            # 对经纬度分别做 RANSAC
            try:
                # 使用 lat 预测 lon 的线性关系
                ransac = RANSACRegressor(
                    residual_threshold=self.config.residual_threshold,
                    min_samples=min(self.config.min_samples, len(group)),
                    max_iterations=self.config.max_iterations,
                )
                X = lats.reshape(-1, 1)
                y = lons
                ransac.fit(X, y)
                inlier_mask = ransac.inlier_mask_
            except Exception:
                # RANSAC 失败时，全部视为内点
                inlier_mask = np.ones(len(group), dtype=bool)

            # 统计离群点
            inlier_group = []
            for i, point in enumerate(group):
                sid = point["station_id"]
                station_total[sid] += 1
                if not inlier_mask[i]:
                    station_outlier[sid] += 1
                else:
                    inlier_group.append(point)

            if inlier_group:
                inlier_groups.append(inlier_group)
                inlier_count += 1

        # 计算离群率
        outlier_rates = {}
        fault_stations = []
        for sid in station_total:
            rate = station_outlier[sid] / station_total[sid]
            outlier_rates[sid] = round(rate, 4)
            if rate >= self.config.outlier_ratio_threshold:
                fault_stations.append(sid)

        # 用内点数据计算系统误差（复用 ErrorCalculator）
        mrra_config = self._build_mrra_config()
        error_calc = ErrorCalculator(mrra_config)

        # 使用正确的 calculate_radar_errors 方法
        station_errors = error_calc.calculate_radar_errors(inlier_groups, radar_positions)

        errors = {}
        for sid, (az_err, range_err, elev_err) in station_errors.items():
            errors[sid] = {
                "azimuth_error": az_err,
                "range_error": range_err,
                "elevation_error": elev_err,
            }

        return {
            "errors": errors,
            "outlier_rates": outlier_rates,
            "fault_stations": fault_stations,
            "inlier_count": inlier_count,
        }

    def _update_task_progress(
        self, db: Session, task_id: str, progress: int, message: str
    ):
        """更新数据库中任务的进度（如果存在对应任务）"""
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
    def get_default_config() -> RansacAlgorithmConfig:
        return RansacAlgorithmConfig()

    @staticmethod
    def get_config_class():
        return RansacAlgorithmConfig

    def get_config_schema(self) -> Dict[str, Any]:
        return RansacAlgorithmConfig.model_json_schema()

    def get_config_preset_profiles(self) -> Dict[str, RansacAlgorithmConfig]:
        return {
            "standard": RansacAlgorithmConfig(),
            "strict": RansacAlgorithmConfig(
                residual_threshold=0.3,
                min_samples=2,
                outlier_ratio_threshold=0.3,
                optimization_steps=[0.05, 0.01, 0.005],
            ),
            "loose": RansacAlgorithmConfig(
                residual_threshold=1.0,
                min_samples=2,
                outlier_ratio_threshold=0.7,
                optimization_steps=[0.1, 0.01],
            ),
            "fast": RansacAlgorithmConfig(
                residual_threshold=0.5,
                max_iterations=100,
                grid_resolution=0.5,
                optimization_steps=[0.2, 0.05],
                range_optimization_steps=[1000, 500, 100],
            ),
        }
