import json
import base64
import time
from pathlib import Path
from openai import OpenAI

class QwenAnalyzer:
    def __init__(self):
        self.api_key = "YOUR_OPENROUTER_KEY"
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
            timeout=60.0,
            max_retries=1,
        )
        self.model = "openrouter/free"

    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def analyze_one_frame(self, frame_path, prompt):
        base64_image = self.encode_image(frame_path)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ],
            max_tokens=250,
            temperature=0.2
        )
        return response.choices[0].message.content.strip()

    def analyze_key_frames(self, frames_folder="frames", skip=90, max_frames=15, delay=5):
        frames = sorted(Path(frames_folder).glob("*.jpg"))
        results = {}

        prompt = (
            "Проанализируй кадр на наличие деструктивного контента: "
            "оружие, кровь, насилие, ненавистнические символы, "
            "наркотики, алкоголь, порнография, экстремизм. "
            "Ответь только: 'Есть: ...' или 'Нет'."
        )

        selected = frames[::skip][:max_frames]

        for frame_path in selected:
            try:
                text = self.analyze_one_frame(frame_path, prompt)
                results[frame_path.name] = {
                    "model": self.model,
                    "result": text
                }
                print(f"{frame_path.name}: {text[:60]}...")
            except Exception as e:
                msg = str(e)
                results[frame_path.name] = {
                    "model": None,
                    "result": f"Ошибка: {msg[:200]}"
                }
                print(f"{frame_path.name} → ошибка")

            time.sleep(delay)

        output_path = Path("pz7_qwen_results.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print(f"\n   Анализ завершен: {len(results)} ключевых кадров")
        print(f"   Результаты сохранены в {output_path}")
        return results
