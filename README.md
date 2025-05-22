# OpenAIOps Platform (PoC)

## Overview

OpenAIOps is an open-source AIOps platform to help IT Ops, DevOps, and SRE teams manage digital incidents using machine learning and automation.

## Architecture

```mermaid
graph TD
  SimData[Simulated Data (Metrics/Logs)] --> Anomaly[Anomaly Detector]
  Anomaly --> Incident[Incident Store]
  Incident --> API[FastAPI Backend]
  API --> UI[Web UI]
```
