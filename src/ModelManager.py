from ultralytics import YOLO
import torch 


class ModelManager:
    """
    Manages YOLO model loading, device selection, and inference execution
    """
    
    def __init__(self, model_path):  
     """
     The consturctor function for model manager and prepare the device for running the model
     """
     self.model_path = model_path
     self.device = self._device_selection()        
     self.model = self._load_model()
    
    def _device_selection(self):
        """
        Select the available device for comptation based on the user inpu
        t"""
        choice = input("Choose 1 for GPU or 2 for CPU: ")
        if choice == "1" and torch.cuda.is_available():
            print(f" GPU Enabled: {torch.cuda.get_device_name(0)}")
            return "cuda"
        else:
            print("Using CPU")
            return "cpu"
        
    def _load_model(self):
        """
        Load the model and pass it to the device
        """
        return YOLO(self.model_path).to(self.device)
    
    def predict(self, frame, imgsz=1080):
        """
        Run inference on a single frame using the model
        """
        return self.model(frame, imgsz=imgsz, device=self.device)
    
    def get_class_name(self, class_id):
        """
        Get class name from class ID
        """
        return self.model.names[class_id] 