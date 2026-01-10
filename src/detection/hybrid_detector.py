"""Hybrid detector combining color and ML detection."""
import logging
from typing import List, Tuple, Optional
import cv2
from src.detection.color_detector import ColorDetector
from src.detection.ml_detector import MLDetector
from src.config import Config

logger = logging.getLogger(__name__)


class HybridDetector:
    """Combines color-based and ML-based detection."""
    
    def __init__(self):
        """Initialize hybrid detector with color and ML components."""
        self.color_detector = ColorDetector()
        self.ml_detector = MLDetector(Config.ML_MODEL_PATH) if Config.ML_DETECTION_ENABLED else None
    
    def detect(self, frame: cv2.typing.MatLike) -> List[Tuple[int, int, float]]:
        """
        Detect golf balls using hybrid approach.
        
        Args:
            frame: Input BGR frame
            
        Returns:
            List of (x, y, confidence) tuples for detected balls
        """
        detections = []
        
        # First pass: Color detection (fast)
        color_detections = self.color_detector.detect(frame)
        detections.extend(color_detections)
        
        # Second pass: ML verification (if enabled)
        if self.ml_detector and Config.ML_DETECTION_ENABLED:
            ml_detections = self.ml_detector.detect(frame)
            
            # Combine and deduplicate detections
            # For now, just add ML detections (could implement NMS here)
            for ml_det in ml_detections:
                # Check if this detection is close to any color detection
                is_duplicate = False
                for color_det in color_detections:
                    dist = ((ml_det[0] - color_det[0])**2 + (ml_det[1] - color_det[1])**2)**0.5
                    if dist < 30:  # Within 30 pixels
                        is_duplicate = True
                        break
                
                if not is_duplicate:
                    detections.append(ml_det)
        
        # If no detections from color, use ML only if available
        if not detections and self.ml_detector and Config.ML_DETECTION_ENABLED:
            detections = self.ml_detector.detect(frame)
        
        return detections
    
    def get_best_detection(self, frame: cv2.typing.MatLike) -> Optional[Tuple[int, int, float]]:
        """
        Get the best (highest confidence) detection.
        
        Args:
            frame: Input BGR frame
            
        Returns:
            (x, y, confidence) tuple or None if no detection
        """
        detections = self.detect(frame)
        if not detections:
            return None
        
        # Return detection with highest confidence
        return max(detections, key=lambda d: d[2])
