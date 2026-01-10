"""Detection module."""
from src.detection.color_detector import ColorDetector
from src.detection.ml_detector import MLDetector
from src.detection.hybrid_detector import HybridDetector
from src.detection.launch_detector import LaunchDetector

__all__ = ['ColorDetector', 'MLDetector', 'HybridDetector', 'LaunchDetector']
