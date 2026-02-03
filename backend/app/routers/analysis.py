"""
AI 分析路由 - 处理轨迹分析和报告生成
"""
from typing import Annotated
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.orm import Session
from core.database import get_db
from app.routers.auth import get_current_active_user, UserResponse
from app.schemas.analysis import (
    TrajectoryAnalysisRequest,
    SegmentAnalysisRequest,
    AnalysisResult,
    AnalysisReport,
    LLMAnalysisRequest,
    LLMAnalysisResponse,
    AnalysisTaskResponse,
)
from app.services import analysis_service

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("/trajectory", response_model=AnalysisResult)
async def analyze_trajectory(
    request: TrajectoryAnalysisRequest,
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    整体轨迹分析

    - **track_id**: 轨迹编号
    - **start_time**: 开始时间（可选）
    - **end_time**: 结束时间（可选）
    - **analysis_type**: 分析类型
      - `comprehensive`: 综合分析
      - `behavior`: 行为分析
      - `anomaly`: 异常检测
      - `pattern`: 模式识别
    - **include_predictions**: 是否包含预测
    """
    result = analysis_service.analyze_trajectory(db, request)
    return result


@router.post("/segment", response_model=AnalysisResult)
async def analyze_segment(
    request: SegmentAnalysisRequest,
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    区间轨迹分析

    - **track_id**: 轨迹编号
    - **start_time**: 区间开始时间
    - **end_time**: 区间结束时间
    - **analysis_type**: 分析类型
      - `behavior`: 行为分析
      - `movement`: 运动分析
      - `characteristics`: 特征分析
    """
    result = analysis_service.analyze_segment(db, request)
    return result


@router.post("/llm", response_model=LLMAnalysisResponse)
async def llm_analysis(
    request: LLMAnalysisRequest,
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
):
    """
    调用大语言模型进行分析

    - **prompt**: 分析提示词
    - **context_data**: 上下文数据（可选）
    - **model**: 使用的模型
      - `deepseek`: DeepSeek 模型
      - `ollama`: Ollama 本地模型
    - **max_tokens**: 最大生成令牌数
    - **temperature**: 温度参数（0-2）
    """
    try:
        result = await analysis_service.call_llm_analysis(request)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/report/{track_id}", response_model=AnalysisReport)
async def generate_report(
    track_id: str,
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
    start_time: Annotated[datetime | None, None] = None,
    end_time: Annotated[datetime | None, None] = None,
):
    """
    生成综合分析报告

    包含多种分析类型的结果和总体评估
    """
    report = analysis_service.generate_analysis_report(db, track_id, start_time, end_time)
    return report


@router.get("/features/available")
async def list_available_features():
    """
    获取可提取的轨迹特征列表
    """
    return {
        "position_features": [
            "latitude_range",
            "longitude_range",
            "max_altitude",
            "altitude_variance",
        ],
        "velocity_features": [
            "avg_speed",
            "max_speed",
            "speed_variance",
        ],
        "movement_features": [
            "avg_heading_change",
            "tracking_confidence",
            "outlier_ratio",
        ],
        "temporal_features": [
            "duration_seconds",
            "avg_sampling_interval",
        ],
    }


@router.get("/result/{analysis_id}", response_model=AnalysisTaskResponse)
async def get_analysis_result(
    analysis_id: str,
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
):
    """
    获取分析结果
    """
    from datetime import datetime

    # 简化实现：返回模拟状态
    # 实际应该从分析服务或缓存获取结果
    return AnalysisTaskResponse(
        analysis_id=analysis_id,
        status="completed",
        progress=100.0,
        result=AnalysisResult(
            analysis_type="comprehensive",
            track_id="",
            analyzed_at=datetime.utcnow(),
            summary="分析完成",
            features=[],
            risk_level="low",
            recommendations=[],
        ),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@router.get("/tasks/{analysis_id}", response_model=AnalysisTaskResponse)
async def get_analysis_task_status(
    analysis_id: str,
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
):
    """
    查询分析任务状态
    """
    from datetime import datetime

    # 简化实现：返回模拟状态
    # 实际应该从任务队列（如 Celery）获取状态
    return AnalysisTaskResponse(
        analysis_id=analysis_id,
        status="completed",
        progress=100.0,
        message="分析完成",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
