"""
轨迹处理服务 - 实现轨迹数据处理和修正算法
"""
import json
import numpy as np
from datetime import datetime
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sklearn.linear_model import RANSACRegressor
from filterpy.kalman import KalmanFilter

from app.models.flight_track import FlightTrackRaw, FlightTrackCorrected
from app.schemas.track import TrackProcessRequest, TrackProcessResponse


class RANSACCorrector:
    """RANSAC 多源参考修正器"""

    def __init__(self, residual_threshold: float = 0.5, min_samples: int = 2):
        self.residual_threshold = residual_threshold
        self.min_samples = min_samples

    def correct_position(
        self,
        positions: List[Tuple[float, float, float]]
    ) -> Tuple[Optional[Tuple[float, float]], List[bool], float]:
        """
        使用 RANSAC 算法修正位置

        Args:
            positions: 多个雷达站的位置数据 [(lat, lng, altitude), ...]

        Returns:
            (修正后位置, 是否为离群值列表, 置信度)
        """
        if len(positions) < self.min_samples:
            return None, [False] * len(positions), 0.0

        # 提取经纬度
        coords = np.array([(p[0], p[1]) for p in positions])

        # 使用 RANSAC 找到一致性集合
        ransac = RANSACRegressor(
            residual_threshold=self.residual_threshold,
            min_samples=self.min_samples,
        )

        try:
            # 分别处理纬度和经度
            lats = np.array([p[0] for p in positions]).reshape(-1, 1)
            lngs = np.array([p[1] for p in positions]).reshape(-1, 1)

            ransac.fit(lats, lngs)
            inlier_mask = ransac.inlier_mask_

            # 计算修正后的位置（使用内点的平均值）
            inliers = [positions[i] for i in range(len(positions)) if inlier_mask[i]]
            if inliers:
                corrected_lat = np.mean([p[0] for p in inliers])
                corrected_lng = np.mean([p[1] for p in inliers])
                corrected_alt = np.mean([p[2] for p in inliers if p[2] is not None]) or 0

                # 置信度基于内点比例
                confidence = np.sum(inlier_mask) / len(inlier_mask)

                return (corrected_lat, corrected_lng, corrected_alt), inlier_mask.tolist(), confidence
            else:
                return None, [False] * len(positions), 0.0

        except Exception:
            return None, [False] * len(positions), 0.0


class KalmanFilterCorrector:
    """卡尔曼滤波单源修正器"""

    def __init__(self, process_noise: float = 0.1, measurement_noise: float = 1.0):
        self.process_noise = process_noise
        self.measurement_noise = measurement_noise
        self.kf = None
        self.initialized = False

    def initialize(self, initial_state: np.ndarray):
        """初始化卡尔曼滤波器"""
        # 状态: [lat, lng, alt, velocity_lat, velocity_lng, velocity_alt]
        self.kf = KalmanFilter(dim_x=6, dim_z=3)

        # 状态转移矩阵 (匀速模型)
        dt = 1.0  # 时间步长
        self.kf.F = np.array([
            [1, 0, 0, dt, 0, 0],
            [0, 1, 0, 0, dt, 0],
            [0, 0, 1, 0, 0, dt],
            [0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 1],
        ])

        # 测量矩阵
        self.kf.H = np.array([
            [1, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0],
        ])

        # 噪声协方差矩阵
        self.kf.Q = np.eye(6) * self.process_noise
        self.kf.R = np.eye(3) * self.measurement_noise

        # 初始状态
        self.kf.x = initial_state.reshape(6, 1)

        # 初始协方差
        self.kf.P = np.eye(6) * 100

        self.initialized = True

    def filter(self, measurement: Tuple[float, float, float]) -> Tuple[float, float, float, float]:
        """
        应用卡尔曼滤波

        Args:
            measurement: 测量值 (lat, lng, alt)

        Returns:
            (修正后lat, 修正后lng, 修正后alt, 置信度)
        """
        if not self.initialized:
            initial_state = np.array([measurement[0], measurement[1], measurement[2] or 0, 0, 0, 0])
            self.initialize(initial_state)
            confidence = 0.5
        else:
            # 预测
            self.kf.predict()

            # 更新
            self.kf.update(np.array([measurement[0], measurement[1], measurement[2] or 0]))

            # 基于协方差计算置信度
            confidence = 1.0 / (1.0 + np.trace(self.kf.P))

        # 获取修正后的状态
        corrected_lat = float(self.kf.x[0, 0])
        corrected_lng = float(self.kf.x[1, 0])
        corrected_alt = float(self.kf.x[2, 0])

        return corrected_lat, corrected_lng, corrected_alt, confidence


def process_track_multi_source(
    file_id: int,
    db: Session,
    ransac_threshold: float = 0.5,
) -> TrackProcessResponse:
    """
    多源参考模式处理轨迹（RANSAC 算法）

    当多台雷达探测同一目标时，利用 RANSAC 算法剔除偏离群体的"坏点"站号
    """
    # 获取原始轨迹数据
    raw_tracks = db.query(FlightTrackRaw).filter(
        FlightTrackRaw.file_id == file_id
    ).order_by(FlightTrackRaw.timestamp, FlightTrackRaw.radar_station_id).all()

    if not raw_tracks:
        raise ValueError("没有找到可处理的轨迹数据")

    # 按时间戳分组
    from collections import defaultdict
    tracks_by_time = defaultdict(list)
    for track in raw_tracks:
        key = track.timestamp.isoformat()
        tracks_by_time[key].append(track)

    corrector = RANSACCorrector(residual_threshold=ransac_threshold)
    total_points = 0
    corrected_points = 0
    outliers_detected = 0

    # 处理每个时间点的数据
    for timestamp_str, tracks in tracks_by_time.items():
        if len(tracks) < 2:
            # 单站数据，直接保存
            for track in tracks:
                corrected = FlightTrackCorrected(
                    raw_track_id=track.id,
                    track_id=track.track_id,
                    timestamp=track.timestamp,
                    latitude=track.latitude,
                    longitude=track.longitude,
                    altitude=track.altitude,
                    speed=track.speed,
                    heading=track.heading,
                    correction_method="single",
                    confidence_score=0.5,
                    is_outlier=0,
                )
                db.add(corrected)
                corrected_points += 1
            total_points += len(tracks)
            continue

        # 多站数据，应用 RANSAC
        positions = [(t.latitude, t.longitude, t.altitude or 0) for t in tracks]
        result = corrector.correct_position(positions)

        if result[0] is not None:
            corrected_pos, inlier_mask, confidence = result
            for i, track in enumerate(tracks):
                is_outlier = 0 if inlier_mask[i] else 1
                if is_outlier:
                    outliers_detected += 1

                corrected = FlightTrackCorrected(
                    raw_track_id=track.id,
                    track_id=track.track_id,
                    timestamp=track.timestamp,
                    latitude=corrected_pos[0],
                    longitude=corrected_pos[1],
                    altitude=corrected_pos[2],
                    correction_method="ransac",
                    confidence_score=confidence,
                    is_outlier=is_outlier,
                    correction_metadata=json.dumps({
                        "original_position": {"lat": positions[i][0], "lng": positions[i][1], "alt": positions[i][2]},
                        "inlier": inlier_mask[i],
                    }),
                )
                db.add(corrected)
                corrected_points += 1
        else:
            # RANSAC 失败，保存原始数据
            for track in tracks:
                corrected = FlightTrackCorrected(
                    raw_track_id=track.id,
                    track_id=track.track_id,
                    timestamp=track.timestamp,
                    latitude=track.latitude,
                    longitude=track.longitude,
                    altitude=track.altitude,
                    correction_method="none",
                    confidence_score=0.0,
                )
                db.add(corrected)
                corrected_points += 1

        total_points += len(tracks)

    db.commit()

    return TrackProcessResponse(
        task_id=f"task_{file_id}_{datetime.utcnow().timestamp()}",
        status="completed",
        message=f"多源处理完成，共处理 {total_points} 个点",
        total_points=total_points,
        corrected_points=corrected_points,
        outliers_detected=outliers_detected,
    )


def process_track_single_source(
    file_id: int,
    db: Session,
    process_noise: float = 0.1,
    measurement_noise: float = 1.0,
) -> TrackProcessResponse:
    """
    单源盲测模式处理轨迹（卡尔曼滤波）

    采用卡尔曼滤波算法，基于物理运动模型对单站噪声数据进行预测与修正
    """
    # 获取原始轨迹数据
    raw_tracks = db.query(FlightTrackRaw).filter(
        FlightTrackRaw.file_id == file_id
    ).order_by(FlightTrackRaw.timestamp).all()

    if not raw_tracks:
        raise ValueError("没有找到可处理的轨迹数据")

    # 按轨迹ID分组
    from collections import defaultdict
    tracks_by_id = defaultdict(list)
    for track in raw_tracks:
        tracks_by_id[track.track_id].append(track)

    total_points = 0
    corrected_points = 0
    outliers_detected = 0

    # 处理每条轨迹
    for track_id, tracks in tracks_by_id.items():
        corrector = KalmanFilterCorrector(
            process_noise=process_noise,
            measurement_noise=measurement_noise,
        )

        for track in tracks:
            # 应用卡尔曼滤波
            measurement = (track.latitude, track.longitude, track.altitude or 0)
            corrected_lat, corrected_lng, corrected_alt, confidence = corrector.filter(measurement)

            # 创建修正记录
            corrected = FlightTrackCorrected(
                raw_track_id=track.id,
                track_id=track.track_id,
                timestamp=track.timestamp,
                latitude=corrected_lat,
                longitude=corrected_lng,
                altitude=corrected_alt,
                speed=track.speed,
                heading=track.heading,
                correction_method="kalman",
                confidence_score=confidence,
                is_outlier=0,
            )
            db.add(corrected)
            corrected_points += 1
            total_points += 1

    db.commit()

    return TrackProcessResponse(
        task_id=f"task_{file_id}_{datetime.utcnow().timestamp()}",
        status="completed",
        message=f"单源处理完成，共处理 {total_points} 个点",
        total_points=total_points,
        corrected_points=corrected_points,
        outliers_detected=outliers_detected,
    )


def process_tracks(request: TrackProcessRequest, db: Session) -> TrackProcessResponse:
    """处理轨迹数据的主入口"""
    if request.mode == "multi_source":
        return process_track_multi_source(
            file_id=request.file_id,
            db=db,
            ransac_threshold=request.ransac_threshold or 0.5,
        )
    elif request.mode == "single_source":
        return process_track_single_source(
            file_id=request.file_id,
            db=db,
            process_noise=request.kalman_process_noise or 0.1,
            measurement_noise=request.kalman_measurement_noise or 1.0,
        )
    else:
        raise ValueError(f"不支持的处理模式: {request.mode}")


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
