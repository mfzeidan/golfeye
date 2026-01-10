"""Configuration management for golf ball tracker."""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""
    
    # Camera Configuration
    CAMERA_INDEX: int = int(os.getenv("CAMERA_INDEX", "0"))
    CAMERA_WIDTH: int = int(os.getenv("CAMERA_WIDTH", "640"))
    CAMERA_HEIGHT: int = int(os.getenv("CAMERA_HEIGHT", "480"))
    FRAME_SKIP: int = int(os.getenv("FRAME_SKIP", "3"))
    
    # Detection Thresholds
    COLOR_DETECTION_ENABLED: bool = os.getenv("COLOR_DETECTION_ENABLED", "true").lower() == "true"
    ML_DETECTION_ENABLED: bool = os.getenv("ML_DETECTION_ENABLED", "false").lower() == "true"
    MIN_BALL_AREA: int = int(os.getenv("MIN_BALL_AREA", "50"))
    MAX_BALL_AREA: int = int(os.getenv("MAX_BALL_AREA", "5000"))
    MIN_CIRCULARITY: float = float(os.getenv("MIN_CIRCULARITY", "0.7"))
    
    # Color detection HSV ranges (for white ball)
    COLOR_LOWER_H: int = int(os.getenv("COLOR_LOWER_H", "0"))
    COLOR_LOWER_S: int = int(os.getenv("COLOR_LOWER_S", "0"))
    COLOR_LOWER_V: int = int(os.getenv("COLOR_LOWER_V", "200"))
    COLOR_UPPER_H: int = int(os.getenv("COLOR_UPPER_H", "180"))
    COLOR_UPPER_S: int = int(os.getenv("COLOR_UPPER_S", "30"))
    COLOR_UPPER_V: int = int(os.getenv("COLOR_UPPER_V", "255"))
    
    # ML Model Paths
    ML_MODEL_PATH: Optional[str] = os.getenv("ML_MODEL_PATH", "models/golf_ball_detector.tflite")
    
    # Launch Detection
    LAUNCH_VELOCITY_THRESHOLD: float = float(os.getenv("LAUNCH_VELOCITY_THRESHOLD", "50.0"))
    LAUNCH_MOTION_THRESHOLD: float = float(os.getenv("LAUNCH_MOTION_THRESHOLD", "1000.0"))
    
    # Trajectory Prediction
    GRAVITY: float = float(os.getenv("GRAVITY", "9.81"))
    AIR_RESISTANCE_COEFF: float = float(os.getenv("AIR_RESISTANCE_COEFF", "0.02"))
    PREDICTION_FRAMES: int = int(os.getenv("PREDICTION_FRAMES", "60"))
    
    # Kalman Filter
    KALMAN_PROCESS_NOISE: float = float(os.getenv("KALMAN_PROCESS_NOISE", "0.03"))
    KALMAN_MEASUREMENT_NOISE: float = float(os.getenv("KALMAN_MEASUREMENT_NOISE", "0.3"))
    
    # Web Server
    WEB_PORT: int = int(os.getenv("WEB_PORT", "5000"))
    WEB_HOST: str = os.getenv("WEB_HOST", "0.0.0.0")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
