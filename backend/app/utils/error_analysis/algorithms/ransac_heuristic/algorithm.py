"""
启发式 RANSAC 算法实现

通过启发式方法识别故障雷达站：
1. 计算每个匹配组的几何中心
2. 计算每个站与中心的偏差
3. 按偏差排序，检测差值突变点
4. 突变点之前是健康站，之后是故障站
5. 用健康站数据计算最终系统误差
"""
import numpy as np
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from collections import defaultdict

from app.utils.error_analysis.base import (
    BaseErrorAnalysisAlgorithm,
    AnalysisResult,
    ProgressCallback,
)
from app.utils.error_analysis.algorithms.ransac_heuristic.config import (
    RansacHeuristicAlgorithmConfig,
)
from app.utils.mrra.config import MrraConfig, CostWeights
from app.utils.mrra.track_extractor import load_track_points_by_track_ids, extract_key_tracks
from app.utils.mrra.track_interpolator import interpolate_and_save_tracks
from app.utils.mrra.track_matcher import match_tracks_from_database, save_matched_groups
from app.utils.mrra.error_calculator import ErrorCalculator
from app.models.flight_track import RadarStation, FlightTrackRaw
from sqlalchemy.orm import Session
from core.logging import get_logger

logger = get_logger(__name__)


class RansacHeuristicAlgorithm(BaseErrorAnalysisAlgorithm):
    """
    启发式 RANSAC 算法

    与传统 RANSAC 不同，不使用随机采样：
    - 计算每个站与几何中心的偏差
    - 按偏差排序后检测突变点
    - 突变点之前是健康站，之后是故障站
    """

    ALGORITHM_NAME = "ransac_heuristic"
    ALGORITHM_VERSION = "1.0.0"
    ALGORITHM_DISPLAY_NAME = "启发式 RANSAC 算法"
    ALGORITHM_DESCRIPTION = (
        "通过启发式方法（偏差排序 + 差值突变检测）从多雷达匹配组中识别故障雷达站，"
        "然后基于健康站数据计算各站的系统误差。"
    )

    ConfigClass = RansacHeuristicAlgorithmConfig

    def __init__(self, config: RansacHeuristicAlgorithmConfig):
        super().__init__(config)

    def _validate_config(self):
        if not isinstance(self.config, RansacHeuristicAlgorithmConfig):
            raise ValueError("配置必须是 RansacHeuristicAlgorithmConfig 类型")

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

            # 构建 MRRA 兼容配置
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

            # 步骤4: 启发式 RANSAC 分析
            if progress_callback:
                progress_callback.on_progress(0.7, "启发式 RANSAC 故障站检测")
            self._update_task_progress(db_session, task_id, 80, "启发式 RANSAC 分析中")

            heuristic_results = self._heuristic_ransac(matched_groups, radar_positions)

            result.progress = 1.0

            # 完成
            result.status = "completed"
            result.errors = heuristic_results["errors"]
            result.completed_at = datetime.now()
            result.processing_time_seconds = (
                result.completed_at - start_time
            ).total_seconds()
            result.match_statistics = {
                "total_match_groups": len(matched_groups),
                "station_outlier_rates": heuristic_results["outlier_rates"],
                "fault_stations": heuristic_results["fault_stations"],
                "healthy_stations": heuristic_results["healthy_stations"],
            }
            result.metadata = {
                "algorithm": "ransac_heuristic",
                "jump_threshold": self.config.jump_threshold,
                "min_healthy_stations": self.config.min_healthy_stations,
                "outlier_ratio_threshold": self.config.outlier_ratio_threshold,
            }

            logger.info(
                f"[{task_id}] 启发式 RANSAC 分析完成，耗时 {result.processing_time_seconds:.2f} 秒，"
                f"健康站: {heuristic_results['healthy_stations']}, 故障站: {heuristic_results['fault_stations']}"
            )

            return result

        except Exception as e:
            logger.error(f"[{task_id}] 启发式 RANSAC 分析失败: {str(e)}", exc_info=True)
            result.status = "failed"
            result.error_message = str(e)
            result.completed_at = datetime.now()
            if progress_callback:
                progress_callback.on_error(str(e))
            return result

    def _build_mrra_config(self) -> MrraConfig:
        """将配置转换为 MRRA 兼容配置"""
        if self.config.cost_weights:
            cost_weights = CostWeights(
                variance=self.config.cost_weights.variance,
                azimuth_error_square=self.config.cost_weights.azimuth_error_square,
                range_error_square=self.config.cost_weights.range_error_square,
                elevation_error_square=self.config.cost_weights.elevation_error_square,
            )
        else:
            cost_weights = CostWeights()
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

    def _heuristic_ransac(
        self,
        matched_groups: List[List[Dict]],
        radar_positions: Dict[int, Tuple],
    ) -> Dict[str, Any]:
        """
        启发式 RANSAC 分析

        对每个匹配组：
        1. 计算几何中心
        2. 计算每个站与中心的偏差
        3. 按偏差排序，检测差值突变点
        4. 突变点之前是健康站，之后是故障站
        """
        # 统计每个站在所有匹配组中的故障判定次数
        station_total = defaultdict(int)
        station_outlier_count = defaultdict(int)

        # 健康站的所有匹配组数据
        healthy_groups = []

        for group in matched_groups:
            if len(group) < 2:
                continue

            # 计算几何中心（简单平均）
            lats = np.array([p["latitude"] for p in group])
            lons = np.array([p["longitude"] for p in group])
            center_lat = np.mean(lats)
            center_lon = np.mean(lons)

            # 计算每个站与中心的偏差（欧氏距离）
            station_deviations = []
            for i, point in enumerate(group):
                sid = point["station_id"]
                lat = point["latitude"]
                lon = point["longitude"]
                deviation = np.sqrt((lat - center_lat)**2 + (lon - center_lon)**2)
                station_deviations.append((sid, deviation))
                station_total[sid] += 1

            # 按偏差从小到大排序
            station_deviations.sort(key=lambda x: x[1])

            # 检测差值突变点
            healthy_stations_in_group, faulty_stations_in_group = self._detect_jump_point(
                station_deviations
            )

            # 统计故障站
            for sid in faulty_stations_in_group:
                station_outlier_count[sid] += 1

            # 收集健康站的数据
            healthy_sids = set(sid for sid, _ in healthy_stations_in_group)
            if healthy_sids:
                healthy_group = [p for p in group if p["station_id"] in healthy_sids]
                if len(healthy_group) >= 2:
                    healthy_groups.append(healthy_group)

        # 计算离群率
        outlier_rates = {}
        fault_stations = []
        healthy_stations_list = []

        for sid in station_total:
            rate = station_outlier_count[sid] / station_total[sid]
            outlier_rates[sid] = round(rate, 4)
            if rate >= self.config.outlier_ratio_threshold:
                fault_stations.append(sid)
            else:
                healthy_stations_list.append(sid)

        # 用健康站数据计算系统误差
        mrra_config = self._build_mrra_config()
        error_calc = ErrorCalculator(mrra_config)

        # 如果有足够的健康组，用健康数据计算误差
        if healthy_groups:
            station_errors = error_calc.calculate_radar_errors(healthy_groups, radar_positions)
        else:
            # 兜底：用所有数据计算误差
            station_errors = error_calc.calculate_radar_errors(matched_groups, radar_positions)

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
            "healthy_stations": healthy_stations_list,
        }

    def _detect_jump_point(
        self,
        station_deviations: List[Tuple[int, float]]
    ) -> Tuple[List[Tuple[int, float]], List[Tuple[int, float]]]:
        """
        检测差值突变点

        Args:
            station_deviations: [(station_id, deviation), ...]，已按偏差从小到大排序

        Returns:
            (healthy_stations, faulty_stations): 健康站和故障站列表
        """
        n = len(station_deviations)
        if n < 2:
            return station_deviations, []

        # 确保至少有 min_healthy_stations 个健康站
        healthy_count = self.config.min_healthy_stations

        # 计算相邻偏差的差值
        jumps = []
        for i in range(n - 1):
            sid1, dev1 = station_deviations[i]
            sid2, dev2 = station_deviations[i + 1]
            jump = dev2 - dev1
            jumps.append((i + 1, jump, sid2, dev2))

        # 找到最大差值的位置
        if jumps:
            max_jump_idx, max_jump, _, _ = max(jumps, key=lambda x: x[1])

            # 如果最大差值超过阈值，则在突变点分割
            if max_jump > self.config.jump_threshold:
                healthy_count = max(healthy_count, max_jump_idx)

        # 取前 healthy_count 个为健康站
        healthy_stations = station_deviations[:healthy_count]
        faulty_stations = station_deviations[healthy_count:]

        return healthy_stations, faulty_stations

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
    def get_default_config() -> RansacHeuristicAlgorithmConfig:
        return RansacHeuristicAlgorithmConfig()

    @staticmethod
    def get_config_class():
        return RansacHeuristicAlgorithmConfig

    def get_config_schema(self) -> Dict[str, Any]:
        return RansacHeuristicAlgorithmConfig.model_json_schema()

    def get_config_preset_profiles(self) -> Dict[str, RansacHeuristicAlgorithmConfig]:
        return {
            "standard": RansacHeuristicAlgorithmConfig(),
            "strict": RansacHeuristicAlgorithmConfig(
                jump_threshold=0.005,
                min_healthy_stations=3,
                outlier_ratio_threshold=0.3,
            ),
            "loose": RansacHeuristicAlgorithmConfig(
                jump_threshold=0.02,
                min_healthy_stations=2,
                outlier_ratio_threshold=0.7,
            ),
        }
