"This class will process the yolo detection result and extract the drone only based on the confidence"
class DroneDetector:
    
    def __init__(self, confidence_threshold=0.60):
        "The constructor function for the object and set the threshold value"
        self.confidence_threshold = confidence_threshold
    
    def extract_detections(self, results, model_manager):
        """Extract drone detections above confidence threshold"""
        detections = []
        
        for box in results[0].boxes:
            cls_id = int(box.cls[0])
            cls_name = model_manager.get_class_name(cls_id)
            conf = float(box.conf[0])
            
            if cls_name == "drone" and conf >= self.confidence_threshold:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                detections.append({
                    'class_name': cls_name,
                    'confidence': conf,
                    'bbox': (x1, y1, x2, y2)
                     })
        
        return detections