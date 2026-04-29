"""
误差分析服务

提供误差分析任务的管理和查询功能
"""
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.error_analysis import (
    ErrorAnalysisTask,
    ErrorAnalysisTaskStatus,
    ErrorResult,
    MatchGroup,
    TrackSegment,
    SmoothedTrajectoryResult,
)
from app.models.flight_track import RadarStation
from app.schemas.error_analysis import (
    ErrorAnalysisConfig,
    ErrorAnalysisRequest,
    ErrorAnalysisTaskResponse,
    ErrorAnalysisResult,
    ErrorChartResponse,
    MatchStatistics,
    ErrorAnalysisSummary,
    ErrorResultResponse,
    MatchGroupResponse,
    TrackSegmentResponse,
)
from app.algorithms.multi_source.preprocessing.config import MrraConfig
from app.services.error_analysis_executor import execute_analysis, SINGLE_SOURCE_ALGORITHMS
from core.logging import get_logger

logger = get_logger(__name__)


class ErrorAnalysisService:
    """误差分析服务类"""

    def __init__(self, db: Session):
        self.db = db

    def create_analysis_task(
        self,
        request: ErrorAnalysisRequest,
        user_id: int,
    ) -> ErrorAnalysisTaskResponse:
        task_id = str(uuid.uuid4())
        config_dict = request.config.model_dump() if request.config else {}

        task = ErrorAnalysisTask(
            task_id=task_id,
            radar_station_ids=request.radar_station_ids,
            track_ids=request.track_ids,
            user_id=user_id,
            algorithm_name=request.algorithm,
            config=config_dict,
            status=ErrorAnalysisTaskStatus.PENDING,
            progress=0,
        )

        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)

        logger.info(
            f"创建误差分析任务: {task_id}, "
            f"算法: {request.algorithm}, "
            f"雷达站: {request.radar_station_ids}, "
            f"轨迹: {request.track_ids}"
        )

        return self._task_to_response(task)

    def execute_analysis(self, task_id: str) -> None:
        task = self.db.query(ErrorAnalysisTask).filter(
            ErrorAnalysisTask.task_id == task_id
        ).first()

        if not task:
            raise ValueError(f"任务不存在: {task_id}")

        if task.status != ErrorAnalysisTaskStatus.PENDING:
            raise ValueError(f"任务状态不正确: {task.status}")

        execute_analysis(self.db, task)

    def update_progress(self, task_id: str, progress: int, message: Optional[str] = None) -> None:
        task = self.db.query(ErrorAnalysisTask).filter(
            ErrorAnalysisTask.task_id == task_id
        ).first()

        if task:
            task.progress = progress
            self.db.commit()
            logger.debug(f"任务 {task_id} 进度: {progress}% - {message}")

    def get_task_status(self, task_id: str) -> ErrorAnalysisTaskResponse:
        task = self.db.query(ErrorAnalysisTask).filter(
            ErrorAnalysisTask.task_id == task_id
        ).first()

        if not task:
            raise ValueError(f"任务不存在: {task_id}")

        return self._task_to_response(task)

    def get_analysis_results(self, task_id: str) -> ErrorAnalysisResult:
        task = self.db.query(ErrorAnalysisTask).filter(
            ErrorAnalysisTask.task_id == task_id
        ).first()

        if not task:
            raise ValueError(f"任务不存在: {task_id}")

        if task.status != ErrorAnalysisTaskStatus.COMPLETED:
            raise ValueError(f"任务未完成: {task.status}")

        error_results = self.db.query(ErrorResult).filter(
            ErrorResult.task_id == task_id
        ).all()

        match_groups = self.db.query(MatchGroup).filter(
            MatchGroup.task_id == task_id
        ).all()

        match_statistics = self._calculate_match_statistics(match_groups)

        segments_count = self.db.query(TrackSegment).filter(
            TrackSegment.task_id == task_id
        ).count()

        processing_time = 0.0
        if task.started_at and task.completed_at:
            processing_time = (task.completed_at - task.started_at).total_seconds()

        summary = ErrorAnalysisSummary(
            total_stations=len(error_results),
            total_matches=len(match_groups),
            processing_time=processing_time,
            segments_extracted=segments_count,
        )

        errors = [
            ErrorResultResponse(
                id=e.id,
                station_id=e.station_id,
                azimuth_error=e.azimuth_error,
                range_error=e.range_error,
                elevation_error=e.elevation_error,
                match_count=e.match_count,
                confidence=e.confidence,
                iterations=e.iterations,
                final_cost=e.final_cost,
            )
            for e in error_results
        ]

        if task.config:
            mrra_fields = set(MrraConfig.model_fields.keys())
            filtered = {k: v for k, v in task.config.items() if k in mrra_fields}
            config = MrraConfig(**filtered)
        else:
            config = MrraConfig()

        return ErrorAnalysisResult(
            task_id=task_id,
            status=task.status,
            summary=summary,
            errors=errors,
            match_statistics=match_statistics,
            config=config,
        )

    def get_chart_data(self, task_id: str) -> ErrorChartResponse:
        task = self.db.query(ErrorAnalysisTask).filter(
            ErrorAnalysisTask.task_id == task_id
        ).first()

        if not task:
            raise ValueError(f"任务不存在: {task_id}")

        error_results = self.db.query(ErrorResult).filter(
            ErrorResult.task_id == task_id
        ).order_by(ErrorResult.station_id).all()

        radar_stations = self.db.query(RadarStation).all()
        station_map = {s.id: s.description or s.station_id or f"站{s.id}" for s in radar_stations}

        stations = []
        azimuth_errors = []
        range_errors = []
        elevation_errors = []
        confidences = []
        match_counts = []

        for e in error_results:
            stations.append(station_map.get(e.station_id, f"站{e.station_id}"))
            azimuth_errors.append(e.azimuth_error)
            range_errors.append(e.range_error)
            elevation_errors.append(e.elevation_error)
            confidences.append(e.confidence or 0.0)
            match_counts.append(e.match_count)

        match_groups = self.db.query(MatchGroup).filter(
            MatchGroup.task_id == task_id
        ).all()

        group_size_distribution = {}
        for g in match_groups:
            size = g.point_count
            group_size_distribution[str(size)] = group_size_distribution.get(str(size), 0) + 1

        return ErrorChartResponse(
            stations=stations,
            azimuth_errors=azimuth_errors,
            range_errors=range_errors,
            elevation_errors=elevation_errors,
            confidences=confidences,
            match_counts=match_counts,
            group_size_distribution=group_size_distribution,
        )

    def get_track_segments(self, task_id: str, limit: int = 100) -> List[TrackSegmentResponse]:
        segments = self.db.query(TrackSegment).filter(
            TrackSegment.task_id == task_id
        ).limit(limit).all()

        return [
            TrackSegmentResponse(
                id=s.id,
                segment_id=s.segment_id,
                station_id=s.station_id,
                track_id=s.track_id,
                start_time=s.start_time,
                end_time=s.end_time,
                point_count=s.point_count,
                start_point_index=s.start_point_index,
                end_point_index=s.end_point_index,
            )
            for s in segments
        ]

    def get_match_groups(self, task_id: str, limit: int = 100) -> List[MatchGroupResponse]:
        from app.schemas.error_analysis import MatchPoint

        groups = self.db.query(MatchGroup).filter(
            MatchGroup.task_id == task_id
        ).limit(limit).all()

        result = []
        for g in groups:
            match_points = [
                MatchPoint(
                    station_id=p['station_id'],
                    point_id=p.get('point_id'),
                    longitude=p['longitude'],
                    latitude=p['latitude'],
                    altitude=p.get('altitude'),
                )
                for p in g.match_points
            ]

            result.append(MatchGroupResponse(
                id=g.id,
                group_id=g.group_id,
                match_time=g.match_time,
                match_points=match_points,
                point_count=g.point_count,
                avg_distance=g.avg_distance,
                max_distance=g.max_distance,
                variance=g.variance,
            ))

        return result

    def list_tasks(
        self,
        user_id: Optional[int] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Tuple[List[ErrorAnalysisTaskResponse], int]:
        query = self.db.query(ErrorAnalysisTask)

        if user_id is not None:
            query = query.filter(ErrorAnalysisTask.user_id == user_id)

        total = query.count()
        tasks = query.order_by(ErrorAnalysisTask.created_at.desc()).offset(offset).limit(limit).all()

        return [self._task_to_response(t) for t in tasks], total

    def get_task_detail_full(
        self,
        task_id: str,
        include_intermediate: bool = True,
        include_points: bool = False,
    ) -> Dict:
        from app.schemas.error_analysis import (
            ProcessStepInfo,
            InterpolationSummary,
            TrackSegmentDetail,
            MatchGroupDetail,
            ErrorResultDetail,
            InterpolatedPointResponse,
        )

        task = self.db.query(ErrorAnalysisTask).filter(
            ErrorAnalysisTask.task_id == task_id
        ).first()

        if not task:
            raise ValueError(f"任务不存在: {task_id}")

        radar_stations = self.db.query(RadarStation).all()
        station_map = {s.id: s for s in radar_stations}
        station_names = {s.id: s.description or s.station_id or f"站{s.id}" for s in radar_stations}

        processing_time = 0.0
        if task.started_at and task.completed_at:
            processing_time = (task.completed_at - task.started_at).total_seconds()

        if task.config:
            config_fields = set(ErrorAnalysisConfig.model_fields.keys())
            filtered = {k: v for k, v in task.config.items() if k in config_fields}
            config = ErrorAnalysisConfig(**filtered)
        else:
            config = ErrorAnalysisConfig()
        process_steps = self._build_process_steps(task, processing_time)

        # 航迹段数据
        segments = self.db.query(TrackSegment).filter(
            TrackSegment.task_id == task_id
        ).all()

        segments_detail = []
        segments_by_station = {}
        for s in segments:
            station_name = station_names.get(s.station_id, f"站{s.station_id}")
            duration = (s.end_time - s.start_time).total_seconds() if s.end_time and s.start_time else 0.0

            detail = TrackSegmentDetail(
                id=s.id,
                segment_id=s.segment_id,
                station_id=s.station_id,
                track_id=s.track_id,
                start_time=s.start_time,
                end_time=s.end_time,
                point_count=s.point_count,
                start_point_index=s.start_point_index,
                end_point_index=s.end_point_index,
                duration_seconds=duration,
                station_name=station_name,
            )
            segments_detail.append(detail)

            if station_name not in segments_by_station:
                segments_by_station[station_name] = 0
            segments_by_station[station_name] += 1

        segments_summary = {
            "total_segments": len(segments),
            "total_points": sum(s.point_count for s in segments),
            "by_station": segments_by_station,
        }

        # 插值点数据
        from app.models.error_analysis import TrackInterpolatedPoint

        interpolation_summary = None
        interpolated_points = []
        if include_points:
            points = self.db.query(TrackInterpolatedPoint).filter(
                TrackInterpolatedPoint.task_id == task_id
            ).limit(10000).all()

            points_by_station = {}
            original_count = 0
            interpolated_count = 0

            for p in points:
                is_original = p.is_original == 1
                if is_original:
                    original_count += 1
                else:
                    interpolated_count += 1

                station_name = station_names.get(p.station_id, f"站{p.station_id}")
                if station_name not in points_by_station:
                    points_by_station[station_name] = 0
                points_by_station[station_name] += 1

                interpolated_points.append(InterpolatedPointResponse(
                    id=p.id,
                    station_id=p.station_id,
                    track_id=p.track_id,
                    time_seconds=p.time_seconds,
                    timestamp=p.timestamp,
                    longitude=p.longitude,
                    latitude=p.latitude,
                    altitude=p.altitude,
                    is_original=is_original,
                ))

            interpolation_summary = InterpolationSummary(
                total_points=len(points),
                original_points=original_count,
                interpolated_points=interpolated_count,
                stations=points_by_station,
            )
        else:
            total_points = self.db.query(TrackInterpolatedPoint).filter(
                TrackInterpolatedPoint.task_id == task_id
            ).count()
            original_points = self.db.query(TrackInterpolatedPoint).filter(
                TrackInterpolatedPoint.task_id == task_id,
                TrackInterpolatedPoint.is_original == 1,
            ).count()

            points_by_station = {}
            points = self.db.query(
                TrackInterpolatedPoint.station_id,
                func.count(TrackInterpolatedPoint.id).label('count'),
            ).filter(
                TrackInterpolatedPoint.task_id == task_id,
            ).group_by(TrackInterpolatedPoint.station_id).all()

            for p in points:
                station_name = station_names.get(p.station_id, f"站{p.station_id}")
                points_by_station[station_name] = p.count

            interpolation_summary = InterpolationSummary(
                total_points=total_points,
                original_points=original_points,
                interpolated_points=total_points - original_points,
                stations=points_by_station,
            )

        # 匹配组数据
        match_groups_db = self.db.query(MatchGroup).filter(
            MatchGroup.task_id == task_id
        ).all()

        match_groups_detail = []
        for g in match_groups_db:
            station_ids = list(set(
                p.get('station_id') for p in (g.match_points or [])
                if isinstance(p, dict) and p.get('station_id') is not None
            ))

            match_groups_detail.append(MatchGroupDetail(
                id=g.id,
                group_id=g.group_id,
                match_time=g.match_time,
                match_points=g.match_points,
                point_count=g.point_count,
                avg_distance=g.avg_distance,
                max_distance=g.max_distance,
                variance=g.variance,
                station_ids=station_ids,
                time_difference_ms=0.0,
            ))

        if match_groups_db:
            avg_distances = [g.avg_distance for g in match_groups_db if g.avg_distance is not None]
            all_station_ids = set()
            for g in match_groups_db:
                for p in (g.match_points or []):
                    if isinstance(p, dict) and p.get('station_id') is not None:
                        all_station_ids.add(p.get('station_id'))
            match_summary = {
                "total_groups": len(match_groups_db),
                "total_points": sum(g.point_count for g in match_groups_db),
                "avg_distance_mean": sum(avg_distances) / len(avg_distances) if avg_distances else 0.0,
                "stations_involved": len(all_station_ids),
            }
        else:
            match_summary = {
                "total_groups": 0,
                "total_points": 0,
                "avg_distance_mean": 0.0,
                "stations_involved": 0,
            }

        # 误差结果
        error_results_db = self.db.query(ErrorResult).filter(
            ErrorResult.task_id == task_id
        ).all()

        error_results_detail = []
        for e in error_results_db:
            azimuth_quality = _evaluate_quality(e.azimuth_error, "azimuth")
            range_quality = _evaluate_quality(e.range_error, "range")
            elevation_quality = _evaluate_quality(e.elevation_error, "elevation")

            error_results_detail.append(ErrorResultDetail(
                id=e.id,
                station_id=e.station_id,
                station_name=station_names.get(e.station_id, f"站{e.station_id}"),
                azimuth_error=e.azimuth_error,
                range_error=e.range_error,
                elevation_error=e.elevation_error,
                match_count=e.match_count,
                confidence=e.confidence,
                iterations=e.iterations,
                final_cost=e.final_cost,
                azimuth_quality=azimuth_quality,
                range_quality=range_quality,
                elevation_quality=elevation_quality,
            ))

        # 平滑轨迹结果（单源盲测算法）
        from app.schemas.error_analysis import SmoothedTrajectoryResponse, SmoothedTrajectoryPoint
        smoothed_trajectories = []
        algorithm_name = task.algorithm_name or ""

        if algorithm_name in SINGLE_SOURCE_ALGORITHMS:
            smoothed_results = self.db.query(SmoothedTrajectoryResult).filter(
                SmoothedTrajectoryResult.task_id == task_id
            ).all()

            for sr in smoothed_results:
                original_points_list = []
                for p in (sr.original_trajectory or []):
                    if isinstance(p, dict):
                        original_points_list.append(SmoothedTrajectoryPoint(
                            longitude=p.get("longitude", 0.0),
                            latitude=p.get("latitude", 0.0),
                            altitude=p.get("altitude"),
                        ))

                smoothed_points_list = []
                for p in (sr.smoothed_trajectory or []):
                    if isinstance(p, dict):
                        smoothed_points_list.append(SmoothedTrajectoryPoint(
                            timestamp=p.get("timestamp"),
                            longitude=p.get("longitude", 0.0),
                            latitude=p.get("latitude", 0.0),
                            altitude=p.get("altitude"),
                            covariance_trace=p.get("covariance_trace"),
                        ))

                smoothed_trajectories.append(SmoothedTrajectoryResponse(
                    id=sr.id,
                    station_id=sr.station_id,
                    station_name=station_names.get(sr.station_id, f"站{sr.station_id}"),
                    batch_id=sr.batch_id,
                    original_trajectory=original_points_list,
                    smoothed_trajectory=smoothed_points_list,
                    rmse_lat=sr.rmse_lat,
                    rmse_lon=sr.rmse_lon,
                    rmse_alt=sr.rmse_alt,
                    point_count=sr.point_count,
                    process_noise=sr.process_noise,
                    measurement_noise=sr.measurement_noise,
                ))

        return {
            "task_id": task.task_id,
            "status": task.status,
            "progress": task.progress,
            "error_message": task.error_message,
            "created_at": task.created_at,
            "started_at": task.started_at,
            "completed_at": task.completed_at,
            "algorithm_name": algorithm_name,
            "config": config,
            "radar_station_ids": task.radar_station_ids or [],
            "track_ids": task.track_ids or [],
            "process_steps": process_steps,
            "segments_summary": segments_summary,
            "interpolation_summary": interpolation_summary,
            "match_summary": match_summary,
            "segments": segments_detail if include_intermediate else [],
            "interpolated_points": interpolated_points,
            "match_groups": match_groups_detail if include_intermediate else [],
            "error_results": error_results_detail,
            "smoothed_trajectories": smoothed_trajectories,
            "processing_time_seconds": processing_time,
            "total_segments": len(segments),
            "total_match_groups": len(match_groups_db),
            "total_interpolated_points": interpolation_summary.total_points if interpolation_summary else 0,
        }

    def _calculate_match_statistics(self, match_groups: List[MatchGroup]) -> MatchStatistics:
        if not match_groups:
            return MatchStatistics(
                total_groups=0,
                group_size_avg=0.0,
                group_size_std=0.0,
                distance_avg=0.0,
                distance_std=0.0,
                min_group_size=0,
                max_group_size=0,
            )

        import numpy as np

        sizes = [g.point_count for g in match_groups]
        avg_distances = [g.avg_distance for g in match_groups if g.avg_distance is not None]

        return MatchStatistics(
            total_groups=len(match_groups),
            group_size_avg=float(np.mean(sizes)),
            group_size_std=float(np.std(sizes)),
            distance_avg=float(np.mean(avg_distances)) if avg_distances else 0.0,
            distance_std=float(np.std(avg_distances)) if avg_distances else 0.0,
            min_group_size=int(np.min(sizes)),
            max_group_size=int(np.max(sizes)),
        )

    def _task_to_response(self, task: ErrorAnalysisTask) -> ErrorAnalysisTaskResponse:
        station_ids_display = task.radar_station_ids or []
        if task.radar_station_ids:
            stations = self.db.query(RadarStation.station_id).filter(
                RadarStation.id.in_(task.radar_station_ids)
            ).all()
            station_ids_display = [s.station_id for s in stations]

        return ErrorAnalysisTaskResponse(
            id=task.id,
            task_id=task.task_id,
            radar_station_ids=station_ids_display,
            track_ids=task.track_ids or [],
            user_id=task.user_id,
            algorithm_name=task.algorithm_name,
            status=task.status,
            progress=task.progress,
            error_message=task.error_message,
            created_at=task.created_at,
            started_at=task.started_at,
            completed_at=task.completed_at,
        )

    def _build_process_steps(self, task: ErrorAnalysisTask, processing_time: float) -> List[Dict]:
        steps = [
            {
                "step_id": "extracting",
                "step_name": "航迹提取",
                "step_description": "从原始雷达数据中提取飞机航迹，根据时间连续性和空间相关性将点连接成段",
                "status": "completed" if task.status != ErrorAnalysisTaskStatus.PENDING else "pending",
            },
            {
                "step_id": "interpolating",
                "step_name": "航迹插值",
                "step_description": "对航迹进行时间对齐和空间插值，使不同雷达站的航迹能够在同一时间点进行比较",
                "status": "completed" if task.status in [ErrorAnalysisTaskStatus.COMPLETED, ErrorAnalysisTaskStatus.CALCULATING, ErrorAnalysisTaskStatus.MATCHING] else "pending",
            },
            {
                "step_id": "matching",
                "step_name": "航迹匹配",
                "step_description": "在时间窗口内，将不同雷达站观测到的同一架飞机进行匹配，形成匹配组",
                "status": "completed" if task.status in [ErrorAnalysisTaskStatus.COMPLETED, ErrorAnalysisTaskStatus.CALCULATING] else "pending",
            },
            {
                "step_id": "calculating",
                "step_name": "误差计算",
                "step_description": "基于匹配组结果，计算各雷达站的系统误差（方位角、距离、俯仰角）",
                "status": "completed" if task.status == ErrorAnalysisTaskStatus.COMPLETED else "pending",
            },
        ]

        status_mapping = {
            ErrorAnalysisTaskStatus.PENDING: ["pending", "pending", "pending", "pending"],
            ErrorAnalysisTaskStatus.EXTRACTING: ["running", "pending", "pending", "pending"],
            ErrorAnalysisTaskStatus.INTERPOLATING: ["completed", "running", "pending", "pending"],
            ErrorAnalysisTaskStatus.MATCHING: ["completed", "completed", "running", "pending"],
            ErrorAnalysisTaskStatus.CALCULATING: ["completed", "completed", "completed", "running"],
            ErrorAnalysisTaskStatus.COMPLETED: ["completed", "completed", "completed", "completed"],
            ErrorAnalysisTaskStatus.FAILED: ["completed", "completed", "completed", "failed"],
        }

        mapped_statuses = status_mapping.get(task.status, ["pending"] * 4)
        for i, step in enumerate(steps):
            step["status"] = mapped_statuses[i]
            step["duration_seconds"] = None

        return steps


def _evaluate_quality(value: float, error_type: str) -> str:
    thresholds = {
        "azimuth": [0.5, 1.0, 2.0],
        "range": [50, 100, 200],
        "elevation": [0.5, 1.0, 2.0],
    }

    if error_type not in thresholds:
        return "unknown"

    t = thresholds[error_type]
    abs_value = abs(value)

    if abs_value <= t[0]:
        return "excellent"
    elif abs_value <= t[1]:
        return "good"
    elif abs_value <= t[2]:
        return "fair"
    else:
        return "poor"
