"""
禁飞区相关模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base


class RestrictedZone(Base):
    """用户自定义禁飞区表"""
    __tablename__ = "restricted_zones"

    id = Column(Integer, primary_key=True, index=True, comment="禁飞区ID")
    user_id = Column(Integer, nullable=False, index=True, comment="创建用户ID")
    zone_name = Column(String(100), nullable=False, comment="禁飞区名称")
    zone_type = Column(String(20), nullable=False, comment="禁飞区类型 (circle/polygon)")
    coordinates = Column(Text, nullable=False, comment="坐标数据（JSON）圆形:中心点+半径;多边形:顶点列表")
    min_altitude = Column(Float, default=0, comment="最低高度限制（米）")
    max_altitude = Column(Float, default=10000, comment="最高高度限制（米）")
    is_active = Column(Integer, default=1, comment="是否激活 (0:禁用, 1:激活)")
    notification_email = Column(String(100), comment="预警通知邮箱")
    notification_enabled = Column(Integer, default=1, comment="是否启用邮件通知 (0:禁用, 1:启用)")
    description = Column(Text, comment="描述")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关系
    intrusions = relationship("ZoneIntrusion", back_populates="zone", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<RestrictedZone(id={self.id}, name='{self.zone_name}', type='{self.zone_type}')>"


class ZoneIntrusion(Base):
    """禁飞区入侵记录表"""
    __tablename__ = "zone_intrusions"

    id = Column(Integer, primary_key=True, index=True, comment="入侵记录ID")
    zone_id = Column(Integer, ForeignKey("restricted_zones.id"), nullable=False, index=True, comment="禁飞区ID")
    track_id = Column(String(50), nullable=False, index=True, comment="轨迹编号")
    timestamp = Column(DateTime, nullable=False, index=True, comment="入侵时间")
    latitude = Column(Float, nullable=False, comment="入侵位置纬度")
    longitude = Column(Float, nullable=False, comment="入侵位置经度")
    altitude = Column(Float, comment="入侵高度（米）")
    intrusion_type = Column(String(20), default="breach", comment="入侵类型 (breach/crossing/loitering)")
    severity = Column(String(20), default="medium", comment="严重程度 (low/medium/high)")
    duration = Column(Float, comment="持续时间（秒）")
    distance_from_boundary = Column(Float, comment="距离边界（米，负数表示内部）")
    target_info = Column(Text, comment="目标信息（JSON）")
    notification_sent = Column(Integer, default=0, comment="是否已发送通知 (0:否, 1:是)")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    # 关系
    zone = relationship("RestrictedZone", back_populates="intrusions")

    def __repr__(self):
        return f"<ZoneIntrusion(id={self.id}, zone_id={self.zone_id}, track_id='{self.track_id}')>"
