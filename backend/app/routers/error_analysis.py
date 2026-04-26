"""
误差分析API路由

提供误差分析功能的API接口
算法：基于梯度下降的迭代寻优算法
"""
from typing import Annotated, List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func

from core.database import get_db
from app.routers.auth import get_current_active_user, UserResponse
from app.schemas.error_analysis import (
    ErrorAnalysisRequest,
    ErrorAnalysisTaskResponse,
    ErrorAnalysisResult,
    ErrorChartResponse,
    ErrorAnalysisConfig,
    TaskListResponse,
    TrackSegmentResponse,
    MatchGroupResponse,
    TaskDetailResponse,
)
from app.services.error_analysis_service import ErrorAnalysisService

router = APIRouter(prefix="/error-analysis", tags=["error-analysis"])


@router.post("/analyze", response_model=ErrorAnalysisTaskResponse)
async def create_analysis_task(
    request: ErrorAnalysisRequest,
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
    background_tasks: BackgroundTasks
):
    """
    创建误差分析任务

    - **file_id**: 数据文件ID
    - **config**: 分析配置参数（可选）
      - grid_resolution: 网格分辨率（度）
      - time_window: 时间窗口（秒）
      - match_distance_threshold: 匹配距离阈值（度）
      - min_track_points: 最小航迹点数
      - optimization_steps: 优化步长序列
      - range_optimization_steps: 距离优化步长序列
      - cost_weights: 代价函数权重
      - max_match_groups: 最大匹配组数
    """
    try:
        service = ErrorAnalysisService(db)
        task = service.create_analysis_task(request, current_user.id)

        # 在后台执行分析
        background_tasks.add_task(execute_analysis_task, db, task.task_id)

        return task

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建分析任务失败: {str(e)}"
        )


@router.get("/config", response_model=ErrorAnalysisConfig)
async def get_analysis_config(
    current_user: Annotated[UserResponse, Depends(get_current_active_user)]
):
    """
    获取默认分析配置
    """
    return ErrorAnalysisConfig()


@router.get("/tasks", response_model=TaskListResponse)
async def list_analysis_tasks(
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
    page: Annotated[int, Query(ge=1, description="页码")] = 1,
    limit: Annotated[int, Query(ge=1, le=100, description="每页数量")] = 20
):
    """
    获取误差分析任务列表

    - **page**: 页码（从1开始）
    - **limit**: 每页数量（1-100）
    """
    try:
        service = ErrorAnalysisService(db)
        offset = (page - 1) * limit
        tasks, total = service.list_tasks(
            user_id=current_user.id,
            limit=limit,
            offset=offset
        )

        return TaskListResponse(
            tasks=tasks,
            total=total,
            page=page,
            limit=limit
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取任务列表失败: {str(e)}"
        )


@router.get("/tasks/{task_id}", response_model=ErrorAnalysisTaskResponse)
async def get_task_detail(
    task_id: str,
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    获取任务详情

    - **task_id**: 任务ID
    """
    try:
        service = ErrorAnalysisService(db)
        task = service.get_task_status(task_id)
        return task

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取任务详情失败: {str(e)}"
        )


@router.get("/tasks/{task_id}/results", response_model=ErrorAnalysisResult)
async def get_analysis_results(
    task_id: str,
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    获取分析结果

    - **task_id**: 任务ID

    返回完整的误差分析结果，包括：
    - 各雷达站的误差值
    - 匹配统计信息
    - 处理摘要
    """
    try:
        service = ErrorAnalysisService(db)
        results = service.get_analysis_results(task_id)
        return results

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取分析结果失败: {str(e)}"
        )


@router.get("/tasks/{task_id}/segments", response_model=List[TrackSegmentResponse])
async def get_track_segments(
    task_id: str,
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=1000, description="限制数量")] = 100
):
    """
    获取航迹段列表

    - **task_id**: 任务ID
    - **limit**: 限制数量
    """
    try:
        service = ErrorAnalysisService(db)
        segments = service.get_track_segments(task_id, limit)
        return segments

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取航迹段失败: {str(e)}"
        )


@router.get("/tasks/{task_id}/matches", response_model=List[MatchGroupResponse])
async def get_match_groups(
    task_id: str,
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=1000, description="限制数量")] = 100
):
    """
    获取匹配组列表

    - **task_id**: 任务ID
    - **limit**: 限制数量
    """
    try:
        service = ErrorAnalysisService(db)
        matches = service.get_match_groups(task_id, limit)
        return matches

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取匹配组失败: {str(e)}"
        )


@router.get("/tasks/{task_id}/chart", response_model=ErrorChartResponse)
async def get_chart_data(
    task_id: str,
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    获取图表数据

    - **task_id**: 任务ID

    返回用于可视化展示的数据：
    - 各雷达站的误差值
    - 匹配点数
    - 置信度
    - 匹配组大小分布
    """
    try:
        service = ErrorAnalysisService(db)
        chart_data = service.get_chart_data(task_id)
        return chart_data

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取图表数据失败: {str(e)}"
        )


# ========== 数据查询端点 ==========

from app.models.flight_track import RadarStation, FlightTrackRaw
from pydantic import BaseModel

class RadarStationInfo(BaseModel):
    """雷达站信息"""
    id: int
    station_id: str
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True

class TrackInfo(BaseModel):
    """轨迹信息"""
    batch_id: str
    point_count: int
    start_time: datetime
    end_time: datetime

class TimeRange(BaseModel):
    """时间范围"""
    start_time: datetime
    end_time: datetime


@router.get("/radar-stations", response_model=List[RadarStationInfo])
async def list_radar_stations(
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    获取所有雷达站列表

    返回数据库中所有已配置的雷达站信息
    """
    try:
        stations = db.query(RadarStation).all()
        return [
            RadarStationInfo(
                id=s.id,
                station_id=s.station_id,
                latitude=s.latitude,
                longitude=s.longitude,
                altitude=s.altitude,
                description=s.description
            )
            for s in stations
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取雷达站列表失败: {str(e)}"
        )


@router.get("/radar-stations/{station_id}/tracks", response_model=List[TrackInfo])
async def get_radar_station_tracks(
    station_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    获取某雷达站观测的所有轨迹

    - **station_id**: 雷达站ID（数据库主键）

    返回该雷达站观测到的所有飞机批号列表及其时间范围
    """
    try:
        # 查询该雷达站的所有轨迹点
        tracks = db.query(
            FlightTrackRaw.batch_id,
            func.count(FlightTrackRaw.id).label('point_count'),
            func.min(FlightTrackRaw.timestamp).label('start_time'),
            func.max(FlightTrackRaw.timestamp).label('end_time')
        ).filter(
            FlightTrackRaw.radar_station_id == station_id
        ).group_by(
            FlightTrackRaw.batch_id
        ).all()

        return [
            TrackInfo(
                batch_id=t.batch_id,
                point_count=t.point_count,
                start_time=t.start_time,
                end_time=t.end_time
            )
            for t in tracks
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取雷达站轨迹失败: {str(e)}"
        )


@router.get("/tracks/time-range", response_model=TimeRange)
async def get_tracks_time_range(
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
    batch_ids: str = Query(..., description="逗号分隔的轨迹批号列表")
):
    """
    获取指定轨迹的时间范围

    - **batch_ids**: 逗号分隔的轨迹批号列表

    返回这些轨迹的最早和最晚时间
    """
    try:
        batch_list = [b.strip() for b in batch_ids.split(',')]
        result = db.query(
            func.min(FlightTrackRaw.timestamp).label('start_time'),
            func.max(FlightTrackRaw.timestamp).label('end_time')
        ).filter(
            FlightTrackRaw.batch_id.in_(batch_list)
        ).first()

        if not result or not result.start_time:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="未找到指定的轨迹"
            )

        return TimeRange(
            start_time=result.start_time,
            end_time=result.end_time
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取时间范围失败: {str(e)}"
        )


@router.get("/common-tracks", response_model=List[TrackInfo])
async def get_common_tracks(
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
    station_ids: str = Query(..., description="逗号分隔的雷达站ID列表")
):
    """
    获取多个雷达站共同观测到的轨迹

    - **station_ids**: 逗号分隔的雷达站ID列表

    返回这些雷达站同时观测到的飞机批号列表
    """
    try:
        station_list = [int(s.strip()) for s in station_ids.split(',')]
        station_set = set(station_list)

        # 查询每个 batch_id 被哪些雷达站观测到（兼容 MySQL）
        track_station_rows = db.query(
            FlightTrackRaw.batch_id,
            FlightTrackRaw.radar_station_id
        ).filter(
            FlightTrackRaw.radar_station_id.in_(station_list)
        ).distinct().all()

        # 按 batch_id 分组统计雷达站
        from collections import defaultdict
        batch_stations = defaultdict(set)
        for row in track_station_rows:
            batch_stations[row.batch_id].add(row.radar_station_id)

        # 筛选出被所有指定雷达站都观测到的轨迹
        common_batch_ids = [
            bid for bid, sids in batch_stations.items()
            if station_set.issubset(sids)
        ]

        common_tracks = []
        for bid in common_batch_ids:
            info = db.query(
                FlightTrackRaw.batch_id,
                func.count(FlightTrackRaw.id).label('point_count'),
                func.min(FlightTrackRaw.timestamp).label('start_time'),
                func.max(FlightTrackRaw.timestamp).label('end_time')
            ).filter(
                FlightTrackRaw.batch_id == bid
            ).first()

            if info:
                common_tracks.append(TrackInfo(
                    batch_id=info.batch_id,
                    point_count=info.point_count,
                    start_time=info.start_time,
                    end_time=info.end_time
                ))

        return common_tracks
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取共同轨迹失败: {str(e)}"
        )


@router.get("/tasks/{task_id}/detail", response_model=TaskDetailResponse)
async def get_task_detail_full(
    task_id: str,
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
    include_intermediate: bool = Query(True, description="是否包含中间步骤详细数据"),
    include_points: bool = Query(False, description="是否包含插值点明细")
):
    """
    获取完整任务详情

    返回任务的完整信息，包括：
    - 任务基本信息（配置参数、状态、时间等）
    - 航迹段信息（提取了多少段、每段的时间范围、点数等）
    - 插值点数据概要（插值前后对比）
    - 匹配组信息（匹配了多少组、每组的详情）
    - 最终误差结果（各雷达站的方位角误差、距离误差、俯仰角误差等）
    - MRRA 分析流程各步骤的说明
    """
    try:
        service = ErrorAnalysisService(db)
        detail = service.get_task_detail_full(
            task_id,
            include_intermediate=include_intermediate,
            include_points=include_points
        )
        return detail

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取任务详情失败: {str(e)}"
        )


def execute_analysis_task(db: Session, task_id: str):
    """
    后台执行分析任务的函数

    Args:
        db: 数据库会话
        task_id: 任务ID
    """
    from core.logging import get_logger
    logger = get_logger(__name__)

    try:
        service = ErrorAnalysisService(db)
        service.execute_analysis(task_id)
        logger.info(f"后台任务完成: {task_id}")
    except Exception as e:
        logger.error(f"后台任务失败: {task_id}, 错误: {str(e)}")


# ========== 算法管理端点 ==========

from app.utils.error_analysis import registry, AlgorithmFactory


@router.get("/algorithms")
async def list_algorithms(
    current_user: Annotated[UserResponse, Depends(get_current_active_user)]
):
    """
    获取所有可用的误差分析算法

    返回系统中所有已注册的算法列表，包括：
    - 算法名称
    - 版本号
    - 显示名称
    - 描述
    - 是否支持俯仰角误差计算
    """
    return {
        "algorithms": registry.list_algorithms()
    }


@router.get("/algorithms/{algorithm_name}")
async def get_algorithm_info(
    algorithm_name: str,
    current_user: Annotated[UserResponse, Depends(get_current_active_user)]
):
    """
    获取指定算法的详细信息

    - **algorithm_name**: 算法名称（如：gradient_descent）
    """
    info = AlgorithmFactory.get_algorithm_info(algorithm_name)
    if info is None:
        available = ", ".join([alg["name"] for alg in registry.list_algorithms()])
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"算法不存在: '{algorithm_name}'. 可用算法: {available}"
        )
    return info


@router.get("/algorithms/{algorithm_name}/config-schema")
async def get_algorithm_config_schema(
    algorithm_name: str,
    current_user: Annotated[UserResponse, Depends(get_current_active_user)]
):
    """
    获取算法配置的 JSON Schema（用于前端动态生成表单）

    - **algorithm_name**: 算法名称

    返回配置参数的JSON Schema，前端可以据此自动生成配置表单
    """
    algorithm_class = registry.get(algorithm_name)
    if algorithm_class is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"算法不存在: {algorithm_name}"
        )

    # 创建临时实例以获取 schema
    temp = AlgorithmFactory.create_algorithm(algorithm_name)
    return temp.get_config_schema()


@router.get("/algorithms/{algorithm_name}/presets")
async def get_algorithm_presets(
    algorithm_name: str,
    current_user: Annotated[UserResponse, Depends(get_current_active_user)]
):
    """
    获取算法的预设配置方案

    - **algorithm_name**: 算法名称

    返回该算法的所有预设配置，如：标准配置、高精度配置、快速配置等
    """
    algorithm_class = registry.get(algorithm_name)
    if algorithm_class is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"算法不存在: {algorithm_name}"
        )

    temp = AlgorithmFactory.create_algorithm(algorithm_name)
    presets = temp.get_config_preset_profiles()

    # 预设名称的中文显示
    PRESET_DISPLAY_NAMES = {
        "standard": "标准配置",
        "high_precision": "高精度配置",
        "fast": "快速分析",
        "coarse": "粗粒度配置",
        "strict": "严格配置",
        "loose": "宽松配置",
        "inverse_variance": "反方差权重",
        "uniform": "均匀权重",
        "robust": "鲁棒配置",
        "smooth": "平滑配置",
        "responsive": "快速响应",
        "tight": "紧密贴合",
        "interpolated": "插值模式",
    }

    return {
        "algorithm": algorithm_name,
        "presets": [
            {
                "name": key,
                "display_name": PRESET_DISPLAY_NAMES.get(key, key),
                "config": preset.model_dump() if hasattr(preset, 'model_dump') else preset
            }
            for key, preset in presets.items()
        ]
    }


@router.post("/algorithms/{algorithm_name}/validate-config")
async def validate_algorithm_config(
    algorithm_name: str,
    config: dict,
    current_user: Annotated[UserResponse, Depends(get_current_active_user)]
):
    """
    验证算法配置

    - **algorithm_name**: 算法名称
    - **config**: 待验证的配置参数

    返回配置是否有效，如果无效则返回错误信息
    """
    try:
        algorithm = AlgorithmFactory.create_algorithm_from_dict(
            algorithm_name, config
        )
        return {"valid": True, "errors": None}
    except Exception as e:
        return {"valid": False, "errors": [str(e)]}


@router.get("/tasks/{task_id}/fused-trajectory")
async def get_fused_trajectory(
    task_id: str,
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    获取融合轨迹数据

    - **task_id**: 任务ID

    返回加权融合后的轨迹点列表，仅对 weighted_lstsq 算法任务有效。
    """
    try:
        task = db.query(ErrorAnalysisTask).filter(
            ErrorAnalysisTask.task_id == task_id
        ).first()

        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")

        metadata = task.result_metadata or {}
        fused_trajectory = metadata.get("fused_trajectory", [])
        match_stats = metadata.get("match_statistics", {})

        return {
            "task_id": task_id,
            "algorithm": task.algorithm_name,
            "fused_trajectory": fused_trajectory,
            "station_weights": match_stats.get("station_weights", {}),
            "total_points": len(fused_trajectory),
            "outlier_removed": match_stats.get("outlier_removed", 0),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取融合轨迹失败: {str(e)}"
        )
