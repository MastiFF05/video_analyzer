import cv2
import torch
from torchvision.models import resnet50, ResNet50_Weights
from pathlib import Path
import json
from PIL import Image
from collections import Counter


def classify_frames_resnet(input_folder="frames", output_data="pz6_resnet_classes.json"):
    weights = ResNet50_Weights.IMAGENET1K_V1
    model = resnet50(weights=weights)
    model.eval()
    preprocess = weights.transforms()

    results = {}
    frames = sorted(Path(input_folder).glob("*.jpg"))

    for i, frame_path in enumerate(frames):
        if i % 15 != 0:
            continue

        img = cv2.imread(str(frame_path))
        if img is None:
            continue

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(img_rgb)
        batch = preprocess(pil_image).unsqueeze(0)

        with torch.no_grad():
            prediction = model(batch).squeeze(0).softmax(0)
            class_id = prediction.argmax().item()
            score = prediction[class_id].item()
            category_name = weights.meta["categories"][class_id]

        results[str(frame_path.name)] = {
            "class": category_name,
            "score": round(score, 3)
        }

    with open(output_data, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    classes_counter = Counter(item['class'] for item in results.values())
    print("ТОП-10 обнаруженных классов:")
    for cls, count in classes_counter.most_common(10):
        print(f"{cls}: {count}")
