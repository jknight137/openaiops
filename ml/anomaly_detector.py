import pandas as pd
from sklearn.ensemble import IsolationForest

def detect_metric_anomalies(input_csv="ingestion/simulated_metrics.csv", output_csv="ml/detected_anomalies.csv"):
    df = pd.read_csv(input_csv)
    metrics = df[["cpu", "mem", "latency"]]

    # Simple outlier detection
    clf = IsolationForest(contamination=0.1, random_state=42)
    preds = clf.fit_predict(metrics)
    df["anomaly"] = preds == -1

    # Store only anomalies
    anomalies = df[df["anomaly"]]
    anomalies.to_csv(output_csv, index=False)
    print(f"Detected {len(anomalies)} anomalies; written to {output_csv}")

def detect_log_anomalies(input_txt="ingestion/simulated_logs.txt", output_csv="ml/log_anomalies.csv"):
    with open(input_txt) as f:
        lines = f.readlines()

    results = []
    for line in lines:
        if "ERROR" in line or "CRITICAL" in line:
            results.append({"timestamp": line.split("|")[0].strip(), "log": line.strip(), "severity": "high"})
        elif "WARNING" in line:
            results.append({"timestamp": line.split("|")[0].strip(), "log": line.strip(), "severity": "medium"})

    df = pd.DataFrame(results)
    df.to_csv(output_csv, index=False)
    print(f"Detected {len(df)} log anomalies; written to {output_csv}")

if __name__ == "__main__":
    detect_metric_anomalies()
    detect_log_anomalies()
