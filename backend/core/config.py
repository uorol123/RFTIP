import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "RFTIP API"
    app_version: str = "1.0.0"
    debug: bool = False

    database_url: str = "mysql+pymysql://root:password@localhost:3306/rftip_db"
    secret_key: str = "your-secret-key-change-this-in-production"
    access_token_expire_minutes: int = 30

    cors_origins: list = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings():
    return Settings()
