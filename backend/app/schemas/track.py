"""
轨迹相关的 Pydantic 模型
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class RadarStationBase(BaseModel):
    """雷达站基础模型"""
    station_code: str = Field(..., max_length=20, description="雷达站编号")
    station_name: str = Field(..., max_length=100, description="雷达站名称")
    latitude: float = Field(..., ge=-90, le=90, description="纬度")
    longitude: float = Field(..., ge=-180, le=180, description="经度")
    altitude: float = Field(0, ge=0, description="海拔高度（米）")
    max_range: Optional[float] = Field(None, ge=0, description="最大探测距离（千米）")
    frequency: Optional[str] = Field(None, max_length=50, description="工作频率")


class RadarStationCreate(RadarStationBase):
    """雷达站创建模型"""
    pass


class RadarStationResponse(RadarStationBase):
    """雷达站响应模型"""
    id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class TrackPointBase(BaseModel):
    """轨迹点基础模型"""
    track_id: str = Field(..., max_length=50, description="轨迹编号")
    timestamp: datetime = Field(..., description="时间戳")
    latitude: float = Field(..., ge=-90, le=90, description="纬度")
    longitude: float = Field(..., ge=-180, le=180, description="经度")
    altitude: Optional[float] = Field(None, description="高度（米）")
    speed: Optional[float] = Field(None, ge=0, description="速度（米/秒）")
    heading: Optional[float] = Field(None, ge=0, lt=360, description="航向（度）")


class RawTrackPoint(TrackPointBase):
    """原始轨迹点模型"""
    radar_station_id: Optional[int] = Field(None, description="雷达站ID")
    target_id: Optional[str] = Field(None, max_length=50, description="目标编号")
    radar_cross_section: Optional[float] = Field(None, description="雷达截面积")
    signal_quality: Optional[float] = Field(None, ge=0, le=1, description="信号质量")
    raw_data: Optional[str] = Field(None, description="原始数据（JSON）")


class RawTrackResponse(TrackPointBase):
    """原始轨迹响应模型"""
    id: int
    file_id: int
    radar_station_id: Optional[int] = None
    target_id: Optional[str] = None
    radar_cross_section: Optional[float] = None
    signal_quality: Optional[float] = None
    raw_data: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CorrectedTrackPoint(TrackPointBase):
    """修正轨迹点模型"""
    correction_method: str = Field(..., description="修正方法")
    confidence_score: Optional[float] = Field(None, ge=0, le=1, description="置信度分数")
    is_outlier: bool = Field(False, description="是否为离群值")


class CorrectedTrackResponse(TrackPointBase):
    """修正轨迹响应模型"""
    id: int
    raw_track_id: int
    correction_method: str
    confidence_score: Optional[float] = None
    is_outlier: bool
    correction_metadata: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TrackProcessRequest(BaseModel):
    """轨迹处理请求模型"""
    file_id: int = Field(..., description="数据文件ID")
    mode: str = Field(..., description="处理模式 (multi_source/single_source)")
    ransac_threshold: Optional[float] = Field(0.5, ge=0, le=1, description="RANSAC阈值")
    kalman_process_noise: Optional[float] = Field(0.1, ge=0, description="卡尔曼滤波过程噪声")
    kalman_measurement_noise: Optional[float] = Field(1.0, ge=0, description="卡尔曼滤波测量噪声")


class TrackProcessResponse(BaseModel):
    """轨迹处理响应模型"""
    task_id: str
    status: str
    message: str
    total_points: int
    corrected_points: int
    outliers_detected: int


class TrackQueryParams(BaseModel):
    """轨迹查询参数模型"""
    track_id: Optional[str] = Field(None, description="轨迹编号")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    radar_station_id: Optional[int] = Field(None, description="雷达站ID")
    limit: int = Field(100, ge=1, le=10000, description="返回数量限制")
    offset: int = Field(0, ge=0, description="偏移量")
