import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    # Database (either full URL or individual components)
    database_url: str = os.getenv(
        "DATABASE_URL", 
        "sqlite+aiosqlite:///./aerorhythm.db"
    )
    postgres_user: str | None = None
    postgres_password: str | None = None
    postgres_db: str | None = None
    postgres_host: str | None = None

    # Security
    secret_key: str = os.getenv(
        "SECRET_KEY", 
        "your-super-secret-key-change-this-in-production"
    )
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # Application
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"
    api_host: str | None = None
    api_port: int | None = None

    # AI Keys / Paths
    groq_api_key: str | None = None
    perplexity_api_key: str | None = None
    openai_api_key: str | None = None
    ml_model_path: str | None = None
    chroma_dir: str | None = None

settings = Settings()
