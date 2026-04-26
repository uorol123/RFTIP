"""粒子滤波算法模块"""
from app.utils.error_analysis.algorithms.particle_filter.algorithm import ParticleFilterAlgorithm

__all__ = ["ParticleFilterAlgorithm"]

from app.utils.error_analysis.registry import register_algorithm
register_algorithm(ParticleFilterAlgorithm)
