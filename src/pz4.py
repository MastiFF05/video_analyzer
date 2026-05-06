import whisper
from moviepy.editor import VideoFileClip

class AudioProcessor:
    def transcribe_video(self, video_path):
        # Извлекаем аудио
        video = VideoFileClip(video_path)
        audio_path = video_path.replace('.mp4', '_audio.wav')
        video.audio.write_audiofile(audio_path)
        video.close()
        
        # Whisper
        model = whisper.load_model("large-v3")
        result = model.transcribe(audio_path, language='ru')
        return result['segments']
