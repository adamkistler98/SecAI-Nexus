import math
from collections import Counter
import json

def calculate_entropy(data: bytes) -> float:
    if not data:
        return 0.0
    counter = Counter(data)
    length = len(data)
    entropy = -sum((count / length) * math.log2(count / length) for count in counter.values())
    return entropy

def extract_features(content: bytes) -> dict:
    size = len(content)
    entropy = calculate_entropy(content)
    with open("config/config.json") as f:
        config = json.load(f)
    keywords = config["suspicious_keywords"]
    text = content.lower().decode('utf-8', errors='ignore')
    suspicious_count = sum(1 for kw in keywords if kw.lower() in text)
    return {"file_size": size, "entropy": round(entropy, 2), "suspicious_count": suspicious_count}
