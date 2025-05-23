
# This script generates synthetic metric data and logs for testing purposes.
import pandas as pd
import numpy as np
from datetime import datetime

def generate_metrics(n=1, anomaly_freq=10, base_idx=0):
    # Returns a list of dicts representing metrics, simulates a batch
    np.random.seed()
    metrics = []
    for i in range(base_idx, base_idx + n):
        timestamp = datetime.now().isoformat()
        cpu = np.random.normal(50, 10)
        mem = np.random.normal(60, 10)
        latency = np.random.normal(100, 20)
        if (i % anomaly_freq) == 0:
            cpu += np.random.choice([30, -25])
            mem += np.random.choice([20, -15])
            latency += np.random.choice([60, -40])
        metrics.append({
            "timestamp": timestamp,
            "cpu": cpu,
            "mem": mem,
            "latency": latency
        })
    return metrics

def generate_logs(n=1, anomaly_freq=10, base_idx=0):
    np.random.seed()
    logs = []
    base_msgs = [
        "Service started successfully",
        "Received request",
        "Database query executed",
        "Background job ran",
        "User login succeeded"
    ]
    error_msgs = [
        "ERROR: Out of memory",
        "WARNING: High CPU usage",
        "ERROR: Service unavailable",
        "CRITICAL: Database timeout"
    ]
    for i in range(base_idx, base_idx + n):
        timestamp = datetime.now().isoformat()
        if (i % anomaly_freq) == 0:
            msg = np.random.choice(error_msgs)
        else:
            msg = np.random.choice(base_msgs)
        logs.append({"timestamp": timestamp, "log": msg})
    return logs
