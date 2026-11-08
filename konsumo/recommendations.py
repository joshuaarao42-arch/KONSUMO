from .analytics import usage_stats, detect_anomalies

def generate_recommendations(db_path, user_id=None):
    tips=[]
    for r in ("electricity","water"):
        s=usage_stats(r,db_path,user_id=user_id)
        if s["average"]: tips.append(f"Review {r} usage around the daily average of {s['average']:.2f} units.")
        if detect_anomalies(r,db_path,user_id=user_id):
            tips.append(f"Investigate unusual {r} readings before the next bill.")
    return tips or ["Add more meter readings to receive personalized recommendations."]
