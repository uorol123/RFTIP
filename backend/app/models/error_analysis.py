"""
误差分析数据模型
算法：基于梯度下降的迭代寻优算法
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, Enum as SQLEnum, ForeignKey, Index, Text
from sqlalchemy.orm import relationship
from enum import Enum
import json

from core.database import Base


class ErrorAnalysisTaskStatus(str, Enum):
    """误差分析任务状态"""
    PENDING = "pending"
    EXTRACTING = "extracting"
    INTERPOLATING = "interpolating"
    MATCHING = "matching"
    CALCULATING = "calculating"
    COMPLETED = "completed"
    FAILED = "failed"


class ErrorAnalysisTask(Base):
    """误差分析任务表"""
    __tablename__ = "error_analysis_tasks"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    task_id = Column(String(36), unique=True, nullable=False, index=True, comment="任务UUID")
    radar_station_ids = Column(JSON, nullable=False, comment="雷达站ID列表")
    track_ids = Column(JSON, nullable=False, comment="轨迹ID列表")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="创建用户ID")

    # 算法名称 (支持多算法扩展)
    algorithm_name = Column(String(50), nullable=True, default="gradient_descent", comment="算法名称")

    # 配置参数 (JSON格式存储)
    config = Column(JSON, nullable=True, comment="分析配置参数")

    # 状态信息
    status = Column(
        SQLEnum(ErrorAnalysisTaskStatus),
        default=ErrorAnalysisTaskStatus.PENDING,
        nullable=False,
        index=True,
        comment="任务状态"
    )
    progress = Column(Integer, default=0, comment="进度百分比")
    error_message = Column(Text, nullable=True, comment="错误信息")
    result_metadata = Column(JSON, nullable=True, comment="分析结果元数据（融合轨迹等）")

    # 时间信息
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    started_at = Column(DateTime, nullable=True, comment="开始时间")
    completed_at = Column(DateTime, nullable=True, comment="完成时间")

    # 关系
    user = relationship("User", back_populates="error_analysis_tasks")
    track_segments = relationship("TrackSegment", back_populates="task", cascade="all, delete-orphan")
    match_groups = relationship("MatchGroup", back_populates="task", cascade="all, delete-orphan")
    error_results = relationship("ErrorResult", back_populates="task", cascade="all, delete-orphan")

    def set_config(self, config_dict: dict):
        """设置配置参数"""
        self.config = config_dict

    def get_config(self) -> dict:
        """获取配置参数"""
        return self.config or {}

    __table_args__ = (
        Index("idx_user_id", "user_id"),
        Index("idx_status", "status"),
        {"comment": "误差分析任务表"}
    )


class TrackSegment(Base):
    """航迹段表"""
    __tablename__ = "track_segments"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    task_id = Column(String(36), ForeignKey("error_analysis_tasks.task_id"), nullable=False, comment="关联任务ID")
    segment_id = Column(Integer, nullable=False, comment="段号")

    # 航迹信息
    station_id = Column(Integer, nullable=False, comment="雷达站号")
    track_id = Column(String(50), nullable=False, comment="航迹批号")
    start_time = Column(DateTime, nullable=False, comment="开始时间")
    end_time = Column(DateTime, nullable=False, comment="结束时间")
    point_count = Column(Integer, nullable=False, comment="点数")

    # 关键点索引
    start_point_index = Column(Integer, nullable=True, comment="起始点索引")
    end_point_index = Column(Integer, nullable=True, comment="结束点索引")

    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    # 关系
    task = relationship("ErrorAnalysisTask", back_populates="track_segments")

    __table_args__ = (
        Index("idx_task_id", "task_id"),
        Index("idx_station_track", "station_id", "track_id"),
        {"comment": "航迹段表"}
    )


class MatchGroup(Base):
    """匹配组表"""
    __tablename__ = "match_groups"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    task_id = Column(String(36), ForeignKey("error_analysis_tasks.task_id"), nullable=False, comment="关联任务ID")
    group_id = Column(Integer, nullable=False, comment="匹配组号")

    # 匹配点信息
    match_time = Column(DateTime, nullable=False, index=True, comment="匹配时间")
    match_points = Column(JSON, nullable=False, comment="匹配点列表")
    point_count = Column(Integer, nullable=False, comment="匹配点数量")

    # 质量指标
    avg_distance = Column(Float, nullable=True, comment="平均距离")
    max_distance = Column(Float, nullable=True, comment="最大距离")
    variance = Column(Float, nullable=True, comment="距离方差")

    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    # 关系
    task = relationship("ErrorAnalysisTask", back_populates="match_groups")

    __table_args__ = (
        Index("idx_match_time", "match_time"),
        {"comment": "匹配组表"}
    )


class ErrorResult(Base):
    """误差结果表"""
    __tablename__ = "error_results"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    task_id = Column(String(36), ForeignKey("error_analysis_tasks.task_id"), nullable=False, comment="关联任务ID")

    # 雷达站信息
    station_id = Column(Integer, nullable=False, comment="雷达站号")

    # 误差值
    azimuth_error = Column(Float, default=0, comment="方位角误差(度)")
    range_error = Column(Float, default=0, comment="距离误差(米)")
    elevation_error = Column(Float, default=0, comment="俯仰角误差(度)")

    # 统计信息
    match_count = Column(Integer, default=0, comment="匹配点数量")
    confidence = Column(Float, nullable=True, comment="置信度")

    # 优化信息
    iterations = Column(Integer, nullable=True, comment="优化迭代次数")
    final_cost = Column(Float, nullable=True, comment="最终代价函数值")

    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    # 关系
    task = relationship("ErrorAnalysisTask", back_populates="error_results")

    __table_args__ = (
        Index("uk_task_station", "task_id", "station_id", unique=True),
        Index("idx_task_id", "task_id"),
        {"comment": "误差结果表"}
    )


class TrackInterpolatedPoint(Base):
    """插值点表"""
    __tablename__ = "track_interpolated_points"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    task_id = Column(String(36), ForeignKey("error_analysis_tasks.task_id"), nullable=False, comment="关联任务ID")
    segment_id = Column(Integer, nullable=True, comment="航迹段ID")

    # 航迹点信息
    station_id = Column(Integer, nullable=False, comment="雷达站号")
    track_id = Column(String(50), nullable=False, comment="航迹批号")
    time_seconds = Column(Float, nullable=False, comment="时间（秒）")
    timestamp = Column(DateTime, nullable=True, comment="时间戳")

    # 位置信息
    longitude = Column(Float, nullable=False, comment="经度")
    latitude = Column(Float, nullable=False, comment="纬度")
    altitude = Column(Float, nullable=True, comment="高度")

    # 标记
    is_original = Column(Integer, default=0, comment="是否为原始点: 1=是, 0=否")

    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    __table_args__ = (
        Index("idx_task_id", "task_id"),
        Index("idx_station_track", "station_id", "track_id"),
        Index("idx_time", "time_seconds"),
        {"comment": "插值点表"}
    )
