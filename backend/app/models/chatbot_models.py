# backend/models/chatbot_models.py
from sqlalchemy import Column, Integer, String, DateTime, Date, JSON, ForeignKey, Text
from sqlalchemy.sql import func
# from backend.database import Base
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class CrewCertification(Base):
    __tablename__ = "crew_certification"
    
    id = Column(Integer, primary_key=True, index=True)
    crew_id = Column(Integer, ForeignKey("crew.id"), nullable=False)
    cert_type = Column(String(100), nullable=False)  # license, type-rating, medical
    aircraft_type = Column(String(50))
    issue_date = Column(Date, nullable=False)
    expiry_date = Column(Date, nullable=False)
    details = Column(JSON)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    crew = relationship("Crew", back_populates="certifications")

class CrewTraining(Base):
    __tablename__ = "crew_training"
    
    id = Column(Integer, primary_key=True, index=True)
    crew_id = Column(Integer, ForeignKey("crew.id"), nullable=False)
    course = Column(String(200), nullable=False)
    valid_from = Column(Date, nullable=False)
    valid_to = Column(Date, nullable=False)
    status = Column(String(50), default="active")
    created_at = Column(DateTime, default=func.now())

    crew = relationship("Crew", back_populates="trainings")

class Pairing(Base):
    __tablename__ = "pairing"
    
    id = Column(Integer, primary_key=True, index=True)
    pairing_code = Column(String(20), unique=True, nullable=False)
    origin = Column(String(3), nullable=False)
    destination = Column(String(3), nullable=False)
    sectors = Column(JSON, nullable=False)  # Array of flight legs
    planned_start = Column(DateTime, nullable=False)
    planned_end = Column(DateTime, nullable=False)
    aircraft_type = Column(String(50), nullable=False)
    attributes = Column(JSON)
    created_at = Column(DateTime, default=func.now())

class LeaveRequest(Base):
    __tablename__ = "leave_request"
    
    id = Column(Integer, primary_key=True, index=True)
    crew_id = Column(Integer, ForeignKey("crew.id"), nullable=False)
    leave_start = Column(DateTime, nullable=False)
    leave_end = Column(DateTime, nullable=False)
    leave_type = Column(String(50), nullable=False)  # annual, sick, personal
    status = Column(String(50), default="pending")  # pending, approved, rejected
    reason = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    crew = relationship("Crew", back_populates="leave_requests")

class WeatherForecast(Base):
    __tablename__ = "weather_forecast"
    
    id = Column(Integer, primary_key=True, index=True)
    airport_code = Column(String(3), nullable=False)
    forecast_time = Column(DateTime, nullable=False)
    valid_from = Column(DateTime, nullable=False)
    valid_to = Column(DateTime, nullable=False)
    severity = Column(String(50), nullable=False)  # low, medium, high, severe
    conditions = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=func.now())

class DisruptionEvent(Base):
    __tablename__ = "disruption_event"
    
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(100), nullable=False)  # weather, maintenance, atc, crew
    severity = Column(String(50), nullable=False)
    affected_pairings = Column(JSON)  # Array of pairing IDs
    description = Column(Text)
    detected_at = Column(DateTime, nullable=False)
    resolved_at = Column(DateTime)
    source = Column(String(100))
    attributes = Column(JSON)
    created_at = Column(DateTime, default=func.now())

class CredentialAuditLog(Base):
    __tablename__ = "credential_audit_log"
    
    id = Column(Integer, primary_key=True, index=True)
    crew_id = Column(Integer, ForeignKey("crew.id"), nullable=False)
    snapshot_time = Column(DateTime, nullable=False)
    active_certificates = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=func.now())

    crew = relationship("Crew")