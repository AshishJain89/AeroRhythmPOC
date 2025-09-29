# backend/scripts/sample_data.py
from backend.database import SessionLocal
from backend.models.chatbot_models import *
from datetime import datetime, timedelta
import json

def create_sample_data():
    db = SessionLocal()
    
    try:
        # Sample crew certifications
        certifications = [
            CrewCertification(
                crew_id=1,
                cert_type="type-rating",
                aircraft_type="A320",
                issue_date=datetime(2023, 5, 10).date(),
                expiry_date=datetime(2026, 5, 9).date(),
                details={"rating": "A320", "authority": "DGCA"}
            ),
            CrewCertification(
                crew_id=1,
                cert_type="ATPL",
                aircraft_type=None,
                issue_date=datetime(2022, 1, 15).date(),
                expiry_date=datetime(2027, 12, 31).date(),
                details={"license_no": "ATPL12345"}
            ),
            CrewCertification(
                crew_id=2,
                cert_type="type-rating",
                aircraft_type="B737",
                issue_date=datetime(2024, 1, 20).date(),
                expiry_date=datetime(2025, 1, 19).date(),  # Expiring soon
                details={"rating": "B737", "authority": "DGCA"}
            )
        ]
        
        # Sample training records
        trainings = [
            CrewTraining(
                crew_id=1,
                course="CRM Recurrent",
                valid_from=datetime(2024, 9, 1).date(),
                valid_to=datetime(2025, 9, 1).date(),
                status="active"
            )
        ]
        
        # Sample pairings
        pairings = [
            Pairing(
                pairing_code="PAIR001",
                origin="DEL",
                destination="BOM",
                sectors=json.dumps([
                    {
                        "leg": 1,
                        "flight_number": "AI101",
                        "departure": "2025-10-01T05:00:00Z",
                        "arrival": "2025-10-01T06:30:00Z",
                        "origin": "DEL",
                        "destination": "BOM"
                    }
                ]),
                planned_start=datetime(2025, 10, 1, 5, 0),
                planned_end=datetime(2025, 10, 1, 12, 0),
                aircraft_type="A320"
            )
        ]
        
        # Sample leave requests
        leaves = [
            LeaveRequest(
                crew_id=3,  # Different crew
                leave_start=datetime(2025, 10, 1, 0, 0),
                leave_end=datetime(2025, 10, 3, 23, 59),
                leave_type="annual",
                status="approved",
                reason="Family vacation"
            )
        ]
        
        # Sample weather forecasts
        weather = [
            WeatherForecast(
                airport_code="DEL",
                forecast_time=datetime(2025, 9, 30, 18, 0),
                valid_from=datetime(2025, 10, 1, 0, 0),
                valid_to=datetime(2025, 10, 1, 12, 0),
                severity="medium",
                conditions={
                    "visibility": "2000m",
                    "wind": "25 knots",
                    "weather": "fog",
                    "temperature": 15
                }
            )
        ]
        
        # Add all to database
        for obj in certifications + trainings + pairings + leaves + weather:
            db.add(obj)
        
        db.commit()
        print("Sample data created successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"Error creating sample data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_data()