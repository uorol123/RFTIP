"""
误差分析算法集成测试
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from sqlalchemy.orm import Session

from app.services.error_analysis_service import ErrorAnalysisService
from app.schemas.error_analysis import ErrorAnalysisRequest, ErrorAnalysisConfig
from app.models.error_analysis import ErrorAnalysisTask, ErrorAnalysisTaskStatus


@pytest.mark.integration
class TestErrorAnalysisAlgorithmIntegration:
    """误差分析算法集成测试"""

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
    def sample_request(self):
        """样本请求"""
        return ErrorAnalysisRequest(
            radar_station_ids=[1, 2, 3],
            track_ids=["T001", "T002"],
            algorithm="gradient_descent",
            config=ErrorAnalysisConfig()
        )

    def test_full_workflow_with_gradient_descent(self, service, db_session, sample_request):
        """测试完整的梯度下降算法工作流程"""
        # 1. 创建任务
        db_session.add = Mock()
        db_session.commit = Mock()
        db_session.refresh = Mock()

        response = service.create_analysis_task(sample_request, user_id=1)

        assert response.algorithm_name == "gradient_descent"
        assert response.status == ErrorAnalysisTaskStatus.PENDING

        # 2. 模拟任务对象
        task = ErrorAnalysisTask(
            task_id=response.task_id,
            radar_station_ids=sample_request.radar_station_ids,
            track_ids=sample_request.track_ids,
            user_id=1,
            algorithm_name="gradient_descent",
            config=sample_request.config.model_dump(),
            status=ErrorAnalysisTaskStatus.PENDING
        )

        # 模拟数据库查询
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = task
        db_session.query.return_value = mock_query

        # 3. 模拟分析流程
        with patch('app.services.error_analysis_service.load_track_points_by_track_ids') as mock_load:
            mock_load.return_value = {
                1: [],
                2: [],
                3: []
            }

            with patch('app.services.error_analysis_service.extract_key_tracks') as mock_extract:
                mock_extract.return_value = []

                with patch('app.services.error_analysis_service.interpolate_and_save_tracks'):
                    with patch('app.services.error_analysis_service.match_tracks_from_database') as mock_match:
                        mock_match.return_value = []

                        with patch('app.services.error_analysis_service.save_matched_groups'):
                            with patch('app.services.error_analysis_service.calculate_error_results') as mock_calc:
                                mock_calc.return_value = {
                                    'errors': {
                                        1: {'azimuth_error': 0.5, 'range_error': 100, 'elevation_error': 0.3},
                                        2: {'azimuth_error': -0.3, 'range_error': -80, 'elevation_error': 0.2},
                                        3: {'azimuth_error': 0.1, 'range_error': 50, 'elevation_error': -0.1},
                                    },
                                    'match_group_count': 100
                                }

                                # 执行分析
                                service.execute_analysis(response.task_id)

                                # 验证任务状态
                                assert task.status == ErrorAnalysisTaskStatus.COMPLETED
                                assert task.progress == 100

    def test_backward_compatibility_without_algorithm_name(self, service, db_session):
        """测试向后兼容性：没有算法名称的任务"""
        # 创建不指定算法的请求
        request = ErrorAnalysisRequest(
            radar_station_ids=[1, 2],
            track_ids=["T001"]
        )

        db_session.add = Mock()
        db_session.commit = Mock()
        db_session.refresh = Mock()

        response = service.create_analysis_task(request, user_id=1)

        # 应该使用默认算法
        assert response.algorithm_name == "gradient_descent"

    def test_algorithm_factory_integration(self, service, db_session):
        """测试算法工厂集成"""
        request = ErrorAnalysisRequest(
            radar_station_ids=[1, 2],
            track_ids=["T001"],
            algorithm="gradient_descent"
        )

        db_session.add = Mock()
        db_session.commit = Mock()
        db_session.refresh = Mock()

        response = service.create_analysis_task(request, user_id=1)

        task = ErrorAnalysisTask(
            task_id=response.task_id,
            radar_station_ids=[1, 2],
            track_ids=["T001"],
            user_id=1,
            algorithm_name="gradient_descent",
            status=ErrorAnalysisTaskStatus.PENDING
        )

        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = task
        db_session.query.return_value = mock_query

        with patch('app.services.error_analysis_service.AlgorithmFactory') as mock_factory:
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

                                service.execute_analysis(response.task_id)

                                # 验证算法工厂被正确调用
                                mock_factory.create_algorithm_from_dict.assert_called_once()
                                call_args = mock_factory.create_algorithm_from_dict.call_args
                                assert call_args[0][0] == "gradient_descent"

    @pytest.mark.parametrize("algorithm_name,should_succeed", [
        ("gradient_descent", True),
        ("least_squares", False),  # 假设未实现
        ("invalid_algorithm", False),
    ])
    def test_different_algorithms(self, service, db_session, algorithm_name, should_succeed):
        """测试不同算法的处理"""
        request = ErrorAnalysisRequest(
            radar_station_ids=[1, 2],
            track_ids=["T001"],
            algorithm=algorithm_name
        )

        db_session.add = Mock()
        db_session.commit = Mock()
        db_session.refresh = Mock()

        if should_succeed:
            response = service.create_analysis_task(request, user_id=1)
            assert response.algorithm_name == algorithm_name
        else:
            # 未实现的算法应该抛出异常
            with patch('app.services.error_analysis_service.AlgorithmFactory') as mock_factory:
                mock_factory.create_algorithm_from_dict.side_effect = ValueError(f"未知算法: {algorithm_name}")

                task = ErrorAnalysisTask(
                    task_id="test-task",
                    radar_station_ids=[1, 2],
                    track_ids=["T001"],
                    user_id=1,
                    algorithm_name=algorithm_name,
                    status=ErrorAnalysisTaskStatus.PENDING
                )

                mock_query = Mock()
                mock_query.filter.return_value.first.return_value = task
                db_session.query.return_value = mock_query

                with pytest.raises(ValueError):
                    service.execute_analysis("test-task")
