def perform_grc_check(risk_factors: dict) -> dict:
    score = sum(risk_factors.values()) * 20
    level = "Low" if score < 40 else "Medium" if score < 70 else "High" if score < 90 else "Critical"
    return {"risk_score": score, "risk_level": level, "recommendations": ["Review policies", "Implement controls", "Monitor continuously"]}
