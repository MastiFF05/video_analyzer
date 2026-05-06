import cv2
import numpy as np
import easyocr

class ImageProcessor:
    def __init__(self):
        self.ocr = easyocr.Reader(['ru','en'], gpu=False)
    
    def preprocess_meter(self, img_path):
        """Предобработка для счетчиков"""
        img = cv2.imread(img_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
      
        blurred = cv2.medianBlur(gray, 5)
        binary = cv2.adaptiveThreshold(blurred, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
        
        # Морфология для очистки
        kernel = np.ones((2,2), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        return binary
    
    def extract_number(self, processed_img):
        results = self.ocr.readtext(processed_img)
        for (_, text, _) in results:
            digits = ''.join(c for c in text if c.isdigit())
            if len(digits) >= 6:
                return digits[:6]
        return None
