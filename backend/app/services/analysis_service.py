"""
AI 分析服务 - 处理轨迹特征提取、大模型调用和报告生成
"""
import json
import time
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import numpy as np
from sqlalchemy.orm import Session

from app.models.flight_track import FlightTrackCorrected
from app.schemas.analysis import (
    TrajectoryAnalysisRequest,
    SegmentAnalysisRequest,
    TrajectoryFeature,
    AnalysisResult,
    AnalysisReport,
    LLMAnalysisRequest,
    LLMAnalysisResponse,
)


class TrajectoryFeatureExtractor:
    """轨迹特征提取器"""

    @staticmethod
    def extract_position_features(tracks: List[FlightTrackCorrected]) -> List[TrajectoryFeature]:
        """提取位置特征"""
        features = []

        if not tracks:
            return features

        lats = [t.latitude for t in tracks]
        lngs = [t.longitude for t in tracks]
        alts = [t.altitude or 0 for t in tracks]

        # 经纬度范围
        features.append(TrajectoryFeature(
            feature_name="latitude_range",
            feature_value=float(max(lats) - min(lats)),
            confidence=1.0,
            description="纬度变化范围"
        ))

        features.append(TrajectoryFeature(
            feature_name="longitude_range",
            feature_value=float(max(lngs) - min(lngs)),
            confidence=1.0,
            description="经度变化范围"
        ))

        # 高度特征
        if alts:
            features.append(TrajectoryFeature(
                feature_name="max_altitude",
                feature_value=float(max(alts)),
                confidence=1.0,
                description="最大高度"
            ))

            features.append(TrajectoryFeature(
                feature_name="altitude_variance",
                feature_value=float(np.var(alts)),
                confidence=1.0,
                description="高度方差"
            ))

        return features

    @staticmethod
    def extract_velocity_features(tracks: List[FlightTrackCorrected]) -> List[TrajectoryFeature]:
        """
        提取速度特征

        注意：由于原始数据中的 speed/heading 字段存在问题，
        这里从位置数据计算实际速度
        """
        import math

        features = []

        if len(tracks) < 2:
            return features

        # 从位置变化计算速度
        calculated_speeds = []
        for i in range(len(tracks) - 1):
            curr = tracks[i]
            next_track = tracks[i + 1]

            # 计算距离（米）- 使用 Haversine 公式
            lat1, lon1 = math.radians(curr.latitude), math.radians(curr.longitude)
            lat2, lon2 = math.radians(next_track.latitude), math.radians(next_track.longitude)

            dlat = lat2 - lat1
            dlon = lon2 - lon1

            a = (math.sin(dlat / 2) ** 2 +
                 math.cos(lat1) * math.cos(lat2) *
                 math.sin(dlon / 2) ** 2)

            c = 2 * math.asin(math.sqrt(a))
            distance = 6371000 * c  # 地球半径 6371km

            # 计算时间差（秒）
            time_diff = (next_track.timestamp - curr.timestamp).total_seconds()

            if time_diff > 0:
                speed = distance / time_diff  # 米/秒
                calculated_speeds.append(speed)

        if not calculated_speeds:
            return features

        features.append(TrajectoryFeature(
            feature_name="avg_speed",
            feature_value=float(np.mean(calculated_speeds)),
            confidence=1.0,
            description="平均速度（米/秒，从位置计算）"
        ))

        features.append(TrajectoryFeature(
            feature_name="max_speed",
            feature_value=float(max(calculated_speeds)),
            confidence=1.0,
            description="最大速度（米/秒，从位置计算）"
        ))

        features.append(TrajectoryFeature(
            feature_name="speed_variance",
            feature_value=float(np.var(calculated_speeds)),
            confidence=1.0,
            description="速度方差（从位置计算）"
        ))

        return features

    @staticmethod
    def extract_movement_features(tracks: List[FlightTrackCorrected]) -> List[TrajectoryFeature]:
        """
        提取运动特征

        注意：由于原始数据中的 heading 字段存在问题，
        这里从位置数据计算实际航向
        """
        import math

        features = []

        if len(tracks) < 2:
            return features

        # 从位置变化计算航向
        calculated_headings = []

        for i in range(len(tracks) - 1):
            curr = tracks[i]
            next_track = tracks[i + 1]

            # 计算方位角（航向）
            lat1 = math.radians(curr.latitude)
            lat2 = math.radians(next_track.latitude)
            dlon = math.radians(next_track.longitude - curr.longitude)

            y = math.sin(dlon) * math.cos(lat2)
            x = (math.cos(lat1) * math.sin(lat2) -
                 math.sin(lat1) * math.cos(lat2) * math.cos(dlon))

            bearing = math.atan2(y, x)
            bearing = math.degrees(bearing)
            bearing = (bearing + 360) % 360

            calculated_headings.append(bearing)

        if len(calculated_headings) > 1:
            # 计算航向变化
            heading_changes = [
                abs(calculated_headings[i + 1] - calculated_headings[i])
                for i in range(len(calculated_headings) - 1)
            ]
            # 处理跨越0/360度的情况
            heading_changes = [
                h if h <= 180 else 360 - h
                for h in heading_changes
            ]

            avg_heading_change = np.mean(heading_changes)

            features.append(TrajectoryFeature(
                feature_name="avg_heading_change",
                feature_value=float(avg_heading_change),
                confidence=1.0,
                description="平均航向变化（度，从位置计算）"
            ))

        # 计算运动模式
        avg_confidence = np.mean([t.confidence_score or 0.5 for t in tracks])
        features.append(TrajectoryFeature(
            feature_name="tracking_confidence",
            feature_value=float(avg_confidence),
            confidence=1.0,
            description="轨迹追踪置信度"
        ))

        # 离群值比例
        outlier_ratio = np.mean([t.is_outlier for t in tracks])
        features.append(TrajectoryFeature(
            feature_name="outlier_ratio",
            feature_value=float(outlier_ratio),
            confidence=1.0,
            description="离群值比例"
        ))

        return features

    @staticmethod
    def extract_temporal_features(tracks: List[FlightTrackCorrected]) -> List[TrajectoryFeature]:
        """提取时间特征"""
        features = []

        if len(tracks) < 2:
            return features

        # 计算持续时间
        duration = (tracks[-1].timestamp - tracks[0].timestamp).total_seconds()
        features.append(TrajectoryFeature(
            feature_name="duration_seconds",
            feature_value=float(duration),
            confidence=1.0,
            description="轨迹持续时间（秒）"
        ))

        # 计算平均采样间隔
        intervals = [
            (tracks[i + 1].timestamp - tracks[i].timestamp).total_seconds()
            for i in range(len(tracks) - 1)
        ]
        if intervals:
            features.append(TrajectoryFeature(
                feature_name="avg_sampling_interval",
                feature_value=float(np.mean(intervals)),
                confidence=1.0,
                description="平均采样间隔（秒）"
            ))

        return features


def analyze_trajectory(
    db: Session,
    request: TrajectoryAnalysisRequest,
) -> AnalysisResult:
    """分析整体轨迹"""
    # 获取轨迹数据
    query = db.query(FlightTrackCorrected).filter(
        FlightTrackCorrected.track_id == request.track_id
    )

    if request.start_time:
        query = query.filter(FlightTrackCorrected.timestamp >= request.start_time)
    if request.end_time:
        query = query.filter(FlightTrackCorrected.timestamp <= request.end_time)

    tracks = query.order_by(FlightTrackCorrected.timestamp).all()

    if not tracks:
        return AnalysisResult(
            analysis_type=request.analysis_type,
            track_id=request.track_id,
            analyzed_at=datetime.utcnow(),
            summary="未找到轨迹数据",
            features=[],
            risk_level="unknown",
            recommendations=["无法分析：没有可用的轨迹数据"],
            metadata={}
        )

    # 提取特征
    extractor = TrajectoryFeatureExtractor()
    features = []

    if request.analysis_type in ["comprehensive", "behavior"]:
        features.extend(extractor.extract_position_features(tracks))
        features.extend(extractor.extract_velocity_features(tracks))
        features.extend(extractor.extract_movement_features(tracks))

    if request.analysis_type in ["comprehensive", "pattern"]:
        features.extend(extractor.extract_temporal_features(tracks))

    # 评估风险等级
    risk_level = assess_risk_level(tracks, features)

    # 生成建议
    recommendations = generate_recommendations(tracks, features, risk_level)

    # 生成摘要
    summary = generate_analysis_summary(tracks, features, risk_level)

    return AnalysisResult(
        analysis_type=request.analysis_type,
        track_id=request.track_id,
        analyzed_at=datetime.utcnow(),
        summary=summary,
        features=features,
        risk_level=risk_level,
        recommendations=recommendations,
        metadata={
            "track_count": len(tracks),
            "time_span": f"{(tracks[-1].timestamp - tracks[0].timestamp).total_seconds():.1f}s" if tracks else "0s"
        }
    )


def analyze_segment(
    db: Session,
    request: SegmentAnalysisRequest,
) -> AnalysisResult:
    """分析区间轨迹"""
    query = db.query(FlightTrackCorrected).filter(
        FlightTrackCorrected.track_id == request.track_id,
        FlightTrackCorrected.timestamp >= request.start_time,
        FlightTrackCorrected.timestamp <= request.end_time,
    )

    tracks = query.order_by(FlightTrackCorrected.timestamp).all()

    if not tracks:
        return AnalysisResult(
            analysis_type=request.analysis_type,
            track_id=request.track_id,
            analyzed_at=datetime.utcnow(),
            summary="指定时间区间内未找到轨迹数据",
            features=[],
            risk_level="unknown",
            recommendations=["无法分析：指定区间内没有可用的轨迹数据"],
            metadata={}
        )

    # 提取区间特征
    extractor = TrajectoryFeatureExtractor()
    features = []

    if request.analysis_type == "behavior":
        features.extend(extractor.extract_velocity_features(tracks))
        features.extend(extractor.extract_movement_features(tracks))
    elif request.analysis_type == "movement":
        features.extend(extractor.extract_position_features(tracks))
    else:  # characteristics
        features.extend(extractor.extract_temporal_features(tracks))

    # 评估风险
    risk_level = assess_risk_level(tracks, features)

    # 生成摘要和建议
    summary = f"区间 {request.start_time} 至 {request.end_time} 的轨迹分析完成"
    recommendations = generate_recommendations(tracks, features, risk_level)

    return AnalysisResult(
        analysis_type=request.analysis_type,
        track_id=request.track_id,
        analyzed_at=datetime.utcnow(),
        summary=summary,
        features=features,
        risk_level=risk_level,
        recommendations=recommendations,
        metadata={
            "segment_start": request.start_time.isoformat(),
            "segment_end": request.end_time.isoformat(),
            "track_count": len(tracks)
        }
    )


def assess_risk_level(tracks: List[FlightTrackCorrected], features: List[TrajectoryFeature]) -> str:
    """评估风险等级"""
    # 基于特征评估风险
    risk_score = 0

    # 检查离群值比例
    outlier_feature = next((f for f in features if f.feature_name == "outlier_ratio"), None)
    if outlier_feature and outlier_feature.feature_value > 0.3:
        risk_score += 2

    # 检查速度异常 (阈值调整为更合理的值: 飞机速度方差 > 2500 m/s²)
    speed_variance = next((f for f in features if f.feature_name == "speed_variance"), None)
    if speed_variance and speed_variance.feature_value > 2500:
        risk_score += 1

    # 检查高度变化
    altitude_variance = next((f for f in features if f.feature_name == "altitude_variance"), None)
    if altitude_variance and altitude_variance.feature_value > 10000:
        risk_score += 1

    # 检查航向变化
    heading_change = next((f for f in features if f.feature_name == "avg_heading_change"), None)
    if heading_change and heading_change.feature_value > 90:
        risk_score += 1

    if risk_score >= 3:
        return "high"
    elif risk_score >= 1:
        return "medium"
    else:
        return "low"


def generate_recommendations(
    tracks: List[FlightTrackCorrected],
    features: List[TrajectoryFeature],
    risk_level: str
) -> List[str]:
    """生成建议"""
    recommendations = []

    if risk_level == "high":
        recommendations.append("检测到高风险行为，建议进一步调查该轨迹")

    # 检查追踪质量
    confidence = next((f for f in features if f.feature_name == "tracking_confidence"), None)
    if confidence and confidence.feature_value < 0.6:
        recommendations.append("轨迹追踪置信度较低，建议检查雷达数据质量")

    # 检查离群值
    outlier_ratio = next((f for f in features if f.feature_name == "outlier_ratio"), None)
    if outlier_ratio and outlier_ratio.feature_value > 0.2:
        recommendations.append("检测到较多离群值，建议检查雷达校准状态")

    if not recommendations:
        recommendations.append("轨迹分析未发现明显异常")

    return recommendations


def generate_analysis_summary(
    tracks: List[FlightTrackCorrected],
    features: List[TrajectoryFeature],
    risk_level: str
) -> str:
    """生成分析摘要"""
    summary_parts = [
        f"分析了 {len(tracks)} 个轨迹点",
        f"风险等级: {risk_level}",
    ]

    if features:
        summary_parts.append(f"提取了 {len(features)} 个特征")

    return "; ".join(summary_parts)


async def call_llm_analysis(request: LLMAnalysisRequest) -> LLMAnalysisResponse:
    """
    调用大模型进行分析

    支持 DeepSeek 和 Ollama 模型
    """
    start_time = time.time()

    # 模拟 LLM 调用（实际使用时需要连接真实 API）
    if request.model == "deepseek":
        response_text = await _call_deepseek(request.prompt, request.context_data)
    elif request.model == "ollama":
        response_text = await _call_ollama(request.prompt, request.context_data)
    else:
        raise ValueError(f"不支持的模型: {request.model}")

    processing_time = time.time() - start_time

    return LLMAnalysisResponse(
        response=response_text,
        model_used=request.model,
        tokens_used=len(response_text.split()),
        processing_time=processing_time,
    )


async def _call_deepseek(prompt: str, context: Optional[dict]) -> str:
    """调用 DeepSeek API"""
    # TODO: 实际实现需要调用 DeepSeek API
    # 这里返回模拟响应
    return f"DeepSeek 分析结果: {prompt}\n上下文: {json.dumps(context, ensure_ascii=False) if context else '无'}"


async def _call_ollama(prompt: str, context: Optional[dict]) -> str:
    """调用 Ollama 本地模型"""
    # TODO: 实际实现需要调用 Ollama API
    # 这里返回模拟响应
    return f"Ollama 分析结果: {prompt}\n上下文: {json.dumps(context, ensure_ascii=False) if context else '无'}"


def generate_analysis_report(
    db: Session,
    track_id: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
) -> AnalysisReport:
    """生成综合分析报告"""
    # 执行多种分析
    comprehensive_request = TrajectoryAnalysisRequest(
        track_id=track_id,
        start_time=start_time,
        end_time=end_time,
        analysis_type="comprehensive",
    )

    behavior_request = TrajectoryAnalysisRequest(
        track_id=track_id,
        start_time=start_time,
        end_time=end_time,
        analysis_type="behavior",
    )

    anomaly_request = TrajectoryAnalysisRequest(
        track_id=track_id,
        start_time=start_time,
        end_time=end_time,
        analysis_type="anomaly",
    )

    results = [
        analyze_trajectory(db, comprehensive_request),
        analyze_trajectory(db, behavior_request),
        analyze_trajectory(db, anomaly_request),
    ]

    # 计算总体风险分数
    high_risk_count = sum(1 for r in results if r.risk_level == "high")
    medium_risk_count = sum(1 for r in results if r.risk_level == "medium")
    risk_score = (high_risk_count * 0.6 + medium_risk_count * 0.3) / len(results)

    # 生成总体评估
    overall_assessment = generate_overall_assessment(results, risk_score)

    return AnalysisReport(
        report_id=f"report_{track_id}_{int(datetime.utcnow().timestamp())}",
        track_id=track_id,
        generated_at=datetime.utcnow(),
        analysis_results=results,
        overall_assessment=overall_assessment,
        risk_score=risk_score,
    )


def generate_overall_assessment(results: List[AnalysisResult], risk_score: float) -> str:
    """生成总体评估"""
    if risk_score > 0.6:
        return "该轨迹存在高风险行为，建议重点关注和进一步调查"
    elif risk_score > 0.3:
        return "该轨迹存在一些异常情况，建议持续关注"
    else:
        return "该轨迹未发现明显异常，属于正常飞行轨迹"
