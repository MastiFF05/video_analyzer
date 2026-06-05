from pathlib import Path
import json
from datetime import datetime
from src.config import config

def get_recommendation(risk_level: str) -> str:
    if risk_level == "high":
        return "Рекомендуется немедленная модерация / блокировка контента."
    elif risk_level == "medium":
        return "Требуется дополнительная проверка модератором."
    else:
        return "Контент выглядит безопасным."

def generate_final_report(video_path, analysis_results):
    frames_folder = Path("frames")
    frames_count = len(list(frames_folder.glob("*.jpg"))) if frames_folder.exists() else 0

    report = {
        "video_name": video_path.name,
        "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "task": config.TASK,
        "risk_level": analysis_results.get("risk_level", "low"),
        "risk_score": round(analysis_results.get("risk_score", 0.0), 2),
        "statistics": {
            "frames_extracted": frames_count,
            "unique_objects_detected": len(analysis_results.get("top_objects", {})),
            "audio_segments": analysis_results.get("audio_segments", 0),
            "llm_analyzed_frames": len(analysis_results.get("qwen_findings", []))
        },
        "key_findings": {
            "top_objects": dict(list(analysis_results.get("top_objects", {}).items())[:12]),
            "ai_destructive_findings": analysis_results.get("qwen_findings", [])[:8],
            "explanation": analysis_results.get("explanation", "")
        },
        "recommendation": get_recommendation(analysis_results.get("risk_level", "low"))
    }

    report_dir = Path("results")
    report_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%H%M")
    base_name = f"report_{video_path.stem}_{timestamp}"

    # JSON
    json_path = report_dir / f"{base_name}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # TXT
    txt_path = report_dir / f"{base_name}.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"Анализ видео: {report['video_name']}\n")
        f.write(f"Дата: {report['analysis_date']}\n")
        f.write(f"Уровень риска: {report['risk_level'].upper()} (score: {report['risk_score']})\n\n")
        f.write("ТОП-объекты:\n")
        for obj, count in report["key_findings"]["top_objects"].items():
            f.write(f"  • {obj}: {count} раз\n")
        f.write(f"\nПояснение: {report['key_findings']['explanation']}\n")
        f.write(f"\nРекомендация: {report['recommendation']}\n")

    print(f"Отчёт сохранён: {json_path}")
    return {
        "report_path": str(json_path),
        "risk_level": report["risk_level"],
        **report
    }
