from paddleocr import PaddleOCR

class OCRProcessor:
    def __init__(self):
        self.ocr = PaddleOCR(use_angle_cls=True, lang='ru')
    
    def recognize_frames(self, frames_dir):
        texts = []
        for frame_path in Path(frames_dir).glob('*.jpg'):
            result = self.ocr.ocr(frame_path, cls=True)
            for line in result[0]:
                text, conf = line[1][0], line[1][1]
                if conf > 0.7:  # Только уверенные
                    texts.append({'frame': frame_path.name, 'text': text, 'conf': conf})
        return texts
