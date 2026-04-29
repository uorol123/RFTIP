from app.algorithms.registry import register_algorithm
from app.algorithms.multi_source.ransac.algorithm import RansacAlgorithm

register_algorithm(RansacAlgorithm)
