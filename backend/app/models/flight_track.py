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
    file_id = Column(Integer, ForeignKey("data_files.id"), nullable=False, index=True, comment="来源文件ID")
    station_id = Column(String(50), nullable=False, index=True, comment="站号（原始值）")
    latitude = Column(Float, nullable=False, comment="纬度")
    longitude = Column(Float, nullable=False, comment="经度")
    altitude = Column(Float, comment="雷达站高度（米）")
    description = Column(String(255), comment="备注说明")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    # 关系
    raw_tracks = relationship("FlightTrackRaw", back_populates="radar_station")

    def __repr__(self):
        return f"<RadarStation(id={self.id}, station_id='{self.station_id}')>"


class FlightTrackRaw(Base):
    """原始飞行轨迹表"""
    __tablename__ = "flight_tracks_raw"

    id = Column(Integer, primary_key=True, index=True, comment="轨迹ID")
    file_id = Column(Integer, ForeignKey("data_files.id"), nullable=False, index=True, comment="来源文件ID")
    batch_id = Column(String(50), nullable=False, index=True, comment="飞机批号")
    station_id = Column(String(50), nullable=False, index=True, comment="雷达站号")
    radar_station_id = Column(Integer, ForeignKey("radar_stations.id"), nullable=True, comment="雷达站ID（外键）")
    timestamp = Column(DateTime, nullable=False, index=True, comment="观测时间")
    latitude = Column(Float, nullable=False, comment="纬度")
    longitude = Column(Float, nullable=False, comment="经度")
    altitude = Column(Float, comment="高度（米）")
    speed = Column(Float, comment="速度（m/s）")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    # 关系
    data_file = relationship("DataFile", back_populates="raw_tracks")
    radar_station = relationship("RadarStation", back_populates="raw_tracks")
    corrected_tracks = relationship("FlightTrackCorrected", back_populates="raw_track")

    def __repr__(self):
        return f"<FlightTrackRaw(id={self.id}, batch_id='{self.batch_id}', timestamp={self.timestamp})>"


class FlightTrackCorrected(Base):
    """修正后飞行轨迹表"""
    __tablename__ = "flight_tracks_corrected"

    id = Column(Integer, primary_key=True, index=True, comment="修正轨迹ID")
    raw_track_id = Column(Integer, ForeignKey("flight_tracks_raw.id"), nullable=False, index=True, comment="原始轨迹ID")
    batch_id = Column(String(50), nullable=False, index=True, comment="飞机批号")
    timestamp = Column(DateTime, nullable=False, index=True, comment="修正后时间")
    latitude = Column(Float, nullable=False, comment="修正后纬度")
    longitude = Column(Float, nullable=False, comment="修正后经度")
    altitude = Column(Float, comment="修正后高度（米）")
    speed = Column(Float, comment="修正后速度（m/s）")
    correction_method = Column(String(50), comment="修正方法 (ransac/kalman)")
    confidence_score = Column(Float, comment="置信度分数 (0-1)")
    is_outlier = Column(Integer, default=0, comment="是否为离群值 (0:否, 1:是)")
    correction_metadata = Column(Text, comment="修正元数据（JSON）")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    # 关系
    raw_track = relationship("FlightTrackRaw", back_populates="corrected_tracks")

    def __repr__(self):
        return f"<FlightTrackCorrected(id={self.id}, batch_id='{self.batch_id}', method='{self.correction_method}')>"
