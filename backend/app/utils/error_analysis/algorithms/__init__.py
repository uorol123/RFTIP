"""
误差分析算法实现目录

所有算法实现都在此目录下
"""

def register_all_algorithms():
    """注册所有算法"""
    # 多源参考模式
    from app.utils.error_analysis.algorithms.mrra import MrraAlgorithm
    from app.utils.error_analysis.algorithms.ransac import RansacAlgorithm
    from app.utils.error_analysis.algorithms.ransac_heuristic import RansacHeuristicAlgorithm
    from app.utils.error_analysis.algorithms.weighted_lstsq import WeightedLstsqAlgorithm

    # 单源盲测模式
    from app.utils.error_analysis.algorithms.kalman import KalmanAlgorithm
    from app.utils.error_analysis.algorithms.particle_filter import ParticleFilterAlgorithm
    from app.utils.error_analysis.algorithms.spline import SplineAlgorithm
