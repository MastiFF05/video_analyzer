from difflib import SequenceMatcher
import numpy as np

def deduplicate_texts(texts, threshold=0.8):
    """Дедупликация OCR"""
    unique_texts = []
    for text in texts:
        if not any(SequenceMatcher(None, text['text'], ut['text']).ratio() > threshold 
                   for ut in unique_texts):
            unique_texts.append(text)
    return unique_texts

class ObjectTracker:
    def __init__(self):
        self.tracks = {}
    
    def update(self, detections, frame_id):
        pass
