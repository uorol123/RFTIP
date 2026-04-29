"""
加权最小二乘融合算法实现

算法流程：
1. 复用 MRRA 的航迹提取、插值、匹配流程获取匹配组
2. 对每个匹配组，计算各站观测与组质心的偏差
3. 根据偏差计算各站权重（反方差 / 均匀 / 按匹配数）
4. 可选移除离群观测（3-sigma 准则）
5. 加权融合得到"真实位置"估计
6. 计算各站系统误差（方位角、距离、俯仰角）
7. 输出融合轨迹
"""
import math
import numpy as np
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from collections import defaultdict

from app.algorithms.base import (
    BaseErrorAnalysisAlgorithm,
    AnalysisResult,
    ProgressCallback,
)
from app.algorithms.multi_source.weighted_lstsq.config import WeightedLstsqAlgorithmConfig, WeightedLstsqCostWeights
from app.algorithms.multi_source.preprocessing.config import MrraConfig
from app.algorithms.multi_source.preprocessing.track_extractor import load_track_points_by_track_ids, extract_key_tracks
from app.algorithms.multi_source.preprocessing.track_interpolator import interpolate_and_save_tracks
from app.algorithms.multi_source.preprocessing.track_matcher import match_tracks_from_database, save_matched_groups
from app.algorithms.multi_source.preprocessing.error_calculator import ErrorCalculator
from app.models.flight_track import RadarStation, FlightTrackRaw
from sqlalchemy.orm import Session
from core.logging import get_logger

logger = get_logger(__name__)


class WeightedLstsqAlgorithm(BaseErrorAnalysisAlgorithm):
    """
    加权最小二乘融合算法

    根据各雷达站的可靠性权重融合多站观测，
    计算系统误差并输出优化轨迹。
    """

    ALGORITHM_NAME = "weighted_lstsq"
    ALGORITHM_VERSION = "1.0.0"
    ALGORITHM_DISPLAY_NAME = "加权最小二乘融合算法"
    ALGORITHM_DESCRIPTION = (
        "综合多雷达观测数据，根据各站可靠性权重进行加权融合，"
        "输出最优估计轨迹及各站系统误差。支持反方差、均匀、按匹配数等多种权重策略。"
    )

    ConfigClass = WeightedLstsqAlgorithmConfig

    def __init__(self, config: WeightedLstsqAlgorithmConfig):
        super().__init__(config)

    def _validate_config(self):
        if not isinstance(self.config, WeightedLstsqAlgorithmConfig):
            raise ValueError("配置必须是 WeightedLstsqAlgorithmConfig 类型")

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

            # 步骤4: 加权融合（核心步骤）
            if progress_callback:
                progress_callback.on_progress(0.7, "加权最小二乘融合")
            self._update_task_progress(db_session, task_id, 80, "加权融合中")

            fusion_results = self._weighted_fusion(matched_groups, radar_positions)

            result.progress = 1.0

            # 完成
            result.status = "completed"
            result.errors = fusion_results["errors"]
            result.completed_at = datetime.now()
            result.processing_time_seconds = (
                result.completed_at - start_time
            ).total_seconds()
            result.match_statistics = {
                "total_match_groups": len(matched_groups),
                "fusion_points": len(fusion_results["fused_trajectory"]),
                "station_weights": fusion_results["station_weights"],
                "weighting_method": self.config.weighting_method,
                "outlier_removed": fusion_results["outlier_removed_count"],
            }
            result.metadata = {
                "algorithm": "weighted_lstsq",
                "weighting_method": self.config.weighting_method,
                "outlier_removal": self.config.outlier_removal,
                "fused_trajectory": fusion_results["fused_trajectory"][:100],
            }

            logger.info(
                f"[{task_id}] 加权融合完成，耗时 {result.processing_time_seconds:.2f} 秒，"
                f"融合轨迹点: {len(fusion_results['fused_trajectory'])}"
            )

            return result

        except Exception as e:
            logger.error(f"[{task_id}] 加权融合失败: {str(e)}", exc_info=True)
            result.status = "failed"
            result.error_message = str(e)
            result.completed_at = datetime.now()
            if progress_callback:
                progress_callback.on_error(str(e))
            return result

    def _build_mrra_config(self) -> MrraConfig:
        # 如果 cost_weights 为 None，使用默认值
        weights = self.config.cost_weights or WeightedLstsqCostWeights()
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

    def _weighted_fusion(
        self,
        matched_groups: List[List[Dict]],
        radar_positions: Dict[int, Tuple],
    ) -> Dict[str, Any]:
        """
        加权最小二乘融合

        1. 计算各站观测方差，确定权重
        2. 可选移除离群观测
        3. 加权融合得到各时间点的真实位置
        4. 用 ErrorCalculator 计算系统误差
        """
        # 阶段1：计算各站的观测偏差统计量
        station_deviations = defaultdict(list)
        station_match_count = defaultdict(int)

        for group in matched_groups:
            if len(group) < 2:
                continue

            # 计算组质心
            lats = [p["latitude"] for p in group]
            lons = [p["longitude"] for p in group]
            centroid_lat = np.mean(lats)
            centroid_lon = np.mean(lons)

            for point in group:
                sid = point["station_id"]
                station_match_count[sid] += 1
                # 计算该观测到质心的距离（度）
                dev = math.sqrt(
                    (point["latitude"] - centroid_lat) ** 2
                    + (point["longitude"] - centroid_lon) ** 2
                )
                station_deviations[sid].append(dev)

        # 阶段2：计算各站权重
        station_weights = {}
        for sid in radar_positions:
            if sid not in station_deviations or len(station_deviations[sid]) == 0:
                station_weights[sid] = 1.0
                continue

            devs = np.array(station_deviations[sid])
            variance = np.var(devs) if len(devs) > 1 else 1.0

            if self.config.weighting_method == "inverse_variance":
                station_weights[sid] = 1.0 / (variance + 1e-10)
            elif self.config.weighting_method == "match_count":
                station_weights[sid] = float(station_match_count.get(sid, 1))
            else:
                station_weights[sid] = 1.0

        # 归一化权重
        total_weight = sum(station_weights.values())
        if total_weight > 0:
            station_weights = {k: v / total_weight for k, v in station_weights.items()}

        # 阶段3：离群点移除（可选）
        outlier_removed_count = 0
        filtered_groups = []

        if self.config.outlier_removal:
            for group in matched_groups:
                if len(group) < 3:
                    filtered_groups.append(group)
                    continue

                lats = np.array([p["latitude"] for p in group])
                lons = np.array([p["longitude"] for p in group])
                centroid_lat = np.mean(lats)
                centroid_lon = np.mean(lons)

                distances = np.sqrt(
                    (lats - centroid_lat) ** 2 + (lons - centroid_lon) ** 2
                )
                mean_dist = np.mean(distances)
                std_dist = np.std(distances) if len(distances) > 1 else 0.0

                filtered = []
                for i, point in enumerate(group):
                    if std_dist > 0 and distances[i] > mean_dist + 3 * std_dist:
                        outlier_removed_count += 1
                    else:
                        filtered.append(point)

                filtered_groups.append(filtered if filtered else group)
        else:
            filtered_groups = matched_groups

        # 阶段4：加权融合轨迹
        fused_trajectory = []
        for group in filtered_groups:
            if not group:
                continue

            total_w = 0.0
            w_lat = 0.0
            w_lon = 0.0
            w_alt = 0.0

            for point in group:
                sid = point["station_id"]
                w = station_weights.get(sid, 1.0 / len(radar_positions))
                w_lat += w * point["latitude"]
                w_lon += w * point["longitude"]
                w_alt += w * (point.get("altitude", 0.0) or 0.0)
                total_w += w

            if total_w > 0:
                fused_point = {
                    "latitude": w_lat / total_w,
                    "longitude": w_lon / total_w,
                    "altitude": w_alt / total_w,
                    "match_group_size": len(group),
                }

                if group:
                    fused_point["time_seconds"] = group[0].get("time_seconds", 0.0)
                    fused_point["station_ids"] = [p["station_id"] for p in group]

                fused_trajectory.append(fused_point)

        # 阶段5：用 ErrorCalculator 计算系统误差
        mrra_config = self._build_mrra_config()
        error_calc = ErrorCalculator(mrra_config)

        opt_az, opt_r, opt_elev = error_calc.optimize_station_errors_separately(
            filtered_groups,
            {sid: 0.0 for sid in radar_positions},
            radar_positions,
        )

        errors = {}
        for sid in radar_positions:
            errors[sid] = {
                "azimuth_error": opt_az.get(sid, 0.0),
                "range_error": opt_r.get(sid, 0.0),
                "elevation_error": opt_elev.get(sid, 0.0),
            }

        return {
            "errors": errors,
            "station_weights": {str(k): round(v, 6) for k, v in station_weights.items()},
            "fused_trajectory": fused_trajectory,
            "outlier_removed_count": outlier_removed_count,
        }

    def _update_task_progress(
        self, db: Session, task_id: str, progress: int, message: str
    ):
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
    def get_default_config() -> WeightedLstsqAlgorithmConfig:
        return WeightedLstsqAlgorithmConfig()

    @staticmethod
    def get_config_class():
        return WeightedLstsqAlgorithmConfig

    def get_config_schema(self) -> Dict[str, Any]:
        return WeightedLstsqAlgorithmConfig.model_json_schema()

    def get_config_preset_profiles(self) -> Dict[str, WeightedLstsqAlgorithmConfig]:
        return {
            "standard": WeightedLstsqAlgorithmConfig(),
            "inverse_variance": WeightedLstsqAlgorithmConfig(
                weighting_method="inverse_variance",
                outlier_removal=True,
            ),
            "uniform": WeightedLstsqAlgorithmConfig(
                weighting_method="uniform",
                outlier_removal=False,
            ),
            "robust": WeightedLstsqAlgorithmConfig(
                weighting_method="inverse_variance",
                outlier_removal=True,
                optimization_steps=[0.05, 0.01, 0.005],
            ),
        }
