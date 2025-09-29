# backend/scripts/seed_chatbot_data.py
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.app.core.database import SessionLocal
from backend.app.models.chatbot_models import CrewCertification, CrewTraining, Pairing, LeaveRequest, WeatherForecast

def seed_chatbot_sample_data():
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
                sectors=[
                    {
                        "leg": 1,
                        "flight_number": "AI101",
                        "departure": "2025-10-01T05:00:00Z",
                        "arrival": "2025-10-01T06:30:00Z",
                        "origin": "DEL",
                        "destination": "BOM"
                    }
                ],
                planned_start=datetime(2025, 10, 1, 5, 0),
                planned_end=datetime(2025, 10, 1, 12, 0),
                aircraft_type="A320"
            )
        ]
        
        # Add to database
        for obj in certifications + trainings + pairings:
            db.add(obj)
        
        db.commit()
        print("✅ Chatbot sample data seeded successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding chatbot data: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_chatbot_sample_data()