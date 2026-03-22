"""
MRRA 集成测试脚本

测试 MRRA 模块的各个组件
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.mrra.config import MrraConfig, CostWeights
from app.utils.mrra.track_extractor import TrackPoint, TrackExtractor
from app.utils.mrra.track_interpolator import TrackInterpolator
from app.utils.mrra.error_calculator import ErrorCalculator

import numpy as np
from typing import List, Dict, Tuple


def test_config():
    """测试配置模块"""
    print("=" * 50)
    print("测试配置模块")
    print("=" * 50)

    # 测试默认配置
    config = MrraConfig()
    print(f"网格分辨率: {config.grid_resolution}")
    print(f"时间窗口: {config.time_window}")
    print(f"匹配距离阈值: {config.match_distance_threshold}")
    print(f"优化步长: {config.optimization_steps}")

    # 测试自定义配置
    custom_config = MrraConfig(
        grid_resolution=0.1,
        time_window=30,
        match_distance_threshold=0.05
    )
    print(f"\n自定义配置:")
    print(f"网格分辨率: {custom_config.grid_resolution}")
    print(f"时间窗口: {custom_config.time_window}")

    print("\n✓ 配置模块测试通过\n")


def test_track_extractor():
    """测试航迹提取器"""
    print("=" * 50)
    print("测试航迹提取器")
    print("=" * 50)

    config = MrraConfig(
        grid_resolution=0.001,
        time_window=5,
        min_track_points=3
    )

    # 创建测试数据
    min_coord = np.array([116.0, 39.0])
    max_coord = np.array([116.01, 39.01])

    extractor = TrackExtractor(config, min_coord, max_coord)

    # 创建测试航迹点
    points = [
        TrackPoint(
            station_id=1001,
            track_id="T001",
            time_seconds=0.0,
            longitude=116.001,
            latitude=39.001,
            altitude=5000.0
        ),
        TrackPoint(
            station_id=1001,
            track_id="T001",
            time_seconds=1.0,
            longitude=116.0011,
            latitude=39.0011,
            altitude=5001.0
        ),
        TrackPoint(
            station_id=1001,
            track_id="T001",
            time_seconds=2.0,
            longitude=116.0012,
            latitude=39.0012,
            altitude=5002.0
        ),
    ]

    # 添加点
    extractor.add_points(0, points)
    extractor.add_points(5, [])

    # 获取关键点
    key_points = extractor.get_key_points()
    print(f"提取到 {len(key_points)} 个关键点")

    print("\n✓ 航迹提取器测试通过\n")


def test_track_interpolator():
    """测试航迹插值器"""
    print("=" * 50)
    print("测试航迹插值器")
    print("=" * 50)

    config = MrraConfig()
    interpolator = TrackInterpolator(config)

    # 创建测试航迹段
    segment_points = [
        (1001, "T001", 0.0, 116.0, 39.0, 5000.0),
        (1001, "T001", 5.0, 116.001, 39.001, 5010.0),
    ]

    # 执行插值
    original_points, interpolated_points = interpolator.interpolate_track_segment(
        station_id=1001,
        track_id="T001",
        segment_points=segment_points,
        segment_index=1
    )

    print(f"原始点: {len(original_points)}")
    print(f"插值点: {len(interpolated_points)}")
    print(f"总点数: {len(original_points) + len(interpolated_points)}")

    print("\n✓ 航迹插值器测试通过\n")


def test_error_calculator():
    """测试误差计算器"""
    print("=" * 50)
    print("测试误差计算器")
    print("=" * 50)

    config = MrraConfig()
    calculator = ErrorCalculator(config)

    # 创建测试匹配组
    match_groups = [
        [
            {'station_id': 1001, 'longitude': 116.001, 'latitude': 39.001, 'altitude': 5000.0},
            {'station_id': 1002, 'longitude': 116.0011, 'latitude': 39.0011, 'altitude': 5001.0},
        ]
    ]

    # 雷达站位置
    radar_positions = {
        1001: (116.0, 39.0, 100.0),
        1002: (116.002, 39.002, 100.0),
    }

    # 计算代价
    azimuth_errors = {1001: 0.0, 1002: 0.0}
    range_errors = {1001: 0.0, 1002: 0.0}

    cost = calculator.calculate_cost(match_groups, azimuth_errors, radar_positions, range_errors)
    print(f"初始代价: {cost:.6f}")

    # 测试方位角优化
    optimized_az = calculator.optimize_azimuth_errors(
        match_groups[:1],  # 只使用第一个匹配组进行测试
        azimuth_errors,
        radar_positions,
        range_errors
    )
    print(f"优化后方位角误差: {optimized_az}")

    print("\n✓ 误差计算器测试通过\n")


def test_integration():
    """测试完整流程"""
    print("=" * 50)
    print("测试完整流程")
    print("=" * 50)

    config = MrraConfig(
        grid_resolution=0.001,
        time_window=5,
        min_track_points=3,
        match_distance_threshold=0.01
    )

    # 步骤1: 创建测试航迹数据
    print("步骤1: 创建测试航迹数据")
    station_data = {
        1001: [
            TrackPoint(1001, "T001", 0.0, 116.0, 39.0, 5000.0),
            TrackPoint(1001, "T001", 1.0, 116.0001, 39.0001, 5001.0),
            TrackPoint(1001, "T001", 2.0, 116.0002, 39.0002, 5002.0),
        ],
        1002: [
            TrackPoint(1002, "T001", 0.0, 116.00005, 39.00005, 5000.5),
            TrackPoint(1002, "T001", 1.0, 116.00015, 39.00015, 5001.5),
            TrackPoint(1002, "T001", 2.0, 116.00025, 39.00025, 5002.5),
        ],
    }
    print(f"创建了 {len(station_data)} 个雷达站的数据")

    # 步骤2: 提取关键航迹
    print("\n步骤2: 提取关键航迹")
    from app.utils.mrra.track_extractor import extract_key_tracks

    key_tracks = extract_key_tracks(station_data, config)
    print(f"提取到 {sum(len(v) for v in key_tracks.values())} 个航迹段")

    # 步骤3: 插值
    print("\n步骤3: 航迹插值")
    interpolator = TrackInterpolator(config)

    all_interpolated = []
    for station_id, track_segments in key_tracks.items():
        for track_id, segment_points in track_segments:
            _, interpolated = interpolator.interpolate_track_segment(
                station_id, track_id, segment_points, 1
            )
            all_interpolated.extend(interpolated)

    print(f"生成了 {len(all_interpolated)} 个插值点")

    # 步骤4: 匹配
    print("\n步骤4: 航迹匹配")
    # 创建简单的匹配组用于测试
    match_groups = [
        [
            {'station_id': 1001, 'longitude': 116.0, 'latitude': 39.0, 'altitude': 5000.0},
            {'station_id': 1002, 'longitude': 116.00005, 'latitude': 39.00005, 'altitude': 5000.5},
        ]
    ]
    print(f"创建了 {len(match_groups)} 个匹配组")

    # 步骤5: 计算误差
    print("\n步骤5: 计算误差")
    radar_positions = {
        1001: (116.0, 39.0, 100.0),
        1002: (116.0005, 39.0005, 100.0),
    }

    from app.utils.mrra.error_calculator import calculate_error_results

    error_results = calculate_error_results(match_groups, radar_positions, config)
    print(f"计算了 {len(error_results['errors'])} 个雷达站的误差")

    for station_id, errors in error_results['errors'].items():
        print(f"  站{station_id}: 方位角={errors['azimuth_error']:.4f}°, "
              f"距离={errors['range_error']:.2f}m, "
              f"俯仰角={errors['elevation_error']:.4f}°")

    print("\n✓ 完整流程测试通过\n")


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("MRRA 集成测试")
    print("=" * 50 + "\n")

    try:
        test_config()
        test_track_extractor()
        test_track_interpolator()
        test_error_calculator()
        test_integration()

        print("=" * 50)
        print("所有测试通过! ✓")
        print("=" * 50)

    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
