"""
航迹插值模块

负责对关键航迹进行时间插值并存储到数据库
"""
import numpy as np
from typing import List, Tuple, Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.error_analysis import TrackInterpolatedPoint, TrackSegment
from app.algorithms.multi_source.preprocessing.config import MrraConfig
from core.logging import get_logger

logger = get_logger(__name__)


class TrackInterpolator:
    """
    航迹插值器类

    对航迹段进行时间插值，生成更密集的航迹点
    """

    def __init__(self, config: MrraConfig):
        """
        初始化航迹插值器

        Args:
            config: MRRA 配置
        """
        self.config = config

    def interpolate_track_segment(
        self,
        station_id: int,
        track_id: str,
        segment_points: List[Tuple],
        segment_index: int
    ) -> Tuple[List[Dict], List[Dict]]:
        """
        对航迹段进行时间插值

        Args:
            station_id: 雷达站号
            track_id: 航迹批号
            segment_points: 航迹段点列表
                每个点格式为 (station_id, track_id, time, lon, lat, alt)
            segment_index: 航迹段索引

        Returns:
            (原始点字典列表, 插值点字典列表)
        """
        original_points = []
        interpolated_points = []

        if not segment_points or len(segment_points) < 2:
            return original_points, interpolated_points

        # 添加原始点
        for point in segment_points:
            original_points.append({
                'station_id': station_id,
                'track_id': track_id,
                'time_seconds': point[2],
                'longitude': point[3],
                'latitude': point[4],
                'altitude': point[5],
                'segment_index': segment_index,
                'is_original': 1
            })

        # 插值处理
        prev_point = {
            'station_id': station_id,
            'track_id': track_id,
            'time_seconds': segment_points[0][2],
            'lon': segment_points[0][3],
            'lat': segment_points[0][4],
            'alt': segment_points[0][5]
        }

        # 添加第一个点
        interpolated_points.append({
            'station_id': station_id,
            'track_id': track_id,
            'time_seconds': prev_point['time_seconds'],
            'longitude': prev_point['lon'],
            'latitude': prev_point['lat'],
            'altitude': prev_point['alt'],
            'segment_index': segment_index,
            'is_original': 1
        })

        for current_point in segment_points[1:]:
            current = {
                'station_id': station_id,
                'track_id': track_id,
                'time_seconds': current_point[2],
                'lon': current_point[3],
                'lat': current_point[4],
                'alt': current_point[5]
            }

            # 计算速度向量 (经度/秒, 纬度/秒, 高度/秒)
            time_diff = current['time_seconds'] - prev_point['time_seconds']
            if time_diff > 0:
                velocity = (
                    (current['lon'] - prev_point['lon']) / time_diff,
                    (current['lat'] - prev_point['lat']) / time_diff,
                    (current['alt'] - prev_point['alt']) / time_diff
                )

                # 在每个整数时间点插值
                for t in np.arange(prev_point['time_seconds'] + 1, current['time_seconds'] + 0.1, 1.0):
                    interpolated_position = (
                        prev_point['lon'] + velocity[0] * (t - prev_point['time_seconds']),
                        prev_point['lat'] + velocity[1] * (t - prev_point['time_seconds']),
                        prev_point['alt'] + velocity[2] * (t - prev_point['time_seconds'])
                    )
                    interpolated_points.append({
                        'station_id': station_id,
                        'track_id': track_id,
                        'time_seconds': float(t),
                        'longitude': interpolated_position[0],
                        'latitude': interpolated_position[1],
                        'altitude': interpolated_position[2],
                        'segment_index': segment_index,
                        'is_original': 0
                    })

            prev_point = current

        return original_points, interpolated_points

    def save_to_database(
        self,
        db: Session,
        task_id: str,
        original_points: List[Dict],
        interpolated_points: List[Dict],
        reference_time: datetime
    ) -> int:
        """
        将点数据保存到数据库

        Args:
            db: 数据库会话
            task_id: 任务ID
            original_points: 原始点列表
            interpolated_points: 插值点列表
            reference_time: 参考时间（用于将秒数转换为时间戳）

        Returns:
            保存的点数
        """
        logger.info(f"保存 {len(original_points)} 个原始点和 {len(interpolated_points)} 个插值点到数据库")

        total_saved = 0

        # 保存原始点
        for point in original_points:
            timestamp = reference_time + timedelta(seconds=point['time_seconds'])
            db_point = TrackInterpolatedPoint(
                task_id=task_id,
                segment_id=point['segment_index'],
                station_id=point['station_id'],
                track_id=point['track_id'],
                time_seconds=point['time_seconds'],
                timestamp=timestamp,
                longitude=point['longitude'],
                latitude=point['latitude'],
                altitude=point['altitude'],
                is_original=1
            )
            db.add(db_point)
            total_saved += 1

        # 保存插值点
        for point in interpolated_points:
            timestamp = reference_time + timedelta(seconds=point['time_seconds'])
            db_point = TrackInterpolatedPoint(
                task_id=task_id,
                segment_id=point['segment_index'],
                station_id=point['station_id'],
                track_id=point['track_id'],
                time_seconds=point['time_seconds'],
                timestamp=timestamp,
                longitude=point['longitude'],
                latitude=point['latitude'],
                altitude=point['altitude'],
                is_original=0
            )
            db.add(db_point)
            total_saved += 1

        db.commit()
        logger.info(f"成功保存 {total_saved} 个点到数据库")

        return total_saved

    def save_track_segments(
        self,
        db: Session,
        task_id: str,
        key_tracks: Dict[int, List[Tuple[str, List[Tuple]]]],
        reference_time: datetime
    ) -> int:
        """
        保存航迹段信息到数据库

        Args:
            db: 数据库会话
            task_id: 任务ID
            key_tracks: 关键航迹字典
            reference_time: 参考时间

        Returns:
            保存的航迹段数量
        """
        logger.info("保存航迹段信息到数据库")

        segment_count = 0

        for station_id, track_segments in key_tracks.items():
            for segment_index, (track_id, segment_points) in enumerate(track_segments, start=1):
                if not segment_points:
                    continue

                start_time = reference_time + timedelta(seconds=segment_points[0][2])
                end_time = reference_time + timedelta(seconds=segment_points[-1][2])

                segment = TrackSegment(
                    task_id=task_id,
                    segment_id=segment_index,
                    station_id=station_id,
                    track_id=track_id,
                    start_time=start_time,
                    end_time=end_time,
                    point_count=len(segment_points)
                )
                db.add(segment)
                segment_count += 1

        db.commit()
        logger.info(f"成功保存 {segment_count} 个航迹段")

        return segment_count


def interpolate_and_save_tracks(
    db: Session,
    task_id: str,
    key_tracks: Dict[int, List[Tuple[str, List[Tuple]]]],
    config: MrraConfig,
    reference_time: datetime
) -> int:
    """
    对关键航迹进行插值并保存到数据库

    Args:
        db: 数据库会话
        task_id: 任务ID
        key_tracks: 关键航迹字典
        config: MRRA 配置
        reference_time: 参考时间

    Returns:
        总点数
    """
    logger.info("开始航迹插值处理")

    interpolator = TrackInterpolator(config)
    segment_index = 1

    # 先保存航迹段信息
    interpolator.save_track_segments(db, task_id, key_tracks, reference_time)

    # 插值并保存点数据
    all_original_points = []
    all_interpolated_points = []

    for station_id, track_segments in key_tracks.items():
        logger.debug(f"处理雷达站 [{station_id}] 的航迹插值")

        for track_id, segment_points in track_segments:
            original_points, interpolated_points = interpolator.interpolate_track_segment(
                station_id, track_id, segment_points, segment_index
            )

            all_original_points.extend(original_points)
            all_interpolated_points.extend(interpolated_points)
            segment_index += 1

    # 按时间排序插值点
    all_interpolated_points.sort(key=lambda p: p['time_seconds'])

    # 保存到数据库
    total_points = interpolator.save_to_database(
        db, task_id, all_original_points, all_interpolated_points, reference_time
    )

    logger.info(f"航迹插值完成: 共 {segment_index - 1} 个航迹段, {total_points} 个点")

    return total_points
