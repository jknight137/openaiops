FROM python:3.11-slim

WORKDIR /app

COPY dashboard.py .

RUN pip install dash pandas requests

EXPOSE 8050

CMD ["python", "dashboard.py"]
