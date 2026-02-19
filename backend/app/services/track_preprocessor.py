"""
轨迹预处理模块 - 基于参考文档的实现

实现三个核心功能：
1. 关键航迹提取：使用空间网格 + 时间窗口检测稳定航迹
2. 航迹分组：将相近时间 + 相近位置的观测分组
3. 噪音过滤：去除异常点和短时航迹

参考：docs/参考.md 中的 MRRA 雷达误差分析方法
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict
from typing import List, Tuple, Dict
import math


class TrackPreprocessor:
    """轨迹预处理器 - 基于参考文档实现"""

    def __init__(self):
        # 参考文档中的参数配置
        self.GRID_RESOLUTION = 0.2  # 空间网格分辨率（度）
        self.TIME_WINDOW = 60  # 时间窗口（秒），用于提取稳定航迹
        self.MATCH_TIME_WINDOW = 1.0  # 匹配时间窗口（秒）
        self.POSITION_THRESHOLD = 0.12  # 位置匹配阈值（度），约13.3km
        self.MIN_DURATION = 45  # 最短持续时间（秒）
        self.MIN_POINTS = 10  # 最小航迹点数

    def extract_key_tracks(
        self,
        df: pd.DataFrame,
        min_coord: np.ndarray = None,
        max_coord: np.ndarray = None
    ) -> List[List[Tuple]]:
        """
        关键航迹提取

        使用空间网格 + 时间窗口的方法，从原始数据中提取
        持续、稳定的航迹段，过滤噪声和短暂出现的点。

        Args:
            df: 原始轨迹数据，需包含批号、入库时间、经度、纬度
            min_coord: 最小坐标 [经度, 纬度]
            max_coord: 最大坐标 [经度, 纬度]

        Returns:
            关键航迹段列表，每个段为 (批号, 时间秒, 经度, 纬度, 高度) 的列表
        """
        # 解析时间
        df['timestamp'] = pd.to_datetime(df['入库时间'])
        df['time_seconds'] = (df['timestamp'] - df['timestamp'].min()).dt.total_seconds()

        # 自动计算坐标范围
        if min_coord is None:
            min_coord = np.array([df['经度'].min(), df['纬度'].min()])
        if max_coord is None:
            max_coord = np.array([df['经度'].max(), df['纬度'].max()])

        # 初始化空间网格
        min_xy = np.floor(min_coord / self.GRID_RESOLUTION).astype(int)
        max_xy = np.ceil(max_coord / self.GRID_RESOLUTION).astype(int) + 1
        dim = max_xy - min_xy

        # 网格：data[经度索引][纬度索引] = 点列表
        data = [[[] for _ in range(dim[1])] for _ in range(dim[0])]
        key_points = []
        processed_flags = set()

        # 按时间遍历（每秒一个时间步）
        for current_time in range(int(df['time_seconds'].min()), int(df['time_seconds'].max()) + 1):
            # 获取当前时间窗口内的点
            time_mask = (df['time_seconds'] <= current_time) & (df['time_seconds'] > current_time - self.TIME_WINDOW)
            current_points = df[time_mask]

            # 步骤1: 添加新点到网格
            for _, point in current_points.iterrows():
                grid_x, grid_y = (np.array([point['经度'], point['纬度']]) / self.GRID_RESOLUTION).astype(int) - min_xy

                if 0 <= grid_x < dim[0] and 0 <= grid_y < dim[1]:
                    point_data = (
                        point['批号'],
                        point['time_seconds'],
                        point['经度'],
                        point['纬度'],
                        point['高度'] if '高度' in point else 0
                    )
                    data[grid_x][grid_y].append(point_data)

            # 步骤2: 清理过期点
            for x in range(dim[0]):
                for y in range(dim[1]):
                    while data[x][y] and data[x][y][0][1] < current_time - self.TIME_WINDOW:
                        data[x][y].pop(0)

            # 步骤3: 检测3×3邻域内的关键点
            for x in range(1, dim[0] - 1):
                for y in range(1, dim[1] - 1):
                    # 收集3×3邻域内的所有点
                    neighborhood = []
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            neighborhood.extend(data[x + dx][y + dy])

                    # 判断条件
                    if len(neighborhood) < 5:
                        continue

                    # 检查是否来自同一批号
                    track_ids = set([p[0] for p in neighborhood])
                    if len(track_ids) != 1:
                        continue

                    # 按时间排序
                    sorted_points = sorted(neighborhood, key=lambda p: p[1])

                    # 检查持续时间
                    time_span = sorted_points[-1][1] - sorted_points[0][1]
                    if time_span >= self.MIN_DURATION:
                        # 取中间点作为关键点
                        key_point = sorted_points[len(sorted_points) // 2]
                        point_key = (key_point[0], key_point[1])

                        if point_key not in processed_flags:
                            processed_flags.add(point_key)
                            key_points.append(key_point)

        # 按批号分组并分割连续段
        track_groups = defaultdict(list)
        for point in key_points:
            track_groups[point[0]].append(point)

        key_track_segments = []

        for track_id, track_points in track_groups.items():
            if len(track_points) < self.MIN_POINTS:
                continue

            # 按时间排序
            track_points = sorted(track_points, key=lambda p: p[1])

            # 检测时间间隔 > 100秒的断裂点
            times = np.array([p[1] for p in track_points])
            time_gaps = times[1:] - times[:-1]
            split_indices = [0]

            for i, gap in enumerate(time_gaps):
                if gap > 100:
                    split_indices.append(i + 1)
            split_indices.append(len(track_points))

            # 创建航迹段（去掉首尾各2个点）
            for i in range(len(split_indices) - 1):
                start_idx = split_indices[i] + 2
                end_idx = split_indices[i + 1] - 1

                if end_idx > start_idx and (end_idx - start_idx) >= self.MIN_POINTS:
                    segment = track_points[start_idx:end_idx]
                    key_track_segments.append(segment)

        return key_track_segments

    def group_simultaneous_observations(
        self,
        df: pd.DataFrame,
        key_tracks: List[List[Tuple]] = None
    ) -> List[Dict]:
        """
        分组同时观测

        将不同雷达站在相近时间观测到相近位置的观测分组。
        这是参考文档中"航迹匹配"的核心思想。

        Args:
            df: 原始轨迹数据
            key_tracks: 关键航迹段（如果为None则使用所有数据）

        Returns:
            匹配组列表，每个组包含同时观测的多个点
        """
        df['timestamp'] = pd.to_datetime(df['入库时间'])
        df['time_seconds'] = (df['timestamp'] - df['timestamp'].min()).dt.total_seconds()

        # 如果没有提供关键航迹，使用所有数据
        if key_tracks is None:
            key_tracks = [df.to_records(index=False)]

        matched_groups = []

        # 按时间遍历（整数秒）
        for current_time in range(int(df['time_seconds'].min()), int(df['time_seconds'].max()) + 1):
            # 收集当前时间窗口内的点
            time_mask = (df['time_seconds'] <= current_time) & (df['time_seconds'] > current_time - self.MATCH_TIME_WINDOW)
            current_points = df[time_mask]

            if len(current_points) < 2:
                continue

            # 使用空间网格加速匹配
            groups = self._match_points_in_window(current_points, current_time)

            matched_groups.extend(groups)

        # 去重
        unique_groups = []
        seen = set()
        for group in matched_groups:
            # 创建组标识（按批号+时间排序）
            group_key = tuple(sorted([p['批号'] for _, p in group]))
            if group_key not in seen:
                seen.add(group_key)
                unique_groups.append(group)

        return unique_groups

    def _match_points_in_window(self, points: pd.DataFrame, current_time: int) -> List[List]:
        """
        在时间窗口内匹配点

        使用空间网格和位置阈值进行匹配
        """
        matched_groups = []
        processed = set()

        # 转换为列表便于处理
        point_list = []
        for _, point in points.iterrows():
            point_list.append({
                'station': point['站号'],
                'batch': point['批号'],
                'time': point['time_seconds'],
                'lon': point['经度'],
                'lat': point['纬度'],
                'alt': point['高度'] if '高度' in point else 0,
            })

        # 为每个点寻找匹配
        for i, point_a in enumerate(point_list):
            point_key = (point_a['station'], point_a['batch'])

            if point_key in processed:
                continue

            processed.add(point_key)
            current_group = [{'index': i, 'data': point_a}]

            # 寻找其他匹配的点
            for j, point_b in enumerate(point_list):
                if i == j:
                    continue

                point_b_key = (point_b['station'], point_b['batch'])
                if point_b_key in processed:
                    continue

                # 同站号的点不匹配
                if point_b['station'] in [p['station'] for p in current_group]:
                    continue

                # 计算位置距离（欧氏距离）
                pos_a = np.array([point_a['lon'], point_a['lat']])
                pos_b = np.array([point_b['lon'], point_b['lat']])
                distance = np.sqrt(np.sum((pos_b - pos_a) ** 2))

                # 检查是否在位置阈值内
                if distance < self.POSITION_THRESHOLD:
                    current_group.append({'index': j, 'data': point_b})
                    processed.add(point_b_key)

            # 只有匹配到多个点才保留
            if len(current_group) >= 2:
                matched_groups.append(current_group)

        return matched_groups

    def filter_noise_by_velocity(
        self,
        df: pd.DataFrame,
        max_speed_kmh: float = 800.0,
        min_speed_kmh: float = 50.0
    ) -> pd.DataFrame:
        """
        基于速度过滤噪音点

        计算相邻点之间的速度，去除异常速度的点。

        Args:
            df: 轨迹数据
            max_speed_kmh: 最大合理速度（km/h）
            min_speed_kmh: 最小合理速度（km/h）

        Returns:
            过滤后的数据
        """
        df['timestamp'] = pd.to_datetime(df['入库时间'])

        # 按站号+批号分组
        df['group_key'] = df['站号'].astype(str) + '_' + df['批号'].astype(str)

        valid_indices = []

        for group_key, group in df.groupby('group_key'):
            group = group.sort_values('timestamp').reset_index(drop=True)

            if len(group) < 2:
                # 只有一个点，保留
                valid_indices.extend(group.index.tolist())
                continue

            # 检查每个点的相邻速度
            for i in range(len(group)):
                is_valid = True

                # 检查与后一个点的速度
                if i < len(group) - 1:
                    speed = self._calculate_speed(group.iloc[i], group.iloc[i + 1])
                    if speed > max_speed_kmh or speed < min_speed_kmh:
                        is_valid = False

                # 检查与前一个点的速度
                if is_valid and i > 0:
                    speed = self._calculate_speed(group.iloc[i - 1], group.iloc[i])
                    if speed > max_speed_kmh or speed < min_speed_kmh:
                        is_valid = False

                if is_valid:
                    valid_indices.append(group.iloc[i].name)

        return df.loc[valid_indices]

    def _calculate_speed(self, point1, point2) -> float:
        """计算两点间的速度（km/h）"""
        # Haversine 距离
        R = 6371000  # 地球半径（米）

        lat1, lon1 = math.radians(point1['纬度']), math.radians(point1['经度'])
        lat2, lon2 = math.radians(point2['纬度']), math.radians(point2['经度'])

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = (math.sin(dlat / 2) ** 2 +
             math.cos(lat1) * math.cos(lat2) *
             math.sin(dlon / 2) ** 2)

        distance = R * 2 * math.asin(math.sqrt(a))  # 米

        # 时间差
        time_diff = (pd.to_datetime(point2['入库时间']) - pd.to_datetime(point1['入库时间'])).total_seconds()

        if time_diff == 0:
            return 0

        speed_mps = distance / time_diff  # 米/秒
        speed_kmh = speed_mps * 3.6  # km/h

        return speed_kmh

    def get_preprocessing_summary(self, df: pd.DataFrame) -> Dict:
        """获取数据预处理摘要"""
        df['timestamp'] = pd.to_datetime(df['入库时间'])

        summary = {
            'total_points': len(df),
            'unique_batches': df['批号'].nunique(),
            'unique_stations': df['站号'].nunique(),
            'time_range': (df['timestamp'].min(), df['timestamp'].max()),
            'coord_range': {
                'lon': (df['经度'].min(), df['经度'].max()),
                'lat': (df['纬度'].min(), df['纬度'].max()),
            },
        }

        # 分析时间差
        time_diffs = []
        for batch_id, group in df.groupby('批号'):
            if len(group) >= 2:
                times = sorted(group['timestamp'].tolist())
                for i in range(len(times) - 1):
                    diff = (times[i + 1] - times[i]).total_seconds()
                    time_diffs.append(diff)

        if time_diffs:
            summary['time_diff_stats'] = {
                'median': np.median(time_diffs),
                'p90': np.percentile(time_diffs, 90),
                'p95': np.percentile(time_diffs, 95),
                'p99': np.percentile(time_diffs, 99),
                'max': max(time_diffs),
            }

        return summary


def main():
    """测试预处理模块"""
    data_dir = r"D:\myworld\毕设\RFTIP\data"

    # 加载数据
    df = pd.concat([
        pd.read_csv(f'{data_dir}/qb_xp_point_zb_210000-212000.csv', encoding='utf-8-sig'),
        pd.read_csv(f'{data_dir}/qb_xp_point_zb_212000-214000.csv', encoding='utf-8-sig'),
    ])

    print(f"原始数据: {len(df)} 行")

    # 创建预处理器
    preprocessor = TrackPreprocessor()

    # 获取摘要
    summary = preprocessor.get_preprocessing_summary(df)
    print(f"\n数据摘要:")
    print(f"  总点数: {summary['total_points']:,}")
    print(f"  唯一批号: {summary['unique_batches']}")
    print(f"  唯一站号: {summary['unique_stations']}")
    print(f"  时间范围: {summary['time_range'][0]} 到 {summary['time_range'][1]}")
    if 'time_diff_stats' in summary:
        stats = summary['time_diff_stats']
        print(f"\n时间差统计:")
        print(f"  中位数: {stats['median']:.3f} 秒")
        print(f"  90%分位: {stats['p90']:.3f} 秒")
        print(f"  95%分位: {stats['p95']:.3f} 秒")

    # 过滤噪音
    print(f"\n过滤噪音...")
    df_filtered = preprocessor.filter_noise_by_velocity(df, max_speed_kmh=800)
    print(f"  过滤前: {len(df)} 行")
    print(f"  过滤后: {len(df_filtered)} 行")
    print(f"  去除: {len(df) - len(df_filtered)} 行噪音")

    # 提取关键航迹
    print(f"\n提取关键航迹...")
    key_tracks = preprocessor.extract_key_tracks(df_filtered)
    print(f"  提取了 {len(key_tracks)} 个关键航迹段")

    # 分组同时观测
    print(f"\n分组同时观测...")
    matched_groups = preprocessor.group_simultaneous_observations(df_filtered, key_tracks)
    print(f"  形成了 {len(matched_groups)} 个匹配组")

    # 统计匹配组规模
    group_sizes = [len(g) for g in matched_groups]
    if group_sizes:
        print(f"\n匹配组规模分布:")
        from collections import Counter
        size_dist = Counter(group_sizes)
        for size in sorted(size_dist.keys()):
            print(f"  {size}个点: {size_dist[size]} 组")


if __name__ == "__main__":
    main()
