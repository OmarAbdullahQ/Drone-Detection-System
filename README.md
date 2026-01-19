# Drone-Detection-System
Real-time drone detection from live streams or recorded videos (webcam/RTSP/MP4) using YOLO + OpenCV, with SQLite logging and annotated frame saving. [file:18

## Project Idea (Brief)
This project detects drones in video input, draws bounding boxes with confidence and FPS, then stores detection events in a local SQLite database and saves annotated frames to disk.

## Key Features
- Video input support via OpenCV `VideoCapture` (webcam index, video file, or RTSP stream). 
- YOLO inference through a dedicated model manager (model loading + device selection + prediction). 
- Drone-only filtering using class name `drone` + confidence threshold. 
- Live visualization (bounding boxes + confidence + FPS overlay). 
- Local persistence: SQLite tables + saved annotated images. 

## Dataset & Local Training
### Dataset
- Type: Images (object detection).
- Size: ~1300 labeled images.
- Class: `drone`.
- Label format: YOLO txt labels (one `.txt` per image, each row uses normalized bbox fields).

### Training Setup
Trained locally using **YOLOv8 Nano (YOLOv8n)** with:
- Image size (imgsz): 640. 
- Device: CPU. 
- Epochs: 50. 
- Batch size: 16. 

### Output
- Final weights: `model/best.pt`

## Methods / Implementation (OOP)
The code is structured using an OOP modular design, where each responsibility is isolated in a class:
- `Main`: pipeline controller (read frames → inference → detections → visualize → log). 
- `ModelManager`: loads YOLO weights, selects device (CPU/GPU), and runs inference. 
- `VideoProcessor`: handles video capture and FPS calculation. 
- `DroneDetector`: parses YOLO results and extracts drone detections above a threshold. 
- `DetectionVisualizer`: draws FPS + bounding boxes + confidence on frames. 
- `DetectionLogger`: logs to SQLite and saves annotated frames (images) on disk.

## Project Structure
drone-detection-system/
  README.md
  .gitignore
  requirements.txt
  src/
    Main.py
    ModelManager.py
    VideoProcessor.py
    DroneDetector.py
    DetectionVisualizer.py
    DetectionLogger.py
  model/
    best.pt

## Getting started
1) Create a virtual environment
python -m venv venv

2) Activate it:
venv\Scripts\activate

Linux/macOS
source venv/bin/activate

3) Install dependencies
pip install -r requirements.txt

4) Prepare the YOLO Model
The trained YOLOv8 model is already included in this repository
model/best.pt

5) Configuration
Before running the system, you can adjust the main configuration parameters in Main.py under the USER CONFIG section

Configuration Options:

MODEL_PATH
Path to the YOLOv8 trained weights.

VIDEO_SOURCE
Video input source:

0, 1, 2 → webcam index

"video.mp4" → video file

"rtsp://..." → IP camera stream

FRAME_WIDTH / FRAME_HEIGHT
Desired capture resolution (may be ignored by some cameras or streams).

CONFIDENCE_THRESHOLD
Minimum confidence score required to consider a detection valid.

INFERENCE_IMGSZ
Image size used during YOLO inference (higher values may improve accuracy at the cost of speed).

SAVE_EVERY_SECONDS
Limits how often detections are logged and images are saved to disk

6) Run the System
From the project root director
python src/Main.py

## Detection examples
Below are sample outputs showing real-time drone detection with bounding boxes,
confidence scores, and FPS overlay.

![Detection_1](https://github.com/user-attachments/assets/7fca71cd-8d3f-4c31-943f-39d1dc6e7adb)


![Detection_2](https://github.com/user-attachments/assets/773b52e5-b810-4ec5-abf5-f4697cf1e212)

## Logging the Detections (Database)

All detection events are persistently stored in a local SQLite database to enable
traceability, analysis, and future integration with external systems.

The database is created automatically on the first run of the application.

### Database Overview

The database consists of multiple normalized tables to organize detection data
by session, source, and detection event.

### Sessions Table

<img width="1366" height="808" alt="image" src="https://github.com/user-attachments/assets/c5d27972-30b0-4512-b05f-4ec06c64ecd5" />

Stores information about each application run.

Fields:
- id – Unique session identifier
- start_time – Session start timestamp
- end_time – Session end timestamp

### Sources Table

<img width="1361" height="802" alt="image" src="https://github.com/user-attachments/assets/06c1f6f5-623e-493e-a526-c7a0a83f886f" />

Stores metadata about the video input source.

Fields:
- id – Source identifier
- name – Source name (e.g., Webcam, IP Camera)
- type – Source type (webcam / video / stream)
- value – Source index or stream URL

### Detections Table

<img width="1344" height="800" alt="image" src="https://github.com/user-attachments/assets/cb6826fc-2657-4f4e-9a92-0fd6da738dae" />

Stores individual drone detection events.

Fields:
- id – Detection ID
- session_id – Linked session reference
- source_id – Source reference
- timestamp – Detection time
- confidence – Detection confidence score
- image_path – Path to the saved annotated frame

### Why Database Logging?

- Enables structured analysis of detection events
- Allows linking visual evidence (images) with metadata
- Makes the system suitable for auditing and future scaling
- Simplifies integration with dashboards or cloud databases






