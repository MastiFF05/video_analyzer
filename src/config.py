import torch
from pathlib import Path

# Параметры обработки
VIDEO_FPS = 1.0
YOLO_SKIP_FRAMES = 10
RESNET_SKIP_FRAMES = 20
GEMINI_SKIP_FRAMES = 30

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Прикладная задача
TASK = "Много-модальный анализ видео на наличие деструктивного контента"

Path("frames").mkdir(exist_ok=True)
Path("results").mkdir(exist_ok=True)
