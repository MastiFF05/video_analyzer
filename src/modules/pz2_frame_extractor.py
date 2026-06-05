import yt_dlp
import cv2
import os
from src.utils.logging import setup_logging

logger = setup_logging()

class VideoDownloader:
    QUALITY_MAP = {
        'best': 'best',
        '720p': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
        '1080p': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]'
    }

    def download(self, url, quality='1080p', output_dir='downloads'):
        os.makedirs(output_dir, exist_ok=True)
        ydl_opts = {
            'format': self.QUALITY_MAP.get(quality, 'best'),
            'outtmpl': f'{output_dir}/%(title)s.%(ext)s'
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return ydl.prepare_filename(info)


class FrameExtractor:
    def extract(self, video_source, output_folder='frames', fps=1):
        os.makedirs(output_folder, exist_ok=True)
        cap = cv2.VideoCapture(video_source)

        if not cap.isOpened():
            logger.info(f'Ошибка: не удалось открыть источник {video_source}')
            return

        video_fps = cap.get(cv2.CAP_PROP_FPS)
        if video_fps <= 0:
            video_fps = 30.0

        frame_interval = 1 if fps >= video_fps else int(video_fps / fps)
        frame_count = 0
        saved_count = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % frame_interval == 0:
                frame_path = os.path.join(output_folder, f'frame_{saved_count:05d}.jpg')
                cv2.imwrite(frame_path, frame)
                saved_count += 1

            frame_count += 1

        cap.release()
        print('Сохранено кадров:', saved_count)
