"""Web module."""
from src.web.app import app, socketio, compass_state, broadcast_update, start_server

__all__ = ['app', 'socketio', 'compass_state', 'broadcast_update', 'start_server']
