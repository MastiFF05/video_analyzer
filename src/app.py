import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import subprocess
import os
import sys
from pathlib import Path

from src.main_pipeline import run_pipeline
from src.modules.pz2_frame_extractor import VideoDownloader


class VideoAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Analyzer")
        self.root.geometry("980x720")
        self.root.minsize(850, 600)

        self.mode = tk.StringVar(value="local")
        self.video_path = tk.StringVar()
        self.rutube_url = tk.StringVar()
        self.fps = tk.StringVar(value="2")
        self.skip_frames = tk.StringVar(value="90")
        self.max_frames = tk.StringVar(value="15")
        self.delay = tk.StringVar(value="5")
        self.status = tk.StringVar(value="Готов к запуску")

        self.build_ui()

    def build_ui(self):
        main = ttk.Frame(self.root, padding=12)
        main.pack(fill="both", expand=True)

        ttk.Label(main, text="Video Analyzer", font=("Arial", 16, "bold")).pack(anchor="w", pady=(0, 10))

        mode_frame = ttk.LabelFrame(main, text="Режим")
        mode_frame.pack(fill="x", pady=8)

        ttk.Radiobutton(mode_frame, text="Локальный файл", variable=self.mode, value="local", command=self.refresh_mode).pack(anchor="w", padx=8, pady=4)
        ttk.Radiobutton(mode_frame, text="Rutube URL", variable=self.mode, value="rutube", command=self.refresh_mode).pack(anchor="w", padx=8, pady=4)

        self.local_frame = ttk.LabelFrame(main, text="Локальный видеофайл")
        self.local_frame.pack(fill="x", pady=8)

        ttk.Entry(self.local_frame, textvariable=self.video_path).pack(side="left", fill="x", expand=True, padx=8, pady=8)
        ttk.Button(self.local_frame, text="Выбрать файл", command=self.choose_file).pack(side="left", padx=8, pady=8)

        self.rutube_frame = ttk.LabelFrame(main, text="Rutube URL")
        self.rutube_frame.pack(fill="x", pady=8)

        ttk.Entry(self.rutube_frame, textvariable=self.rutube_url).pack(side="left", fill="x", expand=True, padx=8, pady=8)

        params = ttk.LabelFrame(main, text="Параметры")
        params.pack(fill="x", pady=8)

        row1 = ttk.Frame(params)
        row1.pack(fill="x", padx=8, pady=4)

        ttk.Label(row1, text="FPS:").pack(side="left")
        ttk.Entry(row1, textvariable=self.fps, width=8).pack(side="left", padx=(6, 18))

        ttk.Label(row1, text="Skip frames PZ7:").pack(side="left")
        ttk.Entry(row1, textvariable=self.skip_frames, width=8).pack(side="left", padx=(6, 18))

        ttk.Label(row1, text="Max frames PZ7:").pack(side="left")
        ttk.Entry(row1, textvariable=self.max_frames, width=8).pack(side="left", padx=(6, 18))

        ttk.Label(row1, text="Delay PZ7:").pack(side="left")
        ttk.Entry(row1, textvariable=self.delay, width=8).pack(side="left", padx=(6, 18))

        controls = ttk.Frame(main)
        controls.pack(fill="x", pady=8)

        self.start_btn = ttk.Button(controls, text="Скачать / Запустить анализ", command=self.start_analysis)
        self.start_btn.pack(side="left", padx=4)

        ttk.Button(controls, text="Открыть папку результата", command=self.open_output_folder).pack(side="left", padx=4)

        self.progress = ttk.Progressbar(main, orient="horizontal", mode="indeterminate")
        self.progress.pack(fill="x", pady=8)

        ttk.Label(main, textvariable=self.status).pack(anchor="w", pady=(0, 8))

        log_frame = ttk.LabelFrame(main, text="Лог")
        log_frame.pack(fill="both", expand=True, pady=8)

        self.log = tk.Text(log_frame, wrap="word", height=18)
        self.log.pack(fill="both", expand=True, padx=8, pady=8)

        self.refresh_mode()

    def refresh_mode(self):
        # Сначала скрываем оба фрейма ввода
        self.local_frame.pack_forget()
        self.rutube_frame.pack_forget()
        # Скрываем лог (чтобы потом упаковать его после поля ввода)
        self.log.master.pack_forget()

        if self.mode.get() == "local":
            # Упаковываем поле выбора локального файла
            self.local_frame.pack(fill="x", pady=8)
        else:
            # Упаковываем поле ввода Rutube URL
            self.rutube_frame.pack(fill="x", pady=8)

        # Упаковываем лог ПОСЛЕ поля ввода
        self.log.master.pack(fill="both", expand=True, pady=8)

    def choose_file(self):
        path = filedialog.askopenfilename(
            title="Выберите видео",
            filetypes=[("Video files", "*.mp4 *.mkv *.avi *.mov"), ("All files", "*.*")]
        )
        if path:
            self.video_path.set(path)
            self.log_message(f"Выбран файл: {path}")

    def log_message(self, msg):
        self.log.insert("end", msg + "\n")
        self.log.see("end")

    def start_analysis(self):
        try:
            float(self.fps.get())
            int(self.skip_frames.get())
            int(self.max_frames.get())
            float(self.delay.get())
        except Exception:
            messagebox.showerror("Ошибка", "Проверь параметры")
            return

        if self.mode.get() == "local":
            if not self.video_path.get().strip():
                messagebox.showwarning("Внимание", "Выберите локальный видеофайл")
                return
        else:
            if not self.rutube_url.get().strip():
                messagebox.showwarning("Внимание", "Введите Rutube URL")
                return

        self.start_btn.config(state="disabled")
        self.progress.start(10)
        self.status.set("Анализ запущен...")
        self.log_message("Запуск анализа...")

        thread = threading.Thread(target=self.run_analysis_thread, daemon=True)
        thread.start()

    def run_analysis_thread(self):
        try:
            if self.mode.get() == "local":
                video_path = self.video_path.get().strip()
            else:
                url = self.rutube_url.get().strip()
                self.log_message("Скачивание видео с Rutube...")
                downloader = VideoDownloader()
                video_path = downloader.download(url, quality="720p")
                self.log_message(f"Видео скачано: {video_path}")

            result = run_pipeline(
                video_path=video_path,
                fps=float(self.fps.get()),
                skip_frames=int(self.skip_frames.get()),
                max_frames=int(self.max_frames.get()),
                delay=float(self.delay.get())
            )
            self.root.after(0, self.analysis_finished(result))
        except Exception as e:
            err = str(e)
            self.root.after(0, self.analysis_failed(err))

    def analysis_finished(self, result):
        self.progress.stop()
        self.start_btn.config(state="normal")
        self.status.set("Анализ завершён")
        self.log_message(f"Готово: {result}")
        messagebox.showinfo("Готово", f"Анализ завершён.\nУровень риска: {result.get('risk_level', 'unknown')}")

    def analysis_failed(self, error_text):
        self.progress.stop()
        self.start_btn.config(state="normal")
        self.status.set("Ошибка анализа")
        self.log_message("Ошибка: " + error_text)
        messagebox.showerror("Ошибка", error_text)

    def open_output_folder(self):
        out = Path(".").resolve()
        if sys.platform.startswith("win"):
            os.startfile(out)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(out)])
        else:
            subprocess.Popen(["xdg-open", str(out)])


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoAnalyzerApp(root)
    root.mainloop()
