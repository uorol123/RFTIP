"""
误差分析API模式定义
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator, model_validator
from enum import Enum


class ErrorAnalysisTaskStatus(str, Enum):
    """误差分析任务状态"""
    PENDING = "pending"
    EXTRACTING = "extracting"
    INTERPOLATING = "interpolating"
    MATCHING = "matching"
    CALCULATING = "calculating"
    COMPLETED = "completed"
    FAILED = "failed"


class CostWeights(BaseModel):
    """代价函数权重配置"""
    variance: float = Field(default=100.0, description="方差权重")
    azimuth_error_square: float = Field(default=0.15, description="方位角误差平方项权重（度^2）")
    range_error_square: float = Field(default=6e-7, description="距离误差平方项权重（米^2）")
    elevation_error_square: float = Field(default=0.1, description="俯仰角误差平方项权重（度^2）")


class ErrorAnalysisConfig(BaseModel):
    """误差分析配置参数"""
    grid_resolution: float = Field(default=0.2, ge=0.01, le=1.0, description="网格分辨率（度）")
    time_window: int = Field(default=60, ge=10, le=600, description="时间窗口长度（秒）")
    match_distance_threshold: float = Field(default=0.12, ge=0.01, le=1.0, description="匹配距离阈值（度）")
    min_track_points: int = Field(default=10, ge=3, le=100, description="最小航迹点数")
    optimization_steps: List[float] = Field(default=[0.1, 0.01], description="方位角优化步长序列")
    range_optimization_steps: List[float] = Field(
        default=[1000, 800, 500, 200, 100, 50, 20],
        description="距离优化步长序列（米）"
    )
    cost_weights: Optional[CostWeights] = Field(default=None, description="代价函数权重")
    max_match_groups: int = Field(default=15000, ge=1000, le=100000, description="最大匹配组数")

    @model_validator(mode='before')
    @classmethod
    def validate_cost_weights(cls, values):
        """允许 cost_weights 为 null"""
        if isinstance(values, dict) and values.get('cost_weights') is None:
            values['cost_weights'] = None
        return values

    @field_validator('optimization_steps')
    @classmethod
    def validate_optimization_steps(cls, v):
        if not v or len(v) == 0:
            return [0.1, 0.01]
        return v

    @field_validator('range_optimization_steps')
    @classmethod
    def validate_range_steps(cls, v):
        if not v or len(v) == 0:
            return [1000, 800, 500, 300, 200, 100, 50, 20, 10]
        return v


class ErrorAnalysisRequest(BaseModel):
    """创建误差分析请求"""
    radar_station_ids: List[int] = Field(..., min_length=1, description="雷达站ID列表")
    track_ids: List[str] = Field(..., min_length=1, description="轨迹编号列表（如 '100081'）")
    start_time: Optional[datetime] = Field(default=None, description="分析开始时间")
    end_time: Optional[datetime] = Field(default=None, description="分析结束时间")
    algorithm: str = Field(default="mrra", description="算法名称（如：mrra）")
    config: Optional[ErrorAnalysisConfig] = Field(default=None, description="分析配置参数")


class ErrorAnalysisTaskResponse(BaseModel):
    """误差分析任务响应"""
    id: int
    task_id: str
    radar_station_ids: List[str]  # 雷达站站号列表（用于显示）
    track_ids: List[str]  # 轨迹编号列表
    user_id: int
    algorithm_name: Optional[str] = None  # 算法名称
    status: ErrorAnalysisTaskStatus
    progress: int
    error_message: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TrackSegmentResponse(BaseModel):
    """航迹段响应"""
    id: int
    segment_id: int
    station_id: int
    track_id: int
    start_time: datetime
    end_time: datetime
    point_count: int
    start_point_index: Optional[int] = None
    end_point_index: Optional[int] = None

    class Config:
        from_attributes = True


class MatchPoint(BaseModel):
    """匹配点"""
    station_id: int
    point_id: Optional[int] = None
    longitude: float
    latitude: float
    altitude: Optional[float] = None


class MatchGroupResponse(BaseModel):
    """匹配组响应"""
    id: int
    group_id: int
    match_time: datetime
    match_points: List[MatchPoint]
    point_count: int
    avg_distance: Optional[float] = None
    max_distance: Optional[float] = None
    variance: Optional[float] = None

    class Config:
        from_attributes = True


class ErrorResultResponse(BaseModel):
    """误差结果响应"""
    id: int
    station_id: int
    azimuth_error: float
    range_error: float
    elevation_error: float
    match_count: int
    confidence: Optional[float] = None
    iterations: Optional[int] = None
    final_cost: Optional[float] = None

    class Config:
        from_attributes = True


class MatchStatistics(BaseModel):
    """匹配统计信息"""
    total_groups: int = Field(..., description="总匹配组数")
    group_size_avg: float = Field(..., description="平均组大小")
    group_size_std: float = Field(..., description="组大小标准差")
    distance_avg: float = Field(..., description="平均距离")
    distance_std: float = Field(..., description="距离标准差")
    min_group_size: int = Field(..., description="最小组大小")
    max_group_size: int = Field(..., description="最大组大小")


class ErrorAnalysisSummary(BaseModel):
    """误差分析摘要"""
    total_stations: int = Field(..., description="总雷达站数")
    total_matches: int = Field(..., description="总匹配数")
    processing_time: float = Field(..., description="处理时间（秒）")
    segments_extracted: int = Field(..., description="提取的航迹段数")


class ErrorAnalysisResult(BaseModel):
    """完整误差分析结果"""
    task_id: str
    status: ErrorAnalysisTaskStatus
    summary: ErrorAnalysisSummary
    errors: List[ErrorResultResponse]
    match_statistics: MatchStatistics
    config: ErrorAnalysisConfig


class ErrorChartResponse(BaseModel):
    """图表数据响应"""
    stations: List[str] = Field(..., description="雷达站名称列表")
    azimuth_errors: List[float] = Field(..., description="方位角误差列表")
    range_errors: List[float] = Field(..., description="距离误差列表")
    elevation_errors: List[float] = Field(..., description="俯仰角误差列表")
    confidences: List[float] = Field(..., description="置信度列表")
    match_counts: List[int] = Field(..., description="匹配点数列表")

    # 匹配组大小分布
    group_size_distribution: Dict[str, int] = Field(
        default_factory=dict,
        description="匹配组大小分布"
    )


class TaskListResponse(BaseModel):
    """任务列表响应"""
    tasks: List[ErrorAnalysisTaskResponse]
    total: int
    page: int
    limit: int


class ErrorResponse(BaseModel):
    """错误响应"""
    code: int
    message: str
    detail: Optional[str] = None


# ========== 历史任务详情相关 Schema ==========

class InterpolatedPointResponse(BaseModel):
    """插值点响应"""
    id: int
    station_id: int
    track_id: int
    time_seconds: float
    timestamp: Optional[datetime] = None
    longitude: float
    latitude: float
    altitude: Optional[float] = None
    is_original: bool = False

    class Config:
        from_attributes = True


class TrackSegmentDetail(BaseModel):
    """航迹段详情"""
    id: int
    segment_id: int
    station_id: int
    track_id: int
    start_time: datetime
    end_time: datetime
    point_count: int
    start_point_index: Optional[int] = None
    end_point_index: Optional[int] = None
    duration_seconds: float = 0.0
    station_name: str = ""

    class Config:
        from_attributes = True


class MatchGroupDetail(BaseModel):
    """匹配组详情"""
    id: int
    group_id: int
    match_time: datetime
    match_points: List[MatchPoint]
    point_count: int
    avg_distance: Optional[float] = None
    max_distance: Optional[float] = None
    variance: Optional[float] = None
    station_ids: List[int] = []
    time_difference_ms: float = 0.0

    class Config:
        from_attributes = True


class ErrorResultDetail(BaseModel):
    """误差结果详情"""
    id: int
    station_id: int
    station_name: str = ""
    azimuth_error: float = 0.0
    range_error: float = 0.0
    elevation_error: float = 0.0
    match_count: int = 0
    confidence: Optional[float] = None
    iterations: Optional[int] = None
    final_cost: Optional[float] = None
    azimuth_quality: str = "unknown"
    range_quality: str = "unknown"
    elevation_quality: str = "unknown"

    class Config:
        from_attributes = True


class InterpolationSummary(BaseModel):
    """插值汇总信息"""
    total_points: int = 0
    original_points: int = 0
    interpolated_points: int = 0
    stations: Dict[str, int] = {}

    class Config:
        from_attributes = True


class SmoothedTrajectoryPoint(BaseModel):
    """平滑轨迹点"""
    timestamp: Optional[datetime] = None
    longitude: float
    latitude: float
    altitude: Optional[float] = None
    covariance_trace: Optional[float] = None


class SmoothedTrajectoryResponse(BaseModel):
    """平滑轨迹结果响应"""
    id: int
    station_id: int
    station_name: str = ""
    batch_id: str
    original_trajectory: List[SmoothedTrajectoryPoint] = []
    smoothed_trajectory: List[SmoothedTrajectoryPoint] = []
    rmse_lat: Optional[float] = None
    rmse_lon: Optional[float] = None
    rmse_alt: Optional[float] = None
    point_count: int = 0
    process_noise: Optional[float] = None
    measurement_noise: Optional[float] = None

    class Config:
        from_attributes = True


class ProcessStepInfo(BaseModel):
    """流程步骤信息"""
    step_id: str
    step_name: str
    step_description: str
    status: str
    duration_seconds: Optional[float] = None
    data_summary: Dict[str, Any] = {}

    class Config:
        from_attributes = True


class TaskDetailResponse(BaseModel):
    """完整任务详情响应"""
    # 基本信息
    task_id: str
    status: ErrorAnalysisTaskStatus
    progress: int
    error_message: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # 算法名称
    algorithm_name: Optional[str] = None

    # 配置参数
    config: ErrorAnalysisConfig
    radar_station_ids: List[int] = []
    track_ids: List[str] = []

    # 流程步骤信息
    process_steps: List[ProcessStepInfo] = []

    # 各步骤数据概要
    segments_summary: Dict[str, Any] = {}
    interpolation_summary: Optional[InterpolationSummary] = None
    match_summary: Dict[str, Any] = {}

    # 详细数据
    segments: List[TrackSegmentDetail] = []
    interpolated_points: List[InterpolatedPointResponse] = []
    match_groups: List[MatchGroupDetail] = []
    error_results: List[ErrorResultDetail] = []
    smoothed_trajectories: List[SmoothedTrajectoryResponse] = []

    # 统计信息
    processing_time_seconds: float = 0.0
    total_segments: int = 0
    total_match_groups: int = 0
    total_interpolated_points: int = 0

    class Config:
        from_attributes = True


# 导出所有模式
__all__ = [
    "ErrorAnalysisTaskStatus",
    "CostWeights",
    "ErrorAnalysisConfig",
    "ErrorAnalysisRequest",
    "ErrorAnalysisTaskResponse",
    "TrackSegmentResponse",
    "MatchPoint",
    "MatchGroupResponse",
    "ErrorResultResponse",
    "MatchStatistics",
    "ErrorAnalysisSummary",
    "ErrorAnalysisResult",
    "ErrorChartResponse",
    "TaskListResponse",
    "ErrorResponse",
    # 历史任务详情
    "InterpolatedPointResponse",
    "TrackSegmentDetail",
    "MatchGroupDetail",
    "ErrorResultDetail",
    "InterpolationSummary",
    "SmoothedTrajectoryPoint",
    "SmoothedTrajectoryResponse",
    "ProcessStepInfo",
    "TaskDetailResponse",
]
