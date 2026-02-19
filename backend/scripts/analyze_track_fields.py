"""
分析真实数据中的航向和速度字段

按"站号+批号"分组，分析：
1. 航向字段 vs 计算出的实际航向
2. 速度字段 vs 计算出的实际速度

使用真实数据: D:\myworld\毕设\RFTIP\data\
"""
import os
import pandas as pd
import numpy as np
from datetime import datetime
from collections import defaultdict
from typing import List, Tuple, Dict
import math


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    计算两点之间的球面距离（米）

    使用 Haversine 公式
    """
    R = 6371000  # 地球半径（米）

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = (math.sin(delta_lat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) *
         math.sin(delta_lon / 2) ** 2)

    c = 2 * math.asin(math.sqrt(a))
    distance = R * c
    return distance


def calculate_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    计算从点1到点2的方位角（航向，度）

    返回值范围: 0-360度
    0度 = 北，90度 = 东，180度 = 南，270度 = 西
    """
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lon = math.radians(lon2 - lon1)

    y = math.sin(delta_lon) * math.cos(lat2_rad)
    x = (math.cos(lat1_rad) * math.sin(lat2_rad) -
         math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon))

    bearing = math.atan2(y, x)
    bearing = math.degrees(bearing)
    bearing = (bearing + 360) % 360  # 确保在 0-360 范围内

    return bearing


def calculate_velocity(distance: float, time_diff: float) -> float:
    """
    计算速度（米/秒）

    Args:
        distance: 距离（米）
        time_diff: 时间差（秒）

    Returns:
        速度（米/秒）
    """
    if time_diff == 0:
        return 0
    return distance / time_diff


def normalize_angle(angle: float) -> float:
    """
    将角度标准化到 0-360 范围
    """
    return angle % 360


def angle_difference(angle1: float, angle2: float) -> float:
    """
    计算两个角度之间的最小差值（0-180度）
    """
    diff = abs(angle1 - angle2) % 360
    if diff > 180:
        diff = 360 - diff
    return diff


def load_data_files(data_dir: str) -> pd.DataFrame:
    """加载所有数据文件"""
    all_data = []

    for filename in os.listdir(data_dir):
        if filename.endswith('.csv') and filename.startswith('qb_xp_point'):
            filepath = os.path.join(data_dir, filename)
            print(f"加载文件: {filename}")
            df = pd.read_csv(filepath, encoding='utf-8-sig')
            all_data.append(df)

    if not all_data:
        raise ValueError(f"在 {data_dir} 中没有找到数据文件")

    combined = pd.concat(all_data, ignore_index=True)
    print(f"总共加载 {len(combined)} 行数据")
    return combined


def analyze_group(group: pd.DataFrame, group_id: str) -> Dict:
    """
    分析单个组（站号+批号）的数据

    Returns:
        分析结果字典
    """
    # 按时间排序
    group = group.sort_values('入库时间').reset_index(drop=True)

    if len(group) < 2:
        return {
            'group_id': group_id,
            'point_count': len(group),
            'error': '数据点少于2个，无法分析'
        }

    results = {
        'group_id': group_id,
        'point_count': len(group),
        'time_range': (group['入库时间'].min(), group['入库时间'].max()),
        'sample_data': [],
    }

    # 分析前10个点（避免输出过多）
    sample_size = min(10, len(group) - 1)

    for i in range(sample_size):
        curr = group.iloc[i]
        next_row = group.iloc[i + 1]

        # 解析时间
        curr_time = pd.to_datetime(curr['入库时间'])
        next_time = pd.to_datetime(next_row['入库时间'])
        time_diff = (next_time - curr_time).total_seconds()

        # 原始数据中的值
        orig_heading = float(curr['航向'])
        orig_speed = float(curr['速度'])

        # 计算实际值
        lat1, lon1 = float(curr['纬度']), float(curr['经度'])
        lat2, lon2 = float(next_row['纬度']), float(next_row['经度'])

        # 计算距离和实际速度
        distance = haversine_distance(lat1, lon1, lat2, lon2)
        actual_speed_mps = calculate_velocity(distance, time_diff)
        actual_speed_knots = actual_speed_mps * 1.94384  # 转换为节
        actual_speed_kmh = actual_speed_mps * 3.6  # 转换为 km/h

        # 计算实际航向
        actual_bearing = calculate_bearing(lat1, lon1, lat2, lon2)

        # 比较航向
        heading_diff = angle_difference(orig_heading, actual_bearing)

        results['sample_data'].append({
            'index': i,
            'time': str(curr_time),
            'orig_heading': orig_heading,
            'actual_heading': actual_bearing,
            'heading_diff': heading_diff,
            'orig_speed': orig_speed,
            'actual_speed_mps': actual_speed_mps,
            'actual_speed_knots': actual_speed_knots,
            'actual_speed_kmh': actual_speed_kmh,
            'time_diff': time_diff,
            'distance': distance,
        })

    # 统计分析
    headings = [d['orig_heading'] for d in results['sample_data']]
    calculated_headings = [d['actual_heading'] for d in results['sample_data']]
    heading_diffs = [d['heading_diff'] for d in results['sample_data']]

    speeds = [d['orig_speed'] for d in results['sample_data']]
    calculated_speeds_knots = [d['actual_speed_knots'] for d in results['sample_data']]
    calculated_speeds_kmh = [d['actual_speed_kmh'] for d in results['sample_data']]

    results['statistics'] = {
        'heading': {
            'original_range': (min(headings), max(headings)),
            'calculated_range': (min(calculated_headings), max(calculated_headings)),
            'avg_difference': np.mean(heading_diffs),
            'max_difference': max(heading_diffs),
        },
        'speed': {
            'original_range': (min(speeds), max(speeds)),
            'calculated_range_knots': (min(calculated_speeds_knots), max(calculated_speeds_knots)),
            'calculated_range_kmh': (min(calculated_speeds_kmh), max(calculated_speeds_kmh)),
        }
    }

    return results


def analyze_all_data(df: pd.DataFrame, max_groups: int = 5, max_samples_per_group: int = 3):
    """
    分析所有数据

    Args:
        df: 数据框
        max_groups: 最大分析组数
        max_samples_per_group: 每组显示的最大样本数
    """
    print("=" * 80)
    print("航向和速度字段分析")
    print("=" * 80)

    # 按站号+批号分组
    df['group_key'] = df['站号'].astype(str) + '_' + df['批号'].astype(str)
    groups = df.groupby('group_key')

    print(f"\n总共有 {len(groups)} 个不同的 站号+批号 组合")
    print(f"将分析前 {min(max_groups, len(groups))} 组数据\n")

    group_count = 0
    all_results = []

    for group_key, group_data in groups:
        if group_count >= max_groups:
            break

        group_id = f"站号:{group_data.iloc[0]['站号']}, 批号:{group_data.iloc[0]['批号']}"
        result = analyze_group(group_data, group_id)

        if 'error' not in result:
            all_results.append(result)
            print(f"\n{'=' * 80}")
            print(f"组 {group_count + 1}: {group_id}")
            print(f"{'=' * 80}")
            print(f"数据点数量: {result['point_count']}")
            print(f"时间范围: {result['time_range'][0]} 到 {result['time_range'][1]}")

            # 打印样本数据
            print(f"\n样本数据（前 {min(max_samples_per_group, len(result['sample_data']))} 个点）:")
            print("-" * 120)
            print(f"{'序号':<6} {'原始航向':<12} {'计算航向':<12} {'航向差':<12} {'原始速度':<12} {'计算速度(节)':<15} {'计算速度(km/h)':<15}")
            print("-" * 120)

            for i, sample in enumerate(result['sample_data'][:max_samples_per_group]):
                print(f"{sample['index']:<6} "
                      f"{sample['orig_heading']:<12.2f} "
                      f"{sample['actual_heading']:<12.2f} "
                      f"{sample['heading_diff']:<12.2f} "
                      f"{sample['orig_speed']:<12.2f} "
                      f"{sample['actual_speed_knots']:<15.2f} "
                      f"{sample['actual_speed_kmh']:<15.2f}")

            # 打印统计信息
            stats = result['statistics']
            print(f"\n统计信息:")
            print(f"  航向:")
            print(f"    原始值范围: [{stats['heading']['original_range'][0]:.2f}, {stats['heading']['original_range'][1]:.2f}]")
            print(f"    计算值范围: [{stats['heading']['calculated_range'][0]:.2f}, {stats['heading']['calculated_range'][1]:.2f}]")
            print(f"    平均差值: {stats['heading']['avg_difference']:.2f} 度")
            print(f"    最大差值: {stats['heading']['max_difference']:.2f} 度")
            print(f"  速度:")
            print(f"    原始值范围: [{stats['speed']['original_range'][0]:.2f}, {stats['speed']['original_range'][1]:.2f}]")
            print(f"    计算值范围(节): [{stats['speed']['calculated_range_knots'][0]:.2f}, {stats['speed']['calculated_range_knots'][1]:.2f}]")
            print(f"    计算值范围(km/h): [{stats['speed']['calculated_range_kmh'][0]:.2f}, {stats['speed']['calculated_range_kmh'][1]:.2f}]")

        group_count += 1

    # 总结分析
    print(f"\n\n{'=' * 80}")
    print("总结分析")
    print("=" * 80)

    if all_results:
        # 分析所有组的航向差异
        all_heading_diffs = []
        all_orig_speeds = []
        all_calc_speeds_knots = []
        all_calc_speeds_kmh = []

        for result in all_results:
            for sample in result['sample_data']:
                all_heading_diffs.append(sample['heading_diff'])
                all_orig_speeds.append(sample['orig_speed'])
                all_calc_speeds_knots.append(sample['actual_speed_knots'])
                all_calc_speeds_kmh.append(sample['actual_speed_kmh'])

        print(f"\n航向分析:")
        print(f"  原始航向字段值范围: [{min(all_orig_speeds):.2f}, {max(all_orig_speeds):.2f}]")
        print(f"  平均航向差值: {np.mean(all_heading_diffs):.2f} 度")
        print(f"  最大航向差值: {max(all_heading_diffs):.2f} 度")

        print(f"\n速度分析:")
        print(f"  原始速度字段值范围: [{min(all_orig_speeds):.2f}, {max(all_orig_speeds):.2f}]")
        print(f"  计算速度范围(节): [{min(all_calc_speeds_knots):.2f}, {max(all_calc_speeds_knots):.2f}]")
        print(f"  计算速度范围(km/h): [{min(all_calc_speeds_kmh):.2f}, {max(all_calc_speeds_kmh):.2f}]")

        # 判断字段含义
        print(f"\n字段含义判断:")
        print(f"  1. 航向字段:")
        if np.mean(all_heading_diffs) > 90:
            print(f"     [X] 原始'航向'字段不是实际的方位角（度）")
            print(f"     可能含义: 其他参数（如：俯仰角、滚转角、或其他）")
        else:
            print(f"     [OK] 原始'航向'字段可能是方位角")

        print(f"  2. 速度字段:")
        speed_ratio_knots = np.mean(all_calc_speeds_knots) / (np.mean(all_orig_speeds) or 1)
        speed_ratio_kmh = np.mean(all_calc_speeds_kmh) / (np.mean(all_orig_speeds) or 1)

        print(f"     计算/原始 比例(节): {speed_ratio_knots:.2f}")
        print(f"     计算/原始 比例(km/h): {speed_ratio_kmh:.2f}")

        if 0.9 < speed_ratio_knots < 1.1:
            print(f"     [OK] 原始'速度'字段单位可能是: 节")
        elif 0.9 < speed_ratio_kmh < 1.1:
            print(f"     [OK] 原始'速度'字段单位可能是: km/h")
        elif 0.4 < speed_ratio_knots < 0.6:
            print(f"     [!] 原始'速度'字段可能约为: 节 * 2")
            print(f"     实际速度(节) ≈ 原始速度 * {speed_ratio_knots:.2f}")
        else:
            print(f"     [?] 原始'速度'字段含义不明确")


def main():
    """主函数"""
    import sys
    from io import StringIO

    # 数据目录
    data_dir = r"D:\myworld\毕设\RFTIP\data"

    # 捕获输出到文件
    output_file = os.path.join(os.path.dirname(__file__), "logs", "analysis_result.txt")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # 重定向输出
    original_stdout = sys.stdout
    sys.stdout = StringIO()

    print("航向和速度字段分析工具")
    print("=" * 80)
    print(f"数据目录: {data_dir}")

    # 加载数据
    df = load_data_files(data_dir)

    # 显示基本信息
    print(f"\n数据基本信息:")
    print(f"  总行数: {len(df)}")
    print(f"  列名: {', '.join(df.columns)}")
    print(f"  唯一站号数: {df['站号'].nunique()}")
    print(f"  唯一批号数: {df['批号'].nunique()}")

    # 显示数据样本
    print(f"\n前3行数据样本:")
    print(df.head(3).to_string())

    # 分析数据
    analyze_all_data(df, max_groups=5, max_samples_per_group=3)

    # 获取输出并写入文件
    output = sys.stdout.getvalue()
    sys.stdout = original_stdout

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output)

    # 同时输出到控制台（安全版本）
    print(output.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore'))
    print(f"\n分析结果已保存到: {output_file}")


if __name__ == "__main__":
    main()
