"""
测试配置和共享 fixtures
"""
import pytest
from unittest.mock import Mock
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.error_analysis import ErrorAnalysisTask, ErrorAnalysisTaskStatus
from app.schemas.error_analysis import ErrorAnalysisRequest, ErrorAnalysisConfig


@pytest.fixture
def db_session():
    """模拟数据库会话"""
    session = Mock(spec=Session)
    session.add = Mock()
    session.commit = Mock()
    session.refresh = Mock()
    session.query = Mock()
    session.rollback = Mock()
    return session


@pytest.fixture
def sample_error_analysis_config():
    """样本误差分析配置"""
    return ErrorAnalysisConfig(
        grid_resolution=0.2,
        time_window=60,
        match_distance_threshold=0.12,
        min_track_points=10,
        optimization_steps=[0.1, 0.01],
        range_optimization_steps=[1000, 800, 500, 200, 100, 50, 20],
        max_match_groups=15000,
    )


@pytest.fixture
def sample_error_analysis_request(sample_error_analysis_config):
    """样本误差分析请求"""
    return ErrorAnalysisRequest(
        radar_station_ids=[1, 2, 3],
        track_ids=["T001", "T002"],
        algorithm="gradient_descent",
        config=sample_error_analysis_config
    )


@pytest.fixture
def sample_error_analysis_task(sample_error_analysis_request):
    """样本误差分析任务"""
    return ErrorAnalysisTask(
        id=1,
        task_id="test-task-123",
        radar_station_ids=sample_error_analysis_request.radar_station_ids,
        track_ids=sample_error_analysis_request.track_ids,
        user_id=1,
        algorithm_name=sample_error_analysis_request.algorithm,
        config=sample_error_analysis_request.config.model_dump(),
        status=ErrorAnalysisTaskStatus.PENDING,
        progress=0,
        created_at=datetime.utcnow(),
    )


@pytest.fixture
def mock_radar_stations():
    """模拟雷达站数据"""
    return [
        Mock(id=1, station_id="STATION_1", longitude=116.0, latitude=39.0, altitude=100.0),
        Mock(id=2, station_id="STATION_2", longitude=116.5, latitude=39.5, altitude=120.0),
        Mock(id=3, station_id="STATION_3", longitude=117.0, latitude=40.0, altitude=110.0),
    ]


@pytest.fixture
def algorithm_info():
    """算法信息 fixture"""
    return {
        "name": "gradient_descent",
        "version": "1.0.0",
        "display_name": "基于梯度下降的迭代寻优算法",
        "description": "通过航迹匹配和梯度下降优化计算雷达误差",
        "supports_elevation": True,
    }


@pytest.fixture
def config_schema():
    """配置 Schema fixture"""
    return {
        "type": "object",
        "properties": {
            "grid_resolution": {
                "type": "number",
                "title": "网格分辨率",
                "default": 0.2,
                "minimum": 0.01,
                "maximum": 1.0,
            },
            "time_window": {
                "type": "number",
                "title": "时间窗口",
                "default": 60,
                "minimum": 10,
                "maximum": 600,
            },
        },
        "required": ["grid_resolution", "time_window"],
    }


@pytest.fixture
def preset_configs():
    """预设配置 fixture"""
    return [
        {
            "name": "standard",
            "display_name": "标准配置",
            "config": {
                "grid_resolution": 0.2,
                "time_window": 60,
                "match_distance_threshold": 0.12,
            },
        },
        {
            "name": "high_precision",
            "display_name": "高精度配置",
            "config": {
                "grid_resolution": 0.1,
                "time_window": 30,
                "match_distance_threshold": 0.08,
            },
        },
    ]
