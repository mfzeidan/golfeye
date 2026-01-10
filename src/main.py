"""Main application entry point for golf ball tracker."""
import logging
import threading
import time
import sys
from typing import Optional
from src.config import Config
from src.camera import CameraHandler
from src.detection import HybridDetector, LaunchDetector
from src.tracking import BallTracker
from src.compass import DirectionCalculator
from src.web import compass_state, broadcast_update, start_server, debug_state, broadcast_debug_update, encode_image

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GolfBallTracker:
    """Main application orchestrator."""
    
    def __init__(self):
        """Initialize golf ball tracker."""
        self.camera: Optional[CameraHandler] = None
        self.detector = HybridDetector()
        self.launch_detector = LaunchDetector()
        self.tracker = BallTracker()
        self.direction_calc = DirectionCalculator()
        self.running = False
        self.frame_count = 0
        self.fps = 30.0  # Estimated FPS
        
    def initialize_camera(self) -> bool:
        """
        Initialize camera.
        
        Returns:
            True if camera initialized successfully
        """
        try:
            self.camera = CameraHandler()
            if not self.camera.open():
                logger.error("Failed to initialize camera")
                return False
            
            compass_state.update(camera_status="connected")
            broadcast_update()
            logger.info("Camera initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing camera: {e}")
            compass_state.update(camera_status="error")
            broadcast_update()
            return False
    
    def process_frame(self, frame) -> None:
        """
        Process a single frame.
        
        Args:
            frame: Camera frame
        """
        self.frame_count += 1
        
        # Skip frames for performance
        if self.frame_count % Config.FRAME_SKIP != 0:
            return
        
        try:
            # Detect ball with debug info
            debug_info = self.detector.detect_with_debug(frame)
            detection = debug_info.get('best_detection')
            
            # Update debug state (every 5 frames to reduce bandwidth)
            if self.frame_count % 5 == 0:
                # Create annotated frame
                debug_frame = frame.copy()
                
                # Draw all detections
                for det in debug_info.get('all_detections', []):
                    x, y, conf = det
                    cv2.circle(debug_frame, (x, y), 10, (0, 255, 0), 2)
                    cv2.putText(debug_frame, f"{conf:.2f}", (x+15, y), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                
                # Draw best detection
                if detection:
                    x, y, conf = detection
                    cv2.circle(debug_frame, (x, y), 20, (0, 0, 255), 3)
                    cv2.putText(debug_frame, f"BEST: {conf:.2f}", (x-30, y-25), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                
                # Draw tracked position
                position = self.tracker.get_position()
                if position:
                    px, py = int(position[0]), int(position[1])
                    cv2.circle(debug_frame, (px, py), 15, (255, 0, 0), 2)
                
                # Update debug state
                debug_state['frame_data'] = encode_image(debug_frame)
                debug_state['mask_data'] = encode_image(debug_info.get('color_mask'))
                debug_state['detections'] = [
                    {'x': int(d[0]), 'y': int(d[1]), 'confidence': float(d[2])} 
                    for d in debug_info.get('all_detections', [])
                ]
                debug_state['frame_count'] = self.frame_count
                debug_state['fps'] = self.fps
                debug_state['config'] = {
                    'camera_index': Config.CAMERA_INDEX,
                    'frame_skip': Config.FRAME_SKIP,
                    'min_ball_area': Config.MIN_BALL_AREA,
                    'max_ball_area': Config.MAX_BALL_AREA,
                    'min_circularity': Config.MIN_CIRCULARITY,
                    'color_lower': [Config.COLOR_LOWER_H, Config.COLOR_LOWER_S, Config.COLOR_LOWER_V],
                    'color_upper': [Config.COLOR_UPPER_H, Config.COLOR_UPPER_S, Config.COLOR_UPPER_V]
                }
                broadcast_debug_update()
            
            # Update tracker
            self.tracker.update(detection)
            
            # Check for launch
            if detection:
                launch_detected = self.launch_detector.update((detection[0], detection[1]))
                if launch_detected:
                    compass_state.update(launch_detected=True)
                    logger.info("Ball launch detected!")
            else:
                self.launch_detector.update(None)
            
            # Get current position
            position = self.tracker.get_position()
            velocity = self.tracker.get_velocity()
            
            # Determine status
            if not self.tracker.is_tracking():
                status = "lost"
                # Try to predict landing location
                landing = self.tracker.predict_landing(self.fps)
                if landing:
                    direction = self.direction_calc.calculate_direction(landing)
                    distance_px = self.direction_calc.calculate_distance(landing)
                    distance_m = self.direction_calc.pixel_to_meters(distance_px) if distance_px else None
                    
                    compass_state.update(
                        direction=direction,
                        distance=distance_m,
                        status="predicted",
                        confidence=0.7  # Lower confidence for predictions
                    )
                else:
                    compass_state.update(status="lost")
            elif position:
                # Calculate direction to current position
                direction = self.direction_calc.calculate_direction(position)
                distance_px = self.direction_calc.calculate_distance(position)
                distance_m = self.direction_calc.pixel_to_meters(distance_px) if distance_px else None
                
                # Get confidence from detection
                confidence = detection[2] if detection else 0.5
                
                compass_state.update(
                    direction=direction,
                    distance=distance_m,
                    status="tracking",
                    confidence=confidence
                )
            else:
                compass_state.update(status="waiting")
            
            # Broadcast update
            broadcast_update()
            
        except Exception as e:
            logger.error(f"Error processing frame: {e}")
    
    def run_camera_loop(self) -> None:
        """Main camera processing loop."""
        logger.info("Starting camera processing loop")
        
        while self.running:
            if self.camera is None or not self.camera.is_open:
                logger.warning("Camera not available, waiting...")
                time.sleep(1)
                continue
            
            success, frame = self.camera.read()
            if not success:
                logger.warning("Failed to read frame")
                time.sleep(0.1)
                continue
            
            self.process_frame(frame)
            
            # Small delay to prevent CPU overload
            time.sleep(1.0 / self.fps)
        
        logger.info("Camera processing loop stopped")
    
    def start(self) -> None:
        """Start the tracker."""
        logger.info("Starting Golf Ball Tracker")
        
        if not self.initialize_camera():
            logger.error("Failed to initialize camera, exiting")
            return
        
        self.running = True
        
        # Start camera processing in separate thread
        camera_thread = threading.Thread(target=self.run_camera_loop, daemon=True)
        camera_thread.start()
        
        logger.info("Golf Ball Tracker started")
    
    def stop(self) -> None:
        """Stop the tracker."""
        logger.info("Stopping Golf Ball Tracker")
        self.running = False
        
        if self.camera:
            self.camera.release()
        
        compass_state.update(camera_status="disconnected")
        broadcast_update()
    
    def reset(self) -> None:
        """Reset tracking state."""
        logger.info("Resetting tracker")
        self.tracker.reset()
        self.launch_detector.reset()
        compass_state.update(
            direction=None,
            distance=None,
            status="waiting",
            confidence=0.0,
            launch_detected=False
        )
        broadcast_update()


def main():
    """Main entry point."""
    tracker = GolfBallTracker()
    
    try:
        # Start tracker
        tracker.start()
        
        # Start web server (blocks)
        logger.info(f"Starting web server on {Config.WEB_HOST}:{Config.WEB_PORT}")
        start_server(host=Config.WEB_HOST, port=Config.WEB_PORT, debug=False)
        
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
    finally:
        tracker.stop()
        logger.info("Application stopped")


if __name__ == "__main__":
    main()
