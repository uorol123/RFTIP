"""
误差计算模块

负责计算和优化雷达系统误差
"""
import copy
import math
import numpy as np
import pyproj
from typing import Dict, List, Tuple, Optional

from app.algorithms.multi_source.preprocessing.config import MrraConfig
from core.logging import get_logger

logger = get_logger(__name__)

# 初始化地理坐标转换器（WGS84椭球）
geod = pyproj.Geod(ellps='WGS84')


class ErrorCalculator:
    """
    误差计算器类

    计算方位角、距离和俯仰角误差
    """

    def __init__(self, config: MrraConfig):
        """
        初始化误差计算器

        Args:
            config: MRRA 配置
        """
        self.config = config

    def calculate_cost(
        self,
        match_groups: List[List[Dict]],
        azimuth_errors: Dict[int, float],
        radar_positions: Dict[int, Tuple],
        range_errors: Optional[Dict[int, float]] = None,
    ) -> float:
        """
        计算综合代价函数，同时考虑方位角和距离误差

        Args:
            match_groups: 匹配组列表
            azimuth_errors: 各雷达站的方位角误差（单位：度）
            radar_positions: 雷达站位置（可以是二维或三维）
            range_errors: 各站的距离误差（单位：米），可选

        Returns:
            综合代价值
        """
        if not match_groups:
            return 0.0

        # 如果没有距离误差字典，则默认全为0
        if range_errors is None:
            range_errors = {sid: 0.0 for sid in azimuth_errors.keys()}

        variances: List[float] = []

        for group in match_groups:
            corrected_positions: List[Tuple[float, float]] = []
            for point in group:
                sid = point['station_id']
                lon, lat = point['longitude'], point['latitude']

                if sid not in radar_positions:
                    continue

                # 处理二维或三维的雷达位置
                pos = radar_positions[sid]
                if len(pos) >= 2:
                    r_lon, r_lat = pos[0], pos[1]
                else:
                    continue

                # 计算方位角和距离
                az, back_az, dist = geod.inv(r_lon, r_lat, lon, lat)
                da = azimuth_errors.get(sid, 0.0)
                dr = range_errors.get(sid, 0.0)

                # 方位角误差为观测角减去误差，距离误差为观测距离加上误差
                corr_az = az - da
                corr_dist = dist - dr
                new_lon, new_lat, _ = geod.fwd(r_lon, r_lat, corr_az, corr_dist)
                corrected_positions.append((new_lon, new_lat))

            if len(corrected_positions) < 2:
                continue

            coords = np.array(corrected_positions)
            mean_coords = coords.mean(axis=0)
            diffs = coords - mean_coords
            var = float(np.sqrt((diffs ** 2).sum(axis=1).mean()))
            variances.append(var)

        if not variances:
            return 0.0

        variance_cost = float(np.mean(variances))
        az_values = np.array(list(azimuth_errors.values())) if azimuth_errors else np.array([0.0])
        r_values = np.array(list(range_errors.values())) if range_errors else np.array([0.0])
        az_sq = float(np.mean(az_values ** 2))
        r_sq = float(np.mean(r_values ** 2))

        total_cost = (
            self.config.cost_weights.variance * variance_cost
            + self.config.cost_weights.azimuth_error_square * az_sq
            + self.config.cost_weights.range_error_square * r_sq
        )
        return total_cost

    def optimize_azimuth_errors(
        self,
        match_groups: List[List[Dict]],
        initial_azimuth_errors: Dict[int, float],
        radar_positions: Dict[int, Tuple[float, float]],
        range_errors: Dict[int, float]
    ) -> Dict[int, float]:
        """
        仅优化方位角误差，距离误差固定

        Args:
            match_groups: 匹配组列表
            initial_azimuth_errors: 初始方位角误差字典
            radar_positions: 雷达站位置字典
            range_errors: 固定的距离误差字典

        Returns:
            优化后的方位角误差字典
        """
        logger.info("开始方位角误差优化...")

        # 限制匹配组数量
        if len(match_groups) > self.config.max_match_groups:
            match_groups = match_groups[:self.config.max_match_groups]
            logger.info(f"限制匹配组数量为: {self.config.max_match_groups}")

        # 初始化最佳解
        stations = list(initial_azimuth_errors.keys())
        best_az = copy.deepcopy(initial_azimuth_errors)
        best_cost = self.calculate_cost(match_groups, best_az, radar_positions, range_errors)

        logger.info(f"方位角误差初始代价: {best_cost:.6f}")
        logger.info(f"方位角误差初始值: {best_az}")
        logger.info(f"处理 {len(match_groups)} 个匹配组")
        logger.info(f"雷达站数量: {len(stations)}")

        # 方位角误差优化
        step_count = 0
        for step_az in self.config.optimization_steps:
            logger.info(f"方位角优化步长 {step_az}° 开始")
            improved = True
            iteration = 0

            while improved:
                iteration += 1
                improved = False

                # 遍历每个站点
                for sid in stations:
                    step_count += 1
                    # 尝试正负两个方向
                    for delta_az in [step_az, -step_az]:
                        temp_az = copy.deepcopy(best_az)
                        temp_az[sid] += delta_az
                        cost = self.calculate_cost(match_groups, temp_az, radar_positions, range_errors)

                        if cost < best_cost:
                            best_cost = cost
                            best_az = temp_az
                            improved = True
                            logger.info(f"方位角优化 站{sid}: +{delta_az:.3f}° → 代价:{best_cost:.6f}")

                # 如果没有改进，跳出循环
                if not improved:
                    logger.info(f"方位角步长 {step_az}° 收敛，迭代 {iteration} 次")
                    break
                elif iteration % 5 == 0:
                    logger.info(f"方位角步长 {step_az}° 迭代{iteration}: 当前代价 {best_cost:.6f}")

        logger.info("方位角误差优化完成")
        logger.info(f"总步数: {step_count}")
        logger.info(f"最终方位角误差: {best_az}")
        logger.info(f"方位角误差优化后代价: {best_cost:.6f}")

        return best_az

    def optimize_range_errors(
        self,
        match_groups: List[List[Dict]],
        azimuth_errors: Dict[int, float],
        radar_positions: Dict[int, Tuple[float, float]],
        initial_range_errors: Dict[int, float]
    ) -> Dict[int, float]:
        """
        仅优化距离误差，方位角误差固定

        Args:
            match_groups: 匹配组列表
            azimuth_errors: 固定的方位角误差字典
            radar_positions: 雷达站位置字典
            initial_range_errors: 初始距离误差字典

        Returns:
            优化后的距离误差字典
        """
        logger.info("开始距离误差优化...")

        # 限制匹配组数量
        if len(match_groups) > self.config.max_match_groups:
            match_groups = match_groups[:self.config.max_match_groups]

        # 初始化最佳解
        stations = list(azimuth_errors.keys())
        best_r = copy.deepcopy(initial_range_errors)
        best_cost = self.calculate_cost(match_groups, azimuth_errors, radar_positions, best_r)

        logger.info(f"距离误差初始代价: {best_cost:.6f}")
        logger.info(f"距离误差初始值: {best_r}")
        logger.info(f"距离优化步长序列: {self.config.range_optimization_steps}")

        # 距离误差优化
        step_count = 0
        for step_r in self.config.range_optimization_steps:
            logger.info(f"距离优化步长 {step_r}m 开始")
            improved = True
            iteration = 0

            while improved:
                iteration += 1
                improved = False

                # 遍历每个站点
                for sid in stations:
                    step_count += 1
                    # 尝试正负两个方向
                    for delta_r in [step_r, -step_r]:
                        temp_r = copy.deepcopy(best_r)
                        temp_r[sid] += delta_r
                        cost = self.calculate_cost(match_groups, azimuth_errors, radar_positions, temp_r)

                        if cost < best_cost:
                            best_cost = cost
                            best_r = temp_r
                            improved = True
                            logger.info(f"距离优化 站{sid}: +{delta_r:.1f}m → 代价:{best_cost:.6f}")

                # 如果没有改进，跳出循环
                if not improved:
                    logger.info(f"距离步长 {step_r}m 收敛，迭代 {iteration} 次")
                    break
                elif iteration % 5 == 0:
                    logger.info(f"距离步长 {step_r}m 迭代{iteration}: 当前代价 {best_cost:.6f}")

        logger.info("距离误差优化完成")
        logger.info(f"总步数: {step_count}")
        logger.info(f"最终距离误差: {best_r}")
        logger.info(f"距离误差优化后代价: {best_cost:.6f}")

        return best_r

    def calculate_cost_with_elevation(
        self,
        match_groups: List[List[Dict]],
        azimuth_errors: Dict[int, float],
        range_errors: Dict[int, float],
        elevation_errors: Dict[int, float],
        radar_positions: Dict[int, Tuple],
    ) -> float:
        """
        计算综合代价函数，同时考虑方位角、距离和俯仰角误差

        Args:
            match_groups: 匹配组列表
            azimuth_errors: 各雷达站的方位角误差（单位：度）
            range_errors: 各站的距离误差（单位：米）
            elevation_errors: 各站的俯仰角误差（单位：度）
            radar_positions: 雷达站位置（包含高度）

        Returns:
            综合代价值
        """
        if not match_groups:
            return 0.0

        variances_2d: List[float] = []
        variances_alt: List[float] = []
        variances_3d: List[float] = []

        for group in match_groups:
            if len(group) < 2:
                continue

            corrected_positions_2d: List[Tuple[float, float]] = []
            corrected_altitudes: List[float] = []
            corrected_positions_3d: List[Tuple[float, float, float]] = []

            for point in group:
                sid = point['station_id']
                lon, lat, alt = point['longitude'], point['latitude'], point.get('altitude', 0.0)

                if sid not in radar_positions:
                    continue

                # 获取雷达站位置和高度
                pos = radar_positions[sid]
                if len(pos) >= 3:
                    r_lon, r_lat, r_alt = pos[0], pos[1], pos[2]
                else:
                    continue

                # 计算方位角、距离
                az, back_az, dist = geod.inv(r_lon, r_lat, lon, lat)

                # 计算原始俯仰角
                dx = (lon - r_lon) * 111000 * math.cos(math.radians(r_lat))
                dy = (lat - r_lat) * 111000
                horizontal_dist = math.sqrt(dx ** 2 + dy ** 2)
                height_diff = alt - r_alt

                # 计算原始俯仰角
                if horizontal_dist > 0:
                    original_elevation = math.degrees(math.atan2(height_diff, horizontal_dist))
                else:
                    original_elevation = 0.0

                # 应用误差修正
                da = azimuth_errors.get(sid, 0.0)
                dr = range_errors.get(sid, 0.0)
                de = elevation_errors.get(sid, 0.0)

                # 修正后的方位角和距离
                corr_az = az - da
                corr_dist = dist - dr

                # 修正后的俯仰角
                corr_elevation = original_elevation - de

                # 计算修正后的位置（2D）
                new_lon, new_lat, _ = geod.fwd(r_lon, r_lat, corr_az, corr_dist)

                # 计算修正后的高度
                if corr_dist > 0:
                    new_alt = r_alt + corr_dist * math.sin(math.radians(corr_elevation))
                else:
                    new_alt = alt

                corrected_positions_2d.append((new_lon, new_lat))
                corrected_altitudes.append(new_alt)
                corrected_positions_3d.append((new_lon, new_lat, new_alt))

            # 计算2D方差
            if len(corrected_positions_2d) >= 2:
                coords_2d = np.array(corrected_positions_2d)
                mean_coords_2d = coords_2d.mean(axis=0)
                diffs_2d = coords_2d - mean_coords_2d
                var_2d = float(np.sqrt((diffs_2d ** 2).sum(axis=1).mean()))
                variances_2d.append(var_2d)

            # 计算高度方差
            if len(corrected_altitudes) >= 2:
                alts = np.array(corrected_altitudes)
                mean_alt = alts.mean()
                var_alt = float(np.sqrt(((alts - mean_alt) ** 2).mean()))
                variances_alt.append(var_alt)

            # 计算3D方差
            if len(corrected_positions_3d) >= 2:
                coords_3d = []
                for lon, lat, alt in corrected_positions_3d:
                    x = lon * 111000 * math.cos(math.radians(lat))
                    y = lat * 111000
                    coords_3d.append([x, y, alt])

                coords_3d = np.array(coords_3d)
                mean_coords_3d = coords_3d.mean(axis=0)
                diffs_3d = coords_3d - mean_coords_3d
                var_3d = float(np.sqrt((diffs_3d ** 2).sum(axis=1).mean()))
                variances_3d.append(var_3d)

        if not variances_2d:
            return float('inf')

        # 计算各项代价
        variance_3d_cost = float(np.mean(variances_3d)) if variances_3d else 0.0

        az_values = np.array(list(azimuth_errors.values())) if azimuth_errors else np.array([0.0])
        r_values = np.array(list(range_errors.values())) if range_errors else np.array([0.0])
        elev_values = np.array(list(elevation_errors.values())) if elevation_errors else np.array([0.0])

        az_sq = float(np.mean(az_values ** 2))
        r_sq = float(np.mean(r_values ** 2))
        elev_sq = float(np.mean(elev_values ** 2))

        # 综合代价
        total_cost = (
            self.config.cost_weights.variance * variance_3d_cost
            + self.config.cost_weights.azimuth_error_square * az_sq
            + self.config.cost_weights.range_error_square * r_sq
            + self.config.cost_weights.elevation_error_square * elev_sq
        )

        return total_cost

    def optimize_elevation_errors(
        self,
        match_groups: List[List[Dict]],
        azimuth_errors: Dict[int, float],
        range_errors: Dict[int, float],
        radar_positions: Dict[int, Tuple[float, float, float]],
        initial_elevation_errors: Dict[int, float]
    ) -> Dict[int, float]:
        """
        优化俯仰角误差，固定方位角和距离误差

        Args:
            match_groups: 匹配组列表
            azimuth_errors: 固定的方位角误差字典
            range_errors: 固定的距离误差字典
            radar_positions: 雷达站位置字典（包含高度）
            initial_elevation_errors: 初始俯仰角误差字典

        Returns:
            优化后的俯仰角误差字典
        """
        logger.info("开始俯仰角误差优化...")

        # 限制匹配组数量
        if len(match_groups) > self.config.max_match_groups:
            match_groups = match_groups[:self.config.max_match_groups]

        # 初始化最佳解
        stations = list(azimuth_errors.keys())
        best_elev = copy.deepcopy(initial_elevation_errors)
        best_cost = self.calculate_cost_with_elevation(
            match_groups, azimuth_errors, range_errors, best_elev, radar_positions
        )

        logger.info(f"俯仰角误差初始代价: {best_cost:.6f}")
        logger.info(f"俯仰角误差初始值: {best_elev}")

        # 俯仰角误差优化
        step_count = 0
        for step_elev in self.config.optimization_steps:
            logger.info(f"俯仰角优化步长 {step_elev}° 开始")
            improved = True
            iteration = 0

            while improved:
                iteration += 1
                improved = False

                # 遍历每个站点
                for sid in stations:
                    step_count += 1
                    # 尝试正负两个方向
                    for delta_elev in [step_elev, -step_elev]:
                        temp_elev = copy.deepcopy(best_elev)
                        temp_elev[sid] += delta_elev
                        cost = self.calculate_cost_with_elevation(
                            match_groups, azimuth_errors, range_errors, temp_elev, radar_positions
                        )

                        if cost < best_cost:
                            best_cost = cost
                            best_elev = temp_elev
                            improved = True
                            logger.info(f"俯仰角优化 站{sid}: +{delta_elev:.3f}° → 代价:{best_cost:.6f}")

                # 如果没有改进，跳出循环
                if not improved:
                    logger.info(f"俯仰角步长 {step_elev}° 收敛，迭代 {iteration} 次")
                    break
                elif iteration % 5 == 0:
                    logger.info(f"俯仰角步长 {step_elev}° 迭代{iteration}: 当前代价 {best_cost:.6f}")

        logger.info("俯仰角误差优化完成")
        logger.info(f"总步数: {step_count}")
        logger.info(f"最终俯仰角误差: {best_elev}")
        logger.info(f"俯仰角误差优化后代价: {best_cost:.6f}")

        return best_elev

    def calculate_radar_errors(
        self,
        match_groups: List[List[Dict]],
        radar_positions: Dict[int, Tuple[float, float, float]],
    ) -> Dict[int, Tuple[float, float, float]]:
        """
        计算各雷达站的方位角、距离和俯仰角误差

        Args:
            match_groups: 匹配组列表
            radar_positions: 雷达站位置字典（包含高度）

        Returns:
            站号 -> (方位角误差, 距离误差, 俯仰角误差) 的字典
        """
        logger.info("开始分模块误差计算...")
        logger.info(f"共有 {len(match_groups)} 个匹配组")
        logger.info(f"处理雷达站: {list(radar_positions.keys())}")

        # 初始化误差
        initial_azimuth_errors = {sid: 0.0 for sid in radar_positions.keys()}
        initial_range_errors = {sid: 0.0 for sid in radar_positions.keys()}
        initial_elevation_errors = {sid: 0.0 for sid in radar_positions.keys()}

        # 创建只包含经纬度的雷达位置字典
        radar_positions_2d = {sid: (lon, lat) for sid, (lon, lat, alt) in radar_positions.items()}

        logger.info("=== 步骤1: 计算方位角误差 ===")
        optimized_az = self.optimize_azimuth_errors(
            match_groups,
            initial_azimuth_errors,
            radar_positions_2d,
            {sid: 0.0 for sid in initial_azimuth_errors.keys()}
        )

        logger.info("=== 步骤2: 计算距离误差 ===")
        optimized_r = self.optimize_range_errors(
            match_groups,
            optimized_az,
            radar_positions_2d,
            initial_range_errors
        )

        logger.info("=== 步骤3: 计算俯仰角误差 ===")
        optimized_elev = self.optimize_elevation_errors(
            match_groups,
            optimized_az,
            optimized_r,
            radar_positions,
            initial_elevation_errors
        )

        # 计算最终综合代价
        final_cost = self.calculate_cost_with_elevation(
            match_groups, optimized_az, optimized_r, optimized_elev, radar_positions
        )

        logger.info("=== 误差计算总结 ===")
        logger.info(f"方位角误差最终结果: {optimized_az}")
        logger.info(f"距离误差最终结果: {optimized_r}")
        logger.info(f"俯仰角误差最终结果: {optimized_elev}")
        logger.info(f"综合最终代价: {final_cost:.6f}")

        # 输出每个雷达站的详细误差
        logger.info("各雷达站详细误差:")
        for sid in radar_positions.keys():
            az_err = optimized_az.get(sid, 0.0)
            range_err = optimized_r.get(sid, 0.0)
            elev_err = optimized_elev.get(sid, 0.0)
            logger.info(f"  雷达站 {sid}: 方位角={az_err:.3f}°, 距离={range_err:.1f}m, 俯仰角={elev_err:.3f}°")

        # 组合误差
        combined = {
            sid: (optimized_az.get(sid, 0.0), optimized_r.get(sid, 0.0), optimized_elev.get(sid, 0.0))
            for sid in radar_positions.keys()
        }

        return combined


def calculate_error_results(
    match_groups: List[List[Dict]],
    radar_positions: Dict[int, Tuple[float, float, float]],
    config: MrraConfig
) -> Dict:
    """
    计算误差结果

    Args:
        match_groups: 匹配组列表
        radar_positions: 雷达站位置字典
        config: MRRA 配置

    Returns:
        误差结果字典
    """
    calculator = ErrorCalculator(config)
    errors = calculator.calculate_radar_errors(match_groups, radar_positions)

    # 转换为结果格式
    result = {
        'errors': {},
        'radar_stations': list(radar_positions.keys()),
        'match_group_count': len(match_groups)
    }

    for station_id, (az_err, range_err, elev_err) in errors.items():
        result['errors'][station_id] = {
            'azimuth_error': az_err,
            'range_error': range_err,
            'elevation_error': elev_err
        }

    return result
