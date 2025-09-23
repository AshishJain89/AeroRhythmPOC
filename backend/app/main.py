from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .utils.seed_loader import load_seed_data
from .core.config import settings
from .core.database_async import engine, AsyncSessionLocal, init_db
from . import models

from .endpoints import (
    auth as auth_router,
    crews as crews_router,
    flights as flights_router,
    rosters as rosters_router,
    disruptions as disruptions_router,
    chat as chat_router,
    explanations as explanations_router,
    jobs as jobs_router,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables at startup (for dev only)
    if settings.CREATE_TABLES_ON_STARTUP:
        await init_db()
    
    if settings.USE_SEED_DATA:
        async with AsyncSessionLocal() as db:
            await load_seed_data(db)
    yield
    # cleanup logic here if needed



app = FastAPI(
    title="AeroRhythm Rostering API", 
    version="0.1.0",
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# register routers
app.include_router(auth_router.router)
app.include_router(crews_router.router)
app.include_router(flights_router.router)
app.include_router(rosters_router.router)
app.include_router(disruptions_router.router)
app.include_router(chat_router.router)
app.include_router(explanations_router.router)
app.include_router(jobs_router.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
