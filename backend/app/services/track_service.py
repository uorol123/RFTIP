"""
轨迹处理服务 - 实现轨迹数据处理和修正算法

架构设计：
1. 预处理管道：TrackPreprocessor 基于参考文档实现
2. 算法接口：可扩展的修正算法接口
3. 数据模型：统一的轨迹数据模型

参考文档：docs/参考.md (MRRA 雷达误差分析方法)
"""
import json
import math
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Optional, Tuple, Dict, Protocol
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from sklearn.linear_model import RANSACRegressor
from filterpy.kalman import KalmanFilter

from app.models.flight_track import FlightTrackRaw, FlightTrackCorrected
from app.schemas.track import TrackProcessRequest, TrackProcessResponse


# ============================================================================
# 配置常量
# ============================================================================

class PreprocessingConfig:
    """预处理配置（基于参考文档和数据分析）"""

    # 时间窗口（秒）
    TIME_WINDOW_MATCH = 1.0  # 同时观测时间窗口
    TIME_WINDOW_EXTRACTION = 60  # 关键航迹提取时间窗口

    # 空间参数（度）
    GRID_RESOLUTION = 0.2  # 空间网格分辨率（约22km）
    POSITION_THRESHOLD = 0.12  # 位置匹配阈值（约13.3km）

    # 轨迹质量参数
    MIN_DURATION = 45  # 最短持续时间（秒）
    MIN_POINTS = 10  # 最小航迹点数
    MAX_TIME_GAP = 100  # 最大时间间隔（秒）

    # 速度阈值（用于噪音过滤，从位置计算）
    MAX_SPEED_KMH = 800  # 最大合理速度
    MIN_SPEED_KMH = 50   # 最小合理速度


# ============================================================================
# 工具函数
# ============================================================================

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """计算两点之间的球面距离（米）"""
    R = 6371000
    lat1_rad, lat2_rad = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (math.sin(dlat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) *
         math.sin(dlon / 2) ** 2)

    return R * 2 * math.asin(math.sqrt(a))


def calculate_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """计算从点1到点2的方位角（度）"""
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlon = math.radians(lon2 - lon1)

    y = math.sin(dlon) * math.cos(lat2_rad)
    x = (math.cos(lat1_rad) * math.sin(lat2_rad) -
         math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon))

    bearing = math.atan2(y, x)
    return (math.degrees(bearing) + 360) % 360


def calculate_velocity(
    point1: Dict,
    point2: Dict
) -> Tuple[float, float, float]:
    """
    从位置数据计算速度和航向

    Returns:
        (速度_mps, 速度_kmh, 航向度)
    """
    distance = haversine_distance(
        point1['latitude'], point1['longitude'],
        point2['latitude'], point2['longitude']
    )

    time_diff = (point2['timestamp'] - point1['timestamp']).total_seconds()

    if time_diff == 0:
        return 0, 0, 0

    speed_mps = distance / time_diff
    speed_kmh = speed_mps * 3.6

    heading = calculate_bearing(
        point1['latitude'], point1['longitude'],
        point2['latitude'], point2['longitude']
    )

    return speed_mps, speed_kmh, heading


# ============================================================================
# 算法接口定义
# ============================================================================

class TrackCorrectionAlgorithm(ABC):
    """轨迹修正算法接口"""

    @abstractmethod
    def get_name(self) -> str:
        """获取算法名称"""
        pass

    @abstractmethod
    def get_parameters(self) -> Dict:
        """获取算法参数"""
        pass

    @abstractmethod
    def set_parameters(self, params: Dict):
        """设置算法参数"""
        pass

    @abstractmethod
    def correct(
        self,
        observations: List[Dict]
    ) -> Dict:
        """
        执行修正算法

        Args:
            observations: 观测数据列表，每个包含:
                - latitude, longitude, altitude
                - timestamp (datetime)
                - radar_station_id
                - track_id
                - raw_data (原始数据)

        Returns:
            修正结果，包含:
                - corrected_observations: 修正后的观测列表
                - confidence_scores: 置信度列表
                - outlier_flags: 离群点标记列表
                - metadata: 算法元数据
        """
        pass


# ============================================================================
# 具体算法实现
# ============================================================================

class RANSACAlgorithm(TrackCorrectionAlgorithm):
    """RANSAC 多源修正算法"""

    def __init__(
        self,
        residual_threshold: float = 0.5,
        min_samples: int = 2,
        time_window: float = PreprocessingConfig.TIME_WINDOW_MATCH,
        position_threshold: float = PreprocessingConfig.POSITION_THRESHOLD
    ):
        self.residual_threshold = residual_threshold
        self.min_samples = min_samples
        self.time_window = time_window
        self.position_threshold = position_threshold

    def get_name(self) -> str:
        return "RANSAC"

    def get_parameters(self) -> Dict:
        return {
            'residual_threshold': self.residual_threshold,
            'min_samples': self.min_samples,
            'time_window': self.time_window,
            'position_threshold': self.position_threshold,
        }

    def set_parameters(self, params: Dict):
        self.residual_threshold = params.get('residual_threshold', self.residual_threshold)
        self.min_samples = params.get('min_samples', self.min_samples)
        self.time_window = params.get('time_window', self.time_window)
        self.position_threshold = params.get('position_threshold', self.position_threshold)

    def correct(self, observations: List[Dict]) -> Dict:
        """
        RANSAC 多源修正

        将相近时间 + 相近位置的观测分组，然后对每组应用 RANSAC
        """
        if len(observations) < self.min_samples:
            return self._return_observations(observations, confidence=0.5)

        # 按时间分组
        time_groups = self._group_by_time_window(observations)

        corrected_observations = []
        confidence_scores = []
        outlier_flags = []

        for group_obs in time_groups:
            if len(group_obs) < self.min_samples:
                # 数据不足，直接返回
                for obs in group_obs:
                    corrected_observations.append(obs)
                    confidence_scores.append(0.5)
                    outlier_flags.append(0)
            else:
                # 应用 RANSAC
                result = self._apply_ransac(group_obs)
                corrected_observations.extend(result['observations'])
                confidence_scores.extend(result['confidences'])
                outlier_flags.extend(result['outliers'])

        return {
            'corrected_observations': corrected_observations,
            'confidence_scores': confidence_scores,
            'outlier_flags': outlier_flags,
            'metadata': {
                'algorithm': self.get_name(),
                'parameters': self.get_parameters(),
                'time_groups': len(time_groups),
            }
        }

    def _group_by_time_window(self, observations: List[Dict]) -> List[List[Dict]]:
        """按时间窗口分组"""
        if not observations:
            return []

        # 按时间排序
        sorted_obs = sorted(observations, key=lambda o: o['timestamp'])

        groups = []
        current_group = [sorted_obs[0]]

        for obs in sorted_obs[1:]:
            time_diff = (obs['timestamp'] - current_group[0]['timestamp']).total_seconds()

            if time_diff <= self.time_window:
                current_group.append(obs)
            else:
                groups.append(current_group)
                current_group = [obs]

        if current_group:
            groups.append(current_group)

        return groups

    def _apply_ransac(self, observations: List[Dict]) -> Dict:
        """应用 RANSAC 算法"""
        positions = [(o['latitude'], o['longitude'], o.get('altitude', 0)) for o in observations]

        coords = np.array([(p[0], p[1]) for p in positions])

        ransac = RANSACRegressor(
            residual_threshold=self.residual_threshold,
            min_samples=self.min_samples,
        )

        try:
            lats = np.array([p[0] for p in positions]).reshape(-1, 1)
            lngs = np.array([p[1] for p in positions]).reshape(-1, 1)

            ransac.fit(lats, lngs)
            inlier_mask = ransac.inlier_mask_

            # 计算修正位置（内点平均）
            inliers = [positions[i] for i in range(len(positions)) if inlier_mask[i]]

            if inliers:
                corrected_lat = np.mean([p[0] for p in inliers])
                corrected_lng = np.mean([p[1] for p in inliers])
                corrected_alt = np.mean([p[2] for p in inliers if p[2] is not None] or 0])
                confidence = np.sum(inlier_mask) / len(inlier_mask)
            else:
                corrected_lat, corrected_lng, corrected_alt = None, None, None
                confidence = 0.0

            # 构建结果
            result_obs = []
            confidences = []
            outliers = []

            for i, obs in enumerate(observations):
                if corrected_lat is not None:
                    result_obs.append({
                        **obs,
                        'latitude': corrected_lat,
                        'longitude': corrected_lng,
                        'altitude': corrected_alt,
                    })
                    confidences.append(confidence)
                    outliers.append(0 if inlier_mask[i] else 1)
                else:
                    result_obs.append(obs)
                    confidences.append(0.0)
                    outliers.append(0)

            return {
                'observations': result_obs,
                'confidences': confidences,
                'outliers': outliers,
            }

        except Exception as e:
            # RANSAC 失败，返回原始数据
            return self._return_observations(observations, confidence=0.0, error=str(e))

    def _return_observations(
        self,
        observations: List[Dict],
        confidence: float = 0.5,
        error: str = None
    ) -> Dict:
        """返回原始观测数据"""
        return {
            'observations': observations,
            'confidences': [confidence] * len(observations),
            'outliers': [0] * len(observations),
            'metadata': {'error': error} if error else {},
        }


class KalmanFilterAlgorithm(TrackCorrectionAlgorithm):
    """卡尔曼滤波单源修正算法"""

    def __init__(
        self,
        process_noise: float = 0.1,
        measurement_noise: float = 1.0
    ):
        self.process_noise = process_noise
        self.measurement_noise = measurement_noise
        self.filters = {}  # 每条轨迹独立的滤波器

    def get_name(self) -> str:
        return "KalmanFilter"

    def get_parameters(self) -> Dict:
        return {
            'process_noise': self.process_noise,
            'measurement_noise': self.measurement_noise,
        }

    def set_parameters(self, params: Dict):
        self.process_noise = params.get('process_noise', self.process_noise)
        self.measurement_noise = params.get('measurement_noise', self.measurement_noise)

    def correct(self, observations: List[Dict]) -> Dict:
        """
        卡尔曼滤波修正

        对每条轨迹独立应用卡尔曼滤波
        """
        if not observations:
            return {
                'corrected_observations': [],
                'confidence_scores': [],
                'outlier_flags': [],
                'metadata': {'algorithm': self.get_name()},
            }

        # 按轨迹ID分组
        track_groups = {}
        for obs in observations:
            track_id = obs.get('track_id', 'unknown')
            if track_id not in track_groups:
                track_groups[track_id] = []
            track_groups[track_id].append(obs)

        corrected_observations = []
        confidence_scores = []
        outlier_flags = []

        for track_id, track_obs in track_groups.items():
            # 按时间排序
            track_obs = sorted(track_obs, key=lambda o: o['timestamp'])

            # 获取或创建滤波器
            if track_id not in self.filters:
                self.filters[track_id] = self._create_filter()

            kf = self.filters[track_id]

            for obs in track_obs:
                # 应用滤波
                measurement = (obs['latitude'], obs['longitude'], obs.get('altitude', 0))
                corrected_lat, corrected_lng, corrected_alt, confidence = self._filter_step(kf, measurement)

                corrected_observations.append({
                    **obs,
                    'latitude': corrected_lat,
                    'longitude': corrected_lng,
                    'altitude': corrected_alt,
                })
                confidence_scores.append(confidence)
                outlier_flags.append(0)

        return {
            'corrected_observations': corrected_observations,
            'confidence_scores': confidence_scores,
            'outlier_flags': outlier_flags,
            'metadata': {
                'algorithm': self.get_name(),
                'parameters': self.get_parameters(),
                'tracks_processed': len(track_groups),
            }
        }

    def _create_filter(self):
        """创建卡尔曼滤波器"""
        kf = KalmanFilter(dim_x=6, dim_z=3)

        # 状态转移矩阵 (匀速模型)
        dt = 1.0
        kf.F = np.array([
            [1, 0, 0, dt, 0, 0],
            [0, 1, 0, 0, dt, 0],
            [0, 0, 1, 0, 0, dt],
            [0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 1],
        ])

        # 测量矩阵
        kf.H = np.array([
            [1, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0],
        ])

        # 噪声协方差
        kf.Q = np.eye(6) * self.process_noise
        kf.R = np.eye(3) * self.measurement_noise

        return kf

    def _filter_step(
        self,
        kf: KalmanFilter,
        measurement: Tuple[float, float, float]
    ) -> Tuple[float, float, float, float]:
        """单步滤波"""
        if not hasattr(kf, 'initialized') or not kf.initialized:
            # 初始化
            initial_state = np.array([
                measurement[0], measurement[1], measurement[2], 0, 0, 0
            ])
            kf.x = initial_state.reshape(6, 1)
            kf.P = np.eye(6) * 100
            kf.initialized = True
            confidence = 0.5
        else:
            # 预测 + 更新
            kf.predict()
            kf.update(np.array(measurement))

            # 计算置信度
            confidence = 1.0 / (1.0 + np.trace(kf.P))

        corrected_lat = float(kf.x[0, 0])
        corrected_lng = float(kf.x[1, 0])
        corrected_alt = float(kf.x[2, 0])

        return corrected_lat, corrected_lng, corrected_alt, confidence


# ============================================================================
# 算法工厂
# ============================================================================

class AlgorithmFactory:
    """算法工厂，用于创建和获取算法实例"""

    _algorithms = {
        'ransac': RANSACAlgorithm,
        'kalman': KalmanFilterAlgorithm,
    }

    @classmethod
    def create_algorithm(
        cls,
        algorithm_name: str,
        **params
    ) -> TrackCorrectionAlgorithm:
        """创建算法实例"""
        if algorithm_name.lower() not in cls._algorithms:
            raise ValueError(f"不支持的算法: {algorithm_name}")

        algorithm_class = cls._algorithms[algorithm_name.lower()]
        return algorithm_class(**params)

    @classmethod
    def register_algorithm(cls, name: str, algorithm_class: type):
        """注册新算法（用于扩展）"""
        cls._algorithms[name.lower()] = algorithm_class

    @classmethod
    def list_algorithms(cls) -> List[str]:
        """列出所有可用算法"""
        return list(cls._algorithms.keys())


# ============================================================================
# 预处理管道
# ============================================================================

class TrackPreprocessor:
    """轨迹预处理管道"""

    def __init__(self, config: PreprocessingConfig = None):
        self.config = config or PreprocessingConfig()

    def preprocess_raw_data(
        self,
        raw_tracks: List[FlightTrackRaw]
    ) -> List[Dict]:
        """
        预处理原始轨迹数据

        步骤：
        1. 噪音过滤（基于速度）
        2. 数据转换为字典格式
        """
        # 按站号+批号分组
        from collections import defaultdict
        groups = defaultdict(list)

        for track in raw_tracks:
            key = f"{track.radar_station_id}_{track.track_id}"
            groups[key].append(track)

        processed_data = []

        for group_key, tracks in groups.items():
            # 按时间排序
            tracks = sorted(tracks, key=lambda t: t.timestamp)

            # 速度过滤
            valid_indices = [0]  # 第一个点总是保留

            for i in range(1, len(tracks)):
                # 计算与前一个点的速度
                point1 = {
                    'latitude': tracks[i-1].latitude,
                    'longitude': tracks[i-1].longitude,
                    'timestamp': tracks[i-1].timestamp,
                }
                point2 = {
                    'latitude': tracks[i].latitude,
                    'longitude': tracks[i].longitude,
                    'timestamp': tracks[i].timestamp,
                }

                _, speed_kmh, _ = calculate_velocity(point1, point2)

                # 检查速度是否合理
                if self.config.MIN_SPEED_KMH <= speed_kmh <= self.config.MAX_SPEED_KMH:
                    valid_indices.append(i)

            # 转换为字典格式
            for idx in valid_indices:
                track = tracks[idx]
                # 安全解析 raw_data (可能是 None、空字符串或无效 JSON)
                raw_data = {}
                if track.raw_data and track.raw_data.strip():
                    try:
                        raw_data = json.loads(track.raw_data)
                    except (json.JSONDecodeError, TypeError, ValueError):
                        raw_data = {}

                processed_data.append({
                    'raw_track_id': track.id,
                    'track_id': track.track_id,
                    'timestamp': track.timestamp,
                    'latitude': track.latitude,
                    'longitude': track.longitude,
                    'altitude': track.altitude or 0,
                    'radar_station_id': track.radar_station_id,
                    'raw_data': raw_data,
                })

        return processed_data

    def group_simultaneous_observations(
        self,
        observations: List[Dict]
    ) -> List[List[Dict]]:
        """
        分组同时观测

        条件：
        1. 时间差 <= TIME_WINDOW_MATCH
        2. 位置差 <= POSITION_THRESHOLD
        3. 不同雷达站
        """
        if not observations:
            return []

        # 按时间排序
        sorted_obs = sorted(observations, key=lambda o: o['timestamp'])

        groups = []
        processed = set()

        for i, obs_a in enumerate(sorted_obs):
            if id(obs_a) in processed:
                continue

            current_group = [obs_a]
            processed.add(id(obs_a))

            # 寻找匹配的观测
            for j, obs_b in enumerate(sorted_obs):
                if i == j or id(obs_b) in processed:
                    continue

                # 不同雷达站
                if obs_a['radar_station_id'] == obs_b['radar_station_id']:
                    continue

                # 检查时间差
                time_diff = abs((obs_b['timestamp'] - obs_a['timestamp']).total_seconds())
                if time_diff > self.config.TIME_WINDOW_MATCH:
                    continue

                # 检查位置距离
                distance = haversine_distance(
                    obs_a['latitude'], obs_a['longitude'],
                    obs_b['latitude'], obs_b['longitude']
                )
                distance_deg = distance / 111000  # 转换为度（粗略）

                if distance_deg > self.config.POSITION_THRESHOLD:
                    continue

                # 匹配成功
                current_group.append(obs_b)
                processed.add(id(obs_b))

            if len(current_group) >= 2:
                groups.append(current_group)

        return groups


# ============================================================================
# 主处理函数
# ============================================================================

def process_tracks(request: TrackProcessRequest, db: Session) -> TrackProcessResponse:
    """
    处理轨迹数据的主入口

    流程：
    1. 加载原始数据
    2. 预处理（噪音过滤）
    3. 选择算法并执行
    4. 保存结果
    """
    # 获取原始数据
    raw_tracks = db.query(FlightTrackRaw).filter(
        FlightTrackRaw.file_id == request.file_id
    ).order_by(FlightTrackRaw.timestamp).all()

    if not raw_tracks:
        raise ValueError("没有找到可处理的轨迹数据")

    # 预处理
    preprocessor = TrackPreprocessor()
    processed_data = preprocessor.preprocess_raw_data(raw_tracks)

    if not processed_data:
        raise ValueError("预处理后没有可用的数据")

    # 创建算法实例
    algorithm_name = request.mode.lower()
    algorithm_params = {}

    if algorithm_name == 'multi_source':
        algorithm_params = {
            'residual_threshold': request.ransac_threshold or 0.5,
            'min_samples': 2,
        }
    elif algorithm_name == 'single_source':
        algorithm_params = {
            'process_noise': request.kalman_process_noise or 0.1,
            'measurement_noise': request.kalman_measurement_noise or 1.0,
        }
    else:
        raise ValueError(f"不支持的处理模式: {request.mode}")

    algorithm = AlgorithmFactory.create_algorithm(algorithm_name, **algorithm_params)

    # 执行算法
    result = algorithm.correct(processed_data)

    # 保存到数据库
    corrected_count = 0
    outlier_count = 0

    for i, obs in enumerate(result['corrected_observations']):
        corrected = FlightTrackCorrected(
            raw_track_id=obs['raw_track_id'],
            track_id=obs['track_id'],
            timestamp=obs['timestamp'],
            latitude=obs['latitude'],
            longitude=obs['longitude'],
            altitude=obs['altitude'],
            correction_method=algorithm.get_name(),
            confidence_score=result['confidence_scores'][i],
            is_outlier=result['outlier_flags'][i],
            correction_metadata=json.dumps({
                'algorithm': algorithm.get_name(),
                'parameters': algorithm.get_parameters(),
                'raw_data': obs['raw_data'],
            }),
        )
        db.add(corrected)
        corrected_count += 1
        outlier_count += result['outlier_flags'][i]

    db.commit()

    return TrackProcessResponse(
        task_id=f"task_{request.file_id}_{datetime.utcnow().timestamp()}",
        status="completed",
        message=f"{algorithm.get_name()}处理完成，共处理 {corrected_count} 个点",
        total_points=len(raw_tracks),
        corrected_points=corrected_count,
        outliers_detected=outlier_count,
    )


# ============================================================================
# 查询函数
# ============================================================================

def get_raw_tracks(
    db: Session,
    file_id: Optional[int] = None,
    track_id: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = 1000,
) -> List[FlightTrackRaw]:
    """查询原始轨迹数据"""
    query = db.query(FlightTrackRaw)

    if file_id is not None:
        query = query.filter(FlightTrackRaw.file_id == file_id)
    if track_id is not None:
        query = query.filter(FlightTrackRaw.track_id == track_id)
    if start_time is not None:
        query = query.filter(FlightTrackRaw.timestamp >= start_time)
    if end_time is not None:
        query = query.filter(FlightTrackRaw.timestamp <= end_time)

    return query.order_by(FlightTrackRaw.timestamp).limit(limit).all()


def get_corrected_tracks(
    db: Session,
    file_id: Optional[int] = None,
    track_id: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = 1000,
) -> List[FlightTrackCorrected]:
    """查询修正后的轨迹数据"""
    query = db.query(FlightTrackCorrected)

    if track_id is not None:
        query = query.filter(FlightTrackCorrected.track_id == track_id)
    if start_time is not None:
        query = query.filter(FlightTrackCorrected.timestamp >= start_time)
    if end_time is not None:
        query = query.filter(FlightTrackCorrected.timestamp <= end_time)

    return query.order_by(FlightTrackCorrected.timestamp).limit(limit).all()
