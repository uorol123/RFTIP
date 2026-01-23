"""
禁飞区相关的 Pydantic 模型
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ZoneCoordinates(BaseModel):
    """禁飞区坐标模型"""
    type: str = Field(..., description="类型 (circle/polygon)")
    center: Optional[dict] = Field(None, description="圆形中心点 {lat, lng}")
    radius: Optional[float] = Field(None, description="圆形半径（米）")
    vertices: Optional[list[dict]] = Field(None, description="多边形顶点列表 [{lat, lng}, ...]")


class RestrictedZoneBase(BaseModel):
    """禁飞区基础模型"""
    zone_name: str = Field(..., max_length=100, description="禁飞区名称")
    zone_type: str = Field(..., description="禁飞区类型 (circle/polygon)")
    coordinates: str = Field(..., description="坐标数据（JSON字符串）")
    min_altitude: float = Field(0, ge=0, description="最低高度限制（米）")
    max_altitude: float = Field(10000, ge=0, description="最高高度限制（米）")
    is_active: bool = Field(True, description="是否激活")
    notification_email: Optional[str] = Field(None, max_length=100, description="预警通知邮箱")
    notification_enabled: bool = Field(True, description="是否启用邮件通知")
    description: Optional[str] = Field(None, description="描述")


class RestrictedZoneCreate(RestrictedZoneBase):
    """禁飞区创建模型"""
    pass


class RestrictedZoneUpdate(BaseModel):
    """禁飞区更新模型"""
    zone_name: Optional[str] = Field(None, max_length=100, description="禁飞区名称")
    min_altitude: Optional[float] = Field(None, ge=0, description="最低高度限制（米）")
    max_altitude: Optional[float] = Field(None, ge=0, description="最高高度限制（米）")
    is_active: Optional[bool] = Field(None, description="是否激活")
    notification_email: Optional[str] = Field(None, max_length=100, description="预警通知邮箱")
    notification_enabled: Optional[bool] = Field(None, description="是否启用邮件通知")
    description: Optional[str] = Field(None, description="描述")


class RestrictedZoneResponse(RestrictedZoneBase):
    """禁飞区响应模型"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ZoneIntrusionResponse(BaseModel):
    """禁飞区入侵记录响应模型"""
    id: int
    zone_id: int
    track_id: str
    timestamp: datetime
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    intrusion_type: str
    severity: str
    duration: Optional[float] = None
    distance_from_boundary: Optional[float] = None
    target_info: Optional[str] = None
    notification_sent: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ZoneIntrusionListResponse(BaseModel):
    """禁飞区入侵记录列表响应模型"""
    total: int
    intrusions: list[ZoneIntrusionResponse]
