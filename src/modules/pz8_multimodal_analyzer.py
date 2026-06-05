from collections import Counter
import json
from src.config import config
from src.utils.logging import setup_logging

logger = setup_logging()

def postprocess_all(yolo_data, resnet_data, audio_data, qwen_data=None):
    # YOLO
    all_objects = []
    for detections in yolo_data.values():
        for obj in detections:
            all_objects.append(obj.get("class", "").lower())

    object_counter = Counter(all_objects)
    yolo_risk = sum(0.4 for obj in object_counter if obj in config.DANGEROUS_CLASSES)

    # LLM
    destructive_count = 0
    findings = []
    if qwen_data:
        for item in qwen_data.values():
            text = item.get("result", "") if isinstance(item, dict) else str(item)
            if text and len(text.strip()) > 5:
                findings.append(text)
                low = text.lower()
                if any(word in low for word in ["есть", "оруж", "кров", "насил", "наркот", "экстре", "алко"]):
                    destructive_count += 1

    llm_risk = destructive_count * 0.6

    # Audio
    audio_segments = len(audio_data.get("segments", [])) if isinstance(audio_data, dict) else 0
    audio_risk = audio_segments * 0.08

    total_score = (
        yolo_risk * config.YOLO_WEIGHT +
        llm_risk * config.LLM_WEIGHT +
        audio_risk * config.AUDIO_WEIGHT
    )

    risk_level = "high" if total_score >= 1.6 else "medium" if total_score >= 0.8 else "low"
    explanation = f"YOLO risk: {yolo_risk:.1f} | LLM: {llm_risk:.1f} | Audio: {audio_risk:.1f}"

    final = {
        "risk_level": risk_level,
        "risk_score": round(total_score, 2),
        "top_objects": dict(object_counter.most_common(15)),
        "qwen_findings": findings[:10],
        "audio_segments": audio_segments,
        "explanation": explanation
    }

    with open("final_analysis.json", "w", encoding="utf-8") as f:
        json.dump(final, f, ensure_ascii=False, indent=2)

    logger.info(f"Финальный риск: {risk_level} ({total_score:.2f})")
    return final
