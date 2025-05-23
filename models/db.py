from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os

DB_URL = os.getenv("DB_URL", "sqlite:///openaiops.db")
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    incidents = relationship("Incident", back_populates="tenant")
    users = relationship("User", back_populates="tenant")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    tenant_id = Column(Integer, ForeignKey("tenants.id"))
    is_admin = Column(Boolean, default=False)
    tenant = relationship("Tenant", back_populates="users")

class Incident(Base):
    __tablename__ = "incidents"
    id = Column(Integer, primary_key=True, index=True)
    incident_uid = Column(String, unique=True, index=True)
    timestamp = Column(DateTime)
    type = Column(String)
    description = Column(String)
    status = Column(String, default="open")  # open, ack, resolved
    cpu = Column(Float, nullable=True)
    mem = Column(Float, nullable=True)
    latency = Column(Float, nullable=True)
    log = Column(Text, nullable=True)
    severity = Column(String, nullable=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"))
    tenant = relationship("Tenant", back_populates="incidents")

def init_db():
    Base.metadata.create_all(bind=engine)
