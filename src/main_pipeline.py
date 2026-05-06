from pz1_image_processing import ImageProcessor
from pz2_video_frames import VideoDownloader, FrameExtractor
# ... импорты всех ПЗ

def analyze_video(source, quality='1080p', output_dir='analysis'):
    pipeline = {
        'frames': [], 'texts': [], 'objects_yolo': [],
        'objects_resnet': [], 'gemini': [], 'audio': []
    }
    
    # 1-2. Скачать + нарезать
    video_path = VideoDownloader().download(source, quality)
    frames_dir = FrameExtractor().extract(video_path, fps=2)
    
    # 3-7. Анализ каждого кадра
    processor = ImageProcessor()
    yolo = YOLODetector()
    for frame in Path(frames_dir).glob('*.jpg'):
        # OCR
        binary = processor.preprocess_meter(frame)
        number = processor.extract_number(binary)
        if number: pipeline['texts'].append(number)
        
        # YOLO + ResNet + Gemini
        pipeline['objects_yolo'].extend(yolo.detect_frame(frame))
    
    # 4. Аудио
    pipeline['audio'] = AudioProcessor().transcribe_video(video_path)
    
    # 8. Постобработка
    pipeline['texts'] = deduplicate_texts(pipeline['texts'])
    
    # Отчет
    generate_report(pipeline, output_dir)
    return pipeline

if __name__ == "__main__":
    analyze_video("https://rutube.ru/video/demo", "720p")
