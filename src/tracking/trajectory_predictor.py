"""Predicts ball trajectory and landing location."""
import numpy as np
import logging
from typing import List, Tuple, Optional
from src.config import Config

logger = logging.getLogger(__name__)


class TrajectoryPredictor:
    """Predicts ball trajectory using physics-based modeling."""
    
    def __init__(self):
        """Initialize trajectory predictor."""
        self.gravity = Config.GRAVITY
        self.air_resistance_coeff = Config.AIR_RESISTANCE_COEFF
        self.prediction_frames = Config.PREDICTION_FRAMES
        self.trajectory_history: List[Tuple[float, float, float, float]] = []  # (x, y, vx, vy)
        self.max_history = 30
    
    def add_point(self, x: float, y: float, vx: float, vy: float) -> None:
        """
        Add a point to trajectory history.
        
        Args:
            x: X position
            y: Y position
            vx: X velocity
            vy: Y velocity
        """
        self.trajectory_history.append((x, y, vx, vy))
        if len(self.trajectory_history) > self.max_history:
            self.trajectory_history.pop(0)
    
    def predict_landing(self, fps: float = 30.0) -> Optional[Tuple[float, float]]:
        """
        Predict landing location based on trajectory history.
        
        Args:
            fps: Frames per second (for time calculations)
            
        Returns:
            (x, y) predicted landing location or None if insufficient data
        """
        if len(self.trajectory_history) < 3:
            return None
        
        # Get the most recent point
        x0, y0, vx0, vy0 = self.trajectory_history[-1]
        
        # Convert pixel velocities to m/s (rough approximation)
        # Assuming camera is calibrated: 1 pixel ≈ 0.01 meters at ball distance
        pixel_to_meter = 0.01
        vx_mps = vx0 * pixel_to_meter * fps
        vy_mps = vy0 * pixel_to_meter * fps
        
        # Simple projectile motion with air resistance
        # For golf ball, we'll use simplified model
        # Assuming ball is in flight (y is increasing upward in image coordinates)
        # In image coordinates, y increases downward, so we need to account for that
        
        # Time to landing (simplified - find when ball hits ground level)
        # Using last few points to estimate trajectory
        if len(self.trajectory_history) >= 5:
            # Use recent points to fit trajectory
            recent_points = self.trajectory_history[-5:]
            
            # Estimate vertical acceleration
            vy_values = [p[3] for p in recent_points]
            if len(vy_values) >= 2:
                # Estimate acceleration from velocity change
                dt = 1.0 / fps
                ay_estimate = (vy_values[-1] - vy_values[0]) / (len(vy_values) - 1) / dt
            else:
                ay_estimate = self.gravity * pixel_to_meter * fps * fps  # Convert gravity to pixels/frame^2
            
            # Predict forward until ball would hit ground (y stops increasing or starts decreasing)
            # In image coordinates, ground is typically at bottom (high y values)
            current_y = y0
            current_x = x0
            current_vy = vy0
            current_vx = vx0
            
            for _ in range(self.prediction_frames):
                # Update position
                current_x += current_vx
                current_y += current_vy
                
                # Update velocity (apply gravity and air resistance)
                current_vy += ay_estimate * (1.0 / fps)
                current_vx *= (1.0 - self.air_resistance_coeff / fps)
                
                # Check if ball would have landed (velocity becomes positive downward)
                # or if we've gone too far
                if current_vy > 0:  # Ball falling
                    break
            
            return (current_x, current_y)
        
        # Fallback: simple linear extrapolation
        if abs(vx0) > 0.1 or abs(vy0) > 0.1:
            # Extrapolate forward
            landing_x = x0 + vx0 * self.prediction_frames
            landing_y = y0 + vy0 * self.prediction_frames
            return (landing_x, landing_y)
        
        return None
    
    def get_trajectory_points(self) -> List[Tuple[float, float]]:
        """
        Get historical trajectory points.
        
        Returns:
            List of (x, y) positions
        """
        return [(x, y) for x, y, _, _ in self.trajectory_history]
    
    def reset(self) -> None:
        """Reset trajectory history."""
        self.trajectory_history.clear()
