"""
误差分析执行器

负责任务的算法调度和执行
"""
from datetime import datetime
from collections import defaultdict
from typing import Dict

from sqlalchemy.orm import Session

from app.models.error_analysis import (
    ErrorAnalysisTask,
    ErrorAnalysisTaskStatus,
    ErrorResult,
    SmoothedTrajectoryResult,
)
from app.models.flight_track import RadarStation, FlightTrackRaw
from app.algorithms.multi_source.preprocessing.config import MrraConfig
from app.algorithms.multi_source.preprocessing.track_extractor import load_track_points_by_track_ids, extract_key_tracks
from app.algorithms.multi_source.preprocessing.track_interpolator import interpolate_and_save_tracks
from app.algorithms.multi_source.preprocessing.track_matcher import match_tracks_from_database, save_matched_groups
from app.algorithms.multi_source.preprocessing.error_calculator import calculate_error_results
from core.logging import get_logger

logger = get_logger(__name__)

# 单源盲测算法列表
SINGLE_SOURCE_ALGORITHMS = ("kalman", "particle_filter", "spline")


def execute_analysis(db: Session, task: ErrorAnalysisTask) -> None:
    """执行误差分析任务"""
    task_id = task.task_id
    algorithm_name = task.algorithm_name or "mrra"
    # 兼容旧名称
    if algorithm_name == "gradient_descent":
        algorithm_name = "mrra"

    try:
        task.status = ErrorAnalysisTaskStatus.EXTRACTING
        task.started_at = datetime.utcnow()
        db.commit()

        from app.algorithms.factory import AlgorithmFactory
        algorithm = AlgorithmFactory.create_algorithm_from_dict(
            algorithm_name, task.config or {}
        )

        logger.info(f"使用算法 {algorithm_name} 执行任务 {task_id}")

        if algorithm_name in ("mrra", "ransac", "ransac_heuristic", "weighted_lstsq", "kalman", "particle_filter", "spline"):
            _execute_with_algorithm_interface(db, task, algorithm)
        else:
            _execute_with_legacy_flow(db, task, algorithm)

        task.status = ErrorAnalysisTaskStatus.COMPLETED
        task.progress = 100
        task.completed_at = datetime.utcnow()
        db.commit()
        logger.info(f"误差分析任务完成: {task_id}")

    except Exception as e:
        logger.error(f"误差分析任务失败: {task_id}, 错误: {str(e)}")
        task.status = ErrorAnalysisTaskStatus.FAILED
        task.error_message = str(e)
        task.completed_at = datetime.utcnow()
        db.commit()
        raise


def _execute_with_algorithm_interface(db: Session, task: ErrorAnalysisTask, algorithm) -> None:
    """使用算法框架的 analyze() 接口执行分析"""
    result = algorithm.analyze(
        task_id=task.task_id,
        radar_station_ids=task.radar_station_ids,
        track_ids=task.track_ids,
        db_session=db,
    )

    if result.status == "failed":
        raise RuntimeError(result.error_message or "算法执行失败")

    algorithm_name = task.algorithm_name or ""
    is_single_source = algorithm_name in SINGLE_SOURCE_ALGORITHMS

    if is_single_source:
        _save_smoothed_trajectory_results(db, task.task_id, result)
    else:
        _save_error_results_from_result(db, task.task_id, result)

    if result.metadata:
        task.result_metadata = result.metadata

    if result.match_statistics:
        if not task.result_metadata:
            task.result_metadata = {}
        task.result_metadata["match_statistics"] = result.match_statistics

    db.commit()


def _save_smoothed_trajectory_results(db: Session, task_id: str, result) -> None:
    """保存单源盲测的平滑轨迹结果"""
    metadata = result.metadata or {}
    smoothed_trajectory = metadata.get("smoothed_trajectory", [])

    trajectories_by_key = defaultdict(list)
    for point in smoothed_trajectory:
        key = (point.get("station_id"), point.get("batch_id", "unknown"))
        trajectories_by_key[key].append(point)

    errors = result.errors or {}

    for (station_id, batch_id), points in trajectories_by_key.items():
        original_points = []
        smoothed_points = []

        for p in points:
            smoothed_points.append({
                "timestamp": p.get("timestamp"),
                "longitude": p.get("longitude"),
                "latitude": p.get("latitude"),
                "altitude": p.get("altitude"),
                "covariance_trace": p.get("covariance_trace"),
            })
            original_points.append({
                "longitude": p.get("orig_lon"),
                "latitude": p.get("orig_lat"),
                "altitude": p.get("orig_alt"),
            })

        station_errors = errors.get(station_id, {})
        rmse_lat = station_errors.get("azimuth_error", 0.0)
        rmse_lon = station_errors.get("range_error", 0.0) / 111000
        rmse_alt = station_errors.get("elevation_error", 0.0)

        record = SmoothedTrajectoryResult(
            task_id=task_id,
            station_id=station_id,
            batch_id=batch_id,
            original_trajectory=original_points,
            smoothed_trajectory=smoothed_points,
            rmse_lat=rmse_lat,
            rmse_lon=rmse_lon,
            rmse_alt=rmse_alt,
            point_count=len(points),
            process_noise=result.match_statistics.get("process_noise") if result.match_statistics else None,
            measurement_noise=result.match_statistics.get("measurement_noise") if result.match_statistics else None,
        )
        db.add(record)


def _save_error_results_from_result(db: Session, task_id: str, result) -> None:
    """从算法执行结果保存误差结果（多源参考算法）"""
    for station_id, errors in result.errors.items():
        error_record = ErrorResult(
            task_id=task_id,
            station_id=station_id,
            azimuth_error=errors.get("azimuth_error", 0.0),
            range_error=errors.get("range_error", 0.0),
            elevation_error=errors.get("elevation_error", 0.0),
            match_count=result.match_statistics.get("total_match_groups", 0),
            confidence=result.match_statistics.get("station_weights", {}).get(str(station_id)),
        )
        db.add(error_record)


def _execute_with_legacy_flow(db: Session, task: ErrorAnalysisTask, algorithm) -> None:
    """使用旧的 MRRA 流程执行分析（向后兼容）"""
    if task.config:
        mrra_fields = set(MrraConfig.model_fields.keys())
        filtered = {k: v for k, v in task.config.items() if k in mrra_fields}
        config = MrraConfig(**filtered)
    else:
        config = MrraConfig()

    radar_stations = db.query(RadarStation).filter(
        RadarStation.id.in_(task.radar_station_ids)
    ).all()
    radar_positions = {
        station.id: (station.longitude, station.latitude, station.altitude or 0.0)
        for station in radar_stations
    }

    if not radar_positions:
        raise ValueError("没有找到指定的雷达站位置信息")

    logger.info(f"使用 {len(radar_positions)} 个雷达站: {task.radar_station_ids}")

    # 步骤1: 加载航迹数据
    _update_progress(db, task.task_id, 10, "加载航迹数据")
    station_data = load_track_points_by_track_ids(db, task.track_ids, radar_positions)

    if not station_data:
        raise ValueError("没有找到有效的航迹数据")

    # 步骤2: 提取关键航迹
    task.status = ErrorAnalysisTaskStatus.EXTRACTING
    _update_progress(db, task.task_id, 20, "提取关键航迹")
    key_tracks = extract_key_tracks(station_data, config)

    if not key_tracks:
        raise ValueError("没有提取到关键航迹")

    # 步骤3: 插值
    task.status = ErrorAnalysisTaskStatus.INTERPOLATING
    _update_progress(db, task.task_id, 40, "航迹插值")

    first_track = db.query(FlightTrackRaw).filter(
        FlightTrackRaw.batch_id.in_(task.track_ids)
    ).order_by(FlightTrackRaw.timestamp).first()
    reference_time = first_track.timestamp.replace(hour=0, minute=0, second=0, microsecond=0) if first_track else datetime.utcnow()

    interpolate_and_save_tracks(db, task.task_id, key_tracks, config, reference_time)

    # 步骤4: 匹配
    task.status = ErrorAnalysisTaskStatus.MATCHING
    _update_progress(db, task.task_id, 60, "航迹匹配")
    matched_groups = match_tracks_from_database(db, task.task_id, config)

    if not matched_groups:
        raise ValueError("没有匹配到航迹组")

    save_matched_groups(db, task.task_id, matched_groups, reference_time)

    # 步骤5: 计算误差
    task.status = ErrorAnalysisTaskStatus.CALCULATING
    _update_progress(db, task.task_id, 80, "计算雷达误差")
    error_results = calculate_error_results(matched_groups, radar_positions, config)

    _save_error_results(db, task.task_id, error_results)


def _save_error_results(db: Session, task_id: str, error_results: Dict) -> None:
    """保存误差结果到数据库"""
    match_group_count = error_results.get('match_group_count', 0)

    for station_id, errors in error_results['errors'].items():
        result = ErrorResult(
            task_id=task_id,
            station_id=station_id,
            azimuth_error=errors.get('azimuth_error', 0.0),
            range_error=errors.get('range_error', 0.0),
            elevation_error=errors.get('elevation_error', 0.0),
            match_count=match_group_count,
            confidence=errors.get('confidence'),
            iterations=errors.get('iterations'),
            final_cost=errors.get('final_cost'),
        )
        db.add(result)

    db.commit()


def _update_progress(db: Session, task_id: str, progress: int, message: str = None) -> None:
    """更新任务进度"""
    task = db.query(ErrorAnalysisTask).filter(
        ErrorAnalysisTask.task_id == task_id
    ).first()

    if task:
        task.progress = progress
        db.commit()
        logger.debug(f"任务 {task_id} 进度: {progress}% - {message}")
