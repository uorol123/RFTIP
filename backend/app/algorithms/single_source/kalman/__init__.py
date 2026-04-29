from app.algorithms.registry import register_algorithm
from app.algorithms.single_source.kalman.algorithm import KalmanAlgorithm

register_algorithm(KalmanAlgorithm)
