// Debug page JavaScript
const socket = io();

// DOM elements
const cameraFeed = document.getElementById('camera-feed');
const maskFeed = document.getElementById('mask-feed');
const connectionStatus = document.getElementById('connection-status');
const frameCount = document.getElementById('frame-count');
const fpsDisplay = document.getElementById('fps');
const detectionCount = document.getElementById('detection-count');
const bestDetection = document.getElementById('best-detection');
const detectionsList = document.getElementById('detections-list');
const configList = document.getElementById('config-list');

let lastUpdateTime = Date.now();

// Socket event handlers
socket.on('connect', () => {
    console.log('Connected to debug server');
    updateConnectionStatus('connected');
    socket.emit('debug_connect');
});

socket.on('disconnect', () => {
    console.log('Disconnected from debug server');
    updateConnectionStatus('disconnected');
});

socket.on('debug_update', (data) => {
    updateDebugDisplay(data);
});

function updateConnectionStatus(status) {
    connectionStatus.textContent = status === 'connected' ? 'Connected' : 'Disconnected';
    connectionStatus.className = `status-badge ${status === 'connected' ? 'status-connected' : 'status-disconnected'}`;
}

function updateDebugDisplay(data) {
    // Update frame
    if (data.frame_data) {
        cameraFeed.src = `data:image/jpeg;base64,${data.frame_data}`;
    }
    
    // Update mask
    if (data.mask_data) {
        maskFeed.src = `data:image/jpeg;base64,${data.mask_data}`;
    }
    
    // Update frame count and FPS
    if (data.frame_count !== undefined) {
        frameCount.textContent = data.frame_count.toLocaleString();
    }
    
    if (data.fps !== undefined) {
        fpsDisplay.textContent = data.fps.toFixed(1);
    }
    
    // Update detections
    if (data.detections) {
        const count = data.detections.length;
        detectionCount.textContent = count;
        
        if (count > 0) {
            // Find best detection
            const best = data.detections.reduce((max, det) => 
                det.confidence > max.confidence ? det : max, data.detections[0]);
            bestDetection.textContent = `(${best.x}, ${best.y}) - ${(best.confidence * 100).toFixed(1)}%`;
            
            // Update detections list
            detectionsList.innerHTML = data.detections.map((det, idx) => `
                <div class="detection-item ${det === best ? 'best' : ''}">
                    <div class="detection-header">
                        <span class="detection-id">#${idx + 1}</span>
                        <span class="detection-confidence">${(det.confidence * 100).toFixed(1)}%</span>
                    </div>
                    <div class="detection-details">
                        Position: (${det.x}, ${det.y})
                    </div>
                </div>
            `).join('');
        } else {
            detectionsList.innerHTML = '<p class="no-data">No detections</p>';
            bestDetection.textContent = 'None';
        }
    }
    
    // Update configuration
    if (data.config) {
        configList.innerHTML = `
            <div class="config-item">
                <span class="config-label">Camera Index:</span>
                <span class="config-value">${data.config.camera_index}</span>
            </div>
            <div class="config-item">
                <span class="config-label">Frame Skip:</span>
                <span class="config-value">${data.config.frame_skip}</span>
            </div>
            <div class="config-item">
                <span class="config-label">Min Ball Area:</span>
                <span class="config-value">${data.config.min_ball_area}</span>
            </div>
            <div class="config-item">
                <span class="config-label">Max Ball Area:</span>
                <span class="config-value">${data.config.max_ball_area}</span>
            </div>
            <div class="config-item">
                <span class="config-label">Min Circularity:</span>
                <span class="config-value">${data.config.min_circularity}</span>
            </div>
            <div class="config-item">
                <span class="config-label">Color Lower (HSV):</span>
                <span class="config-value">[${data.config.color_lower.join(', ')}]</span>
            </div>
            <div class="config-item">
                <span class="config-label">Color Upper (HSV):</span>
                <span class="config-value">[${data.config.color_upper.join(', ')}]</span>
            </div>
        `;
    }
    
    // Calculate actual FPS
    const now = Date.now();
    const elapsed = (now - lastUpdateTime) / 1000;
    if (elapsed > 0) {
        const actualFps = 1 / elapsed;
        // You could display this separately if needed
    }
    lastUpdateTime = now;
}

// Initialize
updateConnectionStatus('disconnected');
