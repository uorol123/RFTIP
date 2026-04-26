"""
卡尔曼滤波算法实现

6 状态变量: [lat, lon, alt, v_lat, v_lon, v_alt]
匀速运动模型
"""
import numpy as np
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from collections import defaultdict

from filterpy.kalman import KalmanFilter

from app.utils.error_analysis.base import (
    BaseErrorAnalysisAlgorithm,
    AnalysisResult,
    ProgressCallback,
)
from app.utils.error_analysis.algorithms.kalman.config import KalmanAlgorithmConfig
from app.models.flight_track import RadarStation, FlightTrackRaw
from sqlalchemy.orm import Session
from core.logging import get_logger

logger = get_logger(__name__)


class KalmanAlgorithm(BaseErrorAnalysisAlgorithm):
    """
    卡尔曼滤波算法

    基于匀速运动模型对单站雷达轨迹进行平滑去噪
    """

    ALGORITHM_NAME = "kalman"
    ALGORITHM_VERSION = "1.0.0"
    ALGORITHM_DISPLAY_NAME = "卡尔曼滤波算法"
    ALGORITHM_DESCRIPTION = (
        "基于匀速运动模型的卡尔曼滤波，对单站雷达轨迹进行平滑去噪，"
        "输出修正后的轨迹和状态估计协方差（不确定性评估）。"
    )

    ConfigClass = KalmanAlgorithmConfig

    def __init__(self, config: KalmanAlgorithmConfig):
        super().__init__(config)

    def _validate_config(self):
        if not isinstance(self.config, KalmanAlgorithmConfig):
            raise ValueError("配置必须是 KalmanAlgorithmConfig 类型")

    @classmethod
    def supports_elevation(cls) -> bool:
        return True

    def analyze(
        self,
        radar_station_ids: List[int],
        track_ids: List[str],
        db_session: Session,
        progress_callback: Optional[ProgressCallback] = None,
    ) -> AnalysisResult:
        start_time = datetime.now()
        task_id = f"{self.ALGORITHM_NAME}_{int(start_time.timestamp())}"

        result = AnalysisResult(
            task_id=task_id,
            algorithm_name=self.ALGORITHM_NAME,
            algorithm_version=self.ALGORITHM_VERSION,
            status="running",
            progress=0.0,
            started_at=start_time,
        )

        try:
            if progress_callback:
                progress_callback.on_progress(0.1, "加载轨迹数据")

            # 加载原始轨迹数据
            tracks = db_session.query(FlightTrackRaw).filter(
                FlightTrackRaw.batch_id.in_(track_ids),
                FlightTrackRaw.radar_station_id.in_(radar_station_ids),
            ).order_by(FlightTrackRaw.timestamp).all()

            if not tracks:
                raise ValueError("没有找到指定的轨迹数据")

            # 按 batch_id 分组
            track_groups = defaultdict(list)
            for t in tracks:
                track_groups[t.batch_id].append(t)

            total_tracks = len(track_groups)
            smoothed_all = []
            errors = {}
            track_idx = 0

            for batch_id, group in track_groups.items():
                # 按时间排序
                group.sort(key=lambda t: t.timestamp)

                if len(group) < self.config.min_track_points:
                    track_idx += 1
                    continue

                if progress_callback:
                    progress = 0.1 + 0.8 * (track_idx / total_tracks)
                    progress_callback.on_progress(progress, f"滤波处理: {batch_id}")

                # 执行卡尔曼滤波
                smoothed = self._apply_kalman_filter(group)
                smoothed_all.extend(smoothed)

                # 计算平滑前后的偏差作为"误差"
                for i, point in enumerate(smoothed):
                    sid = point["station_id"]
                    if sid not in errors:
                        errors[sid] = {
                            "azimuth_error": 0.0,
                            "range_error": 0.0,
                            "elevation_error": 0.0,
                            "_count": 0,
                            "_lat_diff_sq": 0.0,
                            "_lon_diff_sq": 0.0,
                            "_alt_diff_sq": 0.0,
                        }
                    errors[sid]["_count"] += 1
                    errors[sid]["_lat_diff_sq"] += (point["orig_lat"] - point["latitude"]) ** 2
                    errors[sid]["_lon_diff_sq"] += (point["orig_lon"] - point["longitude"]) ** 2
                    if point.get("orig_alt") is not None and point.get("altitude") is not None:
                        errors[sid]["_alt_diff_sq"] += (point["orig_alt"] - point["altitude"]) ** 2

                track_idx += 1

            # 计算平均偏差
            for sid in errors:
                n = errors[sid]["_count"]
                if n > 0:
                    lat_rmse = np.sqrt(errors[sid]["_lat_diff_sq"] / n)
                    lon_rmse = np.sqrt(errors[sid]["_lon_diff_sq"] / n)
                    errors[sid]["azimuth_error"] = round(lat_rmse, 6)
                    errors[sid]["range_error"] = round(
                        np.sqrt(errors[sid]["_lat_diff_sq"] + errors[sid]["_lon_diff_sq"]) / n * 111000, 2
                    )
                    errors[sid]["elevation_error"] = round(
                        np.sqrt(errors[sid]["_alt_diff_sq"] / n), 4
                    )
                del errors[sid]["_count"]
                del errors[sid]["_lat_diff_sq"]
                del errors[sid]["_lon_diff_sq"]
                del errors[sid]["_alt_diff_sq"]

            result.progress = 1.0
            result.status = "completed"
            result.errors = errors
            result.completed_at = datetime.now()
            result.processing_time_seconds = (result.completed_at - start_time).total_seconds()
            result.match_statistics = {
                "total_tracks": total_tracks,
                "total_smoothed_points": len(smoothed_all),
                "process_noise": self.config.process_noise,
                "measurement_noise": self.config.measurement_noise,
            }
            result.metadata = {
                "algorithm": "kalman",
                "smoothed_trajectory": smoothed_all[:500],
                "total_points": len(smoothed_all),
            }

            logger.info(f"[{task_id}] 卡尔曼滤波完成，处理 {len(smoothed_all)} 个点")
            return result

        except Exception as e:
            logger.error(f"[{task_id}] 卡尔曼滤波失败: {str(e)}", exc_info=True)
            result.status = "failed"
            result.error_message = str(e)
            result.completed_at = datetime.now()
            return result

    def _apply_kalman_filter(self, points: List) -> List[Dict]:
        """对一组轨迹点应用卡尔曼滤波"""
        kf = KalmanFilter(dim_x=6, dim_z=3)

        # 初始状态
        dt = 1.0
        kf.F = np.array([
            [1, 0, 0, dt, 0, 0],
            [0, 1, 0, 0, dt, 0],
            [0, 0, 1, 0, 0, dt],
            [0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 1],
        ])

        kf.H = np.array([
            [1, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0],
        ])

        kf.Q = np.eye(6) * self.config.process_noise
        kf.R = np.eye(3) * self.config.measurement_noise
        kf.P = np.eye(6) * self.config.initial_uncertainty

        # 初始化
        first = points[0]
        kf.x = np.array([
            first.latitude, first.longitude, first.altitude or 0,
            0, 0, 0
        ]).reshape(6, 1)

        results = []
        for i, point in enumerate(points):
            if i > 0:
                # 计算实际时间间隔
                dt_actual = (point.timestamp - points[i-1].timestamp).total_seconds()
                dt_actual = max(dt_actual, 0.1)

                kf.F = np.array([
                    [1, 0, 0, dt_actual, 0, 0],
                    [0, 1, 0, 0, dt_actual, 0],
                    [0, 0, 1, 0, 0, dt_actual],
                    [0, 0, 0, 1, 0, 0],
                    [0, 0, 0, 0, 1, 0],
                    [0, 0, 0, 0, 0, 1],
                ])

                kf.predict()

            measurement = np.array([
                point.latitude, point.longitude, point.altitude or 0
            ])
            kf.update(measurement)

            results.append({
                "batch_id": point.batch_id,
                "station_id": point.radar_station_id,
                "timestamp": point.timestamp.isoformat() if point.timestamp else None,
                "latitude": float(kf.x[0, 0]),
                "longitude": float(kf.x[1, 0]),
                "altitude": float(kf.x[2, 0]),
                "orig_lat": point.latitude,
                "orig_lon": point.longitude,
                "orig_alt": point.altitude or 0,
                "covariance_trace": float(np.trace(kf.P)),
                "is_original": 0,
            })

        return results

    @staticmethod
    def get_default_config() -> KalmanAlgorithmConfig:
        return KalmanAlgorithmConfig()

    @staticmethod
    def get_config_class():
        return KalmanAlgorithmConfig

    def get_config_schema(self) -> Dict[str, Any]:
        return KalmanAlgorithmConfig.model_json_schema()

    def get_config_preset_profiles(self) -> Dict[str, KalmanAlgorithmConfig]:
        return {
            "standard": KalmanAlgorithmConfig(),
            "smooth": KalmanAlgorithmConfig(
                process_noise=0.01,
                measurement_noise=5.0,
            ),
            "responsive": KalmanAlgorithmConfig(
                process_noise=1.0,
                measurement_noise=0.1,
            ),
        }
