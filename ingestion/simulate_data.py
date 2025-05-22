
# This script generates synthetic metric data and logs for testing purposes.
import pandas as pd
import numpy as np
import time
from datetime import datetime

def generate_metrics(n=100, anomaly_freq=20):
    np.random.seed(42)
    timestamps = [datetime.now().isoformat()]
    cpu = [np.random.normal(50, 10)]
    mem = [np.random.normal(60, 10)]
    latency = [np.random.normal(100, 20)]

    for i in range(1, n):
        timestamps.append((datetime.now()).isoformat())
        cpu_val = cpu[-1] + np.random.normal(0, 2)
        mem_val = mem[-1] + np.random.normal(0, 2)
        latency_val = latency[-1] + np.random.normal(0, 3)

        # Inject anomaly every anomaly_freq samples
        if i % anomaly_freq == 0:
            cpu_val += np.random.choice([30, -25])  # spike or drop
            mem_val += np.random.choice([20, -15])
            latency_val += np.random.choice([60, -40])

        cpu.append(cpu_val)
        mem.append(mem_val)
        latency.append(latency_val)

    df = pd.DataFrame({
        "timestamp": timestamps,
        "cpu": cpu,
        "mem": mem,
        "latency": latency,
    })
    df.to_csv("ingestion/simulated_metrics.csv", index=False)
    print("Simulated metric data written to ingestion/simulated_metrics.csv")

def generate_logs(n=100, anomaly_freq=20):
    np.random.seed(43)
    lines = []
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
    for i in range(n):
        timestamp = datetime.now().isoformat()
        if i % anomaly_freq == 0:
            msg = np.random.choice(error_msgs)
        else:
            msg = np.random.choice(base_msgs)
        lines.append(f"{timestamp} | {msg}")
    with open("ingestion/simulated_logs.txt", "w") as f:
        f.write("\n".join(lines))
    print("Simulated logs written to ingestion/simulated_logs.txt")

if __name__ == "__main__":
    generate_metrics()
    generate_logs()
