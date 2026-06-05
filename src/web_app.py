import gradio as gr
from pathlib import Path
from src.main_pipeline import run_pipeline


def analyze_video(video_file):
    if video_file is None:
        return "Загрузите видео файл", "low", ""

    try:
        video_path = video_file.name  # Gradio возвращает путь к временному файлу

        print(f"✅ Получен файл: {Path(video_path).name}")

        # Запускаем анализ
        result = run_pipeline(
            video_path=video_path,
            fps=2.0,
            skip_frames=90,
            max_frames=15,
            delay=5
        )

        report = f"""✅ **Анализ завершён успешно!**

**Уровень риска:** {result['risk_level'].upper()}
**Score:** {result.get('risk_score', 0):.2f}

Подробный отчёт сохранён в папке `results/`
"""
        return report, result['risk_level'], result.get('report_path', 'Готово')

    except Exception as e:
        return f"Ошибка при анализе:\n{str(e)}", "error", ""


# ====================== ИНТЕРФЕЙС ======================
with gr.Blocks(title="Video Analyzer", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🎥 Анализатор Деструктивного Контента")

    with gr.Row():
        video_input = gr.File(
            label="Загрузите видео (mp4, mkv, avi, mov)",
            file_types=[".mp4", ".mkv", ".avi", ".mov", ".webm"],
            height=200
        )

    with gr.Row():
        btn = gr.Button("Запустить анализ", variant="primary", size="large")

    with gr.Row():
        output_text = gr.Markdown(label="Результат анализа", value="")

    with gr.Row():
        risk_box = gr.Textbox(label="Уровень риска", interactive=False)
        report_box = gr.Textbox(label="Путь к отчёту", interactive=False)

    btn.click(
        fn=analyze_video,
        inputs=video_input,
        outputs=[output_text, risk_box, report_box]
    )

    gr.Markdown("**Примечание:** Анализ может занять 1–3 минуты в зависимости от длины видео.")

if __name__ == "__main__":
    print("Запуск веб-интерфейса...")
    print("Открыть в браузере: http://127.0.0.1:7860")

    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=True,
        debug=True
    )
