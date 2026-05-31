import pywhisper
from moviepy.editor import VideoFileClip
import json
import os
import re

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

def extract_audio_and_transcribe(video_path, audio_path="temp_audio.wav", output_json="pz4_transcription.json"):
    if not os.path.exists(audio_path):
        video = VideoFileClip(video_path)
        video.audio.write_audiofile(audio_path, codec='pcm_s16le', verbose=False, logger=None)

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

        if repeat_count >= 2:
            continue
        if key in seen:
            continue

        seen.add(key)
        segments.append({
            "start": seg.get("start"),
            "end": seg.get("end"),
            "text": text
        })

    output = {
        "text": " ".join(item["text"] for item in segments),
        "segments": segments
    }

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(output["text"])
    return output
