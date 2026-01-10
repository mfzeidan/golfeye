"""Flask web server with WebSocket support for real-time compass updates."""
import logging
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from typing import Optional, Tuple
import json

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'golf-eye-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")


class CompassState:
    """Manages compass state for web interface."""
    
    def __init__(self):
        """Initialize compass state."""
        self.direction: Optional[float] = None
        self.distance: Optional[float] = None
        self.status: str = "waiting"  # waiting, tracking, lost, predicted
        self.confidence: float = 0.0
        self.camera_status: str = "disconnected"
        self.launch_detected: bool = False
    
    def update(self, direction: Optional[float] = None,
               distance: Optional[float] = None,
               status: Optional[str] = None,
               confidence: Optional[float] = None,
               camera_status: Optional[str] = None,
               launch_detected: Optional[bool] = None) -> None:
        """
        Update compass state.
        
        Args:
            direction: Compass direction in degrees
            distance: Distance in meters
            status: Tracking status
            confidence: Detection confidence
            camera_status: Camera status
            launch_detected: Whether launch was detected
        """
        if direction is not None:
            self.direction = direction
        if distance is not None:
            self.distance = distance
        if status is not None:
            self.status = status
        if confidence is not None:
            self.confidence = confidence
        if camera_status is not None:
            self.camera_status = camera_status
        if launch_detected is not None:
            self.launch_detected = launch_detected
    
    def to_dict(self) -> dict:
        """Convert state to dictionary for JSON serialization."""
        return {
            'direction': self.direction,
            'distance': self.distance,
            'status': self.status,
            'confidence': self.confidence,
            'camera_status': self.camera_status,
            'launch_detected': self.launch_detected
        }


# Global compass state
compass_state = CompassState()


@app.route('/')
def index():
    """Serve main compass interface."""
    return render_template('index.html')


@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    logger.info('Client connected')
    # Send current state to newly connected client
    emit('compass_update', compass_state.to_dict())


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    logger.info('Client disconnected')


@socketio.on('reset')
def handle_reset():
    """Handle reset request from client."""
    logger.info('Reset requested by client')
    compass_state.update(
        direction=None,
        distance=None,
        status="waiting",
        confidence=0.0,
        launch_detected=False
    )
    emit('compass_update', compass_state.to_dict())


def broadcast_update():
    """Broadcast compass state update to all connected clients."""
    socketio.emit('compass_update', compass_state.to_dict())


def start_server(host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
    """
    Start the Flask web server.
    
    Args:
        host: Host to bind to
        port: Port to listen on
        debug: Enable debug mode
    """
    logger.info(f"Starting web server on {host}:{port}")
    socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)
