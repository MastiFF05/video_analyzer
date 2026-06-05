import json
import base64
import time
import os
from pathlib import Path
from openai import OpenAI
from src.config import config
from src.utils.logging import setup_logging

logger = setup_logging()


class QwenAnalyzer:
    def __init__(self):
        # ВСТАВЬТЕ СВОЙ КЛЮЧ ЗДЕСЬ ↓↓↓
        self.api_key = "sk-or-..."  # ← Замените на свой настоящий ключ OpenRouter

        if not self.api_key or self.api_key == "sk-or-...":
            logger.warning("Вы не вставили OPENROUTER_KEY! Анализ PZ7 работать не будет.")

        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
            timeout=90.0,
        )
        self.model = config.LLM_MODEL  # "openrouter/free"

    def encode_image(self, image_path: str) -> str:
        """Кодирует изображение в base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def analyze_one_frame(self, frame_path: Path, prompt: str):
        """Анализирует один кадр через LLM"""
        base64_image = self.encode_image(str(frame_path))

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                    },
                    {"type": "text", "text": prompt}
                ]
            }],
            max_tokens=300,
            temperature=0.2
        )
        return response.choices[0].message.content.strip()

    def analyze_key_frames(self, frames_folder="frames", skip=90, max_frames=15, delay=5):
        """Анализ ключевых кадров"""
        frames = sorted(Path(frames_folder).glob("*.jpg"))
        results = {}

        prompt = (
            "Проанализируй кадр на наличие деструктивного контента: "
            "оружие, кровь, насилие, ненавистнические символы, наркотики, "
            "алкоголь, порнография, экстремизм, ЛГБТ. "
            "Ответь только: 'Есть: ...' или 'Нет'."
        )

        selected_frames = frames[::skip][:max_frames]

        logger.info(f"Начинаем анализ {len(selected_frames)} ключевых кадров...")

        for i, frame_path in enumerate(selected_frames):
            try:
                text = self.analyze_one_frame(frame_path, prompt)
                results[frame_path.name] = {
                    "model": self.model,
                    "result": text
                }
                logger.info(f"[{i + 1}/{len(selected_frames)}] {frame_path.name}: {text[:70]}...")
            except Exception as e:
                logger.error(f"Ошибка при анализе {frame_path.name}: {e}")
                results[frame_path.name] = {
                    "model": None,
                    "result": f"Ошибка: {str(e)[:200]}"
                }

            time.sleep(delay)  # задержка между запросами

        # Сохраняем результаты
        output_path = Path("pz7_qwen_results.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        logger.info(f"PZ7 завершён. Проанализировано {len(results)} кадров.")
        return results
