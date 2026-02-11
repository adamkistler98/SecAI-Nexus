import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib
import os
from utils import extract_features

MODEL_PATH = "models/threat_model.pkl"
os.makedirs("models", exist_ok=True)

def train_model():
    df = pd.read_csv("data/threat_samples.csv")
    X = df[["file_size", "entropy", "suspicious_count"]]
    y = df["label"]
    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X, y)
    joblib.dump(model, MODEL_PATH)
    return model

def get_model():
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)
    return train_model()

def analyze_file(content: bytes) -> dict:
    model = get_model()
    features = extract_features(content)
    df = pd.DataFrame([features])
    pred = model.predict(df)[0]
    prob = model.predict_proba(df)[0][1]
    threat_score = int(prob * 100)
    return {
        "features": features,
        "prediction": "Malware" if pred == 1 else "Benign",
        "threat_score": threat_score,
        "confidence": round(prob * 100, 2)
    }
