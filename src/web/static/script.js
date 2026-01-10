// Golf Ball Tracker Compass JavaScript
const socket = io();

let currentDirection = null;
let currentDistance = null;
let currentStatus = 'waiting';

// DOM elements
const compassNeedle = document.getElementById('compass-needle');
const directionDisplay = document.getElementById('direction-display');
const distanceDisplay = document.getElementById('distance-display');
const statusValue = document.getElementById('status-value');
const confidenceValue = document.getElementById('confidence-value');
const cameraStatusValue = document.getElementById('camera-status-value');
const launchStatusValue = document.getElementById('launch-status-value');
const resetButton = document.getElementById('reset-button');

// Socket event handlers
socket.on('connect', () => {
    console.log('Connected to server');
    updateCameraStatus('connected');
});

socket.on('disconnect', () => {
    console.log('Disconnected from server');
    updateCameraStatus('disconnected');
});

socket.on('compass_update', (data) => {
    updateCompass(data);
});

// Update compass display
function updateCompass(data) {
    // Update direction
    if (data.direction !== null && data.direction !== undefined) {
        currentDirection = data.direction;
        updateDirection(data.direction);
    }
    
    // Update distance
    if (data.distance !== null && data.distance !== undefined) {
        currentDistance = data.distance;
        updateDistance(data.distance);
    } else {
        distanceDisplay.textContent = '-- m';
    }
    
    // Update status
    if (data.status) {
        currentStatus = data.status;
        updateStatus(data.status);
    }
    
    // Update confidence
    if (data.confidence !== null && data.confidence !== undefined) {
        updateConfidence(data.confidence);
    }
    
    // Update camera status
    if (data.camera_status) {
        updateCameraStatus(data.camera_status);
    }
    
    // Update launch status
    if (data.launch_detected !== null && data.launch_detected !== undefined) {
        updateLaunchStatus(data.launch_detected);
    }
}

function updateDirection(degrees) {
    // Rotate compass needle
    compassNeedle.style.transform = `translate(-50%, -100%) rotate(${degrees}deg)`;
    
    // Update direction display
    const direction = Math.round(degrees);
    directionDisplay.textContent = `${direction}°`;
    
    // Add cardinal direction
    const cardinal = getCardinalDirection(degrees);
    directionDisplay.textContent = `${direction}° ${cardinal}`;
}

function updateDistance(meters) {
    if (meters !== null && meters !== undefined) {
        const distance = Math.round(meters);
        distanceDisplay.textContent = `${distance} m`;
    }
}

function updateStatus(status) {
    statusValue.textContent = status.charAt(0).toUpperCase() + status.slice(1);
    statusValue.className = `status-value status-${status}`;
}

function updateConfidence(confidence) {
    const percent = Math.round(confidence * 100);
    confidenceValue.textContent = `${percent}%`;
}

function updateCameraStatus(status) {
    cameraStatusValue.textContent = status.charAt(0).toUpperCase() + status.slice(1);
    cameraStatusValue.className = `status-value ${status === 'connected' ? 'status-tracking' : 'status-lost'}`;
}

function updateLaunchStatus(detected) {
    launchStatusValue.textContent = detected ? 'Yes' : 'No';
    launchStatusValue.className = `status-value ${detected ? 'status-tracking' : 'status-waiting'}`;
}

function getCardinalDirection(degrees) {
    const directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'];
    const index = Math.round(degrees / 45) % 8;
    return directions[index];
}

// Reset button handler
resetButton.addEventListener('click', () => {
    socket.emit('reset');
});

// Initialize display
updateStatus('waiting');
updateConfidence(0);
updateCameraStatus('disconnected');
updateLaunchStatus(false);
