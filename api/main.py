from fastapi import FastAPI
import pandas as pd
from pathlib import Path

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/incidents")
def incidents():
    metric_anom_path = Path("ml/detected_anomalies.csv")
    log_anom_path = Path("ml/log_anomalies.csv")
    incidents = []
    if metric_anom_path.exists():
        metric_df = pd.read_csv(metric_anom_path)
        for _, row in metric_df.iterrows():
            incidents.append({
                "type": "metric",
                "timestamp": row["timestamp"],
                "cpu": row["cpu"],
                "mem": row["mem"],
                "latency": row["latency"]
            })
    if log_anom_path.exists():
        log_df = pd.read_csv(log_anom_path)
        for _, row in log_df.iterrows():
            incidents.append({
                "type": "log",
                "timestamp": row["timestamp"],
                "log": row["log"],
                "severity": row.get("severity", "unknown")
            })
    return {"incidents": incidents}
