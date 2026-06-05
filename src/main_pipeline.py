import json
from pathlib import Path
from src.utils.logging import setup_logging
from src.modules.pz2_frame_extractor import VideoDownloader, FrameExtractor
from src.modules.pz3_subtitle_ocr import run_subtitle_analysis
from src.modules.pz4_whisper_transcriber import extract_audio_and_transcribe
from src.modules.pz5_yolo import run_yolo_detection
from src.modules.pz6_resnet import classify_frames_resnet
from src.modules.pz7_llm_analyzer import QwenAnalyzer
from src.modules.pz8_multimodal_analyzer import postprocess_all
from src.utils.report import generate_final_report
from config import config

logger = setup_logging()

def run_pipeline(video_path, fps=None, skip_frames=None, max_frames=None, delay=None):
    video_path = Path(video_path)
    logger.info(f"Запуск анализа: {video_path.name}")

    fps = fps or config.VIDEO_FPS
    skip_frames = skip_frames or config.LLM_SKIP_FRAMES
    max_frames = max_frames or config.LLM_MAX_FRAMES
    delay = delay or config.LLM_DELAY

    # PZ2
    FrameExtractor().extract(str(video_path), output_folder="frames", fps=fps)

    # PZ3
    logger.info("PZ3 → OCR субтитров...")
    run_subtitle_analysis()

    # PZ4
    logger.info("PZ4 → Whisper транскрипция...")
    audio_result = extract_audio_and_transcribe(str(video_path))

    # PZ5
    logger.info("PZ5 → YOLOv8...")
    yolo_data = run_yolo_detection("frames")

    # PZ6
    logger.info("PZ6 → ResNet50...")
    resnet_data = classify_frames_resnet("frames")

    # PZ7
    logger.info("PZ7 → LLM анализ...")
    analyzer = QwenAnalyzer()
    qwen_results = analyzer.analyze_key_frames(
        frames_folder="frames",
        skip=skip_frames,
        max_frames=max_frames,
        delay=delay
    )

    # PZ8
    logger.info("PZ8 → Постобработка...")
    final_results = postprocess_all(yolo_data, resnet_data, audio_result, qwen_results)

    report = generate_final_report(video_path, final_results)
    logger.info(f"Анализ завершён. Risk level: {report['risk_level']}")
    return report
