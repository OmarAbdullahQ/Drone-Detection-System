import cv2

class DetectionVisualizer:
    """
    This class handles drawing detection result, and the perfomance information on the frame
    """

    def __init__(self):
        """
        The constructor function will set the colors for the drowing
        """
        self.box_color = (0, 255, 0)
        self.text_color = (0, 255, 0)
        self.fps_color = (0, 255, 255)

    def draw_fps(self, frame, fps):
        """
        Drawing the current FPS value on the frame
        """
        cv2.putText(frame, f"FPS: {fps:.2f}", (20, 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, self.fps_color, 2)
        
    def draw_detections(self, frame, detections):
        """
        drawing boxes around every detection
        """
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            conf = det['confidence']
            
            cv2.rectangle(frame, (x1, y1), (x2, y2), self.box_color, 3)

            label = f"Drone {conf*100:.1f}%"
            cv2.putText(frame, label, (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, self.text_color, 2)
            
    def annotate_frame(self, frame, fps, detections):
        """
        Combine all visual text into single frame
        """
        annotated = frame.copy()
        self.draw_fps(annotated, fps)
        self.draw_detections(annotated, detections)
        return annotated
    
    def show_frame(self, frame, window_name="Drone Detection"):
        """
        Display frame in window
        """
        cv2.imshow(window_name, frame) 