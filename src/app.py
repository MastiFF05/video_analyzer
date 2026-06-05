import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import sys
from pathlib import Path

from src.main_pipeline import run_pipeline
from src.modules.pz2_frame_extractor import VideoDownloader
from src.config import config

class VideoAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Analyzer — Деструктивный Контент")
        self.root.geometry("1020x760")
        self.root.minsize(950, 680)

        self.mode = tk.StringVar(value="local")
        self.video_path = tk.StringVar()
        self.rutube_url = tk.StringVar()
        self.fps = tk.StringVar(value=str(config.VIDEO_FPS))
        self.skip_frames = tk.StringVar(value=str(config.LLM_SKIP_FRAMES))
        self.max_frames = tk.StringVar(value=str(config.LLM_MAX_FRAMES))
        self.delay = tk.StringVar(value=str(config.LLM_DELAY))
        self.status = tk.StringVar(value="Готов к запуску")

        self.build_ui()

    def build_ui(self):
        main = ttk.Frame(self.root, padding=15)
        main.pack(fill="both", expand=True)

        ttk.Label(main, text="Video Analyzer", font=("Arial", 18, "bold")).pack(anchor="w", pady=(0, 12))

        # === Режим ===
        mode_frame = ttk.LabelFrame(main, text="Режим обработки", padding=10)
        mode_frame.pack(fill="x", pady=8)

        ttk.Radiobutton(mode_frame, text="Локальный файл", variable=self.mode, value="local",
                        command=self.refresh_mode).pack(anchor="w", pady=2)
        ttk.Radiobutton(mode_frame, text="Rutube URL", variable=self.mode, value="rutube",
                        command=self.refresh_mode).pack(anchor="w", pady=2)

        # === Локальный файл ===
        self.local_frame = ttk.LabelFrame(main, text="Локальный видеофайл", padding=10)
        entry_local = ttk.Entry(self.local_frame, textvariable=self.video_path)
        entry_local.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ttk.Button(self.local_frame, text="Выбрать файл", command=self.choose_file).pack(side="left")

        # === Rutube URL ===
        self.rutube_frame = ttk.LabelFrame(main, text="Rutube URL", padding=10)
        ttk.Entry(self.rutube_frame, textvariable=self.rutube_url).pack(fill="x", padx=2, pady=2)

        # === Параметры ===
        params = ttk.LabelFrame(main, text="Параметры анализа", padding=10)
        params.pack(fill="x", pady=10)

        row1 = ttk.Frame(params)
        row1.pack(fill="x", pady=4)
        ttk.Label(row1, text="FPS:").pack(side="left", padx=(0, 5))
        ttk.Entry(row1, textvariable=self.fps, width=8).pack(side="left", padx=(0, 20))

        ttk.Label(row1, text="Skip frames PZ7:").pack(side="left", padx=(0, 5))
        ttk.Entry(row1, textvariable=self.skip_frames, width=8).pack(side="left", padx=(0, 20))

        ttk.Label(row1, text="Max frames PZ7:").pack(side="left", padx=(0, 5))
        ttk.Entry(row1, textvariable=self.max_frames, width=8).pack(side="left", padx=(0, 20))

        ttk.Label(row1, text="Delay PZ7 (сек):").pack(side="left", padx=(0, 5))
        ttk.Entry(row1, textvariable=self.delay, width=8).pack(side="left")

        # === Кнопки управления ===
        controls = ttk.Frame(main)
        controls.pack(fill="x", pady=12)

        self.start_btn = ttk.Button(controls, text="🚀 Скачать / Запустить анализ", command=self.start_analysis)
        self.start_btn.pack(side="left", padx=5)

        ttk.Button(controls, text="📂 Открыть папку results", command=self.open_output_folder).pack(side="left", padx=5)
        ttk.Button(controls, text="🧹 Очистить frames/results", command=self.clear_folders).pack(side="left", padx=5)

        # Прогресс
        self.progress = ttk.Progressbar(main, orient="horizontal", mode="indeterminate")
        self.progress.pack(fill="x", pady=10)

        ttk.Label(main, textvariable=self.status, font=("Arial", 10, "bold")).pack(anchor="w", pady=4)

        # === Лог ===
        log_frame = ttk.LabelFrame(main, text="Лог выполнения", padding=8)
        log_frame.pack(fill="both", expand=True)
        self.log = tk.Text(log_frame, wrap="word", height=20, font=("Consolas", 9))
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log.yview)
        self.log.configure(yscrollcommand=scrollbar.set)
        self.log.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

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
            filetypes=[("Video files", "*.mp4 *.mkv *.avi *.mov *.webm"), ("All files", "*.*")]
        )
        if path:
            self.video_path.set(path)
            self.log_message(f"✅ Выбран файл: {path}")

    def log_message(self, msg: str):
        self.log.insert("end", msg + "\n")
        self.log.see("end")
        self.root.update_idletasks()

    def start_analysis(self):
        try:
            fps = float(self.fps.get())
            skip = int(self.skip_frames.get())
            max_f = int(self.max_frames.get())
            delay = float(self.delay.get())
        except Exception:
            messagebox.showerror("Ошибка", "Проверьте корректность числовых параметров")
            return

        if self.mode.get() == "local":
            if not self.video_path.get().strip():
                messagebox.showwarning("Внимание", "Выберите видеофайл")
                return
            video_input = self.video_path.get().strip()
        else:
            if not self.rutube_url.get().strip():
                messagebox.showwarning("Внимание", "Введите URL Rutube")
                return
            video_input = self.rutube_url.get().strip()

        self.start_btn.config(state="disabled")
        self.progress.start(10)
        self.status.set("Запуск анализа...")
        self.log_message("🔄 Запуск пайплайна...")

        thread = threading.Thread(
            target=self.run_analysis_thread,
            args=(video_input, fps, skip, max_f, delay),
            daemon=True
        )
        thread.start()

    def run_analysis_thread(self, video_input, fps, skip, max_f, delay):
        try:
            if self.mode.get() == "rutube":
                self.log_message("📥 Скачивание видео с Rutube...")
                downloader = VideoDownloader()
                video_path = downloader.download(video_input, quality="720p")
                self.log_message(f"✅ Видео скачано: {video_path}")
            else:
                video_path = video_input

            result = run_pipeline(
                video_path=video_path,
                fps=fps,
                skip_frames=skip,
                max_frames=max_f,
                delay=delay
            )

            self.root.after(0, lambda r=result: self.analysis_finished(r))

        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda msg=error_msg: self.analysis_failed(str(msg)))

    def analysis_finished(self, result):
        self.progress.stop()
        self.start_btn.config(state="normal")
        self.status.set(f"✅ Готово — Risk: {result.get('risk_level', 'unknown').upper()}")
        self.log_message(f"🎉 Анализ завершён. Уровень риска: {result.get('risk_level')}")
        messagebox.showinfo("Готово", f"Анализ завершён!\nУровень риска: {result.get('risk_level', 'unknown').upper()}")

    def analysis_failed(self, error_text):
        self.progress.stop()
        self.start_btn.config(state="normal")
        self.status.set("❌ Ошибка анализа")
        self.log_message(f"❌ Ошибка: {error_text}")
        messagebox.showerror("Ошибка", error_text[:600])

    def clear_folders(self):
        for folder in [Path("frames"), Path


("results")]:
            if folder.exists():
                for file in folder.glob("*"):
                    if file.is_file():
                        file.unlink()
        self.log_message("🧹 Папки frames и results очищены.")

    def open_output_folder(self):
        out_dir = Path("results").resolve()
        if sys.platform.startswith("win"):
            os.startfile(out_dir)
        elif sys.platform == "darwin":
            os.system(f"open \"{out_dir}\"")
        else:
            os.system(f"xdg-open \"{out_dir}\"")

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoAnalyzerApp(root)
    root.mainloop()
