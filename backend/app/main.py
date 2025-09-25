from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

# Import your modules correctly
from app.core.database import engine, Base, get_db, test_connection, init_db
# from app.endpoints import crews, flights, disruptions, rosters, auth
from app.endpoints import async_endpoints


# async def run_create_admin():
#     async_gen = get_db()
#     db: AsyncSession = await async_gen.__anext__()
#     try:
#         await auth.create_admin_user(db)
#     finally:
#         await async_gen.aclose()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    print("Starting AeroRhythm API...")
    
    try:
        await init_db()
        print("Database tables created successfully!")

        # Test connection
        if await test_connection():
            print("Database connection verified!")
        else:
            print("Database connection failed!")
    except Exception as e:
        print(f"Startup error: {e}")

    yield

    print("Shutting down AeroRhythm API...")
    await engine.dispose()
    print("Database engine disposed!")
    
    # # Create database tables
    # try:
    #     async with engine.begin() as conn:
    #         await conn.run_sync(Base.metadata.create_all)
    #     print("Database tables created successfully!")
        
    #     # Test connection
    #     if await test_connection():
    #         print("Database connection verified!")
    #     else:
    #         print("Database connection failed!")
            
    # except Exception as e:
    #     print(f"Startup error: {e}")
    
    # yield  # This is where the application runs
    
    # # Shutdown code
    # print("Shutting down AeroRhythm API...")
    # await engine.dispose()
    # print("Database engine disposed!")

app = FastAPI(
    title="AeroRhythm API", 
    version="1.0.0",
    description="Crew management and Roster Optimization System",
    lifespan=lifespan
)

origins = [
    "http://localhost:5173",
    "http://localhost:8080",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8080",
]

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the unified async router
app.include_router(async_endpoints.router, prefix="/api/v1", tags=["api"])

# Include routers
# app.include_router(crews.router, prefix="/crews", tags=["crews"])
# app.include_router(flights.router, prefix="/flights", tags=["flights"])
# app.include_router(disruptions.router, prefix="/disruptions", tags=["disruptions"])
# app.include_router(rosters.router, prefix="/rosters", tags=["rosters"])
# app.include_router(auth.router, prefix="/auth", tags=["auth"])

@app.get("/")
async def root():
    return {"message": "AeroRhythm API", "status": "running"}

@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        # Test database connection
        await db.execute(text("SELECT 1"))
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
        # FIXED: Use text() for raw SQL and correct SELECT 1
        result = await db.execute(text("SELECT 1"))
        return {
            "database": "connected",
            "status": "success"
        }
    except Exception as e:
        return {
            "database": "disconnected",
            "error": str(e),
            "status": "error"
        }



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
