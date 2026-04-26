"""
测试误差分析任务模型的 algorithm_name 字段
"""
import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import ProgrammingError

from app.models.error_analysis import ErrorAnalysisTask, ErrorAnalysisTaskStatus
from core.database import Base


class TestErrorAnalysisTaskAlgorithmField:
    """测试 ErrorAnalysisTask 的 algorithm_name 字段"""

    def test_model_has_algorithm_name_field(self):
        """测试模型是否有 algorithm_name 字段"""
        # 检查字段是否存在
        assert hasattr(ErrorAnalysisTask, 'algorithm_name'), \
            "ErrorAnalysisTask 模型应该有 algorithm_name 字段"

    def test_algorithm_name_field_type(self):
        """测试 algorithm_name 字段类型"""
        # 获取字段类型
        field_type = ErrorAnalysisTask.algorithm_name.type
        # 应该是 String 类型
        from sqlalchemy import String
        assert isinstance(field_type, String), \
            "algorithm_name 应该是 String 类型"

    def test_algorithm_name_field_nullable(self):
        """测试 algorithm_name 字段是否可空"""
        # 默认情况下应该是可空的，以保持向后兼容
        assert ErrorAnalysisTask.algorithm_name.nullable, \
            "algorithm_name 应该是可空的，以保持向后兼容"

    def test_algorithm_name_field_default(self):
        """测试 algorithm_name 字段默认值"""
        # 创建任务时不提供 algorithm_name
        task = ErrorAnalysisTask(
            task_id="test-task-1",
            radar_station_ids=[1, 2],
            track_ids=["T001"],
            user_id=1,
        )
        # 默认值应该是 None 或 'gradient_descent'
        assert task.algorithm_name is None or task.algorithm_name == 'gradient_descent', \
            "algorithm_name 默认值应该是 None 或 'gradient_descent'"

    def test_create_task_with_algorithm_name(self, db_session: Session):
        """测试创建带有算法名称的任务"""
        task = ErrorAnalysisTask(
            task_id="test-task-2",
            radar_station_ids=[1, 2, 3],
            track_ids=["T001", "T002"],
            user_id=1,
            algorithm_name="gradient_descent"
        )

        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        assert task.algorithm_name == "gradient_descent"

    def test_create_task_with_different_algorithm(self, db_session: Session):
        """测试创建使用不同算法的任务"""
        # 为未来扩展做准备
        task = ErrorAnalysisTask(
            task_id="test-task-3",
            radar_station_ids=[1, 2],
            track_ids=["T001"],
            user_id=1,
            algorithm_name="least_squares"  # 假设的未来算法
        )

        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        assert task.algorithm_name == "least_squares"

    def test_algorithm_name_max_length(self):
        """测试 algorithm_name 字段最大长度"""
        field_type = ErrorAnalysisTask.algorithm_name.type
        # 应该有合理的最大长度限制
        if hasattr(field_type, 'length'):
            assert field_type.length >= 50, \
                "algorithm_name 字段长度应该至少为 50"

    @pytest.mark.parametrize("algorithm_name", [
        "gradient_descent",
        "least_squares",
        "kalman_filter",
        "particle_filter",
        "neural_network",
        "ensemble_method",
    ])
    def test_valid_algorithm_names(self, db_session: Session, algorithm_name: str):
        """测试有效的算法名称"""
        task = ErrorAnalysisTask(
            task_id=f"test-task-{algorithm_name}",
            radar_station_ids=[1, 2],
            track_ids=["T001"],
            user_id=1,
            algorithm_name=algorithm_name
        )

        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        assert task.algorithm_name == algorithm_name

    def test_backwards_compatibility(self, db_session: Session):
        """测试向后兼容性：创建没有 algorithm_name 的任务"""
        # 模拟旧数据
        task = ErrorAnalysisTask(
            task_id="test-task-old",
            radar_station_ids=[1, 2],
            track_ids=["T001"],
            user_id=1
            # 不设置 algorithm_name
        )

        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        # 应该能正常创建和查询
        assert task.task_id == "test-task-old"
        # algorithm_name 应该是 None 或默认值
        assert task.algorithm_name is None or task.algorithm_name == 'gradient_descent'
