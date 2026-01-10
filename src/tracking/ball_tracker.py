"""Main ball tracking coordinator."""
import logging
from typing import Optional, Tuple
from src.tracking.kalman_tracker import KalmanTracker
from src.tracking.trajectory_predictor import TrajectoryPredictor

logger = logging.getLogger(__name__)


class BallTracker:
    """Coordinates ball tracking using Kalman filter and trajectory prediction."""
    
    def __init__(self):
        """Initialize ball tracker."""
        self.kalman = KalmanTracker()
        self.trajectory = TrajectoryPredictor()
        self.current_position: Optional[Tuple[float, float]] = None
        self.current_velocity: Optional[Tuple[float, float]] = None
        self.frames_lost = 0
        self.max_frames_lost = 10
    
    def update(self, detection: Optional[Tuple[int, int, float]]) -> None:
        """
        Update tracker with new detection.
        
        Args:
            detection: (x, y, confidence) or None if no detection
        """
        if detection is None:
            self.frames_lost += 1
            # Predict position even without detection
            x, y, vx, vy = self.kalman.predict()
            self.current_position = (x, y)
            self.current_velocity = (vx, vy)
        else:
            x, y, confidence = detection
            self.frames_lost = 0
            
            # Update Kalman filter
            x, y, vx, vy = self.kalman.update((x, y))
            self.current_position = (x, y)
            self.current_velocity = (vx, vy)
            
            # Add to trajectory history
            self.trajectory.add_point(x, y, vx, vy)
    
    def get_position(self) -> Optional[Tuple[float, float]]:
        """
        Get current tracked position.
        
        Returns:
            (x, y) position or None if ball lost
        """
        if self.frames_lost > self.max_frames_lost:
            return None
        return self.current_position
    
    def get_velocity(self) -> Optional[Tuple[float, float]]:
        """
        Get current velocity.
        
        Returns:
            (vx, vy) velocity or None if ball lost
        """
        if self.frames_lost > self.max_frames_lost:
            return None
        return self.current_velocity
    
    def is_tracking(self) -> bool:
        """
        Check if tracker is actively tracking ball.
        
        Returns:
            True if tracking, False if ball lost
        """
        return self.frames_lost <= self.max_frames_lost
    
    def predict_landing(self, fps: float = 30.0) -> Optional[Tuple[float, float]]:
        """
        Predict landing location.
        
        Args:
            fps: Frames per second
            
        Returns:
            (x, y) predicted landing location or None
        """
        return self.trajectory.predict_landing(fps)
    
    def reset(self) -> None:
        """Reset tracker."""
        self.kalman.reset()
        self.trajectory.reset()
        self.current_position = None
        self.current_velocity = None
        self.frames_lost = 0
