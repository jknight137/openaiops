from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import threading, time, uuid
from datetime import datetime
from typing import List, Optional
from contextlib import asynccontextmanager

from models.db import SessionLocal, init_db, Tenant, User, Incident
from ingestion.simulate_data import generate_metrics, generate_logs
from ml.anomaly_detector import detect_metric_anomalies, detect_log_anomalies

init_db()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Background scheduler for data simulation
def incident_scheduler():
    db = SessionLocal()
    base_idx = 0
    while True:
        tenant = db.query(Tenant).first()
        if not tenant:
            tenant = Tenant(name="DefaultOrg")
            db.add(tenant)
            db.commit()
            db.refresh(tenant)
        metrics = generate_metrics(n=5, base_idx=base_idx)
        logs = generate_logs(n=5, base_idx=base_idx)
        base_idx += 5

        metric_anoms = detect_metric_anomalies(metrics)
        log_anoms = detect_log_anomalies(logs)

        for anom in metric_anoms + log_anoms:
            exists = db.query(Incident).filter(
                Incident.timestamp == datetime.fromisoformat(anom["timestamp"]),
                Incident.type == anom["type"],
                Incident.tenant_id == tenant.id
            ).first()
            if not exists:
                inc = Incident(
                    incident_uid=str(uuid.uuid4()),
                    timestamp=datetime.fromisoformat(anom["timestamp"]),
                    type=anom.get("type"),
                    description=anom.get("description"),
                    status="open",
                    cpu=anom.get("cpu"),
                    mem=anom.get("mem"),
                    latency=anom.get("latency"),
                    log=anom.get("log"),
                    severity=anom.get("severity"),
                    tenant=tenant
                )
                db.add(inc)
                db.commit()
        time.sleep(5)
    db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    thread = threading.Thread(target=incident_scheduler, daemon=True)
    thread.start()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/incidents", response_model=List[dict])
def list_incidents(status: Optional[str] = None, db: Session = Depends(get_db)):
    tenant = db.query(Tenant).first()
    if not tenant:
        return []
    q = db.query(Incident).filter(Incident.tenant_id == tenant.id)
    if status:
        q = q.filter(Incident.status == status)
    res = q.order_by(Incident.timestamp.desc()).all()
    return [
        {
            "id": inc.incident_uid,
            "timestamp": inc.timestamp.isoformat(),
            "type": inc.type,
            "description": inc.description,
            "status": inc.status,
            "cpu": inc.cpu,
            "mem": inc.mem,
            "latency": inc.latency,
            "log": inc.log,
            "severity": inc.severity
        }
        for inc in res
    ]

@app.post("/incidents/{incident_id}/ack")
def acknowledge_incident(incident_id: str, db: Session = Depends(get_db)):
    tenant = db.query(Tenant).first()
    inc = db.query(Incident).filter(Incident.incident_uid == incident_id, Incident.tenant_id == tenant.id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    inc.status = "ack"
    db.commit()
    return {"msg": "Acknowledged"}

@app.post("/incidents/{incident_id}/resolve")
def resolve_incident(incident_id: str, db: Session = Depends(get_db)):
    tenant = db.query(Tenant).first()
    inc = db.query(Incident).filter(Incident.incident_uid == incident_id, Incident.tenant_id == tenant.id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    inc.status = "resolved"
    db.commit()
    return {"msg": "Resolved"}

@app.get("/me")
def profile():
    return {"email": "guest@example.com", "tenant": "DefaultOrg", "is_admin": True}

@app.get("/users")
def users(db: Session = Depends(get_db)):
    tenant = db.query(Tenant).first()
    users = db.query(User).filter(User.tenant_id == tenant.id).all()
    return [{"email": u.email, "is_admin": u.is_admin} for u in users]
