"""
数据查询路由 - 提供各类数据查询接口
"""
from typing import Annotated, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from core.database import get_db
from app.routers.auth import get_current_active_user, UserResponse
from app.schemas.track import RadarStationResponse

router = APIRouter(prefix="/query", tags=["query"])


@router.get("/radar-stations", response_model=list[RadarStationResponse])
async def list_radar_stations(
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
    status_filter: Annotated[Optional[str], Query()] = None,
):
    """
    查询雷达站列表

    - **status_filter**: 状态过滤 (active/inactive/maintenance)
    """
    from app.models.flight_track import RadarStation

    query = db.query(RadarStation)

    if status_filter:
        query = query.filter(RadarStation.status == status_filter)

    stations = query.order_by(RadarStation.station_code).all()
    return [RadarStationResponse.model_validate(s) for s in stations]


@router.get("/statistics")
async def get_statistics(
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    获取系统统计信息
    """
    from app.models.data_file import DataFile
    from app.models.flight_track import FlightTrackRaw, FlightTrackCorrected, RadarStation
    from app.models.restricted_zone import RestrictedZone, ZoneIntrusion
    from sqlalchemy import func

    stats = {}

    # 文件统计
    stats["files"] = {
        "total": db.query(func.count(DataFile.id)).scalar(),
        "completed": db.query(func.count(DataFile.id)).filter(DataFile.status == "completed").scalar(),
        "processing": db.query(func.count(DataFile.id)).filter(DataFile.status == "processing").scalar(),
        "failed": db.query(func.count(DataFile.id)).filter(DataFile.status == "failed").scalar(),
    }

    # 轨迹统计
    stats["tracks"] = {
        "raw_count": db.query(func.count(FlightTrackRaw.id)).scalar(),
        "corrected_count": db.query(func.count(FlightTrackCorrected.id)).scalar(),
        "unique_tracks": db.query(func.count(func.distinct(FlightTrackRaw.track_id))).scalar(),
    }

    # 雷达站统计
    stats["radar_stations"] = {
        "total": db.query(func.count(RadarStation.id)).scalar(),
        "active": db.query(func.count(RadarStation.id)).filter(RadarStation.status == "active").scalar(),
    }

    # 禁飞区统计
    stats["zones"] = {
        "total": db.query(func.count(RestrictedZone.id)).scalar(),
        "active": db.query(func.count(RestrictedZone.id)).filter(RestrictedZone.is_active == 1).scalar(),
    }

    # 入侵记录统计
    stats["intrusions"] = {
        "total": db.query(func.count(ZoneIntrusion.id)).scalar(),
        "high_severity": db.query(func.count(ZoneIntrusion.id)).filter(ZoneIntrusion.severity == "high").scalar(),
        "today": db.query(func.count(ZoneIntrusion.id)).filter(
            func.date(ZoneIntrusion.timestamp) == func.current_date()
        ).scalar(),
    }

    return stats


@router.get("/health")
async def get_system_health(
    db: Annotated[Session, Depends(get_db)],
):
    """
    获取系统健康状态
    """
    from sqlalchemy import text

    health = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {}
    }

    # 检查数据库连接
    try:
        db.execute(text("SELECT 1"))
        health["components"]["database"] = {"status": "healthy"}
    except Exception as e:
        health["status"] = "unhealthy"
        health["components"]["database"] = {"status": "unhealthy", "error": str(e)}

    return health
