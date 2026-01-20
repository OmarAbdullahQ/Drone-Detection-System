import cv2
import time
from DetectionLogger import DetectionLogger
from DroneDetector import DroneDetector
from ModelManager import ModelManager
from VideoProcessor import VideoProcessor
from DetectionVisualizer import DetectionVisualizer


# =========================
# USER CONFIG (Edit here)
# =========================

# Path to YOLO weights (.pt)
MODEL_PATH = "model/best.pt"

# Video source:
# - 0 / 1 / 2 ... for webcam index
# - "video.mp4" for a recorded video file
# - "rtsp://..." for IP camera stream
VIDEO_SOURCE = 0

# Capture resolution (may be ignored by some cameras/streams)
FRAME_WIDTH = 1280
FRAME_HEIGHT = 800

# Detection settings
CONFIDENCE_THRESHOLD = 0.60
INFERENCE_IMGSZ = 1080

# UI / Logging settings
WINDOW_NAME = "Drone Detection"
SAVE_EVERY_SECONDS = 1.0  # Log/save at most one detection every N seconds


class Main:
    """
    Entry point/controller for the drone detection pipeline.

    Flow:
      1) Read frames from a video source (webcam / mp4 / IP stream).
      2) Run inference using the model manager.
      3) Convert raw results to detections (bbox + confidence).
      4) Draw detections and show the live preview.
      5) Log detections to SQLite and save annotated frames.
    """

    def __init__(
        self,
        model_path=MODEL_PATH,
        source=VIDEO_SOURCE,
        width=FRAME_WIDTH,
        height=FRAME_HEIGHT,
        confidence_threshold=CONFIDENCE_THRESHOLD,
        imgsz=INFERENCE_IMGSZ,
        window_name=WINDOW_NAME,
        save_every_seconds=SAVE_EVERY_SECONDS,
    ):
        print("Starting the detection")

        # Store settings
        self.imgsz = imgsz
        self.window_name = window_name
        self.save_every_seconds = save_every_seconds
        self.last_save_time = 0.0

        # Init components
        self.model_manager = ModelManager(model_path)
        self.video_processor = VideoProcessor(source=source, width=width, height=height, name="Phone Camera")
        self.detector = DroneDetector(confidence_threshold=confidence_threshold)
        self.visualizer = DetectionVisualizer()

        # Init logging
        self.logger = DetectionLogger()
        self.logger.start_session()

        # Best-effort source typing for the DB
        source_type = "webcam" if isinstance(source, int) else "video/stream"
        self.logger.register_source(
            name=self.video_processor.name,
            source_type=source_type,
            source_value=self.video_processor.source
        )

        print("Detection started... Press Q to quit.")

    def run(self):
        """
        Main loop:
        - Reading frames 
        - Perform inference and visualization
        - logs the detections
        - break the loop if the user press 'q'
        """
        try:
            while True:
                ret, frame = self.video_processor.read_frame()
                if not ret:
                    print("No video input.")
                    break

                results = self.model_manager.predict(frame, imgsz=self.imgsz)
                detections = self.detector.extract_detections(results, self.model_manager)

                fps = self.video_processor.get_fps()
                annotated_frame = self.visualizer.annotate_frame(frame, fps, detections)
                self.visualizer.show_frame(annotated_frame, self.window_name)

                # DetectionLogger.log_detection() saves an image AND inserts a DB row.
                # Logging every detection in every frame will generate too many files quickly.
                now = time.time()
                if detections and (now - self.last_save_time) >= self.save_every_seconds:
                    # Save the best detection (highest confidence) in this time window.
                    best_det = max(detections, key=lambda d: d["confidence"])
                    self.logger.log_detection(annotated_frame, best_det)
                    self.last_save_time = now

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

        finally:
            self.cleanup()

    def cleanup(self):
        """
        Release resources, end the logging session, and close OpenCV windows.
        """
        self.logger.end_session()
        self.video_processor.release()
        cv2.destroyAllWindows()
        print("Cleanup complete")


if __name__ == "__main__":
    app = Main()
    app.run()
