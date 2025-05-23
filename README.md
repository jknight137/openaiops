# OpenAIOps – Open Source AIOps SaaS Platform

## Overview
OpenAIOps is a multi-tenant, cloud-native, SaaS-ready AIOps platform designed for IT Operations, DevOps, and SRE teams...

## Quickstart
1. pip install -r requirements.txt
2. python -m uvicorn api.main:app --reload
3. python ui/dashboard.py
4. Visit http://localhost:8050

## Docker
docker-compose up --build

## Kubernetes with Helm
1. eval $(minikube docker-env)
2. docker build -t openaiops-api:latest .
3. docker build -t openaiops-ui:latest -f ui/Dockerfile ui
4. helm install openaiops ./openaiops-helm
