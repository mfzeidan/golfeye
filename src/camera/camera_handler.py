"""Camera abstraction layer for Mac and Raspberry Pi."""
import cv2
import logging
from typing import Optional, Tuple
from src.config import Config

logger = logging.getLogger(__name__)


class CameraHandler:
    """Handles camera initialization and frame capture."""
    
    def __init__(self, camera_index: Optional[int] = None, 
                 width: Optional[int] = None, 
                 height: Optional[int] = None):
        """
        Initialize camera handler.
        
        Args:
            camera_index: Camera device index (defaults to config)
            width: Frame width (defaults to config)
            height: Frame height (defaults to config)
        """
        self.camera_index = camera_index or Config.CAMERA_INDEX
        self.width = width or Config.CAMERA_WIDTH
        self.height = height or Config.CAMERA_HEIGHT
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_open = False
        
    def open(self) -> bool:
        """
        Open camera connection.
        
        Returns:
            True if camera opened successfully, False otherwise
        """
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            if not self.cap.isOpened():
                logger.error(f"Failed to open camera at index {self.camera_index}")
                return False
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            # Verify resolution was set correctly
            actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            logger.info(f"Camera opened: {actual_width}x{actual_height}")
            self.is_open = True
            return True
            
        except Exception as e:
            logger.error(f"Error opening camera: {e}")
            return False
    
    def read(self) -> Tuple[bool, Optional[cv2.typing.MatLike]]:
        """
        Read a frame from the camera.
        
        Returns:
            Tuple of (success, frame) where success is True if frame was read
        """
        if not self.is_open or self.cap is None:
            return False, None
        
        try:
            ret, frame = self.cap.read()
            if not ret:
                logger.warning("Failed to read frame from camera")
                return False, None
            
            return True, frame
            
        except Exception as e:
            logger.error(f"Error reading frame: {e}")
            return False, None
    
    def release(self) -> None:
        """Release camera resources."""
        if self.cap is not None:
            self.cap.release()
            self.is_open = False
            logger.info("Camera released")
    
    def __enter__(self):
        """Context manager entry."""
        self.open()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.release()
    
    def __del__(self):
        """Cleanup on deletion."""
        self.release()
