import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator

class Settings(BaseSettings):
    APP_ENV: str
    PORT: int = 8000

    DATABASE_URL: str

    REDIS_URL: str
    REDIS_PASSWORD: str

    JWT_SECRET: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    INTERNAL_CRON_SECRET: str
    METRICS_SECRET: str

    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str

    FRONTEND_URL: str

    GCS_BUCKET_NAME: str
    GOOGLE_APPLICATION_CREDENTIALS: str

    # TimescaleDB Logging Config
    LOG_RETENTION_DAYS: int = 30
    LOG_COMPRESSION_DAYS: int = 7
    LOG_FLUSH_INTERVAL_SECONDS: int = 5
    LOG_BUFFER_SIZE: int = 100

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_production_security(self) -> "Settings":
        if self.APP_ENV == "production":
            insecure_jwt = ["dev_jwt_secret_key_change_me", ""]
            insecure_cron = ["dev_internal_cron_secret", ""]
            insecure_metrics = ["dev_metrics_secret", ""]
            
            if self.JWT_SECRET in insecure_jwt:
                raise ValueError("JWT_SECRET must be secure in production")
            if self.INTERNAL_CRON_SECRET in insecure_cron:
                raise ValueError("INTERNAL_CRON_SECRET must be secure in production")
            if self.METRICS_SECRET in insecure_metrics:
                raise ValueError("METRICS_SECRET must be secure in production")
        return self

@lru_cache
def get_settings() -> Settings:
    env_state = os.getenv("APP_ENV", "development")
    env_file_path = f"app/config/env/{env_state}.env"
    
    return Settings(_env_file=env_file_path)

settings = get_settings()