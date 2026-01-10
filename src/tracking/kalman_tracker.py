"""Kalman filter for smooth ball tracking."""
import cv2
import numpy as np
import logging
from typing import Optional, Tuple
from src.config import Config

logger = logging.getLogger(__name__)


class KalmanTracker:
    """Kalman filter for tracking ball position and velocity."""
    
    def __init__(self):
        """Initialize Kalman filter."""
        # State: [x, y, vx, vy] (position and velocity)
        self.kalman = cv2.KalmanFilter(4, 2)
        
        # Transition matrix (constant velocity model)
        self.kalman.transitionMatrix = np.array([
            [1, 0, 1, 0],
            [0, 1, 0, 1],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)
        
        # Measurement matrix (we only observe position)
        self.kalman.measurementMatrix = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0]
        ], dtype=np.float32)
        
        # Process noise covariance
        process_noise = Config.KALMAN_PROCESS_NOISE
        self.kalman.processNoiseCov = np.eye(4, dtype=np.float32) * process_noise
        
        # Measurement noise covariance
        measurement_noise = Config.KALMAN_MEASUREMENT_NOISE
        self.kalman.measurementNoiseCov = np.eye(2, dtype=np.float32) * measurement_noise
        
        # Error covariance
        self.kalman.errorCovPost = np.eye(4, dtype=np.float32)
        
        self.is_initialized = False
    
    def update(self, measurement: Optional[Tuple[int, int]]) -> Tuple[float, float, float, float]:
        """
        Update Kalman filter with new measurement.
        
        Args:
            measurement: (x, y) position or None if ball not detected
            
        Returns:
            (x, y, vx, vy) predicted state
        """
        if measurement is None:
            # No measurement, just predict
            predicted = self.kalman.predict()
            return (predicted[0], predicted[1], predicted[2], predicted[3])
        
        x, y = measurement
        
        if not self.is_initialized:
            # Initialize with first measurement
            self.kalman.statePre = np.array([x, y, 0, 0], dtype=np.float32)
            self.kalman.statePost = np.array([x, y, 0, 0], dtype=np.float32)
            self.is_initialized = True
        
        # Convert measurement to numpy array
        meas = np.array([[x], [y]], dtype=np.float32)
        
        # Predict
        predicted = self.kalman.predict()
        
        # Correct with measurement
        corrected = self.kalman.correct(meas)
        
        return (corrected[0], corrected[1], corrected[2], corrected[3])
    
    def predict(self) -> Tuple[float, float, float, float]:
        """
        Predict next state without measurement.
        
        Returns:
            (x, y, vx, vy) predicted state
        """
        if not self.is_initialized:
            return (0.0, 0.0, 0.0, 0.0)
        
        predicted = self.kalman.predict()
        return (predicted[0], predicted[1], predicted[2], predicted[3])
    
    def reset(self) -> None:
        """Reset Kalman filter."""
        self.is_initialized = False
        self.kalman.errorCovPost = np.eye(4, dtype=np.float32)
