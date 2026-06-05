import torch
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv
import os

load_dotenv()


@dataclass
class Config:
    VIDEO_FPS: float = 2.0
    YOLO_SKIP_FRAMES: int = 10
    RESNET_SKIP_FRAMES: int = 20
    GEMINI_SKIP_FRAMES: int = 30

    DEVICE: str = "cuda" if torch.cuda.is_available() else "cpu"

    # PZ7
    LLM_MODEL: str = "openrouter/free"
    LLM_DELAY: float = 5.0
    LLM_MAX_FRAMES: int = 15
    LLM_SKIP_FRAMES: int = 90

    # Risk scoring
    DANGEROUS_CLASSES: set = frozenset({
        "knife", "gun", "weapon", "blood", "skull", "person",
        "nazi", "drugs", "alcohol", "cigarette"
    })
    YOLO_WEIGHT: float = 0.35
    LLM_WEIGHT: float = 0.45
    AUDIO_WEIGHT: float = 0.2

    TASK: str = "Много-модальный анализ видео на наличие деструктивного контента"

# Singleton
config = Config()

# Папки
Path("frames").mkdir(exist_ok=True)
Path("results").mkdir(exist_ok=True)
Path("logs").mkdir(exist_ok=True)
