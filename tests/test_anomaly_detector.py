import os
from ml.anomaly_detector import detect_metric_anomalies, detect_log_anomalies

def test_detect_metric_anomalies():
    detect_metric_anomalies()
    assert os.path.exists("ml/detected_anomalies.csv")

def test_detect_log_anomalies():
    detect_log_anomalies()
    assert os.path.exists("ml/log_anomalies.csv")
