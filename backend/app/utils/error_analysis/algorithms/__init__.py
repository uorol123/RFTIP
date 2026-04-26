"""
误差分析算法实现目录

所有算法实现都在此目录下
"""

def register_all_algorithms():
    """注册所有算法"""
    # 导入并注册 MRRA 算法
    from app.utils.error_analysis.algorithms.mrra import MrraAlgorithm

    # 未来添加的算法在这里导入注册:
    # from app.utils.error_analysis.algorithms.least_squares import LeastSquaresAlgorithm
    # from app.utils.error_analysis.algorithms.kalman_filter import KalmanFilterAlgorithm
