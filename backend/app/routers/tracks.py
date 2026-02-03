"""
轨迹处理路由 - 处理轨迹数据处理和查询
"""
from typing import Annotated, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from core.database import get_db
from app.routers.auth import get_current_active_user, UserResponse
from app.schemas.track import (
    TrackProcessRequest,
    TrackProcessResponse,
    RawTrackResponse,
    CorrectedTrackResponse,
    TrackQueryParams,
    TrackDetailResponse,
    TrackPointsResponse,
    TaskStatusResponse,
)
from app.services import track_service

router = APIRouter(prefix="/tracks", tags=["tracks"])


@router.post("/process", response_model=TrackProcessResponse)
async def process_tracks(
    request: TrackProcessRequest,
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    处理轨迹数据

    - **mode**: 处理模式
      - `multi_source`: 多源参考模式（RANSAC 算法）- 适用于多台雷达探测同一目标
      - `single_source`: 单源盲测模式（卡尔曼滤波）- 适用于单站数据平滑
    - **ransac_threshold**: RANSAC 阈值（0-1），默认 0.5
    - **kalman_process_noise**: 卡尔曼滤波过程噪声，默认 0.1
    - **kalman_measurement_noise**: 卡尔曼滤波测量噪声，默认 1.0
    """
    try:
        result = track_service.process_tracks(request, db)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/raw", response_model=list[RawTrackResponse])
async def get_raw_tracks(
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
    file_id: Annotated[Optional[int], Query()] = None,
    track_id: Annotated[Optional[str], Query()] = None,
    start_time: Annotated[Optional[datetime], Query()] = None,
    end_time: Annotated[Optional[datetime], Query()] = None,
    limit: Annotated[int, Query(ge=1, le=10000)] = 1000,
):
    """
    查询原始轨迹数据
    """
    tracks = track_service.get_raw_tracks(db, file_id, track_id, start_time, end_time, limit)
    return [RawTrackResponse.model_validate(t) for t in tracks]


@router.get("/corrected", response_model=list[CorrectedTrackResponse])
async def get_corrected_tracks(
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
    file_id: Annotated[Optional[int], Query()] = None,
    track_id: Annotated[Optional[str], Query()] = None,
    start_time: Annotated[Optional[datetime], Query()] = None,
    end_time: Annotated[Optional[datetime], Query()] = None,
    limit: Annotated[int, Query(ge=1, le=10000)] = 1000,
):
    """
    查询修正后的轨迹数据
    """
    tracks = track_service.get_corrected_tracks(db, file_id, track_id, start_time, end_time, limit)
    return [CorrectedTrackResponse.model_validate(t) for t in tracks]


@router.get("/summary")
async def get_track_summary(
    track_id: str,
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    获取轨迹摘要信息
    """
    corrected_tracks = track_service.get_corrected_tracks(db, None, track_id, None, None, limit=10000)

    if not corrected_tracks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到轨迹数据",
        )

    # 计算摘要
    import numpy as np

    lats = [t.latitude for t in corrected_tracks]
    lngs = [t.longitude for t in corrected_tracks]
    alts = [t.altitude or 0 for t in corrected_tracks]

    return {
        "track_id": track_id,
        "point_count": len(corrected_tracks),
        "time_span": {
            "start": corrected_tracks[0].timestamp.isoformat(),
            "end": corrected_tracks[-1].timestamp.isoformat(),
            "duration_seconds": (corrected_tracks[-1].timestamp - corrected_tracks[0].timestamp).total_seconds()
        },
        "position": {
            "min_lat": float(np.min(lats)),
            "max_lat": float(np.max(lats)),
            "min_lng": float(np.min(lngs)),
            "max_lng": float(np.max(lngs)),
        },
        "altitude": {
            "min": float(np.min(alts)) if alts else 0,
            "max": float(np.max(alts)) if alts else 0,
            "avg": float(np.mean(alts)) if alts else 0,
        },
        "quality": {
            "avg_confidence": float(np.mean([t.confidence_score or 0.5 for t in corrected_tracks])),
            "outlier_count": sum(1 for t in corrected_tracks if t.is_outlier),
        }
    }


@router.get("/{track_id}", response_model=TrackDetailResponse)
async def get_track_detail(
    track_id: str,
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    获取单个轨迹详情
    """
    # 获取原始轨迹点
    raw_tracks = track_service.get_raw_tracks(db, None, track_id, None, None, limit=10000)
    corrected_tracks = track_service.get_corrected_tracks(db, None, track_id, None, None, limit=10000)

    if not raw_tracks and not corrected_tracks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到轨迹数据",
        )

    # 获取轨迹时间范围
    all_tracks = corrected_tracks if corrected_tracks else raw_tracks
    start_time = all_tracks[0].timestamp
    end_time = all_tracks[-1].timestamp
    duration_seconds = (end_time - start_time).total_seconds()

    return TrackDetailResponse(
        track_id=track_id,
        file_id=raw_tracks[0].file_id if raw_tracks else corrected_tracks[0].file_id,
        point_count=len(corrected_tracks) if corrected_tracks else len(raw_tracks),
        start_time=start_time,
        end_time=end_time,
        duration_seconds=duration_seconds,
        raw_points=[RawTrackResponse.model_validate(t) for t in raw_tracks],
        corrected_points=[CorrectedTrackResponse.model_validate(t) for t in corrected_tracks],
    )


@router.get("/points", response_model=TrackPointsResponse)
async def get_track_points(
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
    track_id: str | None = None,
    file_id: int | None = None,
    limit: int = 1000,
):
    """
    获取轨迹点数据
    """
    tracks = track_service.get_corrected_tracks(db, file_id, track_id, None, None, limit=limit)

    return TrackPointsResponse(
        track_id=track_id or (tracks[0].track_id if tracks else ""),
        points=[CorrectedTrackResponse.model_validate(t) for t in tracks],
        total_count=len(tracks),
    )


@router.get("/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_track_task_status(
    task_id: str,
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
):
    """
    查询轨迹处理任务状态
    """
    from datetime import datetime

    # 简化实现：返回模拟状态
    # 实际应该从任务队列（如 Celery）获取状态
    return TaskStatusResponse(
        task_id=task_id,
        status="completed",
        progress=100.0,
        message="轨迹处理完成",
        result={
            "total_points": 0,
            "corrected_points": 0,
            "outliers_detected": 0,
        },
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
