"""
航迹匹配模块

负责匹配不同雷达的航迹点
"""
from datetime import datetime
import numpy as np
from typing import List, Tuple, Set, Dict, Optional
from sqlalchemy.orm import Session

from app.models.error_analysis import TrackInterpolatedPoint, MatchGroup
from app.utils.mrra.config import MrraConfig
from core.logging import get_logger

logger = get_logger(__name__)


class TrackMatcher:
    """
    航迹匹配器类

    基于空间距离阈值匹配不同雷达的航迹点
    """

    def __init__(self, config: MrraConfig, min_coord: np.ndarray, max_coord: np.ndarray):
        """
        初始化航迹匹配器

        Args:
            config: MRRA 配置
            min_coord: 最小坐标 [经度, 纬度]
            max_coord: 最大坐标 [经度, 纬度]
        """
        self.config = config
        self.min_xy = np.floor(min_coord / config.grid_resolution).astype(np.int32)
        max_xy = np.ceil(max_coord / config.grid_resolution).astype(np.int32) + 1
        self.dim = max_xy - self.min_xy

        # 初始化网格数据
        self.grid_data: List[List[List[Dict]]] = [
            [[] for _ in range(self.dim[1])]
            for _ in range(self.dim[0])
        ]
        self.matched_groups: List[List[Dict]] = []

        logger.debug(f"航迹匹配器初始化: 网格维度 {self.dim}, 分辨率 {self.config.grid_resolution}度")

    def match_points(
        self,
        current_time: int,
        points_a: List[Dict],
        points_b: List[Dict]
    ) -> List[List[Dict]]:
        """
        匹配两个点集

        Args:
            current_time: 当前时间（秒）
            points_a: 第一个点集
            points_b: 第二个点集

        Returns:
            匹配组列表，每个匹配组包含多个匹配点
        """
        matched_groups = []
        processed_pairs = set()

        # 处理点集A中的每个点
        for point_a in points_a:
            point_key = (point_a['station_id'], point_a['track_id'])

            # 跳过已处理的点
            if point_key in processed_pairs:
                continue

            processed_pairs.add(point_key)
            current_group = [point_a]

            # 在点集B中寻找匹配点
            for point_b in points_b:
                point_b_key = (point_b['station_id'], point_b['track_id'])

                # 跳过已处理的点或同站点的点
                if point_b_key in processed_pairs:
                    continue
                if point_b['station_id'] in [p['station_id'] for p in current_group]:
                    continue

                # 计算距离
                point_a_coord = np.array([point_a['longitude'], point_a['latitude']])
                point_b_coord = np.array([point_b['longitude'], point_b['latitude']])
                distance = np.sqrt(np.sum((point_b_coord - point_a_coord) ** 2))

                # 检查是否在阈值内
                if distance < self.config.match_distance_threshold:
                    current_group.append(point_b)
                    processed_pairs.add(point_b_key)

            # 只有匹配到至少2个点（来自不同雷达）才保留
            if len(current_group) > 1:
                matched_groups.append(current_group)

        return matched_groups


def load_interpolated_points(
    db: Session,
    task_id: str
) -> Tuple[List[Dict], List[Dict]]:
    """
    从数据库加载插值点数据

    Args:
        db: 数据库会话
        task_id: 任务ID

    Returns:
        (原始点列表, 插值点列表)
    """
    logger.info(f"从数据库加载任务 {task_id} 的插值点数据")

    # 查询所有点
    points = db.query(TrackInterpolatedPoint).filter(
        TrackInterpolatedPoint.task_id == task_id
    ).order_by(TrackInterpolatedPoint.time_seconds).all()

    if not points:
        logger.warning(f"任务 {task_id} 没有插值点数据")
        return [], []

    # 分离原始点和插值点
    original_points = []
    interpolated_points = []

    for point in points:
        point_dict = {
            'id': point.id,
            'station_id': point.station_id,
            'track_id': point.track_id,
            'time_seconds': point.time_seconds,
            'longitude': point.longitude,
            'latitude': point.latitude,
            'altitude': point.altitude or 0.0,
            'segment_id': point.segment_id
        }

        if point.is_original == 1:
            original_points.append(point_dict)
        else:
            interpolated_points.append(point_dict)

    logger.info(f"加载了 {len(original_points)} 个原始点和 {len(interpolated_points)} 个插值点")

    return original_points, interpolated_points


def match_tracks_from_database(
    db: Session,
    task_id: str,
    config: MrraConfig
) -> List[List[Dict]]:
    """
    从数据库加载数据并进行航迹匹配

    Args:
        db: 数据库会话
        task_id: 任务ID
        config: MRRA 配置

    Returns:
        匹配组列表，每个匹配组包含多个匹配点
    """
    logger.info("开始航迹匹配分析")

    # 加载数据
    original_points, interpolated_points = load_interpolated_points(db, task_id)

    if not interpolated_points:
        logger.warning("没有插值点数据，无法进行匹配")
        return []

    # 计算坐标范围
    coords = np.array([[p['longitude'], p['latitude']] for p in interpolated_points])
    min_coord = coords.min(axis=0)
    max_coord = coords.max(axis=0)

    # 创建匹配器
    matcher = TrackMatcher(config, min_coord, max_coord)

    # 按时间进行匹配
    all_matched_groups = []
    index_a = 0  # 原始点索引
    index_b = 0  # 插值点索引

    # 获取时间范围
    min_time = int(interpolated_points[0]['time_seconds'])
    max_time = int(interpolated_points[-1]['time_seconds']) + 1

    for current_time in range(min_time, max_time + 1):
        # 进度报告
        if current_time % 3600 == 0:
            hour = current_time // 3600
            logger.info(f"匹配分析时刻 {hour:02d}:00:00")

        # 收集当前时间的原始点
        points_a = []
        while index_a < len(original_points) and original_points[index_a]['time_seconds'] <= current_time:
            points_a.append(original_points[index_a])
            index_a += 1

        if not points_a:
            continue

        # 收集当前时间的插值点
        points_b = []
        while index_b < len(interpolated_points) and interpolated_points[index_b]['time_seconds'] <= current_time:
            points_b.append(interpolated_points[index_b])
            index_b += 1

        if not points_b:
            continue

        # 进行匹配
        matched_groups = matcher.match_points(current_time, points_a, points_b)
        all_matched_groups.extend(matched_groups)

    # 对每个匹配组排序
    for group in all_matched_groups:
        group.sort(key=lambda p: (p['station_id'], p['track_id']))

    logger.info(f"航迹匹配完成: 共 {len(all_matched_groups)} 个匹配组")

    return all_matched_groups


def save_matched_groups(
    db: Session,
    task_id: str,
    matched_groups: List[List[Dict]],
    reference_time: datetime
) -> int:
    """
    保存匹配结果到数据库

    Args:
        db: 数据库会话
        task_id: 任务ID
        matched_groups: 匹配组列表
        reference_time: 参考时间

    Returns:
        保存的匹配组数量
    """
    logger.info(f"保存 {len(matched_groups)} 个匹配组到数据库")

    group_count = 0

    for group_index, group in enumerate(matched_groups, start=1):
        if not group:
            continue

        # 获取匹配时间（使用第一个点的时间）
        match_time = reference_time

        # 计算质量指标
        positions = np.array([[p['longitude'], p['latitude']] for p in group])
        center = positions.mean(axis=0)
        distances = np.sqrt(np.sum((positions - center) ** 2, axis=1))

        avg_distance = float(np.mean(distances))
        max_distance = float(np.max(distances))
        variance = float(np.var(distances))

        # 构建匹配点列表
        match_points = []
        for point in group:
            match_points.append({
                'station_id': point['station_id'],
                'point_id': point.get('id'),
                'longitude': point['longitude'],
                'latitude': point['latitude'],
                'altitude': point.get('altitude', 0.0)
            })

        # 创建匹配组记录
        match_group = MatchGroup(
            task_id=task_id,
            group_id=group_index,
            match_time=match_time,
            match_points=match_points,
            point_count=len(group),
            avg_distance=avg_distance,
            max_distance=max_distance,
            variance=variance
        )
        db.add(match_group)
        group_count += 1

    db.commit()
    logger.info(f"成功保存 {group_count} 个匹配组")

    return group_count


def analyze_match_statistics(matched_groups: List[List[Dict]]) -> Dict[int, int]:
    """
    分析匹配统计信息

    Args:
        matched_groups: 匹配组列表

    Returns:
        字典：匹配组大小 -> 数量
    """
    if not matched_groups:
        return {}

    group_sizes = [len(group) for group in matched_groups]
    max_size = max(group_sizes)

    statistics = {}
    for size in range(2, max_size + 1):
        count = sum(1 for s in group_sizes if s == size)
        if count > 0:
            statistics[size] = count

    logger.info("匹配统计信息:")
    for size, count in statistics.items():
        logger.info(f"  大小 {size}: {count} 组")

    return statistics
