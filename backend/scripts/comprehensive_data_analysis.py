"""
综合数据分析脚本

分析内容：
1. 同一批号下不同站号的时间差值分布，确定合理的时间窗口参数
2. 分析位置噪音点，提出去除策略
3. 分析数据质量，提出预处理建议
"""
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict
import math


def load_data_files(data_dir: str) -> pd.DataFrame:
    """加载所有数据文件"""
    all_data = []

    for filename in sorted(os.listdir(data_dir)):
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


def analyze_time_differences(df: pd.DataFrame):
    """
    分析同一批号下不同站号的时间差值

    目标：确定合理的时间窗口参数，用于将"近似同时"的观测点分组
    """
    print("\n" + "=" * 80)
    print("一、时间差值分析")
    print("=" * 80)

    # 解析时间戳
    df['timestamp'] = pd.to_datetime(df['入库时间'])

    # 按批号分组
    grouped = df.groupby('批号')

    time_diffs = []
    batch_stats = []

    for batch_id, group in grouped:
        if len(group) < 2:
            continue

        # 按时间排序
        group = group.sort_values('timestamp')

        # 计算该批号内所有时间点之间的差值
        timestamps = group['timestamp'].values
        n = len(timestamps)

        for i in range(n):
            for j in range(i + 1, n):
                diff = abs((timestamps[i] - timestamps[j]))
                # 转换 numpy timedelta64 为秒
                if hasattr(diff, 'astype'):
                    diff = diff.astype('timedelta64[s]').astype(int)
                else:
                    diff = diff.total_seconds()
                time_diffs.append(diff)

        # 统计该批号的时间范围
        time_range = timestamps[-1] - timestamps[0]
        # 转换 numpy timedelta64 为秒
        if hasattr(time_range, 'astype'):
            time_range_seconds = time_range.astype('timedelta64[s]').astype(int)
        else:
            time_range_seconds = time_range.total_seconds()
        station_count = group['站号'].nunique()

        batch_stats.append({
            'batch_id': batch_id,
            'point_count': len(group),
            'station_count': station_count,
            'time_range_seconds': int(time_range_seconds),
            'time_range_str': str(timedelta(seconds=int(time_range_seconds))),
        })

    time_diffs = np.array(time_diffs)

    print(f"\n总共有 {len(time_diffs):,} 个时间差值对")

    # 统计分析
    print(f"\n时间差值统计（秒）:")
    print(f"  最小值: {np.min(time_diffs):.6f} 秒")
    print(f"  5%分位: {np.percentile(time_diffs, 5):.6f} 秒")
    print(f"  10%分位: {np.percentile(time_diffs, 10):.6f} 秒")
    print(f"  25%分位: {np.percentile(time_diffs, 25):.6f} 秒")
    print(f"  50%分位(中位数): {np.percentile(time_diffs, 50):.6f} 秒")
    print(f"  75%分位: {np.percentile(time_diffs, 75):.6f} 秒")
    print(f"  90%分位: {np.percentile(time_diffs, 90):.6f} 秒")
    print(f"  95%分位: {np.percentile(time_diffs, 95):.6f} 秒")
    print(f"  99%分位: {np.percentile(time_diffs, 99):.6f} 秒")
    print(f"  最大值: {np.max(time_diffs):.6f} 秒")

    # 分析分布
    print(f"\n时间差值分布:")
    print(f"  < 0.1秒: {np.sum(time_diffs < 0.1):,} ({np.sum(time_diffs < 0.1) / len(time_diffs) * 100:.2f}%)")
    print(f"  < 0.5秒: {np.sum(time_diffs < 0.5):,} ({np.sum(time_diffs < 0.5) / len(time_diffs) * 100:.2f}%)")
    print(f"  < 1秒: {np.sum(time_diffs < 1):,} ({np.sum(time_diffs < 1) / len(time_diffs) * 100:.2f}%)")
    print(f"  < 2秒: {np.sum(time_diffs < 2):,} ({np.sum(time_diffs < 2) / len(time_diffs) * 100:.2f}%)")
    print(f"  < 5秒: {np.sum(time_diffs < 5):,} ({np.sum(time_diffs < 5) / len(time_diffs) * 100:.2f}%)")
    print(f"  < 10秒: {np.sum(time_diffs < 10):,} ({np.sum(time_diffs < 10) / len(time_diffs) * 100:.2f}%)")
    print(f"  > 60秒: {np.sum(time_diffs > 60):,} ({np.sum(time_diffs > 60) / len(time_diffs) * 100:.2f}%)")

    # 批号时间范围统计
    print(f"\n批号时间范围统计（前10个）:")
    batch_stats_df = pd.DataFrame(batch_stats).sort_values('time_range_seconds')
    for i, row in batch_stats_df.head(10).iterrows():
        print(f"  批号 {row['batch_id']}: {row['point_count']} 点, {row['station_count']} 站, 时间范围 {row['time_range_str']}")

    # 时间窗口建议
    print(f"\n" + "-" * 80)
    print("时间窗口参数建议:")
    print("-" * 80)

    # 基于95%分位数建议
    window_95 = np.percentile(time_diffs, 95)
    window_99 = np.percentile(time_diffs, 99)

    print(f"\n方案1: 基于95%分位数")
    print(f"  时间窗口: {window_95:.3f} 秒")
    print(f"  说明: 能覆盖95%的同时观测对")
    print(f"  优点: 较严格，能较好地区分不同时间点")
    print(f"  缺点: 可能遗漏一些稍有不同的观测")

    print(f"\n方案2: 基于99%分位数")
    print(f"  时间窗口: {window_99:.3f} 秒")
    print(f"  说明: 能覆盖99%的同时观测对")
    print(f"  优点: 覆盖更多观测")
    print(f"  缺点: 可能混入不同时间的观测")

    # 基于分布分析建议
    # 找到一个"拐点"，即大部分差值都在某个范围内
    diff_threshold_1 = 1.0  # 1秒
    diff_threshold_2 = 2.0  # 2秒
    diff_threshold_3 = 5.0  # 5秒

    within_1s = np.sum(time_diffs <= diff_threshold_1)
    within_2s = np.sum(time_diffs <= diff_threshold_2)
    within_5s = np.sum(time_diffs <= diff_threshold_3)

    print(f"\n方案3: 固定阈值（推荐）")
    print(f"  1秒窗口: 覆盖 {within_1s / len(time_diffs) * 100:.2f}% 的观测对")
    print(f"  2秒窗口: 覆盖 {within_2s / len(time_diffs) * 100:.2f}% 的观测对")
    print(f"  5秒窗口: 覆盖 {within_5s / len(time_diffs) * 100:.2f}% 的观测对")
    print(f"\n  推荐: 使用 **2秒窗口** 作为RANSAC分组的时间阈值")
    print(f"  理由:")
    print(f"    - 覆盖了 {within_2s / len(time_diffs) * 100:.2f}% 的同时观测")
    print(f"    - 既能容忍雷达站间的时间不同步")
    print(f"    - 又不会混入不同时间的观测点")

    return {
        'time_diffs': time_diffs,
        'percentile_95': window_95,
        'percentile_99': window_99,
        'recommended_window': 2.0,  # 推荐值
    }


def analyze_position_noise(df: pd.DataFrame):
    """
    分析位置噪音点

    检测异常位置值：
    1. 位置突变（相邻点间距离过大）
    2. 速度异常（计算出的速度不合理）
    """
    print("\n" + "=" * 80)
    print("二、位置噪音分析")
    print("=" * 80)

    df['timestamp'] = pd.to_datetime(df['入库时间'])

    # 按站号+批号分组分析
    df['group_key'] = df['站号'].astype(str) + '_' + df['批号'].astype(str)
    groups = df.groupby('group_key')

    all_distances = []
    all_speeds = []
    noise_candidates = []

    for group_key, group in groups:
        if len(group) < 2:
            continue

        group = group.sort_values('timestamp').reset_index(drop=True)

        for i in range(len(group) - 1):
            curr = group.iloc[i]
            next_row = group.iloc[i + 1]

            # 计算距离
            distance = haversine_distance(
                curr['纬度'], curr['经度'],
                next_row['纬度'], next_row['经度']
            )

            # 计算时间差
            time_diff = (pd.to_datetime(next_row['入库时间']) - pd.to_datetime(curr['入库时间'])).total_seconds()

            if time_diff > 0:
                speed = distance / time_diff  # 米/秒
                speed_kmh = speed * 3.6
                all_speeds.append(speed)
            else:
                speed = 0
                speed_kmh = 0

            all_distances.append(distance)

            # 检测异常
            is_noise = False
            noise_reason = []

            # 1. 距离异常（>10km）
            if distance > 10000:
                is_noise = True
                noise_reason.append(f"距离过大: {distance:.0f}m")

            # 2. 速度异常（>1000 km/h）
            if speed_kmh > 1000:
                is_noise = True
                noise_reason.append(f"速度过高: {speed_kmh:.0f}km/h")

            # 3. 位置突变（相对平均距离）
            if len(all_distances) > 10:
                avg_distance = np.mean(all_distances[-10:])
                if distance > avg_distance * 5:
                    is_noise = True
                    noise_reason.append(f"相对距离突增: {distance / avg_distance:.1f}x平均")

            if is_noise:
                noise_candidates.append({
                    'group_key': group_key,
                    'index': i,
                    'timestamp': curr['入库时间'],
                    'lat': curr['纬度'],
                    'lon': curr['经度'],
                    'distance': distance,
                    'speed_kmh': speed_kmh,
                    'reasons': noise_reason,
                })

    all_distances = np.array(all_distances)
    all_speeds = np.array(all_speeds)

    print(f"\n距离统计（相邻点间）:")
    print(f"  平均距离: {np.mean(all_distances):.1f} 米")
    print(f"  中位数: {np.median(all_distances):.1f} 米")
    print(f"  标准差: {np.std(all_distances):.1f} 米")
    print(f"  最大值: {np.max(all_distances):.1f} 米")
    print(f"  > 1km: {np.sum(all_distances > 1000)} ({np.sum(all_distances > 1000) / len(all_distances) * 100:.2f}%)")
    print(f"  > 5km: {np.sum(all_distances > 5000)} ({np.sum(all_distances > 5000) / len(all_distances) * 100:.2f}%)")
    print(f"  > 10km: {np.sum(all_distances > 10000)} ({np.sum(all_distances > 10000) / len(all_distances) * 100:.2f}%)")

    print(f"\n速度统计（从位置计算）:")
    print(f"  平均速度: {np.mean(all_speeds):.1f} 米/秒 ({np.mean(all_speeds) * 3.6:.1f} km/h)")
    print(f"  中位数: {np.median(all_speeds):.1f} 米/秒 ({np.median(all_speeds) * 3.6:.1f} km/h)")
    print(f"  标准差: {np.std(all_speeds):.1f} 米/秒")
    print(f"  > 500 km/h: {np.sum(all_speeds * 3.6 > 500)} ({np.sum(all_speeds * 3.6 > 500) / len(all_speeds) * 100:.2f}%)")
    print(f"  > 1000 km/h: {np.sum(all_speeds * 3.6 > 1000)} ({np.sum(all_speeds * 3.6 > 1000) / len(all_speeds) * 100:.2f}%)")

    print(f"\n噪音候选点: {len(noise_candidates)}")
    if noise_candidates:
        print(f"\n噪音候选点示例（前10个）:")
        for i, noise in enumerate(noise_candidates[:10]):
            print(f"  {i+1}. 批号:{noise['group_key']} 时间:{noise['timestamp']}")
            print(f"     位置:({noise['lat']:.4f}, {noise['lon']:.4f})")
            print(f"     距离:{noise['distance']:.0f}m, 速度:{noise['speed_kmh']:.0f}km/h")
            print(f"     原因: {', '.join(noise['reasons'])}")

    # 噪音去除建议
    print(f"\n" + "-" * 80)
    print("噪音去除策略建议:")
    print("-" * 80)

    print(f"\n1. 速度过滤（推荐）")
    print(f"   阈值: 800 km/h (约 222 米/秒)")
    print(f"   说明: 民航客机巡航速度约 800-900 km/h")
    print(f"   预计过滤: {np.sum(all_speeds * 3.6 > 800)} 个点 ({np.sum(all_speeds * 3.6 > 800) / len(all_speeds) * 100:.2f}%)")

    print(f"\n2. 距离突变检测")
    print(f"   阈值: 超过中位距离的 5 倍")
    print(f"   说明: 检测突然的位置跳变")
    median_distance = np.median(all_distances)
    far_points = np.sum(all_distances > median_distance * 5)
    print(f"   预计过滤: 约 {far_points} 个点")

    print(f"\n3. RANSAC 内点筛选")
    print(f"   说明: 在多站观测时，RANSAC 会自动筛选出一致的内点")
    print(f"   参数建议: residual_threshold=0.5, min_samples=2")

    return {
        'noise_candidates': noise_candidates,
        'speed_threshold': 800,  # km/h
        'distance_outlier_threshold': 5,  # x 中位数
    }


def haversine_distance(lat1, lon1, lat2, lon2):
    """计算两点之间的球面距离（米）"""
    R = 6371000
    lat1_rad, lat2_rad = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (math.sin(dlat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) *
         math.sin(dlon / 2) ** 2)

    c = 2 * math.asin(math.sqrt(a))
    return R * c


def analyze_multi_station_sync(df: pd.DataFrame, time_window: float = 2.0):
    """
    分析多站同步情况

    使用给定的时间窗口，分析：
    1. 有多少观测是真正"同时"的（多站观测同一目标）
    2. 有多少观测是单站的
    """
    print("\n" + "=" * 80)
    print(f"三、多站同步分析（时间窗口: {time_window}秒）")
    print("=" * 80)

    df['timestamp'] = pd.to_datetime(df['入库时间'])

    # 按批号分组
    grouped = df.groupby('批号')

    single_obs = 0
    multi_obs = 0
    multi_obs_details = []

    for batch_id, group in grouped:
        group = group.sort_values('timestamp')

        # 使用时间窗口分组
        time_groups = []
        current_group = [group.iloc[0]]

        for i in range(1, len(group)):
            curr = group.iloc[i]
            prev = current_group[0]

            time_diff = (pd.to_datetime(curr['入库时间']) - pd.to_datetime(prev['入库时间'])).total_seconds()

            if time_diff <= time_window:
                current_group.append(curr)
            else:
                time_groups.append(current_group)
                current_group = [curr]

        if current_group:
            time_groups.append(current_group)

        # 统计
        for tg in time_groups:
            stations = len(set([row['站号'] for row in tg]))
            if stations >= 2:
                multi_obs += 1
                multi_obs_details.append({
                    'batch_id': batch_id,
                    'station_count': stations,
                    'point_count': len(tg),
                    'time_span': (pd.to_datetime(tg[-1]['入库时间']) - pd.to_datetime(tg[0]['入库时间'])).total_seconds(),
                })
            else:
                single_obs += len(tg)

    total = single_obs + multi_obs

    print(f"\n同步观测统计:")
    print(f"  单站观测: {single_obs:,} ({single_obs / total * 100:.2f}%)")
    print(f"  多站观测: {multi_obs:,} ({multi_obs / total * 100:.2f}%)")

    # 多站观测的站数分布
    if multi_obs_details:
        station_dist = defaultdict(int)
        for detail in multi_obs_details:
            station_dist[detail['station_count']] += 1

        print(f"\n多站观测的站数分布:")
        for station_count in sorted(station_dist.keys()):
            count = station_dist[station_count]
            print(f"  {station_count} 站: {count:,} 次 ({count / sum(station_dist.values()) * 100:.2f}%)")

    print(f"\n结论:")
    print(f"  - 使用 {time_window} 秒时间窗口，{multi_obs / total * 100:.2f}% 的观测可进行多站RANSAC修正")
    print(f"  - {single_obs / total * 100:.2f}% 的观测为单站，需要使用卡尔曼滤波")

    return {
        'single_obs': single_obs,
        'multi_obs': multi_obs,
        'multi_ratio': multi_obs / total if total > 0 else 0,
    }


def generate_preprocessing_config(time_analysis, noise_analysis):
    """生成预处理配置建议"""
    print("\n" + "=" * 80)
    print("四、预处理配置建议")
    print("=" * 80)

    config = {
        'time_window': {
            'description': '多站观测时间窗口（秒）',
            'value': time_analysis['recommended_window'],
            'reason': f'基于时间差分析，推荐使用 {time_analysis["recommended_window"]} 秒窗口'
        },
        'noise_filtering': {
            'speed_threshold_km': {
                'description': '速度阈值（去除异常速度点）',
                'value': noise_analysis['speed_threshold'],
                'unit': 'km/h',
                'reason': f'民航客机正常巡航速度约 800-900 km/h'
            },
            'distance_outlier_factor': {
                'description': '距离异常倍数',
                'value': noise_analysis['distance_outlier_threshold'],
                'unit': 'x中位数',
                'reason': '超过中位数距离N倍的点视为异常'
            }
        },
        'ransac_params': {
            'residual_threshold': {
                'description': 'RANSAC残差阈值',
                'value': 0.5,
                'unit': '度',
                'reason': '用于判断内点/离群点的阈值'
            },
            'min_samples': {
                'description': 'RANSAC最小样本数',
                'value': 2,
                'unit': '站',
                'reason': '至少需要2个雷达站的观测'
            }
        }
    }

    print("\n推荐配置:")
    print("\n1. 时间窗口设置:")
    print(f"   TIME_WINDOW = {config['time_window']['value']} 秒")
    print(f"   // {config['time_window']['reason']}")

    print("\n2. 噪音过滤设置:")
    print(f"   MAX_SPEED = {config['noise_filtering']['speed_threshold_km']['value']} km/h")
    print(f"   // {config['noise_filtering']['speed_threshold_km']['reason']}")
    print(f"   DISTANCE_OUTLIER_FACTOR = {config['noise_filtering']['distance_outlier_factor']['value']}")
    print(f"   // {config['noise_filtering']['distance_outlier_factor']['reason']}")

    print("\n3. RANSAC参数:")
    print(f"   RESIDUAL_THRESHOLD = {config['ransac_params']['residual_threshold']['value']}")
    print(f"   // {config['ransac_params']['residual_threshold']['reason']}")
    print(f"   MIN_SAMPLES = {config['ransac_params']['min_samples']['value']}")
    print(f"   // {config['ransac_params']['min_samples']['reason']}")

    return config


def main():
    """主函数"""
    import sys
    from io import StringIO

    data_dir = r"D:\myworld\毕设\RFTIP\data"

    # 输出文件
    output_file = os.path.join(os.path.dirname(__file__), "logs", "comprehensive_analysis.txt")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # 重定向输出
    original_stdout = sys.stdout
    sys.stdout = StringIO()

    print("综合数据分析工具")
    print("=" * 80)
    print(f"数据目录: {data_dir}")
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 加载数据
    df = load_data_files(data_dir)

    print(f"\n数据基本信息:")
    print(f"  总行数: {len(df):,}")
    print(f"  唯一批号数: {df['批号'].nunique()}")
    print(f"  唯一站号数: {df['站号'].nunique()}")

    # 1. 时间差值分析
    time_analysis = analyze_time_differences(df)

    # 2. 位置噪音分析
    noise_analysis = analyze_position_noise(df)

    # 3. 多站同步分析
    sync_analysis = analyze_multi_station_sync(df, time_window=time_analysis['recommended_window'])

    # 4. 生成配置建议
    config = generate_preprocessing_config(time_analysis, noise_analysis)

    # 获取输出并保存
    output = sys.stdout.getvalue()
    sys.stdout = original_stdout

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output)

    # 输出到控制台
    print(output.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore'))
    print(f"\n分析结果已保存到: {output_file}")


if __name__ == "__main__":
    main()
