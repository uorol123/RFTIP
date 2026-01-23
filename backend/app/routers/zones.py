"""
禁飞区管理路由 - 处理禁飞区创建、查询和入侵检测
"""
from typing import Annotated, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from core.database import get_db
from app.routers.auth import get_current_active_user, UserResponse
from app.schemas.zone import (
    RestrictedZoneCreate,
    RestrictedZoneUpdate,
    RestrictedZoneResponse,
    ZoneIntrusionResponse,
    ZoneIntrusionListResponse,
)
from app.services import zone_service

router = APIRouter(prefix="/zones", tags=["zones"])


@router.post("/", response_model=RestrictedZoneResponse, status_code=status.HTTP_201_CREATED)
async def create_zone(
    zone_data: RestrictedZoneCreate,
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    创建禁飞区

    - **zone_name**: 禁飞区名称
    - **zone_type**: 禁飞区类型 (circle/polygon)
    - **coordinates**: 坐标数据（JSON 字符串）
      - 圆形: {"type": "circle", "center": {"lat": 0, "lng": 0}, "radius": 1000}
      - 多边形: {"type": "polygon", "vertices": [{"lat": 0, "lng": 0}, ...]}
    - **min_altitude**: 最低高度限制（米）
    - **max_altitude**: 最高高度限制（米）
    - **notification_email**: 预警通知邮箱（可选）
    """
    zone = zone_service.create_zone(db, zone_data, current_user.id)
    return RestrictedZoneResponse.model_validate(zone)


@router.get("/", response_model=list[RestrictedZoneResponse])
async def list_zones(
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    """
    获取当前用户的禁飞区列表
    """
    from app.models.restricted_zone import RestrictedZone

    zones = (
        db.query(RestrictedZone)
        .filter(RestrictedZone.user_id == current_user.id)
        .order_by(RestrictedZone.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [RestrictedZoneResponse.model_validate(z) for z in zones]


@router.get("/{zone_id}", response_model=RestrictedZoneResponse)
async def get_zone(
    zone_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    获取禁飞区详情
    """
    zone = zone_service.get_zone_by_id(db, zone_id, current_user.id)
    if not zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="禁飞区不存在",
        )
    return RestrictedZoneResponse.model_validate(zone)


@router.put("/{zone_id}", response_model=RestrictedZoneResponse)
async def update_zone(
    zone_id: int,
    zone_update: RestrictedZoneUpdate,
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    更新禁飞区信息
    """
    zone = zone_service.update_zone(db, zone_id, zone_update, current_user.id)
    if not zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="禁飞区不存在",
        )
    return RestrictedZoneResponse.model_validate(zone)


@router.delete("/{zone_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_zone(
    zone_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    删除禁飞区
    """
    success = zone_service.delete_zone(db, zone_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="禁飞区不存在",
        )
    return None


@router.post("/detect-intrusions", response_model=list[ZoneIntrusionResponse])
async def detect_intrusions(
    track_id: str,
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
    start_time: Annotated[Optional[datetime], Query()] = None,
    end_time: Annotated[Optional[datetime], Query()] = None,
):
    """
    检测指定轨迹的禁飞区入侵

    会自动检测所有激活的禁飞区，并记录入侵事件
    """
    intrusions = zone_service.detect_intrusions(db, track_id, start_time, end_time)
    return [ZoneIntrusionResponse.model_validate(i) for i in intrusions]


@router.get("/intrusions/list", response_model=ZoneIntrusionListResponse)
async def list_intrusions(
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
    zone_id: Annotated[Optional[int], Query()] = None,
    track_id: Annotated[Optional[str], Query()] = None,
    start_time: Annotated[Optional[datetime], Query()] = None,
    end_time: Annotated[Optional[datetime], Query()] = None,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
):
    """
    查询入侵记录
    """
    intrusions = zone_service.get_intrusions(db, zone_id, track_id, start_time, end_time, limit)
    return ZoneIntrusionListResponse(
        total=len(intrusions),
        intrusions=[ZoneIntrusionResponse.model_validate(i) for i in intrusions]
    )
