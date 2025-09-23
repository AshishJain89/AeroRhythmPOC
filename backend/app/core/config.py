from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import AnyUrl, Field, field_validator
from typing import Optional


class Settings(BaseSettings):
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:8080", "http://localhost:5173"]


    POSTGRES_USER: str = "crew_user"
    POSTGRES_PASSWORD: str = "P@$$3nger"
    POSTGRES_HOST: str = "localhost"  # or your actual PostgreSQL host
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "crew_rostering"
    DATABASE_URL: Optional[str] = None


    SECRET_KEY: str = "7M3qx-3myhB4qzLZ0CCrXWwgvkt4B1UQ8Qjw7HTt1EI"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    OPENAI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    PERPLEXITY_API_KEY: Optional[str] = None
    ML_MODEL_PATH: Optional[str] = None

    USE_SEED_DATA: bool = False
    CREATE_TABLES_ON_STARTUP: bool = False

    class Config:
        env_file = "backend/.env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields instead of raising validation error
    

    @field_validator("DATABASE_URL", mode="before")
    def assemble_db_connection(cls, v, info):
        if v:
            return v
        data = getattr(info, "data", {}) or {}
        
        # For local development, use PostgreSQL by default
        import os
        if os.getenv("USE_SQLITE", "false").lower() == "true":
            return "sqlite:///./aero_rhythm.db"
        
        # Otherwise use PostgreSQL (for production/Docker)
        user = data.get("POSTGRES_USER")
        pwd = data.get("POSTGRES_PASSWORD")
        host = data.get("POSTGRES_HOST")
        port = data.get("POSTGRES_PORT")
        db = data.get("POSTGRES_DB")
        return f"postgresql://{user}:{pwd}@{host}:{port}/{db}"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
