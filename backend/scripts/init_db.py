import asyncio
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine, Base, AsyncSessionLocal
from app.models import User
from app.services.auth_service import AuthService
from sqlalchemy import select

async def init_database():
    print("Initializing database...")
    
    try:
        async with engine.begin() as conn:
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            print("Database tables created!")

        # Create initial admin user
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User).where(User.username == "admin"))
            admin_user = result.scalar_one_or_none()
            
            if not admin_user:
                hashed_password = AuthService.get_password_hash("admin123")
                admin_user = User(
                    username="admin",
                    email="admin@aerorhythm.com",
                    full_name="System Administrator",
                    hashed_password=hashed_password
                )
                session.add(admin_user)
                await session.commit()
                print("Admin user created!")
            else:
                print("Admin user already exists")

        print("Database initialization completed!")
        
    except Exception as e:
        print(f"Database initialization failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(init_database())