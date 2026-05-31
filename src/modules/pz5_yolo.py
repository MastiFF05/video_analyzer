from ultralytics import YOLO
import cv2
import json
from pathlib import Path


def run_yolo_detection(input_folder="frames"):
    model = YOLO('../yolov8n.pt')
    results_dict = {}
    frames = sorted(Path(input_folder).glob("*.jpg"))

    for i, frame_path in enumerate(frames):
        if i % 10 != 0:          # YOLO_SKIP_FRAMES
            continue

        img = cv2.imread(str(frame_path))
        if img is None:
            continue

        res = model.track(img, persist=True, verbose=False)[0]

        frame_objects = []
        for box in res.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            name = model.names[cls_id]

            frame_objects.append({
                "class": name,
                "confidence": round(conf, 3),
                "bbox": [int(x) for x in box.xyxy[0].tolist()]
            })

        if frame_objects:
            results_dict[frame_path.name] = frame_objects

    with open("../pz5_yolo_detections.json", "w", encoding="utf-8") as f:
        json.dump(results_dict, f, ensure_ascii=False, indent=2)

    print(f"   YOLO: обнаружено объектов на {len(results_dict)} кадрах")
    return results_dict
