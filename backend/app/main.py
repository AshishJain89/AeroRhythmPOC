from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from .core.database import engine, Base, get_db, test_connection
from .endpoints import crews, flights, disruptions, rosters, auth
import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    print("Starting AeroRhythm API...")
    
    # Create database tables
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("Database tables created successfully!")
        
        # Test connection
        if await test_connection():
            print("Database connection verified!")
        else:
            print("Database connection failed!")
            
    except Exception as e:
        print(f"Startup error: {e}")
    
    yield  # This is where the application runs
    
    # Shutdown code
    print("Shutting down AeroRhythm API...")
    await engine.dispose()
    print("Database engine disposed!")

app = FastAPI(
    title="AeroRhythm API", 
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(crews.router, prefix="/crews", tags=["crews"])
app.include_router(flights.router, prefix="/flights", tags=["flights"])
app.include_router(disruptions.router, prefix="/disruptions", tags=["disruptions"])
app.include_router(rosters.router, prefix="/rosters", tags=["rosters"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])

@app.get("/")
async def root():
    return {"message": "AeroRhythm API", "status": "running"}

@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        # Test database connection
        await db.execute("SELECT 1")
        return {
            "status": "healthy", 
            "database": "connected",
            "timestamp": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        return {
            "status": "unhealthy", 
            "database": "disconnected",
            "error": str(e)
        }

@app.get("/test-db")
async def test_db_connection(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute("SELECT version()")
        db_version = result.scalar()
        return {
            "database": "connected",
            "version": db_version,
            "status": "success"
        }
    except Exception as e:
        return {
            "database": "disconnected",
            "error": str(e),
            "status": "error"
        }

# Additional startup tasks can be added here
async def additional_startup_tasks():
    """Run additional startup tasks if needed"""
    # Example: Preload cache, initialize external services, etc.
    await asyncio.sleep(0.1)  # Simulate some startup work
    print("Additional startup tasks completed!")



# from contextlib import asynccontextmanager
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware

# from .utils.seed_loader import load_seed_data
# from .core.config import settings
# from .core.database_async import engine, AsyncSessionLocal, init_db
# from . import models

# from .endpoints import (
#     auth as auth_router,
#     crews as crews_router,
#     flights as flights_router,
#     rosters as rosters_router,
#     disruptions as disruptions_router,
#     chat as chat_router,
#     explanations as explanations_router,
#     jobs as jobs_router,
# )

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Create tables at startup (for dev only)
#     if settings.CREATE_TABLES_ON_STARTUP:
#         await init_db()
    
#     if settings.USE_SEED_DATA:
#         async with AsyncSessionLocal() as db:
#             await load_seed_data(db)
#     yield
#     # cleanup logic here if needed



# app = FastAPI(
#     title="AeroRhythm Rostering API", 
#     version="0.1.0",
#     lifespan=lifespan
# )


# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=settings.BACKEND_CORS_ORIGINS,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # register routers
# app.include_router(auth_router.router)
# app.include_router(crews_router.router)
# app.include_router(flights_router.router)
# app.include_router(rosters_router.router)
# app.include_router(disruptions_router.router)
# app.include_router(chat_router.router)
# app.include_router(explanations_router.router)
# app.include_router(jobs_router.router)


# @app.get("/health")
# def health() -> dict:
#     return {"status": "ok"}
