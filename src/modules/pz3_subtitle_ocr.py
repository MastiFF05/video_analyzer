import cv2
import easyocr
import json
from pathlib import Path
from src.modules.pz1_ocr_preprocessor import ImageProcessor
from src.utils.logging import setup_logging

logger = setup_logging()

def run_subtitle_analysis():
    logger.info("   Предобработка кадров для OCR...")
    processor = ImageProcessor()
    processor.batch_preprocess()

    reader = easyocr.Reader(['ru', 'en'], gpu=False)
    results = {}
    frames = sorted(Path("pz1_preprocessed").glob("*.jpg")) or sorted(Path("../frames").glob("*.jpg"))

    for i, frame_path in enumerate(frames):
        if i % 5 != 0:          # пропускаем часть кадров
            continue
        img = cv2.imread(str(frame_path))
        if img is None:
            continue

        # Вырезаем нижнюю часть (типичное место субтитров)
        h, w = img.shape[:2]
        roi = img[int(h * 0.72):, :]

        processed = processor.preprocess_for_ocr(roi)
        text_list = reader.readtext(
            processed,
            detail=0,
            paragraph=True,
            text_threshold=0.4,
            low_text=0.3
        )

        if text_list:
            text = " ".join(text_list).strip()
            results[frame_path.name] = text

    with open("../pz3_text_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    logger.info(f"   Распознано уникальных фрагментов: {len(set(results.values()))}")
