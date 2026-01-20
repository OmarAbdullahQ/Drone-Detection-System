# Drone Detection System
Real-time drone detection from live streams or recorded videos (webcam / RTSP / MP4) using YOLOv8 and OpenCV, with SQLite-based logging and annotated frame saving.

## Project Idea (Brief)
This project detects drones in video input, draws bounding boxes with confidence scores and FPS, then stores detection events in a local SQLite database while saving annotated frames to disk for traceability and analysis.

## Key Features
- Video input support via OpenCV `VideoCapture` (webcam index, video file, or RTSP stream)
- YOLOv8 inference through a dedicated model manager (model loading, device selection, prediction)
- Drone-only filtering using class name `drone` with configurable confidence threshold
- Real-time visualization (bounding boxes, confidence score, FPS overlay)
- Local persistence using SQLite with saved annotated images

## Dataset & Local Training

### Dataset
- Type: Images (object detection)
- Size: ~1300 labeled images
- Class: `drone`
- Label format: YOLO `.txt` labels (normalized bounding boxes)

### Training Setup
Trained locally using **YOLOv8 Nano (YOLOv8n)**:
- Image size (imgsz): 640
- Device: CPU
- Epochs: 50
- Batch size: 16

### Output
- Final weights: `model/best.pt`

## Methods / Implementation (OOP)
The system is implemented using an object-oriented design to ensure modularity,
maintainability, and scalability. Each core responsibility is encapsulated in a
dedicated class as described below:

- `Main`: Pipeline controller (frame capture → inference → detection → visualization → logging)
- `ModelManager`: Loads YOLO weights, selects device (CPU/GPU), and runs inference
- `VideoProcessor`: Handles video capture and FPS calculation
- `DroneDetector`: Parses YOLO outputs and filters valid drone detections
- `DetectionVisualizer`: Draws bounding boxes, confidence scores, and FPS overlay
- `DetectionLogger`: Logs detection metadata to SQLite and saves annotated frames

## System Flow
1. Capture video frames from the selected source
2. Run YOLOv8 inference on each frame
3. Filter detections to keep only the `drone` class above the confidence threshold 
4. Draw bounding boxes, confidence scores, and FPS
5. Log detection metadata into SQLite
6. Save annotated frames to disk

 ## Technologies Used
- Python
- YOLOv8 (Ultralytics)
- PyTorch
- OpenCV
- NumPy
- SQLite (Relational Database Design)
- Computer Vision
- Object-Oriented Programming (OOP)

## Getting started
1) Create a virtual environment
`python -m venv venv`

2) Activate it:
`venv\Scripts\activate`

Linux/macOS
`source venv/bin/activate`

3) Install dependencies
`pip install -r requirements.txt`

4) Prepare the YOLO Model
The trained YOLOv8 model is already included in this repository
`model/best.pt`

5) Configuration
Before running the system, you can adjust the main configuration parameters in `Main.py` under the USER CONFIG section

Configuration Options:

- MODEL_PATH
Path to the YOLOv8 trained weights.

- VIDEO_SOURCE
Video input source:

0, 1, 2 → webcam index

"video.mp4" → video file

"rtsp://..." → IP camera stream

- FRAME_WIDTH / FRAME_HEIGHT
Desired capture resolution (may be ignored by some cameras or streams).

- CONFIDENCE_THRESHOLD
Minimum confidence score required to consider a detection valid.

- INFERENCE_IMGSZ
Image size used during YOLO inference (higher values may improve accuracy at the cost of speed).

- SAVE_EVERY_SECONDS
Limits how often detections are logged and images are saved to disk

6) Run the System
From the project root director
`python src/Main.py`

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

Stores metadata about each application run (session), allowing detections to be grouped and analyzed per execution.

Fields:
- `id` – Unique session identifier
- `start_time` – Timestamp indicating when the detection session started
- `end_time` – Timestamp indicating when the detection session ended

### Sources Table

<img width="1361" height="802" alt="image" src="https://github.com/user-attachments/assets/06c1f6f5-623e-493e-a526-c7a0a83f886f" />

Stores metadata describing the video input source used during a detection session.

Fields:
- `id` – Unique source identifier
- `name` – Human-readable source name (e.g., Webcam, IP Camera)
- `type` – Source type (`webcam`, `video`, or `stream`)
- `value` – Source value such as webcam index, video file path, or RTSP URL

### Detections Table

<img width="1344" height="800" alt="image" src="https://github.com/user-attachments/assets/cb6826fc-2657-4f4e-9a92-0fd6da738dae" />

Stores individual drone detection events along with spatial and confidence metadata.

Fields:
- `id` – Unique detection identifier
- `session_id` – Foreign key referencing the session in which the detection occurred
- `source_id` – Foreign key referencing the video source
- `timestamp` – Detection timestamp
- `confidence` – Model confidence score for the detected object
- `x1` – Top-left X coordinate of the bounding box (in pixels)
- `y1` – Top-left Y coordinate of the bounding box (in pixels)
- `x2` – Bottom-right X coordinate of the bounding box (in pixels)
- `y2` – Bottom-right Y coordinate of the bounding box (in pixels)
- `label` – Detected object class label (e.g., `drone`)
- `image_path` – Absolute path to the saved annotated frame

### Why Database Logging?

- Enables structured analysis of detection events
- Allows linking visual evidence (images) with metadata
- Makes the system suitable for auditing and future scaling
- Simplifies integration with dashboards or cloud databases

## Results

The system successfully performs real-time drone detection on live and recorded
video streams using YOLOv8.

Key observed results:
- Accurate detection of drones in various scenes and lighting conditions
- Stable real-time performance on GPU and CPU with FPS displayed on each frame
- Reliable logging of detection events into the SQLite database
- Correct saving of annotated frames linked to each detection record
- Clear spatial localization using bounding boxes (x1, y1, x2, y2)

The logged detection data enables further offline analysis, performance evaluation,
and future integration with monitoring dashboards or cloud-based systems.

 ## Future Improvements
- Cloud-based logging (AWS / Firebase)
- REST API for detection events
- Web dashboard for detection analytics
- Multi-class detection support







