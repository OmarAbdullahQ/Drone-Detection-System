import cv2
import time

class VideoProcessor:
    """This class handles video input, frame capture, and FPS calculation"""
 
    def __init__(self, source=0, width=1280, height=800, name="Camera"):
        """Initializes the video source and configures capture settings"""
        self.name = name
        self.source = source 
        self.cap = cv2.VideoCapture(source)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.prev_time = 0
        self.fps = 0
    
    def read_frame(self):
        """Reading one frame from the camera or the video and updates the FPS"""
        ret, frame = self.cap.read()
        if ret:
            self._update_fps()
        return ret, frame
   
    def _update_fps(self):
        """calulate the time difference between two current and the previous frame"""
        curr_time = time.time()
        self.fps = 1 / (curr_time - self.prev_time) if self.prev_time != 0 else 0
        self.prev_time = curr_time

    def get_fps(self):
        """Returns the updated FPS value"""
        return self.fps
    
    def release(self):
        """Releasing the video capturing resource"""
        self.cap.release()
