"""Color-based golf ball detection using HSV color space."""
import cv2
import numpy as np
import logging
from typing import List, Tuple, Optional
from src.config import Config

logger = logging.getLogger(__name__)


class ColorDetector:
    """Detects golf balls using color-based detection in HSV space."""
    
    def __init__(self):
        """Initialize color detector with HSV ranges from config."""
        self.lower_bound = np.array([
            Config.COLOR_LOWER_H,
            Config.COLOR_LOWER_S,
            Config.COLOR_LOWER_V
        ])
        self.upper_bound = np.array([
            Config.COLOR_UPPER_H,
            Config.COLOR_UPPER_S,
            Config.COLOR_UPPER_V
        ])
        self.min_area = Config.MIN_BALL_AREA
        self.max_area = Config.MAX_BALL_AREA
        self.min_circularity = Config.MIN_CIRCULARITY
    
    def detect(self, frame: cv2.typing.MatLike) -> List[Tuple[int, int, float]]:
        """
        Detect golf balls in a frame.
        
        Args:
            frame: Input BGR frame
            
        Returns:
            List of (x, y, confidence) tuples for detected balls
        """
        result = self.detect_with_debug(frame)
        return result['detections']
    
    def detect_with_debug(self, frame: cv2.typing.MatLike) -> dict:
        """
        Detect golf balls with debug information.
        
        Args:
            frame: Input BGR frame
            
        Returns:
            Dictionary with 'detections', 'mask', 'all_contours', 'filtered_contours'
        """
        if not Config.COLOR_DETECTION_ENABLED:
            return {
                'detections': [],
                'mask': None,
                'all_contours': [],
                'filtered_contours': []
            }
        
        try:
            # Convert to HSV
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(hsv, (5, 5), 0)
            
            # Create mask for white/light colors
            mask = cv2.inRange(blurred, self.lower_bound, self.upper_bound)
            
            # Morphological operations to clean up mask
            kernel = np.ones((5, 5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            
            # Find contours
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            all_contours = contours.copy()
            
            detections = []
            filtered_contours = []
            for contour in contours:
                area = cv2.contourArea(contour)
                
                # Filter by area
                if area < self.min_area or area > self.max_area:
                    continue
                
                # Calculate circularity
                perimeter = cv2.arcLength(contour, True)
                if perimeter == 0:
                    continue
                
                circularity = 4 * np.pi * area / (perimeter * perimeter)
                
                # Filter by circularity
                if circularity < self.min_circularity:
                    continue
                
                # Get centroid
                M = cv2.moments(contour)
                if M["m00"] == 0:
                    continue
                
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                
                # Confidence based on circularity and area
                confidence = min(circularity * (area / self.max_area), 1.0)
                
                detections.append((cx, cy, confidence))
                filtered_contours.append({
                    'contour': contour.tolist(),
                    'centroid': (cx, cy),
                    'area': float(area),
                    'circularity': float(circularity),
                    'confidence': float(confidence)
                })
            
            return {
                'detections': detections,
                'mask': mask,
                'all_contours': [c.tolist() for c in all_contours],
                'filtered_contours': filtered_contours
            }
            
        except Exception as e:
            logger.error(f"Error in color detection: {e}")
            return {
                'detections': [],
                'mask': None,
                'all_contours': [],
                'filtered_contours': []
            }
