from pathlib import Path

import cv2
import numpy as np
import easyocr


class ImageProcessor:
    def __init__(self):
        self.reader = easyocr.Reader(['ru', 'en'], gpu=False)

    def preprocess_for_ocr(self, img):
        """Улучшенная предобработка для OCR (субтитры + текст)"""
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img

        # CLAHE + медианный фильтр
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        contrasted = clahe.apply(gray)
        blurred = cv2.medianBlur(contrasted, 3)

        # Бинаризация
        binary = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 15, 3)

        # Морфология
        kernel = np.ones((2, 2), np.uint8)
        processed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

        return processed

    def batch_preprocess(self, input_folder="frames", output_folder="pz1_preprocessed"):
        """Пакетная предобработка всех кадров"""
        Path(output_folder).mkdir(exist_ok=True)
        for img_path in Path(input_folder).glob("*.jpg"):
            img = cv2.imread(str(img_path))
            if img is None:
                continue
            processed = self.preprocess_for_ocr(img)
            cv2.imwrite(str(Path(output_folder) / img_path.name), processed)
