from ultralytics import YOLO

class YOLODetector:
    def __init__(self):
        self.model = YOLO('yolov8n.pt')
    
    def detect_frame(self, frame_path):
        results = self.model(frame_path)
        detections = []
        for r in results:
            boxes = r.boxes
            for box in boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                if conf > 0.5:
                    detections.append({
                        'class': self.model.names[cls],
                        'conf': conf,
                        'bbox': box.xyxy[0].tolist()
                    })
        return detections
