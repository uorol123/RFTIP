def register_all_algorithms():
    """注册所有算法"""
    # 多源参考模式
    from app.algorithms.multi_source.mrra import MrraAlgorithm
    from app.algorithms.multi_source.ransac import RansacAlgorithm
    from app.algorithms.multi_source.ransac_heuristic import RansacHeuristicAlgorithm
    from app.algorithms.multi_source.weighted_lstsq import WeightedLstsqAlgorithm

    # 单源盲测模式
    from app.algorithms.single_source.kalman import KalmanAlgorithm
    from app.algorithms.single_source.particle_filter import ParticleFilterAlgorithm
    from app.algorithms.single_source.spline import SplineAlgorithm
