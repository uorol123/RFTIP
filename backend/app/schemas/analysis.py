"""
AI 分析相关的 Pydantic 模型
"""
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field


class TrajectoryAnalysisRequest(BaseModel):
    """整体轨迹分析请求模型"""
    track_id: str = Field(..., description="轨迹编号")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    analysis_type: str = Field("comprehensive", description="分析类型 (comprehensive/behavior/anomaly/pattern)")
    include_predictions: bool = Field(False, description="是否包含预测")


class SegmentAnalysisRequest(BaseModel):
    """区间轨迹分析请求模型"""
    track_id: str = Field(..., description="轨迹编号")
    start_time: datetime = Field(..., description="区间开始时间")
    end_time: datetime = Field(..., description="区间结束时间")
    analysis_type: str = Field("behavior", description="分析类型 (behavior/movement/characteristics)")


class TrajectoryFeature(BaseModel):
    """轨迹特征模型"""
    feature_name: str = Field(..., description="特征名称")
    feature_value: float = Field(..., description="特征值")
    confidence: float = Field(..., ge=0, le=1, description="置信度")
    description: Optional[str] = Field(None, description="特征描述")


class AnalysisResult(BaseModel):
    """分析结果模型"""
    analysis_type: str = Field(..., description="分析类型")
    track_id: str = Field(..., description="轨迹编号")
    analyzed_at: datetime = Field(default_factory=datetime.utcnow, description="分析时间")
    summary: str = Field(..., description="分析摘要")
    features: list[TrajectoryFeature] = Field(default_factory=list, description="提取的特征")
    risk_level: str = Field(..., description="风险等级 (low/medium/high)")
    recommendations: list[str] = Field(default_factory=list, description="建议列表")
    metadata: dict = Field(default_factory=dict, description="额外元数据")


class AnalysisReport(BaseModel):
    """分析报告模型"""
    report_id: str = Field(..., description="报告ID")
    track_id: str = Field(..., description="轨迹编号")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="生成时间")
    analysis_results: list[AnalysisResult] = Field(default_factory=list, description="分析结果列表")
    overall_assessment: str = Field(..., description="总体评估")
    risk_score: float = Field(..., ge=0, le=1, description="风险分数")


class LLMAnalysisRequest(BaseModel):
    """大模型分析请求模型"""
    prompt: str = Field(..., description="分析提示词")
    context_data: Optional[dict] = Field(None, description="上下文数据")
    model: str = Field("deepseek", description="使用的模型 (deepseek/ollama)")
    max_tokens: Optional[int] = Field(1000, ge=1, le=4000, description="最大生成令牌数")
    temperature: float = Field(0.7, ge=0, le=2, description="温度参数")


class LLMAnalysisResponse(BaseModel):
    """大模型分析响应模型"""
    response: str = Field(..., description="模型响应")
    model_used: str = Field(..., description="使用的模型")
    tokens_used: int = Field(..., description="使用的令牌数")
    processing_time: float = Field(..., description="处理时间（秒）")


class AnalysisTaskResponse(BaseModel):
    """分析任务响应模型"""
    analysis_id: str
    status: str = Field(..., description="任务状态: pending/processing/completed/failed")
    progress: float = Field(0.0, ge=0, le=100, description="任务进度（百分比）")
    result: Optional[AnalysisResult] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime
