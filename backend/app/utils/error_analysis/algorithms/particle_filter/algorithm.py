"""
粒子滤波算法实现

状态空间: [lat, lon, alt, v_lat, v_lon, v_alt]
使用系统重采样策略
"""
import numpy as np
from typing import List, Optional, Dict, Any
from datetime import datetime
from collections import defaultdict

from app.utils.error_analysis.base import (
    BaseErrorAnalysisAlgorithm,
    AnalysisResult,
    ProgressCallback,
)
from app.utils.error_analysis.algorithms.particle_filter.config import ParticleFilterAlgorithmConfig
from app.models.flight_track import FlightTrackRaw
from sqlalchemy.orm import Session
from core.logging import get_logger

logger = get_logger(__name__)


class ParticleFilterAlgorithm(BaseErrorAnalysisAlgorithm):
    """
    粒子滤波算法

    处理非线性非高斯噪声场景，对单站轨迹进行平滑
    """

    ALGORITHM_NAME = "particle_filter"
    ALGORITHM_VERSION = "1.0.0"
    ALGORITHM_DISPLAY_NAME = "粒子滤波算法"
    ALGORITHM_DESCRIPTION = (
        "基于蒙特卡洛方法的粒子滤波，适用于非线性非高斯噪声场景，"
        "通过大量粒子模拟状态分布，输出加权平均后的平滑轨迹。"
    )

    ConfigClass = ParticleFilterAlgorithmConfig

    def __init__(self, config: ParticleFilterAlgorithmConfig):
        super().__init__(config)

    def _validate_config(self):
        if not isinstance(self.config, ParticleFilterAlgorithmConfig):
            raise ValueError("配置必须是 ParticleFilterAlgorithmConfig 类型")

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
                    progress_callback.on_progress(progress, f"粒子滤波: {batch_id}")

                smoothed = self._apply_particle_filter(group)
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
                "num_particles": self.config.num_particles,
            }
            result.metadata = {
                "algorithm": "particle_filter",
                "smoothed_trajectory": smoothed_all[:500],
                "total_points": len(smoothed_all),
            }

            logger.info(f"[{task_id}] 粒子滤波完成，处理 {len(smoothed_all)} 个点")
            return result

        except Exception as e:
            logger.error(f"[{task_id}] 粒子滤波失败: {str(e)}", exc_info=True)
            result.status = "failed"
            result.error_message = str(e)
            result.completed_at = datetime.now()
            return result

    def _apply_particle_filter(self, points: List) -> List[Dict]:
        """对一组轨迹点应用粒子滤波"""
        N = self.config.num_particles
        dim = 6  # [lat, lon, alt, v_lat, v_lon, v_alt]

        # 初始化粒子
        first = points[0]
        particles = np.zeros((N, dim))
        particles[:, 0] = first.latitude + np.random.normal(0, self.config.process_noise_std, N)
        particles[:, 1] = first.longitude + np.random.normal(0, self.config.process_noise_std, N)
        particles[:, 2] = (first.altitude or 0) + np.random.normal(0, self.config.process_noise_std * 100, N)
        particles[:, 3:6] = 0.0

        weights = np.ones(N) / N

        results = []
        for i, point in enumerate(points):
            if i > 0:
                dt = (point.timestamp - points[i-1].timestamp).total_seconds()
                dt = max(dt, 0.1)

                # 预测（匀速模型 + 过程噪声）
                particles[:, 0] += particles[:, 3] * dt + np.random.normal(0, self.config.process_noise_std, N)
                particles[:, 1] += particles[:, 4] * dt + np.random.normal(0, self.config.process_noise_std, N)
                particles[:, 2] += particles[:, 5] * dt + np.random.normal(0, self.config.process_noise_std * 100, N)

                # 速度也加小噪声
                particles[:, 3] += np.random.normal(0, self.config.process_noise_std * 0.1, N)
                particles[:, 4] += np.random.normal(0, self.config.process_noise_std * 0.1, N)
                particles[:, 5] += np.random.normal(0, self.config.process_noise_std * 10, N)

            # 更新权重（高斯似然）
            obs = np.array([point.latitude, point.longitude, point.altitude or 0])
            diff = particles[:, :3] - obs
            dist_sq = np.sum(diff ** 2, axis=1)
            weights = np.exp(-dist_sq / (2 * self.config.measurement_noise_std ** 2))
            weights += 1e-300
            weights /= weights.sum()

            # 估计状态（加权平均）
            state = np.average(particles, weights=weights, axis=0)

            # 有效粒子数检查
            n_eff = 1.0 / np.sum(weights ** 2)
            if n_eff < N * self.config.effective_particle_threshold:
                particles = self._resample(particles, weights)
                weights = np.ones(N) / N

            results.append({
                "batch_id": point.batch_id,
                "station_id": point.radar_station_id,
                "timestamp": point.timestamp.isoformat() if point.timestamp else None,
                "latitude": float(state[0]),
                "longitude": float(state[1]),
                "altitude": float(state[2]),
                "orig_lat": point.latitude,
                "orig_lon": point.longitude,
                "orig_alt": point.altitude or 0,
                "effective_particles": float(n_eff),
            })

        return results

    def _resample(self, particles: np.ndarray, weights: np.ndarray) -> np.ndarray:
        """系统重采样"""
        N = len(weights)
        indices = np.zeros(N, dtype=int)

        if self.config.resampling_method == "systematic":
            positions = (np.arange(N) + np.random.uniform()) / N
        else:
            positions = np.random.uniform(0, 1, N)

        cumsum = np.cumsum(weights)
        i, j = 0, 0
        while i < N:
            if positions[i] < cumsum[j]:
                indices[i] = j
                i += 1
            else:
                j += 1

        return particles[indices].copy()

    @staticmethod
    def get_default_config() -> ParticleFilterAlgorithmConfig:
        return ParticleFilterAlgorithmConfig()

    @staticmethod
    def get_config_class():
        return ParticleFilterAlgorithmConfig

    def get_config_schema(self) -> Dict[str, Any]:
        return ParticleFilterAlgorithmConfig.model_json_schema()

    def get_config_preset_profiles(self) -> Dict[str, ParticleFilterAlgorithmConfig]:
        return {
            "standard": ParticleFilterAlgorithmConfig(),
            "high_precision": ParticleFilterAlgorithmConfig(
                num_particles=5000,
                process_noise_std=0.0005,
                measurement_noise_std=0.005,
            ),
            "fast": ParticleFilterAlgorithmConfig(
                num_particles=200,
                process_noise_std=0.005,
                measurement_noise_std=0.05,
            ),
        }
