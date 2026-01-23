"""
飞行轨迹相关模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base


class RadarStation(Base):
    """雷达站信息表"""
    __tablename__ = "radar_stations"

    id = Column(Integer, primary_key=True, index=True, comment="雷达站ID")
    station_code = Column(String(20), unique=True, nullable=False, index=True, comment="雷达站编号")
    station_name = Column(String(100), nullable=False, comment="雷达站名称")
    latitude = Column(Float, nullable=False, comment="纬度")
    longitude = Column(Float, nullable=False, comment="经度")
    altitude = Column(Float, default=0, comment="海拔高度（米）")
    max_range = Column(Float, comment="最大探测距离（千米）")
    frequency = Column(String(50), comment="工作频率")
    status = Column(String(20), default="active", comment="状态 (active/inactive/maintenance)")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    # 关系
    raw_tracks = relationship("FlightTrackRaw", back_populates="radar_station")

    def __repr__(self):
        return f"<RadarStation(id={self.id}, code='{self.station_code}', name='{self.station_name}')>"


class FlightTrackRaw(Base):
    """原始飞行轨迹表"""
    __tablename__ = "flight_tracks_raw"

    id = Column(Integer, primary_key=True, index=True, comment="轨迹ID")
    file_id = Column(Integer, ForeignKey("data_files.id"), nullable=False, index=True, comment="数据文件ID")
    track_id = Column(String(50), nullable=False, index=True, comment="轨迹编号")
    timestamp = Column(DateTime, nullable=False, index=True, comment="时间戳")
    radar_station_id = Column(Integer, ForeignKey("radar_stations.id"), comment="雷达站ID")
    target_id = Column(String(50), comment="目标编号")
    latitude = Column(Float, nullable=False, comment="纬度")
    longitude = Column(Float, nullable=False, comment="经度")
    altitude = Column(Float, comment="高度（米）")
    speed = Column(Float, comment="速度（米/秒）")
    heading = Column(Float, comment="航向（度）")
    radar_cross_section = Column(Float, comment="雷达截面积")
    signal_quality = Column(Float, comment="信号质量")
    measurement_id = Column(String(50), comment="测量ID")
    raw_data = Column(Text, comment="原始数据（JSON）")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    # 关系
    data_file = relationship("DataFile", back_populates="raw_tracks")
    radar_station = relationship("RadarStation", back_populates="raw_tracks")
    corrected_tracks = relationship("FlightTrackCorrected", back_populates="raw_track")

    def __repr__(self):
        return f"<FlightTrackRaw(id={self.id}, track_id='{self.track_id}', timestamp={self.timestamp})>"


class FlightTrackCorrected(Base):
    """修正后飞行轨迹表"""
    __tablename__ = "flight_tracks_corrected"

    id = Column(Integer, primary_key=True, index=True, comment="修正轨迹ID")
    raw_track_id = Column(Integer, ForeignKey("flight_tracks_raw.id"), nullable=False, index=True, comment="原始轨迹ID")
    track_id = Column(String(50), nullable=False, index=True, comment="轨迹编号")
    timestamp = Column(DateTime, nullable=False, index=True, comment="时间戳")
    latitude = Column(Float, nullable=False, comment="修正后纬度")
    longitude = Column(Float, nullable=False, comment="修正后经度")
    altitude = Column(Float, comment="修正后高度（米）")
    speed = Column(Float, comment="修正后速度（米/秒）")
    heading = Column(Float, comment="修正后航向（度）")
    correction_method = Column(String(50), comment="修正方法 (ransac/kalman)")
    confidence_score = Column(Float, comment="置信度分数 (0-1)")
    is_outlier = Column(Integer, default=0, comment="是否为离群值 (0:否, 1:是)")
    correction_metadata = Column(Text, comment="修正元数据（JSON）")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    # 关系
    raw_track = relationship("FlightTrackRaw", back_populates="corrected_tracks")

    def __repr__(self):
        return f"<FlightTrackCorrected(id={self.id}, track_id='{self.track_id}', method='{self.correction_method}')>"
