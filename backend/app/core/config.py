from pydantic_settings import BaseSettings
from typing import Optional
from pydantic import model_validator

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    # Environment variables for database connection
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    
    # This will be constructed automatically
    DATABASE_URL: Optional[str] = None

    @model_validator(mode='before')
    def db_url(cls, values):
        if isinstance(values, dict) and values.get("DATABASE_URL") is None:
            values["DATABASE_URL"] = (
                f"postgresql://{values.get('POSTGRES_USER')}:{values.get('POSTGRES_PASSWORD')}"
                f"@{values.get('POSTGRES_SERVER')}/{values.get('POSTGRES_DB')}"
            )
        return values

    # Environment variables for security and tokens
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Gemini API Key
    GEMINI_API_KEY: str

    # Environment variables for Celery
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()