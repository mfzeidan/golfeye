"""Calculates direction to ball landing location for compass."""
import math
import logging
from typing import Optional, Tuple
import cv2
from src.config import Config

logger = logging.getLogger(__name__)


class DirectionCalculator:
    """Calculates compass direction to ball location."""
    
    def __init__(self, frame_width: int = None, frame_height: int = None):
        """
        Initialize direction calculator.
        
        Args:
            frame_width: Camera frame width (defaults to config)
            frame_height: Camera frame height (defaults to config)
        """
        self.frame_width = frame_width or Config.CAMERA_WIDTH
        self.frame_height = frame_height or Config.CAMERA_HEIGHT
        self.camera_center_x = self.frame_width / 2
        self.camera_center_y = self.frame_height / 2
    
    def calculate_direction(self, target_position: Optional[Tuple[float, float]], 
                          camera_position: Tuple[float, float] = None) -> Optional[float]:
        """
        Calculate compass direction (0-360 degrees) to target position.
        
        Args:
            target_position: (x, y) target position in image coordinates
            camera_position: (x, y) camera position (defaults to center)
            
        Returns:
            Direction in degrees (0-360, where 0 is north/forward, 90 is east/right)
            or None if position is invalid
        """
        if target_position is None:
            return None
        
        tx, ty = target_position
        
        # Use camera center as reference point
        cx, cy = camera_position if camera_position else (self.camera_center_x, self.camera_center_y)
        
        # Calculate vector from camera to target
        dx = tx - cx
        dy = ty - cy
        
        # Calculate angle in radians (atan2 gives angle from positive x-axis)
        # In image coordinates: x increases right, y increases down
        # For compass: 0° = forward (negative y in image), 90° = right (positive x)
        angle_rad = math.atan2(dx, -dy)  # Negative y because forward is up
        
        # Convert to degrees (0-360)
        angle_deg = math.degrees(angle_rad)
        if angle_deg < 0:
            angle_deg += 360
        
        return angle_deg
    
    def calculate_distance(self, target_position: Optional[Tuple[float, float]],
                          camera_position: Tuple[float, float] = None) -> Optional[float]:
        """
        Calculate approximate distance to target (in pixels).
        
        Args:
            target_position: (x, y) target position
            camera_position: (x, y) camera position (defaults to center)
            
        Returns:
            Distance in pixels or None if position is invalid
        """
        if target_position is None:
            return None
        
        tx, ty = target_position
        cx, cy = camera_position if camera_position else (self.camera_center_x, self.camera_center_y)
        
        distance = math.sqrt((tx - cx)**2 + (ty - cy)**2)
        return distance
    
    def pixel_to_meters(self, pixel_distance: float, estimated_ball_height: float = 0.043) -> float:
        """
        Convert pixel distance to meters (rough approximation).
        
        Args:
            pixel_distance: Distance in pixels
            estimated_ball_height: Estimated ball height in meters (golf ball ≈ 0.043m)
            
        Returns:
            Distance in meters (rough estimate)
        """
        # This is a very rough approximation
        # In a real system, you'd need camera calibration
        # Assuming ball appears ~20 pixels tall at 10 meters
        pixels_per_meter = 20 / 10
        return pixel_distance / pixels_per_meter
