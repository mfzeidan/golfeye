"""Detects when golf ball is launched/hit."""
import logging
from typing import Optional, Tuple
import numpy as np
from src.config import Config

logger = logging.getLogger(__name__)


class LaunchDetector:
    """Detects ball launch by monitoring motion and velocity."""
    
    def __init__(self):
        """Initialize launch detector."""
        self.velocity_threshold = Config.LAUNCH_VELOCITY_THRESHOLD
        self.motion_threshold = Config.LAUNCH_MOTION_THRESHOLD
        self.last_position: Optional[Tuple[int, int]] = None
        self.frame_count = 0
        self.launch_detected = False
    
    def update(self, position: Optional[Tuple[int, int]]) -> bool:
        """
        Update launch detector with new ball position.
        
        Args:
            position: Current ball position (x, y) or None if not detected
            
        Returns:
            True if launch detected, False otherwise
        """
        self.frame_count += 1
        
        # Reset launch flag after some time
        if self.launch_detected and self.frame_count > 30:
            self.launch_detected = False
        
        if position is None:
            self.last_position = None
            return False
        
        if self.last_position is None:
            self.last_position = position
            return False
        
        # Calculate velocity (pixels per frame)
        dx = position[0] - self.last_position[0]
        dy = position[1] - self.last_position[1]
        velocity = np.sqrt(dx**2 + dy**2)
        
        # Detect launch if velocity exceeds threshold
        if velocity > self.velocity_threshold and not self.launch_detected:
            self.launch_detected = True
            logger.info(f"Launch detected! Velocity: {velocity:.2f} px/frame")
            return True
        
        self.last_position = position
        return False
    
    def reset(self) -> None:
        """Reset launch detector state."""
        self.last_position = None
        self.frame_count = 0
        self.launch_detected = False
