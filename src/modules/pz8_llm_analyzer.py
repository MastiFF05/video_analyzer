from collections import Counter
import json

def postprocess_all(yolo_data, resnet_data, audio_data, qwen_data=None):
    # === Объекты YOLO ===
    all_objects = []
    for detections in yolo_data.values():
        for obj in detections:
            all_objects.append(obj.get("class", ""))

    object_counter = Counter(all_objects)

    # === Risk Scoring ===
    dangerous = {"knife", "gun", "weapon", "blood", "person", "skull", "nazi"}  # можно расширять
    risk_score = sum(0.25 for obj in object_counter if obj.lower() in dangerous)

    # LLM findings
    destructive_count = 0
    findings = []
    if qwen_data:
        for item in qwen_data.values():
            if isinstance(item, dict):
                text = item.get("result", "")
            else:
                text = str(item)

            if not text:
                continue

            if "ошибка" in text.lower():
                continue

            if len(text.strip()) > 5:
                findings.append(text)

            low = text.lower()
            if any(word in low for word in ["есть", "да", "оруж", "кров", "насил", "экстре"]):
                destructive_count += 1

    risk_score += destructive_count * 0.4

    risk_level = "high" if risk_score >= 1.5 else "medium" if risk_score >= 0.7 else "low"

    final = {
        "risk_level": risk_level,
        "risk_score": round(risk_score, 2),
        "top_objects": dict(object_counter.most_common(15)),
        "qwen_findings": findings[:8],
        "audio_segments": len(audio_data.get("segments", [])) if isinstance(audio_data, dict) else 0,
    }

    with open("final_analysis.json", "w", encoding="utf-8") as f:
        json.dump(final, f, ensure_ascii=False, indent=2)

    return final
