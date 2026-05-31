from pathlib import Path
import json
from datetime import datetime


def generate_final_report(video_path, analysis_results):
    """
    Генерирует красивый и полный финальный отчёт
    """
    frames_folder = Path("frames")
    frames_count = len(list(frames_folder.glob("*.jpg"))) if frames_folder.exists() else 0

    report = {
        "video_name": video_path.name,
        "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "task": "Много-модальный анализ видео на деструктивный контент",
        "risk_level": analysis_results.get("risk_level", "low"),
        "risk_score": analysis_results.get("risk_score", 0.0),

        "statistics": {
            "frames_extracted": frames_count,
            "unique_objects_detected": len(analysis_results.get("top_objects", {})),
            "audio_segments": analysis_results.get("audio_segments", 0),
            "ai_analyzed_frames": len(analysis_results.get("ai_findings", []))
        },

        "key_findings": {
            "top_objects": dict(list(analysis_results.get("top_objects", {}).items())[:10]),
            "ai_destructive_findings": analysis_results.get("ai_findings", [])[:6],
        },

        "recommendation": get_recommendation(analysis_results.get("risk_level", "low"))
    }

    # Создаём папку results, если её нет
    Path("results").mkdir(exist_ok=True)
    report_path = f"results/report_{video_path.stem}_{datetime.now().strftime('%H%M')}.json"

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # Также сохраняем удобочитаемую версию
    with open(f"results/report_{video_path.stem}_{datetime.now().strftime('%H%M')}.txt", "w", encoding="utf-8") as f:
        f.write(f"Анализ видео: {video_path.name}\n")
        f.write(f"Дата: {report['analysis_date']}\n")
        f.write(f"Уровень риска: {report['risk_level'].upper()} (score: {report['risk_score']})\n\n")
        f.write("ТОП объекты:\n")
        for obj, count in report["key_findings"]["top_objects"].items():
            f.write(f"  • {obj}: {count} раз\n")

    print(f"   Отчёт сохранён: {report_path}")
    return {
        "report_path": report_path,
        "risk_level": report["risk_level"]
    }


def get_recommendation(risk_level: str) -> str:
    if risk_level == "high":
        return "Рекомендуется немедленная модерация / блокировка контента."
    elif risk_level == "medium":
        return "Требуется дополнительная проверка модератором."
    else:
        return "Контент выглядит безопасным."
