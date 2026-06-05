import pywhisper
from moviepy.editor import VideoFileClip
import json
import os
import re
from pathlib import Path
from src.utils.logging import setup_logging

logger = setup_logging()


def clean_text(text):
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    return text


def is_valid_text(text):
    t = text.strip()
    if len(t) < 4:
        return False
    if len(re.sub(r'[^a-zA-Zа-яА-Я0-9 ]', '', t)) < 4:
        return False
    bad = {"we", "i", "ok", "yes", "no", "bye", "на", "и", "я"}
    if t.lower() in bad:
        return False
    return True


def extract_audio_and_transcribe(video_path):
    video_path = Path(video_path)
    video_name = video_path.stem

    # Делаем уникальное имя для каждого видео
    audio_path = f"temp_audio_{video_name}.wav"
    output_json = f"pz4_transcription_{video_name}.json"

    try:
        if not os.path.exists(audio_path):
            logger.info(f"Извлечение аудио из {video_path.name}...")
            video = VideoFileClip(str(video_path))
            video.audio.write_audiofile(audio_path, codec='pcm_s16le', verbose=False, logger=None)
            video.close()

        logger.info("Запуск Whisper транскрипции...")
        model = pywhisper.load_model("small")
        result = model.transcribe(audio_path, language='ru', verbose=False)

        segments = []
        seen = set()
        prev_text = None
        repeat_count = 0

        for seg in result.get("segments", []):
            text = clean_text(seg.get("text", ""))
            if not is_valid_text(text):
                continue

            key = text.lower()
            if key == prev_text:
                repeat_count += 1
            else:
                repeat_count = 0
            prev_text = key

            if repeat_count >= 2 or key in seen:
                continue

            seen.add(key)
            segments.append({
                "start": round(seg.get("start"), 2),
                "end": round(seg.get("end"), 2),
                "text": text
            })

        full_text = " ".join(item["text"] for item in segments)

        output = {
            "video_name": video_name,
            "text": full_text,
            "segments": segments,
            "segments_count": len(segments)
        }

        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        logger.info(f"PZ4 завершён. Распознано сегментов: {len(segments)}")
        return output

    except Exception as e:
        logger.error(f"Ошибка в PZ4: {e}")
        return {"text": "", "segments": [], "error": str(e)}
