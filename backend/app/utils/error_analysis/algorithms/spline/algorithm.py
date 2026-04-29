"""
样条平滑算法实现

使用 scipy.interpolate.UnivariateSpline 对经度、纬度、高度分别平滑
"""
import numpy as np
from scipy.interpolate import UnivariateSpline
from typing import List, Optional, Dict, Any
from datetime import datetime
from collections import defaultdict

from app.utils.error_analysis.base import (
    BaseErrorAnalysisAlgorithm,
    AnalysisResult,
    ProgressCallback,
)
from app.utils.error_analysis.algorithms.spline.config import SplineAlgorithmConfig
from app.models.flight_track import FlightTrackRaw
from sqlalchemy.orm import Session
from core.logging import get_logger

logger = get_logger(__name__)


class SplineAlgorithm(BaseErrorAnalysisAlgorithm):
    """
    样条平滑算法

    对单站轨迹进行连续平滑处理，获得平滑曲线
    """

    ALGORITHM_NAME = "spline"
    ALGORITHM_VERSION = "1.0.0"
    ALGORITHM_DISPLAY_NAME = "样条平滑算法"
    ALGORITHM_DESCRIPTION = (
        "使用样条插值对单站轨迹进行平滑处理，获得连续平滑的轨迹曲线，"
        "可有效去除高频噪声，保留轨迹的整体趋势。"
    )

    ConfigClass = SplineAlgorithmConfig

    def __init__(self, config: SplineAlgorithmConfig):
        super().__init__(config)

    def _validate_config(self):
        if not isinstance(self.config, SplineAlgorithmConfig):
            raise ValueError("配置必须是 SplineAlgorithmConfig 类型")

    @classmethod
    def supports_elevation(cls) -> bool:
        return True

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
            if progress_callback:
                progress_callback.on_progress(0.1, "加载轨迹数据")

            tracks = db_session.query(FlightTrackRaw).filter(
                FlightTrackRaw.batch_id.in_(track_ids),
                FlightTrackRaw.radar_station_id.in_(radar_station_ids),
            ).order_by(FlightTrackRaw.timestamp).all()

            if not tracks:
                raise ValueError("没有找到指定的轨迹数据")

            track_groups = defaultdict(list)
            for t in tracks:
                track_groups[t.batch_id].append(t)

            total_tracks = len(track_groups)
            smoothed_all = []
            errors = {}
            track_idx = 0

            for batch_id, group in track_groups.items():
                group.sort(key=lambda t: t.timestamp)

                if len(group) < self.config.min_track_points:
                    track_idx += 1
                    continue

                if progress_callback:
                    progress = 0.1 + 0.8 * (track_idx / total_tracks)
                    progress_callback.on_progress(progress, f"样条平滑: {batch_id}")

                smoothed = self._apply_spline(group)
                smoothed_all.extend(smoothed)

                for point in smoothed:
                    sid = point["station_id"]
                    if sid not in errors:
                        errors[sid] = {"_count": 0, "_lat_diff_sq": 0.0, "_lon_diff_sq": 0.0, "_alt_diff_sq": 0.0,
                                       "azimuth_error": 0.0, "range_error": 0.0, "elevation_error": 0.0}
                    errors[sid]["_count"] += 1
                    errors[sid]["_lat_diff_sq"] += (point["orig_lat"] - point["latitude"]) ** 2
                    errors[sid]["_lon_diff_sq"] += (point["orig_lon"] - point["longitude"]) ** 2
                    if point.get("orig_alt") is not None:
                        errors[sid]["_alt_diff_sq"] += (point["orig_alt"] - point["altitude"]) ** 2

                track_idx += 1

            for sid in errors:
                n = errors[sid]["_count"]
                if n > 0:
                    errors[sid]["azimuth_error"] = round(np.sqrt(errors[sid]["_lat_diff_sq"] / n), 6)
                    errors[sid]["range_error"] = round(
                        np.sqrt(errors[sid]["_lat_diff_sq"] + errors[sid]["_lon_diff_sq"]) / n * 111000, 2
                    )
                    errors[sid]["elevation_error"] = round(np.sqrt(errors[sid]["_alt_diff_sq"] / n), 4)
                for k in ["_count", "_lat_diff_sq", "_lon_diff_sq", "_alt_diff_sq"]:
                    del errors[sid][k]

            result.progress = 1.0
            result.status = "completed"
            result.errors = errors
            result.completed_at = datetime.now()
            result.processing_time_seconds = (result.completed_at - start_time).total_seconds()
            result.match_statistics = {
                "total_tracks": total_tracks,
                "total_smoothed_points": len(smoothed_all),
                "smoothing_factor": self.config.smoothing_factor,
                "spline_degree": self.config.spline_degree,
            }
            result.metadata = {
                "algorithm": "spline",
                "smoothed_trajectory": smoothed_all[:500],
                "total_points": len(smoothed_all),
            }

            logger.info(f"[{task_id}] 样条平滑完成，处理 {len(smoothed_all)} 个点")
            return result

        except Exception as e:
            logger.error(f"[{task_id}] 样条平滑失败: {str(e)}", exc_info=True)
            result.status = "failed"
            result.error_message = str(e)
            result.completed_at = datetime.now()
            return result

    def _apply_spline(self, points: List) -> List[Dict]:
        """对一组轨迹点应用样条平滑"""
        n = len(points)

        # 时间轴（秒）
        t0 = points[0].timestamp
        t = np.array([(p.timestamp - t0).total_seconds() for p in points])

        lats = np.array([p.latitude for p in points])
        lons = np.array([p.longitude for p in points])
        alts = np.array([p.altitude or 0 for p in points], dtype=float)

        # 去除重复时间点
        unique_mask = np.diff(t, prepend=-1) > 0
        t_u = t[unique_mask]
        lats_u = lats[unique_mask]
        lons_u = lons[unique_mask]
        alts_u = alts[unique_mask]

        if len(t_u) < 4:
            # 点太少，直接返回原始数据
            return [
                {
                    "batch_id": p.batch_id,
                    "station_id": p.radar_station_id,
                    "timestamp": p.timestamp.isoformat(),
                    "latitude": p.latitude,
                    "longitude": p.longitude,
                    "altitude": p.altitude or 0,
                    "orig_lat": p.latitude,
                    "orig_lon": p.longitude,
                    "orig_alt": p.altitude or 0,
                }
                for p in points
            ]

        degree = min(self.config.spline_degree, len(t_u) - 1)

        try:
            spl_lat = UnivariateSpline(t_u, lats_u, k=degree, s=self.config.smoothing_factor)
            spl_lon = UnivariateSpline(t_u, lons_u, k=degree, s=self.config.smoothing_factor)
            spl_alt = UnivariateSpline(t_u, alts_u, k=degree, s=self.config.smoothing_factor)
        except Exception:
            return [
                {
                    "batch_id": p.batch_id,
                    "station_id": p.radar_station_id,
                    "timestamp": p.timestamp.isoformat(),
                    "latitude": p.latitude,
                    "longitude": p.longitude,
                    "altitude": p.altitude or 0,
                    "orig_lat": p.latitude,
                    "orig_lon": p.longitude,
                    "orig_alt": p.altitude or 0,
                }
                for p in points
            ]

        results = []

        if self.config.interpolate:
            # 插值模式：在原始点之间插入额外点
            t_fine = np.linspace(t[0], t[-1], len(t) * self.config.interpolation_density)
            for ti in t_fine:
                results.append({
                    "batch_id": points[0].batch_id,
                    "station_id": points[0].radar_station_id,
                    "timestamp": None,
                    "time_offset": float(ti),
                    "latitude": float(spl_lat(ti)),
                    "longitude": float(spl_lon(ti)),
                    "altitude": float(spl_alt(ti)),
                    "orig_lat": float(spl_lat(ti)),
                    "orig_lon": float(spl_lon(ti)),
                    "orig_alt": float(spl_alt(ti)),
                    "is_interpolated": 1,
                })
        else:
            # 仅平滑模式：在原始时间点评估样条
            for i, point in enumerate(points):
                ti = t[i]
                results.append({
                    "batch_id": point.batch_id,
                    "station_id": point.radar_station_id,
                    "timestamp": point.timestamp.isoformat(),
                    "latitude": float(spl_lat(ti)),
                    "longitude": float(spl_lon(ti)),
                    "altitude": float(spl_alt(ti)),
                    "orig_lat": point.latitude,
                    "orig_lon": point.longitude,
                    "orig_alt": point.altitude or 0,
                })

        return results

    @staticmethod
    def get_default_config() -> SplineAlgorithmConfig:
        return SplineAlgorithmConfig()

    @staticmethod
    def get_config_class():
        return SplineAlgorithmConfig

    def get_config_schema(self) -> Dict[str, Any]:
        return SplineAlgorithmConfig.model_json_schema()

    def get_config_preset_profiles(self) -> Dict[str, SplineAlgorithmConfig]:
        return {
            "standard": SplineAlgorithmConfig(),
            "smooth": SplineAlgorithmConfig(
                smoothing_factor=1.0,
                spline_degree=3,
            ),
            "tight": SplineAlgorithmConfig(
                smoothing_factor=0.01,
                spline_degree=3,
            ),
            "interpolated": SplineAlgorithmConfig(
                smoothing_factor=0.1,
                spline_degree=3,
                interpolate=True,
                interpolation_density=10,
            ),
        }
