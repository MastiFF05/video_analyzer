import json
from pathlib import Path

from src.modules.pz2_frame_extractor import VideoDownloader, FrameExtractor
from src.modules.pz3_subtitle_ocr import run_subtitle_analysis
from src.modules.pz4_whisper_transcriber import extract_audio_and_transcribe
from src.modules.pz5_yolo import run_yolo_detection
from src.modules.pz6_resnet import classify_frames_resnet
from src.modules.pz7_llm_analyzer import QwenAnalyzer
from src.modules.pz8_multimodal_analyzer import postprocess_all
from src.utils.report import generate_final_report


def run_pipeline(video_path, fps=2.0, skip_frames=90, max_frames=15, delay=5):
    video_path = Path(video_path)
    print(f"Видео: {video_path.name}")

    FrameExtractor().extract(str(video_path), output_folder="frames", fps=fps)

    print("PZ3 → Распознавание текста (субтитры)...")
    run_subtitle_analysis()

    print("PZ4 → Whisper транскрипция аудио...")
    audio_result = extract_audio_and_transcribe(str(video_path))

    print("PZ5 → YOLOv8 детекция объектов...")
    yolo_data = run_yolo_detection("frames")

    print("PZ6 → ResNet50 классификация...")
    resnet_data = classify_frames_resnet("frames")

    print("PZ7 → LLM (анализ деструктивного контента)...")
    analyzer = QwenAnalyzer()
    qwen_results = analyzer.analyze_key_frames(
        frames_folder="frames",
        skip=skip_frames,
        max_frames=max_frames,
        delay=delay
    )

    print("PZ8 → Постобработка и risk-scoring...")
    final_results = postprocess_all(yolo_data, resnet_data, audio_result, qwen_results)

    report = generate_final_report(video_path, final_results)

    return report
