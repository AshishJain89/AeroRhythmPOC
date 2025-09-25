from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import date, timezone
from sqlalchemy.future import select

from ..core.database import get_db
from ..models import Crew, Flight, Roster, Disruption
# from ..crud.async_crud import crew_crud, flight_crud, roster_crud, disruption_crud

router = APIRouter()

@router.get("/crews/", response_model=List[dict])
async def get_crews(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(Crew)
            .offset(skip)
            .limit(limit)
            .order_by(Crew.id)
        )
        crews = result.scalars().all()
        return [{
            "id": crew.id,
            "firstName": crew.first_name,
            "lastName": crew.last_name,
            "employeeNumber": crew.employee_id,
            "position": crew.position,
            "homeBase": crew.home_base,
            "status": crew.status,
            "licenceExpiry": crew.licence_expiry.isoformat() if crew.licence_expiry else "2026-12-31",
            "qualifications": crew.qualifications or [],
            "isActive": crew.is_active,
            "createdAt": crew.created_at.isoformat() if crew.created_at else None
        } for crew in crews]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching crews: {str(e)}")

    # crews = await crew_crud.get_multi(db, skip, limit)
    # return [{
    #     "id": crew.id,
    #     "firstName": crew.first_name,
    #     "lastName": crew.last_name,
    #     "employeeNumber": crew.employee_id,
    #     "position": crew.position,
    #     "homeBase": crew.home_base,
    #     "status": crew.status,
    #     "licenceExpiry": crew.licence_expiry.isoformat() if crew.licence_expiry else None,
    #     "qualifications": crew.qualifications or [],
    #     "isActive": crew.is_active,
    #     "createdAt": crew.created_at.isoformat() if crew.created_at else None
    # } for crew in crews]


@router.get("/flights/", response_model=List[dict])
async def get_flights(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(Flight)
            .offset(skip)
            .limit(limit)
            .order_by(Flight.departure_time)
        )
        flights = result.scalars().all()
        
        return [{
            "id": flight.id,
            "flightNumber": flight.flight_number,
            "origin": flight.origin,
            "destination": flight.destination,
            "departureTime": flight.departure_time.isoformat() if flight.departure_time else None,
            "arrivalTime": flight.arrival_time.isoformat() if flight.arrival_time else None,
            "aircraftType": flight.aircraft_type,
            "status": flight.status,
            "createdAt": flight.created_at.isoformat() if flight.created_at else None
        } for flight in flights]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching flights: {str(e)}")
    
    # flights = await flight_crud.get_multi(db, skip, limit)
    # return [{
    #     "id": flight.id,
    #     "flightNumber": flight.flight_number,
    #     "origin": flight.origin,
    #     "destination": flight.destination,
    #     "departureTime": flight.departure_time.isoformat() if flight.departure_time else None,
    #     "arrivalTime": flight.arrival_time.sioformat() if flight.arrival_time else None,
    #     "aircraftType": flight.aircraft_type,
    #     "status": flight.status,
    #     "createdAt": flight.created_at.isoformat() if flight.created_at else None
    # } for flight in flights]


@router.get("/rosters/", response_model=dict)
async def get_rosters(
    start: date = Query(..., description="Start date"), 
    end: date = Query(..., description="End date"), 
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(Roster)
            .filter(Roster.assignment_date >= start, Roster.assignment_date <= end)
            .offset(skip)
            .limit(limit)
            .order_by(Roster.assignment_date, Roster.report_time)
        )
        rosters = result.scalars().all()
        
        return {
            "rosters": [{
                "id": roster.id,
                "crewId": roster.crew_id,
                "flightId": roster.flight_id,
                "date": roster.assignment_date.isoformat() if roster.assignment_date else None,
                "reportTime": roster.report_time.isoformat() if roster.report_time else None,
                "dutyType": roster.duty_type,
                "status": roster.status,
                "confidence": float(roster.confidence) if roster.confidence else 0.95,
                "violations": roster.violations or [],
                "isActive": roster.is_active,
                "createdAt": roster.created_at.isoformat() if roster.created_at else None
            } for roster in rosters]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching rosters: {str(e)}")
    
    # rosters = await roster_crud.get_by_date_range(db, start, end)
    # return {
    #     "rosters": [{
    #         "id": roster.id,
    #         "crewID": roster.crew_id,
    #         "flightID": roster.flight_id,
    #         "date": roster.assignment_date.isoformat() if roster.assignment_date else None,
    #         "reportTime": roster.report_time.isoformat() if roster.report_time else None,
    #         "dutyType": roster.duty_type,
    #         "status": roster.status,
    #         "confidence": roster.confidence or 0.95,
    #         "violations": roster.violations or [],
    #         "isActive": roster.is_active,
    #         "createdAt": roster.created_at.isoformat() if roster.created_at else None
    #     } for roster in rosters]
    # }

@router.get("/disruptions/", response_model=List[dict])
async def get_disruptions(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(Disruption)
            .offset(skip)
            .limit(limit)
            .order_by(Disruption.created_at.desc())
        )
        disruptions = result.scalars().all()
        
        return [{
            "id": disruption.id,
            "title": disruption.title,
            "description": disruption.description,
            "type": disruption.type,
            "severity": disruption.severity,
            "status": disruption.status,
            "affectedFlights": disruption.affected_flights or [],
            "affectedCrew": disruption.affected_crew or [],
            "startTime": disruption.start_time.isoformat() if disruption.start_time else None,
            "endTime": disruption.end_time.isoformat() if disruption.end_time else None,
            "createdAt": disruption.created_at.isoformat() if disruption.created_at else None
        } for disruption in disruptions]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching disruptions: {str(e)}")
    
    # disruptions = await disruption_crud.get_multi(db, skip, limit)
    # return [{
    #     "id": disruption.id,
    #     "title": disruption.title,
    #     "description": disruption.description,
    #     "type": disruption.type,
    #     "severity": disruption.severity,
    #     "status": disruption.status,
    #     "affectedFlights": disruption.affected_flights or [],
    #     "affectedCrew": disruption.affected_crew or [],
    #     "startTime": disruption.start_time.isoformat() if disruption.start_time else None,
    #     "endTime": disruption.end_time.isoformat() if disruption.end_time else None,
    #     "createdAt": disruption.created_at.isoformat() if disruption.created_at else None
    # } for disruption in disruptions]