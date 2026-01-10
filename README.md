# Golf Ball Tracker

A golf ball tracking compass system that helps golfers locate their ball after hitting it. The system uses computer vision to track golf ball trajectories and provides directional guidance via a web interface.

## Features

- Real-time golf ball detection and tracking
- Trajectory prediction for errant shots
- Web-based compass interface
- Works on Mac (prototyping) and Raspberry Pi (production)

## Setup

### Mac (Development)

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Copy environment configuration:
```bash
cp .env.example .env
```

3. Adjust `.env` settings if needed (camera index, thresholds, etc.)

4. Run the application:
```bash
python src/main.py
```

5. Open your browser to `http://localhost:5000`

### Raspberry Pi

1. Install system dependencies:
```bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-opencv libopencv-dev
```

2. Install Python dependencies:
```bash
pip3 install -r requirements.txt
```

3. Configure `.env` for Raspberry Pi camera:
```bash
CAMERA_INDEX=0  # or use /dev/video0
```

4. Run the application:
```bash
python3 src/main.py
```

5. Access from your phone/tablet at `http://<raspberry-pi-ip>:5000`

## Project Structure

```
golfeye/
├── src/
│   ├── detection/      # Ball detection modules
│   ├── tracking/       # Ball tracking and trajectory prediction
│   ├── compass/        # Direction calculation
│   ├── web/            # Web server and frontend
│   ├── camera/         # Camera abstraction
│   └── main.py         # Main application entry point
├── models/             # ML models (optional)
├── tests/              # Unit and integration tests
└── requirements.txt    # Python dependencies
```

## Configuration

See `.env.example` for all configuration options. Key settings:

- `CAMERA_INDEX`: Camera device index (0 for default)
- `FRAME_SKIP`: Process every Nth frame (higher = better performance)
- `LAUNCH_VELOCITY_THRESHOLD`: Minimum velocity to detect ball launch
- `WEB_PORT`: Web server port

## Usage

1. Position the camera on your golf cart to view the golfer
2. Start the application
3. Open the web interface on your phone/tablet
4. Hit your golf ball
5. The compass will guide you to the predicted landing location

## Development

The system uses a hybrid detection approach:
1. Color-based detection (fast, good for white balls)
2. ML verification (optional, more accurate)
3. Kalman filtering for smooth tracking
4. Physics-based trajectory prediction

## License

MIT
