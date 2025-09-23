# app/schemas.py
from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field, EmailStr


# ------------------------------
# User / Auth
# ------------------------------
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
    exp: Optional[int] = None


class UserBase(BaseModel):
    username: str = Field(..., max_length=150)
    email: Optional[EmailStr] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserRead(UserBase):
    id: int
    is_active: bool = Field(..., alias="isActive")
    is_superuser: bool = Field(..., alias="isSuperuser")
    created_at: datetime = Field(..., alias="createdAt")

    class Config:
        from_attributes = True
        validate_by_name = True


# ------------------------------
# Crew
# ------------------------------
class CrewBase(BaseModel):
    employee_id: str
    first_name: str
    last_name: str
    rank: str
    base_airport: Optional[str] = None
    hire_date: Optional[datetime] = None
    seniority_number: Optional[int] = 0
    status: Optional[str] = "active"


class CrewCreate(CrewBase):
    pass


class CrewRead(CrewBase):
    id: int
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")

    class Config:
        from_attributes = True
        validate_by_name = True


# ------------------------------
# Flight
# ------------------------------
class FlightBase(BaseModel):
    id: str = Field(..., description="Primary flight identifier (e.g. AI205)")
    flight_number: str = Field(..., alias="flightNumber")
    origin: str
    destination: str
    departure: datetime
    arrival: datetime
    aircraft: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = Field(default_factory=dict)


class FlightCreate(FlightBase):
    pass


class FlightRead(FlightBase):
    created_at: datetime = Field(..., alias="createdAt")

    class Config:
        from_attributes = True
        validate_by_name = True


# ------------------------------
# Roster Assignment
# ------------------------------
class RosterAssignmentBase(BaseModel):
    crew_id: int = Field(..., alias="crewId")
    flight_id: str = Field(..., alias="flightId")
    start: datetime
    end: datetime
    position: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = Field(default_factory=dict)


class RosterAssignmentCreate(RosterAssignmentBase):
    pass


class RosterAssignmentRead(RosterAssignmentBase):
    id: int
    start: datetime = Field(..., alias="startTime")
    end: datetime = Field(..., alias="endTime")
    created_at: datetime = Field(..., alias="createdAt")
    crew: Optional[CrewRead] = None
    flight: Optional[FlightRead] = None

    class Config:
        from_attributes = True
        validate_by_name = True


# ------------------------------
# Disruption
# ------------------------------
class DisruptionBase(BaseModel):
    type: str
    affected: Optional[Dict[str, Any]] = {}
    severity: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = Field(default_factory=dict)


class DisruptionCreate(DisruptionBase):
    pass


class DisruptionRead(DisruptionBase):
    id: int
    created_at: datetime = Field(..., alias="createdAt")

    class Config:
        from_attributes = True
        validate_by_name = True


# ------------------------------
# Utility / Metrics
# ------------------------------
class GenerateRosterResponse(BaseModel):
    id: Optional[int] = None
    assignments: List[RosterAssignmentRead] = []
    ai_confidence: Optional[float] = Field(None, alias="aiConfidence")
    metrics: Optional[Dict[str, Any]] = {}

    class Config:
        from_attributes = True
        validate_by_name = True


# ------------------------------
# Jobs
# ------------------------------
class JobRead(BaseModel):
    id: int
    type: str
    status: str
    created_at: datetime = Field(..., alias="createdAt")
    completed_at: Optional[datetime] = Field(None, alias="completedAt")
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = Field(None, alias="errorMessage")

    class Config:
        from_attributes = True
        validate_by_name = True
