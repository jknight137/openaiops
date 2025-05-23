import pandas as pd
from sklearn.ensemble import IsolationForest

def detect_metric_anomalies(metrics, contamination=0.15):
    # metrics: list of dicts (from simulate_data.generate_metrics)
    if not metrics:
        return []
    df = pd.DataFrame(metrics)
    if len(df) < 5:
        # Not enough for ML, fallback to simple rule
        df["anomaly"] = (df["cpu"] > 80) | (df["cpu"] < 20) | (df["mem"] > 85) | (df["latency"] > 200)
    else:
        clf = IsolationForest(contamination=contamination, random_state=42)
        preds = clf.fit_predict(df[["cpu", "mem", "latency"]])
        df["anomaly"] = preds == -1
    result = []
    for idx, row in df[df["anomaly"]].iterrows():
        result.append({
            "type": "metric",
            "timestamp": row["timestamp"],
            "cpu": row["cpu"],
            "mem": row["mem"],
            "latency": row["latency"],
            "description": "Metric anomaly detected"
        })
    return result

def detect_log_anomalies(logs):
    # logs: list of dicts (from simulate_data.generate_logs)
    anomalies = []
    for entry in logs:
        msg = entry["log"]
        sev = None
        if "CRITICAL" in msg or "ERROR" in msg:
            sev = "high"
        elif "WARNING" in msg:
            sev = "medium"
        if sev:
            anomalies.append({
                "type": "log",
                "timestamp": entry["timestamp"],
                "log": msg,
                "severity": sev,
                "description": f"Log {sev} anomaly"
            })
    return anomalies
