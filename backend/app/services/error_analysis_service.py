"""
误差分析服务

提供误差分析任务的管理和执行功能
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
    TrackSegment
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
    TrackSegmentResponse
)
from app.utils.mrra.config import MrraConfig
from app.utils.mrra.track_extractor import TrackPoint, load_track_points_by_track_ids, extract_key_tracks
from app.utils.mrra.track_interpolator import interpolate_and_save_tracks
from app.utils.mrra.track_matcher import match_tracks_from_database, save_matched_groups, analyze_match_statistics
from app.utils.mrra.error_calculator import calculate_error_results
from core.logging import get_logger

logger = get_logger(__name__)


class ErrorAnalysisService:
    """误差分析服务类"""

    def __init__(self, db: Session):
        """
        初始化服务

        Args:
            db: 数据库会话
        """
        self.db = db

    def create_analysis_task(
        self,
        request: ErrorAnalysisRequest,
        user_id: int
    ) -> ErrorAnalysisTaskResponse:
        """
        创建误差分析任务

        Args:
            request: 分析请求（包含雷达站ID列表和轨迹ID列表）
            user_id: 用户ID

        Returns:
            任务响应
        """
        # 生成任务ID
        task_id = str(uuid.uuid4())

        # 转换配置为字典
        config_dict = request.config.model_dump() if request.config else {}

        # 创建任务记录
        task = ErrorAnalysisTask(
            task_id=task_id,
            radar_station_ids=request.radar_station_ids,
            track_ids=request.track_ids,
            user_id=user_id,
            config=config_dict,
            status=ErrorAnalysisTaskStatus.PENDING,
            progress=0
        )

        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)

        logger.info(f"创建误差分析任务: {task_id}, 雷达站: {request.radar_station_ids}, 轨迹: {request.track_ids}")

        return self._task_to_response(task)

    def execute_analysis(self, task_id: str) -> None:
        """
        执行误差分析任务

        Args:
            task_id: 任务ID
        """
        # 获取任务
        task = self.db.query(ErrorAnalysisTask).filter(
            ErrorAnalysisTask.task_id == task_id
        ).first()

        if not task:
            raise ValueError(f"任务不存在: {task_id}")

        if task.status != ErrorAnalysisTaskStatus.PENDING:
            raise ValueError(f"任务状态不正确: {task.status}")

        try:
            # 更新任务状态
            task.status = ErrorAnalysisTaskStatus.EXTRACTING
            task.started_at = datetime.utcnow()
            self.db.commit()

            # 加载配置
            config = MrraConfig(**task.config) if task.config else MrraConfig()

            # 获取选中的雷达站位置
            radar_stations = self.db.query(RadarStation).filter(
                RadarStation.id.in_(task.radar_station_ids)
            ).all()
            radar_positions = {
                station.id: (station.longitude, station.latitude, station.altitude or 0.0)
                for station in radar_stations
            }

            if not radar_positions:
                raise ValueError("没有找到指定的雷达站位置信息")

            logger.info(f"使用 {len(radar_positions)} 个雷达站: {task.radar_station_ids}")

            # 步骤1: 加载航迹数据（按轨迹编号筛选）
            self.update_progress(task_id, 10, "加载航迹数据")
            station_data = load_track_points_by_track_ids(self.db, task.track_ids, radar_positions)

            if not station_data:
                raise ValueError("没有找到有效的航迹数据")

            # 步骤2: 提取关键航迹
            task.status = ErrorAnalysisTaskStatus.EXTRACTING
            self.update_progress(task_id, 20, "提取关键航迹")
            key_tracks = extract_key_tracks(station_data, config)

            if not key_tracks:
                raise ValueError("没有提取到关键航迹")

            # 步骤3: 插值
            task.status = ErrorAnalysisTaskStatus.INTERPOLATING
            self.update_progress(task_id, 40, "航迹插值")

            # 获取参考时间（使用第一条轨迹的时间）
            from app.models.flight_track import FlightTrackRaw
            first_track = self.db.query(FlightTrackRaw).filter(
                FlightTrackRaw.batch_id.in_(task.track_ids)
            ).order_by(FlightTrackRaw.timestamp).first()
            reference_time = first_track.timestamp.replace(hour=0, minute=0, second=0, microsecond=0) if first_track else datetime.utcnow()

            interpolate_and_save_tracks(self.db, task_id, key_tracks, config, reference_time)

            # 步骤4: 匹配
            task.status = ErrorAnalysisTaskStatus.MATCHING
            self.update_progress(task_id, 60, "航迹匹配")
            matched_groups = match_tracks_from_database(self.db, task_id, config)

            if not matched_groups:
                raise ValueError("没有匹配到航迹组")

            # 保存匹配结果
            save_matched_groups(self.db, task_id, matched_groups, reference_time)

            # 步骤5: 计算误差
            task.status = ErrorAnalysisTaskStatus.CALCULATING
            self.update_progress(task_id, 80, "计算雷达误差")
            error_results = calculate_error_results(matched_groups, radar_positions, config)

            # 保存误差结果
            self._save_error_results(task_id, error_results)

            # 完成
            task.status = ErrorAnalysisTaskStatus.COMPLETED
            task.progress = 100
            task.completed_at = datetime.utcnow()
            self.db.commit()

            logger.info(f"误差分析任务完成: {task_id}")

        except Exception as e:
            logger.error(f"误差分析任务失败: {task_id}, 错误: {str(e)}")
            task.status = ErrorAnalysisTaskStatus.FAILED
            task.error_message = str(e)
            task.completed_at = datetime.utcnow()
            self.db.commit()
            raise

    def update_progress(
        self,
        task_id: str,
        progress: int,
        message: Optional[str] = None
    ) -> None:
        """
        更新任务进度

        Args:
            task_id: 任务ID
            progress: 进度百分比
            message: 进度消息
        """
        task = self.db.query(ErrorAnalysisTask).filter(
            ErrorAnalysisTask.task_id == task_id
        ).first()

        if task:
            task.progress = progress
            self.db.commit()
            logger.debug(f"任务 {task_id} 进度: {progress}% - {message}")

    def get_task_status(self, task_id: str) -> ErrorAnalysisTaskResponse:
        """
        获取任务状态

        Args:
            task_id: 任务ID

        Returns:
            任务响应
        """
        task = self.db.query(ErrorAnalysisTask).filter(
            ErrorAnalysisTask.task_id == task_id
        ).first()

        if not task:
            raise ValueError(f"任务不存在: {task_id}")

        return self._task_to_response(task)

    def get_analysis_results(self, task_id: str) -> ErrorAnalysisResult:
        """
        获取分析结果

        Args:
            task_id: 任务ID

        Returns:
            分析结果
        """
        task = self.db.query(ErrorAnalysisTask).filter(
            ErrorAnalysisTask.task_id == task_id
        ).first()

        if not task:
            raise ValueError(f"任务不存在: {task_id}")

        if task.status != ErrorAnalysisTaskStatus.COMPLETED:
            raise ValueError(f"任务未完成: {task.status}")

        # 获取误差结果
        error_results = self.db.query(ErrorResult).filter(
            ErrorResult.task_id == task_id
        ).all()

        # 获取匹配统计
        match_groups = self.db.query(MatchGroup).filter(
            MatchGroup.task_id == task_id
        ).all()

        # 计算统计信息
        match_statistics = self._calculate_match_statistics(match_groups)

        # 获取航迹段数量
        segments_count = self.db.query(TrackSegment).filter(
            TrackSegment.task_id == task_id
        ).count()

        # 计算处理时间
        processing_time = 0.0
        if task.started_at and task.completed_at:
            processing_time = (task.completed_at - task.started_at).total_seconds()

        # 构建结果
        summary = ErrorAnalysisSummary(
            total_stations=len(error_results),
            total_matches=len(match_groups),
            processing_time=processing_time,
            segments_extracted=segments_count
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
                final_cost=e.final_cost
            )
            for e in error_results
        ]

        config = MrraConfig(**task.config) if task.config else MrraConfig()

        return ErrorAnalysisResult(
            task_id=task_id,
            status=task.status,
            summary=summary,
            errors=errors,
            match_statistics=match_statistics,
            config=config
        )

    def get_chart_data(self, task_id: str) -> ErrorChartResponse:
        """
        获取图表数据

        Args:
            task_id: 任务ID

        Returns:
            图表数据
        """
        task = self.db.query(ErrorAnalysisTask).filter(
            ErrorAnalysisTask.task_id == task_id
        ).first()

        if not task:
            raise ValueError(f"任务不存在: {task_id}")

        # 获取误差结果
        error_results = self.db.query(ErrorResult).filter(
            ErrorResult.task_id == task_id
        ).order_by(ErrorResult.station_id).all()

        # 获取雷达站信息
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

        # 获取匹配组大小分布
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
            group_size_distribution=group_size_distribution
        )

    def get_track_segments(
        self,
        task_id: str,
        limit: int = 100
    ) -> List[TrackSegmentResponse]:
        """
        获取航迹段列表

        Args:
            task_id: 任务ID
            limit: 限制数量

        Returns:
            航迹段列表
        """
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
                end_point_index=s.end_point_index
            )
            for s in segments
        ]

    def get_match_groups(
        self,
        task_id: str,
        limit: int = 100
    ) -> List[MatchGroupResponse]:
        """
        获取匹配组列表

        Args:
            task_id: 任务ID
            limit: 限制数量

        Returns:
            匹配组列表
        """
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
                    altitude=p.get('altitude')
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
                variance=g.variance
            ))

        return result

    def list_tasks(
        self,
        user_id: Optional[int] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Tuple[List[ErrorAnalysisTaskResponse], int]:
        """
        列出任务

        Args:
            user_id: 用户ID（可选）
            limit: 限制数量
            offset: 偏移量

        Returns:
            (任务列表, 总数)
        """
        query = self.db.query(ErrorAnalysisTask)

        if user_id is not None:
            query = query.filter(ErrorAnalysisTask.user_id == user_id)

        total = query.count()
        tasks = query.order_by(ErrorAnalysisTask.created_at.desc()).offset(offset).limit(limit).all()

        return [self._task_to_response(t) for t in tasks], total

    def _save_error_results(self, task_id: str, error_results: Dict) -> None:
        """
        保存误差结果到数据库

        Args:
            task_id: 任务ID
            error_results: 误差结果字典
        """
        for station_id, errors in error_results['errors'].items():
            result = ErrorResult(
                task_id=task_id,
                station_id=station_id,
                azimuth_error=errors['azimuth_error'],
                range_error=errors['range_error'],
                elevation_error=errors['elevation_error'],
                match_count=error_results['match_group_count']
            )
            self.db.add(result)

        self.db.commit()

    def _calculate_match_statistics(self, match_groups: List[MatchGroup]) -> MatchStatistics:
        """
        计算匹配统计信息

        Args:
            match_groups: 匹配组列表

        Returns:
            匹配统计
        """
        if not match_groups:
            return MatchStatistics(
                total_groups=0,
                group_size_avg=0.0,
                group_size_std=0.0,
                distance_avg=0.0,
                distance_std=0.0,
                min_group_size=0,
                max_group_size=0
            )

        sizes = [g.point_count for g in match_groups]
        avg_distances = [g.avg_distance for g in match_groups if g.avg_distance is not None]

        import numpy as np

        return MatchStatistics(
            total_groups=len(match_groups),
            group_size_avg=float(np.mean(sizes)),
            group_size_std=float(np.std(sizes)),
            distance_avg=float(np.mean(avg_distances)) if avg_distances else 0.0,
            distance_std=float(np.std(avg_distances)) if avg_distances else 0.0,
            min_group_size=int(np.min(sizes)),
            max_group_size=int(np.max(sizes))
        )

    def _task_to_response(self, task: ErrorAnalysisTask) -> ErrorAnalysisTaskResponse:
        """
        将任务模型转换为响应

        Args:
            task: 任务模型

        Returns:
            任务响应
        """
        return ErrorAnalysisTaskResponse(
            id=task.id,
            task_id=task.task_id,
            radar_station_ids=task.radar_station_ids or [],
            track_ids=task.track_ids or [],
            user_id=task.user_id,
            status=task.status,
            progress=task.progress,
            error_message=task.error_message,
            created_at=task.created_at,
            started_at=task.started_at,
            completed_at=task.completed_at
        )

    def get_task_detail_full(
        self,
        task_id: str,
        include_intermediate: bool = True,
        include_points: bool = False
    ) -> Dict:
        """
        获取完整任务详情

        Args:
            task_id: 任务ID
            include_intermediate: 是否包含中间步骤详细数据
            include_points: 是否包含插值点明细（数据量大，默认不返回）

        Returns:
            完整任务详情字典
        """
        from app.schemas.error_analysis import (
            ErrorAnalysisConfig,
            ProcessStepInfo,
            InterpolationSummary,
            TrackSegmentDetail,
            MatchGroupDetail,
            ErrorResultDetail,
            InterpolatedPointResponse,
        )

        # 1. 获取任务基本信息
        task = self.db.query(ErrorAnalysisTask).filter(
            ErrorAnalysisTask.task_id == task_id
        ).first()

        if not task:
            raise ValueError(f"任务不存在: {task_id}")

        # 获取雷达站信息
        radar_stations = self.db.query(RadarStation).all()
        station_map = {s.id: s for s in radar_stations}
        station_names = {s.id: s.description or s.station_id or f"站{s.id}" for s in radar_stations}

        # 计算处理时间
        processing_time = 0.0
        if task.started_at and task.completed_at:
            processing_time = (task.completed_at - task.started_at).total_seconds()

        # 2. 构建流程步骤信息
        config = ErrorAnalysisConfig(**task.config) if task.config else ErrorAnalysisConfig()
        process_steps = self._build_process_steps(task, processing_time)

        # 3. 获取航迹段数据
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
                station_name=station_name
            )
            segments_detail.append(detail)

            # 按雷达站统计
            if station_name not in segments_by_station:
                segments_by_station[station_name] = 0
            segments_by_station[station_name] += 1

        segments_summary = {
            "total_segments": len(segments),
            "total_points": sum(s.point_count for s in segments),
            "by_station": segments_by_station
        }

        # 4. 获取插值点数据
        interpolation_summary = None
        interpolated_points = []
        if include_points:
            from app.models.error_analysis import TrackInterpolatedPoint
            points = self.db.query(TrackInterpolatedPoint).filter(
                TrackInterpolatedPoint.task_id == task_id
            ).limit(10000).all()  # 限制最多返回10000条

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
                    is_original=is_original
                ))

            interpolation_summary = InterpolationSummary(
                total_points=len(points),
                original_points=original_count,
                interpolated_points=interpolated_count,
                stations=points_by_station
            )
        else:
            # 只统计，不返回明细
            from app.models.error_analysis import TrackInterpolatedPoint
            total_points = self.db.query(TrackInterpolatedPoint).filter(
                TrackInterpolatedPoint.task_id == task_id
            ).count()
            original_points = self.db.query(TrackInterpolatedPoint).filter(
                TrackInterpolatedPoint.task_id == task_id,
                TrackInterpolatedPoint.is_original == 1
            ).count()

            points_by_station = {}
            points = self.db.query(
                TrackInterpolatedPoint.station_id,
                func.count(TrackInterpolatedPoint.id).label('count')
            ).filter(
                TrackInterpolatedPoint.task_id == task_id
            ).group_by(TrackInterpolatedPoint.station_id).all()

            for p in points:
                station_name = station_names.get(p.station_id, f"站{p.station_id}")
                points_by_station[station_name] = p.count

            interpolation_summary = InterpolationSummary(
                total_points=total_points,
                original_points=original_points,
                interpolated_points=total_points - original_points,
                stations=points_by_station
            )

        # 5. 获取匹配组数据
        match_groups_db = self.db.query(MatchGroup).filter(
            MatchGroup.task_id == task_id
        ).all()

        match_groups_detail = []
        for g in match_groups_db:
            # 提取涉及的雷达站
            station_ids = list(set(
                p.get('station_id') for p in (g.match_points or [])
                if isinstance(p, dict) and p.get('station_id') is not None
            ))

            # 计算时间差
            time_diff_ms = 0.0
            if g.match_time:
                # 简单计算：第一个点和最后一个点的时间差
                time_diff_ms = 0.0

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
                time_difference_ms=time_diff_ms
            ))

        # 计算匹配统计
        if match_groups_db:
            avg_distances = [g.avg_distance for g in match_groups_db if g.avg_distance is not None]
            # 提取所有涉及的雷达站ID
            all_station_ids = set()
            for g in match_groups_db:
                for p in (g.match_points or []):
                    if isinstance(p, dict) and p.get('station_id') is not None:
                        all_station_ids.add(p.get('station_id'))
            match_summary = {
                "total_groups": len(match_groups_db),
                "total_points": sum(g.point_count for g in match_groups_db),
                "avg_distance_mean": sum(avg_distances) / len(avg_distances) if avg_distances else 0.0,
                "stations_involved": len(all_station_ids)
            }
        else:
            match_summary = {
                "total_groups": 0,
                "total_points": 0,
                "avg_distance_mean": 0.0,
                "stations_involved": 0
            }

        # 6. 获取误差结果详情
        error_results_db = self.db.query(ErrorResult).filter(
            ErrorResult.task_id == task_id
        ).all()

        error_results_detail = []
        for e in error_results_db:
            # 质量评级
            azimuth_quality = self._evaluate_quality(e.azimuth_error, "azimuth")
            range_quality = self._evaluate_quality(e.range_error, "range")
            elevation_quality = self._evaluate_quality(e.elevation_error, "elevation")

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
                elevation_quality=elevation_quality
            ))

        # 7. 组装返回
        return {
            "task_id": task.task_id,
            "status": task.status,
            "progress": task.progress,
            "error_message": task.error_message,
            "created_at": task.created_at,
            "started_at": task.started_at,
            "completed_at": task.completed_at,
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
            "processing_time_seconds": processing_time,
            "total_segments": len(segments),
            "total_match_groups": len(match_groups_db),
            "total_interpolated_points": interpolation_summary.total_points if interpolation_summary else 0
        }

    def _build_process_steps(self, task: ErrorAnalysisTask, processing_time: float) -> List[Dict]:
        """构建流程步骤信息"""
        from app.schemas.error_analysis import ProcessStepInfo

        steps = [
            {
                "step_id": "extracting",
                "step_name": "航迹提取",
                "step_description": "从原始雷达数据中提取飞机航迹，根据时间连续性和空间相关性将点连接成段",
                "status": "completed" if task.status != ErrorAnalysisTaskStatus.PENDING else "pending"
            },
            {
                "step_id": "interpolating",
                "step_name": "航迹插值",
                "step_description": "对航迹进行时间对齐和空间插值，使不同雷达站的航迹能够在同一时间点进行比较",
                "status": "completed" if task.status in [ErrorAnalysisTaskStatus.COMPLETED, ErrorAnalysisTaskStatus.CALCULATING, ErrorAnalysisTaskStatus.MATCHING] else "pending"
            },
            {
                "step_id": "matching",
                "step_name": "航迹匹配",
                "step_description": "在时间窗口内，将不同雷达站观测到的同一架飞机进行匹配，形成匹配组",
                "status": "completed" if task.status in [ErrorAnalysisTaskStatus.COMPLETED, ErrorAnalysisTaskStatus.CALCULATING] else "pending"
            },
            {
                "step_id": "calculating",
                "step_name": "误差计算",
                "step_description": "基于匹配组结果，计算各雷达站的系统误差（方位角、距离、俯仰角）",
                "status": "completed" if task.status == ErrorAnalysisTaskStatus.COMPLETED else "pending"
            }
        ]

        # 根据任务状态更新步骤状态
        status_mapping = {
            ErrorAnalysisTaskStatus.PENDING: ["pending", "pending", "pending", "pending"],
            ErrorAnalysisTaskStatus.EXTRACTING: ["running", "pending", "pending", "pending"],
            ErrorAnalysisTaskStatus.INTERPOLATING: ["completed", "running", "pending", "pending"],
            ErrorAnalysisTaskStatus.MATCHING: ["completed", "completed", "running", "pending"],
            ErrorAnalysisTaskStatus.CALCULATING: ["completed", "completed", "completed", "running"],
            ErrorAnalysisTaskStatus.COMPLETED: ["completed", "completed", "completed", "completed"],
            ErrorAnalysisTaskStatus.FAILED: ["completed", "completed", "completed", "failed"]
        }

        mapped_statuses = status_mapping.get(task.status, ["pending"] * 4)
        for i, step in enumerate(steps):
            step["status"] = mapped_statuses[i]
            step["duration_seconds"] = None  # 可以后续添加更精确的时间统计

        return steps

    def _evaluate_quality(self, value: float, error_type: str) -> str:
        """评估误差质量等级"""
        thresholds = {
            "azimuth": [0.5, 1.0, 2.0],  # 方位角阈值（度）
            "range": [50, 100, 200],       # 距离阈值（米）
            "elevation": [0.5, 1.0, 2.0]   # 俯仰角阈值（度）
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
