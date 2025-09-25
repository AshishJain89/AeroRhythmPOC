from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .core.database import Base
from sqlalchemy import (
    Column, 
    Integer, 
    String, 
    DateTime, 
    Boolean, 
    ForeignKey, 
    Text, 
    Date, 
    Time,
    JSON,
    Float
)
import uuid

def generate_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, default=generate_uuid, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    
    # Relationships
    disruptions = relationship("Disruption", back_populates="reporter")


class Crew(Base):
    __tablename__ = "crews"
    
    id = Column(Integer, primary_key=True, default=generate_uuid, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    employee_id = Column(String(20), unique=True, index=True)
    position = Column(String(50), nullable=False)
    home_base = Column(String(50))
    status = Column(String(20), default="available")
    licence_expiry = Column(Date)
    qualifications = Column(JSON, default=[])
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    roster_assignments = relationship("Roster", back_populates="crew")


class Flight(Base):
    __tablename__ = "flights"
    
    id = Column(Integer, primary_key=True, default=generate_uuid, index=True)
    flight_number = Column(String(10), nullable=False, index=True)
    origin = Column(String(50), nullable=False)
    destination = Column(String(50), nullable=False)
    departure_time = Column(DateTime, nullable=False)
    arrival_time = Column(DateTime, nullable=False)
    aircraft_type = Column(String(20))
    status = Column(String(20), default="scheduled")  # scheduled, active, completed, cancelled
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    roster_assignments = relationship("Roster", back_populates="flight")


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, default=generate_uuid, index=True)
    type = Column(String(100), nullable=False) # e.g. "roster_generation"
    status = Column(String(32), nullable=False, default="PENDING") # PENDING | RUNNING | SUCCESS | FAILED
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)
    result = Column(JSON, nullable=True)
    error_message = Column(String(1024), nullable=True)


class Roster(Base):
    __tablename__ = "rosters"
    
    id = Column(Integer, primary_key=True, default=generate_uuid, index=True)
    crew_id = Column(Integer, ForeignKey("crews.id"), nullable=False)
    flight_id = Column(Integer, ForeignKey("flights.id"), nullable=False)
    assignment_date = Column(Date, nullable=False)
    report_time = Column(Time, nullable=False)
    duty_type = Column(String(20))  # flight, standby, training
    status = Column(String(20), default="scheduled")
    confidence = Column(Float, default=1.0)
    violations = Column(JSON, default=[])
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    crew = relationship("Crew", back_populates="roster_assignments")
    flight = relationship("Flight", back_populates="roster_assignments")


class Disruption(Base):
    __tablename__ = "disruptions"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    type = Column(String(50), nullable=False)  # weather, technical, crew, etc.
    severity = Column(String(20))  # low, medium, high, critical
    affected_flights = Column(JSON, default=[])
    affected_crew = Column(JSON, default=[])
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    status = Column(String(20), default="active")  # active, resolved, cancelled
    reporter_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    reporter = relationship("User", back_populates="disruptions")



# from datetime import datetime, timezone
# from typing import Any

# from sqlalchemy import (
#     Column,
#     Integer,
#     String,
#     DateTime,
#     JSON,
#     ForeignKey,
#     Boolean,
#     Text,
#     UniqueConstraint,
# )
# from sqlalchemy.orm import relationship
# from sqlalchemy.ext.declarative import declarative_base

# Base = declarative_base()


# class User(Base):
#     __tablename__ = "users"
#     id = Column(Integer, primary_key=True, index=True)
#     username = Column(String(150), unique=True, nullable=False, index=True)
#     email = Column(String(255), unique=True, nullable=True, index=True)
#     hashed_password = Column(String(255), nullable=False)
#     is_active = Column(Boolean, default=True)
#     is_superuser = Column(Boolean, default=False)
#     created_at = Column(DateTime, default=datetime.now(timezone.utc))

#     def __repr__(self) -> str:
#         return f"<User id={self.id} username={self.username}>"


# class Crew(Base):
#     __tablename__ = "crew"
#     id = Column(Integer, primary_key=True, index=True)
#     employee_id = Column(String(50), nullable=False, index=True)
#     first_name = Column(String(100), nullable=False)
#     last_name = Column(String(100), nullable=False)
#     rank = Column(String(50), nullable=False)  # e.g., CPT, FO, FA
#     base_airport = Column(String(10), nullable=True, index=True)
#     hire_date = Column(DateTime, nullable=True)
#     seniority_number = Column(Integer, default=0)
#     status = Column(String(50), default="active")
#     created_at = Column(DateTime, default=datetime.now(timezone.utc))
#     updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

#     assignments = relationship("RosterAssignment", back_populates="crew", cascade="all, delete-orphan")

#     def __repr__(self) -> str:
#         return f"<Crew id={self.id} name={self.first_name} {self.last_name} rank={self.rank}>"


# class Flight(Base):
#     __tablename__ = "flights"
#     id = Column(String(64), primary_key=True, index=True)  # flight code e.g. "AI205"
#     flight_number = Column(String(32), index=True, nullable=False)
#     origin = Column(String(10), nullable=False, index=True)
#     destination = Column(String(10), nullable=False, index=True)
#     departure = Column(DateTime, nullable=False, index=True)
#     arrival = Column(DateTime, nullable=False, index=True)
#     aircraft = Column(String(50), nullable=True)
#     attributes = Column("attributes", JSON, default={})
#     created_at = Column(DateTime, default=datetime.now(timezone.utc))

#     assignments = relationship("RosterAssignment", back_populates="flight", cascade="all, delete-orphan")

#     def __repr__(self) -> str:
#         return f"<Flight id={self.id} {self.origin}->{self.destination} depart={self.departure}>"


# class RosterAssignment(Base):
#     __tablename__ = "rosters"
#     id = Column(Integer, primary_key=True, index=True)
#     crew_id = Column(Integer, ForeignKey("crew.id", ondelete="CASCADE"), nullable=False, index=True)
#     flight_id = Column(String(64), ForeignKey("flights.id", ondelete="CASCADE"), nullable=False, index=True)
#     start = Column(DateTime, nullable=False, index=True)
#     end = Column("end", DateTime, nullable=False, index=True)
#     position = Column(String(32), nullable=True)  # CPT / FO / FA etc.
#     attributes = Column("attributes", JSON, default={})  # assignment_confidence, tags, etc.
#     created_at = Column(DateTime, default=datetime.now(timezone.utc))

#     crew = relationship("Crew", back_populates="assignments")
#     flight = relationship("Flight", back_populates="assignments")

#     __table_args__ = (
#         UniqueConstraint("crew_id", "flight_id", name="uq_crew_flight"),
#     )

#     def __repr__(self) -> str:
#         return f"<RosterAssignment id={self.id} crew={self.crew_id} flight={self.flight_id}>"


# class Disruption(Base):
#     __tablename__ = "disruptions"
#     id = Column(Integer, primary_key=True, index=True)
#     type = Column(String(80), nullable=False)  # e.g., "delay", "cancellation", "absence"
#     affected = Column(JSON, default={})  # which flights/crews affected
#     severity = Column(String(32), nullable=True)
#     attributes = Column("attributes", JSON, default={})
#     created_at = Column(DateTime, default=datetime.now(timezone.utc))

#     def __repr__(self) -> str:
#         return f"<Disruption id={self.id} type={self.type} severity={self.severity}>"


# class Job(Base):
#     __tablename__ = "jobs"
#     id = Column(Integer, primary_key=True, index=True)
#     type = Column(String(100), nullable=False) # e.g. "roster_generation"
#     status = Column(String(32), nullable=False, default="PENDING") # PENDING | RUNNING | SUCCESS | FAILED
#     created_at = Column(DateTime, default=datetime.now(timezone.utc))
#     completed_at = Column(DateTime, nullable=True)
#     result = Column(JSON, nullable=True)
#     error_message = Column(String(1024), nullable=True)

# class Job(Base):
#     __tablename__ = "jobs"
#     id = Column(Integer, primary_key=True, index=True)
#     type = Column(String(100), nullable=False) # e.g. "roster_generation"
#     status = Column(String(32), nullable=False, default="PENDING") # PENDING | RUNNING | SUCCESS | FAILED
#     created_at = Column(DateTime, default=datetime.now(timezone.utc))
#     completed_at = Column(DateTime, nullable=True)
#     result = Column(JSON, nullable=True)
#     error_message = Column(String(1024), nullable=True)


#     def __repr__(self) -> str:
#         return f"<Job id={self.id} type={self.type} status={self.status}>"

# # Add these missing models to match your database

# class AuditLog(Base):
#     __tablename__ = "audit_log"
#     id = Column(Integer, primary_key=True, index=True)
#     table_name = Column(String(100), nullable=False)
#     record_id = Column(String(100), nullable=False)
#     action = Column(String(50), nullable=False)  # INSERT, UPDATE, DELETE
#     old_values = Column(JSON, nullable=True)
#     new_values = Column(JSON, nullable=True)
#     user_id = Column(Integer, nullable=True)
#     timestamp = Column(DateTime, default=datetime.now(timezone.utc))
#     ip_address = Column(String(45), nullable=True)

# class ComplianceRule(Base):
#     __tablename__ = "compliance_rules"
#     id = Column(Integer, primary_key=True, index=True)
#     rule_name = Column(String(200), nullable=False)
#     rule_type = Column(String(100), nullable=False)  # REST_TIME, DUTY_TIME, etc.
#     description = Column(Text, nullable=True)
#     parameters = Column(JSON, default={})
#     is_active = Column(Boolean, default=True)
#     created_at = Column(DateTime, default=datetime.now(timezone.utc))
#     updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

# class Conflict(Base):
#     __tablename__ = "conflicts"
#     id = Column(Integer, primary_key=True, index=True)
#     conflict_type = Column(String(100), nullable=False)  # OVERLAP, REST_VIOLATION, etc.
#     severity = Column(String(50), nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
#     crew_id = Column(Integer, ForeignKey("crew.id"), nullable=True)
#     flight_id = Column(String(64), ForeignKey("flights.id"), nullable=True)
#     assignment_id = Column(Integer, nullable=True)
#     description = Column(Text, nullable=True)
#     resolution_status = Column(String(50), default="OPEN")  # OPEN, RESOLVED, IGNORED
#     created_at = Column(DateTime, default=datetime.now(timezone.utc))
#     resolved_at = Column(DateTime, nullable=True)
#     resolved_by = Column(Integer, nullable=True)