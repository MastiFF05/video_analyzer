import yt_dlp
import cv2
import os
from pathlib import Path

class VideoDownloader:
    QUALITY_MAP = {
        'best': 'bestvideo+bestaudio/best',
        '1080p': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
        '720p': 'bestvideo[height<=720]+bestaudio/best[height<=720]'
    }
    
    def download(self, url, quality='1080p', output_dir='downloads'):
        ydl_opts = {
            'format': self.QUALITY_MAP[quality],
            'outtmpl': f'{output_dir}/%(title)s.%(ext)s'
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            return ydl.prepare_filename(ydl.extract_info(url, download=False))

class FrameExtractor:
    def extract(self, video_path, fps=2, output_dir='frames'):
        cap = cv2.VideoCapture(video_path)
        os.makedirs(output_dir, exist_ok=True)
        
        frame_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            
            if frame_count % int(cap.get(cv2.CAP_PROP_FPS)/fps) == 0:
                cv2.imwrite(f'{output_dir}/frame_{frame_count:06d}.jpg', frame)
            
            frame_count += 1
        
        cap.release()
        print(f"Извлечено {len(os.listdir(output_dir))} кадров")
