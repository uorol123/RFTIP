"""
航迹提取模块

负责从原始航迹数据中提取关键航迹段
"""
import numpy as np
from typing import List, Dict, Tuple, Set, Optional
from collections import defaultdict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.flight_track import FlightTrackRaw, RadarStation
from app.algorithms.multi_source.preprocessing.config import MrraConfig
from core.logging import get_logger

logger = get_logger(__name__)


class TrackPoint:
    """航迹点数据类"""

    def __init__(
        self,
        station_id: int,
        track_id: str,
        time_seconds: float,
        longitude: float,
        latitude: float,
        altitude: float,
        raw_track_id: Optional[int] = None
    ):
        self.station_id = station_id
        self.track_id = track_id
        self.time_seconds = time_seconds
        self.longitude = longitude
        self.latitude = latitude
        self.altitude = altitude
        self.raw_track_id = raw_track_id

    def to_tuple(self) -> Tuple:
        """转换为元组格式 (station_id, track_id, time, lon, lat, alt)"""
        return (self.station_id, self.track_id, self.time_seconds, self.longitude, self.latitude, self.altitude)


class TrackExtractor:
    """
    航迹提取器类

    使用空间网格和时间窗口检测持续的关键航迹点
    """

    def __init__(self, config: MrraConfig, min_coord: np.ndarray, max_coord: np.ndarray):
        """
        初始化航迹提取器

        Args:
            config: MRRA 配置
            min_coord: 最小坐标 [经度, 纬度]
            max_coord: 最大坐标 [经度, 纬度]
        """
        self.config = config

        # 计算网格维度
        self.min_xy = np.floor(min_coord / config.grid_resolution).astype(np.int32)
        max_xy = np.ceil(max_coord / config.grid_resolution).astype(np.int32) + 1
        self.dim = max_xy - self.min_xy

        # 确保网格至少为 3x3（保证 3x3 邻域检测正常工作）
        if self.dim[0] < 3:
            logger.warning(f"网格X维度 {self.dim[0]} < 3，自动扩展为 3")
            self.dim[0] = 3
        if self.dim[1] < 3:
            logger.warning(f"网格Y维度 {self.dim[1]} < 3，自动扩展为 3")
            self.dim[1] = 3

        # 初始化网格数据
        # grid_data[x][y] 存储落在该网格内的航迹点
        self.grid_data: List[List[List[TrackPoint]]] = [
            [[] for _ in range(self.dim[1])]
            for _ in range(self.dim[0])
        ]
        self.key_points: List[Tuple] = []
        self.processed_flags: Set[Tuple] = set()

        logger.debug(
            f"航迹提取器初始化: 网格维度 {self.dim}, "
            f"分辨率 {config.grid_resolution}度, 时间窗口 {config.time_window}秒"
        )

    def add_points(self, current_time: int, points: List[TrackPoint]) -> None:
        """
        添加当前时间的航迹点

        Args:
            current_time: 当前时间（秒）
            points: 航迹点列表
        """
        # 添加新点到网格
        for point in points:
            # 计算网格坐标
            grid_x = int(np.round(point.longitude / self.config.grid_resolution)) - self.min_xy[0]
            grid_y = int(np.round(point.latitude / self.config.grid_resolution)) - self.min_xy[1]

            # 检查边界
            if 0 <= grid_x < self.dim[0] and 0 <= grid_y < self.dim[1]:
                self.grid_data[grid_x][grid_y].append(point)

        # 清理过期点（超过时间窗口）
        for row in self.grid_data:
            for cell in row:
                # 移除超过时间窗口的点
                while cell and cell[0].time_seconds < current_time - self.config.time_window:
                    cell.pop(0)

        # 检测关键点（3×3邻域）
        for x in range(1, self.dim[0] - 1):
            for y in range(1, self.dim[1] - 1):
                # 获取3×3邻域内的所有点
                neighborhood: List[TrackPoint] = []
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        neighborhood.extend(self.grid_data[x + dx][y + dy])

                if len(neighborhood) < 5:
                    continue

                # 检查是否来自同一雷达站
                station_ids = {p.station_id for p in neighborhood}
                if len(station_ids) == 1:
                    # 按时间排序
                    sorted_points = sorted(neighborhood, key=lambda p: p.time_seconds)

                    # 检查持续时间
                    time_span = sorted_points[-1].time_seconds - sorted_points[0].time_seconds
                    if time_span >= self.config.time_window * self.config.time_window_ratio:
                        # 取中间点作为关键点
                        key_point = sorted_points[len(sorted_points) // 2]
                        point_key = (key_point.station_id, key_point.track_id, key_point.time_seconds)

                        # 避免重复添加
                        if point_key not in self.processed_flags:
                            self.processed_flags.add(point_key)
                            self.key_points.append(key_point.to_tuple())

    def get_key_points(self) -> List[Tuple]:
        """
        获取提取的关键点

        Returns:
            关键点列表，每个点格式为 (station_id, track_id, time, lon, lat, alt)
        """
        return sorted(self.key_points, key=lambda p: p[2])


def load_track_points_from_db(
    db: Session,
    file_id: int,
    radar_positions: Dict[int, Tuple[float, float, float]]
) -> Dict[int, List[TrackPoint]]:
    """
    从数据库加载航迹点数据

    Args:
        db: 数据库会话
        file_id: 文件ID
        radar_positions: 雷达站位置字典 {station_id: (lon, lat, alt)}

    Returns:
        字典：雷达站ID -> 航迹点列表
    """
    # 查询原始航迹数据
    raw_tracks = db.query(FlightTrackRaw).filter(
        FlightTrackRaw.file_id == file_id
    ).order_by(FlightTrackRaw.timestamp).all()

    if not raw_tracks:
        logger.warning(f"文件ID {file_id} 没有找到航迹数据")
        return {}

    # 按雷达站分组
    station_data: Dict[int, List[TrackPoint]] = defaultdict(list)

    # 获取参考时间（第一条记录的时间）
    reference_time = raw_tracks[0].timestamp.replace(hour=0, minute=0, second=0, microsecond=0)

    for track in raw_tracks:
        # 检查雷达站是否在配置中
        if track.radar_station_id not in radar_positions:
            continue

        # 计算时间秒数
        time_delta = track.timestamp - reference_time
        time_seconds = time_delta.total_seconds()

        # 创建航迹点
        point = TrackPoint(
            station_id=track.radar_station_id,
            track_id=track.batch_id,
            time_seconds=time_seconds,
            longitude=track.longitude,
            latitude=track.latitude,
            altitude=track.altitude or 0.0,
            raw_track_id=track.id
        )
        station_data[track.radar_station_id].append(point)

    # 按时间排序
    for station_id in station_data:
        station_data[station_id].sort(key=lambda p: p.time_seconds)

    total_points = sum(len(points) for points in station_data.values())
    logger.info(f"从数据库加载了 {len(station_data)} 个雷达站的 {total_points} 个航迹点")

    return station_data


def load_track_points_by_track_ids(
    db: Session,
    track_ids: List[str],
    radar_positions: Dict[int, Tuple[float, float, float]]
) -> Dict[int, List[TrackPoint]]:
    """
    从数据库加载航迹点数据（按轨迹编号筛选）

    Args:
        db: 数据库会话
        track_ids: 轨迹编号列表（如 ['100081', '396405']）
        radar_positions: 雷达站位置字典 {station_id: (lon, lat, alt)}

    Returns:
        字典：雷达站ID -> 航迹点列表
    """
    # 查询原始航迹数据（按轨迹编号筛选）
    raw_tracks = db.query(FlightTrackRaw).filter(
        FlightTrackRaw.batch_id.in_(track_ids)
    ).order_by(FlightTrackRaw.timestamp).all()

    if not raw_tracks:
        logger.warning(f"轨迹编号 {track_ids} 没有找到航迹数据")
        return {}

    # 按雷达站分组
    station_data: Dict[int, List[TrackPoint]] = defaultdict(list)

    # 获取参考时间（第一条记录的时间）
    reference_time = raw_tracks[0].timestamp.replace(hour=0, minute=0, second=0, microsecond=0)

    for track in raw_tracks:
        # 检查雷达站是否在配置中
        if track.radar_station_id not in radar_positions:
            continue

        # 计算时间秒数
        time_delta = track.timestamp - reference_time
        time_seconds = time_delta.total_seconds()

        # 创建航迹点
        point = TrackPoint(
            station_id=track.radar_station_id,
            track_id=track.batch_id,
            time_seconds=time_seconds,
            longitude=track.longitude,
            latitude=track.latitude,
            altitude=track.altitude or 0.0,
            raw_track_id=track.id
        )
        station_data[track.radar_station_id].append(point)

    # 按时间排序
    for station_id in station_data:
        station_data[station_id].sort(key=lambda p: p.time_seconds)

    total_points = sum(len(points) for points in station_data.values())
    logger.info(f"按轨迹编号加载了 {len(station_data)} 个雷达站的 {total_points} 个航迹点")

    return station_data


def extract_key_tracks(
    station_data: Dict[int, List[TrackPoint]],
    config: MrraConfig
) -> Dict[int, List[Tuple[str, List[Tuple]]]]:
    """
    从雷达站数据中提取关键航迹段

    Args:
        station_data: 雷达站数据字典
            键: 雷达站号
            值: 航迹点列表
        config: MRRA 配置

    Returns:
        字典：雷达站号 -> [(track_id, 关键航迹段), ...]
        关键航迹段为点列表，每个点格式为 (station_id, track_id, time, lon, lat, alt)
    """
    all_key_tracks = defaultdict(list)

    for station_id, points in station_data.items():
        logger.info(f"处理雷达站 [{station_id}] 的关键航迹提取")

        if not points:
            logger.warning(f"雷达站 [{station_id}] 没有数据")
            continue

        # 计算坐标范围
        coords = np.array([[p.longitude, p.latitude] for p in points])
        min_coord = coords.min(axis=0)
        max_coord = coords.max(axis=0)

        # 创建提取器
        extractor = TrackExtractor(config, min_coord, max_coord)

        # 获取时间范围
        min_time = int(points[0].time_seconds)
        max_time = int(points[-1].time_seconds) + 1

        # 按时间处理
        point_index = 0
        total_points = len(points)

        for current_time in range(min_time, max_time + 1):
            # 进度报告
            if current_time % 1000 == 0:
                logger.debug(f"时间 {current_time}s, 已提取 {len(extractor.key_points)} 个关键点")

            # 收集当前时间窗口内的点
            current_points = []
            while point_index < total_points and points[point_index].time_seconds <= current_time:
                current_points.append(points[point_index])
                point_index += 1

            if current_points:
                extractor.add_points(current_time, current_points)

        # 获取结果并排序
        key_points = extractor.get_key_points()

        # 按批号分组
        track_groups = defaultdict(list)
        for point in key_points:
            track_id = point[1]
            track_groups[track_id].append(point)

        # 分割连续航迹段
        for track_id, track_points in track_groups.items():
            if len(track_points) > 2:
                # 计算时间间隔
                times = np.array([p[2] for p in track_points])
                time_gaps = (times[1:] - times[:-1]) > 100

                # 找到分割点
                split_indices = [0] + list(np.where(time_gaps)[0] + 1) + [len(times)]

                # 创建航迹段（去掉首尾各2个点）
                for i in range(len(split_indices) - 1):
                    start_idx = split_indices[i] + 2
                    end_idx = split_indices[i + 1] - 1

                    if end_idx > start_idx and (end_idx - start_idx) >= config.min_track_points:
                        track_segment = track_points[start_idx:end_idx]
                        all_key_tracks[station_id].append((track_id, track_segment))

        logger.info(f"雷达站 [{station_id}] 提取到 {len(all_key_tracks[station_id])} 个关键航迹段")

    # 统计信息
    total_segments = sum(len(segments) for segments in all_key_tracks.values())
    logger.info(f"关键航迹提取完成: 共 {total_segments} 个航迹段")

    return all_key_tracks
