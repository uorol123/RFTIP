"""
测试误差分析服务的算法支持
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from sqlalchemy.orm import Session

from app.services.error_analysis_service import ErrorAnalysisService
from app.models.error_analysis import ErrorAnalysisTask, ErrorAnalysisTaskStatus
from app.schemas.error_analysis import ErrorAnalysisRequest, ErrorAnalysisConfig


class TestErrorAnalysisServiceAlgorithmSupport:
    """测试 ErrorAnalysisService 的算法支持"""

    @pytest.fixture
    def db_session(self):
        """模拟数据库会话"""
        session = Mock(spec=Session)
        session.add = Mock()
        session.commit = Mock()
        session.refresh = Mock()
        session.query = Mock()
        return session

    @pytest.fixture
    def service(self, db_session):
        """创建服务实例"""
        return ErrorAnalysisService(db_session)

    @pytest.fixture
    def valid_request(self):
        """有效的分析请求"""
        return ErrorAnalysisRequest(
            radar_station_ids=[1, 2, 3],
            track_ids=["T001", "T002"],
            algorithm="gradient_descent",
            config=ErrorAnalysisConfig()
        )

    def test_create_task_with_algorithm_name(self, service, db_session, valid_request):
        """测试创建包含算法名称的任务"""
        # 模拟数据库添加和刷新
        db_session.add = Mock()
        db_session.commit = Mock()
        db_session.refresh = Mock()

        # 执行
        response = service.create_analysis_task(valid_request, user_id=1)

        # 验证
        assert response.algorithm_name == "gradient_descent"

    def test_create_task_with_default_algorithm(self, service, db_session):
        """测试创建任务时使用默认算法"""
        # 不指定算法名称的请求
        request = ErrorAnalysisRequest(
            radar_station_ids=[1, 2],
            track_ids=["T001"]
        )
        db_session.add = Mock()
        db_session.commit = Mock()
        db_session.refresh = Mock()

        # 执行
        response = service.create_analysis_task(request, user_id=1)

        # 验证：应该使用默认算法
        assert response.algorithm_name == "gradient_descent"

    @pytest.mark.parametrize("algorithm_name", [
        "gradient_descent",
        "least_squares",
        "kalman_filter",
    ])
    def test_create_task_with_different_algorithms(self, service, db_session, algorithm_name):
        """测试创建使用不同算法的任务"""
        request = ErrorAnalysisRequest(
            radar_station_ids=[1, 2],
            track_ids=["T001"],
            algorithm=algorithm_name
        )
        db_session.add = Mock()
        db_session.commit = Mock()
        db_session.refresh = Mock()

        response = service.create_analysis_task(request, user_id=1)

        assert response.algorithm_name == algorithm_name

    @patch('app.services.error_analysis_service.AlgorithmFactory')
    def test_execute_analysis_uses_algorithm_factory(self, mock_factory, service, db_session):
        """测试执行分析时使用 AlgorithmFactory"""
        # 准备测试数据
        task = ErrorAnalysisTask(
            task_id="test-task-1",
            radar_station_ids=[1, 2],
            track_ids=["T001"],
            user_id=1,
            algorithm_name="gradient_descent",
            status=ErrorAnalysisTaskStatus.PENDING
        )

        # 模拟数据库查询返回任务
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = task
        db_session.query.return_value = mock_query

        # 模拟算法实例
        mock_algorithm = Mock()
        mock_factory.create_algorithm_from_dict.return_value = mock_algorithm

        # 模拟雷达站数据
        with patch('app.services.error_analysis_service.load_track_points_by_track_ids') as mock_load:
            mock_load.return_value = {
                1: [],
                2: []
            }

            with patch('app.services.error_analysis_service.extract_key_tracks') as mock_extract:
                mock_extract.return_value = []

                with patch('app.services.error_analysis_service.interpolate_and_save_tracks'):
                    with patch('app.services.error_analysis_service.match_tracks_from_database') as mock_match:
                        mock_match.return_value = []

                        with patch('app.services.error_analysis_service.save_matched_groups'):
                            with patch('app.services.error_analysis_service.calculate_error_results') as mock_calc:
                                mock_calc.return_value = {
                                    'errors': {},
                                    'match_group_count': 0
                                }

                                # 执行
                                service.execute_analysis("test-task-1")

                                # 验证：应该调用 AlgorithmFactory
                                mock_factory.create_algorithm_from_dict.assert_called_once()
                                call_args = mock_factory.create_algorithm_from_dict.call_args
                                assert call_args[0][0] == "gradient_descent"

    def test_task_to_response_includes_algorithm_name(self, service):
        """测试任务转换响应包含算法名称"""
        task = ErrorAnalysisTask(
            id=1,
            task_id="test-task-1",
            radar_station_ids=[1, 2],
            track_ids=["T001"],
            user_id=1,
            algorithm_name="gradient_descent",
            status=ErrorAnalysisTaskStatus.PENDING,
            progress=0
        )

        response = service._task_to_response(task)

        assert response.algorithm_name == "gradient_descent"

    def test_task_to_response_with_none_algorithm_name(self, service):
        """测试任务转换响应处理 None 算法名称"""
        task = ErrorAnalysisTask(
            id=1,
            task_id="test-task-1",
            radar_station_ids=[1, 2],
            track_ids=["T001"],
            user_id=1,
            algorithm_name=None,
            status=ErrorAnalysisTaskStatus.PENDING,
            progress=0
        )

        response = service._task_to_response(task)

        assert response.algorithm_name is None

    @patch('app.services.error_analysis_service.AlgorithmFactory')
    def test_execute_analysis_handles_missing_algorithm(self, mock_factory, service, db_session):
        """测试执行分析时处理缺少算法名称的任务"""
        # 创建没有算法名称的任务（向后兼容）
        task = ErrorAnalysisTask(
            task_id="test-task-2",
            radar_station_ids=[1, 2],
            track_ids=["T001"],
            user_id=1,
            algorithm_name=None,  # 没有算法名称
            status=ErrorAnalysisTaskStatus.PENDING
        )

        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = task
        db_session.query.return_value = mock_query

        mock_algorithm = Mock()
        mock_factory.create_algorithm_from_dict.return_value = mock_algorithm

        with patch('app.services.error_analysis_service.load_track_points_by_track_ids') as mock_load:
            mock_load.return_value = {1: [], 2: []}

            with patch('app.services.error_analysis_service.extract_key_tracks') as mock_extract:
                mock_extract.return_value = []

                with patch('app.services.error_analysis_service.interpolate_and_save_tracks'):
                    with patch('app.services.error_analysis_service.match_tracks_from_database') as mock_match:
                        mock_match.return_value = []

                        with patch('app.services.error_analysis_service.save_matched_groups'):
                            with patch('app.services.error_analysis_service.calculate_error_results') as mock_calc:
                                mock_calc.return_value = {'errors': {}, 'match_group_count': 0}

                                # 执行
                                service.execute_analysis("test-task-2")

                                # 验证：应该使用默认算法
                                mock_factory.create_algorithm_from_dict.assert_called_once()
                                call_args = mock_factory.create_algorithm_from_dict.call_args
                                assert call_args[0][0] == "gradient_descent"
